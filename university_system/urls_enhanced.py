"""
Enhanced URL Configuration for University Management System
تكوين محسن للروابط في نظام إدارة الجامعة

This enhanced URL configuration provides:
- Better organization and structure
- Enhanced security
- API versioning
- Comprehensive error handling
- Multi-language support
- Performance optimizations
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# API DOCUMENTATION SETUP - إعداد توثيق API
# =============================================================================

def setup_api_documentation():
    """Setup API documentation with error handling"""
    try:
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi
        
        schema_view = get_schema_view(
            openapi.Info(
                title="University Management System API",
                default_version='v1',
                description="""
                # University Management System API Documentation
                
                ## Overview
                Complete RESTful API for University Management System with comprehensive endpoints for:
                
                ### 🎓 Academic Management
                - Student enrollment and management
                - Course management and scheduling
                - Grade and transcript management
                - Academic year and semester management
                
                ### 💰 Financial Management
                - Fee management and payments
                - Financial reports and analytics
                - Scholarship and aid management
                
                ### 👥 Human Resources
                - Staff and faculty management
                - Role and permission management
                - Employee records and payroll
                
                ### 📊 Reports & Analytics
                - Academic performance reports
                - Financial reports
                - System usage analytics
                - AI-powered predictions
                
                ### 🔔 Notifications
                - Real-time notifications
                - Email and SMS notifications
                - System announcements
                
                ## Authentication
                This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
                ```
                Authorization: Bearer <your_token_here>
                ```
                
                ## Rate Limiting
                API requests are rate-limited based on user type:
                - Anonymous users: 100 requests/hour
                - Authenticated users: 1000 requests/hour
                - Login attempts: 5 attempts/minute
                
                ## API Versioning
                Current API version: v1
                Future versions will be available at `/api/v2/`, etc.
                """,
                terms_of_service="https://university.edu/terms/",
                contact=openapi.Contact(
                    name="University IT Support",
                    email="support@university.edu",
                    url="https://university.edu/support/"
                ),
                license=openapi.License(
                    name="MIT License",
                    url="https://opensource.org/licenses/MIT"
                ),
            ),
            public=True,
            permission_classes=[permissions.AllowAny],
            url=f"{'https' if not settings.DEBUG else 'http'}://{'yourdomain.com' if not settings.DEBUG else 'localhost:8000'}",
            patterns=[
                path('api/v1/', include('university_system.api_urls')),
            ],
        )
        
        return [
            path('api/docs/', 
                 cache_page(300)(schema_view.with_ui('swagger', cache_timeout=0)), 
                 name='api-docs-swagger'),
            path('api/redoc/', 
                 cache_page(300)(schema_view.with_ui('redoc', cache_timeout=0)), 
                 name='api-docs-redoc'),
            path('api/schema/', 
                 cache_page(300)(schema_view.without_ui(cache_timeout=0)), 
                 name='api-schema-json'),
        ]
    except ImportError as e:
        logger.warning(f"API documentation not available: {e}")
        return [
            path('api/docs/', 
                 TemplateView.as_view(template_name='errors/api_docs_unavailable.html'),
                 name='api-docs-unavailable'),
        ]

# Get API documentation URLs
api_docs_urls = setup_api_documentation()

# =============================================================================
# ROOT REDIRECT LOGIC - منطق التوجيه الرئيسي
# =============================================================================

def enhanced_root_redirect(request):
    """
    Enhanced root redirect with user role detection and preferences
    """
    try:
        if request.user.is_authenticated:
            # Log user access
            logger.info(f"User {request.user.username} accessed root URL")
            
            # Redirect based on user role
            if hasattr(request.user, 'role'):
                role_redirects = {
                    'ADMIN': '/web/enhanced/admin-panel/',
                    'STAFF': '/web/enhanced/admin-panel/',
                    'TEACHER': '/web/enhanced/teaching/',
                    'STUDENT': '/web/enhanced/dashboard/',
                }
                redirect_url = role_redirects.get(request.user.role, '/web/enhanced/dashboard/')
                return HttpResponseRedirect(redirect_url)
            
            return HttpResponseRedirect('/web/enhanced/dashboard/')
        else:
            # Check if user prefers Arabic or English
            lang = request.GET.get('lang', 'ar')
            return HttpResponseRedirect(f'/web/enhanced/?lang={lang}')
    except Exception as e:
        logger.error(f"Root redirect error: {e}")
        return HttpResponseRedirect('/web/enhanced/')

# =============================================================================
# API HEALTH CHECK - فحص صحة النظام
# =============================================================================

@csrf_exempt
def api_health_check(request):
    """
    API health check endpoint
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        import time
        
        start_time = time.time()
        
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
        
        # Check cache
        cache.set('health_check', 'ok', 30)
        cache_status = "healthy" if cache.get('health_check') == 'ok' else "unhealthy"
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        health_data = {
            "status": "healthy",
            "timestamp": int(time.time()),
            "services": {
                "database": db_status,
                "cache": cache_status,
            },
            "response_time_ms": response_time,
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        }
        
        return JsonResponse(health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time()),
        }, status=503)

# =============================================================================
# CORE URL PATTERNS - الأنماط الأساسية للروابط
# =============================================================================

