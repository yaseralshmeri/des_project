"""
University Management System - Main URLs Configuration
نظام إدارة الجامعة - تكوين الروابط الرئيسية
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Conditional import for API documentation
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from rest_framework import permissions
    
    schema_view = get_schema_view(
        openapi.Info(
            title="University Management System API",
            default_version='v1',
            description="Comprehensive University Management System API Documentation",
            terms_of_service="https://www.university.edu/terms/",
            contact=openapi.Contact(email="admin@university.edu"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )
    
    api_docs_urls = [
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ]
except ImportError:
    api_docs_urls = []


def home_view(request):
    """صفحة ترحيبية بسيطة"""
    return HttpResponse("""
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نظام إدارة الجامعة</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            p {
                font-size: 1.2rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            .btn {
                display: inline-block;
                padding: 12px 30px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 50px;
                transition: all 0.3s ease;
                margin: 0 10px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .features {
                margin-top: 2rem;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                text-align: center;
            }
            .feature {
                padding: 1rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .feature h3 {
                margin-top: 0;
                color: #FFD700;
            }
            .status {
                background: rgba(76, 175, 80, 0.2);
                padding: 10px 20px;
                border-radius: 20px;
                display: inline-block;
                margin-bottom: 1rem;
                border: 1px solid rgba(76, 175, 80, 0.5);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">🟢 النظام يعمل بنجاح</div>
            <h1>🎓 نظام إدارة الجامعة</h1>
            <p>نظام متكامل لإدارة جميع العمليات الأكاديمية والإدارية في الجامعة</p>
            
            <div style="margin: 2rem 0;">
                <a href="/admin/" class="btn">🔧 لوحة الإدارة</a>
                <a href="/api/docs/" class="btn">📚 توثيق API</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>👥 إدارة الطلاب</h3>
                    <p>تسجيل وإدارة بيانات الطلاب</p>
                </div>
                <div class="feature">
                    <h3>📚 إدارة المقررات</h3>
                    <p>إدارة المناهج والبرامج الأكاديمية</p>
                </div>
                <div class="feature">
                    <h3>💰 النظام المالي</h3>
                    <p>إدارة الرسوم والمدفوعات</p>
                </div>
                <div class="feature">
                    <h3>🤖 الذكاء الاصطناعي</h3>
                    <p>تحليلات ذكية وتنبؤات</p>
                </div>
                <div class="feature">
                    <h3>🔔 الإشعارات</h3>
                    <p>نظام إشعارات متطور</p>
                </div>
                <div class="feature">
                    <h3>📊 التقارير</h3>
                    <p>تقارير شاملة وإحصائيات</p>
                </div>
            </div>
            
            <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;">
                <p>تم التطوير والتحسين بواسطة الذكاء الاصطناعي ✨</p>
                <p>الإصدار: 2.0 - محدث: 2024-10-21</p>
            </div>
        </div>
    </body>
    </html>
    """)


# Main URL patterns
urlpatterns = [
    # Home page
    path('', home_view, name='home'),
    
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', lambda request: HttpResponse('OK', content_type='text/plain')),
    
    # JWT Authentication Endpoints
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Documentation
] + api_docs_urls

# Add API endpoints conditionally
try:
    urlpatterns += [
        # path('api/v1/students/', include('students.urls')),
        # path('api/v1/courses/', include('courses.urls')),
        # path('api/v1/finance/', include('finance.urls')),
    ]
except:
    pass

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

# Custom Admin Site Configuration
admin.site.site_header = "نظام إدارة الجامعة | University Management System"
admin.site.site_title = "إدارة الجامعة | University Admin"
admin.site.index_title = "لوحة التحكم الإدارية | Administration Panel"