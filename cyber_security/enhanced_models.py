# نظام الأمان السيبراني المتطور والذكي
# Enhanced Intelligent Cyber Security System

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid
from ipaddress import ip_address, ip_network

User = get_user_model()

class SecurityThreatLevel(models.TextChoices):
    """مستويات التهديد الأمني"""
    LOW = 'LOW', 'منخفض'
    MEDIUM = 'MEDIUM', 'متوسط'
    HIGH = 'HIGH', 'عالي'
    CRITICAL = 'CRITICAL', 'حرج'
    EMERGENCY = 'EMERGENCY', 'طوارئ'

class SecurityEventType(models.TextChoices):
    """أنواع الأحداث الأمنية"""
    LOGIN_ATTEMPT = 'LOGIN_ATTEMPT', 'محاولة دخول'
    FAILED_LOGIN = 'FAILED_LOGIN', 'فشل في الدخول'
    SUCCESSFUL_LOGIN = 'SUCCESSFUL_LOGIN', 'دخول ناجح'
    BRUTE_FORCE = 'BRUTE_FORCE', 'هجوم القوة الغاشمة'
    SQL_INJECTION = 'SQL_INJECTION', 'حقن SQL'
    XSS_ATTEMPT = 'XSS_ATTEMPT', 'محاولة XSS'
    CSRF_ATTACK = 'CSRF_ATTACK', 'هجوم CSRF'
    PRIVILEGE_ESCALATION = 'PRIVILEGE_ESCALATION', 'تصعيد الصلاحيات'
    DATA_BREACH = 'DATA_BREACH', 'اختراق البيانات'
    MALWARE_DETECTION = 'MALWARE_DETECTION', 'كشف برامج ضارة'
    SUSPICIOUS_IP = 'SUSPICIOUS_IP', 'IP مشبوه'
    ANOMALY_DETECTION = 'ANOMALY_DETECTION', 'كشف الشذوذ'
    DDoS_ATTACK = 'DDOS_ATTACK', 'هجوم DDoS'
    PHISHING_ATTEMPT = 'PHISHING_ATTEMPT', 'محاولة احتيال'
    UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS', 'وصول غير مصرح'
    FILE_INTEGRITY_VIOLATION = 'FILE_INTEGRITY_VIOLATION', 'انتهاك سلامة الملفات'
    NETWORK_INTRUSION = 'NETWORK_INTRUSION', 'تسلل للشبكة'
    INSIDER_THREAT = 'INSIDER_THREAT', 'تهديد داخلي'