# Core system URLs (non-internationalized)
core_urlpatterns = [
    # Root redirect
    path('', enhanced_root_redirect, name='root'),
    
    # Health checks
    path('health/', api_health_check, name='api-health-check'),
    path('health/detailed/', include('health_check.urls')),
    
    # API endpoints (non-internationalized)
    path('api/v1/', include('university_system.api_urls')),
    
    # JWT Authentication
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Django admin
    path('admin/', admin.site.urls),
] + api_docs_urls

# =============================================================================
# INTERNATIONALIZED URL PATTERNS - الأنماط متعددة اللغات
# =============================================================================

# Main application URLs (internationalized)
i18n_urlpatterns = i18n_patterns(
    # Web interface
    path('', include('web.urls')),
    
    # Application specific URLs
    path('academic/', include('academic.urls')),
    path('courses/', include('courses.urls')),
    path('students/', include('students.urls')),
    path('finance/', include('finance.urls')),
    path('hr/', include('hr.urls')),
    path('reports/', include('reports.urls')),
    path('ai/', include('ai.urls')),
    
    # Add prefix_default_language=False to remove default language prefix
    prefix_default_language=False,
)

# =============================================================================
# ERROR HANDLERS - معالجات الأخطاء
# =============================================================================

def custom_404_view(request, exception=None):
    """Custom 404 error handler"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Endpoint not found',
            'status_code': 404,
            'message': 'The requested API endpoint does not exist.',
            'available_endpoints': [
                '/api/v1/',
                '/api/docs/',
                '/api/health/',
            ]
        }, status=404)
    
    from django.shortcuts import render
    return render(request, 'errors/404.html', {
        'university_name': getattr(settings, 'UNIVERSITY_NAME', 'University'),
        'support_email': 'support@university.edu',
    }, status=404)

def custom_500_view(request):
    """Custom 500 error handler"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal server error',
            'status_code': 500,
            'message': 'An unexpected error occurred. Please try again later.',
            'support': 'support@university.edu'
        }, status=500)
    
    from django.shortcuts import render
    return render(request, 'errors/500.html', {
        'university_name': getattr(settings, 'UNIVERSITY_NAME', 'University'),
        'support_email': 'support@university.edu',
    }, status=500)

def custom_403_view(request, exception=None):
    """Custom 403 error handler"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Access denied',
            'status_code': 403,
            'message': 'You do not have permission to access this resource.',
            'login_url': '/web/login/',
        }, status=403)
    
    from django.shortcuts import render
    return render(request, 'errors/403.html', {
        'university_name': getattr(settings, 'UNIVERSITY_NAME', 'University'),
        'login_url': '/web/login/',
    }, status=403)

# =============================================================================
# COMBINE ALL URL PATTERNS - دمج جميع أنماط الروابط
# =============================================================================

urlpatterns = core_urlpatterns + i18n_urlpatterns

# =============================================================================
# DEVELOPMENT SPECIFIC URLS - روابط خاصة بالتطوير
# =============================================================================

if settings.DEBUG:
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
    
    # Development utilities
    urlpatterns += [
        path('dev/info/', TemplateView.as_view(template_name='dev/info.html'), name='dev-info'),
        path('dev/test-email/', include('university_system.dev_urls')),
    ]

# =============================================================================
# CUSTOM ERROR HANDLERS - معالجات الأخطاء المخصصة
# =============================================================================

handler404 = custom_404_view
handler500 = custom_500_view
handler403 = custom_403_view

# =============================================================================
# ADMIN SITE CUSTOMIZATION - تخصيص موقع الإدارة
# =============================================================================

# Enhanced admin site configuration
admin.site.site_header = f"{getattr(settings, 'UNIVERSITY_NAME', 'University')} | نظام إدارة الجامعة"
admin.site.site_title = f"{getattr(settings, 'UNIVERSITY_CODE', 'UNI')} Admin | إدارة النظام"
admin.site.index_title = "لوحة التحكم الإدارية | Administrative Control Panel"
admin.site.site_url = "/web/enhanced/dashboard/"
admin.site.enable_nav_sidebar = True

# =============================================================================
# URL VALIDATION - التحقق من صحة الروابط
# =============================================================================

def validate_urls():
    """Validate URL configuration"""
    warnings = []
    
    # Check for duplicate names
    url_names = []
    for pattern in urlpatterns:
        if hasattr(pattern, 'name') and pattern.name:
            if pattern.name in url_names:
                warnings.append(f"Duplicate URL name: {pattern.name}")
            url_names.append(pattern.name)
    
    # Check for missing essential URLs
    essential_urls = ['root', 'api-health-check', 'token_obtain_pair']
    for url_name in essential_urls:
        if url_name not in url_names:
            warnings.append(f"Missing essential URL: {url_name}")
    
    if warnings and settings.DEBUG:
        logger.warning("URL Configuration Warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")

# Run URL validation
validate_urls()

# Log successful URL configuration
logger.info(f"🔗 Enhanced URL configuration loaded successfully")
logger.info(f"📍 Total URL patterns: {len(urlpatterns)}")
logger.info(f"🌐 Internationalization: {'Enabled' if i18n_urlpatterns else 'Disabled'}")
logger.info(f"📚 API Documentation: {'Available' if api_docs_urls else 'Unavailable'}")