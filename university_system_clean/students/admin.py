from django.contrib import admin
from .models import User, Student, Department

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'major', 'current_semester', 'gpa', 'status']
    list_filter = ['status', 'major', 'current_semester']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']
    ordering = ['-enrollment_date']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'head_of_department']
    search_fields = ['code', 'name']
