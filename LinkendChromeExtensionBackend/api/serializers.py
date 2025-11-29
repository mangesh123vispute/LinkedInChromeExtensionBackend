from rest_framework import serializers
from .models import Profile


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


class ProfileSaveSerializer(serializers.Serializer):
    """Serializer for saving profile with analysis data"""
    profile_data = ProfileDataSerializer()
    analysis_data = AnalysisResponseSerializer()
    user_id = serializers.UUIDField(required=False, allow_null=True)


class ProfileModelSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'linkedin_url', 'name', 'headline', 'disc_primary', 
                  'disc_breakdown', 'raw_data', 'created_at']
        read_only_fields = ['id', 'created_at']
