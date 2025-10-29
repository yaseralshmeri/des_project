# نظام الأدوار والصلاحيات المتقدم
# Advanced Role-Based Access Control (RBAC) System

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
    """الصلاحيات في النظام"""
    
    PERMISSION_CATEGORIES = [
        ('SYSTEM', 'نظام'),
        ('ACADEMIC', 'أكاديمي'),
        ('FINANCIAL', 'مالي'),
        ('HR', 'موارد بشرية'),
        ('REPORTING', 'تقارير'),
        ('SECURITY', 'أمان'),
        ('AI', 'ذكاء اصطناعي'),
    ]
    
    PERMISSION_LEVELS = [
        ('VIEW', 'عرض'),
        ('CREATE', 'إنشاء'),
        ('UPDATE', 'تعديل'),
        ('DELETE', 'حذف'),
        ('APPROVE', 'موافقة'),
        ('MANAGE', 'إدارة كاملة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الصلاحية الأساسية
    codename = models.CharField(max_length=100, unique=True, verbose_name="رمز الصلاحية")
    name_ar = models.CharField(max_length=255, verbose_name="اسم الصلاحية - عربي")
    name_en = models.CharField(max_length=255, verbose_name="اسم الصلاحية - إنجليزي")
    description = models.TextField(blank=True, verbose_name="وصف الصلاحية")
    
    # تصنيف الصلاحية
    category = models.CharField(max_length=20, choices=PERMISSION_CATEGORIES,
                              verbose_name="فئة الصلاحية")
    level = models.CharField(max_length=10, choices=PERMISSION_LEVELS,
                           verbose_name="مستوى الصلاحية")
    
    # النموذج المرتبط بالصلاحية
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                   null=True, blank=True, related_name='custom_permissions',
                                   verbose_name="نوع المحتوى")
    
    # الأولوية والتدرج
    priority = models.IntegerField(default=1, verbose_name="الأولوية")
    requires_supervisor_approval = models.BooleanField(default=False,
                                                     verbose_name="يتطلب موافقة المشرف")
    
    # قيود إضافية
    resource_constraints = models.JSONField(default=dict, verbose_name="قيود الموارد")
    time_constraints = models.JSONField(default=dict, verbose_name="قيود زمنية")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    is_system_permission = models.BooleanField(default=False, verbose_name="صلاحية نظام")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_permissions',
                                 verbose_name="أُنشأت بواسطة")
    
    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"
        ordering = ['category', 'priority', 'name_ar']
        indexes = [
            models.Index(fields=['category', 'level']),
            models.Index(fields=['codename']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} ({self.get_level_display()})"
    
    @property
    def display_name(self):
        return self.name_ar


class Role(models.Model):
    """الأدوار في النظام"""
    
    ROLE_TYPES = [
        ('SYSTEM', 'دور نظام'),
        ('ACADEMIC', 'دور أكاديمي'),
        ('ADMINISTRATIVE', 'دور إداري'),
        ('CUSTOM', 'دور مخصص'),
    ]
    
    ROLE_LEVELS = [
        ('SUPER', 'فائق'),  # Super Admin
        ('HIGH', 'عالي'),   # Dean, Department Head
        ('MEDIUM', 'متوسط'), # Teacher, Academic Staff
        ('LOW', 'منخفض'),   # Student, Basic Staff
        ('GUEST', 'زائر'),  # Guest Access
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الدور الأساسية
    name_ar = models.CharField(max_length=100, verbose_name="اسم الدور - عربي")
    name_en = models.CharField(max_length=100, verbose_name="اسم الدور - إنجليزي")
    code = models.CharField(max_length=30, unique=True, verbose_name="رمز الدور")
    description = models.TextField(blank=True, verbose_name="وصف الدور")
    
    # تصنيف الدور
    role_type = models.CharField(max_length=15, choices=ROLE_TYPES,
                               verbose_name="نوع الدور")
    role_level = models.CharField(max_length=10, choices=ROLE_LEVELS,
                                verbose_name="مستوى الدور")
    
    # الصلاحيات المرتبطة بالدور
    permissions = models.ManyToManyField(Permission, through='RolePermission',
                                       related_name='roles',
                                       verbose_name="الصلاحيات")
    
    # التدرج الهرمي
    parent_role = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='child_roles',
                                  verbose_name="الدور الأب")
    hierarchy_level = models.IntegerField(default=1, verbose_name="مستوى التدرج")
    
    # قيود الدور
    max_users = models.IntegerField(null=True, blank=True, verbose_name="الحد الأقصى للمستخدمين")
    session_timeout = models.IntegerField(default=3600, verbose_name="انتهاء الجلسة (ثانية)")
    
    # إعدادات أمنية
    requires_2fa = models.BooleanField(default=False, verbose_name="يتطلب مصادقة ثنائية")
    ip_restrictions = models.JSONField(default=list, verbose_name="قيود عناوين IP")
    time_restrictions = models.JSONField(default=dict, verbose_name="قيود زمنية")
    
    # الحالة والإعدادات
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_system_role = models.BooleanField(default=False, verbose_name="دور نظام")
    is_assignable = models.BooleanField(default=True, verbose_name="قابل للتعيين")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_roles',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        ordering = ['hierarchy_level', 'name_ar']
        indexes = [
            models.Index(fields=['role_type', 'role_level']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'is_assignable']),
        ]
    
    def __str__(self):
        return self.name_ar
    
    @property
    def display_name(self):
        return self.name_ar
    
    @property
    def current_users_count(self):
        """عدد المستخدمين الحاليين في هذا الدور"""
        return self.user_roles.filter(is_active=True).count()
    
    @property
    def can_assign_new_users(self):
        """هل يمكن تعيين مستخدمين جدد لهذا الدور"""
        if not self.is_assignable or not self.is_active:
            return False
        if self.max_users:
            return self.current_users_count < self.max_users
        return True
    
    def get_all_permissions(self):
        """الحصول على جميع الصلاحيات (بما في ذلك الموروثة)"""
        permissions = set()
        
        # إضافة صلاحيات الدور الحالي
        for role_perm in self.role_permissions.filter(is_active=True):
            permissions.add(role_perm.permission)
        
        # إضافة صلاحيات الأدوار الأب (الوراثة)
        current_role = self.parent_role
        while current_role:
            for role_perm in current_role.role_permissions.filter(is_active=True, is_inherited=True):
                permissions.add(role_perm.permission)
            current_role = current_role.parent_role
        
        return list(permissions)


