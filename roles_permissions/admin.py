# إدارة نظام الأدوار والصلاحيات
# Role-Based Access Control Administration

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Permission, Role, RolePermission, UserRole, 
    AccessLog, SecurityPolicy, OrganizationalUnit, UnitMembership
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """إدارة الصلاحيات"""
    list_display = [
        'name_ar', 
        'category', 
        'level', 
        'priority',
        'is_active',
        'is_system_permission',
        'created_at'
    ]
    list_filter = [
        'category', 
        'level', 
        'is_active', 
        'is_system_permission',
        'priority'
    ]
    search_fields = ['name_ar', 'name_en', 'codename', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['category', 'priority', 'name_ar']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('codename', 'name_ar', 'name_en', 'description')
        }),
        ('التصنيف', {
            'fields': ('category', 'level', 'priority')
        }),
        ('الإعدادات', {
            'fields': ('content_type', 'requires_supervisor_approval')
        }),
        ('القيود', {
            'fields': ('resource_constraints', 'time_constraints')
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_system_permission')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """إدارة الأدوار"""
    list_display = [
        'name_ar',
        'code',
        'role_type',
        'role_level',
        'hierarchy_level',
        'current_users_count',
        'is_active',
        'is_assignable'
    ]
    list_filter = [
        'role_type',
        'role_level', 
        'is_active',
        'is_assignable',
        'is_system_role'
    ]
    search_fields = ['name_ar', 'name_en', 'code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'current_users_count']
    ordering = ['hierarchy_level', 'name_ar']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name_ar', 'name_en', 'code', 'description')
        }),
        ('التصنيف', {
            'fields': ('role_type', 'role_level', 'hierarchy_level')
        }),
        ('التدرج الهرمي', {
            'fields': ('parent_role',)
        }),
        ('القيود', {
            'fields': ('max_users', 'session_timeout')
        }),
        ('الأمان', {
            'fields': ('requires_2fa', 'ip_restrictions', 'time_restrictions')
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_system_role', 'is_assignable')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


class RolePermissionInline(admin.TabularInline):
    """صلاحيات الدور"""
    model = RolePermission
    extra = 0
    readonly_fields = ['created_at', 'is_valid']
    fields = ['permission', 'grant_type', 'is_active', 'is_inherited', 'valid_from', 'valid_until']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """إدارة أدوار المستخدمين"""
    list_display = [
        'user_display',
        'role',
        'assignment_type',
        'status',
        'is_primary',
        'is_valid',
        'assigned_at'
    ]
    list_filter = [
        'assignment_type',
        'status',
        'is_primary',
        'is_active'
    ]
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'role__name_ar'
    ]
    readonly_fields = ['id', 'assigned_at', 'created_at', 'updated_at', 'is_valid']
    
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'المستخدم'
    
    fieldsets = (
        ('تعيين الدور', {
            'fields': ('user', 'role', 'assignment_type', 'is_primary')
        }),
        ('التوقيت', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('الحالة', {
            'fields': ('status', 'is_active')
        }),
        ('معلومات التعيين', {
            'fields': ('assigned_by', 'assignment_reason')
        }),
        ('القيود', {
            'fields': ('resource_quotas',)
        }),
        ('معلومات الإلغاء', {
            'fields': ('revoked_at', 'revoked_by', 'revocation_reason'),
            'classes': ('collapse',)
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'assigned_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """إدارة سجلات الوصول"""
    list_display = [
        'user',
        'action_type',
        'was_successful',
        'risk_level',
        'ip_address',
        'timestamp'
    ]
    list_filter = [
        'action_type',
        'was_successful',
        'risk_level',
        'timestamp'
    ]
    search_fields = [
        'user__username',
        'action_description',
        'ip_address',
        'failure_reason'
    ]
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('معلومات الإجراء', {
            'fields': ('user', 'action_type', 'action_description')
        }),
        ('الصلاحية/الدور', {
            'fields': ('permission_used', 'role_used')
        }),
        ('معلومات تقنية', {
            'fields': ('ip_address', 'user_agent', 'request_path', 'request_method')
        }),
        ('النتيجة', {
            'fields': ('was_successful', 'risk_level', 'failure_reason')
        }),
        ('بيانات إضافية', {
            'fields': ('session_id', 'additional_data'),
            'classes': ('collapse',)
        }),
        ('الوقت', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    """إدارة سياسات الأمان"""
    list_display = [
        'name_ar',
        'policy_type',
        'enforcement_level',
        'is_active',
        'is_effective',
        'created_at'
    ]
    list_filter = [
        'policy_type',
        'enforcement_level',
        'is_active',
        'is_system_policy'
    ]
    search_fields = ['name_ar', 'name_en', 'code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_effective']
    
    def is_effective(self, obj):
        """هل السياسة سارية"""
        if obj.is_effective:
            return format_html('<span style="color: green;">✓ سارية</span>')
        return format_html('<span style="color: red;">✗ غير سارية</span>')
    is_effective.short_description = 'الحالة'
    
    fieldsets = (
        ('معلومات السياسة', {
            'fields': ('name_ar', 'name_en', 'code', 'description')
        }),
        ('نوع السياسة', {
            'fields': ('policy_type', 'enforcement_level')
        }),
        ('الإعدادات', {
            'fields': ('policy_settings',)
        }),
        ('التطبيق', {
            'fields': ('applies_to_roles',)
        }),
        ('التوقيت', {
            'fields': ('effective_from', 'effective_until')
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_system_policy')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(admin.ModelAdmin):
    """إدارة الوحدات التنظيمية"""
    list_display = [
        'name_ar',
        'unit_type',
        'code',
        'head',
        'hierarchy_level',
        'is_active'
    ]
    list_filter = [
        'unit_type',
        'hierarchy_level',
        'is_active'
    ]
    search_fields = ['name_ar', 'name_en', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات الوحدة', {
            'fields': ('name_ar', 'name_en', 'code', 'unit_type')
        }),
        ('التدرج الهرمي', {
            'fields': ('parent_unit', 'hierarchy_level')
        }),
        ('المسؤولون', {
            'fields': ('head',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class UnitMembershipInline(admin.TabularInline):
    """عضوية الوحدة"""
    model = UnitMembership
    extra = 0
    fields = ['user', 'membership_type', 'is_active', 'joined_at', 'valid_until']
    readonly_fields = ['joined_at']


# إضافة الصلاحيات كـ inline للأدوار
RoleAdmin.inlines = [RolePermissionInline]

# إضافة العضويات كـ inline للوحدات التنظيمية
OrganizationalUnitAdmin.inlines = [UnitMembershipInline]