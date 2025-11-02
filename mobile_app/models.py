# نماذج التطبيق المحمول
# Mobile App Models

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class MobileDevice(models.Model):
    """أجهزة المستخدمين المحمولة"""
    
    DEVICE_TYPES = [
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
        ('WINDOWS', 'Windows Phone'),
        ('OTHER', 'أخرى'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('BLOCKED', 'محظور'),
        ('PENDING', 'في الانتظار'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='mobile_devices', verbose_name="المستخدم")
    
    # معلومات الجهاز
    device_id = models.CharField(max_length=200, unique=True, verbose_name="معرف الجهاز")
    device_name = models.CharField(max_length=100, verbose_name="اسم الجهاز")
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES, 
                                 verbose_name="نوع الجهاز")
    device_model = models.CharField(max_length=100, blank=True, verbose_name="موديل الجهاز")
    operating_system = models.CharField(max_length=50, blank=True, verbose_name="نظام التشغيل")
    os_version = models.CharField(max_length=20, blank=True, verbose_name="إصدار النظام")
    
    # معلومات التطبيق
    app_version = models.CharField(max_length=20, blank=True, verbose_name="إصدار التطبيق")
    fcm_token = models.TextField(blank=True, verbose_name="رمز FCM للإشعارات")
    
    # الحالة والإعدادات
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
                            default='PENDING', verbose_name="الحالة")
    is_trusted = models.BooleanField(default=False, verbose_name="جهاز موثوق")
    notifications_enabled = models.BooleanField(default=True, verbose_name="الإشعارات مفعلة")
    
    # معلومات الأمان
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="آخر تسجيل دخول")
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="آخر ظهور")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "جهاز محمول"
        verbose_name_plural = "الأجهزة المحمولة"
        ordering = ['-last_seen', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['device_id']),
            models.Index(fields=['device_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name}"
    
    def update_last_seen(self):
        """تحديث آخر ظهور"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class MobileAppSession(models.Model):
    """جلسات التطبيق المحمول"""
    
    SESSION_TYPES = [
        ('LOGIN', 'تسجيل دخول'),
        ('BACKGROUND', 'في الخلفية'),
        ('FOREGROUND', 'في المقدمة'),
        ('LOGOUT', 'تسجيل خروج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE,
                             related_name='app_sessions', verbose_name="الجهاز")
    
    # معلومات الجلسة
    session_id = models.CharField(max_length=100, unique=True, verbose_name="معرف الجلسة")
    session_type = models.CharField(max_length=15, choices=SESSION_TYPES,
                                  verbose_name="نوع الجلسة")
    
    # التوقيت
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="وقت البداية")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الانتهاء")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="آخر نشاط")
    
    # بيانات إضافية
    app_version = models.CharField(max_length=20, blank=True, verbose_name="إصدار التطبيق")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    location_data = models.JSONField(default=dict, blank=True, verbose_name="بيانات الموقع")
    
    class Meta:
        verbose_name = "جلسة تطبيق محمول"
        verbose_name_plural = "جلسات التطبيق المحمول"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['device', '-start_time']),
            models.Index(fields=['session_type']),
        ]
    
    def __str__(self):
        return f"{self.device.user.username} - {self.session_id}"
    
    @property
    def duration(self):
        """مدة الجلسة"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time


class MobilePushNotification(models.Model):
    """إشعارات الدفع للأجهزة المحمولة"""
    
    NOTIFICATION_TYPES = [
        ('GENERAL', 'عام'),
        ('ACADEMIC', 'أكاديمي'),
        ('FINANCIAL', 'مالي'),
        ('ALERT', 'تنبيه'),
        ('REMINDER', 'تذكير'),
        ('ANNOUNCEMENT', 'إعلان'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'في الانتظار'),
        ('SENT', 'مُرسل'),
        ('DELIVERED', 'مُسلّم'),
        ('FAILED', 'فشل'),
        ('CLICKED', 'تم النقر'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('NORMAL', 'عادي'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستقبل
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE,
                             related_name='push_notifications', verbose_name="الجهاز")
    
    # محتوى الإشعار
    title = models.CharField(max_length=100, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES,
                                       default='GENERAL', verbose_name="نوع الإشعار")
    
    # الإعدادات
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS,
                              default='NORMAL', verbose_name="الأولوية")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES,
                            default='PENDING', verbose_name="الحالة")
    
    # بيانات إضافية
    data_payload = models.JSONField(default=dict, blank=True, verbose_name="بيانات إضافية")
    action_url = models.URLField(blank=True, verbose_name="رابط الإجراء")
    
    # التوقيت
    scheduled_at = models.DateTimeField(default=timezone.now, verbose_name="موعد الإرسال")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإرسال")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التسليم")
    clicked_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت النقر")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "إشعار دفع محمول"
        verbose_name_plural = "إشعارات الدفع المحمولة"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'status']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.device.user.username}"


