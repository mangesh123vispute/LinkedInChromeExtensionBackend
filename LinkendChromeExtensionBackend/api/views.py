import os
import json
import re
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfileDataSerializer, AnalysisResponseSerializer, ProfileSaveSerializer, ProfileModelSerializer
from .models import Profile


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
Headline: {profile_data.get('headline', 'Not available')}
Connections: {profile_data.get('connectionsCount', 'Unknown')}

About Section:
{profile_data.get('about', 'No about section available')}

Experience:
{profile_data.get('experience', 'No experience data available')}

Education:
{profile_data.get('education', 'No education data')}

Top Skills: {profile_data.get('skills', 'No skills listed')}

RECENT POSTS & ENGAGEMENT:
{posts_text}

Based on this comprehensive profile, provide a DEEP personality analysis focusing on:
1. DISC personality breakdown (must total 100%)
2. Their values, motivations, and pain points
3. What they care about (based on posts and career)
4. How to approach them in sales
5. What messaging will resonate
6. Red flags or objections they might have

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
  "bestApproach": "Open with a specific insight about their work (reference a post or achievement). Position yourself as a peer, not a salesperson. Lead with a problem you've solved for similar AWS architects. Offer value first (whitepaper, demo, free audit) before asking for a meeting."
}}

Make this analysis SPECIFIC to this person based on their actual content, not generic templates!"""

    gemini_api_key = settings.GEMINI_API_KEY
    if not gemini_api_key:
        raise ValueError('GEMINI_API_KEY is not configured in environment variables')

    api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    
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


@api_view(['POST'])
def save_profile(request):
    """
    Save LinkedIn profile data and analysis results to database.
    
    Expected request body:
    {
        "profile_data": {
            "name": "John Doe",
            "headline": "Software Engineer",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            ...
        },
        "analysis_data": {
            "dominance": 35,
            "influence": 30,
            "primaryType": "Influence (I)",
            ...
        },
        "user_id": "optional-uuid"  # Optional
    }
    """
    serializer = ProfileSaveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    profile_data = validated_data['profile_data']
    analysis_data = validated_data['analysis_data']
    user_id = validated_data.get('user_id')
    
    try:
        # Prepare disc_breakdown
        disc_breakdown = {
            'dominance': analysis_data.get('dominance', 0),
            'influence': analysis_data.get('influence', 0),
            'steadiness': analysis_data.get('steadiness', 0),
            'compliance': analysis_data.get('compliance', 0),
        }
        
        # Create profile record
        profile = Profile.objects.create(
            user_id=user_id,
            linkedin_url=profile_data.get('linkedin_url', ''),
            name=profile_data.get('name', ''),
            headline=profile_data.get('headline', ''),
            disc_primary=analysis_data.get('primaryType', ''),
            disc_breakdown=disc_breakdown,
            raw_data=analysis_data,  # Store full analysis response
        )
        
        # Return saved profile
        response_serializer = ProfileModelSerializer(profile)
        return Response(
            {
                'message': 'Profile saved successfully',
                'profile': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'error': 'Failed to save profile', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
