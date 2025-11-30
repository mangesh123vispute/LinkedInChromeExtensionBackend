import uuid
from django.db import models


class AnalyzedProfile(models.Model):
    """
    Stores LinkedIn profile data and DISC analysis results from LLM.
    Contains all analyzed data including DISC personality, insights, and sales strategies.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True, help_text="User ID (nullable for now)")
    
    # Basic Profile Information
    name = models.TextField(help_text="Profile name")
    headline = models.TextField(blank=True, null=True, help_text="Professional headline")
    linkedin_profile = models.TextField(blank=True, null=True, help_text="LinkedIn profile URL")
    
    # DISC Personality Analysis
    confidence = models.IntegerField(blank=True, null=True, help_text="Confidence score (0-100)")
    dominance = models.IntegerField(blank=True, null=True, help_text="Dominance score (0-100)")
    influence = models.IntegerField(blank=True, null=True, help_text="Influence score (0-100)")
    steadiness = models.IntegerField(blank=True, null=True, help_text="Steadiness score (0-100)")
    compliance = models.IntegerField(blank=True, null=True, help_text="Compliance score (0-100)")
    disc_primary = models.TextField(blank=True, null=True, help_text="Primary DISC type")
    
    # Analysis Insights
    key_insights = models.JSONField(default=list, blank=True, help_text="Key insights as list of strings")
    pain_points = models.JSONField(default=list, blank=True, help_text="Pain points as list of strings")
    communication_style = models.TextField(blank=True, null=True, help_text="Communication style description")
    sales_approach = models.TextField(blank=True, null=True, help_text="Sales approach description")
    best_approach = models.TextField(blank=True, null=True, help_text="Best approach description")
    ideal_pitch = models.TextField(blank=True, null=True, help_text="Ideal pitch description")
    communication_dos = models.JSONField(default=list, blank=True, help_text="Communication do's as list of strings")
    communication_donts = models.JSONField(default=list, blank=True, help_text="Communication don'ts as list of strings")
    
    # Raw data backup
    raw_data = models.JSONField(default=dict, blank=True, help_text="Full analysis response from Gemini")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")

    class Meta:
        db_table = 'analyzed_profiles'
        ordering = ['-created_at']
        verbose_name = 'Analyzed Profile'
        verbose_name_plural = 'Analyzed Profiles'

    def __str__(self):
        return f"{self.name} - {self.disc_primary or 'No DISC type'}"
