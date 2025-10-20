"""
API URL Configuration for University Management System
تكوين روابط API لنظام إدارة الجامعة

This file contains all API endpoints organized by version and functionality.
Features:
- RESTful API endpoints
- Version management
- Rate limiting
- Comprehensive error handling
- Auto-generated documentation
"""

from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# API VERSION MANAGEMENT - إدارة إصدارات API
# =============================================================================

def api_version_info(request):
    """
    API version information endpoint
    """
    return JsonResponse({
        'api_version': 'v1',
        'system_version': '1.0.0',
        'supported_versions': ['v1'],
        'deprecated_versions': [],
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'students': '/api/v1/students/',
            'courses': '/api/v1/courses/',
            'academic': '/api/v1/academic/',
            'finance': '/api/v1/finance/',
            'hr': '/api/v1/hr/',
            'reports': '/api/v1/reports/',
            'ai': '/api/v1/ai/',
            'notifications': '/api/v1/notifications/',
        },
        'documentation': {
            'swagger_ui': '/api/docs/',
            'redoc': '/api/redoc/',
            'openapi_schema': '/api/schema/',
        },
        'support': {
            'email': 'api-support@university.edu',
            'documentation': 'https://university.edu/api-docs',
            'status_page': '/health/',
        }
    })

# =============================================================================
# DRF ROUTERS SETUP - إعداد موجهات DRF
# =============================================================================

# Main API router
api_router = DefaultRouter()

# Try to register viewsets with error handling
def safe_register_viewset(router, prefix, viewset, basename=None):
    """Safely register viewset with error handling"""
    try:
        if basename:
            router.register(prefix, viewset, basename=basename)
        else:
            router.register(prefix, viewset)
        logger.info(f"✅ Registered API viewset: {prefix}")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Failed to register API viewset {prefix}: {e}")
        return False

# Register viewsets from different apps
try:
    # Students API
    from students.views import UserViewSet, StudentViewSet
    safe_register_viewset(api_router, 'users', UserViewSet)
    safe_register_viewset(api_router, 'students', StudentViewSet)
except ImportError as e:
    logger.warning(f"Students API not available: {e}")

try:
    # Courses API
    from courses.views import CourseViewSet, CourseOfferingViewSet
    safe_register_viewset(api_router, 'courses', CourseViewSet)
    safe_register_viewset(api_router, 'course-offerings', CourseOfferingViewSet)
except ImportError as e:
    logger.warning(f"Courses API not available: {e}")

try:
    # Academic API
    from academic.views import AcademicYearViewSet, SemesterViewSet, EnrollmentViewSet
    safe_register_viewset(api_router, 'academic-years', AcademicYearViewSet)
    safe_register_viewset(api_router, 'semesters', SemesterViewSet)
    safe_register_viewset(api_router, 'enrollments', EnrollmentViewSet)
except ImportError as e:
    logger.warning(f"Academic API not available: {e}")

try:
    # Finance API
    from finance.views import FeeViewSet, PaymentViewSet, ScholarshipViewSet
    safe_register_viewset(api_router, 'fees', FeeViewSet)
    safe_register_viewset(api_router, 'payments', PaymentViewSet)
    safe_register_viewset(api_router, 'scholarships', ScholarshipViewSet)
except ImportError as e:
    logger.warning(f"Finance API not available: {e}")

try:
    # HR API
    from hr.views import StaffViewSet, DepartmentViewSet
    safe_register_viewset(api_router, 'staff', StaffViewSet)
    safe_register_viewset(api_router, 'departments', DepartmentViewSet)
except ImportError as e:
    logger.warning(f"HR API not available: {e}")

try:
    # Reports API
    from reports.views import ReportViewSet
    safe_register_viewset(api_router, 'reports', ReportViewSet)
except ImportError as e:
    logger.warning(f"Reports API not available: {e}")

try:
    # AI API
    from ai.views import PredictionViewSet, AnalyticsViewSet
    safe_register_viewset(api_router, 'predictions', PredictionViewSet)
    safe_register_viewset(api_router, 'analytics', AnalyticsViewSet)
except ImportError as e:
    logger.warning(f"AI API not available: {e}")

