# FIX: Notification System - تحسين نظام التنبيهات
"""
نظام شامل للإشعارات مع دعم اللغة العربية
"""

from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import models
from typing import List, Dict, Optional, Union
import logging
from enum import Enum

User = get_user_model()
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """أنواع الإشعارات"""
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    ACADEMIC = 'academic'
    FINANCIAL = 'financial'
    SYSTEM = 'system'

class NotificationPriority(Enum):
    """أولوية الإشعارات"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'

class NotificationChannel(Enum):
    """قنوات الإشعارات"""
    IN_APP = 'in_app'
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'

class NotificationManager:
    """مدير الإشعارات"""
    
    def __init__(self):
        self.channels = {
            NotificationChannel.IN_APP: self._send_in_app_notification,
            NotificationChannel.EMAIL: self._send_email_notification,
            NotificationChannel.SMS: self._send_sms_notification,
            NotificationChannel.PUSH: self._send_push_notification,
        }
    
    def send_notification(
        self,
        recipients: Union[User, List[User]],
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: List[NotificationChannel] = None,
        data: Dict = None,
        template: str = None
    ) -> Dict[str, bool]:
        """إرسال إشعار متعدد القنوات"""
        
        if not isinstance(recipients, list):
            recipients = [recipients]
        
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        
        results = {}
        
        for channel in channels:
            try:
                success = self._send_via_channel(
                    channel, recipients, title, message, 
                    notification_type, priority, data, template
                )
                results[channel.value] = success
                
            except Exception as e:
                logger.error(f"خطأ في إرسال الإشعار عبر {channel.value}: {e}")
                results[channel.value] = False
        
        return results
    
    def _send_via_channel(
        self,
        channel: NotificationChannel,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        data: Dict,
        template: str
    ) -> bool:
        """إرسال الإشعار عبر قناة محددة"""
        
        handler = self.channels.get(channel)
        if not handler:
            logger.warning(f"قناة الإشعار {channel.value} غير مدعومة")
            return False
        
        return handler(
            recipients, title, message, notification_type, 
            priority, data, template
        )
    
    def _send_in_app_notification(
        self,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        data: Dict,
        template: str
    ) -> bool:
        """إرسال إشعار داخل التطبيق"""
        try:
            from notifications.models import Notification
            
            for user in recipients:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type.value,
                    priority=priority.value,
                    data=data or {},
                    template=template
                )
            
            logger.info(f"تم إرسال إشعار داخل التطبيق إلى {len(recipients)} مستخدم")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار داخل التطبيق: {e}")
            return False
    
    def _send_email_notification(
        self,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        data: Dict,
        template: str
    ) -> bool:
        """إرسال إشعار عبر البريد الإلكتروني"""
        try:
            if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
                return False
            
            for user in recipients:
                if not user.email:
                    continue
                
                context = {
                    'user': user,
                    'title': title,
                    'message': message,
                    'notification_type': notification_type.value,
                    'priority': priority.value,
                    'data': data or {},
                    'site_name': getattr(settings, 'UNIVERSITY_NAME', 'نظام إدارة الجامعة')
                }
                
                # استخدام قالب مخصص أو القالب الافتراضي
                email_template = template or 'emails/notification.html'
                
                try:
                    html_content = render_to_string(email_template, context)
                    
                    msg = EmailMultiAlternatives(
                        subject=f"[{context['site_name']}] {title}",
                        body=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    
                except Exception as e:
                    logger.error(f"خطأ في إرسال البريد الإلكتروني إلى {user.email}: {e}")
                    continue
            
            logger.info(f"تم إرسال إشعارات البريد الإلكتروني إلى {len(recipients)} مستخدم")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعارات البريد الإلكتروني: {e}")
            return False
    
    def _send_sms_notification(
        self,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        data: Dict,
        template: str
    ) -> bool:
        """إرسال إشعار عبر الرسائل النصية"""
        try:
            if not getattr(settings, 'ENABLE_SMS_NOTIFICATIONS', False):
                return False
            
            # هنا يمكن إضافة تكامل مع مزود خدمة الرسائل النصية
            # مثل Twilio أو مزود محلي
            
            for user in recipients:
                phone = getattr(user, 'phone', None)
                if hasattr(user, 'student') and hasattr(user.student, 'profile'):
                    phone = user.student.profile.phone
                elif hasattr(user, 'employee'):
                    phone = getattr(user.employee, 'phone', None)
                
                if not phone:
                    continue
                
                # تنسيق الرسالة للرسائل النصية
                sms_message = f"{title}: {message}"
                
                # إرسال الرسالة (يتطلب تكامل مع مزود الخدمة)
                success = self._send_sms(phone, sms_message)
                
                if not success:
                    logger.warning(f"فشل في إرسال الرسالة النصية إلى {phone}")
            
            logger.info(f"تم إرسال الرسائل النصية إلى {len(recipients)} مستخدم")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسائل النصية: {e}")
            return False
    
    def _send_push_notification(
        self,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        data: Dict,
        template: str
    ) -> bool:
        """إرسال إشعار دفع"""
        try:
            # هنا يمكن إضافة تكامل مع خدمة الإشعارات المدفوعة
            # مثل Firebase Cloud Messaging
            
            logger.info(f"إرسال إشعارات الدفع غير مفعل حالياً")
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعارات الدفع: {e}")
            return False
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """إرسال رسالة نصية (يتطلب تكامل مع مزود الخدمة)"""
        # هنا يتم تنفيذ الإرسال الفعلي
        # مثال باستخدام Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(body=message, from_='+1234567890', to=phone)
        # return message.sid is not None
        
        logger.info(f"محاكاة إرسال رسالة نصية إلى {phone}: {message}")
        return True

class PrebuiltNotifications:
    """إشعارات جاهزة للاستخدام"""
    
    def __init__(self, notification_manager: NotificationManager = None):
        self.nm = notification_manager or NotificationManager()
    
    def student_enrollment_success(self, student: User, course_name: str):
        """إشعار نجاح التسجيل في المقرر"""
        return self.nm.send_notification(
            recipients=student,
            title="تم التسجيل بنجاح",
            message=f"تم تسجيلك بنجاح في مقرر {course_name}",
            notification_type=NotificationType.SUCCESS,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def grade_published(self, student: User, course_name: str, grade: float):
        """إشعار نشر الدرجات"""
        return self.nm.send_notification(
            recipients=student,
            title="تم نشر النتائج",
            message=f"تم نشر نتيجتك في مقرر {course_name}. درجتك: {grade}",
            notification_type=NotificationType.ACADEMIC,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def payment_due_reminder(self, student: User, amount: float, due_date: str):
        """تذكير بموعد الدفع"""
        return self.nm.send_notification(
            recipients=student,
            title="تذكير بموعد الدفع",
            message=f"يرجى دفع مبلغ {amount} ريال قبل {due_date}",
            notification_type=NotificationType.FINANCIAL,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.SMS]
        )
    
    def payment_received(self, student: User, amount: float):
        """إشعار استلام الدفعة"""
        return self.nm.send_notification(
            recipients=student,
            title="تم استلام الدفعة",
            message=f"تم استلام دفعتك بمبلغ {amount} ريال بنجاح",
            notification_type=NotificationType.SUCCESS,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def semester_start_reminder(self, recipients: List[User], semester_name: str, start_date: str):
        """تذكير ببداية الفصل الدراسي"""
        return self.nm.send_notification(
            recipients=recipients,
            title="بداية الفصل الدراسي",
            message=f"يبدأ {semester_name} في {start_date}. نتمنى لكم فصلاً دراسياً موفقاً",
            notification_type=NotificationType.ACADEMIC,
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def exam_schedule_published(self, recipients: List[User], semester_name: str):
        """إشعار نشر جدول الامتحانات"""
        return self.nm.send_notification(
            recipients=recipients,
            title="تم نشر جدول الامتحانات",
            message=f"تم نشر جدول امتحانات {semester_name}. يرجى مراجعة الجدول",
            notification_type=NotificationType.ACADEMIC,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def system_maintenance(self, recipients: List[User], maintenance_date: str):
        """إشعار صيانة النظام"""
        return self.nm.send_notification(
            recipients=recipients,
            title="صيانة النظام",
            message=f"سيكون النظام متوقفاً للصيانة في {maintenance_date}",
            notification_type=NotificationType.SYSTEM,
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def scholarship_approved(self, student: User, scholarship_name: str, amount: float):
        """إشعار الموافقة على المنحة"""
        return self.nm.send_notification(
            recipients=student,
            title="تم قبول طلب المنحة",
            message=f"تهانينا! تم قبول طلبك للحصول على {scholarship_name} بقيمة {amount} ريال",
            notification_type=NotificationType.SUCCESS,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def course_cancelled(self, recipients: List[User], course_name: str, reason: str = ""):
        """إشعار إلغاء المقرر"""
        message = f"تم إلغاء مقرر {course_name}"
        if reason:
            message += f" بسبب {reason}"
        
        return self.nm.send_notification(
            recipients=recipients,
            title="إلغاء المقرر",
            message=message,
            notification_type=NotificationType.WARNING,
            priority=NotificationPriority.URGENT,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.SMS]
        )

class NotificationScheduler:
    """مجدول الإشعارات"""
    
    def __init__(self):
        self.prebuilt = PrebuiltNotifications()
    
    def schedule_payment_reminders(self):
        """جدولة تذكيرات الدفع"""
        try:
            from finance.models import Fee
            from datetime import timedelta
            
            # البحث عن الرسوم المستحقة خلال 7 أيام
            upcoming_fees = Fee.objects.filter(
                due_date__lte=timezone.now().date() + timedelta(days=7),
                due_date__gte=timezone.now().date(),
                status='pending'
            ).select_related('student__user')
            
            for fee in upcoming_fees:
                self.prebuilt.payment_due_reminder(
                    student=fee.student.user,
                    amount=float(fee.amount),
                    due_date=fee.due_date.strftime('%Y-%m-%d')
                )
            
            logger.info(f"تم إرسال {upcoming_fees.count()} تذكير دفع")
            
        except Exception as e:
            logger.error(f"خطأ في جدولة تذكيرات الدفع: {e}")
    
    def schedule_grade_notifications(self):
        """جدولة إشعارات الدرجات الجديدة"""
        try:
            from academic.models import Grade
            
            # البحث عن الدرجات المنشورة حديثاً
            recent_grades = Grade.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24),
                is_published=True
            ).select_related('student__user', 'course')
            
            for grade in recent_grades:
                self.prebuilt.grade_published(
                    student=grade.student.user,
                    course_name=grade.course.name,
                    grade=grade.total_grade or 0
                )
            
            logger.info(f"تم إرسال {recent_grades.count()} إشعار درجات")
            
        except Exception as e:
            logger.error(f"خطأ في جدولة إشعارات الدرجات: {e}")

# إنشاء مثيل عام لمدير الإشعارات
notification_manager = NotificationManager()
prebuilt_notifications = PrebuiltNotifications(notification_manager)
notification_scheduler = NotificationScheduler()