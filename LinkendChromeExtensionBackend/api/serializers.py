from rest_framework import serializers
from .models import AnalyzedProfile


class PostSerializer(serializers.Serializer):
    text = serializers.CharField()
    time = serializers.CharField()
    reactions = serializers.CharField()
    comments = serializers.CharField()


class ProfileDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    headline = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    about = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    education = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.CharField(required=False, allow_blank=True)
    connectionsCount = serializers.CharField(required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    posts = PostSerializer(many=True, required=False, allow_null=True)
    highlights = serializers.CharField(required=False, allow_blank=True)
    services = serializers.CharField(required=False, allow_blank=True)
    licensesAndCertifications = serializers.CharField(required=False, allow_blank=True)
    followersCount = serializers.CharField(required=False, allow_blank=True)
    currentCompany = serializers.CharField(required=False, allow_blank=True)
    activity = serializers.CharField(required=False, allow_blank=True)


class EmailTemplateSerializer(serializers.Serializer):
    subject = serializers.CharField()
    body = serializers.CharField()


class AnalysisResponseSerializer(serializers.Serializer):
    dominance = serializers.IntegerField()
    influence = serializers.IntegerField()
    steadiness = serializers.IntegerField()
    compliance = serializers.IntegerField()
    primaryType = serializers.CharField()
    confidence = serializers.IntegerField()
    description = serializers.CharField()
    keyInsights = serializers.ListField(child=serializers.CharField())
    communicationStyle = serializers.CharField()
    salesApproach = serializers.CharField()
    painPoints = serializers.ListField(child=serializers.CharField())
    idealPitch = serializers.CharField()
    communicationDos = serializers.ListField(child=serializers.CharField())
    communicationDonts = serializers.ListField(child=serializers.CharField())
    bestApproach = serializers.CharField()
    emailTemplate = EmailTemplateSerializer(required=False)
    linkedinMessage = serializers.CharField(required=False)
    followUpMessage = serializers.CharField(required=False)


class AnalyzedProfileSaveSerializer(serializers.Serializer):
    """Serializer for saving analyzed profile data"""
    # Basic fields
    name = serializers.CharField(required=True)
    headline = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkedin_profile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # DISC fields
    confidence = serializers.IntegerField(required=False, allow_null=True)
    dominance = serializers.IntegerField(required=False, allow_null=True)
    influence = serializers.IntegerField(required=False, allow_null=True)
    steadiness = serializers.IntegerField(required=False, allow_null=True)
    compliance = serializers.IntegerField(required=False, allow_null=True)
    disc_primary = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Analysis fields
    key_insights = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    pain_points = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    communication_style = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sales_approach = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    best_approach = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ideal_pitch = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    communication_dos = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    communication_donts = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    
    user_id = serializers.UUIDField(required=False, allow_null=True)


class AnalyzedProfileModelSerializer(serializers.ModelSerializer):
    """Serializer for AnalyzedProfile model"""
    class Meta:
        model = AnalyzedProfile
        fields = [
            'id', 'user_id', 'name', 'headline', 'linkedin_profile',
            'confidence', 'dominance', 'influence', 'steadiness', 'compliance',
            'disc_primary', 'key_insights', 'pain_points', 'communication_style',
            'sales_approach', 'best_approach', 'ideal_pitch',
            'communication_dos', 'communication_donts', 'raw_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
