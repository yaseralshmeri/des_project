"""
Serializers for Notification models
مسلسلات نماذج الإشعارات
"""

from rest_framework import serializers
from .models import (
    Notification,
    NotificationType,
    NotificationTemplate,
    UserNotificationPreference,
    NotificationDelivery
)


class NotificationTypeSerializer(serializers.ModelSerializer):
    """Serializer for NotificationType model"""
    
    class Meta:
        model = NotificationType
        fields = [
            'id', 'name', 'type_category', 'description', 
            'is_active', 'priority_level', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    priority_display = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'notification_type_name',
            'recipient', 'sender', 'sender_name', 'is_read', 'read_at', 'priority',
            'priority_display', 'send_email', 'send_sms', 'email_sent', 'sms_sent',
            'scheduled_at', 'expires_at', 'is_expired', 'related_object_type',
            'related_object_id', 'action_url', 'action_text', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'notification_type_name', 
            'priority_display', 'is_expired', 'email_sent', 'sms_sent',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Set sender to current user"""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'subject_template', 'message_template',
            'notification_type', 'notification_type_name', 'default_priority',
            'default_send_email', 'default_send_sms', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'notification_type_name', 'created_at', 'updated_at']


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserNotificationPreference model"""
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'id', 'user', 'receive_email', 'receive_sms', 'receive_push',
            'academic_notifications', 'financial_notifications',
            'administrative_notifications', 'emergency_notifications',
            'announcement_notifications', 'reminder_notifications',
            'system_notifications', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Set user to current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NotificationDeliverySerializer(serializers.ModelSerializer):
    """Serializer for NotificationDelivery model"""
    
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationDelivery
        fields = [
            'id', 'notification', 'notification_title', 'method', 'status',
            'attempt_count', 'last_attempt_at', 'delivered_at',
            'error_message', 'external_id', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'notification_title', 'created_at', 'updated_at'
        ]


class NotificationSummarySerializer(serializers.Serializer):
    """Serializer for notification summary data"""
    
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    by_priority = serializers.DictField()
    by_type = serializers.DictField()


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for sending notifications"""
    
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    recipients = serializers.CharField(help_text="'all' or comma-separated user IDs")
    notification_type = serializers.CharField(required=False)
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, default=2)
    send_email = serializers.BooleanField(default=False)
    send_sms = serializers.BooleanField(default=False)
    action_url = serializers.URLField(required=False, allow_blank=True)
    action_text = serializers.CharField(max_length=50, required=False, allow_blank=True)
    scheduled_at = serializers.DateTimeField(required=False)
    expires_at = serializers.DateTimeField(required=False)