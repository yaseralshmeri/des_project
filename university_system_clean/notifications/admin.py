from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    Announcement, NotificationQueue, EmailLog
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'template_type']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Email Template', {
            'fields': ('subject_template', 'email_template'),
            'classes': ('wide',)
        }),
        ('SMS Template', {
            'fields': ('sms_template',),
            'description': 'Keep SMS messages under 160 characters for best delivery rates.'
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient_name', 'notification_type', 'delivery_method', 'status', 'scheduled_for', 'sent_at']
    list_filter = ['notification_type', 'delivery_method', 'status', 'scheduled_for', 'sent_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['sent_at', 'read_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Recipient & Content', {
            'fields': ('recipient', 'template', 'title', 'message')
        }),
        ('Settings', {
            'fields': ('notification_type', 'delivery_method', 'scheduled_for')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'read_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('related_object_type', 'related_object_id', 'context_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def recipient_name(self, obj):
        return obj.recipient.get_full_name() or obj.recipient.username
    recipient_name.short_description = 'Recipient'
    recipient_name.admin_order_field = 'recipient__first_name'
    
    actions = ['mark_as_sent', 'mark_as_read', 'resend_notification']
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='SENT', sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected notifications as sent'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='READ', read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled']
    list_filter = ['email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['user__username']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Preferences', {
            'fields': ('email_enabled', 'email_enrollment', 'email_grades', 'email_payments', 'email_reminders', 'email_announcements')
        }),
        ('SMS Preferences', {
            'fields': ('sms_enabled', 'sms_urgent_only', 'sms_payments', 'sms_reminders')
        }),
        ('In-App Preferences', {
            'fields': ('in_app_enabled', 'in_app_sound')
        }),
        ('Push Notification Preferences', {
            'fields': ('push_enabled', 'push_grades', 'push_reminders')
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'User'
    user_name.admin_order_field = 'user__first_name'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'audience', 'priority', 'is_published', 'publish_at', 'created_by', 'created_at']
    list_filter = ['audience', 'priority', 'is_published', 'publish_at', 'created_at']
    search_fields = ['title', 'content', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'publish_at'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content')
        }),
        ('Audience & Priority', {
            'fields': ('audience', 'priority', 'is_urgent')
        }),
        ('Targeting', {
            'fields': ('target_roles', 'target_users', 'target_department', 'target_program'),
            'classes': ('collapse',),
            'description': 'Configure specific targeting when audience is set to specific options.'
        }),
        ('Publishing', {
            'fields': ('is_published', 'publish_at', 'expire_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by', 'target_department', 'target_program')
    
    actions = ['publish_announcements', 'unpublish_announcements', 'mark_as_urgent']
    
    def publish_announcements(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} announcements published.')
    publish_announcements.short_description = 'Publish selected announcements'
    
    def unpublish_announcements(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} announcements unpublished.')
    unpublish_announcements.short_description = 'Unpublish selected announcements'
    
    def mark_as_urgent(self, request, queryset):
        updated = queryset.update(priority='URGENT', is_urgent=True)
        self.message_user(request, f'{updated} announcements marked as urgent.')
    mark_as_urgent.short_description = 'Mark selected announcements as urgent'


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = ['notification_title', 'recipient', 'priority', 'retry_count', 'max_retries', 'last_attempt', 'created_at']
    list_filter = ['priority', 'retry_count', 'last_attempt', 'created_at']
    search_fields = ['notification__title', 'notification__recipient__username']
    readonly_fields = ['created_at']
    ordering = ['-priority', 'created_at']
    
    def notification_title(self, obj):
        return obj.notification.title
    notification_title.short_description = 'Notification'
    notification_title.admin_order_field = 'notification__title'
    
    def recipient(self, obj):
        return obj.notification.recipient.get_full_name() or obj.notification.recipient.username
    recipient.short_description = 'Recipient'
    recipient.admin_order_field = 'notification__recipient__first_name'
    
    actions = ['retry_notifications', 'increase_priority']
    
    def retry_notifications(self, request, queryset):
        for item in queryset:
            item.retry_count = 0
            item.last_attempt = None
            item.error_message = ''
            item.save()
        self.message_user(request, f'{queryset.count()} notifications queued for retry.')
    retry_notifications.short_description = 'Reset and retry selected notifications'
    
    def increase_priority(self, request, queryset):
        for item in queryset:
            item.priority = min(item.priority + 1, 10)
            item.save()
        self.message_user(request, f'{queryset.count()} notifications priority increased.')
    increase_priority.short_description = 'Increase priority of selected notifications'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'subject', 'status', 'notification_title', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['recipient_email', 'subject', 'notification__title']
    readonly_fields = ['sent_at']
    ordering = ['-sent_at']
    date_hierarchy = 'sent_at'
    
    def notification_title(self, obj):
        return obj.notification.title if obj.notification else '-'
    notification_title.short_description = 'Related Notification'
    
    def has_add_permission(self, request):
        return False  # Email logs are created programmatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Email logs should not be modified
    
    actions = ['export_email_logs']
    
    def export_email_logs(self, request, queryset):
        # TODO: Implement CSV export functionality
        self.message_user(request, f'{queryset.count()} email logs selected for export.')
    export_email_logs.short_description = 'Export selected email logs'