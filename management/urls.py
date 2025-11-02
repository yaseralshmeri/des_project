"""
Management URLs Configuration
تكوين روابط إدارة النظام
"""

from django.urls import path, include
from . import views

app_name = 'management'

urlpatterns = [
    # System Management
    path('', views.dashboard, name='dashboard'),
    path('system/', views.system_info, name='system_info'),
    path('backup/', views.backup_system, name='backup_system'),
    path('maintenance/', views.maintenance_mode, name='maintenance_mode'),
    
    # Database Management
    path('database/', views.database_status, name='database_status'),
    path('database/optimize/', views.optimize_database, name='optimize_database'),
    path('database/backup/', views.backup_database, name='backup_database'),
    
    # Log Management
    path('logs/', views.view_logs, name='view_logs'),
    path('logs/clear/', views.clear_logs, name='clear_logs'),
    
    # System Health
    path('health/', views.system_health, name='system_health'),
    
    # API Endpoints
    path('api/', include([
        path('status/', views.api_system_status, name='api_system_status'),
        path('performance/', views.api_performance_metrics, name='api_performance_metrics'),
    ])),
]