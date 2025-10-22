"""
Enhanced Web URLs Configuration for University Management System
تكوين روابط الويب المحسن لنظام إدارة الجامعة

This module contains improved URL patterns with better organization,
SEO-friendly URLs, and comprehensive routing.
"""

from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from . import views_improved as views

app_name = 'web'

# Authentication URLs
auth_patterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('password-reset/', PasswordResetView.as_view(
        template_name='web/auth/password_reset.html',
        email_template_name='web/auth/password_reset_email.html',
        subject_template_name='web/auth/password_reset_subject.txt',
        success_url='/web/password-reset/done/'
    ), name='password_reset'),
    
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='web/auth/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='web/auth/password_reset_confirm.html',
        success_url='/web/password-reset/complete/'
    ), name='password_reset_confirm'),
    
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='web/auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]

# Dashboard URLs
dashboard_patterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]

# Student-specific URLs
student_patterns = [
    path('my-courses/', views.student_courses_view, name='student_courses'),
    path('grades/', TemplateView.as_view(template_name='web/student/grades.html'), name='student_grades'),
    path('schedule/', TemplateView.as_view(template_name='web/student/schedule.html'), name='student_schedule'),
    path('enrollment/', TemplateView.as_view(template_name='web/student/enrollment.html'), name='student_enrollment'),
    path('payments/', TemplateView.as_view(template_name='web/student/payments.html'), name='student_payments'),
    path('transcripts/', TemplateView.as_view(template_name='web/student/transcripts.html'), name='student_transcripts'),
    path('attendance/', TemplateView.as_view(template_name='web/student/attendance.html'), name='student_attendance'),
]

# Teacher-specific URLs
teacher_patterns = [
    path('my-teaching/', views.teacher_courses_view, name='teacher_courses'),
    path('students/', TemplateView.as_view(template_name='web/teacher/students.html'), name='teacher_students'),
    path('grading/', TemplateView.as_view(template_name='web/teacher/grading.html'), name='teacher_grading'),
    path('attendance-management/', TemplateView.as_view(template_name='web/teacher/attendance.html'), name='teacher_attendance'),
    path('course-materials/', TemplateView.as_view(template_name='web/teacher/materials.html'), name='teacher_materials'),
    path('reports/', TemplateView.as_view(template_name='web/teacher/reports.html'), name='teacher_reports'),
]

# Admin-specific URLs
admin_patterns = [
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('users-management/', TemplateView.as_view(template_name='web/admin/users.html'), name='admin_users'),
    path('courses-management/', TemplateView.as_view(template_name='web/admin/courses.html'), name='admin_courses'),
    path('reports/', TemplateView.as_view(template_name='web/admin/reports.html'), name='admin_reports'),
    path('system-settings/', TemplateView.as_view(template_name='web/admin/settings.html'), name='admin_settings'),
    path('financial-overview/', TemplateView.as_view(template_name='web/admin/finance.html'), name='admin_finance'),
    path('analytics/', TemplateView.as_view(template_name='web/admin/analytics.html'), name='admin_analytics'),
    path('backup-restore/', TemplateView.as_view(template_name='web/admin/backup.html'), name='admin_backup'),
]

# Academic URLs (General)
academic_patterns = [
    path('courses/', TemplateView.as_view(template_name='web/academic/courses_list.html'), name='courses_list'),
    path('courses/<int:course_id>/', TemplateView.as_view(template_name='web/academic/course_detail.html'), name='course_detail'),
    path('departments/', TemplateView.as_view(template_name='web/academic/departments.html'), name='departments'),
    path('programs/', TemplateView.as_view(template_name='web/academic/programs.html'), name='programs'),
    path('calendar/', TemplateView.as_view(template_name='web/academic/calendar.html'), name='academic_calendar'),
    path('announcements/', TemplateView.as_view(template_name='web/academic/announcements.html'), name='announcements'),
]

# Financial URLs
financial_patterns = [
    path('payments/', TemplateView.as_view(template_name='web/finance/payments.html'), name='payments'),
    path('invoices/', TemplateView.as_view(template_name='web/finance/invoices.html'), name='invoices'),
    path('scholarships/', TemplateView.as_view(template_name='web/finance/scholarships.html'), name='scholarships'),
    path('financial-aid/', TemplateView.as_view(template_name='web/finance/financial_aid.html'), name='financial_aid'),
    path('payment-history/', TemplateView.as_view(template_name='web/finance/payment_history.html'), name='payment_history'),
]

# API-like URLs for AJAX requests
api_patterns = [
    path('api/user-info/', views.api_user_info, name='api_user_info'),
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]

# Help and Support URLs
support_patterns = [
    path('help/', TemplateView.as_view(template_name='web/support/help.html'), name='help'),
    path('faq/', TemplateView.as_view(template_name='web/support/faq.html'), name='faq'),
    path('contact/', TemplateView.as_view(template_name='web/support/contact.html'), name='contact'),
    path('tutorials/', TemplateView.as_view(template_name='web/support/tutorials.html'), name='tutorials'),
    path('downloads/', TemplateView.as_view(template_name='web/support/downloads.html'), name='downloads'),
]

# Main URL patterns
urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),
    
    # Authentication URLs
    path('auth/', include(auth_patterns)),
    
    # Dashboard URLs
    path('dashboard/', include(dashboard_patterns)),
    
    # Role-specific URLs
    path('student/', include(student_patterns)),
    path('teacher/', include(teacher_patterns)),
    path('admin/', include(admin_patterns)),
    
    # Academic URLs
    path('academic/', include(academic_patterns)),
    
    # Financial URLs
    path('finance/', include(financial_patterns)),
    
    # Support URLs
    path('support/', include(support_patterns)),
    
    # API URLs
    path('', include(api_patterns)),
    
    # Legacy URLs for backward compatibility
    path('login/', views.login_view, name='login_legacy'),
    path('logout/', views.logout_view, name='logout_legacy'),
    path('my-courses/', views.student_courses_view, name='my_courses_legacy'),
    path('my-teaching/', views.teacher_courses_view, name='my_teaching_legacy'),
    
    # Utility URLs
    path('switch-language/', TemplateView.as_view(template_name='web/utils/language_switch.html'), name='switch_language'),
    path('accessibility/', TemplateView.as_view(template_name='web/utils/accessibility.html'), name='accessibility'),
    path('privacy-policy/', TemplateView.as_view(template_name='web/legal/privacy.html'), name='privacy_policy'),
    path('terms-of-service/', TemplateView.as_view(template_name='web/legal/terms.html'), name='terms_of_service'),
]

# Add error handlers
handler404 = views.error_404_view
handler500 = views.error_500_view
handler403 = views.error_403_view