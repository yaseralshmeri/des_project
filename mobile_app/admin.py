# تطبيق الهاتف المحمول - لوحة التحكم الإدارية
# Mobile App - Admin Interface

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    MobileDevice, MobileAppSession, MobilePushNotification,
    MobileAppFeedback, MobileAppAnalytics
)


@admin.register(MobileDevice)
class MobileDeviceAdmin(admin.ModelAdmin):
    """إدارة الأجهزة المحمولة"""
    
    list_display = [
        'user', 'device_name', 'device_type', 'status',
        'is_trusted', 'last_seen', 'app_version'
    ]
    list_filter = [
        'device_type', 'status', 'is_trusted', 
        'notifications_enabled', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'device_name',
        'device_id', 'device_model'
    ]
    readonly_fields = [
        'id', 'device_id', 'last_login', 'last_seen',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('معلومات الجهاز', {
            'fields': (
                'device_id', 'device_name', 'device_type', 
                'device_model', 'operating_system', 'os_version'
            )
        }),
        ('إعدادات التطبيق', {
            'fields': (
                'app_version', 'fcm_token', 'status', 
                'is_trusted', 'notifications_enabled'
            )
        }),
        ('معلومات الأمان', {
            'fields': ('last_login', 'last_seen', 'ip_address')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_trusted', 'mark_as_untrusted', 'block_devices']
    
    def mark_as_trusted(self, request, queryset):
        queryset.update(is_trusted=True)
        self.message_user(request, f"تم وضع {queryset.count()} جهاز كموثوق")
    mark_as_trusted.short_description = "وضع كجهاز موثوق"
    
    def mark_as_untrusted(self, request, queryset):
        queryset.update(is_trusted=False)
        self.message_user(request, f"تم إلغاء الثقة من {queryset.count()} جهاز")
    mark_as_untrusted.short_description = "إلغاء الثقة من الجهاز"
    
    def block_devices(self, request, queryset):
        queryset.update(status='BLOCKED')
        self.message_user(request, f"تم حظر {queryset.count()} جهاز")
    block_devices.short_description = "حظر الأجهزة"


@admin.register(MobileAppSession)
class MobileAppSessionAdmin(admin.ModelAdmin):
    """إدارة جلسات التطبيق المحمول"""
    
    list_display = [
        'device', 'session_type', 'start_time', 'end_time',
        'duration_display', 'app_version'
    ]
    list_filter = [
        'session_type', 'start_time', 'device__device_type'
    ]
    search_fields = [
        'device__user__username', 'session_id', 'device__device_name'
    ]
    readonly_fields = [
        'id', 'session_id', 'start_time', 'end_time', 'last_activity'
    ]
    date_hierarchy = 'start_time'
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}:{minutes:02d}"
        return "-"
    duration_display.short_description = "المدة"
    
    def has_add_permission(self, request):
        return False


@admin.register(MobilePushNotification)
class MobilePushNotificationAdmin(admin.ModelAdmin):
    """إدارة إشعارات الدفع المحمولة"""
    
    list_display = [
        'title', 'device', 'notification_type', 'priority',
        'status', 'scheduled_at', 'sent_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'status', 'created_at'
    ]
    search_fields = [
        'title', 'message', 'device__user__username'
    ]
    readonly_fields = [
        'id', 'sent_at', 'delivered_at', 'clicked_at',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'scheduled_at'
    
    fieldsets = (
        ('محتوى الإشعار', {
            'fields': ('device', 'title', 'message', 'notification_type')
        }),
        ('الإعدادات', {
            'fields': ('priority', 'status', 'scheduled_at')
        }),
        ('بيانات إضافية', {
            'fields': ('data_payload', 'action_url')
        }),
        ('إحصائيات', {
            'fields': ('sent_at', 'delivered_at', 'clicked_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['send_notifications', 'mark_as_sent']
    
    def send_notifications(self, request, queryset):
        # هنا يمكن إضافة منطق إرسال الإشعارات
        queryset.filter(status='PENDING').update(
            status='SENT', 
            sent_at=timezone.now()
        )
        self.message_user(request, f"تم إرسال {queryset.count()} إشعار")
    send_notifications.short_description = "إرسال الإشعارات"


@admin.register(MobileAppFeedback)
class MobileAppFeedbackAdmin(admin.ModelAdmin):
    """إدارة ملاحظات التطبيق المحمول"""
    
    list_display = [
        'subject', 'user', 'feedback_type', 'rating',
        'priority', 'status', 'created_at'
    ]
    list_filter = [
        'feedback_type', 'priority', 'status', 'rating', 'created_at'
    ]
    search_fields = [
        'subject', 'description', 'user__username', 'user__email'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'resolved_at'
    ]
    
    fieldsets = (
        ('معلومات المُرسِل', {
            'fields': ('user', 'device')
        }),
        ('محتوى التغذية الراجعة', {
            'fields': (
                'feedback_type', 'subject', 'description', 'rating'
            )
        }),
        ('الحالة والمعالجة', {
            'fields': (
                'status', 'priority', 'assigned_to', 
                'response', 'resolved_at'
            )
        }),
        ('معلومات تقنية', {
            'fields': (
                'app_version', 'device_info', 'error_log', 'screenshots'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_resolved', 'assign_to_me']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED', resolved_at=timezone.now())
        self.message_user(request, f"تم وضع {queryset.count()} ملاحظة كمحلولة")
    mark_as_resolved.short_description = "وضع كمحلول"
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user, status='REVIEWING')
        self.message_user(request, f"تم تعيين {queryset.count()} ملاحظة إليك")
    assign_to_me.short_description = "تعيين لي"


@admin.register(MobileAppAnalytics)
class MobileAppAnalyticsAdmin(admin.ModelAdmin):
    """إدارة تحليلات التطبيق المحمول"""
    
    list_display = [
        'device', 'event_type', 'event_name', 'screen_name',
        'load_time', 'timestamp'
    ]
    list_filter = [
        'event_type', 'screen_name', 'timestamp', 
        'device__device_type'
    ]
    search_fields = [
        'event_name', 'screen_name', 'device__user__username'
    ]
    readonly_fields = [
        'id', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# تخصيص موقع الإدارة
admin.site.site_header = "تطبيق الهاتف المحمول - لوحة التحكم"
admin.site.site_title = "إدارة التطبيق المحمول"
admin.site.index_title = "مرحباً بك في نظام إدارة التطبيق المحمول"