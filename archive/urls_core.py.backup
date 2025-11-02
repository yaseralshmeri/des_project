"""
University Management System - Core URLs Configuration (Minimal Working Version)
تكوين URLs أساسي للنظام الأساسي
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView

# System Health Check
def system_health(request):
    """فحص صحة النظام"""
    return JsonResponse({
        'status': 'ok',
        'system': 'University Management System - Core',
        'version': '3.0.0 Unified Core',
        'timestamp': '2025-11-02',
        'debug_mode': settings.DEBUG,
        'message': 'Core system is running successfully'
    })

# Main URL Patterns - Core Only
urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # System Health
    path('health/', system_health, name='system_health'),
    path('api/health/', system_health, name='api_health'),
    
    # Root path
    path('', system_health, name='home'),
]

# Static & Media Files (Development only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin Site Customization
admin.site.site_header = "نظام إدارة الجامعة - النسخة الأساسية"
admin.site.site_title = "إدارة الجامعة"
admin.site.index_title = "لوحة التحكم الرئيسية"