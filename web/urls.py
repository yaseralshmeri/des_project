"""
URL Configuration for Web Interface
تكوين الروابط للواجهة الويب
"""

from django.urls import path
from . import views
from . import enhanced_views

app_name = 'web'

urlpatterns = [
    # Main pages
    path('', enhanced_views.enhanced_home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('courses/', views.courses_view, name='courses'),
    
    # Enhanced pages
    path('enhanced/', enhanced_views.enhanced_home_view, name='enhanced_home'),
    path('enhanced/dashboard/', enhanced_views.enhanced_dashboard_view, name='enhanced_dashboard'),
    
    # Student specific pages
    path('my-courses/', enhanced_views.my_courses_view, name='my_courses'),
    path('my-grades/', enhanced_views.my_grades_view, name='my_grades'),
    path('my-schedule/', enhanced_views.my_schedule_view, name='my_schedule'),
    path('my-fees/', enhanced_views.my_fees_view, name='my_fees'),
    
    # Teacher specific pages
    path('teaching/', enhanced_views.teaching_view, name='teaching'),
    path('students/', enhanced_views.students_view, name='students'),
    path('grade-management/', enhanced_views.grade_management_view, name='grade_management'),
    
    # Admin specific pages
    path('admin-panel/', enhanced_views.admin_panel_view, name='admin_panel'),
    path('system-stats/', enhanced_views.system_stats_view, name='system_stats'),
    path('user-management/', enhanced_views.user_management_view, name='user_management'),
    
    # API endpoints
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/dashboard-stats/', enhanced_views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/search/', enhanced_views.api_search, name='api_search'),
]