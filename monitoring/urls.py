"""
URLs لنظام المراقبة
Monitoring System URLs

تم تطويره في: 2025-11-02
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'monitoring'

# API URLs
api_urlpatterns = [
    path('health/', views.SystemHealthView.as_view(), name='system-health'),
    path('metrics/', views.PerformanceMetricsView.as_view(), name='performance-metrics'),
    path('errors/', views.ErrorStatisticsView.as_view(), name='error-statistics'),
    path('report/', views.PerformanceReportView.as_view(), name='performance-report'),
    path('quick-health/', views.quick_health_check, name='quick-health-check'),
    path('system-data/', views.system_metrics_json, name='system-metrics-json'),
    path('clear-errors/', views.clear_error_logs, name='clear-error-logs'),
]

# Web Interface URLs
web_urlpatterns = [
    path('dashboard/', views.MonitoringDashboardView.as_view(), name='dashboard'),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', include(web_urlpatterns)),
]