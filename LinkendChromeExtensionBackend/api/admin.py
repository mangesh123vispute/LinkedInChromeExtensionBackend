from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'headline', 'disc_primary', 'linkedin_url', 'created_at']
    list_filter = ['disc_primary', 'created_at']
    search_fields = ['name', 'headline', 'linkedin_url']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user_id', 'name', 'headline', 'linkedin_url')
        }),
        ('DISC Analysis', {
            'fields': ('disc_primary', 'disc_breakdown')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
