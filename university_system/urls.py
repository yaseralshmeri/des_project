"""
University Management System URL Configuration
Unified and optimized URL routing for the University Management System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Conditional import for API documentation
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    
    # API Documentation Setup
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
    
    # API Documentation URLs
    api_docs_urls = [
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ]
except ImportError:
    # If drf_yasg is not installed, provide empty list
    api_docs_urls = []


def root_redirect(request):
    """
    Redirect root URL to appropriate page based on user authentication status
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('/web/enhanced/dashboard/')
    return HttpResponseRedirect('/web/enhanced/')


# Core URL patterns
urlpatterns = [
    # Root redirect
    path('', root_redirect, name='root'),
    
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', include('health_check.urls')),
    
    # JWT Authentication Endpoints
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Web Interface
    path('', include('web.urls')),
    
    # API Endpoints
    path('api/v1/students/', include('students.urls')),
    path('api/v1/courses/', include('courses.urls')),
    path('api/v1/academic/', include('academic.urls')),
    path('api/v1/finance/', include('finance.urls')),
    path('api/v1/hr/', include('hr.urls')),
    path('api/v1/reports/', include('reports.urls')),
    path('api/v1/ai/', include('ai.urls')),
    # path('api/v1/notifications/', include('notifications.urls')),  # Add when URLs are available
    
    # Authentication API
    path('api/v1/auth/', include('rest_framework.urls')),
] + api_docs_urls

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
admin.site.site_url = "/dashboard/"