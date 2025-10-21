# نظام الإشعارات المتطور والذكي
# Advanced Intelligent Notification System with Multi-Channel Support

import json
import smtplib
import datetime
from typing import Dict, List, Optional, Any, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
import requests
import asyncio
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Django imports
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Celery for async tasks
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Mock decorator for development
    def shared_task(func):
        return func

# WebSocket support
try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

logger = logging.getLogger(__name__)
User = get_user_model()

class NotificationPriority(Enum):
    """أولوية الإشعار"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """قنوات الإشعار"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBSOCKET = "websocket"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

class NotificationCategory(Enum):
    """فئات الإشعار"""
    ACADEMIC = "academic"
    FINANCIAL = "financial"
    ADMINISTRATIVE = "administrative"
    SECURITY = "security"
    SYSTEM = "system"
    PERSONAL = "personal"
    EMERGENCY = "emergency"

@dataclass
class NotificationRecipient:
    """متلقي الإشعار"""
    user_id: str
    name: str
    email: str = ""
    phone: str = ""
    preferred_channels: List[NotificationChannel] = field(default_factory=list)
    language: str = "ar"
    timezone: str = "Asia/Riyadh"

@dataclass
class NotificationContent:
    """محتوى الإشعار"""
    title: str
    message: str
    title_en: str = ""
    message_en: str = ""
    html_content: str = ""
    attachments: List[str] = field(default_factory=list)
    action_url: str = ""
    action_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationTemplate:
    """قالب الإشعار"""
    template_id: str
    name: str
    category: NotificationCategory
    default_channels: List[NotificationChannel]
    title_template: str
    message_template: str
    html_template: str = ""
    variables: List[str] = field(default_factory=list)
    is_active: bool = True

