"""
Admin interface for Roles and Permissions
واجهة إدارية للأدوار والصلاحيات
"""
from django.contrib import admin
from .models import Role, Permission, RolePermission, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'role_type', 'department', 'priority', 'is_active']
    list_filter = ['role_type', 'is_active', 'department']
    search_fields = ['name', 'display_name', 'description']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'permission_type', 'resource_name', 'is_active']
    list_filter = ['permission_type', 'is_active']
    search_fields = ['name', 'display_name', 'resource_name']