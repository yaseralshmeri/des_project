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
                'email_enrollment': True,
                'email_grades': True,
                'email_payments': True,
                'email_reminders': True,
                'email_announcements': True,
                'sms_enabled': False,
                'sms_urgent_only': True,
                'sms_payments': True,
                'sms_reminders': False,
                'in_app_enabled': True,
                'in_app_sound': True,
                'push_enabled': True,
                'push_grades': True,
                'push_reminders': True,
            }
        )