from django.contrib import admin
from django.utils.html import format_html
from .models import AnalyzedProfile

# Customize Django Admin Site
admin.site.site_header = "LinkedIn DISC Analyzer"
admin.site.site_title = "LinkedIn DISC Analyzer"
admin.site.index_title = "Welcome to LinkedIn DISC Analyzer Administration"


# Custom Filters
class ConfidenceLevelFilter(admin.SimpleListFilter):
    title = 'Confidence Level'
    parameter_name = 'confidence_level'

    def lookups(self, request, model_admin):
        return (
            ('high', 'High (80-100)'),
            ('medium', 'Medium (50-79)'),
            ('low', 'Low (0-49)'),
            ('none', 'No Confidence Score'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(confidence__gte=80)
        if self.value() == 'medium':
            return queryset.filter(confidence__gte=50, confidence__lt=80)
        if self.value() == 'low':
            return queryset.filter(confidence__lt=50, confidence__isnull=False)
        if self.value() == 'none':
            return queryset.filter(confidence__isnull=True)


class DISCScoreFilter(admin.SimpleListFilter):
    title = 'DISC Score Range'
    parameter_name = 'disc_score'
    score_field = None  # Will be set by subclasses

    def lookups(self, request, model_admin):
        return (
            ('high', 'High (70-100)'),
            ('medium', 'Medium (40-69)'),
            ('low', 'Low (0-39)'),
            ('none', 'No Score'),
        )

    def queryset(self, request, queryset):
        if self.score_field:
            if self.value() == 'high':
                return queryset.filter(**{f'{self.score_field}__gte': 70})
            if self.value() == 'medium':
                return queryset.filter(**{f'{self.score_field}__gte': 40, f'{self.score_field}__lt': 70})
            if self.value() == 'low':
                return queryset.filter(**{f'{self.score_field}__lt': 40, f'{self.score_field}__isnull': False})
            if self.value() == 'none':
                return queryset.filter(**{f'{self.score_field}__isnull': True})
        return queryset


class DominanceFilter(DISCScoreFilter):
    title = 'Dominance Score'
    parameter_name = 'dominance_score'
    score_field = 'dominance'


class InfluenceFilter(DISCScoreFilter):
    title = 'Influence Score'
    parameter_name = 'influence_score'
    score_field = 'influence'


class SteadinessFilter(DISCScoreFilter):
    title = 'Steadiness Score'
    parameter_name = 'steadiness_score'
    score_field = 'steadiness'


class ComplianceFilter(DISCScoreFilter):
    title = 'Compliance Score'
    parameter_name = 'compliance_score'
    score_field = 'compliance'


class HasInsightsFilter(admin.SimpleListFilter):
    title = 'Has Key Insights'
    parameter_name = 'has_insights'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Insights'),
            ('no', 'No Insights'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(key_insights__isnull=True).exclude(key_insights=[])
        if self.value() == 'no':
            return queryset.filter(key_insights__isnull=True) | queryset.filter(key_insights=[])


class HasPainPointsFilter(admin.SimpleListFilter):
    title = 'Has Pain Points'
    parameter_name = 'has_pain_points'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Pain Points'),
            ('no', 'No Pain Points'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(pain_points__isnull=True).exclude(pain_points=[])
        if self.value() == 'no':
            return queryset.filter(pain_points__isnull=True) | queryset.filter(pain_points=[])


class HasCommunicationStyleFilter(admin.SimpleListFilter):
    title = 'Has Communication Style'
    parameter_name = 'has_comm_style'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Communication Style'),
            ('no', 'No Communication Style'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(communication_style__isnull=True).exclude(communication_style='')
        if self.value() == 'no':
            return queryset.filter(communication_style__isnull=True) | queryset.filter(communication_style='')


class HasSalesApproachFilter(admin.SimpleListFilter):
    title = 'Has Sales Approach'
    parameter_name = 'has_sales_approach'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Sales Approach'),
            ('no', 'No Sales Approach'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(sales_approach__isnull=True).exclude(sales_approach='')
        if self.value() == 'no':
            return queryset.filter(sales_approach__isnull=True) | queryset.filter(sales_approach='')


@admin.register(AnalyzedProfile)
class AnalyzedProfileAdmin(admin.ModelAdmin):
    # Display all relevant fields in list view
    list_display = [
        'name', 'linkedin_profile_link', 'headline_short', 'disc_primary', 'confidence', 
        'dominance', 'influence', 'steadiness', 'compliance', 
        'communication_style_short', 'sales_approach_short', 
        'key_insights_count', 'pain_points_count', 
        'communication_dos_count', 'communication_donts_count',
        'created_at'
    ]
    
    list_filter = [
        'disc_primary',
        ConfidenceLevelFilter,
        DominanceFilter,
        InfluenceFilter,
        SteadinessFilter,
        ComplianceFilter,
        HasInsightsFilter,
        HasPainPointsFilter,
        HasCommunicationStyleFilter,
        HasSalesApproachFilter,
        'created_at',
    ]
    search_fields = [
        'name', 'headline', 'linkedin_profile', 'disc_primary', 
        'communication_style', 'sales_approach', 'best_approach', 
        'ideal_pitch', 'user_id'
    ]
    readonly_fields = [
        'id', 'created_at', 'key_insights_display', 'pain_points_display',
        'communication_dos_display', 'communication_donts_display'
    ]
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    # Custom display methods for list view
    def headline_short(self, obj):
        if obj.headline:
            return obj.headline[:50] + '...' if len(obj.headline) > 50 else obj.headline
        return '-'
    headline_short.short_description = 'Headline'
    headline_short.admin_order_field = 'headline'
    
    def communication_style_short(self, obj):
        if obj.communication_style:
            return obj.communication_style[:40] + '...' if len(obj.communication_style) > 40 else obj.communication_style
        return '-'
    communication_style_short.short_description = 'Comm Style'
    communication_style_short.admin_order_field = 'communication_style'
    
    def sales_approach_short(self, obj):
        if obj.sales_approach:
            return obj.sales_approach[:40] + '...' if len(obj.sales_approach) > 40 else obj.sales_approach
        return '-'
    sales_approach_short.short_description = 'Sales Approach'
    sales_approach_short.admin_order_field = 'sales_approach'
    
    def key_insights_count(self, obj):
        if obj.key_insights and isinstance(obj.key_insights, list):
            count = len(obj.key_insights)
            return f"{count} insight{'s' if count != 1 else ''}"
        return '0 insights'
    key_insights_count.short_description = 'Key Insights'
    
    def pain_points_count(self, obj):
        if obj.pain_points and isinstance(obj.pain_points, list):
            count = len(obj.pain_points)
            return f"{count} point{'s' if count != 1 else ''}"
        return '0 points'
    pain_points_count.short_description = 'Pain Points'
    
    def communication_dos_count(self, obj):
        if obj.communication_dos and isinstance(obj.communication_dos, list):
            count = len(obj.communication_dos)
            return f"{count} do{'s' if count != 1 else ''}"
        return '0 dos'
    communication_dos_count.short_description = 'Do\'s'
    
    def communication_donts_count(self, obj):
        if obj.communication_donts and isinstance(obj.communication_donts, list):
            count = len(obj.communication_donts)
            return f"{count} don't{'s' if count != 1 else ''}"
        return '0 don\'ts'
    communication_donts_count.short_description = 'Don\'ts'
    
    def linkedin_profile_link(self, obj):
        if obj.linkedin_profile:
            return format_html('<a href="{}" target="_blank">View Profile</a>', obj.linkedin_profile)
        return '-'
    linkedin_profile_link.short_description = 'LinkedIn'
    
    # Custom display methods for detail view (JSON fields)
    def key_insights_display(self, obj):
        """Display key insights as a formatted list"""
        if obj.key_insights and isinstance(obj.key_insights, list) and len(obj.key_insights) > 0:
            html = '<ul style="margin: 5px 0; padding-left: 20px;">'
            for insight in obj.key_insights:
                html += f'<li>{insight}</li>'
            html += '</ul>'
            return format_html(html)
        return 'No key insights available'
    key_insights_display.short_description = 'Key Insights (Formatted)'
    
    def pain_points_display(self, obj):
        """Display pain points as a formatted list"""
        if obj.pain_points and isinstance(obj.pain_points, list) and len(obj.pain_points) > 0:
            html = '<ul style="margin: 5px 0; padding-left: 20px;">'
            for point in obj.pain_points:
                html += f'<li>{point}</li>'
            html += '</ul>'
            return format_html(html)
        return 'No pain points available'
    pain_points_display.short_description = 'Pain Points (Formatted)'
    
    def communication_dos_display(self, obj):
        """Display communication do's as a formatted list"""
        if obj.communication_dos and isinstance(obj.communication_dos, list) and len(obj.communication_dos) > 0:
            html = '<ul style="margin: 5px 0; padding-left: 20px;">'
            for do in obj.communication_dos:
                html += f'<li>{do}</li>'
            html += '</ul>'
            return format_html(html)
        return 'No communication do\'s available'
    communication_dos_display.short_description = 'Communication Do\'s (Formatted)'
    
    def communication_donts_display(self, obj):
        """Display communication don'ts as a formatted list"""
        if obj.communication_donts and isinstance(obj.communication_donts, list) and len(obj.communication_donts) > 0:
            html = '<ul style="margin: 5px 0; padding-left: 20px;">'
            for dont in obj.communication_donts:
                html += f'<li>{dont}</li>'
            html += '</ul>'
            return format_html(html)
        return 'No communication don\'ts available'
    communication_donts_display.short_description = 'Communication Don\'ts (Formatted)'
    
    # Enhanced fieldsets with all fields properly organized
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user_id', 'name', 'headline', 'linkedin_profile')
        }),
        ('DISC Personality Analysis', {
            'fields': ('confidence', 'dominance', 'influence', 'steadiness', 'compliance', 'disc_primary')
        }),
        ('Analysis Insights', {
            'fields': ('key_insights', 'key_insights_display', 'pain_points', 'pain_points_display', 'communication_style')
        }),
        ('Sales Strategy', {
            'fields': ('sales_approach', 'best_approach', 'ideal_pitch')
        }),
        ('Communication Guidelines', {
            'fields': ('communication_dos', 'communication_dos_display', 'communication_donts', 'communication_donts_display')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',),
            'description': 'Full analysis response from Gemini API'
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
