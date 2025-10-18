"""
URL Configuration for Web Interface
تكوين الروابط للواجهة الويب
"""

from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('courses/', views.courses_view, name='courses'),
    
    # API endpoints
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]