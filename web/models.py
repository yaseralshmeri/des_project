# نماذج واجهة الويب
# Web Interface Models

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class WebPageView(models.Model):
    """مشاهدات صفحات الويب"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='web_page_views', verbose_name="المستخدم")
    
    # معلومات الصفحة
    page_url = models.URLField(verbose_name="رابط الصفحة")
    page_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان الصفحة")
    referrer = models.URLField(blank=True, verbose_name="المرجع")
    
    # معلومات المتصفح
    user_agent = models.TextField(blank=True, verbose_name="متصفح المستخدم")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    
    # الوقت
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت المشاهدة")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    
    class Meta:
        verbose_name = "مشاهدة صفحة ويب"
        verbose_name_plural = "مشاهدات صفحات الويب"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['page_url']),
        ]
    
    def __str__(self):
        return f"{self.page_title or self.page_url} - {self.timestamp}"


class UserPreference(models.Model):
    """تفضيلات المستخدم لواجهة الويب"""
    
    THEME_CHOICES = [
        ('light', 'فاتح'),
        ('dark', 'داكن'),
        ('auto', 'تلقائي'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                               related_name='web_preferences', verbose_name="المستخدم")
    
    # إعدادات الواجهة
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, 
                           default='light', verbose_name="المظهر")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES,
                              default='ar', verbose_name="اللغة")
    
    # إعدادات الصفحة الرئيسية
    dashboard_layout = models.JSONField(default=dict, verbose_name="تخطيط لوحة التحكم")
    widgets_enabled = models.JSONField(default=list, verbose_name="الأدوات المفعلة")
    
    # إعدادات العرض
    items_per_page = models.IntegerField(default=25, verbose_name="عناصر كل صفحة")
    show_sidebar = models.BooleanField(default=True, verbose_name="إظهار الشريط الجانبي")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تفضيلات المستخدم للويب"
        verbose_name_plural = "تفضيلات المستخدمين للويب"
    
    def __str__(self):
        return f"تفضيلات {self.user.username}"


class WebSession(models.Model):
    """جلسات الويب"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='web_sessions', verbose_name="المستخدم")
    
    # معلومات الجلسة
    session_key = models.CharField(max_length=40, unique=True, verbose_name="مفتاح الجلسة")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    
    # التوقيت
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="وقت البداية")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="آخر نشاط")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الانتهاء")
    
    # معلومات إضافية
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    pages_visited = models.IntegerField(default=0, verbose_name="الصفحات المزارة")
    
    class Meta:
        verbose_name = "جلسة ويب"
        verbose_name_plural = "جلسات الويب"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.start_time}"
    
    @property
    def duration(self):
        """مدة الجلسة"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time