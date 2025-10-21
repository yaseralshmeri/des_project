from django.contrib import admin
from .models import User, StudentProfile
from courses.models import Department

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'study_status', 'academic_standing']
    list_filter = ['study_status', 'academic_standing']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
    ordering = ['-created_at']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_ar', 'head']
    search_fields = ['code', 'name_ar', 'name_en']
