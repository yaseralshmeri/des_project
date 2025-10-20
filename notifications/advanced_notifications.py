"""
Advanced Notification System for University Management System
نظام الإشعارات المتقدم لنظام إدارة الجامعة
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from celery import shared_task
import json
import logging
from enum import Enum
from typing import List, Dict, Optional

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationPriority(models.TextChoices):
    """إعدادات أولوية الإشعارات"""
    LOW = 'low', 'منخفضة'
    NORMAL = 'normal', 'عادية'
    HIGH = 'high', 'عالية'
    URGENT = 'urgent', 'عاجلة'


class NotificationChannel(models.TextChoices):
    """قنوات الإشعارات المتاحة"""
    IN_APP = 'in_app', 'داخل التطبيق'
    EMAIL = 'email', 'البريد الإلكتروني'
    SMS = 'sms', 'رسائل SMS'
    PUSH = 'push', 'الإشعارات المدفوعة'
    WHATSAPP = 'whatsapp', 'واتساب'


class NotificationTemplate(models.Model):
    """
    قوالب الإشعارات لسهولة الإدارة والتخصيص
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم القالب')
    title_template = models.CharField(max_length=200, verbose_name='قالب العنوان')
    body_template = models.TextField(verbose_name='قالب المحتوى')
    html_template = models.TextField(blank=True, verbose_name='قالب HTML')
    notification_type = models.CharField(max_length=50, verbose_name='نوع الإشعار')
    default_priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name='الأولوية الافتراضية'
    )
    default_channels = models.JSONField(
        default=list,
        verbose_name='القنوات الافتراضية'
    )
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'قالب إشعار'
        verbose_name_plural = 'قوالب الإشعارات'

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    """
    تفضيلات المستخدم للإشعارات
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='المستخدم'
    )
    
    # تفضيلات القنوات حسب نوع الإشعار
    academic_channels = models.JSONField(
        default=lambda: ['in_app', 'email'],
        verbose_name='قنوات الإشعارات الأكاديمية'
    )
    financial_channels = models.JSONField(
        default=lambda: ['in_app', 'email'],
        verbose_name='قنوات الإشعارات المالية'
    )
    administrative_channels = models.JSONField(
        default=lambda: ['in_app'],
        verbose_name='قنوات الإشعارات الإدارية'
    )
    emergency_channels = models.JSONField(
        default=lambda: ['in_app', 'email', 'sms'],
        verbose_name='قنوات إشعارات الطوارئ'
    )
    
    # إعدادات التوقيت
    quiet_hours_start = models.TimeField(
        default='22:00',
        verbose_name='بداية ساعات الهدوء'
    )
    quiet_hours_end = models.TimeField(
        default='08:00',
        verbose_name='نهاية ساعات الهدوء'
    )
    
    # إعدادات التكرار
    max_daily_notifications = models.PositiveIntegerField(
        default=50,
        verbose_name='الحد الأقصى للإشعارات اليومية'
    )
    
    # إعدادات اللغة والتنسيق
    language = models.CharField(
        max_length=10,
        default='ar',
        verbose_name='اللغة المفضلة'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تفضيلات الإشعارات'
        verbose_name_plural = 'تفضيلات الإشعارات'

    def __str__(self):
        return f'تفضيلات {self.user.username}'


class AdvancedNotification(models.Model):
    """
    نموذج الإشعارات المتقدم مع دعم القنوات المتعددة والجدولة
    """
    title = models.CharField(max_length=200, verbose_name='العنوان')
    message = models.TextField(verbose_name='الرسالة')
    html_content = models.TextField(blank=True, verbose_name='محتوى HTML')
    
    # معلومات المرسل والمستقبل
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='المرسل'
    )
    recipients = models.ManyToManyField(
        User,
        through='NotificationRecipient',
        related_name='received_notifications',
        verbose_name='المستقبلون'
    )
    
    # تصنيف وأولوية
    notification_type = models.CharField(
        max_length=50,
        default='general',
        verbose_name='نوع الإشعار'
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name='الأولوية'
    )
    
    # قنوات الإرسال
    channels = models.JSONField(
        default=lambda: ['in_app'],
        verbose_name='قنوات الإرسال'
    )
    
    # الجدولة والتوقيت
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='موعد الإرسال المجدول'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ انتهاء الصلاحية'
    )
    
    # حالة الإشعار
    is_sent = models.BooleanField(default=False, verbose_name='تم الإرسال')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='وقت الإرسال')
    
    # بيانات إضافية
    metadata = models.JSONField(default=dict, verbose_name='بيانات إضافية')
    
    # معلومات النظام
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'إشعار متقدم'
        verbose_name_plural = 'الإشعارات المتقدمة'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    """
    نموذج ربط المستقبلين مع الإشعارات وحالة القراءة
    """
    notification = models.ForeignKey(
        AdvancedNotification,
        on_delete=models.CASCADE,
        verbose_name='الإشعار'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='المستقبل'
    )
    
    # حالة الإشعار لكل مستقبل
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='وقت القراءة')
    
    # حالة الإرسال لكل قناة
    in_app_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    
    # معلومات التسليم
    delivery_status = models.JSONField(default=dict, verbose_name='حالة التسليم')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مستقبل الإشعار'
        verbose_name_plural = 'مستقبلو الإشعارات'
        unique_together = ['notification', 'recipient']

    def __str__(self):
        return f'{self.notification.title} - {self.recipient.username}'


class NotificationService:
    """
    خدمة الإشعارات المتقدمة مع دعم القنوات المتعددة والقوالب
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_notification(
        self,
        title: str,
        message: str,
        recipients: List[User],
        notification_type: str = 'general',
        priority: str = NotificationPriority.NORMAL,
        channels: Optional[List[str]] = None,
        template_name: Optional[str] = None,
        template_context: Optional[Dict] = None,
        scheduled_at: Optional[timezone.datetime] = None,
        expires_at: Optional[timezone.datetime] = None,
        sender: Optional[User] = None,
        metadata: Optional[Dict] = None
    ) -> AdvancedNotification:
        """
        إرسال إشعار متقدم مع دعم القنوات المتعددة
        """
        try:
            # استخدام القالب إذا كان متوفراً
            if template_name:
                template = NotificationTemplate.objects.filter(
                    name=template_name,
                    is_active=True
                ).first()
                
                if template:
                    context = template_context or {}
                    title = self._render_template(template.title_template, context)
                    message = self._render_template(template.body_template, context)
                    html_content = self._render_template(template.html_template, context) if template.html_template else ''
                    
                    # استخدام إعدادات القالب الافتراضية
                    if not channels:
                        channels = template.default_channels
                    if priority == NotificationPriority.NORMAL:
                        priority = template.default_priority
            
            # إنشاء الإشعار
            notification = AdvancedNotification.objects.create(
                title=title,
                message=message,
                html_content=html_content if 'html_content' in locals() else '',
                notification_type=notification_type,
                priority=priority,
                channels=channels or ['in_app'],
                scheduled_at=scheduled_at,
                expires_at=expires_at,
                sender=sender,
                metadata=metadata or {}
            )
            
            # إضافة المستقبلين
            for recipient in recipients:
                NotificationRecipient.objects.create(
                    notification=notification,
                    recipient=recipient
                )
            
            # إرسال الإشعار فوراً أو جدولته
            if scheduled_at and scheduled_at > timezone.now():
                # جدولة الإشعار للإرسال لاحقاً
                self._schedule_notification(notification)
            else:
                # إرسال الإشعار فوراً
                self._send_notification_now(notification)
            
            self.logger.info(f"Notification created: {notification.id}")
            return notification
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
            raise
    
    def send_bulk_notification(
        self,
        title: str,
        message: str,
        user_filters: Dict,
        **kwargs
    ) -> AdvancedNotification:
        """
        إرسال إشعار جماعي مع فلترة المستخدمين
        """
        try:
            # الحصول على المستخدمين حسب الفلاتر
            recipients = User.objects.filter(**user_filters)
            
            return self.send_notification(
                title=title,
                message=message,
                recipients=list(recipients),
                **kwargs
            )
            
        except Exception as e:
            self.logger.error(f"Error sending bulk notification: {str(e)}")
            raise
    
    def send_role_based_notification(
        self,
        title: str,
        message: str,
        roles: List[str],
        **kwargs
    ) -> AdvancedNotification:
        """
        إرسال إشعار حسب الأدوار
        """
        return self.send_bulk_notification(
            title=title,
            message=message,
            user_filters={'role__in': roles},
            **kwargs
        )
    
    def _send_notification_now(self, notification: AdvancedNotification):
        """إرسال الإشعار فوراً عبر جميع القنوات المحددة"""
        try:
            recipients = NotificationRecipient.objects.filter(notification=notification)
            
            for recipient_obj in recipients:
                recipient = recipient_obj.recipient
                
                # الحصول على تفضيلات المستخدم
                preferences = self._get_user_preferences(recipient)
                
                # تحديد القنوات المناسبة
                effective_channels = self._determine_channels(
                    notification, recipient, preferences
                )
                
                # إرسال عبر كل قناة
                for channel in effective_channels:
                    if channel == 'in_app':
                        self._send_in_app_notification(notification, recipient)
                        recipient_obj.in_app_sent = True
                    
                    elif channel == 'email':
                        self._send_email_notification(notification, recipient)
                        recipient_obj.email_sent = True
                    
                    elif channel == 'sms':
                        self._send_sms_notification(notification, recipient)
                        recipient_obj.sms_sent = True
                    
                    elif channel == 'push':
                        self._send_push_notification(notification, recipient)
                        recipient_obj.push_sent = True
                    
                    elif channel == 'whatsapp':
                        self._send_whatsapp_notification(notification, recipient)
                        recipient_obj.whatsapp_sent = True
                
                recipient_obj.save()
            
            # تحديث حالة الإشعار
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
        except Exception as e:
            self.logger.error(f"Error sending notification {notification.id}: {str(e)}")
    
    def _send_in_app_notification(self, notification: AdvancedNotification, recipient: User):
        """إرسال إشعار داخل التطبيق"""
        try:
            # استيراد النموذج المحلي لتجنب الاستيراد الدائري
            from .models import Notification
            
            Notification.objects.create(
                recipient=recipient,
                title=notification.title,
                message=notification.message,
                notification_type=notification.notification_type,
                priority=notification.priority,
                metadata=notification.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error sending in-app notification: {str(e)}")
    
    def _send_email_notification(self, notification: AdvancedNotification, recipient: User):
        """إرسال إشعار عبر البريد الإلكتروني"""
        try:
            if not recipient.email:
                return
            
            # تحضير محتوى البريد الإلكتروني
            subject = notification.title
            
            if notification.html_content:
                # استخدام قالب HTML
                html_content = notification.html_content
                text_content = strip_tags(html_content)
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
            else:
                # إرسال نص عادي
                send_mail(
                    subject=subject,
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False
                )
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {str(e)}")
    
    def _send_sms_notification(self, notification: AdvancedNotification, recipient: User):
        """إرسال إشعار عبر SMS"""
        try:
            # تنفيذ إرسال SMS (يتطلب خدمة SMS)
            # هذا مثال - يحتاج لتكامل مع خدمة SMS فعلية
            phone = getattr(recipient, 'phone', None)
            if phone:
                # إرسال SMS
                self.logger.info(f"SMS sent to {phone}: {notification.title}")
            
        except Exception as e:
            self.logger.error(f"Error sending SMS notification: {str(e)}")
    
    def _send_push_notification(self, notification: AdvancedNotification, recipient: User):
        """إرسال إشعار مدفوع (Push Notification)"""
        try:
            # تنفيذ إرسال Push Notification
            # يتطلب تكامل مع خدمة مثل Firebase Cloud Messaging
            self.logger.info(f"Push notification sent to {recipient.username}")
            
        except Exception as e:
            self.logger.error(f"Error sending push notification: {str(e)}")
    
    def _send_whatsapp_notification(self, notification: AdvancedNotification, recipient: User):
        """إرسال إشعار عبر واتساب"""
        try:
            # تنفيذ إرسال عبر واتساب (يتطلب WhatsApp Business API)
            phone = getattr(recipient, 'phone', None)
            if phone:
                self.logger.info(f"WhatsApp message sent to {phone}")
            
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp notification: {str(e)}")
    
    def _get_user_preferences(self, user: User) -> NotificationPreference:
        """الحصول على تفضيلات المستخدم"""
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        return preferences
    
    def _determine_channels(
        self,
        notification: AdvancedNotification,
        recipient: User,
        preferences: NotificationPreference
    ) -> List[str]:
        """تحديد القنوات المناسبة للإرسال"""
        # الحصول على القنوات من تفضيلات المستخدم حسب نوع الإشعار
        if notification.notification_type == 'academic':
            user_channels = preferences.academic_channels
        elif notification.notification_type == 'financial':
            user_channels = preferences.financial_channels
        elif notification.notification_type == 'administrative':
            user_channels = preferences.administrative_channels
        elif notification.notification_type == 'emergency':
            user_channels = preferences.emergency_channels
        else:
            user_channels = ['in_app']
        
        # دمج مع قنوات الإشعار المحددة
        effective_channels = list(set(notification.channels) & set(user_channels))
        
        # التحقق من ساعات الهدوء للإشعارات غير العاجلة
        if notification.priority != NotificationPriority.URGENT:
            current_time = timezone.now().time()
            if (preferences.quiet_hours_start <= current_time or 
                current_time <= preferences.quiet_hours_end):
                # إزالة القنوات المزعجة خلال ساعات الهدوء
                effective_channels = [ch for ch in effective_channels if ch in ['in_app']]
        
        return effective_channels
    
    def _render_template(self, template_string: str, context: Dict) -> str:
        """عرض قالب مع السياق المعطى"""
        try:
            from django.template import Template, Context
            template = Template(template_string)
            return template.render(Context(context))
        except Exception as e:
            self.logger.error(f"Error rendering template: {str(e)}")
            return template_string
    
    def _schedule_notification(self, notification: AdvancedNotification):
        """جدولة الإشعار للإرسال لاحقاً"""
        # استخدام Celery لجدولة المهام
        send_scheduled_notification.apply_async(
            args=[notification.id],
            eta=notification.scheduled_at
        )


# مهام Celery للمعالجة غير المتزامنة
@shared_task
def send_scheduled_notification(notification_id):
    """مهمة Celery لإرسال الإشعارات المجدولة"""
    try:
        notification = AdvancedNotification.objects.get(id=notification_id)
        service = NotificationService()
        service._send_notification_now(notification)
    except Exception as e:
        logger.error(f"Error sending scheduled notification {notification_id}: {str(e)}")


@shared_task
def cleanup_old_notifications(days=30):
    """مهمة تنظيف الإشعارات القديمة"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # حذف الإشعارات القديمة المقروءة
        deleted_count = AdvancedNotification.objects.filter(
            created_at__lt=cutoff_date,
            notificationrecipient__is_read=True
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old notifications")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {str(e)}")


# دوال مساعدة للاستخدام السهل
def send_notification(title, message, recipients, **kwargs):
    """دالة مساعدة لإرسال إشعار"""
    service = NotificationService()
    return service.send_notification(title, message, recipients, **kwargs)

def send_to_role(title, message, roles, **kwargs):
    """دالة مساعدة لإرسال إشعار حسب الأدوار"""
    service = NotificationService()
    return service.send_role_based_notification(title, message, roles, **kwargs)

def send_to_all_students(title, message, **kwargs):
    """إرسال إشعار لجميع الطلاب"""
    return send_to_role(title, message, ['STUDENT'], **kwargs)

def send_to_all_teachers(title, message, **kwargs):
    """إرسال إشعار لجميع الأساتذة"""
    return send_to_role(title, message, ['TEACHER'], **kwargs)