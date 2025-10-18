"""
Celery Tasks for Notifications
مهام Celery للإشعارات
"""

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
import logging

from .models import Notification, NotificationTemplate
from .consumers import send_notification_to_user

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, notification_id):
    """Send email notification"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Get email template
        template = NotificationTemplate.objects.filter(
            code=notification.notification_type,
            notification_type='EMAIL',
            is_active=True
        ).first()
        
        if not template:
            template = NotificationTemplate.objects.filter(
                is_default=True,
                notification_type='EMAIL'
            ).first()
        
        if template:
            subject = template.subject_template.format(
                title=notification.title
            )
            message = template.body_template.format(
                title=notification.title,
                message=notification.message,
                user_name=notification.recipient.get_full_name(),
                action_url=notification.action_url or '',
                action_text=notification.action_text or ''
            )
        else:
            subject = notification.title
            message = notification.message
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            fail_silently=False,
        )
        
        # Update notification status
        notification.sent_at = timezone.now()
        notification.status = 'SENT'
        notification.save(update_fields=['sent_at', 'status'])
        
        logger.info(f"Email notification sent to {notification.recipient.username}")
        return f"Email sent to {notification.recipient.email}"
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return f"Notification {notification_id} not found"
    
    except Exception as exc:
        logger.error(f"Failed to send email notification: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def send_bulk_notifications(user_ids, title, message, notification_type='GENERAL', priority='NORMAL'):
    """Send notifications to multiple users"""
    notifications_created = 0
    
    try:
        users = User.objects.filter(id__in=user_ids, is_active=True)
        
        notifications = []
        for user in users:
            notification = Notification(
                recipient=user,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                status='PENDING'
            )
            notifications.append(notification)
        
        # Bulk create notifications
        created_notifications = Notification.objects.bulk_create(notifications)
        notifications_created = len(created_notifications)
        
        # Send real-time notifications via WebSocket
        for notification in created_notifications:
            send_notification_to_user.delay(
                notification.recipient.id,
                {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'priority': notification.priority,
                    'created_at': notification.created_at.isoformat(),
                    'action_url': notification.action_url,
                    'action_text': notification.action_text
                }
            )
        
        logger.info(f"Created {notifications_created} bulk notifications")
        return f"Created {notifications_created} notifications"
        
    except Exception as exc:
        logger.error(f"Failed to send bulk notifications: {str(exc)}")
        raise exc

@shared_task
def send_notification_by_role(role, title, message, notification_type='GENERAL', priority='NORMAL'):
    """Send notifications to all users with specific role"""
    try:
        from students.models import UserProfile
        
        users = User.objects.filter(
            profile__role=role,
            is_active=True
        )
        
        user_ids = list(users.values_list('id', flat=True))
        
        if user_ids:
            return send_bulk_notifications.delay(
                user_ids, title, message, notification_type, priority
            )
        else:
            logger.info(f"No users found with role {role}")
            return f"No users found with role {role}"
            
    except Exception as exc:
        logger.error(f"Failed to send role-based notifications: {str(exc)}")
        raise exc

@shared_task
def cleanup_old_notifications():
    """Clean up old read notifications"""
    try:
        # Delete read notifications older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = Notification.objects.filter(
            read_at__isnull=False,
            read_at__lt=cutoff_date
        ).delete()[0]
        
        # Delete unread notifications older than 90 days
        old_cutoff_date = timezone.now() - timedelta(days=90)
        old_deleted_count = Notification.objects.filter(
            read_at__isnull=True,
            created_at__lt=old_cutoff_date
        ).delete()[0]
        
        total_deleted = deleted_count + old_deleted_count
        logger.info(f"Cleaned up {total_deleted} old notifications")
        return f"Cleaned up {total_deleted} notifications"
        
    except Exception as exc:
        logger.error(f"Failed to cleanup notifications: {str(exc)}")
        raise exc

@shared_task
def send_weekly_digest():
    """Send weekly digest emails to users"""
    try:
        # Get all active users who want email notifications
        users = User.objects.filter(
            is_active=True,
            email__isnull=False
        ).exclude(email='')
        
        digest_count = 0
        
        for user in users:
            # Get user's notifications from the past week
            week_ago = timezone.now() - timedelta(days=7)
            notifications = Notification.objects.filter(
                recipient=user,
                created_at__gte=week_ago
            ).order_by('-created_at')[:20]
            
            if notifications.exists():
                # Render email template
                context = {
                    'user': user,
                    'notifications': notifications,
                    'week_start': week_ago,
                    'week_end': timezone.now()
                }
                
                html_content = render_to_string(
                    'email/weekly_digest.html', 
                    context
                )
                
                # Send email
                send_mail(
                    subject=f'ملخص أسبوعي - {settings.UNIVERSITY_NAME}',
                    message='',
                    html_message=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                
                digest_count += 1
        
        logger.info(f"Sent {digest_count} weekly digest emails")
        return f"Sent {digest_count} digest emails"
        
    except Exception as exc:
        logger.error(f"Failed to send weekly digest: {str(exc)}")
        raise exc

@shared_task(bind=True)
def send_sms_notification(self, phone_number, message):
    """Send SMS notification (requires SMS provider configuration)"""
    try:
        # This would integrate with your SMS provider
        # Example: Twilio, AWS SNS, etc.
        
        # Placeholder implementation
        logger.info(f"SMS would be sent to {phone_number}: {message}")
        
        # Simulate SMS sending
        import time
        time.sleep(1)  # Simulate API call delay
        
        return f"SMS sent to {phone_number}"
        
    except Exception as exc:
        logger.error(f"Failed to send SMS: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def send_push_notification(user_id, title, message, data=None):
    """Send push notification (requires push notification service)"""
    try:
        user = User.objects.get(id=user_id)
        
        # This would integrate with push notification service
        # Example: Firebase Cloud Messaging, Apple Push Notifications
        
        notification_data = {
            'title': title,
            'message': message,
            'data': data or {}
        }
        
        # Placeholder implementation
        logger.info(f"Push notification would be sent to {user.username}: {title}")
        
        return f"Push notification sent to {user.username}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for push notification")
        return f"User {user_id} not found"
    
    except Exception as exc:
        logger.error(f"Failed to send push notification: {str(exc)}")
        raise exc

@shared_task
def process_notification_queue():
    """Process pending notifications"""
    try:
        pending_notifications = Notification.objects.filter(
            status='PENDING'
        ).order_by('priority', 'created_at')[:100]
        
        processed_count = 0
        
        for notification in pending_notifications:
            # Send email if user has email enabled
            if notification.recipient.email:
                send_email_notification.delay(notification.id)
            
            # Send real-time notification
            send_notification_to_user.delay(
                notification.recipient.id,
                {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'priority': notification.priority,
                    'created_at': notification.created_at.isoformat(),
                    'action_url': notification.action_url,
                    'action_text': notification.action_text
                }
            )
            
            processed_count += 1
        
        logger.info(f"Processed {processed_count} pending notifications")
        return f"Processed {processed_count} notifications"
        
    except Exception as exc:
        logger.error(f"Failed to process notification queue: {str(exc)}")
        raise exc

@shared_task
def send_urgent_alert(title, message, user_ids=None, roles=None):
    """Send urgent alert to specified users or roles"""
    try:
        if user_ids:
            users = User.objects.filter(id__in=user_ids, is_active=True)
        elif roles:
            from students.models import UserProfile
            users = User.objects.filter(
                profile__role__in=roles,
                is_active=True
            )
        else:
            # Send to all active users
            users = User.objects.filter(is_active=True)
        
        notifications = []
        for user in users:
            notification = Notification(
                recipient=user,
                title=title,
                message=message,
                notification_type='URGENT',
                priority='URGENT',
                status='PENDING'
            )
            notifications.append(notification)
        
        # Bulk create notifications
        created_notifications = Notification.objects.bulk_create(notifications)
        
        # Send immediate notifications
        for notification in created_notifications:
            # Email
            if notification.recipient.email:
                send_email_notification.delay(notification.id)
            
            # Real-time
            send_notification_to_user.delay(
                notification.recipient.id,
                {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'priority': notification.priority,
                    'created_at': notification.created_at.isoformat(),
                    'action_url': notification.action_url,
                    'action_text': notification.action_text
                }
            )
        
        alert_count = len(created_notifications)
        logger.info(f"Sent urgent alert to {alert_count} users")
        return f"Urgent alert sent to {alert_count} users"
        
    except Exception as exc:
        logger.error(f"Failed to send urgent alert: {str(exc)}")
        raise exc

@shared_task
def generate_notification_analytics():
    """Generate notification analytics and metrics"""
    try:
        # Get notification metrics for the past 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        metrics = {
            'total_sent': Notification.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'total_read': Notification.objects.filter(
                created_at__gte=thirty_days_ago,
                read_at__isnull=False
            ).count(),
            'by_type': {},
            'by_priority': {},
            'read_rate': 0
        }
        
        # Calculate metrics by type
        for notification_type in ['GENERAL', 'ACADEMIC', 'FINANCIAL', 'URGENT']:
            count = Notification.objects.filter(
                created_at__gte=thirty_days_ago,
                notification_type=notification_type
            ).count()
            metrics['by_type'][notification_type] = count
        
        # Calculate metrics by priority
        for priority in ['LOW', 'NORMAL', 'HIGH', 'URGENT']:
            count = Notification.objects.filter(
                created_at__gte=thirty_days_ago,
                priority=priority
            ).count()
            metrics['by_priority'][priority] = count
        
        # Calculate read rate
        if metrics['total_sent'] > 0:
            metrics['read_rate'] = round(
                (metrics['total_read'] / metrics['total_sent']) * 100, 2
            )
        
        logger.info("Generated notification analytics")
        return metrics
        
    except Exception as exc:
        logger.error(f"Failed to generate notification analytics: {str(exc)}")
        raise exc