"""
Courses App URL Configuration - Fixed Version
تكوين روابط تطبيق المقررات - النسخة المصححة
"""

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'courses'

# Placeholder view for endpoints under development
def placeholder_view(request):
    return JsonResponse({'message': 'Endpoint under development'}, status=501)

# API Router for DRF ViewSets
router = DefaultRouter()

# Try to register viewsets with error handling
try:
    from .viewsets import CourseViewSet, CourseOfferingViewSet
    router.register('courses', CourseViewSet, basename='courses')
    router.register('offerings', CourseOfferingViewSet, basename='course-offerings')
except ImportError:
    # Fallback if viewsets don't exist
    pass

# URL patterns
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Custom endpoints with fallbacks
    path('api/search/', 
         views.course_search_api if hasattr(views, 'course_search_api') else placeholder_view, 
         name='course-search-api'),
    path('api/enrollment/', 
         views.course_enrollment_api if hasattr(views, 'course_enrollment_api') else placeholder_view, 
         name='course-enrollment-api'),
    path('api/schedule/', 
         views.course_schedule_api if hasattr(views, 'course_schedule_api') else placeholder_view, 
         name='course-schedule-api'),
]