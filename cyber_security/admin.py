# نظام الأمان السيبراني - لوحة التحكم الإدارية
# Cybersecurity System - Admin Interface

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    SecurityEvent, SecurityThreat, SecurityIncident, SecurityAuditLog,
    SecurityPolicy, ThreatIntelligence, SecurityRule, SecurityDashboard,
    UserBehaviorProfile, SecurityConfiguration, VulnerabilityAssessment
)


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """إدارة أحداث الأمان السيبراني"""
    
    list_display = [
        'title', 'event_type', 'severity', 'affected_user', 
        'source_ip', 'status', 'created_at'
    ]
    list_filter = [
        'event_type', 'severity', 'status', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'source_ip', 'affected_user__username'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('title', 'event_type', 'description', 'severity', 'status')
        }),
        ('تفاصيل المصدر', {
            'fields': ('source_ip', 'user_agent', 'affected_user')
        }),
        ('تفاصيل إضافية', {
            'fields': ('additional_data', 'risk_score')
        }),
        ('معلومات المعالجة', {
            'fields': ('assigned_to', 'resolution_notes', 'resolved_at')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at', 'detected_by'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('affected_user', 'assigned_to')


@admin.register(SecurityThreat)
class SecurityThreatAdmin(admin.ModelAdmin):
    """إدارة التهديدات الأمنية"""
    
    list_display = [
        'threat_id', 'title', 'threat_type', 'severity_level',
        'risk_score', 'status', 'first_detected'
    ]
    list_filter = [
        'threat_type', 'severity_level', 'status', 'first_detected'
    ]
    search_fields = [
        'threat_id', 'title', 'description', 'source_ip'
    ]
    readonly_fields = ['id', 'threat_id', 'first_detected', 'last_seen']
    
    fieldsets = (
        ('معلومات التهديد', {
            'fields': ('threat_id', 'threat_type', 'title', 'description')
        }),
        ('تقييم الخطر', {
            'fields': ('severity_level', 'risk_score')
        }),
        ('معلومات المصدر', {
            'fields': ('source_ip', 'source_country', 'source_user_agent')
        }),
        ('التأثير', {
            'fields': ('affected_user', 'affected_resources')
        }),
        ('تفاصيل الهجوم', {
            'fields': ('attack_vector', 'attack_signature', 'payload', 'request_details')
        }),
        ('الاستجابة', {
            'fields': ('status', 'automated_response', 'manual_actions')
        }),
        ('التحليل', {
            'fields': ('assigned_analyst', 'analysis_notes', 'resolved_at')
        }),
        ('استخبارات التهديد', {
            'fields': ('indicators_of_compromise', 'threat_intelligence'),
            'classes': ('collapse',)
        })
    )


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    """إدارة الحوادث الأمنية"""
    
    list_display = [
        'incident_id', 'title', 'incident_type', 'impact_level',
        'status', 'estimated_cost', 'created_at'
    ]
    list_filter = [
        'incident_type', 'impact_level', 'status', 'created_at'
    ]
    search_fields = [
        'incident_id', 'title', 'description'
    ]
    readonly_fields = ['id', 'incident_id', 'created_at', 'updated_at']
    filter_horizontal = ['affected_users']


@admin.register(SecurityAuditLog)
class SecurityAuditLogAdmin(admin.ModelAdmin):
    """إدارة سجلات المراجعة الأمنية"""
    
    list_display = [
        'user', 'action_type', 'result', 'ip_address', 
        'resource_accessed', 'timestamp'
    ]
    list_filter = [
        'action_type', 'result', 'timestamp'
    ]
    search_fields = [
        'user__username', 'action_description', 'ip_address'
    ]
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # منع الإضافة اليدوية
    
    def has_change_permission(self, request, obj=None):
        return False  # منع التعديل


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    """إدارة سياسات الأمان"""
    
    list_display = [
        'name_ar', 'code', 'category', 'enforcement_level',
        'is_active', 'is_mandatory', 'violations_count'
    ]
    list_filter = [
        'category', 'enforcement_level', 'is_active', 'is_mandatory'
    ]
    search_fields = [
        'name_ar', 'name_en', 'code', 'description'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'violations_count', 'last_violation']
    filter_horizontal = ['applies_to_users']
    
    fieldsets = (
        ('معلومات السياسة', {
            'fields': ('name_ar', 'name_en', 'code', 'description', 'category')
        }),
        ('التطبيق', {
            'fields': ('enforcement_level', 'is_active', 'is_mandatory')
        }),
        ('قواعد السياسة', {
            'fields': ('policy_rules', 'parameters', 'exceptions')
        }),
        ('النطاق', {
            'fields': ('applies_to_users', 'applies_to_ip_ranges', 'applies_to_systems')
        }),
        ('التوقيت', {
            'fields': ('effective_from', 'effective_until')
        }),
        ('المراجعة', {
            'fields': ('approved_by', 'approved_at', 'review_frequency', 'last_reviewed')
        }),
        ('إحصائيات', {
            'fields': ('violations_count', 'last_violation'),
            'classes': ('collapse',)
        })
    )


@admin.register(SecurityConfiguration)
class SecurityConfigurationAdmin(admin.ModelAdmin):
    """إدارة إعدادات الأمان"""
    
    list_display = [
        'config_name', 'config_type', 'is_active', 
        'is_compliant', 'last_reviewed_date'
    ]
    list_filter = [
        'config_type', 'is_active', 'is_compliant', 'is_mandatory'
    ]
    search_fields = [
        'config_name', 'description'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'needs_review']
    
    def needs_review(self, obj):
        return obj.needs_review
    needs_review.boolean = True
    needs_review.short_description = 'يحتاج مراجعة'


@admin.register(VulnerabilityAssessment)
class VulnerabilityAssessmentAdmin(admin.ModelAdmin):
    """إدارة تقييمات الثغرات الأمنية"""
    
    list_display = [
        'vulnerability_id', 'title', 'vulnerability_type',
        'severity_level', 'cvss_score', 'status', 'due_date'
    ]
    list_filter = [
        'vulnerability_type', 'severity_level', 'status', 
        'affected_system', 'discovered_date'
    ]
    search_fields = [
        'vulnerability_id', 'title', 'description', 'affected_system'
    ]
    readonly_fields = ['id', 'vulnerability_id', 'discovered_date', 'created_at', 'updated_at']


# تخصيص موقع الإدارة
admin.site.site_header = "نظام الأمان السيبراني - لوحة التحكم"
admin.site.site_title = "إدارة الأمان السيبراني"
admin.site.index_title = "مرحباً بك في نظام الأمان السيبراني"


# إضافة إجراءات مخصصة
def mark_as_resolved(modeladmin, request, queryset):
    """وضع علامة محلول على العناصر المحددة"""
    queryset.update(status='RESOLVED', resolved_at=timezone.now())
mark_as_resolved.short_description = "وضع علامة محلول"

def activate_items(modeladmin, request, queryset):
    """تفعيل العناصر المحددة"""
    queryset.update(is_active=True)
activate_items.short_description = "تفعيل المحدد"

def deactivate_items(modeladmin, request, queryset):
    """إلغاء تفعيل العناصر المحددة"""
    queryset.update(is_active=False)
deactivate_items.short_description = "إلغاء تفعيل المحدد"

# إضافة الإجراءات للنماذج المناسبة
SecurityEventAdmin.actions = [mark_as_resolved]
SecurityThreatAdmin.actions = [mark_as_resolved]
SecurityIncidentAdmin.actions = [mark_as_resolved]
SecurityPolicyAdmin.actions = [activate_items, deactivate_items]
SecurityConfigurationAdmin.actions = [activate_items, deactivate_items]