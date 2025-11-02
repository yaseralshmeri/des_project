"""
University Management System - Main URLs Configuration
تكوين URLs الرئيسي لنظام إدارة الجامعة

Auto-optimized on: 2025-11-02 17:53:46
تم تحسينه تلقائياً في: 2025-11-02 17:53:46
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

# API Documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Schema for Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="University Management API",
        default_version='v1',
        description="نظام إدارة الجامعة - واجهة برمجة التطبيقات",
        terms_of_service="https://www.university.edu/terms/",
        contact=openapi.Contact(email="api@university.edu"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# System Health Check
def system_health(request):
    """فحص صحة النظام"""
    return JsonResponse({
        'status': 'ok',
        'system': 'University Management System',
        'version': '2.0.0',
        'timestamp': '2025-11-02 17:53:46',
        'debug_mode': settings.DEBUG
    })

# Main URL Patterns
urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication URLs
    path('auth/', include([
        path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
        path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    ])),
    
    # Core Applications
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('academic/', include('academic.urls')),
    path('finance/', include('finance.urls')),
    path('hr/', include('hr.urls')),
    
    # Advanced Applications  
    path('ai/', include('ai.urls')),
    path('smart-ai/', include('smart_ai.urls')),
    path('security/', include('cyber_security.urls')),
    path('attendance/', include('attendance_qr.urls')),
    path('notifications/', include('notifications.urls')),
    
    # Management & Reports
    path('admin-control/', include('admin_control.urls')),
    path('reports/', include('reports.urls')),
    path('roles/', include('roles_permissions.urls')),
    
    # Web Interface & Mobile
    path('web/', include('web.urls')),
    path('mobile/', include('mobile_app.urls')),
    
    # API Endpoints
    path('api/v1/', include([
        path('students/', include('students.urls')),
        path('courses/', include('courses.urls')),
        path('academic/', include('academic.urls')),
        path('finance/', include('finance.urls')),
        path('hr/', include('hr.urls')),
        path('ai/', include('ai.urls')),
        path('security/', include('cyber_security.urls')),
        path('attendance/', include('attendance_qr.urls')),
        path('notifications/', include('notifications.urls')),
        path('reports/', include('reports.urls')),
    ])),
    
    # System Utilities
    path('health/', system_health, name='system_health'),
    path('', TemplateView.as_view(template_name='web/index.html'), name='home'),
]

# Static & Media Files (Development only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom Error Handlers
handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'
handler403 = 'web.views.handler403'
handler400 = 'web.views.handler400'

# Admin Site Customization
admin.site.site_header = "نظام إدارة الجامعة"
admin.site.site_title = "إدارة الجامعة"
admin.site.index_title = "لوحة التحكم الرئيسية"
