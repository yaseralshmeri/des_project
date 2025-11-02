# نظام الحضور بـ QR - لوحة التحكم الإدارية
# QR Attendance System - Admin Interface

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    QRCode, AttendanceSession, AttendanceRecord, 
    AttendanceReport, QRScanLog
)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    """إدارة رموز QR"""
    
    list_display = [
        'code_id', 'session', 'qr_preview', 'is_active', 
        'expires_at', 'created_at'
    ]
    list_filter = [
        'is_active', 'expires_at', 'created_at'
    ]
    search_fields = [
        'code_id', 'session__session_name'
    ]
    readonly_fields = [
        'id', 'code_id', 'qr_image', 'created_at', 
        'updated_at', 'qr_preview'
    ]
    
    fieldsets = (
        ('معلومات الرمز', {
            'fields': ('code_id', 'session', 'qr_data')
        }),
        ('رمز QR', {
            'fields': ('qr_image', 'qr_preview')
        }),
        ('الإعدادات', {
            'fields': ('is_active', 'expires_at', 'scan_limit')
        }),
        ('إحصائيات', {
            'fields': ('scan_count', 'last_scanned_at')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'created_at', 'updated_at'),
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


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    """إدارة جلسات الحضور"""
    
    list_display = [
        'session_name', 'course', 'instructor', 'session_type',
        'start_time', 'end_time', 'is_active', 'total_attendees'
    ]
    list_filter = [
        'session_type', 'is_active', 'start_time', 'course'
    ]
    search_fields = [
        'session_name', 'description', 'course__course_name',
        'instructor__user__first_name', 'instructor__user__last_name'
    ]
    readonly_fields = [
        'id', 'session_id', 'created_at', 'updated_at',
        'total_attendees', 'attendance_percentage'
    ]
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('معلومات الجلسة', {
            'fields': ('session_id', 'session_name', 'description', 'session_type')
        }),
        ('الارتباط الأكاديمي', {
            'fields': ('course', 'instructor')
        }),
        ('التوقيت', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('الإعدادات', {
            'fields': ('is_active', 'allow_late_entry', 'late_entry_minutes')
        }),
        ('المكان', {
            'fields': ('location', 'room_number', 'building')
        }),
        ('إحصائيات', {
            'fields': ('total_attendees', 'attendance_percentage'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'course', 'instructor__user'
        )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """إدارة سجلات الحضور"""
    
    list_display = [
        'student', 'session', 'status', 'check_in_time',
        'is_late', 'verification_method'
    ]
    list_filter = [
        'status', 'verification_method', 'is_late', 
        'check_in_time', 'session__course'
    ]
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'student__student_id', 'session__session_name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'is_late'
    ]
    date_hierarchy = 'check_in_time'
    
    fieldsets = (
        ('معلومات الحضور', {
            'fields': ('student', 'session', 'status')
        }),
        ('تفاصيل التحقق', {
            'fields': ('check_in_time', 'verification_method', 'qr_code_used')
        }),
        ('بيانات إضافية', {
            'fields': ('ip_address', 'device_info', 'location_data')
        }),
        ('ملاحظات', {
            'fields': ('notes', 'verification_notes')
        }),
        ('معلومات تقنية', {
            'fields': ('id', 'is_late', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'session', 'qr_code_used'
        )


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    """إدارة تقارير الحضور"""
    
    list_display = [
        'report_name', 'report_type', 'generated_by', 
        'date_from', 'date_to', 'created_at'
    ]
    list_filter = [
        'report_type', 'created_at', 'date_from'
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
        'qr_code__code_id', 'scanned_by__username', 'ip_address'
    ]
    readonly_fields = [
        'id', 'scanned_at'
    ]
    date_hierarchy = 'scanned_at'
    
    def has_add_permission(self, request):
        return False  # منع الإضافة اليدوية
    
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