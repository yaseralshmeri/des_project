"""
Notification Signals
Automatically create notifications for various system events
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings


@receiver(post_save, sender='students.User')
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users"""
    if created:
        from .models import NotificationPreference
        NotificationPreference.objects.get_or_create(
            user=instance,
            defaults={
                'email_enabled': True,
                'sms_enabled': False,
                'push_enabled': True,
                'in_app_enabled': True,
                'telegram_enabled': False,
                'academic_notifications': True,
                'financial_notifications': True,
                'administrative_notifications': True,
                'security_notifications': True,
                'system_notifications': False,
                'urgent_only': False,
                'quiet_hours_enabled': False,
            }
        )