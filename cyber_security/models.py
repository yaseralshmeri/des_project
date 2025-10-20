# نظام الأمان السيبراني المتقدم
# Advanced Cybersecurity System

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import json
import hashlib

User = get_user_model()

class SecurityThreat(models.Model):
    """التهديدات الأمنية"""
    
    THREAT_TYPES = [
        ('MALWARE', 'برمجيات خبيثة'),
        ('PHISHING', 'تصيد'),
        ('SQL_INJECTION', 'حقن SQL'),
        ('XSS', 'تنفيذ سكريبت متصفح'),
        ('CSRF', 'تزوير طلب عبر المواقع'),
        ('BRUTE_FORCE', 'قوة غاشمة'),
        ('DOS', 'حرمان من الخدمة'),
        ('DDOS', 'حرمان موزع من الخدمة'),
        ('DATA_BREACH', 'اختراق بيانات'),
        ('UNAUTHORIZED_ACCESS', 'وصول غير مصرح'),
        ('INSIDER_THREAT', 'تهديد داخلي'),
        ('SOCIAL_ENGINEERING', 'هندسة اجتماعية'),
        ('RANSOMWARE', 'فدية إلكترونية'),
        ('APT', 'تهديد مستمر متقدم'),
        ('ZERO_DAY', 'يوم صفر'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
        ('EMERGENCY', 'طوارئ'),
    ]
    
    STATUS_CHOICES = [
        ('DETECTED', 'مكتشف'),
        ('ANALYZING', 'تحت التحليل'),
        ('CONFIRMED', 'مؤكد'),
        ('MITIGATING', 'تحت المعالجة'),
        ('RESOLVED', 'مُحلول'),
        ('FALSE_POSITIVE', 'إنذار كاذب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات التهديد الأساسية
    threat_id = models.CharField(max_length=50, unique=True, verbose_name="معرف التهديد")
    threat_type = models.CharField(max_length=30, choices=THREAT_TYPES,
                                 verbose_name="نوع التهديد")
    title = models.CharField(max_length=200, verbose_name="عنوان التهديد")
    description = models.TextField(verbose_name="وصف التهديد")
    
    # خطورة التهديد
    severity_level = models.CharField(max_length=15, choices=SEVERITY_LEVELS,
                                    verbose_name="مستوى الخطورة")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   verbose_name="نقاط المخاطر")
    
    # معلومات المصدر
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP المصدر")
    source_country = models.CharField(max_length=100, blank=True, verbose_name="دولة المصدر")
    source_user_agent = models.TextField(blank=True, verbose_name="متصفح المصدر")
    
    # المستخدم المتأثر
    affected_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='security_threats',
                                    verbose_name="المستخدم المتأثر")
    affected_resources = models.JSONField(default=list, verbose_name="الموارد المتأثرة")
    
    # تفاصيل الهجوم
    attack_vector = models.CharField(max_length=100, blank=True, verbose_name="متجه الهجوم")
    attack_signature = models.TextField(blank=True, verbose_name="بصمة الهجوم")
    payload = models.TextField(blank=True, verbose_name="الحمولة")
    request_details = models.JSONField(default=dict, verbose_name="تفاصيل الطلب")
    
    # الحالة والاستجابة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DETECTED',
                            verbose_name="الحالة")
    automated_response = models.JSONField(default=dict, verbose_name="الاستجابة التلقائية")
    manual_actions = models.JSONField(default=list, verbose_name="الإجراءات اليدوية")
    
    # التوقيت
    first_detected = models.DateTimeField(auto_now_add=True, verbose_name="أول اكتشاف")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="آخر ظهور")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الحل")
    
    # المحلل الأمني
    assigned_analyst = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='assigned_threats',
                                       verbose_name="المحلل المكلف")
    analysis_notes = models.TextField(blank=True, verbose_name="ملاحظات التحليل")
    
    # معلومات إضافية
    indicators_of_compromise = models.JSONField(default=list, verbose_name="مؤشرات الاختراق")
    threat_intelligence = models.JSONField(default=dict, verbose_name="استخبارات التهديد")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تهديد أمني"
        verbose_name_plural = "التهديدات الأمنية"
        ordering = ['-risk_score', '-first_detected']
        indexes = [
            models.Index(fields=['threat_type', 'severity_level']),
            models.Index(fields=['source_ip']),
            models.Index(fields=['status']),
            models.Index(fields=['first_detected']),
            models.Index(fields=['affected_user']),
        ]
    
    def __str__(self):
        return f"{self.threat_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.threat_id:
            self.threat_id = self.generate_threat_id()
        super().save(*args, **kwargs)
    
    def generate_threat_id(self):
        """توليد معرف تهديد فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        threat_code = self.threat_type[:3].upper()
        return f"THR-{threat_code}-{timestamp}"
    
    @property
    def is_active(self):
        """هل التهديد نشط"""
        return self.status not in ['RESOLVED', 'FALSE_POSITIVE']
    
    @property
    def response_time(self):
        """وقت الاستجابة"""
        if self.resolved_at:
            return self.resolved_at - self.first_detected
        return timezone.now() - self.first_detected


class SecurityIncident(models.Model):
    """الحوادث الأمنية"""
    
    INCIDENT_TYPES = [
        ('SECURITY_BREACH', 'اختراق أمني'),
        ('DATA_LEAK', 'تسريب بيانات'),
        ('SYSTEM_COMPROMISE', 'اختراق نظام'),
        ('ACCOUNT_TAKEOVER', 'استحواذ على حساب'),
        ('FRAUD', 'احتيال'),
        ('POLICY_VIOLATION', 'انتهاك سياسة'),
        ('SUSPICIOUS_ACTIVITY', 'نشاط مشبوه'),
        ('MALWARE_INFECTION', 'إصابة ببرمجية خبيثة'),
        ('PHISHING_ATTACK', 'هجوم تصيد'),
        ('INSIDER_THREAT', 'تهديد داخلي'),
    ]
    
    IMPACT_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'مفتوح'),
        ('IN_PROGRESS', 'قيد المعالجة'),
        ('CONTAINED', 'محتوى'),
        ('RESOLVED', 'مُحلول'),
        ('CLOSED', 'مُغلق'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الحادث الأساسية
    incident_id = models.CharField(max_length=50, unique=True, verbose_name="معرف الحادث")
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPES,
                                   verbose_name="نوع الحادث")
    title = models.CharField(max_length=200, verbose_name="عنوان الحادث")
    description = models.TextField(verbose_name="وصف الحادث")
    
    # التأثير والخطورة
    impact_level = models.CharField(max_length=15, choices=IMPACT_LEVELS,
                                  verbose_name="مستوى التأثير")
    affected_systems = models.JSONField(default=list, verbose_name="الأنظمة المتأثرة")
    affected_data_types = models.JSONField(default=list, verbose_name="أنواع البيانات المتأثرة")
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                       verbose_name="التكلفة المُقدرة")
    
    # المستخدمون المتأثرون
    affected_users = models.ManyToManyField(User, related_name='security_incidents',
                                          blank=True, verbose_name="المستخدمون المتأثرون")
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                               related_name='reported_incidents',
                               verbose_name="المُبلغ")
    
    # فريق الاستجابة
    incident_commander = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='commanded_incidents',
                                         verbose_name="قائد الحادث")
    response_team = models.ManyToManyField(User, related_name='response_incidents',
                                         blank=True, verbose_name="فريق الاستجابة")
    
    # التهديدات المرتبطة
    related_threats = models.ManyToManyField(SecurityThreat, related_name='incidents',
                                           blank=True, verbose_name="التهديدات المرتبطة")
    
    # التوقيت
    occurred_at = models.DateTimeField(verbose_name="وقت الحدوث")
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الاكتشاف")
    contained_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الاحتواء")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    # الحالة والتتبع
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN',
                            verbose_name="الحالة")
    priority = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)],
                                 verbose_name="الأولوية")
    
    # التحليل والتحقيق
    root_cause = models.TextField(blank=True, verbose_name="السبب الجذري")
    lessons_learned = models.TextField(blank=True, verbose_name="الدروس المستفادة")
    preventive_measures = models.JSONField(default=list, verbose_name="التدابير الوقائية")
    
    # التواصل
    stakeholders_notified = models.JSONField(default=list, verbose_name="الأطراف المُخطرة")
    external_notifications = models.JSONField(default=list, verbose_name="الإخطارات الخارجية")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "حادث أمني"
        verbose_name_plural = "الحوادث الأمنية"
        ordering = ['-priority', '-occurred_at']
        indexes = [
            models.Index(fields=['incident_type', 'status']),
            models.Index(fields=['impact_level']),
            models.Index(fields=['occurred_at']),
            models.Index(fields=['reporter']),
        ]
    
    def __str__(self):
        return f"{self.incident_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.incident_id:
            self.incident_id = self.generate_incident_id()
        super().save(*args, **kwargs)
    
    def generate_incident_id(self):
        """توليد معرف حادث فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        incident_code = self.incident_type[:3].upper()
        return f"INC-{incident_code}-{timestamp}"
    
    @property
    def detection_time(self):
        """وقت الاكتشاف"""
        return self.detected_at - self.occurred_at
    
    @property
    def containment_time(self):
        """وقت الاحتواء"""
        if self.contained_at:
            return self.contained_at - self.detected_at
        return None
    
    @property
    def resolution_time(self):
        """وقت الحل"""
        if self.resolved_at:
            return self.resolved_at - self.detected_at
        return None