class SecurityPolicy(models.Model):
    """سياسات الأمان"""
    
    POLICY_TYPES = [
        ('PASSWORD', 'سياسة كلمة المرور'),
        ('ACCESS_CONTROL', 'التحكم في الوصول'),
        ('DATA_PROTECTION', 'حماية البيانات'),
        ('NETWORK_SECURITY', 'أمان الشبكة'),
        ('INCIDENT_RESPONSE', 'الاستجابة للحوادث'),
        ('COMPLIANCE', 'الامتثال'),
        ('BACKUP_RECOVERY', 'النسخ الاحتياطي والاستعادة'),
        ('USER_BEHAVIOR', 'سلوك المستخدم'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم السياسة")
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES, verbose_name="نوع السياسة")
    description = models.TextField(verbose_name="وصف السياسة")
    
    # محتوى السياسة
    rules = models.JSONField(default=dict, verbose_name="القواعد")
    parameters = models.JSONField(default=dict, verbose_name="المعاملات")
    thresholds = models.JSONField(default=dict, verbose_name="العتبات")
    
    # إعدادات السياسة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    enforcement_level = models.CharField(max_length=20, choices=[
        ('ADVISORY', 'استشاري'),
        ('WARNING', 'تحذير'),
        ('BLOCKING', 'حجب'),
        ('QUARANTINE', 'حجر صحي'),
    ], default='WARNING', verbose_name="مستوى التطبيق")
    
    # معلومات الإنشاء والتحديث
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_policies', verbose_name="أنشئت بواسطة")
    version = models.CharField(max_length=20, default="1.0", verbose_name="الإصدار")
    
    effective_date = models.DateTimeField(verbose_name="تاريخ السريان")
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ انتهاء الصلاحية")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "سياسة أمان"
        verbose_name_plural = "سياسات الأمان"
        ordering = ['policy_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_policy_type_display()})"

class SecurityEvent(models.Model):
    """سجل الأحداث الأمنية المطور"""
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف الحدث")
    event_type = models.CharField(max_length=50, choices=SecurityEventType.choices, 
                                verbose_name="نوع الحدث")
    threat_level = models.CharField(max_length=20, choices=SecurityThreatLevel.choices, 
                                  verbose_name="مستوى التهديد")
    
    # تفاصيل الحدث
    title = models.CharField(max_length=200, verbose_name="عنوان الحدث")
    description = models.TextField(verbose_name="وصف الحدث")
    
    # معلومات تقنية مفصلة
    source_ip = models.GenericIPAddressField(verbose_name="عنوان IP المصدر")
    destination_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP الوجهة")
    user_agent = models.TextField(blank=True, verbose_name="معرف المتصفح")
    request_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الطلب")
    request_method = models.CharField(max_length=10, blank=True, verbose_name="طريقة الطلب")
    
    # معلومات الجلسة
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    csrf_token = models.CharField(max_length=100, blank=True, verbose_name="رمز CSRF")
    
    # البيانات الخام والإضافية
    raw_data = models.JSONField(default=dict, verbose_name="البيانات الخام")
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    evidence = models.JSONField(default=dict, verbose_name="الأدلة")
    
    # المستخدم المتأثر
    affected_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="المستخدم المتأثر")
    
    # معلومات جغرافية
    geolocation = models.JSONField(default=dict, verbose_name="الموقع الجغرافي")
    country = models.CharField(max_length=100, blank=True, verbose_name="البلد")
    city = models.CharField(max_length=100, blank=True, verbose_name="المدينة")
    
    # التصنيف والتحليل
    attack_vector = models.CharField(max_length=100, blank=True, verbose_name="مسار الهجوم")
    vulnerability_exploited = models.CharField(max_length=200, blank=True, verbose_name="الثغرة المستغلة")
    impact_assessment = models.TextField(blank=True, verbose_name="تقييم التأثير")
    
    # حالة الحدث
    is_investigated = models.BooleanField(default=False, verbose_name="تم التحقيق")
    is_resolved = models.BooleanField(default=False, verbose_name="تم الحل")
    is_false_positive = models.BooleanField(default=False, verbose_name="إنذار كاذب")
    is_critical = models.BooleanField(default=False, verbose_name="حرج")
    
    # الاستجابة والإجراءات
    response_actions = models.JSONField(default=list, verbose_name="إجراءات الاستجابة")
    automated_response = models.BooleanField(default=False, verbose_name="استجابة تلقائية")
    
    # التوقيتات
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الكشف")
    investigated_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التحقيق")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    # معلومات المحقق
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='investigated_events', verbose_name="تم التحقيق بواسطة")
    resolution_notes = models.TextField(blank=True, verbose_name="ملاحظات الحل")
    
    class Meta:
        verbose_name = "حدث أمني"
        verbose_name_plural = "الأحداث الأمنية"
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['event_type', 'detected_at']),
            models.Index(fields=['threat_level', 'is_resolved']),
            models.Index(fields=['source_ip', 'detected_at']),
            models.Index(fields=['affected_user', 'event_type']),
            models.Index(fields=['is_critical', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.event_id} - {self.get_event_type_display()} - {self.get_threat_level_display()}"

class ThreatIntelligence(models.Model):
    """معلومات استخباراتية عن التهديدات المطورة"""
    
    THREAT_TYPES = [
        ('MALICIOUS_IP', 'IP ضار'),
        ('PHISHING_DOMAIN', 'نطاق احتيالي'),
        ('MALWARE_SIGNATURE', 'توقيع برنامج ضار'),
        ('ATTACK_PATTERN', 'نمط هجوم'),
        ('VULNERABILITY', 'ثغرة أمنية'),
        ('BOTNET', 'شبكة بوت'),
        ('C2_SERVER', 'خادم التحكم والسيطرة'),
        ('COMPROMISED_ACCOUNT', 'حساب مخترق'),
        ('SUSPICIOUS_BEHAVIOR', 'سلوك مشبوه'),
        ('ZERO_DAY', 'ثغرة يوم الصفر'),
    ]
    
    SOURCE_TYPES = [
        ('INTERNAL', 'داخلي'),
        ('COMMERCIAL', 'تجاري'),
        ('OPEN_SOURCE', 'مفتوح المصدر'),
        ('GOVERNMENT', 'حكومي'),
        ('COMMUNITY', 'مجتمعي'),
        ('HONEYPOT', 'طُعم'),
        ('PARTNER', 'شريك'),
    ]
    
    threat_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف التهديد")
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES, 
                                 verbose_name="نوع التهديد")
    indicator = models.CharField(max_length=500, verbose_name="المؤشر")
    description = models.TextField(verbose_name="الوصف")
    
    # تصنيف التهديد
    severity = models.CharField(max_length=20, choices=SecurityThreatLevel.choices,
                              verbose_name="الخطورة")
    confidence = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                 verbose_name="درجة الثقة")
    
    # مصدر المعلومات
    source = models.CharField(max_length=200, verbose_name="المصدر")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name="نوع المصدر")
    source_reliability = models.CharField(max_length=20, choices=[
        ('A', 'موثوق تماماً'),
        ('B', 'موثوق عادة'),
        ('C', 'موثوق نوعاً ما'),
        ('D', 'غير موثوق عادة'),
        ('E', 'غير موثوق'),
        ('F', 'موثوقية غير محددة'),
    ], verbose_name="موثوقية المصدر")
    
    # معلومات تقنية
    ioc_data = models.JSONField(default=dict, verbose_name="مؤشرات الاختراق")
    ttps = models.JSONField(default=list, verbose_name="التكتيكات والتقنيات والإجراءات")
    kill_chain_phase = models.CharField(max_length=100, blank=True, verbose_name="مرحلة سلسلة القتل")
    
    # معلومات الهجوم
    target_sectors = models.JSONField(default=list, verbose_name="القطاعات المستهدفة")
    attack_techniques = models.JSONField(default=list, verbose_name="تقنيات الهجوم")
    associated_groups = models.JSONField(default=list, verbose_name="المجموعات المرتبطة")
    
    # دورة الحياة
    first_seen = models.DateTimeField(verbose_name="أول مشاهدة")
    last_seen = models.DateTimeField(verbose_name="آخر مشاهدة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ انتهاء الصلاحية")
    
    # الإجراءات المقترحة
    recommended_actions = models.JSONField(default=list, verbose_name="الإجراءات المقترحة")
    mitigation_strategies = models.JSONField(default=list, verbose_name="استراتيجيات التخفيف")
    
    # التحديث والمتابعة
    update_frequency = models.CharField(max_length=20, choices=[
        ('REAL_TIME', 'فوري'),
        ('HOURLY', 'كل ساعة'),
        ('DAILY', 'يومي'),
        ('WEEKLY', 'أسبوعي'),
        ('MANUAL', 'يدوي'),
    ], default='DAILY', verbose_name="تكرار التحديث")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "معلومات استخباراتية"
        verbose_name_plural = "المعلومات الاستخباراتية"
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['threat_type', 'is_active']),
            models.Index(fields=['severity', 'confidence']),
            models.Index(fields=['first_seen', 'last_seen']),
        ]
    
    def __str__(self):
        return f"{self.threat_id} - {self.get_threat_type_display()}"

