from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AcademicYear, Semester, Enrollment, Grade, Attendance, 
    Schedule, GradeScale, AcademicProgram, Prerequisite, AcademicCalendar
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['name']
    ordering = ['-start_date']
    
    def save_model(self, request, obj, form, change):
        if obj.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save_model(request, obj, form, change)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'registration_start', 'registration_end', 'is_current']
    list_filter = ['name', 'is_current', 'academic_year']
    search_fields = ['academic_year__name']
    ordering = ['-start_date']


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    readonly_fields = ['percentage']
    fields = ['grade_type', 'title', 'points_earned', 'points_possible', 'percentage', 'weight', 'date_assigned', 'date_due']


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    fields = ['date', 'status', 'notes']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'student_name', 'course_name', 'semester', 'status', 'final_grade', 'enrollment_date']
    list_filter = ['status', 'semester', 'course__department']
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name', 'course__code', 'course__name']
    inlines = [GradeInline, AttendanceInline]
    ordering = ['-enrollment_date']
    
    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student Name'
    
    def course_name(self, obj):
        return obj.course.name
    course_name.short_description = 'Course Name'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'grade_type', 'points_earned', 'points_possible', 'percentage_display', 'date_assigned', 'date_graded']
    list_filter = ['grade_type', 'enrollment__semester', 'enrollment__course']
    search_fields = ['title', 'enrollment__student__student_id', 'enrollment__course__code']
    ordering = ['-date_assigned']
    
    def percentage_display(self, obj):
        percentage = obj.percentage
        color = 'green' if percentage >= 70 else 'orange' if percentage >= 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    percentage_display.short_description = 'Percentage'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'student_name', 'course_name', 'date', 'status', 'recorded_by', 'recorded_at']
    list_filter = ['status', 'date', 'enrollment__semester']
    search_fields = ['enrollment__student__student_id', 'enrollment__course__code']
    ordering = ['-date']
    
    def student_name(self, obj):
        return obj.enrollment.student.user.get_full_name()
    student_name.short_description = 'Student'
    
    def course_name(self, obj):
        return obj.enrollment.course.code
    course_name.short_description = 'Course'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'instructor', 'room', 'building', 'semester']
    list_filter = ['day_of_week', 'semester', 'course__department']
    search_fields = ['course__code', 'course__name', 'instructor__first_name', 'instructor__last_name', 'room']
    ordering = ['day_of_week', 'start_time']


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ['letter_grade', 'min_percentage', 'max_percentage', 'gpa_points', 'is_passing']
    ordering = ['-min_percentage']


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'degree_type', 'department', 'required_credits', 'duration_semesters', 'is_active']
    list_filter = ['degree_type', 'department', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['course', 'prerequisite_course', 'min_grade']
    search_fields = ['course__code', 'prerequisite_course__code']
    ordering = ['course__code']


@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'end_date', 'is_holiday', 'semester']
    list_filter = ['event_type', 'is_holiday', 'semester']
    search_fields = ['title', 'description']
    ordering = ['date']
    date_hierarchy = 'date'