class BehaviorAnalysis(models.Model):
    """تحليل السلوك للكشف عن الأنشطة المشبوهة"""
    
    BEHAVIOR_TYPES = [
        ('LOGIN_PATTERN', 'نمط تسجيل الدخول'),
        ('ACCESS_PATTERN', 'نمط الوصول'),
        ('DATA_ACCESS', 'الوصول للبيانات'),
        ('SYSTEM_USAGE', 'استخدام النظام'),
        ('NETWORK_ACTIVITY', 'نشاط الشبكة'),
        ('FILE_OPERATIONS', 'عمليات الملفات'),
        ('PRIVILEGE_USAGE', 'استخدام الصلاحيات'),
        ('TIME_BASED', 'مبني على الوقت'),
    ]
    
    ANOMALY_LEVELS = [
        ('NORMAL', 'طبيعي'),
        ('SUSPICIOUS', 'مشبوه'),
        ('ANOMALOUS', 'شاذ'),
        ('CRITICAL', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستخدم محل التحليل
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='behavior_analyses', verbose_name="المستخدم")
    
    # نوع السلوك المُحلل
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_TYPES,
                                   verbose_name="نوع السلوك")
    
    # البيانات السلوكية
    baseline_behavior = models.JSONField(default=dict, verbose_name="السلوك الأساسي")
    current_behavior = models.JSONField(default=dict, verbose_name="السلوك الحالي")
    behavioral_metrics = models.JSONField(default=dict, verbose_name="مقاييس السلوك")
    
    # تحليل الشذوذ
    anomaly_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000,
                                      validators=[MinValueValidator(0), MaxValueValidator(1)],
                                      verbose_name="نقاط الشذوذ")
    anomaly_level = models.CharField(max_length=15, choices=ANOMALY_LEVELS, default='NORMAL',
                                   verbose_name="مستوى الشذوذ")
    anomaly_details = models.JSONField(default=list, verbose_name="تفاصيل الشذوذ")
    
    # السياق الزمني
    analysis_period_start = models.DateTimeField(verbose_name="بداية فترة التحليل")
    analysis_period_end = models.DateTimeField(verbose_name="نهاية فترة التحليل")
    
    # نتائج التحليل
    risk_indicators = models.JSONField(default=list, verbose_name="مؤشرات المخاطر")
    recommended_actions = models.JSONField(default=list, verbose_name="الإجراءات المُوصى بها")
    confidence_level = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="مستوى الثقة")
    
    # المتابعة
    is_flagged = models.BooleanField(default=False, verbose_name="مُعلم")
    follow_up_required = models.BooleanField(default=False, verbose_name="يتطلب متابعة")
    analyst_notes = models.TextField(blank=True, verbose_name="ملاحظات المحلل")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تحليل سلوك"
        verbose_name_plural = "تحليلات السلوك"
        ordering = ['-anomaly_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'behavior_type']),
            models.Index(fields=['anomaly_level']),
            models.Index(fields=['is_flagged']),
            models.Index(fields=['analysis_period_start', 'analysis_period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.get_behavior_type_display()}"
    
    @property
    def is_high_risk(self):
        """هل هو عالي المخاطر"""
        return self.anomaly_level in ['ANOMALOUS', 'CRITICAL'] or float(self.anomaly_score) > 0.7


class SecurityAuditLog(models.Model):
    """سجل التدقيق الأمني"""
    
    EVENT_TYPES = [
        ('AUTHENTICATION', 'مصادقة'),
        ('AUTHORIZATION', 'تفويض'),
        ('DATA_ACCESS', 'الوصول للبيانات'),
        ('DATA_MODIFICATION', 'تعديل البيانات'),
        ('SYSTEM_ACCESS', 'الوصول للنظام'),
        ('CONFIGURATION_CHANGE', 'تغيير إعدادات'),
        ('PRIVILEGE_ESCALATION', 'رفع صلاحيات'),
        ('SECURITY_VIOLATION', 'انتهاك أمني'),
        ('POLICY_VIOLATION', 'انتهاك سياسة'),
        ('SUSPICIOUS_ACTIVITY', 'نشاط مشبوه'),
    ]
    
    SEVERITY_LEVELS = [
        ('INFO', 'معلوماتي'),
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الحدث
    event_id = models.CharField(max_length=50, unique=True, verbose_name="معرف الحدث")
    event_type = models.CharField(max_length=25, choices=EVENT_TYPES,
                                verbose_name="نوع الحدث")
    event_description = models.CharField(max_length=500, verbose_name="وصف الحدث")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='INFO',
                              verbose_name="الخطورة")
    
    # المستخدم والجلسة
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='security_audit_logs', verbose_name="المستخدم")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    
    # معلومات الطلب
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="متصفح المستخدم")
    request_method = models.CharField(max_length=10, blank=True, verbose_name="طريقة الطلب")
    request_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الطلب")
    request_data = models.JSONField(default=dict, verbose_name="بيانات الطلب")
    
    # النتيجة والاستجابة
    was_successful = models.BooleanField(verbose_name="نجح الحدث")
    response_code = models.IntegerField(null=True, blank=True, verbose_name="رمز الاستجابة")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    
    # الموارد المتأثرة
    affected_objects = models.JSONField(default=list, verbose_name="الكائنات المتأثرة")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # معلومات إضافية
    additional_data = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   verbose_name="نقاط المخاطر")
    
    # التحليل التلقائي
    automated_analysis = models.JSONField(default=dict, verbose_name="التحليل التلقائي")
    threat_indicators = models.JSONField(default=list, verbose_name="مؤشرات التهديد")
    
    # التوقيت
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    class Meta:
        verbose_name = "سجل تدقيق أمني"
        verbose_name_plural = "سجلات التدقيق الأمني"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['was_successful']),
            models.Index(fields=['risk_score']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_id} - {self.event_description}"
    
    def save(self, *args, **kwargs):
        if not self.event_id:
            self.event_id = self.generate_event_id()
        super().save(*args, **kwargs)
    
    def generate_event_id(self):
        """توليد معرف حدث فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
        event_hash = hashlib.md5(f"{self.event_type}{timestamp}".encode()).hexdigest()[:8]
        return f"EVT-{event_hash.upper()}"


class SecurityPolicy(models.Model):
    """سياسات الأمان"""
    
    POLICY_CATEGORIES = [
        ('AUTHENTICATION', 'مصادقة'),
        ('AUTHORIZATION', 'تفويض'),
        ('PASSWORD', 'كلمة المرور'),
        ('SESSION', 'الجلسة'),
        ('DATA_PROTECTION', 'حماية البيانات'),
        ('NETWORK_SECURITY', 'أمان الشبكة'),
        ('INCIDENT_RESPONSE', 'الاستجابة للحوادث'),
        ('COMPLIANCE', 'الامتثال'),
        ('THREAT_DETECTION', 'اكتشاف التهديدات'),
        ('ACCESS_CONTROL', 'التحكم في الوصول'),
    ]
    
    ENFORCEMENT_LEVELS = [
        ('STRICT', 'صارم'),
        ('MODERATE', 'متوسط'),
        ('LENIENT', 'متساهل'),
        ('MONITOR_ONLY', 'مراقبة فقط'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات السياسة
    name_ar = models.CharField(max_length=200, verbose_name="اسم السياسة - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم السياسة - إنجليزي")
    code = models.CharField(max_length=50, unique=True, verbose_name="رمز السياسة")
    description = models.TextField(verbose_name="وصف السياسة")
    
    # تصنيف السياسة
    category = models.CharField(max_length=25, choices=POLICY_CATEGORIES,
                              verbose_name="فئة السياسة")
    enforcement_level = models.CharField(max_length=15, choices=ENFORCEMENT_LEVELS,
                                       default='MODERATE', verbose_name="مستوى التطبيق")
    
    # إعدادات السياسة
    policy_rules = models.JSONField(default=dict, verbose_name="قواعد السياسة")
    parameters = models.JSONField(default=dict, verbose_name="المعاملات")
    exceptions = models.JSONField(default=list, verbose_name="الاستثناءات")
    
    # التطبيق والنطاق
    applies_to_users = models.ManyToManyField(User, blank=True,
                                            related_name='security_policies',
                                            verbose_name="ينطبق على المستخدمين")
    applies_to_ip_ranges = models.JSONField(default=list, verbose_name="نطاقات IP المطبقة")
    applies_to_systems = models.JSONField(default=list, verbose_name="الأنظمة المطبقة")
    
    # التوقيت
    effective_from = models.DateTimeField(default=timezone.now, verbose_name="ساري من")
    effective_until = models.DateTimeField(null=True, blank=True, verbose_name="ساري حتى")
    
    # المراجعة والاعتماد
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_security_policies',
                                  verbose_name="مُعتمد من")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")
    review_frequency = models.CharField(max_length=20, default='QUARTERLY',
                                      choices=[
                                          ('MONTHLY', 'شهري'),
                                          ('QUARTERLY', 'ربع سنوي'),
                                          ('SEMI_ANNUAL', 'نصف سنوي'),
                                          ('ANNUAL', 'سنوي'),
                                      ], verbose_name="تكرار المراجعة")
    last_reviewed = models.DateTimeField(null=True, blank=True, verbose_name="آخر مراجعة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    is_mandatory = models.BooleanField(default=True, verbose_name="إلزامية")
    
    # إحصائيات التطبيق
    violations_count = models.IntegerField(default=0, verbose_name="عدد الانتهاكات")
    last_violation = models.DateTimeField(null=True, blank=True, verbose_name="آخر انتهاك")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_security_policies',
                                 verbose_name="أُنشأت بواسطة")
    
    class Meta:
        verbose_name = "سياسة أمان"
        verbose_name_plural = "سياسات الأمان"
        ordering = ['category', 'name_ar']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['enforcement_level']),
            models.Index(fields=['effective_from', 'effective_until']),
        ]
    
    def __str__(self):
        return self.name_ar
    
    @property
    def is_effective(self):
        """هل السياسة سارية حالياً"""
        now = timezone.now()
        if now < self.effective_from:
            return False
        if self.effective_until and now > self.effective_until:
            return False
        return self.is_active
    
    @property
    def needs_review(self):
        """هل تحتاج السياسة لمراجعة"""
        if not self.last_reviewed:
            return True
        
        frequency_days = {
            'MONTHLY': 30,
            'QUARTERLY': 90,
            'SEMI_ANNUAL': 180,
            'ANNUAL': 365,
        }
        
        days_since_review = (timezone.now() - self.last_reviewed).days
        return days_since_review >= frequency_days.get(self.review_frequency, 90)


class ThreatIntelligence(models.Model):
    """استخبارات التهديدات"""
    
    INTEL_TYPES = [
        ('IOC', 'مؤشر اختراق'),
        ('TTPs', 'تكتيكات وتقنيات وإجراءات'),
        ('CAMPAIGN', 'حملة'),
        ('ACTOR', 'فاعل تهديد'),
        ('MALWARE', 'برمجية خبيثة'),
        ('VULNERABILITY', 'ثغرة أمنية'),
        ('ATTACK_PATTERN', 'نمط هجوم'),
        ('TOOL', 'أداة'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CONFIRMED', 'مؤكد'),
    ]
    
    TLP_LEVELS = [
        ('WHITE', 'أبيض - عام'),
        ('GREEN', 'أخضر - مجتمع'),
        ('AMBER', 'عنبري - محدود'),
        ('RED', 'أحمر - مقيد'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الاستخبارات
    intel_id = models.CharField(max_length=50, unique=True, verbose_name="معرف الاستخبارات")
    intel_type = models.CharField(max_length=20, choices=INTEL_TYPES,
                                verbose_name="نوع الاستخبارات")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(verbose_name="الوصف")
    
    # مصدر الاستخبارات
    source = models.CharField(max_length=200, verbose_name="المصدر")
    source_reliability = models.CharField(max_length=15, choices=CONFIDENCE_LEVELS,
                                        default='MEDIUM', verbose_name="موثوقية المصدر")
    collection_date = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الجمع")
    
    # بيانات الاستخبارات
    indicators = models.JSONField(default=list, verbose_name="المؤشرات")
    attributes = models.JSONField(default=dict, verbose_name="الخصائص")
    relationships = models.JSONField(default=list, verbose_name="العلاقات")
    
    # التقييم
    confidence_level = models.CharField(max_length=15, choices=CONFIDENCE_LEVELS,
                                      default='MEDIUM', verbose_name="مستوى الثقة")
    relevance_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)],
                                        verbose_name="نقاط الصلة")
    threat_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)],
                                     verbose_name="نقاط التهديد")
    
    # التصنيف الأمني
    tlp_level = models.CharField(max_length=10, choices=TLP_LEVELS, default='GREEN',
                               verbose_name="مستوى TLP")
    classification = models.CharField(max_length=50, blank=True, verbose_name="التصنيف")
    
    # التوقيت والصلاحية
    valid_from = models.DateTimeField(default=timezone.now, verbose_name="صالح من")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="صالح حتى")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    # الاستخدام والتطبيق
    applied_to_systems = models.JSONField(default=list, verbose_name="مطبق على الأنظمة")
    detection_rules = models.JSONField(default=list, verbose_name="قواعد الكشف")
    mitigation_strategies = models.JSONField(default=list, verbose_name="استراتيجيات التخفيف")
    
    # التتبع والإحصائيات
    hits_count = models.IntegerField(default=0, verbose_name="عدد الإصابات")
    last_hit = models.DateTimeField(null=True, blank=True, verbose_name="آخر إصابة")
    false_positives = models.IntegerField(default=0, verbose_name="الإيجابيات الكاذبة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_threat_intel',
                                 verbose_name="أُنشأت بواسطة")
    
    class Meta:
        verbose_name = "استخبارات تهديد"
        verbose_name_plural = "استخبارات التهديدات"
        ordering = ['-threat_score', '-collection_date']
        indexes = [
            models.Index(fields=['intel_type', 'confidence_level']),
            models.Index(fields=['source']),
            models.Index(fields=['threat_score']),
            models.Index(fields=['valid_from', 'valid_until']),
            models.Index(fields=['tlp_level']),
        ]
    
    def __str__(self):
        return f"{self.intel_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.intel_id:
            self.intel_id = self.generate_intel_id()
        super().save(*args, **kwargs)
    
    def generate_intel_id(self):
        """توليد معرف استخبارات فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        intel_code = self.intel_type[:3].upper()
        return f"TI-{intel_code}-{timestamp}"
    
    @property
    def is_valid(self):
        """هل الاستخبارات سارية"""
        now = timezone.now()
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True
    
    @property
    def effectiveness_rate(self):
        """معدل الفعالية"""
        total_hits = self.hits_count + self.false_positives
        if total_hits > 0:
            return (self.hits_count / total_hits) * 100
        return 0