class SecurityMonitoring(models.Model):
    """مراقبة الأمان في الوقت الفعلي"""
    
    MONITORING_TYPES = [
        ('NETWORK_TRAFFIC', 'حركة الشبكة'),
        ('USER_BEHAVIOR', 'سلوك المستخدم'),
        ('SYSTEM_INTEGRITY', 'سلامة النظام'),
        ('FILE_INTEGRITY', 'سلامة الملفات'),
        ('DATABASE_ACTIVITY', 'نشاط قاعدة البيانات'),
        ('APPLICATION_SECURITY', 'أمان التطبيق'),
        ('ENDPOINT_SECURITY', 'أمان نقاط النهاية'),
        ('COMPLIANCE_MONITORING', 'مراقبة الامتثال'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('PAUSED', 'متوقف مؤقتاً'),
        ('STOPPED', 'متوقف'),
        ('ERROR', 'خطأ'),
        ('MAINTENANCE', 'صيانة'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم المراقبة")
    monitoring_type = models.CharField(max_length=50, choices=MONITORING_TYPES,
                                     verbose_name="نوع المراقبة")
    description = models.TextField(verbose_name="الوصف")
    
    # إعدادات المراقبة
    monitoring_rules = models.JSONField(default=dict, verbose_name="قواعد المراقبة")
    alert_thresholds = models.JSONField(default=dict, verbose_name="عتبات التنبيه")
    monitoring_interval = models.IntegerField(default=60, verbose_name="فترة المراقبة (ثانية)")
    
    # المصادر المراقبة
    monitored_resources = models.JSONField(default=list, verbose_name="الموارد المراقبة")
    data_sources = models.JSONField(default=list, verbose_name="مصادر البيانات")
    
    # الحالة والإحصائيات
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="حالة المراقبة")
    last_check = models.DateTimeField(null=True, blank=True, verbose_name="آخر فحص")
    events_detected = models.IntegerField(default=0, verbose_name="الأحداث المكتشفة")
    false_positives = models.IntegerField(default=0, verbose_name="الإنذارات الكاذبة")
    
    # إعدادات التنبيه
    enable_alerts = models.BooleanField(default=True, verbose_name="تفعيل التنبيهات")
    alert_recipients = models.JSONField(default=list, verbose_name="مستقبلي التنبيهات")
    escalation_rules = models.JSONField(default=dict, verbose_name="قواعد التصعيد")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_monitoring', verbose_name="أنشئت بواسطة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "مراقبة أمنية"
        verbose_name_plural = "المراقبة الأمنية"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_monitoring_type_display()})"

