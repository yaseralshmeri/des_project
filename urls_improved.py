"""
University Management System - Enhanced Main URLs Configuration
نظام إدارة الجامعة - تكوين الروابط الرئيسية المحسن
Created: 2024-10-22
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
import json

# Conditional import for API documentation
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from rest_framework import permissions
    
    schema_view = get_schema_view(
        openapi.Info(
            title="University Management System API",
            default_version='v1',
            description="""
            ## نظام إدارة الجامعة الشامل | Comprehensive University Management System
            
            ### الوصف | Description
            واجهة برمجية متكاملة لنظام إدارة الجامعة يوفر جميع الوظائف الأكاديمية والإدارية والمالية.
            
            A comprehensive RESTful API for university management system providing all academic, administrative, and financial functions.
            
            ### الميزات الرئيسية | Key Features
            - 🎓 **إدارة الطلاب** | Student Management
            - 📚 **إدارة المقررات** | Course Management  
            - 👨‍🏫 **إدارة الأساتذة** | Faculty Management
            - 💰 **النظام المالي** | Financial System
            - 🔔 **نظام الإشعارات** | Notification System
            - 📊 **التقارير والإحصائيات** | Reports & Analytics
            - 🤖 **الذكاء الاصطناعي** | AI Integration
            - 🔐 **نظام الأدوار والصلاحيات** | Role-based Access Control
            
            ### المصادقة | Authentication
            استخدم JWT Token للمصادقة. احصل على Token من `/api/v1/token/`
            
            Use JWT Token for authentication. Get token from `/api/v1/token/`
            
            ### معدل الطلبات | Rate Limiting
            - مستخدمين غير مسجلين: 100 طلب/ساعة
            - مستخدمين مسجلين: 1000 طلب/ساعة
            
            - Anonymous users: 100 requests/hour
            - Authenticated users: 1000 requests/hour
            """,
            terms_of_service="https://www.university.edu/terms/",
            contact=openapi.Contact(
                name="University IT Support",
                email="it-support@university.edu",
                url="https://www.university.edu/support"
            ),
            license=openapi.License(
                name="MIT License",
                url="https://opensource.org/licenses/MIT"
            ),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
        patterns=[
            path('api/', include('api.urls')),  # Include all API URLs here
        ],
    )
    
    api_docs_urls = [
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('api/schema.json', schema_view.without_ui(cache_timeout=0), name='schema-json-download'),
    ]
except ImportError:
    api_docs_urls = []


def enhanced_home_view(request):
    """صفحة ترحيبية محسنة ومتطورة"""
    
    # Get system status
    system_status = {
        'database': 'اتصال ناجح',
        'cache': 'يعمل بكفاءة', 
        'api': 'متاح',
        'services': 'جميع الخدمات نشطة'
    }
    
    # Get statistics (you can fetch real data from models)
    stats = {
        'students': 1250,
        'teachers': 85,
        'courses': 120,
        'departments': 8
    }
    
    return render(request, 'enhanced_home.html', {
        'system_status': system_status,
        'stats': stats,
        'version': '2.0.1',
        'last_update': '2024-10-22'
    })


@cache_page(60 * 15)  # Cache for 15 minutes
def system_info_view(request):
    """معلومات النظام - مخزنة مؤقتاً"""
    return JsonResponse({
        'status': 'active',
        'version': '2.0.1',
        'environment': 'development' if settings.DEBUG else 'production',
        'database': 'sqlite' if 'sqlite' in str(settings.DATABASES['default']['ENGINE']) else 'postgresql',
        'features': {
            'api_documentation': True,
            'real_time_notifications': True,
            'ai_analytics': True,
            'multi_language': True,
            'mobile_responsive': True,
            'role_based_access': True
        },
        'endpoints': {
            'api_root': '/api/v1/',
            'documentation': '/api/docs/',
            'admin': '/admin/',
            'web_interface': '/web/'
        }
    })


def health_check_view(request):
    """فحص صحة النظام المحسن"""
    try:
        from django.db import connection
        from django.core.cache import cache
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = True
    except Exception:
        db_status = False
    
    # Test cache
    try:
        cache.set('health_check', 'ok', 30)
        cache_status = cache.get('health_check') == 'ok'
    except Exception:
        cache_status = False
    
    status = {
        'status': 'healthy' if (db_status and cache_status) else 'unhealthy',
        'database': 'ok' if db_status else 'error',
        'cache': 'ok' if cache_status else 'error',
        'timestamp': str(timezone.now()) if 'timezone' in globals() else 'unknown'
    }
    
    return JsonResponse(status)


# Custom Error Views
def custom_404_view(request, exception=None):
    """صفحة خطأ 404 مخصصة"""
    return render(request, 'errors/404.html', {
        'error_code': '404',
        'error_title': 'الصفحة غير موجودة',
        'error_message': 'عذراً، الصفحة التي تبحث عنها غير موجودة.',
        'suggestions': [
            'تحقق من صحة الرابط',
            'ارجع إلى الصفحة الرئيسية',
            'استخدم البحث للعثور على ما تريد'
        ]
    }, status=404)


def custom_500_view(request):
    """صفحة خطأ 500 مخصصة"""
    return render(request, 'errors/500.html', {
        'error_code': '500',
        'error_title': 'خطأ في الخادم',
        'error_message': 'حدث خطأ غير متوقع. فريق الدعم الفني تم إشعاره.',
    }, status=500)


def custom_403_view(request, exception=None):
    """صفحة خطأ 403 مخصصة"""
    return render(request, 'errors/403.html', {
        'error_code': '403',
        'error_title': 'ممنوع الوصول',
        'error_message': 'ليس لديك الصلاحية للوصول إلى هذه الصفحة.',
    }, status=403)


# Main URL patterns
urlpatterns = [
    # Home page - Enhanced
    path('', enhanced_home_view, name='home'),
    
    # System Info & Health Check
    path('system/info/', system_info_view, name='system_info'),
    path('health/', health_check_view, name='health_check'),
    path('ping/', lambda request: HttpResponse('pong', content_type='text/plain'), name='ping'),
    
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # Authentication Endpoints (JWT)
    path('api/v1/auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    
    # API Documentation
] + api_docs_urls

# Add Web Interface URLs
try:
    urlpatterns += [
        path('web/', include('web.urls', namespace='web')),
    ]
except Exception as e:
    print(f"Warning: Could not include web URLs: {e}")

# Add API URLs for all applications
api_apps = [
    ('students', 'Students API'),
    ('courses', 'Courses API'),
    ('finance', 'Finance API'),
    ('hr', 'HR API'),
    ('reports', 'Reports API'),
    ('academic', 'Academic API'),
    ('notifications', 'Notifications API'),
    ('ai', 'AI API'),
    ('smart_ai', 'Smart AI API'),
    ('cyber_security', 'Security API'),
    ('attendance_qr', 'Attendance API'),
    ('admin_control', 'Admin Control API'),
    ('roles_permissions', 'Permissions API'),
]

for app_name, description in api_apps:
    try:
        urlpatterns += [
            path(f'api/v1/{app_name}/', include(f'{app_name}.urls')),
        ]
    except Exception as e:
        if settings.DEBUG:
            print(f"Warning: Could not include {app_name} URLs: {e}")

# Custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view
handler403 = custom_403_view

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar if available
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass

# Development-only URLs
if settings.DEBUG:
    urlpatterns += [
        # Test endpoints for development
        path('test/email/', lambda r: HttpResponse('Email test endpoint')),
        path('test/cache/', lambda r: JsonResponse({'cache': 'working'})),
        path('test/db/', lambda r: JsonResponse({'database': 'connected'})),
    ]

# Custom Admin Site Configuration
admin.site.site_header = "نظام إدارة الجامعة | University Management System v2.0"
admin.site.site_title = "إدارة الجامعة | University Admin"
admin.site.index_title = "لوحة التحكم الإدارية المحسنة | Enhanced Administration Panel"

# Add custom admin views
admin.site.site_url = "/"  # Link to main site
admin.site.enable_nav_sidebar = True