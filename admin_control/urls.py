"""
Admin Control URLs Configuration
إعدادات روابط لوحة التحكم الإدارية
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()

# Register viewsets with the router
# router.register(r'system-settings', views.SystemSettingsViewSet, basename='system-settings')
# router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-logs')

app_name = 'admin_control'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    
    # Web interface routes (placeholder)
    # path('', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    # path('settings/', views.SystemSettingsView.as_view(), name='system-settings'),
    # path('logs/', views.AuditLogsView.as_view(), name='audit-logs'),
]