class SecurityDashboard(models.Model):
    """لوحة معلومات الأمان"""
    
    DASHBOARD_TYPES = [
        ('EXECUTIVE', 'تنفيذي'),
        ('ANALYST', 'محلل'),
        ('INCIDENT_RESPONSE', 'الاستجابة للحوادث'),
        ('COMPLIANCE', 'الامتثال'),
        ('THREAT_HUNTING', 'صيد التهديدات'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات اللوحة
    name = models.CharField(max_length=200, verbose_name="اسم اللوحة")
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_TYPES,
                                    verbose_name="نوع اللوحة")
    description = models.TextField(blank=True, verbose_name="وصف اللوحة")
    
    # المستخدم والصلاحيات
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                            related_name='security_dashboards', verbose_name="المالك")
    viewers = models.ManyToManyField(User, related_name='viewable_security_dashboards',
                                   blank=True, verbose_name="المشاهدون")
    
    # إعدادات اللوحة
    layout_config = models.JSONField(default=dict, verbose_name="إعدادات التخطيط")
    widgets = models.JSONField(default=list, verbose_name="الأدوات")
    filters = models.JSONField(default=dict, verbose_name="المرشحات")
    refresh_interval = models.IntegerField(default=300, verbose_name="فترة التحديث (ثانية)")
    
    # البيانات المعروضة
    metrics = models.JSONField(default=dict, verbose_name="المقاييس")
    charts_data = models.JSONField(default=dict, verbose_name="بيانات الرسوم البيانية")
    alerts_data = models.JSONField(default=list, verbose_name="بيانات التنبيهات")
    
    # إعدادات التنبيهات
    alert_thresholds = models.JSONField(default=dict, verbose_name="عتبات التنبيه")
    notification_settings = models.JSONField(default=dict, verbose_name="إعدادات الإشعارات")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    is_default = models.BooleanField(default=False, verbose_name="افتراضية")
    
    # معلومات التحديث
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    data_sources = models.JSONField(default=list, verbose_name="مصادر البيانات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "لوحة أمان"
        verbose_name_plural = "لوحات الأمان"
        ordering = ['dashboard_type', 'name']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['dashboard_type']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_dashboard_type_display()}"