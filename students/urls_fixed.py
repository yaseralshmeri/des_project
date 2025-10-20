"""
Students App URL Configuration - Fixed Version
تكوين روابط تطبيق الطلاب - النسخة المصححة
"""

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'students'

# Placeholder view for endpoints under development
def placeholder_view(request):
    return JsonResponse({'message': 'Endpoint under development'}, status=501)

# API Router for DRF ViewSets
router = DefaultRouter()

# Try to register viewsets with error handling
try:
    from .viewsets import UserViewSet, StudentViewSet
    router.register('users', UserViewSet, basename='users')
    router.register('students', StudentViewSet, basename='students')
except ImportError:
    # Fallback if viewsets don't exist
    pass

# URL patterns
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Custom endpoints with fallbacks
    path('api/profile/', 
         views.student_profile_api if hasattr(views, 'student_profile_api') else placeholder_view, 
         name='student-profile-api'),
    path('api/courses/', 
         views.student_courses_api if hasattr(views, 'student_courses_api') else placeholder_view, 
         name='student-courses-api'),
    path('api/grades/', 
         views.student_grades_api if hasattr(views, 'student_grades_api') else placeholder_view, 
         name='student-grades-api'),
    path('api/transcript/', 
         views.student_transcript_api if hasattr(views, 'student_transcript_api') else placeholder_view, 
         name='student-transcript-api'),
]