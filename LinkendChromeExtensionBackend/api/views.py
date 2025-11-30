import os
import json
import re
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfileDataSerializer, AnalysisResponseSerializer, AnalyzedProfileSaveSerializer, AnalyzedProfileModelSerializer
from .models import AnalyzedProfile

import pdb

@csrf_exempt
@api_view(['POST'])
def analyze_profile(request):
    """
    Analyze LinkedIn profile data using Gemini AI and return DISC personality analysis.
    
    Expected request body:
    {
        "name": "John Doe",
        "headline": "Software Engineer",
        "location": "San Francisco, CA",
        "about": "...",
        "experience": "...",
        "education": "...",
        "skills": "...",
        "connectionsCount": "500+",
        "posts": [
            {
                "text": "...",
                "time": "2 days ago",
                "reactions": "10",
                "comments": "5"
            }
        ]
    }
    """
    # Validate input data
    serializer = ProfileDataSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid profile data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile_data = serializer.validated_data
    
    try:
        # Call Gemini API
        analysis_result = analyze_with_gemini(profile_data)
        
        # Validate response
        response_serializer = AnalysisResponseSerializer(data=analysis_result)
        if not response_serializer.is_valid():
            return Response(
                {'error': 'Invalid analysis response from AI', 'details': response_serializer.errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(analysis_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Analysis failed', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def analyze_with_gemini(profile_data):
    """
    Analyze profile data using Google Gemini API.
    """
    # Format posts for the prompt
    posts_text = 'No recent posts available'
    if profile_data.get('posts') and len(profile_data['posts']) > 0:
        posts_text = '\n\n'.join([
            f"Post {i+1} ({post.get('time', 'Unknown')}): \"{post.get('text', '')}\" - {post.get('reactions', '0')} reactions, {post.get('comments', '0')} comments"
            for i, post in enumerate(profile_data['posts'])
        ])

    prompt = f"""You are an expert sales psychologist and DISC personality analyst. Analyze this LinkedIn profile and provide ACTIONABLE sales insights.

PROFILE DATA:
Name: {profile_data.get('name', 'Not available')}
Location: {profile_data.get('location', 'Not available')}
Headline (Full): {profile_data.get('headline', 'Not available')}
Current Company: {profile_data.get('currentCompany', 'Not available')}
Connections: {profile_data.get('connectionsCount', 'Unknown')}
Followers: {profile_data.get('followersCount', 'Unknown')}

About Section:
{profile_data.get('about', 'No about section available')}

Highlights:
{profile_data.get('highlights', 'No highlights available')}

Experience:
{profile_data.get('experience', 'No experience data available')}

Education:
{profile_data.get('education', 'No education data')}

Licenses and Certifications:
{profile_data.get('licensesAndCertifications', 'No licenses or certifications listed')}

Top Skills: {profile_data.get('skills', 'No skills listed')}

Services:
{profile_data.get('services', 'No services listed')}

RECENT ACTIVITY & POSTS:
{profile_data.get('activity', posts_text)}

Based on this comprehensive profile, provide a DEEP personality analysis focusing on:
1. DISC personality breakdown (must total 100%)
2. Their values, motivations, and pain points
3. What they care about (based on posts and career)
4. How to approach them in sales
5. What messaging will resonate
6. Red flags or objections they might have
7. Personalized email template (subject + body) tailored to their DISC type and interests
8. LinkedIn message (under 300 characters) for connection or InMail
9. Follow-up message for 3-5 days after initial contact

Return ONLY this JSON (no markdown):
{{
  "dominance": 35,
  "influence": 30,
  "steadiness": 20,
  "compliance": 15,
  "primaryType": "Influence (I)",
  "confidence": 78,
  "description": "Engaging • Collaborative • People-focused",
  "keyInsights": [
    "Values innovation and cloud technology",
    "Active on LinkedIn - posts about AWS and DevOps regularly",
    "Career-focused on scalable solutions and architecture",
    "Likely responds to data-driven pitches with ROI focus"
  ],
  "communicationStyle": "This person is technical but collaborative. They value expertise and practical solutions. Based on their posts, they're interested in AWS, cloud architecture, and DevOps practices.",
  "salesApproach": "Lead with technical credibility. Share case studies of similar cloud implementations. Emphasize scalability and cost savings. They're active on LinkedIn, so social proof matters.",
  "painPoints": [
    "Managing cloud costs at scale",
    "Finding reliable DevOps automation tools",
    "Keeping up with rapid AWS updates"
  ],
  "idealPitch": "Brief, technical, backed by data. Show them how your solution saves time and money in cloud infrastructure. Mention specific AWS services they use.",
  "communicationDos": [
    "Be technical and knowledgeable about cloud tech",
    "Share specific metrics and case studies",
    "Respect their expertise - don't oversimplify",
    "Reference their LinkedIn posts to show research"
  ],
  "communicationDonts": [
    "Don't use generic sales pitches",
    "Avoid non-technical fluff",
    "Don't ignore their specific interests (AWS, DevOps)",
    "Don't rush them - they'll evaluate thoroughly"
  ],
  "bestApproach": "Open with a specific insight about their work (reference a post or achievement). Position yourself as a peer, not a salesperson. Lead with a problem you've solved for similar AWS architects. Offer value first (whitepaper, demo, free audit) before asking for a meeting.",
  "emailTemplate": {{
    "subject": "Personalized subject line based on their profile",
    "body": "Complete email body personalized to their DISC type, interests, and pain points. Include specific references to their profile, achievements, or posts. Make it warm, professional, and value-focused."
  }},
  "linkedinMessage": "Personalized LinkedIn connection message or InMail. Should be concise (under 300 characters), reference something specific from their profile, and include a clear value proposition. Match their communication style based on DISC type.",
  "followUpMessage": "Follow-up message for after initial contact. Should acknowledge previous conversation, provide additional value, and include a soft call-to-action. Should be sent 3-5 days after initial contact."
}}

Make this analysis SPECIFIC to this person based on their actual content, not generic templates!"""

    gemini_api_key = settings.GEMINI_API_KEY
    if not gemini_api_key:
        raise ValueError('GEMINI_API_KEY is not configured in environment variables')

    api_url = settings.GEMINI_API_URL
    
    response = requests.post(
        api_url,
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': gemini_api_key
        },
        json={
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }],
            'generationConfig': {
                'temperature': 0.8,
                'maxOutputTokens': 2048
            }
        }
    )
    
    if response.status_code != 200:
        raise Exception(f'Gemini API error: {response.status_code} - {response.text}')
    
    data = response.json()
    text_response = data['candidates'][0]['content']['parts'][0]['text']
    
    # Extract JSON from response
    json_text = text_response.strip()
    json_text = json_text.replace('```json\n', '')
    json_text = json_text.replace('```\n', '')
    json_text = json_text.replace('```', '')
    
    json_match = re.search(r'\{[\s\S]*\}', json_text)
    if not json_match:
        raise Exception('Could not parse AI response as JSON')
    
    analysis = json.loads(json_match.group(0))
    return analysis


