# نظام الصلاحيات والأدوار المتطور
# Enhanced Role-Based Access Control System

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()

class Role(models.Model):
    """الأدوار المختلفة في النظام"""
    
    ROLE_TYPES = [
        ('SUPER_ADMIN', 'مدير النظام الرئيسي'),
        ('ADMIN', 'مدير النظام'),
        ('DEAN', 'عميد الكلية'),
        ('HEAD_OF_DEPARTMENT', 'رئيس القسم'),
        ('TEACHER', 'أستاذ'),
        ('ASSISTANT_TEACHER', 'مساعد تدريس'),
        ('STUDENT', 'طالب'),
        ('ACCOUNTANT', 'محاسب'),
        ('HR_MANAGER', 'مدير الموارد البشرية'),
        ('REGISTRAR', 'مسجل أكاديمي'),
        ('LIBRARIAN', 'أمين المكتبة'),
        ('IT_SUPPORT', 'دعم تقني'),
        ('SECURITY_OFFICER', 'ضابط أمن'),
        ('GUEST', 'زائر'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_TYPES, unique=True, 
                          verbose_name="اسم الدور")
    display_name = models.CharField(max_length=100, verbose_name="الاسم المعروض")
    display_name_en = models.CharField(max_length=100, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(blank=True, verbose_name="وصف الدور")
    
    # مستوى الصلاحية (كلما زاد الرقم زادت الصلاحية)
    permission_level = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="مستوى الصلاحية"
    )
    
    # إعدادات الدور
    can_create_users = models.BooleanField(default=False, verbose_name="يمكنه إنشاء مستخدمين")
    can_delete_users = models.BooleanField(default=False, verbose_name="يمكنه حذف مستخدمين")
    can_modify_grades = models.BooleanField(default=False, verbose_name="يمكنه تعديل الدرجات")
    can_access_financial = models.BooleanField(default=False, verbose_name="يمكنه الوصول للشؤون المالية")
    can_generate_reports = models.BooleanField(default=False, verbose_name="يمكنه إنشاء التقارير")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        ordering = ['-permission_level']
    
    def __str__(self):
        return self.display_name

class Permission(models.Model):
    """الصلاحيات المحددة في النظام"""
    
    PERMISSION_CATEGORIES = [
        ('ACADEMIC', 'أكاديمي'),
        ('FINANCIAL', 'مالي'),
        ('ADMINISTRATIVE', 'إداري'),
        ('TECHNICAL', 'تقني'),
        ('SECURITY', 'أمني'),
        ('REPORTING', 'التقارير'),
        ('USER_MANAGEMENT', 'إدارة المستخدمين'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الصلاحية")
    codename = models.CharField(max_length=100, unique=True, verbose_name="اسم مبرمج")
    description = models.TextField(verbose_name="وصف الصلاحية")
    category = models.CharField(max_length=20, choices=PERMISSION_CATEGORIES, 
                              verbose_name="فئة الصلاحية")
    
    # ربط مع نماذج Django
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                   null=True, blank=True)
    
    is_system_permission = models.BooleanField(default=False, 
                                             verbose_name="صلاحية نظام")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class RolePermission(models.Model):
    """ربط الأدوار بالصلاحيات"""
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    # صلاحيات إضافية
    can_read = models.BooleanField(default=True, verbose_name="قراءة")
    can_create = models.BooleanField(default=False, verbose_name="إنشاء")
    can_update = models.BooleanField(default=False, verbose_name="تحديث")
    can_delete = models.BooleanField(default=False, verbose_name="حذف")
    
    # قيود إضافية
    conditions = models.JSONField(default=dict, blank=True, 
                                verbose_name="شروط إضافية")
    
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "صلاحية الدور"
        verbose_name_plural = "صلاحيات الأدوار"
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role.display_name} - {self.permission.name}"

class UserRole(models.Model):
    """تعيين الأدوار للمستخدمين"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    # معلومات التعيين
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='roles_assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    # صلاحية مؤقتة
    is_temporary = models.BooleanField(default=False, verbose_name="مؤقت")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")
    
    # معلومات إضافية
    department_specific = models.BooleanField(default=False, 
                                            verbose_name="خاص بقسم معين")
    metadata = models.JSONField(default=dict, blank=True, 
                              verbose_name="معلومات إضافية")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    class Meta:
        verbose_name = "دور المستخدم"
        verbose_name_plural = "أدوار المستخدمين"
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.display_name}"
    
    @property
    def is_expired(self):
        """فحص انتهاء صلاحية الدور المؤقت"""
        if not self.is_temporary or not self.expires_at:
            return False
        return timezone.now() > self.expires_at

class PermissionLog(models.Model):
    """سجل تغييرات الصلاحيات"""
    
    ACTION_TYPES = [
        ('GRANTED', 'منح صلاحية'),
        ('REVOKED', 'سحب صلاحية'),
        ('MODIFIED', 'تعديل صلاحية'),
        ('ROLE_ASSIGNED', 'تعيين دور'),
        ('ROLE_REMOVED', 'إزالة دور'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name="الإجراء")
    
    # تفاصيل التغيير
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)
    
    # من قام بالتغيير
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='permission_changes_made')
    
    # تفاصيل إضافية
    description = models.TextField(blank=True, verbose_name="وصف التغيير")
    metadata = models.JSONField(default=dict, blank=True)
    
    # معلومات الجلسة
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "سجل الصلاحيات"
        verbose_name_plural = "سجلات الصلاحيات"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

class SessionPermission(models.Model):
    """صلاحيات الجلسة الحالية للمستخدم"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                               related_name='session_permissions')
    
    # ذاكرة تخزين الصلاحيات المحسوبة
    cached_permissions = models.JSONField(default=dict, 
                                        verbose_name="الصلاحيات المحفوظة")
    
    # معلومات الجلسة
    session_key = models.CharField(max_length=100, blank=True)
    last_calculated = models.DateTimeField(auto_now=True)
    
    # صلاحيات سريعة للفحص
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_access_financials = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "صلاحيات الجلسة"
        verbose_name_plural = "صلاحيات الجلسات"
    
    def refresh_permissions(self):
        """إعادة حساب وتحديث صلاحيات المستخدم"""
        permissions = {}
        
        # جمع جميع الأدوار النشطة للمستخدم
        active_roles = self.user.assigned_roles.filter(
            is_active=True,
            role__is_active=True
        ).exclude(
            is_temporary=True,
            expires_at__lt=timezone.now()
        )
        
        # حساب الصلاحيات من جميع الأدوار
        for user_role in active_roles:
            role_permissions = user_role.role.permissions.filter(
                permission__is_active=True
            )
            
            for role_perm in role_permissions:
                perm_key = role_perm.permission.codename
                if perm_key not in permissions:
                    permissions[perm_key] = {
                        'read': False,
                        'create': False,
                        'update': False,
                        'delete': False,
                    }
                
                # دمج الصلاحيات (أعلى صلاحية تفوز)
                permissions[perm_key]['read'] = (
                    permissions[perm_key]['read'] or role_perm.can_read
                )
                permissions[perm_key]['create'] = (
                    permissions[perm_key]['create'] or role_perm.can_create
                )
                permissions[perm_key]['update'] = (
                    permissions[perm_key]['update'] or role_perm.can_update
                )
                permissions[perm_key]['delete'] = (
                    permissions[perm_key]['delete'] or role_perm.can_delete
                )
        
        # تحديث الصلاحيات المحفوظة
        self.cached_permissions = permissions
        
        # تحديث الصلاحيات السريعة
        self.is_admin = any(
            role.role.name in ['SUPER_ADMIN', 'ADMIN'] 
            for role in active_roles
        )
        self.is_teacher = any(
            role.role.name in ['TEACHER', 'ASSISTANT_TEACHER'] 
            for role in active_roles
        )
        self.is_student = any(
            role.role.name == 'STUDENT' 
            for role in active_roles
        )
        self.can_manage_users = any(
            role.role.can_create_users 
            for role in active_roles
        )
        self.can_access_financials = any(
            role.role.can_access_financial 
            for role in active_roles
        )
        
        self.save()
    
    def has_permission(self, permission_codename, action='read'):
        """فحص وجود صلاحية معينة"""
        if permission_codename in self.cached_permissions:
            return self.cached_permissions[permission_codename].get(action, False)
        return False