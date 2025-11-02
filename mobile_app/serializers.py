# تطبيق الهاتف المحمول - المسلسلات
# Mobile App - Serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    MobileDevice, MobileAppSession, MobilePushNotification,
    MobileAppFeedback, MobileAppAnalytics
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


class MobileDeviceSerializer(serializers.ModelSerializer):
    """مسلسل الأجهزة المحمولة"""
    
    user = UserBasicSerializer(read_only=True)
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MobileDevice
        fields = '__all__'
        read_only_fields = ['id', 'device_id', 'last_login', 'last_seen', 'created_at', 'updated_at']


class MobileDeviceCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء جهاز محمول"""
    
    class Meta:
        model = MobileDevice
        fields = [
            'device_name', 'device_type', 'device_model',
            'operating_system', 'os_version', 'app_version', 'fcm_token'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        
        # توليد device_id فريد
        import hashlib
        import time
        device_string = f"{validated_data.get('device_name', '')}{time.time()}"
        device_id = hashlib.md5(device_string.encode()).hexdigest()
        validated_data['device_id'] = device_id
        
        return super().create(validated_data)


class MobileAppSessionSerializer(serializers.ModelSerializer):
    """مسلسل جلسات التطبيق المحمول"""
    
    device = MobileDeviceSerializer(read_only=True)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = MobileAppSession
        fields = '__all__'
        read_only_fields = ['id', 'session_id', 'start_time', 'end_time', 'last_activity']


class MobilePushNotificationSerializer(serializers.ModelSerializer):
    """مسلسل إشعارات الدفع المحمولة"""
    
    device = MobileDeviceSerializer(read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MobilePushNotification
        fields = '__all__'
        read_only_fields = ['id', 'sent_at', 'delivered_at', 'clicked_at', 'created_at', 'updated_at']


class MobileAppFeedbackSerializer(serializers.ModelSerializer):
    """مسلسل ملاحظات التطبيق المحمول"""
    
    user = UserBasicSerializer(read_only=True)
    device = MobileDeviceSerializer(read_only=True)
    assigned_to = UserBasicSerializer(read_only=True)
    feedback_type_display = serializers.CharField(source='get_feedback_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = MobileAppFeedback
        fields = '__all__'
        read_only_fields = ['id', 'resolved_at', 'created_at', 'updated_at']


class MobileAppFeedbackCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء ملاحظة التطبيق المحمول"""
    
    device_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = MobileAppFeedback
        fields = [
            'feedback_type', 'subject', 'description', 'rating',
            'app_version', 'device_info', 'error_log', 'screenshots',
            'device_id'
        ]
    
    def create(self, validated_data):
        device_id = validated_data.pop('device_id', None)
        
        # ربط بجهاز المستخدم
        if device_id:
            try:
                device = MobileDevice.objects.get(
                    device_id=device_id,
                    user=self.context['request'].user
                )
                validated_data['device'] = device
            except MobileDevice.DoesNotExist:
                pass
        
        return super().create(validated_data)


class MobileAppAnalyticsSerializer(serializers.ModelSerializer):
    """مسلسل تحليلات التطبيق المحمول"""
    
    device = MobileDeviceSerializer(read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = MobileAppAnalytics
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


# مسلسلات للإحصائيات
class MobileAppStatsSerializer(serializers.Serializer):
    """مسلسل إحصائيات التطبيق المحمول"""
    
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    trusted_devices = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    average_session_duration = serializers.FloatField()
    device_types = serializers.DictField()
    app_versions = serializers.DictField()


class UserMobileStatsSerializer(serializers.Serializer):
    """مسلسل إحصائيات المستخدم المحمولة"""
    
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    feedback_count = serializers.IntegerField()
    pending_feedback = serializers.IntegerField()
    last_session = MobileAppSessionSerializer(required=False)


class DeviceUsageReportSerializer(serializers.Serializer):
    """مسلسل تقرير استخدام الأجهزة"""
    
    device = MobileDeviceSerializer()
    session_count = serializers.IntegerField()
    total_usage_hours = serializers.FloatField()
    last_usage = serializers.DateTimeField()
    app_events = serializers.IntegerField()


class FeedbackSummarySerializer(serializers.Serializer):
    """مسلسل ملخص الملاحظات"""
    
    total_feedback = serializers.IntegerField()
    by_type = serializers.DictField()
    by_status = serializers.DictField()
    by_rating = serializers.DictField()
    average_rating = serializers.FloatField()
    pending_count = serializers.IntegerField()