import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField


class Profile(models.Model):
    """
    Stores LinkedIn profile data and DISC analysis results.
    Matches the database schema with fields:
    - id: UUID primary key
    - user_id: UUID (nullable for now, can link to user table later)
    - linkedin_url: LinkedIn profile URL
    - name: Profile name
    - headline: Professional headline
    - disc_primary: Primary DISC type
    - disc_breakdown: JSON with dominance, influence, steadiness, compliance
    - raw_data: JSON with full analysis response
    - created_at: Timestamp
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True, help_text="User ID (nullable for now)")
    linkedin_url = models.TextField(blank=True, null=True, help_text="LinkedIn profile URL")
    name = models.TextField(help_text="Profile name")
    headline = models.TextField(blank=True, null=True, help_text="Professional headline")
    disc_primary = models.TextField(blank=True, null=True, help_text="Primary DISC type")
    disc_breakdown = JSONField(default=dict, blank=True, help_text="DISC breakdown (dominance, influence, steadiness, compliance)")
    raw_data = JSONField(default=dict, blank=True, help_text="Full analysis response from Gemini")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")

    class Meta:
        db_table = 'profiles'
        ordering = ['-created_at']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"{self.name} - {self.disc_primary or 'No DISC type'}"
