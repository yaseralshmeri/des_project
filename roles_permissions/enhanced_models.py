# نظام الصلاحيات والأدوار المتطور والذكي
# Enhanced Intelligent Role-Based Access Control System

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import json

User = get_user_model()

class Permission(models.Model):
    """صلاحيات النظام المتطورة"""
    
    CATEGORY_CHOICES = [
        ('ACADEMIC', 'أكاديمي'),
        ('FINANCIAL', 'مالي'),
        ('ADMINISTRATIVE', 'إداري'),
        ('SYSTEM', 'النظام'),
        ('REPORTING', 'التقارير'),
        ('SECURITY', 'الأمان'),
        ('HR', 'الموارد البشرية'),
        ('STUDENT_SERVICES', 'خدمات الطلاب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الصلاحية")
    codename = models.CharField(max_length=100, unique=True, verbose_name="الرمز")
    description = models.TextField(verbose_name="الوصف")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="الفئة")
    
    # مستوى الخطورة
    risk_level = models.CharField(max_length=10, 
                                choices=[
                                    ('LOW', 'منخفض'),
                                    ('MEDIUM', 'متوسط'),
                                    ('HIGH', 'عالي'),
                                    ('CRITICAL', 'حرج')
                                ], default='LOW', verbose_name="مستوى المخاطر")
    
    # إعدادات إضافية
    requires_approval = models.BooleanField(default=False, verbose_name="يتطلب موافقة")
    auto_expire = models.BooleanField(default=False, verbose_name="انتهاء تلقائي")
    expire_days = models.IntegerField(null=True, blank=True, verbose_name="أيام الانتهاء")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_permissions', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'risk_level']),
            models.Index(fields=['codename']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Role(models.Model):
    """الأدوار الوظيفية المتطورة"""
    
    LEVEL_CHOICES = [
        ('SYSTEM', 'نظام'),
        ('UNIVERSITY', 'جامعة'),
        ('COLLEGE', 'كلية'),
        ('DEPARTMENT', 'قسم'),
        ('COURSE', 'مقرر'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الدور")
    name_en = models.CharField(max_length=100, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(verbose_name="الوصف")
    
    # مستوى الدور
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, verbose_name="المستوى")
    hierarchy_level = models.IntegerField(default=1, verbose_name="مستوى التسلسل الهرمي")
    
    # الصلاحيات
    permissions = models.ManyToManyField(Permission, through='RolePermission',
                                       verbose_name="الصلاحيات")
    
    # الإعدادات
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")
    is_system_role = models.BooleanField(default=False, verbose_name="دور نظام")
    max_users = models.IntegerField(null=True, blank=True, verbose_name="الحد الأقصى للمستخدمين")
    
    # قيود إضافية
    restrictions = models.JSONField(default=dict, verbose_name="القيود")
    settings = models.JSONField(default=dict, verbose_name="الإعدادات")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_roles', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "دور وظيفي"
        verbose_name_plural = "الأدوار الوظيفية"
        ordering = ['hierarchy_level', 'name']
        indexes = [
            models.Index(fields=['level', 'hierarchy_level']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"
    
    @property
    def user_count(self):
        """عدد المستخدمين في هذا الدور"""
        return self.user_roles.filter(is_active=True).count()
    
    @property
    def is_full(self):
        """هل الدور ممتلئ"""
        if self.max_users:
            return self.user_count >= self.max_users
        return False


class RolePermission(models.Model):
    """ربط الأدوار بالصلاحيات مع إعدادات متقدمة"""
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="الدور")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="الصلاحية")
    
    # إعدادات متقدمة
    can_delegate = models.BooleanField(default=False, verbose_name="يمكن التفويض")
    is_temporary = models.BooleanField(default=False, verbose_name="مؤقت")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")
    
    # قيود إضافية
    conditions = models.JSONField(default=dict, verbose_name="الشروط")
    restrictions = models.JSONField(default=dict, verbose_name="القيود")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 verbose_name="مُنح بواسطة")
    
    class Meta:
        verbose_name = "صلاحية الدور"
        verbose_name_plural = "صلاحيات الأدوار"
        unique_together = ['role', 'permission']
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def clean(self):
        if self.is_temporary and not self.expires_at:
            raise ValidationError("الصلاحيات المؤقتة تتطلب تاريخ انتهاء")
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"
    
    @property
    def is_expired(self):
        """هل انتهت صلاحية الإذن"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UserRole(models.Model):
    """تعيين الأدوار للمستخدمين مع إدارة متقدمة"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('SUSPENDED', 'موقوف'),
        ('EXPIRED', 'منتهي'),
        ('REVOKED', 'مُلغى'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles',
                           verbose_name="المستخدم")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles',
                           verbose_name="الدور")
    
    # الحالة والتواريخ
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="الحالة")
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المنح")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="آخر استخدام")
    
    # النطاق والسياق
    scope_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    scope_id = models.PositiveIntegerField(null=True, blank=True)
    scope_object = GenericForeignKey('scope_type', 'scope_id')
    
    # إعدادات إضافية
    is_primary = models.BooleanField(default=False, verbose_name="دور أساسي")
    can_modify_permissions = models.BooleanField(default=False, verbose_name="يمكن تعديل الصلاحيات")
    
    # الإدارة والموافقات
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='granted_roles', verbose_name="مُنح بواسطة")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_roles', verbose_name="وافق عليه")
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الموافقة")
    
    # ملاحظات وأسباب
    reason = models.TextField(blank=True, verbose_name="سبب المنح")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    class Meta:
        verbose_name = "دور المستخدم"
        verbose_name_plural = "أدوار المستخدمين"
        unique_together = ['user', 'role', 'scope_type', 'scope_id']
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'status', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def clean(self):
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("تاريخ الانتهاء يجب أن يكون في المستقبل")
        if self.role.is_full and not self.pk:
            raise ValidationError("هذا الدور وصل للحد الأقصى من المستخدمين")
    
    def __str__(self):
        scope_str = f" - {self.scope_object}" if self.scope_object else ""
        return f"{self.user.display_name} - {self.role.name}{scope_str}"
    
    @property
    def is_expired(self):
        """هل انتهت صلاحية الدور"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def extend_expiry(self, days=30):
        """تمديد صلاحية الدور"""
        if self.expires_at:
            self.expires_at = self.expires_at + timezone.timedelta(days=days)
        else:
            self.expires_at = timezone.now() + timezone.timedelta(days=days)
        self.save()
    
    def revoke(self, reason="", revoked_by=None):
        """إلغاء الدور"""
        self.status = 'REVOKED'
        self.is_active = False
        if reason:
            self.notes = f"ألغي: {reason}\n{self.notes}"
        self.save()


class PermissionRequest(models.Model):
    """طلبات الصلاحيات"""
    
    STATUS_CHOICES = [
        ('PENDING', 'قيد المراجعة'),
        ('APPROVED', 'موافق'),
        ('REJECTED', 'مرفوض'),
        ('EXPIRED', 'منتهي'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'منخفض'),
        ('NORMAL', 'عادي'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # طالب الصلاحية
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, 
                                   related_name='permission_requests',
                                   verbose_name="طالب الصلاحية")
    requested_for = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='requested_permissions',
                                    verbose_name="المطلوب له الصلاحية")
    
    # تفاصيل الطلب
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="الدور المطلوب")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="صلاحيات إضافية")
    
    # النطاق
    scope_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    scope_id = models.PositiveIntegerField(null=True, blank=True)
    scope_object = GenericForeignKey('scope_type', 'scope_id')
    
    # تفاصيل الطلب
    reason = models.TextField(verbose_name="سبب الطلب")
    justification = models.TextField(blank=True, verbose_name="التبرير")
    duration_days = models.IntegerField(null=True, blank=True, verbose_name="المدة بالأيام")
    
    # الحالة والأولوية
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="الحالة")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL',
                              verbose_name="الأولوية")
    
    # المراجعة والموافقة
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='reviewed_requests', verbose_name="راجعه")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    review_notes = models.TextField(blank=True, verbose_name="ملاحظات المراجعة")
    
    # التواريخ
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")
    
    class Meta:
        verbose_name = "طلب صلاحية"
        verbose_name_plural = "طلبات الصلاحيات"
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['reviewed_by', 'status']),
        ]
    
    def __str__(self):
        return f"طلب {self.role.name} لـ {self.requested_for.display_name}"
    
    def approve(self, approved_by, notes=""):
        """الموافقة على الطلب"""
        self.status = 'APPROVED'
        self.reviewed_by = approved_by
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
        
        # إنشاء UserRole
        expires_at = None
        if self.duration_days:
            expires_at = timezone.now() + timezone.timedelta(days=self.duration_days)
        
        user_role = UserRole.objects.create(
            user=self.requested_for,
            role=self.role,
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            expires_at=expires_at,
            granted_by=self.requested_by,
            approved_by=approved_by,
            approval_date=timezone.now(),
            reason=self.reason
        )
        
        return user_role
    
    def reject(self, rejected_by, notes=""):
        """رفض الطلب"""
        self.status = 'REJECTED'
        self.reviewed_by = rejected_by
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()


class AccessLog(models.Model):
    """سجل الوصول والصلاحيات المستخدمة"""
    
    ACTION_CHOICES = [
        ('LOGIN', 'تسجيل دخول'),
        ('LOGOUT', 'تسجيل خروج'),
        ('ACCESS', 'وصول'),
        ('CREATE', 'إنشاء'),
        ('READ', 'قراءة'),
        ('UPDATE', 'تحديث'),
        ('DELETE', 'حذف'),
        ('EXPORT', 'تصدير'),
        ('IMPORT', 'استيراد'),
        ('APPROVE', 'موافقة'),
        ('REJECT', 'رفض'),
    ]
    
    RESULT_CHOICES = [
        ('SUCCESS', 'نجح'),
        ('FAILED', 'فشل'),
        ('DENIED', 'مرفوض'),
        ('ERROR', 'خطأ'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستخدم والسياق
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs',
                           verbose_name="المستخدم")
    role_used = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="الدور المستخدم")
    permission_used = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="الصلاحية المستخدمة")
    
    # تفاصيل الإجراء
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="الإجراء")
    resource = models.CharField(max_length=200, verbose_name="المورد")
    description = models.TextField(verbose_name="الوصف")
    
    # الكائن المستهدف
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey('target_type', 'target_id')
    
    # النتيجة
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, verbose_name="النتيجة")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    
    # معلومات تقنية
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    
    # البيانات الإضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # التوقيت
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    class Meta:
        verbose_name = "سجل الوصول"
        verbose_name_plural = "سجلات الوصول"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', 'result', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.get_action_display()} - {self.timestamp}"


class SecurityAlert(models.Model):
    """تنبيهات الأمان"""
    
    SEVERITY_CHOICES = [
        ('INFO', 'معلومات'),
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'جديد'),
        ('INVESTIGATING', 'قيد التحقيق'),
        ('RESOLVED', 'مُحل'),
        ('FALSE_POSITIVE', 'إيجابي كاذب'),
        ('IGNORED', 'مُتجاهل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # التفاصيل الأساسية
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(verbose_name="الوصف")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, verbose_name="الخطورة")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='NEW',
                            verbose_name="الحالة")
    
    # المستخدم المتأثر
    affected_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='security_alerts',
                                    verbose_name="المستخدم المتأثر")
    
    # تفاصيل التهديد
    threat_type = models.CharField(max_length=100, verbose_name="نوع التهديد")
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP المصدر")
    
    # الإجراءات المتخذة
    actions_taken = models.TextField(blank=True, verbose_name="الإجراءات المتخذة")
    
    # المراجعة
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='investigated_alerts',
                                      verbose_name="حُقق بواسطة")
    investigation_notes = models.TextField(blank=True, verbose_name="ملاحظات التحقيق")
    
    # البيانات الإضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # التواريخ
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الاكتشاف")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    class Meta:
        verbose_name = "تنبيه أمني"
        verbose_name_plural = "التنبيهات الأمنية"
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['severity', 'status', '-detected_at']),
            models.Index(fields=['affected_user', '-detected_at']),
            models.Index(fields=['threat_type', '-detected_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
    
    def resolve(self, resolved_by, notes=""):
        """حل التنبيه"""
        self.status = 'RESOLVED'
        self.investigated_by = resolved_by
        self.investigation_notes = notes
        self.resolved_at = timezone.now()
        self.save()
    
    def mark_false_positive(self, investigated_by, notes=""):
        """تمييز كإيجابي كاذب"""
        self.status = 'FALSE_POSITIVE'
        self.investigated_by = investigated_by
        self.investigation_notes = notes
        self.resolved_at = timezone.now()
        self.save()