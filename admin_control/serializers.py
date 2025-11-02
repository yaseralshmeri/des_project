# نظام التحكم الإداري - المسلسلات
# Admin Control System - Serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    UserActivity, SystemAlert, SystemConfiguration,
    AuditLog, BackupRecord, MaintenanceSchedule,
    SystemMetrics, UserSession
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


class UserActivitySerializer(serializers.ModelSerializer):
    """مسلسل أنشطة المستخدمين"""
    
    user = UserBasicSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)


class SystemAlertSerializer(serializers.ModelSerializer):
    """مسلسل تنبيهات النظام"""
    
    created_by = UserBasicSerializer(read_only=True)
    acknowledged_by = UserBasicSerializer(read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = SystemAlert
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """مسلسل إعدادات النظام"""
    
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)
    config_category_display = serializers.CharField(source='get_config_category_display', read_only=True)
    
    class Meta:
        model = SystemConfiguration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """مسلسل سجل المراجعة"""
    
    user = UserBasicSerializer(read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class BackupRecordSerializer(serializers.ModelSerializer):
    """مسلسل سجلات النسخ الاحتياطية"""
    
    created_by = UserBasicSerializer(read_only=True)
    backup_type_display = serializers.CharField(source='get_backup_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BackupRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    """مسلسل جدولة الصيانة"""
    
    created_by = UserBasicSerializer(read_only=True)
    assigned_to = UserBasicSerializer(read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemMetricsSerializer(serializers.ModelSerializer):
    """مسلسل مقاييس النظام"""
    
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = SystemMetrics
        fields = '__all__'
        read_only_fields = ['id', 'recorded_at']


class UserSessionSerializer(serializers.ModelSerializer):
    """مسلسل جلسات المستخدمين"""
    
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserSession
        fields = '__all__'
        read_only_fields = ['id', 'login_time', 'last_activity']


# مسلسلات للإحصائيات والتقارير
class SystemStatisticsSerializer(serializers.Serializer):
    """مسلسل إحصائيات النظام"""
    
    total_users = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    total_activities = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    system_uptime = serializers.FloatField()
    database_size = serializers.FloatField()
    storage_usage = serializers.FloatField()


class ActivityReportSerializer(serializers.Serializer):
    """مسلسل تقرير الأنشطة"""
    
    date = serializers.DateField()
    total_activities = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    most_active_user = serializers.CharField()
    top_actions = serializers.ListField()


class AlertSummarySerializer(serializers.Serializer):
    """مسلسل ملخص التنبيهات"""
    
    total_alerts = serializers.IntegerField()
    critical_count = serializers.IntegerField()
    high_count = serializers.IntegerField()
    medium_count = serializers.IntegerField()
    low_count = serializers.IntegerField()
    unacknowledged_count = serializers.IntegerField()


# مسلسلات مبسطة للإنشاء
class SystemAlertCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء تنبيه النظام"""
    
    class Meta:
        model = SystemAlert
        fields = ['title', 'message', 'alert_type', 'severity', 'target_users']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class SystemConfigurationUpdateSerializer(serializers.ModelSerializer):
    """مسلسل تحديث إعدادات النظام"""
    
    class Meta:
        model = SystemConfiguration
        fields = ['config_value', 'is_active']
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user:
            instance.updated_by = request.user
        return super().update(instance, validated_data)


class MaintenanceScheduleCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء جدولة صيانة"""
    
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'title', 'description', 'maintenance_type', 'priority',
            'scheduled_date', 'estimated_duration', 'assigned_to'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)