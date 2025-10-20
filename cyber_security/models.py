# نظام الأمان السيبراني المتقدم
# Advanced Cyber Security System

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

class SecurityThreatLevel(models.TextChoices):
    """مستويات التهديد الأمني"""
    LOW = 'low', 'منخفض'
    MEDIUM = 'medium', 'متوسط'
    HIGH = 'high', 'عالي'
    CRITICAL = 'critical', 'حرج'

class SecurityEventType(models.TextChoices):
    """أنواع الأحداث الأمنية"""
    LOGIN_ATTEMPT = 'login_attempt', 'محاولة دخول'
    FAILED_LOGIN = 'failed_login', 'فشل في الدخول'
    BRUTE_FORCE = 'brute_force', 'هجوم القوة الغاشمة'
    SQL_INJECTION = 'sql_injection', 'حقن SQL'
    XSS_ATTEMPT = 'xss_attempt', 'محاولة XSS'
    CSRF_ATTACK = 'csrf_attack', 'هجوم CSRF'
    PRIVILEGE_ESCALATION = 'privilege_escalation', 'تصعيد الصلاحيات'
    DATA_BREACH = 'data_breach', 'اختراق البيانات'
    MALWARE_DETECTION = 'malware_detection', 'كشف برامج ضارة'
    SUSPICIOUS_IP = 'suspicious_ip', 'IP مشبوه'
    ANOMALY_DETECTION = 'anomaly_detection', 'كشف الشذوذ'

class SecurityEvent(models.Model):
    """سجل الأحداث الأمنية"""
    
    event_type = models.CharField(max_length=50, choices=SecurityEventType.choices, 
                                verbose_name="نوع الحدث")
    threat_level = models.CharField(max_length=20, choices=SecurityThreatLevel.choices, 
                                  verbose_name="مستوى التهديد")
    
    # تفاصيل الحدث
    title = models.CharField(max_length=200, verbose_name="عنوان الحدث")
    description = models.TextField(verbose_name="وصف الحدث")
    
    # معلومات تقنية
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="معرف المتصفح")
    request_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الطلب")
    request_method = models.CharField(max_length=10, blank=True, verbose_name="طريقة الطلب")
    
    # البيانات الإضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # المستخدم المتأثر
    affected_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="المستخدم المتأثر")
    
    # حالة الحدث
    is_investigated = models.BooleanField(default=False, verbose_name="تم التحقيق")
    is_resolved = models.BooleanField(default=False, verbose_name="تم الحل")
    is_false_positive = models.BooleanField(default=False, verbose_name="إنذار كاذب")
    
    # التوقيتات
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الكشف")
    investigated_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التحقيق")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    class Meta:
        verbose_name = "حدث أمني"
        verbose_name_plural = "الأحداث الأمنية"
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['event_type', 'detected_at']),
            models.Index(fields=['threat_level', 'is_resolved']),
            models.Index(fields=['ip_address', 'detected_at']),
        ]

class ThreatIntelligence(models.Model):
    """معلومات استخباراتية عن التهديدات"""
    
    THREAT_TYPES = [
        ('malicious_ip', 'IP ضار'),
        ('phishing_domain', 'نطاق احتيالي'),
        ('malware_signature', 'توقيع برنامج ضار'),
        ('attack_pattern', 'نمط هجوم'),
        ('vulnerability', 'ثغرة أمنية'),
    ]
    
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES, 
                                 verbose_name="نوع التهديد")
    indicator = models.CharField(max_length=500, verbose_name="المؤشر")
    description = models.TextField(verbose_name="الوصف")
    
    # تصنيف التهديد
    severity = models.CharField(max_length=20, choices=SecurityThreatLevel.choices,
                              verbose_name="الخطورة")
    confidence = models.FloatField(default=0.0, verbose_name="درجة الثقة")
    
    # مصدر المعلومات
    source = models.CharField(max_length=200, verbose_name="المصدر")
    source_url = models.URLField(blank=True, verbose_name="رابط المصدر")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_seen = models.DateTimeField(verbose_name="آخر مشاهدة")
    
    # التوقيتات
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "معلومات التهديد"
        verbose_name_plural = "معلومات التهديدات"
        unique_together = ['threat_type', 'indicator']