class SecurityAlert(models.Model):
    """تنبيهات الأمان"""
    
    ALERT_STATUS = [
        ('NEW', 'جديد'),
        ('ACKNOWLEDGED', 'تم التأكيد'),
        ('IN_PROGRESS', 'قيد المعالجة'),
        ('RESOLVED', 'تم الحل'),
        ('CLOSED', 'مغلق'),
        ('FALSE_POSITIVE', 'إنذار كاذب'),
    ]
    
    ALERT_SOURCES = [
        ('IDS', 'نظام كشف التسلل'),
        ('IPS', 'نظام منع التسلل'),
        ('SIEM', 'إدارة معلومات وأحداث الأمان'),
        ('ANTIVIRUS', 'مكافح الفيروسات'),
        ('FIREWALL', 'جدار الحماية'),
        ('MONITORING', 'المراقبة'),
        ('USER_REPORT', 'تقرير مستخدم'),
        ('AUTOMATED', 'تلقائي'),
    ]
    
    alert_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف التنبيه")
    title = models.CharField(max_length=200, verbose_name="عنوان التنبيه")
    description = models.TextField(verbose_name="وصف التنبيه")
    
    # تصنيف التنبيه
    severity = models.CharField(max_length=20, choices=SecurityThreatLevel.choices,
                              verbose_name="الخطورة")
    alert_type = models.CharField(max_length=50, choices=SecurityEventType.choices,
                                verbose_name="نوع التنبيه")
    source = models.CharField(max_length=20, choices=ALERT_SOURCES, verbose_name="المصدر")
    
    # الحدث المرتبط
    related_event = models.ForeignKey(SecurityEvent, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='alerts', verbose_name="الحدث المرتبط")
    
    # تفاصيل التنبيه
    details = models.JSONField(default=dict, verbose_name="التفاصيل")
    evidence = models.JSONField(default=dict, verbose_name="الأدلة")
    affected_assets = models.JSONField(default=list, verbose_name="الأصول المتأثرة")
    
    # حالة التنبيه
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='NEW',
                            verbose_name="حالة التنبيه")
    
    # المعالجة
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_alerts', verbose_name="مُعين إلى")
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='acknowledged_alerts', verbose_name="أُكد بواسطة")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='resolved_alerts', verbose_name="حُل بواسطة")
    
    # التوقيتات
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإطلاق")
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التأكيد")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    # الإجراءات المتخذة
    actions_taken = models.JSONField(default=list, verbose_name="الإجراءات المتخذة")
    resolution_notes = models.TextField(blank=True, verbose_name="ملاحظات الحل")
    
    class Meta:
        verbose_name = "تنبيه أمني"
        verbose_name_plural = "التنبيهات الأمنية"
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_id} - {self.title} - {self.get_severity_display()}"

