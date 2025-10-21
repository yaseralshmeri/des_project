# واجهة إدارية لنظام الإشعارات
# Admin Interface for Notification System

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from .models import (
    InAppNotification, NotificationTemplate, NotificationLog,
    UserDeviceToken, UserTelegramAccount, NotificationPreference,
    ScheduledNotification
)

@admin.register(InAppNotification)
class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'is_read', 'created_at']
    list_filter = ['category', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__first_name_ar', 'user__last_name_ar']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('id', 'user', 'title', 'message')
        }),
        ('التصنيف والأولوية', {
            'fields': ('category', 'priority')
        }),
        ('الإجراءات', {
            'fields': ('action_url', 'action_text'),
            'classes': ('collapse',)
        }),
        ('الحالة', {
            'fields': ('is_read', 'read_at', 'is_active', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': ('metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['mark_as_read', 'mark_as_unread', 'deactivate_notifications']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'تم تمييز {updated} إشعار كمقروء.')
    mark_as_read.short_description = "تمييز كمقروء"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'تم تمييز {updated} إشعار كغير مقروء.')
    mark_as_unread.short_description = "تمييز كغير مقروء"
    
    def deactivate_notifications(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم إلغاء تفعيل {updated} إشعار.')
    deactivate_notifications.short_description = "إلغاء التفعيل"

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_id', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'template_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('template_id', 'name', 'description', 'category')
        }),
        ('محتوى القالب', {
            'fields': ('title_template', 'message_template', 'html_template'),
            'classes': ('wide',)
        }),
        ('الإعدادات', {
            'fields': ('required_variables', 'default_channels', 'is_active'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient_user_id', 'template_id', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'message', 'recipient_user_id', 'template_id']
    readonly_fields = ['id', 'created_at', 'sent_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الإشعار', {
            'fields': ('id', 'template_id', 'title', 'message')
        }),
        ('المستلم', {
            'fields': ('recipient_user_id', 'recipient_email', 'recipient_phone')
        }),
        ('الإعدادات', {
            'fields': ('priority', 'category', 'channels_used'),
            'classes': ('collapse',)
        }),
        ('نتائج التسليم', {
            'fields': ('status', 'delivery_results', 'sent_at'),
            'classes': ('collapse',)
        }),
        ('بيانات إضافية', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(UserDeviceToken)
class UserDeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_type', 'device_name', 'is_active', 'last_used']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__first_name_ar', 'user__last_name_ar', 'device_name', 'device_id']
    readonly_fields = ['created_at', 'updated_at', 'last_used']
    ordering = ['-last_used']
    
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user', 'device_type', 'token')
        }),
        ('معلومات الجهاز', {
            'fields': ('device_id', 'device_name', 'app_version'),
            'classes': ('collapse',)
        }),
        ('الحالة', {
            'fields': ('is_active', 'last_used', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['activate_tokens', 'deactivate_tokens']
    
    def activate_tokens(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} رمز جهاز.')
    activate_tokens.short_description = "تفعيل الرموز"
    
    def deactivate_tokens(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم إلغاء تفعيل {updated} رمز جهاز.')
    deactivate_tokens.short_description = "إلغاء تفعيل الرموز"

@admin.register(UserTelegramAccount)
class UserTelegramAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'chat_id', 'notifications_enabled', 'is_active', 'is_verified']
    list_filter = ['notifications_enabled', 'is_active', 'is_verified', 'preferred_language']
    search_fields = ['user__first_name_ar', 'user__last_name_ar', 'username', 'chat_id']
    readonly_fields = ['created_at', 'last_interaction']
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات الحساب', {
            'fields': ('user', 'chat_id', 'username')
        }),
        ('الإعدادات', {
            'fields': ('notifications_enabled', 'preferred_language')
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_verified', 'created_at', 'last_interaction'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'push_enabled', 'quiet_hours_enabled']
    list_filter = ['email_enabled', 'sms_enabled', 'push_enabled', 'urgent_only', 'quiet_hours_enabled']
    search_fields = ['user__first_name_ar', 'user__last_name_ar']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user']
    
    fieldsets = (
        ('المستخدم', {
            'fields': ('user',)
        }),
        ('تفضيلات القنوات', {
            'fields': ('email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled', 'telegram_enabled'),
            'classes': ('wide',)
        }),
        ('تفضيلات الفئات', {
            'fields': ('academic_notifications', 'financial_notifications', 'administrative_notifications',
                      'security_notifications', 'system_notifications'),
            'classes': ('wide',)
        }),
        ('إعدادات متقدمة', {
            'fields': ('urgent_only', 'quiet_hours_enabled', 'quiet_start_time', 'quiet_end_time'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ['template_id', 'scheduled_time', 'status', 'priority', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'scheduled_time', 'created_at']
    search_fields = ['template_id']
    readonly_fields = ['id', 'created_at', 'sent_at', 'delivery_results']
    ordering = ['scheduled_time']
    date_hierarchy = 'scheduled_time'
    
    fieldsets = (
        ('معلومات الإشعار', {
            'fields': ('id', 'template_id', 'priority')
        }),
        ('المستلمون والمحتوى', {
            'fields': ('recipients', 'variables', 'channels'),
            'classes': ('wide',)
        }),
        ('الجدولة', {
            'fields': ('scheduled_time', 'status')
        }),
        ('النتائج', {
            'fields': ('delivery_results', 'error_message', 'sent_at'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    actions = ['cancel_notifications', 'reschedule_notifications']
    
    def cancel_notifications(self, request, queryset):
        updated = queryset.filter(status='scheduled').update(status='cancelled')
        self.message_user(request, f'تم إلغاء {updated} إشعار مجدول.')
    cancel_notifications.short_description = "إلغاء الإشعارات المجدولة"
    
    def has_change_permission(self, request, obj=None):
        if obj and obj.status in ['sent', 'failed']:
            return False
        return True

# إعدادات إضافية للموقع الإداري
admin.site.site_header = "إدارة نظام الإشعارات"
admin.site.site_title = "نظام الإشعارات"
admin.site.index_title = "لوحة تحكم الإشعارات"