class SecurityRule(models.Model):
    """قواعد الأمان التلقائية"""
    
    RULE_TYPES = [
        ('rate_limiting', 'تحديد المعدل'),
        ('ip_blocking', 'حظر IP'),
        ('pattern_detection', 'كشف الأنماط'),
        ('anomaly_detection', 'كشف الشذوذ'),
        ('geo_blocking', 'حظر جغرافي'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم القاعدة")
    description = models.TextField(verbose_name="وصف القاعدة")
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES, 
                               verbose_name="نوع القاعدة")
    
    # معايير القاعدة
    conditions = models.JSONField(verbose_name="الشروط")
    actions = models.JSONField(verbose_name="الإجراءات")
    
    # إعدادات القاعدة
    priority = models.IntegerField(default=100, verbose_name="الأولوية")
    is_enabled = models.BooleanField(default=True, verbose_name="مفعلة")
    
    # الإحصائيات
    triggered_count = models.IntegerField(default=0, verbose_name="عدد التفعيل")
    last_triggered = models.DateTimeField(null=True, blank=True, 
                                        verbose_name="آخر تفعيل")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "قاعدة أمنية"
        verbose_name_plural = "القواعد الأمنية"
        ordering = ['priority', 'name']

class SecurityIncident(models.Model):
    """الحوادث الأمنية"""
    
    INCIDENT_STATUS = [
        ('open', 'مفتوح'),
        ('investigating', 'قيد التحقيق'),
        ('resolved', 'محلول'),
        ('closed', 'مغلق'),
        ('false_positive', 'إنذار كاذب'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="عنوان الحادث")
    description = models.TextField(verbose_name="وصف الحادث")
    
    # تصنيف الحادث
    incident_type = models.CharField(max_length=50, choices=SecurityEventType.choices,
                                   verbose_name="نوع الحادث")
    severity = models.CharField(max_length=20, choices=SecurityThreatLevel.choices,
                              verbose_name="الخطورة")
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS, default='open',
                            verbose_name="الحالة")
    
    # الأحداث المرتبطة
    related_events = models.ManyToManyField(SecurityEvent, blank=True,
                                          verbose_name="الأحداث المرتبطة")
    
    # المسؤوليات
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_incidents',
                                  verbose_name="مكلف بالحل")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='reported_incidents',
                               verbose_name="المبلغ")
    
    # التأثير
    affected_systems = models.JSONField(default=list, verbose_name="الأنظمة المتأثرة")
    impact_assessment = models.TextField(blank=True, verbose_name="تقييم التأثير")
    
    # الاستجابة
    response_actions = models.JSONField(default=list, verbose_name="إجراءات الاستجابة")
    lessons_learned = models.TextField(blank=True, verbose_name="الدروس المستفادة")
    
    # التوقيتات
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")
    first_response_at = models.DateTimeField(null=True, blank=True, 
                                           verbose_name="وقت أول استجابة")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    class Meta:
        verbose_name = "حادث أمني"
        verbose_name_plural = "الحوادث الأمنية"
        ordering = ['-created_at']