class SecurityAuditLog(models.Model):
    """سجل مراجعة الأمان"""
    
    ACTION_TYPES = [
        ('LOGIN', 'تسجيل دخول'),
        ('LOGOUT', 'تسجيل خروج'),
        ('CREATE', 'إنشاء'),
        ('READ', 'قراءة'),
        ('UPDATE', 'تحديث'),
        ('DELETE', 'حذف'),
        ('EXPORT', 'تصدير'),
        ('IMPORT', 'استيراد'),
        ('PERMISSION_CHANGE', 'تغيير صلاحية'),
        ('CONFIGURATION_CHANGE', 'تغيير إعداد'),
        ('SYSTEM_ACCESS', 'وصول للنظام'),
        ('DATA_ACCESS', 'وصول للبيانات'),
    ]
    
    audit_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف المراجعة")
    
    # معلومات المستخدم
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                           related_name='audit_logs', verbose_name="المستخدم")
    username = models.CharField(max_length=150, verbose_name="اسم المستخدم")
    user_role = models.CharField(max_length=50, verbose_name="دور المستخدم")
    
    # تفاصيل الإجراء
    action = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name="الإجراء")
    resource = models.CharField(max_length=200, verbose_name="المورد")
    resource_id = models.CharField(max_length=100, blank=True, verbose_name="معرف المورد")
    
    # الكائن المتأثر
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # تفاصيل تقنية
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="معرف المتصفح")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    
    # البيانات قبل وبعد التغيير
    old_values = models.JSONField(default=dict, blank=True, verbose_name="القيم السابقة")
    new_values = models.JSONField(default=dict, blank=True, verbose_name="القيم الجديدة")
    
    # معلومات إضافية
    description = models.TextField(blank=True, verbose_name="الوصف")
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # النتيجة
    success = models.BooleanField(default=True, verbose_name="نجح")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    
    # التوقيت
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    class Meta:
        verbose_name = "سجل مراجعة"
        verbose_name_plural = "سجلات المراجعة"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'action', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['resource', 'action']),
            models.Index(fields=['success', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.get_action_display()} - {self.resource} - {self.timestamp}"

class SecurityIncident(models.Model):
    """حوادث الأمان الرئيسية"""
    
    INCIDENT_STATUS = [
        ('NEW', 'جديد'),
        ('ASSIGNED', 'مُعين'),
        ('IN_PROGRESS', 'قيد المعالجة'),
        ('ESCALATED', 'مُصعد'),
        ('RESOLVED', 'محلول'),
        ('CLOSED', 'مغلق'),
        ('REOPENED', 'مُعاد فتحه'),
    ]
    
    INCIDENT_CATEGORIES = [
        ('MALWARE', 'برامج ضارة'),
        ('PHISHING', 'احتيال'),
        ('DATA_BREACH', 'اختراق بيانات'),
        ('INSIDER_THREAT', 'تهديد داخلي'),
        ('DENIAL_OF_SERVICE', 'حرمان من الخدمة'),
        ('UNAUTHORIZED_ACCESS', 'وصول غير مصرح'),
        ('SYSTEM_COMPROMISE', 'اختراق النظام'),
        ('POLICY_VIOLATION', 'انتهاك السياسة'),
        ('PHYSICAL_SECURITY', 'الأمان الفيزيائي'),
        ('OTHER', 'أخرى'),
    ]
    
    incident_id = models.CharField(max_length=20, unique=True, verbose_name="رقم الحادثة")
    title = models.CharField(max_length=200, verbose_name="عنوان الحادثة")
    description = models.TextField(verbose_name="وصف الحادثة")
    
    # تصنيف الحادثة
    category = models.CharField(max_length=50, choices=INCIDENT_CATEGORIES,
                              verbose_name="فئة الحادثة")
    severity = models.CharField(max_length=20, choices=SecurityThreatLevel.choices,
                              verbose_name="الخطورة")
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ], verbose_name="الأولوية")
    
    # الأحداث والتنبيهات المرتبطة
    related_events = models.ManyToManyField(SecurityEvent, blank=True,
                                          related_name='incidents', verbose_name="الأحداث المرتبطة")
    related_alerts = models.ManyToManyField(SecurityAlert, blank=True,
                                          related_name='incidents', verbose_name="التنبيهات المرتبطة")
    
    # التأثير والأضرار
    affected_systems = models.JSONField(default=list, verbose_name="الأنظمة المتأثرة")
    affected_users = models.ManyToManyField(User, blank=True,
                                          related_name='security_incidents', verbose_name="المستخدمون المتأثرون")
    business_impact = models.TextField(blank=True, verbose_name="التأثير على الأعمال")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       verbose_name="التكلفة المقدرة")
    
    # فريق الاستجابة
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS, default='NEW',
                            verbose_name="حالة الحادثة")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_incidents', verbose_name="مُعين إلى")
    incident_commander = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='commanded_incidents', verbose_name="قائد الحادثة")
    response_team = models.ManyToManyField(User, blank=True,
                                         related_name='response_incidents', verbose_name="فريق الاستجابة")
    
    # الجدول الزمني
    reported_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإبلاغ")
    occurred_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحدوث")
    detected_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الكشف")
    contained_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الاحتواء")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    # الاستجابة والحل
    containment_actions = models.JSONField(default=list, verbose_name="إجراءات الاحتواء")
    eradication_actions = models.JSONField(default=list, verbose_name="إجراءات الإزالة")
    recovery_actions = models.JSONField(default=list, verbose_name="إجراءات الاستعادة")
    lessons_learned = models.TextField(blank=True, verbose_name="الدروس المستفادة")
    
    # التوثيق
    evidence_collected = models.JSONField(default=list, verbose_name="الأدلة المجمعة")
    forensic_analysis = models.TextField(blank=True, verbose_name="التحليل الجنائي")
    final_report = models.TextField(blank=True, verbose_name="التقرير النهائي")
    
    class Meta:
        verbose_name = "حادثة أمنية"
        verbose_name_plural = "الحوادث الأمنية"
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['category', 'reported_at']),
        ]
    
    def __str__(self):
        return f"{self.incident_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        """توليد رقم حادثة تلقائي"""
        if not self.incident_id:
            year = timezone.now().year
            count = SecurityIncident.objects.filter(
                reported_at__year=year
            ).count() + 1
            self.incident_id = f"INC{year}{count:04d}"
        super().save(*args, **kwargs)