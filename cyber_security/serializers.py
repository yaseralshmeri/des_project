# نظام الأمان السيبراني - المسلسلات
# Cybersecurity System - Serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SecurityEvent, SecurityThreat, SecurityIncident, SecurityAuditLog,
    SecurityPolicy, ThreatIntelligence, SecurityRule, SecurityDashboard,
    UserBehaviorProfile, SecurityConfiguration, VulnerabilityAssessment
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """مسلسل المستخدم الأساسي"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class SecurityEventSerializer(serializers.ModelSerializer):
    """مسلسل أحداث الأمان السيبراني"""
    
    affected_user = UserBasicSerializer(read_only=True)
    assigned_to = UserBasicSerializer(read_only=True)
    detected_by = UserBasicSerializer(read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_critical = serializers.ReadOnlyField()
    is_resolved = serializers.ReadOnlyField()
    days_open = serializers.ReadOnlyField()
    
    class Meta:
        model = SecurityEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['detected_by'] = request.user
        return super().create(validated_data)


class SecurityThreatSerializer(serializers.ModelSerializer):
    """مسلسل التهديدات الأمنية"""
    
    affected_user = UserBasicSerializer(read_only=True)
    assigned_analyst = UserBasicSerializer(read_only=True)
    threat_type_display = serializers.CharField(source='get_threat_type_display', read_only=True)
    severity_level_display = serializers.CharField(source='get_severity_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.ReadOnlyField()
    response_time = serializers.ReadOnlyField()
    
    class Meta:
        model = SecurityThreat
        fields = '__all__'
        read_only_fields = ['id', 'threat_id', 'first_detected', 'last_seen', 'created_at', 'updated_at']


class SecurityIncidentSerializer(serializers.ModelSerializer):
    """مسلسل الحوادث الأمنية"""
    
    incident_commander = UserBasicSerializer(read_only=True)
    affected_users = UserBasicSerializer(many=True, read_only=True)
    incident_type_display = serializers.CharField(source='get_incident_type_display', read_only=True)
    impact_level_display = serializers.CharField(source='get_impact_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SecurityIncident
        fields = '__all__'
        read_only_fields = ['id', 'incident_id', 'created_at', 'updated_at']


class SecurityAuditLogSerializer(serializers.ModelSerializer):
    """مسلسل سجلات المراجعة الأمنية"""
    
    user = UserBasicSerializer(read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    
    class Meta:
        model = SecurityAuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']
    
    def create(self, validated_data):
        # تلقائياً ربط المستخدم الحالي
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)


class SecurityPolicySerializer(serializers.ModelSerializer):
    """مسلسل سياسات الأمان"""
    
    applies_to_users = UserBasicSerializer(many=True, read_only=True)
    approved_by = UserBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    enforcement_level_display = serializers.CharField(source='get_enforcement_level_display', read_only=True)
    is_effective = serializers.ReadOnlyField()
    
    class Meta:
        model = SecurityPolicy
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'violations_count', 'last_violation']


class SecurityConfigurationSerializer(serializers.ModelSerializer):
    """مسلسل إعدادات الأمان"""
    
    owner = UserBasicSerializer(read_only=True)
    last_reviewed_by = UserBasicSerializer(read_only=True)
    last_changed_by = UserBasicSerializer(read_only=True)
    config_type_display = serializers.CharField(source='get_config_type_display', read_only=True)
    needs_review = serializers.ReadOnlyField()
    is_out_of_compliance = serializers.ReadOnlyField()
    
    class Meta:
        model = SecurityConfiguration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class VulnerabilityAssessmentSerializer(serializers.ModelSerializer):
    """مسلسل تقييمات الثغرات الأمنية"""
    
    discovered_by = UserBasicSerializer(read_only=True)
    assigned_to = UserBasicSerializer(read_only=True)
    vulnerability_type_display = serializers.CharField(source='get_vulnerability_type_display', read_only=True)
    severity_level_display = serializers.CharField(source='get_severity_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = VulnerabilityAssessment
        fields = '__all__'
        read_only_fields = ['id', 'vulnerability_id', 'discovered_date', 'created_at', 'updated_at']


# مسلسلات للإحصائيات والتقارير
class SecurityDashboardSerializer(serializers.Serializer):
    """مسلسل لوحة معلومات الأمان"""
    
    total_events = serializers.IntegerField()
    critical_events = serializers.IntegerField()
    open_threats = serializers.IntegerField()
    active_incidents = serializers.IntegerField()
    recent_activities = SecurityAuditLogSerializer(many=True, read_only=True)
    threat_distribution = serializers.DictField()
    risk_score_average = serializers.FloatField()


class SecurityStatisticsSerializer(serializers.Serializer):
    """مسلسل إحصائيات الأمان"""
    
    events_by_type = serializers.DictField()
    threats_by_severity = serializers.DictField()
    incidents_by_impact = serializers.DictField()
    monthly_trends = serializers.DictField()
    compliance_status = serializers.DictField()


class ThreatIntelligenceSerializer(serializers.ModelSerializer):
    """مسلسل استخبارات التهديد"""
    
    class Meta:
        model = ThreatIntelligence
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SecurityRuleSerializer(serializers.ModelSerializer):
    """مسلسل قواعد الأمان"""
    
    created_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = SecurityRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserBehaviorProfileSerializer(serializers.ModelSerializer):
    """مسلسل ملفات السلوك للمستخدمين"""
    
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserBehaviorProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# مسلسلات للعمليات المتقدمة
class SecurityEventCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء أحداث الأمان (مبسط)"""
    
    class Meta:
        model = SecurityEvent
        fields = ['title', 'event_type', 'description', 'severity', 'source_ip', 'additional_data']


class SecurityThreatCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء التهديدات الأمنية (مبسط)"""
    
    class Meta:
        model = SecurityThreat
        fields = [
            'threat_type', 'title', 'description', 'severity_level',
            'source_ip', 'attack_vector', 'indicators_of_compromise'
        ]


class SecurityIncidentCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء الحوادث الأمنية (مبسط)"""
    
    class Meta:
        model = SecurityIncident
        fields = [
            'incident_type', 'title', 'description', 'impact_level',
            'affected_systems', 'affected_data_types'
        ]


# مسلسلات للبحث والتصفية
class SecurityEventFilterSerializer(serializers.Serializer):
    """مسلسل تصفية أحداث الأمان"""
    
    event_type = serializers.ChoiceField(choices=SecurityEvent.EVENT_TYPES, required=False)
    severity = serializers.ChoiceField(choices=SecurityEvent.SEVERITY_LEVELS, required=False)
    status = serializers.ChoiceField(choices=SecurityEvent.STATUS_CHOICES, required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    source_ip = serializers.IPAddressField(required=False)


class SecurityThreatFilterSerializer(serializers.Serializer):
    """مسلسل تصفية التهديدات الأمنية"""
    
    threat_type = serializers.ChoiceField(choices=SecurityThreat.THREAT_TYPES, required=False)
    severity_level = serializers.ChoiceField(choices=SecurityThreat.SEVERITY_LEVELS, required=False)
    status = serializers.ChoiceField(choices=SecurityThreat.STATUS_CHOICES, required=False)
    risk_score_min = serializers.FloatField(required=False)
    risk_score_max = serializers.FloatField(required=False)