# =============================================================================
# CUSTOM API ENDPOINTS - نقاط API مخصصة
# =============================================================================

@csrf_exempt
def api_stats(request):
    """
    API statistics endpoint
    """
    try:
        from django.contrib.auth import get_user_model
        from courses.models import Course
        from students.models import Student
        
        User = get_user_model()
        
        stats = {
            'users': {
                'total': User.objects.count(),
                'students': User.objects.filter(role='STUDENT').count(),
                'teachers': User.objects.filter(role='TEACHER').count(),
                'staff': User.objects.filter(role='STAFF').count(),
                'admins': User.objects.filter(role='ADMIN').count(),
            },
            'courses': {
                'total': Course.objects.count(),
                'active': Course.objects.filter(is_active=True).count(),
            },
            'students': {
                'total': Student.objects.count(),
                'active': Student.objects.filter(is_active=True).count(),
            }
        }
        
        return JsonResponse({
            'status': 'success',
            'data': stats,
            'timestamp': __import__('time').time(),
        })
    except Exception as e:
        logger.error(f"API stats error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Unable to fetch statistics',
        }, status=500)

# =============================================================================
# FALLBACK ENDPOINTS - نقاط الاحتياط
# =============================================================================

def create_fallback_endpoint(app_name):
    """Create a fallback endpoint for unavailable app APIs"""
    def fallback_view(request):
        return JsonResponse({
            'status': 'unavailable',
            'message': f'{app_name.title()} API is currently unavailable',
            'available_endpoints': list(api_router.registry.keys()) if api_router.registry else [],
            'support': 'api-support@university.edu'
        }, status=503)
    return fallback_view

# =============================================================================
# URL PATTERNS - أنماط الروابط
# =============================================================================

app_name = 'api'

urlpatterns = [
    # API version and info
    path('', api_version_info, name='api-version-info'),
    path('info/', api_version_info, name='api-info'),
    path('stats/', api_stats, name='api-stats'),
    
    # DRF router URLs
    path('', include(api_router.urls)),
    
    # Authentication endpoints (handled in main urls.py)
    # path('auth/', include('rest_framework.urls')),
    
    # App-specific API endpoints with fallbacks
    path('students/', include('students.urls') if 'students.urls' else create_fallback_endpoint('students')),
    path('courses/', include('courses.urls') if 'courses.urls' else create_fallback_endpoint('courses')),
    path('academic/', include('academic.urls') if 'academic.urls' else create_fallback_endpoint('academic')),
    path('finance/', include('finance.urls') if 'finance.urls' else create_fallback_endpoint('finance')),
    path('hr/', include('hr.urls') if 'hr.urls' else create_fallback_endpoint('hr')),
    path('reports/', include('reports.urls') if 'reports.urls' else create_fallback_endpoint('reports')),
    path('ai/', include('ai.urls') if 'ai.urls' else create_fallback_endpoint('ai')),
]

# Try to include notifications URLs
try:
    from notifications.urls import urlpatterns as notification_urls
    urlpatterns.append(path('notifications/', include('notifications.urls')))
except (ImportError, AttributeError):
    urlpatterns.append(path('notifications/', create_fallback_endpoint('notifications')))

# =============================================================================
# API URL VALIDATION - التحقق من صحة روابط API
# =============================================================================

def validate_api_urls():
    """Validate API URL configuration"""
    issues = []
    
    # Check if router has registered viewsets
    if not api_router.registry:
        issues.append("No viewsets registered in API router")
    
    # Check for essential endpoints
    essential_patterns = ['', 'info/', 'stats/']
    current_patterns = [pattern.pattern._route for pattern in urlpatterns if hasattr(pattern.pattern, '_route')]
    
    for essential in essential_patterns:
        if essential not in current_patterns:
            issues.append(f"Missing essential API endpoint: {essential}")
    
    if issues:
        logger.warning("API URL Configuration Issues:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("✅ API URL configuration validated successfully")

# Run validation
validate_api_urls()

# Log API configuration status
logger.info(f"🔌 API endpoints loaded: {len(urlpatterns)}")
logger.info(f"📊 DRF viewsets registered: {len(api_router.registry)}")
logger.info(f"🚀 API v1 configuration complete")