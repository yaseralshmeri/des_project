# نماذج نظام الإشعارات المتطور
# Advanced Notification System Models

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import uuid
import json

User = get_user_model()


class NotificationType(models.Model):
    """أنواع الإشعارات"""
    
    DELIVERY_METHODS = [
        ('EMAIL', 'بريد إلكتروني'),
        ('SMS', 'رسالة نصية'),
        ('PUSH', 'إشعار فوري'),
        ('IN_APP', 'داخل التطبيق'),
        ('DASHBOARD', 'لوحة التحكم'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_ar = models.CharField(max_length=100, verbose_name="الاسم - عربي")
    name_en = models.CharField(max_length=100, verbose_name="الاسم - إنجليزي")
    code = models.CharField(max_length=50, unique=True, verbose_name="الرمز")
    description = models.TextField(blank=True, verbose_name="الوصف")
    
    # طرق التوصيل
    delivery_methods = models.JSONField(default=list, verbose_name="طرق التوصيل")
    
    # قالب الرسالة
    default_title_template = models.CharField(max_length=255, blank=True, verbose_name="قالب العنوان")
    default_message_template = models.TextField(blank=True, verbose_name="قالب الرسالة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    requires_user_consent = models.BooleanField(default=False, verbose_name="يتطلب موافقة المستخدم")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "نوع إشعار"
        verbose_name_plural = "أنواع الإشعارات"
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar or self.name_en


# Additional models from enhanced_models.py - دون حذف أي كود

class NotificationTemplate(models.Model):
    """
    Reusable notification templates
    قوالب إشعارات قابلة لإعادة الاستخدام
    """
    TEMPLATE_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
        ('SYSTEM', 'System Alert'),
    ]
    
    CATEGORIES = [
        ('ACADEMIC', 'Academic'),
        ('FINANCIAL', 'Financial'),
        ('ADMINISTRATIVE', 'Administrative'),
        ('EMERGENCY', 'Emergency'),
        ('PROMOTIONAL', 'Promotional'),
        ('REMINDER', 'Reminder'),
        ('WELCOME', 'Welcome'),
        ('GRADUATION', 'Graduation'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Template content
    subject_template = models.CharField(max_length=500, blank=True)
    message_template = models.TextField()
    html_template = models.TextField(blank=True)
    
    # Personalization variables
    variables = models.JSONField(default=list, help_text="List of variables that can be used in templates")
    
    # Delivery settings
    priority = models.IntegerField(default=5, choices=[(i, str(i)) for i in range(1, 11)])
    is_active = models.BooleanField(default=True)
    requires_opt_in = models.BooleanField(default=False)
    
    # Languages and localization
    language = models.CharField(max_length=10, default='en')
    is_rtl = models.BooleanField(default=False)
    
    # Timing and frequency
    send_immediately = models.BooleanField(default=True)
    batch_size = models.IntegerField(default=100, help_text="Number of notifications to send per batch")
    rate_limit = models.IntegerField(default=0, help_text="Maximum notifications per minute (0 = no limit)")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates_enhanced'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    
    def render_content(self, context_data):
        """Render template with context data"""
        import re
        
        def replace_variables(text, data):
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                text = text.replace(placeholder, str(value))
            return text
        
        rendered_subject = replace_variables(self.subject_template, context_data) if self.subject_template else ""
        rendered_message = replace_variables(self.message_template, context_data)
        rendered_html = replace_variables(self.html_template, context_data) if self.html_template else ""
        
        return {
            'subject': rendered_subject,
            'message': rendered_message,
            'html': rendered_html
        }


class NotificationChannel(models.Model):
    """
    Communication channels configuration
    تكوين قنوات الاتصال
    """
    CHANNEL_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('WHATSAPP', 'WhatsApp'),
        ('TELEGRAM', 'Telegram'),
        ('SLACK', 'Slack'),
        ('DISCORD', 'Discord'),
        ('WEBHOOK', 'Webhook'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    configuration = models.JSONField(default=dict, help_text="Channel-specific configuration (API keys, endpoints, etc.)")
    
    # Status and limits
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    daily_limit = models.IntegerField(null=True, blank=True)
    hourly_limit = models.IntegerField(null=True, blank=True)
    
    # Tracking
    total_sent = models.BigIntegerField(default=0)
    total_delivered = models.BigIntegerField(default=0)
    total_failed = models.BigIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_channels_enhanced'
        ordering = ['channel_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.channel_type})"
    
    @property
    def success_rate(self):
        if self.total_sent > 0:
            return (self.total_delivered / self.total_sent) * 100
        return 0
    
    def __str__(self):
        return self.name_ar

# إضافة النموذج المطلوب - Notification مع اسم آخر للتوافق
class Notification(models.Model):
    """نموذج الإشعارات الأساسي للتوافق"""
    
    CATEGORY_CHOICES = [
        ('academic', 'أكاديمي'),
        ('financial', 'مالي'),
        ('administrative', 'إداري'),
        ('security', 'أمني'),
        ('system', 'النظام'),
        ('personal', 'شخصي'),
        ('emergency', 'طوارئ'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('high', 'عالي'),
        ('urgent', 'عاجل'),
        ('critical', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications',
                           verbose_name="المستخدم")
    
    title = models.CharField(max_length=255, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='personal',
                              verbose_name="الفئة")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal',
                              verbose_name="الأولوية")
    
    # إعدادات الإجراء
    action_url = models.URLField(blank=True, verbose_name="رابط الإجراء")
    action_text = models.CharField(max_length=100, blank=True, verbose_name="نص الإجراء")
    
    # البيانات الإضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # حالة القراءة
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت القراءة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['category', 'priority']),
            models.Index(fields=['is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.username}"
    
    def mark_as_read(self):
        """تمييز الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """فحص انتهاء صلاحية الإشعار"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class InAppNotification(models.Model):
    """الإشعارات داخل التطبيق"""
    
    CATEGORY_CHOICES = [
        ('academic', 'أكاديمي'),
        ('financial', 'مالي'),
        ('administrative', 'إداري'),
        ('security', 'أمني'),
        ('system', 'النظام'),
        ('personal', 'شخصي'),
        ('emergency', 'طوارئ'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('high', 'عالي'),
        ('urgent', 'عاجل'),
        ('critical', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',
                           verbose_name="المستخدم")
    
    title = models.CharField(max_length=255, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='personal',
                              verbose_name="الفئة")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal',
                              verbose_name="الأولوية")
    
    # إعدادات الإجراء
    action_url = models.URLField(blank=True, verbose_name="رابط الإجراء")
    action_text = models.CharField(max_length=100, blank=True, verbose_name="نص الإجراء")
    
    # البيانات الإضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # حالة القراءة
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت القراءة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "إشعار داخل التطبيق"
        verbose_name_plural = "الإشعارات داخل التطبيق"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['category', 'priority']),
            models.Index(fields=['is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.username}"
    
    def mark_as_read(self):
        """تمييز الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """فحص انتهاء صلاحية الإشعار"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False




class NotificationLog(models.Model):
    """سجل الإشعارات المرسلة"""
    
    STATUS_CHOICES = [
        ('sent', 'مُرسل'),
        ('failed', 'فاشل'),
        ('pending', 'معلق'),
        ('scheduled', 'مجدول'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الإشعار
    template_id = models.CharField(max_length=100, verbose_name="معرف القالب")
    recipient_user_id = models.CharField(max_length=50, verbose_name="معرف المستلم")
    recipient_email = models.EmailField(blank=True, verbose_name="بريد المستلم")
    recipient_phone = models.CharField(max_length=20, blank=True, verbose_name="هاتف المستلم")
    
    # محتوى الإشعار
    title = models.CharField(max_length=255, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    
    # معلومات الإرسال
    channels_used = models.JSONField(default=list, verbose_name="القنوات المستخدمة")
    priority = models.CharField(max_length=10, choices=InAppNotification.PRIORITY_CHOICES,
                              verbose_name="الأولوية")
    category = models.CharField(max_length=15, choices=InAppNotification.CATEGORY_CHOICES,
                              verbose_name="الفئة")
    
    # نتائج التسليم
    delivery_results = models.JSONField(default=dict, verbose_name="نتائج التسليم")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending',
                            verbose_name="الحالة")
    
    # البيانات الإضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإرسال")
    
    class Meta:
        verbose_name = "سجل إشعار"
        verbose_name_plural = "سجلات الإشعارات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template_id', '-created_at']),
            models.Index(fields=['recipient_user_id', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient_user_id}"


class UserDeviceToken(models.Model):
    """رموز أجهزة المستخدمين للإشعارات"""
    
    DEVICE_TYPE_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens',
                           verbose_name="المستخدم")
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES,
                                 verbose_name="نوع الجهاز")
    token = models.TextField(verbose_name="رمز الجهاز")
    
    # معلومات الجهاز
    device_id = models.CharField(max_length=255, blank=True, verbose_name="معرف الجهاز")
    device_name = models.CharField(max_length=255, blank=True, verbose_name="اسم الجهاز")
    app_version = models.CharField(max_length=20, blank=True, verbose_name="إصدار التطبيق")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_used = models.DateTimeField(auto_now=True, verbose_name="آخر استخدام")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "رمز جهاز مستخدم"
        verbose_name_plural = "رموز أجهزة المستخدمين"
        unique_together = ['user', 'device_id', 'device_type']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.device_type}"


class UserTelegramAccount(models.Model):
    """حسابات Telegram للمستخدمين"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_account',
                               verbose_name="المستخدم")
    chat_id = models.CharField(max_length=50, unique=True, verbose_name="معرف المحادثة")
    username = models.CharField(max_length=100, blank=True, verbose_name="اسم المستخدم")
    
    # إعدادات
    notifications_enabled = models.BooleanField(default=True, verbose_name="الإشعارات مفعلة")
    preferred_language = models.CharField(max_length=5, default='ar', verbose_name="اللغة المفضلة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_verified = models.BooleanField(default=False, verbose_name="موثق")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الربط")
    last_interaction = models.DateTimeField(null=True, blank=True, verbose_name="آخر تفاعل")
    
    class Meta:
        verbose_name = "حساب Telegram"
        verbose_name_plural = "حسابات Telegram"
    
    def __str__(self):
        return f"{self.user.display_name} - {self.chat_id}"


# إضافة النموذج المطلوب للتوافق
class UserNotificationPreference(models.Model):
    """تفضيلات إشعارات المستخدم - نموذج التوافق"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_notification_preference',
                               verbose_name="المستخدم")
    
    # تفضيلات القنوات
    email_enabled = models.BooleanField(default=True, verbose_name="البريد الإلكتروني")
    sms_enabled = models.BooleanField(default=False, verbose_name="الرسائل النصية")
    push_enabled = models.BooleanField(default=True, verbose_name="الإشعارات المدفوعة")
    in_app_enabled = models.BooleanField(default=True, verbose_name="الإشعارات داخل التطبيق")
    
    # تفضيلات الفئات
    academic_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الأكاديمية")
    financial_notifications = models.BooleanField(default=True, verbose_name="الإشعارات المالية")
    administrative_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الإدارية")
    security_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الأمنية")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تفضيلات إشعارات المستخدم"
        verbose_name_plural = "تفضيلات إشعارات المستخدمين"
    
    def __str__(self):
        return f"تفضيلات {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.username}"


class NotificationPreference(models.Model):
    """تفضيلات الإشعارات للمستخدمين"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference',
                               verbose_name="المستخدم")
    
    # تفضيلات القنوات
    email_enabled = models.BooleanField(default=True, verbose_name="البريد الإلكتروني")
    sms_enabled = models.BooleanField(default=False, verbose_name="الرسائل النصية")
    push_enabled = models.BooleanField(default=True, verbose_name="الإشعارات المدفوعة")
    in_app_enabled = models.BooleanField(default=True, verbose_name="الإشعارات داخل التطبيق")
    telegram_enabled = models.BooleanField(default=False, verbose_name="Telegram")
    
    # تفضيلات الفئات
    academic_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الأكاديمية")
    financial_notifications = models.BooleanField(default=True, verbose_name="الإشعارات المالية")
    administrative_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الإدارية")
    security_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الأمنية")
    system_notifications = models.BooleanField(default=False, verbose_name="إشعارات النظام")
    
    # تفضيلات الأولوية
    urgent_only = models.BooleanField(default=False, verbose_name="العاجل فقط")
    
    # إعدادات التوقيت
    quiet_hours_enabled = models.BooleanField(default=False, verbose_name="ساعات الهدوء")
    quiet_start_time = models.TimeField(null=True, blank=True, verbose_name="بداية الهدوء")
    quiet_end_time = models.TimeField(null=True, blank=True, verbose_name="نهاية الهدوء")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تفضيلات الإشعارات"
        verbose_name_plural = "تفضيلات الإشعارات"
    
    def __str__(self):
        return f"تفضيلات {self.user.display_name}"


class ScheduledNotification(models.Model):
    """الإشعارات المجدولة"""
    
    STATUS_CHOICES = [
        ('scheduled', 'مجدول'),
        ('sent', 'مُرسل'),
        ('failed', 'فاشل'),
        ('cancelled', 'ملغي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الإشعار
    template_id = models.CharField(max_length=100, verbose_name="معرف القالب")
    recipients = models.JSONField(verbose_name="المستلمون")
    variables = models.JSONField(default=dict, verbose_name="المتغيرات")
    channels = models.JSONField(default=list, verbose_name="القنوات")
    priority = models.CharField(max_length=10, choices=InAppNotification.PRIORITY_CHOICES,
                              verbose_name="الأولوية")
    
    # الجدولة
    scheduled_time = models.DateTimeField(verbose_name="وقت الإرسال المجدول")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled',
                            verbose_name="الحالة")
    
    # نتائج الإرسال
    delivery_results = models.JSONField(default=dict, blank=True, verbose_name="نتائج التسليم")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإرسال الفعلي")
    
    # المنشئ
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "إشعار مجدول"
        verbose_name_plural = "الإشعارات المجدولة"
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['status', 'scheduled_time']),
            models.Index(fields=['template_id', 'scheduled_time']),
        ]
    
    def __str__(self):
        return f"إشعار مجدول - {self.template_id} - {self.scheduled_time}"


# إضافة النموذج المطلوب للتوافق
class NotificationDelivery(models.Model):
    """تسليم الإشعارات - نموذج التوافق"""
    
    DELIVERY_CHANNELS = [
        ('EMAIL', 'بريد إلكتروني'),
        ('SMS', 'رسالة نصية'),
        ('PUSH', 'إشعار فوري'),
        ('IN_APP', 'داخل التطبيق'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'في الانتظار'),
        ('SENT', 'مُرسل'),
        ('DELIVERED', 'مُسلم'),
        ('FAILED', 'فاشل'),
        ('BOUNCED', 'مرتد'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE,
                                   related_name='deliveries', verbose_name="الإشعار")
    
    # معلومات التسليم
    channel = models.CharField(max_length=10, choices=DELIVERY_CHANNELS,
                             verbose_name="قناة التسليم")
    recipient_address = models.CharField(max_length=255, verbose_name="عنوان المستلم")
    
    # حالة التسليم
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="حالة التسليم")
    delivery_attempts = models.IntegerField(default=0, verbose_name="محاولات التسليم")
    
    # معلومات الاستجابة
    response_data = models.JSONField(default=dict, verbose_name="بيانات الاستجابة")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    
    # التوقيتات
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإرسال")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التسليم")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تسليم إشعار"
        verbose_name_plural = "تسليمات الإشعارات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"تسليم {self.notification.title} - {self.get_channel_display()}"