class RolePermission(models.Model):
    """ربط الدور بالصلاحية مع تفاصيل إضافية"""
    
    GRANT_TYPES = [
        ('DIRECT', 'مباشر'),
        ('INHERITED', 'موروث'),
        ('TEMPORARY', 'مؤقت'),
        ('CONDITIONAL', 'مشروط'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                           related_name='role_permissions', verbose_name="الدور")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE,
                                 related_name='role_permissions', verbose_name="الصلاحية")
    
    # نوع المنح
    grant_type = models.CharField(max_length=15, choices=GRANT_TYPES, default='DIRECT',
                                verbose_name="نوع المنح")
    
    # قيود إضافية
    conditions = models.JSONField(default=dict, verbose_name="شروط الصلاحية")
    resource_limits = models.JSONField(default=dict, verbose_name="حدود الموارد")
    
    # التوقيت
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name="ساري من")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="ساري حتى")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_inherited = models.BooleanField(default=False, verbose_name="قابل للوراثة")
    requires_approval = models.BooleanField(default=False, verbose_name="يتطلب موافقة")
    
    # معلومات الموافقة
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_role_permissions',
                                  verbose_name="مُوافق عليه من")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الموافقة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_role_permissions',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "صلاحية الدور"
        verbose_name_plural = "صلاحيات الأدوار"
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission__category', 'permission__priority']
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
            models.Index(fields=['grant_type']),
        ]
    
    def __str__(self):
        return f"{self.role.name_ar} - {self.permission.name_ar}"
    
    @property
    def is_valid(self):
        """هل الصلاحية سارية حالياً"""
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return self.is_active
    
    def clean(self):
        if self.valid_from and self.valid_until and self.valid_from >= self.valid_until:
            raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")


