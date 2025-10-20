"""
Advanced Admin Interface for Control Panel
واجهة إدارية متقدمة للوحة التحكم
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    SystemConfiguration, UserActivity, SystemAlert, 
    AdminDashboardWidget, MaintenanceMode, BackupLog, 
    SystemMetrics, AdminAction
)


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'category', 'is_active', 'updated_at', 'updated_by']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['key', 'description', 'value']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SystemAlert) 
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'alert_type', 'is_active', 'created_at']
    list_filter = ['severity', 'alert_type', 'is_active']
    search_fields = ['title', 'message']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)