class MobileAppFeedback(models.Model):
    """ملاحظات التطبيق المحمول"""
    
    FEEDBACK_TYPES = [
        ('BUG_REPORT', 'بلاغ خطأ'),
        ('FEATURE_REQUEST', 'طلب ميزة'),
        ('IMPROVEMENT', 'اقتراح تحسين'),
        ('COMPLAINT', 'شكوى'),
        ('COMPLIMENT', 'إطراء'),
        ('OTHER', 'أخرى'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'جديد'),
        ('REVIEWING', 'قيد المراجعة'),
        ('IN_PROGRESS', 'قيد التنفيذ'),
        ('RESOLVED', 'محلول'),
        ('CLOSED', 'مغلق'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المُرسِل
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='mobile_feedback', verbose_name="المستخدم")
    device = models.ForeignKey(MobileDevice, on_delete=models.SET_NULL, null=True,
                             related_name='feedback', verbose_name="الجهاز")
    
    # محتوى التغذية الراجعة
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES,
                                   verbose_name="نوع التغذية الراجعة")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    description = models.TextField(verbose_name="الوصف")
    
    # التقييم
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True, verbose_name="التقييم (1-5)"
    )
    
    # الحالة والأولوية
    status = models.CharField(max_length=15, choices=STATUS_CHOICES,
                            default='NEW', verbose_name="الحالة")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS,
                              default='MEDIUM', verbose_name="الأولوية")
    
    # معلومات تقنية
    app_version = models.CharField(max_length=20, blank=True, verbose_name="إصدار التطبيق")
    device_info = models.JSONField(default=dict, blank=True, verbose_name="معلومات الجهاز")
    error_log = models.TextField(blank=True, verbose_name="سجل الأخطاء")
    screenshots = models.JSONField(default=list, blank=True, verbose_name="لقطات الشاشة")
    
    # المعالجة
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_mobile_feedback',
                                  verbose_name="مُعيّن إلى")
    response = models.TextField(blank=True, verbose_name="الرد")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الحل")
    
    # التوقيت
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تغذية راجعة للتطبيق المحمول"
        verbose_name_plural = "التغذية الراجعة للتطبيق المحمول"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feedback_type', 'status']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"


class MobileAppAnalytics(models.Model):
    """تحليلات التطبيق المحمول"""
    
    EVENT_TYPES = [
        ('APP_OPEN', 'فتح التطبيق'),
        ('APP_CLOSE', 'إغلاق التطبيق'),
        ('SCREEN_VIEW', 'عرض شاشة'),
        ('BUTTON_CLICK', 'نقر زر'),
        ('FEATURE_USE', 'استخدام ميزة'),
        ('ERROR', 'خطأ'),
        ('CRASH', 'تعطل'),
        ('PERFORMANCE', 'أداء'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الجهاز والمستخدم
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE,
                             related_name='analytics', verbose_name="الجهاز")
    session = models.ForeignKey(MobileAppSession, on_delete=models.SET_NULL, null=True,
                              related_name='analytics', verbose_name="الجلسة")
    
    # بيانات الحدث
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES,
                                verbose_name="نوع الحدث")
    event_name = models.CharField(max_length=100, verbose_name="اسم الحدث")
    event_data = models.JSONField(default=dict, blank=True, verbose_name="بيانات الحدث")
    
    # معلومات الشاشة/الصفحة
    screen_name = models.CharField(max_length=50, blank=True, verbose_name="اسم الشاشة")
    screen_class = models.CharField(max_length=50, blank=True, verbose_name="فئة الشاشة")
    
    # بيانات الأداء
    load_time = models.FloatField(null=True, blank=True, verbose_name="وقت التحميل (ثانية)")
    memory_usage = models.FloatField(null=True, blank=True, verbose_name="استخدام الذاكرة (MB)")
    battery_level = models.IntegerField(null=True, blank=True, verbose_name="مستوى البطارية")
    
    # التوقيت
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    class Meta:
        verbose_name = "تحليلات التطبيق المحمول"
        verbose_name_plural = "تحليلات التطبيق المحمول"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'event_type']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['screen_name']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.device.user.username}"