class UserRole(models.Model):
    """تعيين الأدوار للمستخدمين"""
    
    ASSIGNMENT_TYPES = [
        ('PERMANENT', 'دائم'),
        ('TEMPORARY', 'مؤقت'),
        ('ACTING', 'بالوكالة'),
        ('SUBSTITUTE', 'بديل'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'في الانتظار'),
        ('ACTIVE', 'نشط'),
        ('SUSPENDED', 'موقوف'),
        ('EXPIRED', 'منتهي'),
        ('REVOKED', 'مُلغى'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='user_roles', verbose_name="المستخدم")
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                           related_name='user_roles', verbose_name="الدور")
    
    # نوع التعيين
    assignment_type = models.CharField(max_length=15, choices=ASSIGNMENT_TYPES,
                                     default='PERMANENT', verbose_name="نوع التعيين")
    
    # التوقيت
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التعيين")
    valid_from = models.DateTimeField(default=timezone.now, verbose_name="ساري من")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="ساري حتى")
    
    # الحالة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="الحالة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_primary = models.BooleanField(default=False, verbose_name="دور أساسي")
    
    # معلومات التعيين
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='assigned_user_roles',
                                  verbose_name="عُين بواسطة")
    assignment_reason = models.TextField(blank=True, verbose_name="سبب التعيين")
    
    # قيود إضافية
    resource_quotas = models.JSONField(default=dict, verbose_name="حصص الموارد")
    additional_permissions = models.ManyToManyField(Permission, blank=True,
                                                  related_name='user_role_permissions',
                                                  verbose_name="صلاحيات إضافية")
    
    # معلومات الإلغاء/الإيقاف
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإلغاء")
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='revoked_user_roles',
                                 verbose_name="أُلغى بواسطة")
    revocation_reason = models.TextField(blank=True, verbose_name="سبب الإلغاء")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "دور المستخدم"
        verbose_name_plural = "أدوار المستخدمين"
        ordering = ['-is_primary', 'user', 'role']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['status']),
            models.Index(fields=['assignment_type']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.role.name_ar}"
    
    @property
    def is_valid(self):
        """هل التعيين ساري حالياً"""
        now = timezone.now()
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return self.is_active and self.status == 'ACTIVE'
    
    @property
    def is_temporary(self):
        """هل التعيين مؤقت"""
        return self.assignment_type == 'TEMPORARY' or self.valid_until is not None
    
    def clean(self):
        if self.valid_until and self.valid_from >= self.valid_until:
            raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
    
    def save(self, *args, **kwargs):
        # التأكد من وجود دور أساسي واحد فقط للمستخدم
        if self.is_primary:
            UserRole.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        
        # تحديث الحالة بناءً على التوقيت
        now = timezone.now()
        if self.valid_until and now > self.valid_until:
            self.status = 'EXPIRED'
            self.is_active = False
        elif now < self.valid_from:
            self.status = 'PENDING'
        
        super().save(*args, **kwargs)
    
    def revoke(self, revoked_by, reason=""):
        """إلغاء التعيين"""
        self.status = 'REVOKED'
        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        self.revocation_reason = reason
        self.save()
    
    def suspend(self):
        """إيقاف التعيين مؤقتاً"""
        self.status = 'SUSPENDED'
        self.save()
    
    def reactivate(self):
        """إعادة تنشيط التعيين"""
        if self.status == 'SUSPENDED':
            self.status = 'ACTIVE'
            self.save()


class AccessLog(models.Model):
    """سجل الوصول والصلاحيات"""
    
    ACTION_TYPES = [
        ('LOGIN', 'تسجيل دخول'),
        ('LOGOUT', 'تسجيل خروج'),
        ('ACCESS_GRANTED', 'وصول مُسمح'),
        ('ACCESS_DENIED', 'وصول مُرفض'),
        ('PERMISSION_USED', 'استخدام صلاحية'),
        ('ROLE_CHANGED', 'تغيير دور'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المستخدم والجلسة
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='access_logs', verbose_name="المستخدم")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    
    # نوع الإجراء
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES,
                                 verbose_name="نوع الإجراء")
    action_description = models.CharField(max_length=255, verbose_name="وصف الإجراء")
    
    # الصلاحية أو الدور المستخدم
    permission_used = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='access_logs', verbose_name="الصلاحية المستخدمة")
    role_used = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='access_logs', verbose_name="الدور المستخدم")
    
    # معلومات تقنية
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    request_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الطلب")
    request_method = models.CharField(max_length=10, blank=True, verbose_name="طريقة الطلب")
    
    # النتيجة والمخاطر
    was_successful = models.BooleanField(verbose_name="نجح الإجراء")
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='LOW',
                                verbose_name="مستوى المخاطر")
    failure_reason = models.CharField(max_length=500, blank=True, verbose_name="سبب الفشل")
    
    # المعلومات الإضافية
    additional_data = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # التوقيت
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    class Meta:
        verbose_name = "سجل الوصول"
        verbose_name_plural = "سجلات الوصول"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type']),
            models.Index(fields=['was_successful']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.get_action_type_display()} - {self.timestamp}"