@csrf_exempt
@api_view(['POST'])
def save_analyzed_data(request):
    """
    Save analyzed LinkedIn profile data from LLM to database.
    Accepts both camelCase (from LLM) and snake_case formats.
    
    Expected request body (can use either camelCase or snake_case):
    {
        "name": "John Doe",
        "headline": "Software Engineer",
        "linkedin_profile": "https://linkedin.com/in/johndoe",  // or "linkedin_url"
        "confidence": 78,
        "dominance": 35,
        "influence": 30,
        "steadiness": 20,
        "compliance": 15,
        "primaryType": "Influence (I)",  // or "disc_primary"
        "keyInsights": ["insight1", "insight2"],  // or "key_insights"
        "painPoints": ["pain1", "pain2"],  // or "pain_points"
        "communicationStyle": "Description...",  // or "communication_style"
        "salesApproach": "Description...",  // or "sales_approach"
        "bestApproach": "Description...",  // or "best_approach"
        "idealPitch": "Description...",  // or "ideal_pitch"
        "communicationDos": ["do1", "do2"],  // or "communication_dos"
        "communicationDonts": ["dont1", "dont2"],  // or "communication_donts"
        "user_id": "optional-uuid"  // Optional
    }
    """
    # Normalize camelCase to snake_case for processing
    data = request.data.copy()
    
    # Map camelCase fields to snake_case
    field_mapping = {
        'linkedin_url': 'linkedin_profile',
        'primaryType': 'disc_primary',
        'keyInsights': 'key_insights',
        'painPoints': 'pain_points',
        'communicationStyle': 'communication_style',
        'salesApproach': 'sales_approach',
        'bestApproach': 'best_approach',
        'idealPitch': 'ideal_pitch',
        'communicationDos': 'communication_dos',
        'communicationDonts': 'communication_donts',
    }
    
    # Apply mappings (prefer snake_case if both exist)
    for camel_key, snake_key in field_mapping.items():
        if camel_key in data and snake_key not in data:
            data[snake_key] = data[camel_key]
        elif camel_key in data and snake_key in data:
            # Both exist, prefer snake_case
            pass
        # If only snake_case exists, keep it as is
    
    # Handle linkedin_url -> linkedin_profile
    if 'linkedin_url' in data and 'linkedin_profile' not in data:
        data['linkedin_profile'] = data['linkedin_url']
    
    serializer = AnalyzedProfileSaveSerializer(data=data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    user_id = validated_data.get('user_id')
    
    try:
        # Get linkedin_profile - handle empty strings as None
        linkedin_profile = validated_data.get('linkedin_profile', '')
        if linkedin_profile and linkedin_profile.strip():
            linkedin_profile = linkedin_profile.strip()
        else:
            linkedin_profile = None

        
        # Check if profile with same LinkedIn URL already exists
        # Normalize URL for comparison (case-insensitive, remove trailing slashes)
        if linkedin_profile:
            # Normalize the URL: lowercase, remove trailing slash, remove query params
            normalized_url = linkedin_profile.lower().strip().rstrip('/')
            # Remove query parameters and fragments
            if '?' in normalized_url:
                normalized_url = normalized_url.split('?')[0]
            if '#' in normalized_url:
                normalized_url = normalized_url.split('#')[0]
            
            # Check for existing profiles with similar URLs
            existing_profiles = AnalyzedProfile.objects.filter(
                linkedin_profile__isnull=False
            ).exclude(linkedin_profile='')
            
            for existing in existing_profiles:
                # Normalize existing URL for comparison
                existing_url = existing.linkedin_profile.lower().strip().rstrip('/')
                if '?' in existing_url:
                    existing_url = existing_url.split('?')[0]
                if '#' in existing_url:
                    existing_url = existing_url.split('#')[0]
                
                # Check if URLs match (after normalization)
                if normalized_url == existing_url:
                    # Return existing profile data with a message
                    response_serializer = AnalyzedProfileModelSerializer(existing)
                    return Response(
                        {
                            'message': 'Profile already exists in database',
                            'already_exists': True,
                            'profile': response_serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
        
        # Create analyzed profile record with all fields
        analyzed_profile = AnalyzedProfile.objects.create(
            user_id=user_id,
            name=validated_data.get('name', ''),
            headline=validated_data.get('headline', ''),
            linkedin_profile=linkedin_profile,
            confidence=validated_data.get('confidence'),
            dominance=validated_data.get('dominance'),
            influence=validated_data.get('influence'),
            steadiness=validated_data.get('steadiness'),
            compliance=validated_data.get('compliance'),
            disc_primary=validated_data.get('disc_primary', ''),
            key_insights=validated_data.get('key_insights', []),
            pain_points=validated_data.get('pain_points', []),
            communication_style=validated_data.get('communication_style', ''),
            sales_approach=validated_data.get('sales_approach', ''),
            best_approach=validated_data.get('best_approach', ''),
            ideal_pitch=validated_data.get('ideal_pitch', ''),
            communication_dos=validated_data.get('communication_dos', []),
            communication_donts=validated_data.get('communication_donts', []),
            raw_data=request.data,  # Store original request data as backup
        )
        
        # Return saved profile
        response_serializer = AnalyzedProfileModelSerializer(analyzed_profile)
        return Response(
            {
                'message': 'Analyzed data saved successfully',
                'profile': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'error': 'Failed to save analyzed data', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
def generate_message(request):
    """
    Generate customizable email template, LinkedIn message, or follow-up message
    based on user query and profile data.
    
    Expected request body:
    {
        "messageType": "email" | "linkedin" | "followup",
        "query": "User's query/prompt",
        "profileData": {
            "name": "...",
            "headline": "...",
            ... (full profile data)
        }
    }
    """
    message_type = request.data.get('messageType')
    query = request.data.get('query')
    profile_data = request.data.get('profileData')

    if not message_type or message_type not in ['email', 'linkedin', 'followup']:
        return Response(
            {'error': 'Invalid messageType. Must be "email", "linkedin", or "followup"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not query or not query.strip():
        return Response(
            {'error': 'Query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not profile_data:
        return Response(
            {'error': 'Profile data is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = generate_custom_message(message_type, query, profile_data)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Message generation failed', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_custom_message(message_type, query, profile_data):
    """
    Generate custom message using Gemini API based on user query and profile data.
    """
    posts_text = 'No recent posts available'
    if profile_data.get('posts') and len(profile_data['posts']) > 0:
        posts_text = '\n\n'.join([
            f"Post {i+1} ({post.get('time', 'Unknown')}): \"{post.get('text', '')}\" - {post.get('reactions', '0')} reactions, {post.get('comments', '0')} comments"
            for i, post in enumerate(profile_data['posts'])
        ])

    profile_summary = f"""
PROFILE INFORMATION:
Name: {profile_data.get('name', 'Not available')}
Location: {profile_data.get('location', 'Not available')}
Headline (Full): {profile_data.get('headline', 'Not available')}
Current Company: {profile_data.get('currentCompany', 'Not available')}
Connections: {profile_data.get('connectionsCount', 'Unknown')}
Followers: {profile_data.get('followersCount', 'Unknown')}

About: {profile_data.get('about', 'No about section available')}

Highlights: {profile_data.get('highlights', 'No highlights available')}

Experience: {profile_data.get('experience', 'No experience data available')}

Education: {profile_data.get('education', 'No education data')}

Licenses and Certifications: {profile_data.get('licensesAndCertifications', 'No licenses or certifications listed')}

Skills: {profile_data.get('skills', 'No skills listed')}

Services: {profile_data.get('services', 'No services listed')}

Recent Activity:
{profile_data.get('activity', posts_text)}
"""

    if message_type == 'email':
        prompt = f"""You are an expert email copywriter. Based on the following LinkedIn profile information and the user's specific request, create a professional, personalized email.

{profile_summary}

USER REQUEST: {query}

Generate a professional email that:
1. Is personalized to this specific person based on their profile
2. Addresses the user's request: "{query}"
3. Is warm, professional, and engaging
4. Includes a clear subject line
5. Has a compelling body that references specific details from their profile
6. Is appropriate for their DISC personality type (if discernible from profile)
7. Is concise but complete (2-3 paragraphs max)

Return ONLY this JSON (no markdown):
{{
  "subject": "Email subject line here",
  "body": "Complete email body here with proper formatting"
}}"""
    elif message_type == 'linkedin':
        prompt = f"""You are an expert LinkedIn message writer. Based on the following LinkedIn profile information and the user's specific request, create a personalized LinkedIn connection message or InMail.

{profile_summary}

USER REQUEST: {query}

Generate a LinkedIn message that:
1. Is personalized to this specific person based on their profile
2. Addresses the user's request: "{query}"
3. Is warm, professional, and engaging
4. Is concise (under 300 characters for connection requests, can be longer for InMail)
5. References specific details from their profile to show you've done research
6. Has a clear value proposition or reason for connecting
7. Is appropriate for their communication style

Return ONLY this JSON (no markdown):
{{
  "message": "Complete LinkedIn message here"
}}"""
    else:
        prompt = f"""You are an expert follow-up message writer. Based on the following LinkedIn profile information and the user's specific request, create a personalized follow-up message.

{profile_summary}

USER REQUEST: {query}

Generate a follow-up message that:
1. Is personalized to this specific person based on their profile
2. Addresses the user's request: "{query}"
3. Acknowledges any previous conversation or interaction
4. Provides additional value or information
5. Is warm, professional, and not pushy
6. Includes a soft call-to-action
7. Is appropriate for follow-up timing (3-5 days after initial contact)

Return ONLY this JSON (no markdown):
{{
  "message": "Complete follow-up message here"
}}"""

    gemini_api_key = settings.GEMINI_API_KEY
    if not gemini_api_key:
        raise ValueError('GEMINI_API_KEY is not configured in environment variables')

    api_url = settings.GEMINI_API_URL
    
    response = requests.post(
        api_url,
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': gemini_api_key
        },
        json={
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }],
            'generationConfig': {
                'temperature': 0.8,
                'maxOutputTokens': 2048
            }
        }
    )
    
    if response.status_code != 200:
        raise Exception(f'Gemini API error: {response.status_code} - {response.text}')
    
    data = response.json()
    text_response = data['candidates'][0]['content']['parts'][0]['text']
    
    json_text = text_response.strip()
    json_text = json_text.replace('```json\n', '')
    json_text = json_text.replace('```\n', '')
    json_text = json_text.replace('```', '')
    
    json_match = re.search(r'\{[\s\S]*\}', json_text)
    if not json_match:
        raise Exception('Could not parse AI response as JSON')
    
    result = json.loads(json_match.group(0))
    return result
