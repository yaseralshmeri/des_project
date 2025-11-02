# نظام الحضور بـ QR - لوحة التحكم الإدارية
# QR Attendance System - Admin Interface

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    QRCode, AttendanceSession, AttendanceRecord, 
    AttendanceReport, QRScanLog, AttendanceException, AttendanceSettings
)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    """إدارة رموز QR"""
    
    list_display = [
        'qr_code_id', 'attendance_session', 'qr_preview', 'status', 
        'expires_at', 'created_at'
    ]
    list_filter = [
        'status', 'expires_at', 'created_at'
    ]
    search_fields = [
        'qr_code_id', 'attendance_session__session_name'
    ]
    readonly_fields = [
        'id', 'qr_code_id', 'qr_image', 'created_at', 
        'qr_data', 'secret_key', 'qr_preview'
    ]
    
    fieldsets = (
        ('معلومات الرمز', {
            'fields': ('qr_code_id', 'attendance_session', 'qr_data')
        }),
        ('رمز QR', {
            'fields': ('qr_image', 'qr_preview')
        }),
        ('الإعدادات', {
            'fields': ('status', 'expires_at', 'max_usage')
        }),
        ('إحصائيات', {
            'fields': ('usage_count',)
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'secret_key'),
            'classes': ('collapse',)
        })
    )
    
    def qr_preview(self, obj):
        """عرض مصغر لرمز QR"""
        if obj.qr_image:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.qr_image.url
            )
        return "لا يوجد رمز"
    qr_preview.short_description = "معاينة QR"
    
    def minutes_late(self, obj):
        """دقائق التأخير"""
        return getattr(obj, 'minutes_late', 0)
    minutes_late.short_description = "دقائق التأخير"


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    """إدارة جلسات الحضور"""
    
    list_display = [
        'session_name', 'course_offering', 'instructor', 'session_type',
        'scheduled_start_time', 'scheduled_end_time', 'status', 'total_students'
    ]
    list_filter = [
        'session_type', 'status', 'scheduled_start_time', 'course_offering'
    ]
    search_fields = [
        'session_name', 'description', 'course_offering__course__name_ar',
        'instructor__first_name', 'instructor__last_name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at',
        'total_students', 'present_count', 'late_count', 'absent_count'
    ]
    date_hierarchy = 'scheduled_start_time'
    
    fieldsets = (
        ('معلومات الجلسة', {
            'fields': ('session_name', 'description', 'session_type')
        }),
        ('الارتباط الأكاديمي', {
            'fields': ('course_offering', 'instructor')
        }),
        ('التوقيت', {
            'fields': ('scheduled_start_time', 'scheduled_end_time', 'actual_start_time', 'actual_end_time')
        }),
        ('الإعدادات', {
            'fields': ('status', 'attendance_window_minutes', 'late_threshold_minutes')
        }),
        ('المكان', {
            'fields': ('classroom', 'location_coordinates')
        }),
        ('إحصائيات', {
            'fields': ('total_students', 'present_count', 'late_count', 'absent_count'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'course_offering', 'instructor'
        )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """إدارة سجلات الحضور"""
    
    list_display = [
        'student', 'attendance_session', 'status', 'recorded_at',
        'attendance_method', 'is_verified'
    ]
    list_filter = [
        'status', 'attendance_method', 'is_verified', 
        'recorded_at', 'attendance_session__course_offering'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__username', 'attendance_session__session_name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'recorded_at', 'minutes_late'
    ]
    date_hierarchy = 'recorded_at'
    
    fieldsets = (
        ('معلومات الحضور', {
            'fields': ('student', 'attendance_session', 'status')
        }),
        ('تفاصيل التحقق', {
            'fields': ('recorded_at', 'attendance_method', 'qr_code', 'is_verified')
        }),
        ('بيانات إضافية', {
            'fields': ('device_info', 'scan_location_latitude', 'scan_location_longitude')
        }),
        ('ملاحظات', {
            'fields': ('notes', 'excuse_reason')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'attendance_session', 'qr_code'
        )


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    """إدارة تقارير الحضور"""
    
    list_display = [
        'report_name', 'report_type', 'generated_by', 
        'start_date', 'end_date', 'created_at'
    ]
    list_filter = [
        'report_type', 'status', 'created_at', 'start_date'
    ]
    search_fields = [
        'report_name', 'generated_by__username'
    ]
    readonly_fields = [
        'id', 'created_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')


@admin.register(QRScanLog)
class QRScanLogAdmin(admin.ModelAdmin):
    """إدارة سجلات مسح QR"""
    
    list_display = [
        'qr_code', 'scanned_by', 'scan_result', 
        'ip_address', 'scanned_at'
    ]
    list_filter = [
        'scan_result', 'scanned_at'
    ]
    search_fields = [
        'qr_code__qr_code_id', 'scanned_by__username', 'ip_address'
    ]
    readonly_fields = [
        'id', 'scanned_at'
    ]
    date_hierarchy = 'scanned_at'
    
    def has_add_permission(self, request):
        return False  # منع الإضافة اليدوية


@admin.register(AttendanceException)
class AttendanceExceptionAdmin(admin.ModelAdmin):
    """إدارة استثناءات الحضور"""
    
    list_display = [
        'student', 'attendance_session', 'exception_type', 
        'status', 'submitted_at'
    ]
    list_filter = [
        'exception_type', 'status', 'submitted_at'
    ]
    search_fields = [
        'student__username', 'attendance_session__session_name', 'reason'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'submitted_at'
    ]
    
    fieldsets = (
        ('معلومات الاستثناء', {
            'fields': ('student', 'attendance_session', 'exception_type')
        }),
        ('تفاصيل الطلب', {
            'fields': ('reason', 'supporting_documents', 'effective_date')
        }),
        ('المراجعة', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'reviewer_comments')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    """إدارة إعدادات الحضور"""
    
    list_display = [
        'default_attendance_window_minutes', 'default_late_threshold_minutes',
        'enable_location_verification', 'updated_at'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('إعدادات عامة', {
            'fields': ('default_attendance_window_minutes', 'default_late_threshold_minutes')
        }),
        ('إعدادات QR Code', {
            'fields': ('qr_code_refresh_minutes', 'qr_code_valid_range_meters', 'enable_location_verification')
        }),
        ('إعدادات النقاط', {
            'fields': ('present_points', 'late_points', 'excused_points', 'absent_points')
        }),
        ('إعدادات التنبيهات', {
            'fields': ('enable_attendance_reminders', 'reminder_minutes_before')
        }),
        ('إعدادات التقارير', {
            'fields': ('auto_generate_reports', 'report_generation_frequency')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def has_delete_permission(self, request, obj=None):
        return False  # منع حذف الإعدادات
    
    def has_change_permission(self, request, obj=None):
        return False  # منع التعديل


# تخصيص موقع الإدارة
admin.site.site_header = "نظام الحضور بـ QR - لوحة التحكم"
admin.site.site_title = "إدارة نظام الحضور"
admin.site.index_title = "مرحباً بك في نظام إدارة الحضور"

# إجراءات مخصصة
def activate_qr_codes(modeladmin, request, queryset):
    """تفعيل رموز QR المحددة"""
    queryset.update(is_active=True)
activate_qr_codes.short_description = "تفعيل رموز QR المحددة"

def deactivate_qr_codes(modeladmin, request, queryset):
    """إلغاء تفعيل رموز QR المحددة"""
    queryset.update(is_active=False)
deactivate_qr_codes.short_description = "إلغاء تفعيل رموز QR المحددة"

def activate_sessions(modeladmin, request, queryset):
    """تفعيل الجلسات المحددة"""
    queryset.update(is_active=True)
activate_sessions.short_description = "تفعيل الجلسات المحددة"

def deactivate_sessions(modeladmin, request, queryset):
    """إلغاء تفعيل الجلسات المحددة"""
    queryset.update(is_active=False)
deactivate_sessions.short_description = "إلغاء تفعيل الجلسات المحددة"

# إضافة الإجراءات للنماذج
QRCodeAdmin.actions = [activate_qr_codes, deactivate_qr_codes]
AttendanceSessionAdmin.actions = [activate_sessions, deactivate_sessions]