class NotificationEngine:
    """محرك الإشعارات الذكي"""
    
    def __init__(self):
        self.templates = {}
        self.load_templates()
        self.delivery_stats = {}
    
    def load_templates(self):
        """تحميل قوالب الإشعارات"""
        default_templates = [
            NotificationTemplate(
                template_id="welcome_student",
                name="ترحيب بطالب جديد",
                category=NotificationCategory.ACADEMIC,
                default_channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                title_template="مرحباً بك في {university_name}",
                message_template="مرحباً {student_name}، أهلاً وسهلاً بك في {university_name}. رقمك الجامعي هو: {student_id}",
                html_template="welcome_student.html",
                variables=["university_name", "student_name", "student_id"]
            ),
            NotificationTemplate(
                template_id="grade_published",
                name="نشر الدرجات",
                category=NotificationCategory.ACADEMIC,
                default_channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP],
                title_template="تم نشر درجات مقرر {course_name}",
                message_template="تم نشر درجاتك في مقرر {course_name}. درجتك: {grade}",
                variables=["course_name", "grade"]
            ),
            NotificationTemplate(
                template_id="payment_due",
                name="استحقاق دفعة",
                category=NotificationCategory.FINANCIAL,
                default_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.IN_APP],
                title_template="استحقاق دفعة مالية",
                message_template="لديك دفعة مستحقة بقيمة {amount} ريال. تاريخ الاستحقاق: {due_date}",
                variables=["amount", "due_date"]
            ),
            NotificationTemplate(
                template_id="course_enrollment",
                name="تسجيل مقرر",
                category=NotificationCategory.ACADEMIC,
                default_channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                title_template="تم تسجيلك في مقرر {course_name}",
                message_template="تم تسجيلك بنجاح في مقرر {course_name} للفصل الدراسي {semester}",
                variables=["course_name", "semester"]
            ),
            NotificationTemplate(
                template_id="security_alert",
                name="تنبيه أمني",
                category=NotificationCategory.SECURITY,
                default_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PUSH],
                title_template="تنبيه أمني - {alert_type}",
                message_template="تم اكتشاف نشاط مشبوه في حسابك: {alert_details}. يُرجى المراجعة فوراً",
                variables=["alert_type", "alert_details"]
            ),
            NotificationTemplate(
                template_id="attendance_alert",
                name="تنبيه غياب",
                category=NotificationCategory.ACADEMIC,
                default_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
                title_template="تنبيه غياب - {course_name}",
                message_template="تم تسجيل غيابك في مقرر {course_name}. عدد مرات الغياب: {absence_count}",
                variables=["course_name", "absence_count"]
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = template
    
    def send_notification(self, template_id: str, recipients: List[NotificationRecipient],
                         variables: Dict[str, Any], priority: NotificationPriority = NotificationPriority.NORMAL,
                         scheduled_time: datetime.datetime = None, channels: List[NotificationChannel] = None) -> Dict:
        """إرسال إشعار"""
        try:
            # التحقق من وجود القالب
            if template_id not in self.templates:
                raise ValueError(f"قالب الإشعار غير موجود: {template_id}")
            
            template = self.templates[template_id]
            
            # تحديد القنوات
            if not channels:
                channels = template.default_channels
            
            # تحضير محتوى الإشعار
            content = self._prepare_notification_content(template, variables)
            
            # جدولة الإشعار أو إرساله مباشرة
            if scheduled_time and scheduled_time > timezone.now():
                return self._schedule_notification(template_id, recipients, content, channels, scheduled_time, priority)
            else:
                return self._send_immediate_notification(template, recipients, content, channels, priority)
                
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sent_count': 0,
                'failed_count': len(recipients)
            }
    
    def _prepare_notification_content(self, template: NotificationTemplate, variables: Dict[str, Any]) -> NotificationContent:
        """تحضير محتوى الإشعار"""
        # استبدال المتغيرات في العنوان والرسالة
        title = template.title_template
        message = template.message_template
        
        for var, value in variables.items():
            placeholder = f"{{{var}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        # تحضير المحتوى HTML إذا كان متوفراً
        html_content = ""
        if template.html_template:
            try:
                html_content = render_to_string(template.html_template, variables)
            except Exception as e:
                logger.warning(f"فشل في تحضير المحتوى HTML: {str(e)}")
        
        return NotificationContent(
            title=title,
            message=message,
            html_content=html_content,
            action_url=variables.get('action_url', ''),
            action_text=variables.get('action_text', ''),
            metadata=variables
        )
    
    def _send_immediate_notification(self, template: NotificationTemplate, recipients: List[NotificationRecipient],
                                   content: NotificationContent, channels: List[NotificationChannel],
                                   priority: NotificationPriority) -> Dict:
        """إرسال إشعار فوري"""
        sent_count = 0
        failed_count = 0
        results = {}
        
        for recipient in recipients:
            recipient_results = {}
            recipient_channels = self._determine_recipient_channels(recipient, channels)
            
            for channel in recipient_channels:
                try:
                    if CELERY_AVAILABLE and priority != NotificationPriority.CRITICAL:
                        # إرسال غير متزامن للإشعارات غير الحرجة
                        send_notification_async.delay(
                            channel.value, recipient.__dict__, content.__dict__, template.category.value
                        )
                        recipient_results[channel.value] = "scheduled"
                    else:
                        # إرسال متزامن للإشعارات الحرجة
                        result = self._send_via_channel(channel, recipient, content, template.category)
                        recipient_results[channel.value] = result
                        
                        if result.get('success'):
                            sent_count += 1
                        else:
                            failed_count += 1
                            
                except Exception as e:
                    logger.error(f"خطأ في إرسال الإشعار للمستلم {recipient.user_id} عبر {channel.value}: {str(e)}")
                    recipient_results[channel.value] = {'success': False, 'error': str(e)}
                    failed_count += 1
            
            results[recipient.user_id] = recipient_results
        
        # حفظ الرقم السجل
        self._save_notification_record(template, recipients, content, channels, priority, results)
        
        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'results': results,
            'timestamp': timezone.now().isoformat()
        }
    
    def _determine_recipient_channels(self, recipient: NotificationRecipient, 
                                    default_channels: List[NotificationChannel]) -> List[NotificationChannel]:
        """تحديد قنوات الإرسال للمستلم"""
        if recipient.preferred_channels:
            # استخدام تفضيلات المستلم
            return [ch for ch in recipient.preferred_channels if ch in default_channels]
        else:
            # استخدام القنوات الافتراضية
            return default_channels
    
    def _send_via_channel(self, channel: NotificationChannel, recipient: NotificationRecipient,
                         content: NotificationContent, category: NotificationCategory) -> Dict:
        """إرسال عبر قناة محددة"""
        try:
            if channel == NotificationChannel.EMAIL:
                return self._send_email(recipient, content)
            elif channel == NotificationChannel.SMS:
                return self._send_sms(recipient, content)
            elif channel == NotificationChannel.PUSH:
                return self._send_push_notification(recipient, content)
            elif channel == NotificationChannel.IN_APP:
                return self._send_in_app_notification(recipient, content, category)
            elif channel == NotificationChannel.WEBSOCKET:
                return self._send_websocket_notification(recipient, content)
            elif channel == NotificationChannel.TELEGRAM:
                return self._send_telegram_notification(recipient, content)  
            else:
                return {'success': False, 'error': 'قناة غير مدعومة'}
                
        except Exception as e:
            logger.error(f"خطأ في الإرسال عبر {channel.value}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_email(self, recipient: NotificationRecipient, content: NotificationContent) -> Dict:
        """إرسال بريد إلكتروني"""
        try:
            if not recipient.email:
                return {'success': False, 'error': 'عنوان البريد غير متوفر'}
            
            if content.html_content:
                # بريد HTML
                msg = EmailMultiAlternatives(
                    subject=content.title,
                    body=content.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient.email]
                )
                msg.attach_alternative(content.html_content, "text/html")
            else:
                # بريد نصي
                msg = MIMEText(content.message, 'plain', 'utf-8')
                msg['Subject'] = content.title
                msg['From'] = settings.DEFAULT_FROM_EMAIL
                msg['To'] = recipient.email
            
            # إرسال البريد
            if hasattr(msg, 'send'):
                msg.send()
            else:
                # استخدام SMTP مباشرة
                with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                    if settings.EMAIL_USE_TLS:
                        server.starttls()
                    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                    server.send_message(msg)
            
            logger.info(f"تم إرسال بريد إلكتروني إلى {recipient.email}")
            return {'success': True, 'channel': 'email'}
            
        except Exception as e:
            logger.error(f"فشل إرسال البريد الإلكتروني: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_sms(self, recipient: NotificationRecipient, content: NotificationContent) -> Dict:
        """إرسال رسالة نصية"""
        try:
            if not recipient.phone:
                return {'success': False, 'error': 'رقم الهاتف غير متوفر'}
            
            # استخدام خدمة SMS (مثال باستخدام Twilio)
            sms_config = getattr(settings, 'SMS_CONFIG', {})
            
            if not sms_config:
                logger.warning("إعدادات SMS غير متوفرة")
                return {'success': False, 'error': 'خدمة SMS غير مُعدة'}
            
            # مثال لإرسال SMS عبر API
            api_url = sms_config.get('api_url')
            api_key = sms_config.get('api_key')
            
            if api_url and api_key:
                data = {
                    'to': recipient.phone,
                    'message': content.message,
                    'from': sms_config.get('sender_id', 'University')
                }
                
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(api_url, json=data, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"تم إرسال SMS إلى {recipient.phone}")
                    return {'success': True, 'channel': 'sms', 'response': response.json()}
                else:
                    return {'success': False, 'error': f'SMS API error: {response.status_code}'}
            else:
                return {'success': False, 'error': 'إعدادات SMS غير مكتملة'}
                
        except Exception as e:
            logger.error(f"فشل إرسال SMS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_push_notification(self, recipient: NotificationRecipient, content: NotificationContent) -> Dict:
        """إرسال إشعار دفع للتطبيق"""
        try:
            # استخدام Firebase Cloud Messaging أو خدمة مماثلة
            push_config = getattr(settings, 'FCM_CONFIG', {})
            
            if not push_config:
                return {'success': False, 'error': 'إعدادات Push غير متوفرة'}
            
            # الحصول على رمز الجهاز من قاعدة البيانات
            device_token = self._get_user_device_token(recipient.user_id)
            
            if not device_token:
                return {'success': False, 'error': 'رمز الجهاز غير متوفر'}
            
            # إعداد الإشعار
            notification_data = {
                'to': device_token,
                'notification': {
                    'title': content.title,
                    'body': content.message,
                    'click_action': content.action_url
                },
                'data': content.metadata
            }
            
            # إرسال الإشعار
            fcm_url = 'https://fcm.googleapis.com/fcm/send'
            headers = {
                'Authorization': f'key={push_config.get("server_key")}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(fcm_url, json=notification_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"تم إرسال Push notification إلى المستخدم {recipient.user_id}")
                return {'success': True, 'channel': 'push', 'response': response.json()}
            else:
                return {'success': False, 'error': f'FCM error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"فشل إرسال Push notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_in_app_notification(self, recipient: NotificationRecipient, content: NotificationContent,
                                 category: NotificationCategory) -> Dict:
        """إرسال إشعار داخل التطبيق"""
        try:
            # حفظ الإشعار في قاعدة البيانات
            from .models import InAppNotification
            
            notification = InAppNotification.objects.create(
                user_id=recipient.user_id,
                title=content.title,
                message=content.message,
                category=category.value,
                action_url=content.action_url,
                action_text=content.action_text,
                metadata=content.metadata,
                is_read=False
            )
            
            # إشعار الواجهة الأمامية عبر WebSocket إذا كان متوفراً
            if WEBSOCKET_AVAILABLE:
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{recipient.user_id}",
                        {
                            'type': 'notification_message',
                            'notification': {
                                'id': str(notification.id),
                                'title': content.title,
                                'message': content.message,
                                'category': category.value,
                                'timestamp': notification.created_at.isoformat()
                            }
                        }
                    )
                except Exception as e:
                    logger.warning(f"فشل إرسال WebSocket: {str(e)}")
            
            logger.info(f"تم حفظ الإشعار داخل التطبيق للمستخدم {recipient.user_id}")
            return {'success': True, 'channel': 'in_app', 'notification_id': str(notification.id)}
            
        except Exception as e:
            logger.error(f"فشل إرسال الإشعار داخل التطبيق: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_websocket_notification(self, recipient: NotificationRecipient, content: NotificationContent) -> Dict:
        """إرسال إشعار عبر WebSocket"""
        if not WEBSOCKET_AVAILABLE:
            return {'success': False, 'error': 'WebSocket غير متوفر'}
        
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{recipient.user_id}",
                {
                    'type': 'real_time_notification',
                    'data': {
                        'title': content.title,
                        'message': content.message,
                        'action_url': content.action_url,
                        'timestamp': timezone.now().isoformat()
                    }
                }
            )
            
            return {'success': True, 'channel': 'websocket'}
            
        except Exception as e:
            logger.error(f"فشل إرسال WebSocket: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_telegram_notification(self, recipient: NotificationRecipient, content: NotificationContent) -> Dict:
        """إرسال إشعار عبر Telegram"""
        try:
            telegram_config = getattr(settings, 'TELEGRAM_CONFIG', {})
            bot_token = telegram_config.get('bot_token')
            
            if not bot_token:
                return {'success': False, 'error': 'Telegram Bot غير مُعد'}
            
            # الحصول على Telegram Chat ID للمستخدم
            chat_id = self._get_user_telegram_chat_id(recipient.user_id)
            
            if not chat_id:
                return {'success': False, 'error': 'Telegram Chat ID غير متوفر'}
            
            # إرسال الرسالة
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': f"*{content.title}*\n\n{content.message}",
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'channel': 'telegram'}
            else:
                return {'success': False, 'error': f'Telegram API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"فشل إرسال Telegram: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_user_device_token(self, user_id: str) -> Optional[str]:
        """الحصول على رمز جهاز المستخدم للإشعارات"""
        try:
            # البحث في قاعدة البيانات أو الكاش
            cache_key = f"device_token_{user_id}"
            token = cache.get(cache_key)
            
            if not token:
                # البحث في قاعدة البيانات
                from .models import UserDeviceToken
                device = UserDeviceToken.objects.filter(user_id=user_id, is_active=True).first()
                if device:
                    token = device.token
                    cache.set(cache_key, token, timeout=3600)  # ساعة واحدة
            
            return token
        except Exception as e:
            logger.error(f"خطأ في الحصول على رمز الجهاز: {str(e)}")
            return None
    
    def _get_user_telegram_chat_id(self, user_id: str) -> Optional[str]:
        """الحصول على معرف محادثة Telegram للمستخدم"""
        try:
            cache_key = f"telegram_chat_{user_id}"
            chat_id = cache.get(cache_key)
            
            if not chat_id:
                from .models import UserTelegramAccount
                telegram_account = UserTelegramAccount.objects.filter(user_id=user_id, is_active=True).first()
                if telegram_account:
                    chat_id = telegram_account.chat_id
                    cache.set(cache_key, chat_id, timeout=3600)
            
            return chat_id
        except Exception as e:
            logger.error(f"خطأ في الحصول على Telegram Chat ID: {str(e)}")
            return None
    
    def _schedule_notification(self, template_id: str, recipients: List[NotificationRecipient],
                             content: NotificationContent, channels: List[NotificationChannel],
                             scheduled_time: datetime.datetime, priority: NotificationPriority) -> Dict:
        """جدولة إشعار للإرسال لاحقاً"""
        try:
            if not CELERY_AVAILABLE:
                return {'success': False, 'error': 'Celery غير متوفر للجدولة'}
            
            # جدولة المهمة
            send_scheduled_notification.apply_async(
                args=[template_id, [r.__dict__ for r in recipients], content.__dict__, 
                      [c.value for c in channels], priority.value],
                eta=scheduled_time
            )
            
            logger.info(f"تم جدولة الإشعار {template_id} للإرسال في {scheduled_time}")
            
            return {
                'success': True,
                'scheduled': True,
                'scheduled_time': scheduled_time.isoformat(),
                'recipients_count': len(recipients)
            }
            
        except Exception as e:
            logger.error(f"خطأ في جدولة الإشعار: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _save_notification_record(self, template: NotificationTemplate, recipients: List[NotificationRecipient],
                                content: NotificationContent, channels: List[NotificationChannel],
                                priority: NotificationPriority, results: Dict):
        """حفظ سجل الإشعار"""
        try:
            from .models import NotificationLog
            
            for recipient in recipients:
                recipient_results = results.get(recipient.user_id, {})
                
                NotificationLog.objects.create(
                    template_id=template.template_id,
                    recipient_user_id=recipient.user_id,
                    recipient_email=recipient.email,
                    recipient_phone=recipient.phone,
                    title=content.title,
                    message=content.message,
                    channels_used=json.dumps([c.value for c in channels]),
                    priority=priority.value,
                    category=template.category.value,
                    delivery_results=json.dumps(recipient_results),
                    metadata=content.metadata
                )
                
        except Exception as e:
            logger.error(f"خطأ في حفظ سجل الإشعار: {str(e)}")

# Celery Tasks للإرسال غير المتزامن

@shared_task
def send_notification_async(channel: str, recipient_data: Dict, content_data: Dict, category: str):
    """مهمة Celery لإرسال الإشعارات غير المتزامنة"""
    try:
        engine = NotificationEngine()
        
        # تحويل البيانات إلى كائنات
        recipient = NotificationRecipient(**recipient_data)
        content = NotificationContent(**content_data)
        channel_enum = NotificationChannel(channel)
        category_enum = NotificationCategory(category)
        
        # إرسال الإشعار
        result = engine._send_via_channel(channel_enum, recipient, content, category_enum)
        
        logger.info(f"تم إرسال الإشعار غير المتزامن عبر {channel} للمستخدم {recipient.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"خطأ في المهمة غير المتزامنة: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def send_scheduled_notification(template_id: str, recipients_data: List[Dict], content_data: Dict,
                               channels: List[str], priority: str):
    """مهمة Celery للإشعارات المجدولة"""
    try:
        engine = NotificationEngine()
        
        # تحويل البيانات
        recipients = [NotificationRecipient(**r) for r in recipients_data]
        content = NotificationContent(**content_data)
        channel_enums = [NotificationChannel(c) for c in channels]
        priority_enum = NotificationPriority(priority)
        
        # الحصول على القالب
        template = engine.templates.get(template_id)
        if not template:
            raise ValueError(f"قالب غير موجود: {template_id}")
        
        # إرسال الإشعار
        result = engine._send_immediate_notification(template, recipients, content, channel_enums, priority_enum)
        
        logger.info(f"تم إرسال الإشعار المجدول {template_id}")
        return result
        
    except Exception as e:
        logger.error(f"خطأ في الإشعار المجدول: {str(e)}")
        return {'success': False, 'error': str(e)}

# دوال مساعدة للاستخدام الخارجي

def send_notification(template_id: str, user_ids: List[str], variables: Dict[str, Any],
                     priority: str = "normal", channels: List[str] = None,
                     scheduled_time: datetime.datetime = None) -> Dict:
    """إرسال إشعار للمستخدمين"""
    try:
        engine = NotificationEngine()
        
        # الحصول على بيانات المستلمين
        recipients = []
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                recipient = NotificationRecipient(
                    user_id=str(user.id),
                    name=user.display_name,
                    email=user.email,
                    phone=getattr(user, 'phone_number', ''),
                    language=getattr(user, 'language_preference', 'ar')
                )
                recipients.append(recipient)
            except User.DoesNotExist:
                logger.warning(f"المستخدم غير موجود: {user_id}")
                continue
        
        if not recipients:
            return {'success': False, 'error': 'لا يوجد مستلمون صالحون'}
        
        # تحويل القنوات والأولوية
        priority_enum = NotificationPriority(priority)
        channel_enums = [NotificationChannel(c) for c in channels] if channels else None
        
        # إرسال الإشعار
        return engine.send_notification(
            template_id, recipients, variables, priority_enum, scheduled_time, channel_enums
        )
        
    except Exception as e:
        logger.error(f"خطأ في دالة إرسال الإشعار: {str(e)}")
        return {'success': False, 'error': str(e)}

def send_bulk_notification(template_id: str, filter_criteria: Dict[str, Any],
                          variables: Dict[str, Any], priority: str = "normal") -> Dict:
    """إرسال إشعار جماعي مع معايير تصفية"""
    try:
        # بناء الاستعلام بناءً على معايير التصفية
        from django.db.models import Q
        
        query = Q()
        
        if 'role' in filter_criteria:
            query &= Q(role=filter_criteria['role'])
        
        if 'college_id' in filter_criteria:
            query &= Q(studentprofile__college_id=filter_criteria['college_id'])
        
        if 'department_id' in filter_criteria:
            query &= Q(studentprofile__department_id=filter_criteria['department_id'])
        
        if 'academic_level' in filter_criteria:
            query &= Q(studentprofile__academic_level=filter_criteria['academic_level'])
        
        # الحصول على المستخدمين
        users = User.objects.filter(query, is_active=True)
        user_ids = [str(user.id) for user in users]
        
        if not user_ids:
            return {'success': False, 'error': 'لا يوجد مستخدمون يطابقون المعايير'}
        
        # إرسال الإشعار
        return send_notification(template_id, user_ids, variables, priority)
        
    except Exception as e:
        logger.error(f"خطأ في الإشعار الجماعي: {str(e)}")
        return {'success': False, 'error': str(e)}

def create_custom_notification(title: str, message: str, user_ids: List[str],
                             channels: List[str] = None, priority: str = "normal") -> Dict:
    """إنشاء وإرسال إشعار مخصص"""
    try:
        engine = NotificationEngine()
        
        # إنشاء قالب مؤقت
        custom_template = NotificationTemplate(
            template_id="custom_" + str(uuid.uuid4()),
            name="إشعار مخصص",
            category=NotificationCategory.PERSONAL,
            default_channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            title_template=title,
            message_template=message
        )
        
        # إضافة القالب مؤقتاً
        engine.templates[custom_template.template_id] = custom_template
        
        # إرسال الإشعار
        return send_notification(custom_template.template_id, user_ids, {}, priority, channels)
        
    except Exception as e:
        logger.error(f"خطأ في الإشعار المخصص: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_notification_stats(date_range: tuple = None) -> Dict:
    """الحصول على إحصائيات الإشعارات"""
    try:
        from .models import NotificationLog
        from django.db.models import Count, Q
        
        # تحديد نطاق التاريخ
        query = Q()
        if date_range:
            query &= Q(created_at__range=date_range)
        
        logs = NotificationLog.objects.filter(query)
        
        # حساب الإحصائيات
        stats = {
            'total_notifications': logs.count(),
            'by_category': dict(logs.values('category').annotate(count=Count('id'))),
            'by_priority': dict(logs.values('priority').annotate(count=Count('id'))),
            'by_template': dict(logs.values('template_id').annotate(count=Count('id'))),
            'successful_deliveries': logs.filter(
                delivery_results__icontains='"success": true'
            ).count()
        }
        
        return {'success': True, 'stats': stats}
        
    except Exception as e:
        logger.error(f"خطأ في إحصائيات الإشعارات: {str(e)}")
        return {'success': False, 'error': str(e)}