class SecurityPolicy(models.Model):
    """سياسات الأمان والصلاحيات"""
    
    POLICY_TYPES = [
        ('AUTHENTICATION', 'مصادقة'),
        ('AUTHORIZATION', 'تفويض'),
        ('PASSWORD', 'كلمة مرور'),
        ('SESSION', 'جلسة'),
        ('ACCESS_CONTROL', 'التحكم في الوصول'),
        ('DATA_PROTECTION', 'حماية البيانات'),
    ]
    
    ENFORCEMENT_LEVELS = [
        ('STRICT', 'صارم'),
        ('MODERATE', 'متوسط'),
        ('LENIENT', 'متساهل'),
        ('DISABLED', 'معطل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات السياسة
    name_ar = models.CharField(max_length=200, verbose_name="اسم السياسة - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم السياسة - إنجليزي")
    code = models.CharField(max_length=50, unique=True, verbose_name="رمز السياسة")
    description = models.TextField(verbose_name="وصف السياسة")
    
    # نوع السياسة
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES,
                                 verbose_name="نوع السياسة")
    enforcement_level = models.CharField(max_length=15, choices=ENFORCEMENT_LEVELS,
                                       default='MODERATE', verbose_name="مستوى التطبيق")
    
    # إعدادات السياسة
    policy_settings = models.JSONField(default=dict, verbose_name="إعدادات السياسة")
    
    # الأدوار المطبقة عليها
    applies_to_roles = models.ManyToManyField(Role, blank=True,
                                            related_name='security_policies',
                                            verbose_name="الأدوار المطبقة عليها")
    
    # التوقيت
    effective_from = models.DateTimeField(default=timezone.now, verbose_name="سارية من")
    effective_until = models.DateTimeField(null=True, blank=True, verbose_name="سارية حتى")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    is_system_policy = models.BooleanField(default=False, verbose_name="سياسة نظام")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_security_policies',
                                 verbose_name="أُنشأت بواسطة")
    
    class Meta:
        verbose_name = "سياسة أمان"
        verbose_name_plural = "سياسات الأمان"
        ordering = ['policy_type', 'name_ar']
        indexes = [
            models.Index(fields=['policy_type', 'is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['enforcement_level']),
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


class OrganizationalUnit(models.Model):
    """الوحدات التنظيمية لتطبيق الصلاحيات"""
    
    UNIT_TYPES = [
        ('UNIVERSITY', 'جامعة'),
        ('COLLEGE', 'كلية'),
        ('DEPARTMENT', 'قسم'),
        ('CENTER', 'مركز'),
        ('INSTITUTE', 'معهد'),
        ('OFFICE', 'مكتب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name_ar = models.CharField(max_length=200, verbose_name="اسم الوحدة - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم الوحدة - إنجليزي")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز الوحدة")
    
    unit_type = models.CharField(max_length=15, choices=UNIT_TYPES,
                               verbose_name="نوع الوحدة")
    
    # التدرج الهرمي
    parent_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='child_units', verbose_name="الوحدة الأب")
    hierarchy_level = models.IntegerField(default=1, verbose_name="مستوى التدرج")
    
    # المسؤولون
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='headed_units', verbose_name="رئيس الوحدة")
    members = models.ManyToManyField(User, through='UnitMembership',
                                   related_name='organizational_units',
                                   verbose_name="الأعضاء")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "وحدة تنظيمية"
        verbose_name_plural = "الوحدات التنظيمية"
        ordering = ['hierarchy_level', 'name_ar']
        indexes = [
            models.Index(fields=['unit_type', 'is_active']),
            models.Index(fields=['parent_unit']),
        ]
    
    def __str__(self):
        return self.name_ar


class UnitMembership(models.Model):
    """عضوية الوحدة التنظيمية"""
    
    MEMBERSHIP_TYPES = [
        ('MEMBER', 'عضو'),
        ('COORDINATOR', 'منسق'),
        ('DEPUTY', 'نائب'),
        ('SECRETARY', 'سكرتير'),
    ]
    
    unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE,
                           related_name='memberships', verbose_name="الوحدة")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='unit_memberships', verbose_name="المستخدم")
    
    membership_type = models.CharField(max_length=15, choices=MEMBERSHIP_TYPES,
                                     default='MEMBER', verbose_name="نوع العضوية")
    
    # التوقيت
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الانضمام")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="ساري حتى")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    class Meta:
        verbose_name = "عضوية وحدة"
        verbose_name_plural = "عضويات الوحدات"
        unique_together = ['unit', 'user']
        ordering = ['unit', 'membership_type', 'user']
    
    def __str__(self):
        return f"{self.user.display_name} - {self.unit.name_ar}"