class UserBehaviorProfile(models.Model):
    """ملف سلوك المستخدم لكشف الشذوذ"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               verbose_name="المستخدم")
    
    # أنماط تسجيل الدخول
    typical_login_hours = models.JSONField(default=list, verbose_name="ساعات الدخول المعتادة")
    typical_locations = models.JSONField(default=list, verbose_name="المواقع المعتادة")
    typical_devices = models.JSONField(default=list, verbose_name="الأجهزة المعتادة")
    
    # أنماط الاستخدام
    typical_pages = models.JSONField(default=list, verbose_name="الصفحات المعتادة")
    typical_session_duration = models.IntegerField(default=0, 
                                                 verbose_name="مدة الجلسة المعتادة")
    
    # الإحصائيات
    total_logins = models.IntegerField(default=0, verbose_name="إجمالي تسجيلات الدخول")
    failed_logins = models.IntegerField(default=0, verbose_name="فشل تسجيل الدخول")
    last_login_analyzed = models.DateTimeField(null=True, blank=True,
                                             verbose_name="آخر تحليل للدخول")
    
    # مقاييس الشذوذ
    anomaly_score = models.FloatField(default=0.0, verbose_name="درجة الشذوذ")
    risk_score = models.FloatField(default=0.0, verbose_name="درجة المخاطر")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ملف سلوك المستخدم"
        verbose_name_plural = "ملفات سلوك المستخدمين"

class SecurityAuditLog(models.Model):
    """سجل مراجعة الأمان"""
    
    ACTION_TYPES = [
        ('create', 'إنشاء'),
        ('read', 'قراءة'),
        ('update', 'تحديث'),
        ('delete', 'حذف'),
        ('login', 'دخول'),
        ('logout', 'خروج'),
        ('permission_change', 'تغيير صلاحية'),
        ('password_change', 'تغيير كلمة مرور'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="المستخدم")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES,
                                 verbose_name="نوع الإجراء")
    
    # تفاصيل الإجراء
    description = models.TextField(verbose_name="وصف الإجراء")
    
    # الكائن المتأثر
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                   null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # معلومات تقنية
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="معرف المتصفح")
    
    # البيانات قبل وبعد التغيير
    old_values = models.JSONField(null=True, blank=True, verbose_name="القيم السابقة")
    new_values = models.JSONField(null=True, blank=True, verbose_name="القيم الجديدة")
    
    # النتيجة
    success = models.BooleanField(default=True, verbose_name="نجح")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإجراء")
    
    class Meta:
        verbose_name = "سجل مراجعة أمني"
        verbose_name_plural = "سجلات المراجعة الأمنية"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

class VulnerabilityAssessment(models.Model):
    """تقييم الثغرات الأمنية"""
    
    ASSESSMENT_TYPES = [
        ('automated_scan', 'فحص آلي'),
        ('manual_test', 'اختبار يدوي'),
        ('penetration_test', 'اختبار اختراق'),
        ('code_review', 'مراجعة كود'),
    ]
    
    VULNERABILITY_SEVERITY = [
        ('info', 'معلوماتي'),
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي'),
        ('critical', 'حرج'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="عنوان التقييم")
    description = models.TextField(verbose_name="وصف التقييم")
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES,
                                     verbose_name="نوع التقييم")
    
    # نطاق التقييم
    target_systems = models.JSONField(default=list, verbose_name="الأنظمة المستهدفة")
    scope = models.TextField(verbose_name="نطاق التقييم")
    
    # النتائج
    vulnerabilities_found = models.JSONField(default=list, verbose_name="الثغرات المكتشفة")
    risk_rating = models.CharField(max_length=20, choices=VULNERABILITY_SEVERITY,
                                 verbose_name="تقييم المخاطر")
    
    # التوصيات
    recommendations = models.JSONField(default=list, verbose_name="التوصيات")
    remediation_priority = models.CharField(max_length=20, choices=VULNERABILITY_SEVERITY,
                                          verbose_name="أولوية الإصلاح")
    
    # المسؤوليات
    conducted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   verbose_name="منفذ التقييم")
    
    # التوقيتات
    started_at = models.DateTimeField(verbose_name="وقت البدء")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الانتهاء")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "تقييم ثغرة أمنية"
        verbose_name_plural = "تقييمات الثغرات الأمنية"
        ordering = ['-created_at']

class SecurityConfiguration(models.Model):
    """إعدادات الأمان"""
    
    CONFIG_CATEGORIES = [
        ('authentication', 'المصادقة'),
        ('authorization', 'التخويل'),
        ('encryption', 'التشفير'),
        ('monitoring', 'المراقبة'),
        ('backup', 'النسخ الاحتياطي'),
        ('network', 'الشبكة'),
    ]
    
    category = models.CharField(max_length=50, choices=CONFIG_CATEGORIES,
                              verbose_name="الفئة")
    setting_name = models.CharField(max_length=200, verbose_name="اسم الإعداد")
    setting_value = models.JSONField(verbose_name="قيمة الإعداد")
    
    description = models.TextField(verbose_name="الوصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_critical = models.BooleanField(default=False, verbose_name="حرج")
    
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       verbose_name="آخر تعديل بواسطة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "إعداد أمني"
        verbose_name_plural = "الإعدادات الأمنية"
        unique_together = ['category', 'setting_name']