import uuid
import re
from django.db import models


def extract_linkedin_profile_id(url):
    """
    Extract profile ID from LinkedIn URL.
    Example: https://www.linkedin.com/in/sumit-patil-1b31a9271/ -> sumit-patil-1b31a9271
    """
    if not url:
        return None
    
    pattern = r'linkedin\.com/in/([^/?\s]+)'
    match = re.search(pattern, url, re.IGNORECASE)
    
    if match:
        profile_id = match.group(1).rstrip('/')
        return profile_id
    
    return None


class RawData(models.Model):
    """
    Stores raw scraped LinkedIn profile data before analysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_id = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True, help_text="LinkedIn profile ID (e.g., sumit-patil-1b31a9271)")
    linkedin_profile = models.TextField(blank=True, null=True, help_text="Full LinkedIn profile URL")
    
    name = models.TextField(help_text="Profile name")
    headline = models.TextField(blank=True, null=True, help_text="Professional headline")
    location = models.TextField(blank=True, null=True, help_text="Location")
    about = models.TextField(blank=True, null=True, help_text="About section")
    experience = models.TextField(blank=True, null=True, help_text="Experience section")
    education = models.TextField(blank=True, null=True, help_text="Education section")
    skills = models.TextField(blank=True, null=True, help_text="Skills")
    connections_count = models.CharField(max_length=50, blank=True, null=True, help_text="Connections count")
    current_company = models.TextField(blank=True, null=True, help_text="Current company")
    top_skills = models.TextField(blank=True, null=True, help_text="Top skills")
    activity = models.TextField(blank=True, null=True, help_text="Activity")
    posts = models.JSONField(default=list, blank=True, help_text="Recent posts")
    
    raw_data = models.JSONField(default=dict, blank=True, help_text="Complete raw scraped data as JSON")
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        db_table = 'raw_data'
        ordering = ['-created_at']
        verbose_name = 'Raw Data'
        verbose_name_plural = 'Raw Data'

    def __str__(self):
        return f"{self.name} - {self.profile_id}"


class AnalyzedProfile(models.Model):
    """
    Stores LinkedIn profile data and DISC analysis results from LLM.
    Contains all analyzed data including DISC personality, insights, and sales strategies.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True, help_text="User ID (nullable for now)")
    
    profile_id = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True, help_text="LinkedIn profile ID (e.g., sumit-patil-1b31a9271)")
    
    raw_data_ref = models.ForeignKey(
        'RawData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyzed_profiles',
        help_text="Reference to raw scraped data"
    )
    
    name = models.TextField(help_text="Profile name")
    headline = models.TextField(blank=True, null=True, help_text="Professional headline")
    linkedin_profile = models.TextField(blank=True, null=True, help_text="LinkedIn profile URL")
    
    confidence = models.IntegerField(blank=True, null=True, help_text="Confidence score (0-100)")
    dominance = models.IntegerField(blank=True, null=True, help_text="Dominance score (0-100)")
    influence = models.IntegerField(blank=True, null=True, help_text="Influence score (0-100)")
    steadiness = models.IntegerField(blank=True, null=True, help_text="Steadiness score (0-100)")
    compliance = models.IntegerField(blank=True, null=True, help_text="Compliance score (0-100)")
    disc_primary = models.TextField(blank=True, null=True, help_text="Primary DISC type")
    
    key_insights = models.JSONField(default=list, blank=True, help_text="Key insights as list of strings")
    pain_points = models.JSONField(default=list, blank=True, help_text="Pain points as list of strings")
    communication_style = models.TextField(blank=True, null=True, help_text="Communication style description")
    sales_approach = models.TextField(blank=True, null=True, help_text="Sales approach description")
    best_approach = models.TextField(blank=True, null=True, help_text="Best approach description")
    ideal_pitch = models.TextField(blank=True, null=True, help_text="Ideal pitch description")
    communication_dos = models.JSONField(default=list, blank=True, help_text="Communication do's as list of strings")
    communication_donts = models.JSONField(default=list, blank=True, help_text="Communication don'ts as list of strings")
    
    raw_data = models.JSONField(default=dict, blank=True, help_text="Full analysis response from Gemini")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        db_table = 'analyzed_profiles'
        ordering = ['-created_at']
        verbose_name = 'Analyzed Profile'
        verbose_name_plural = 'Analyzed Profiles'

    def __str__(self):
        return f"{self.name} - {self.disc_primary or 'No DISC type'}"
