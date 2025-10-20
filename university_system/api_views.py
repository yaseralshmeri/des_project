"""
Enhanced API Views for University Management System
واجهات API محسنة لنظام إدارة الجامعة

This file contains enhanced API views with comprehensive error handling,
authentication, permissions, filtering, and advanced features.
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.conf import settings

from rest_framework import status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)
User = get_user_model()


# =============================================================================
# CUSTOM PAGINATION CLASSES - فئات الترقيم المخصصة
# =============================================================================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class with customizable page size"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination for large datasets"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


# =============================================================================
# CUSTOM PERMISSION CLASSES - فئات الصلاحيات المخصصة
# =============================================================================

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsTeacherOrReadOnly(permissions.BasePermission):
    """Custom permission for teacher-specific operations"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return request.user.is_authenticated and (
            request.user.is_teacher or request.user.is_admin or request.user.is_staff_member
        )


class IsStudentOwnerOrTeacher(permissions.BasePermission):
    """Permission for student data access"""
    
    def has_object_permission(self, request, view, obj):
        # Students can only access their own data
        if request.user.is_student:
            if hasattr(obj, 'user'):
                return obj.user == request.user
            elif hasattr(obj, 'student'):
                return obj.student.user == request.user
        
        # Teachers and admins can access all data
        return request.user.is_teacher or request.user.is_admin or request.user.is_staff_member


# =============================================================================
# SYSTEM STATUS AND HEALTH API VIEWS - واجهات حالة النظام والصحة
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def system_status(request):
    """
    Get system status and health information
    الحصول على معلومات حالة النظام والصحة
    """
    try:
        # Get cached health status
        health_status = cache.get('system_health_status', {})
        
        # Basic system info
        system_info = {
            'status': 'operational',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
            'maintenance_mode': cache.get('maintenance_mode', False)
        }
        
        # Database check
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            system_info['database'] = 'healthy'
        except Exception:
            system_info['database'] = 'unhealthy'
            system_info['status'] = 'degraded'
        
        # Cache check
        try:
            cache.set('health_check', 'ok', 30)
            cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'unhealthy'
            system_info['cache'] = cache_status
        except Exception:
            system_info['cache'] = 'unhealthy'
            system_info['status'] = 'degraded'
        
        # User statistics
        if request.user.is_authenticated and (request.user.is_admin or request.user.is_staff_member):
            system_info['user_stats'] = {
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
                'online_users': len(cache.get('online_users', []))
            }
        
        return Response(system_info)
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return Response({
            'status': 'error',
            'message': 'Unable to check system status',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def detailed_system_info(request):
    """
    Get detailed system information (admin only)
    الحصول على معلومات النظام المفصلة (للمديرين فقط)
    """
    try:
        from django.db import connection
        import sys
        import platform
        
        system_info = {
            'timestamp': timezone.now().isoformat(),
            'python_version': sys.version,
            'platform': platform.platform(),
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'database_info': {},
            'installed_apps': len(settings.INSTALLED_APPS),
            'middleware': len(settings.MIDDLEWARE),
            'cache_backend': str(cache.__class__),
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'static_url': settings.STATIC_URL,
            'media_url': settings.MEDIA_URL
        }
        
        # Database information
        db_info = connection.get_connection_params()
        system_info['database_info'] = {
            'engine': connection.vendor,
            'name': db_info.get('database', 'Unknown'),
            'host': db_info.get('host', 'localhost'),
            'port': db_info.get('port', 'default')
        }
        
        # Recent activity
        recent_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(hours=24)
        ).count()
        system_info['recent_activity'] = {
            'users_last_24h': recent_users,
            'active_sessions': cache.get('active_sessions_count', 0)
        }
        
        return Response(system_info)
        
    except Exception as e:
        logger.error(f"Detailed system info failed: {e}")
        return Response({
            'error': 'Unable to retrieve system information'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# DASHBOARD API VIEWS - واجهات لوحة التحكم
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics based on user role
    الحصول على إحصائيات لوحة التحكم حسب دور المستخدم
    """
    try:
        user = request.user
        stats = {
            'timestamp': timezone.now().isoformat(),
            'user_role': user.role if hasattr(user, 'role') else 'unknown'
        }
        
        # Role-based statistics
        if user.is_student:
            stats.update(get_student_dashboard_stats(user))
        elif user.is_teacher:
            stats.update(get_teacher_dashboard_stats(user))
        elif user.is_admin or user.is_staff_member:
            stats.update(get_admin_dashboard_stats(user))
        else:
            stats.update(get_general_dashboard_stats())
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Dashboard stats failed: {e}")
        return Response({
            'error': 'Unable to retrieve dashboard statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_student_dashboard_stats(user):
    """Get statistics for student dashboard"""
    try:
        from students.models import Student
        from academic.models import Enrollment, Grade
        
        student = Student.objects.get(user=user)
        enrollments = Enrollment.objects.filter(student=student)
        grades = Grade.objects.filter(enrollment__student=student)
        
        return {
            'total_courses': enrollments.count(),
            'completed_courses': grades.count(),
            'current_gpa': round(grades.aggregate(avg=Avg('points'))['points__avg'] or 0, 2),
            'total_credits': enrollments.aggregate(sum=Sum('course__credits'))['course__credits__sum'] or 0,
            'pending_assignments': 0,  # Implement based on your assignment model
            'upcoming_exams': 0,       # Implement based on your exam model
        }
    except Exception as e:
        logger.error(f"Student dashboard stats error: {e}")
        return {}


def get_teacher_dashboard_stats(user):
    """Get statistics for teacher dashboard"""
    try:
        from courses.models import Course
        from academic.models import Enrollment
        
        courses = Course.objects.filter(instructor=user)
        total_students = Enrollment.objects.filter(course__in=courses).count()
        
        return {
            'total_courses': courses.count(),
            'active_courses': courses.filter(is_active=True).count(),
            'total_students': total_students,
            'pending_grades': 0,  # Implement based on your grading system
            'upcoming_classes': 0,  # Implement based on your schedule model
        }
    except Exception as e:
        logger.error(f"Teacher dashboard stats error: {e}")
        return {}


def get_admin_dashboard_stats(user):
    """Get statistics for admin dashboard"""
    try:
        from students.models import Student
        from courses.models import Course
        from academic.models import Enrollment
        
        return {
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.filter(is_active=True).count(),
            'total_teachers': User.objects.filter(role='TEACHER').count(),
            'total_departments': 12,  # Implement based on your department model
            'total_enrollments': Enrollment.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
        }
    except Exception as e:
        logger.error(f"Admin dashboard stats error: {e}")
        return {}


def get_general_dashboard_stats():
    """Get general statistics for unknown roles"""
    return {
        'message': 'Welcome to University Management System',
        'features': [
            'Student Management',
            'Course Management', 
            'Academic Records',
            'Financial Management',
            'Reporting System'
        ]
    }


# =============================================================================
# USER MANAGEMENT API VIEWS - واجهات إدارة المستخدمين
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile information
    الحصول على معلومات الملف الشخصي للمستخدم الحالي
    """
    try:
        user = request.user
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'role': getattr(user, 'role', 'unknown'),
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
        
        # Add role-specific information
        if hasattr(user, 'role'):
            if user.is_student:
                try:
                    from students.models import Student
                    student = Student.objects.get(user=user)
                    profile_data.update({
                        'student_id': student.student_id,
                        'department': student.department.name if student.department else None,
                        'year_of_study': getattr(student, 'year_of_study', None),
                        'gpa': getattr(student, 'gpa', 0.0),
                    })
                except:
                    pass
            elif user.is_teacher:
                try:
                    from courses.models import Course
                    courses_count = Course.objects.filter(instructor=user).count()
                    profile_data.update({
                        'courses_teaching': courses_count,
                        'department': getattr(user, 'department', None),
                    })
                except:
                    pass
        
        return Response(profile_data)
        
    except Exception as e:
        logger.error(f"User profile retrieval failed: {e}")
        return Response({
            'error': 'Unable to retrieve user profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update current user profile
    تحديث الملف الشخصي للمستخدم الحالي
    """
    try:
        user = request.user
        data = request.data
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            }
        })
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        return Response({
            'error': 'Unable to update profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# SEARCH AND FILTERING API VIEWS - واجهات البحث والتصفية
# =============================================================================

class UniversalSearchView(APIView):
    """
    Universal search across all models
    البحث الشامل عبر جميع النماذج
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({
                'error': 'Search query must be at least 2 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            results = {
                'query': query,
                'results': {},
                'total_count': 0
            }
            
            # Search users
            if request.user.is_admin or request.user.is_staff_member:
                users = User.objects.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(username__icontains=query) |
                    Q(email__icontains=query)
                ).select_related()[:10]
                
                results['results']['users'] = [{
                    'id': user.id,
                    'name': user.get_full_name(),
                    'username': user.username,
                    'email': user.email,
                    'role': getattr(user, 'role', 'unknown'),
                    'type': 'user'
                } for user in users]
            
            # Search courses
            try:
                from courses.models import Course
                courses = Course.objects.filter(
                    Q(name__icontains=query) |
                    Q(code__icontains=query) |
                    Q(description__icontains=query)
                ).select_related('department', 'instructor')[:10]
                
                results['results']['courses'] = [{
                    'id': course.id,
                    'name': course.name,
                    'code': course.code,
                    'instructor': course.instructor.get_full_name() if course.instructor else None,
                    'department': course.department.name if course.department else None,
                    'type': 'course'
                } for course in courses]
            except:
                results['results']['courses'] = []
            
            # Search students (for teachers and admins)
            if request.user.is_teacher or request.user.is_admin or request.user.is_staff_member:
                try:
                    from students.models import Student
                    students = Student.objects.filter(
                        Q(user__first_name__icontains=query) |
                        Q(user__last_name__icontains=query) |
                        Q(student_id__icontains=query)
                    ).select_related('user', 'department')[:10]
                    
                    results['results']['students'] = [{
                        'id': student.id,
                        'name': student.user.get_full_name(),
                        'student_id': student.student_id,
                        'department': student.department.name if student.department else None,
                        'type': 'student'
                    } for student in students]
                except:
                    results['results']['students'] = []
            
            # Calculate total count
            results['total_count'] = sum(
                len(result_list) for result_list in results['results'].values()
            )
            
            return Response(results)
            
        except Exception as e:
            logger.error(f"Universal search failed: {e}")
            return Response({
                'error': 'Search operation failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# ANALYTICS AND REPORTING API VIEWS - واجهات التحليلات والتقارير
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """
    Get analytics overview based on user permissions
    الحصول على نظرة عامة على التحليلات حسب صلاحيات المستخدم
    """
    try:
        user = request.user
        time_range = request.query_params.get('range', '30')  # days
        
        try:
            days = int(time_range)
        except ValueError:
            days = 30
        
        start_date = timezone.now() - timedelta(days=days)
        
        analytics = {
            'time_range': f'{days} days',
            'start_date': start_date.isoformat(),
            'end_date': timezone.now().isoformat(),
        }
        
        if user.is_admin or user.is_staff_member:
            # Admin analytics
            analytics.update({
                'user_registrations': get_user_registration_analytics(start_date),
                'course_enrollments': get_enrollment_analytics(start_date),
                'system_usage': get_system_usage_analytics(start_date),
                'performance_metrics': get_performance_analytics(start_date)
            })
        
        elif user.is_teacher:
            # Teacher analytics
            analytics.update({
                'course_analytics': get_teacher_course_analytics(user, start_date),
                'student_performance': get_teacher_student_analytics(user, start_date)
            })
        
        elif user.is_student:
            # Student analytics
            analytics.update({
                'academic_progress': get_student_academic_analytics(user, start_date),
                'course_performance': get_student_course_analytics(user, start_date)
            })
        
        return Response(analytics)
        
    except Exception as e:
        logger.error(f"Analytics overview failed: {e}")
        return Response({
            'error': 'Unable to retrieve analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_user_registration_analytics(start_date):
    """Get user registration analytics"""
    try:
        return {
            'new_users': User.objects.filter(date_joined__gte=start_date).count(),
            'active_users': User.objects.filter(
                last_login__gte=start_date, is_active=True
            ).count(),
            'user_distribution': {
                'students': User.objects.filter(role='STUDENT').count(),
                'teachers': User.objects.filter(role='TEACHER').count(),
                'staff': User.objects.filter(role='STAFF').count(),
                'admins': User.objects.filter(role='ADMIN').count(),
            }
        }
    except Exception as e:
        logger.error(f"User registration analytics error: {e}")
        return {}


def get_enrollment_analytics(start_date):
    """Get enrollment analytics"""
    try:
        from academic.models import Enrollment
        return {
            'new_enrollments': Enrollment.objects.filter(date_enrolled__gte=start_date).count(),
            'total_enrollments': Enrollment.objects.count(),
        }
    except Exception as e:
        logger.error(f"Enrollment analytics error: {e}")
        return {}


def get_system_usage_analytics(start_date):
    """Get system usage analytics"""
    try:
        # This would require session tracking or activity logging
        return {
            'active_sessions': cache.get('active_sessions_count', 0),
            'page_views': cache.get('total_page_views', 0),
            'api_calls': cache.get('total_api_calls', 0),
        }
    except Exception as e:
        logger.error(f"System usage analytics error: {e}")
        return {}


def get_performance_analytics(start_date):
    """Get performance analytics"""
    try:
        return {
            'average_response_time': cache.get('avg_response_time', 0.0),
            'error_rate': cache.get('error_rate', 0.0),
            'uptime_percentage': cache.get('uptime_percentage', 99.9),
        }
    except Exception as e:
        logger.error(f"Performance analytics error: {e}")
        return {}


def get_teacher_course_analytics(user, start_date):
    """Get teacher-specific course analytics"""
    try:
        from courses.models import Course
        from academic.models import Enrollment
        
        courses = Course.objects.filter(instructor=user)
        return {
            'total_courses': courses.count(),
            'active_courses': courses.filter(is_active=True).count(),
            'total_students': Enrollment.objects.filter(course__in=courses).count(),
        }
    except Exception as e:
        logger.error(f"Teacher course analytics error: {e}")
        return {}


def get_teacher_student_analytics(user, start_date):
    """Get teacher-specific student analytics"""
    try:
        from academic.models import Grade, Enrollment
        
        enrollments = Enrollment.objects.filter(course__instructor=user)
        grades = Grade.objects.filter(enrollment__in=enrollments)
        
        return {
            'students_taught': enrollments.values('student').distinct().count(),
            'average_grade': round(grades.aggregate(avg=Avg('points'))['points__avg'] or 0, 2),
            'pass_rate': round(
                (grades.filter(points__gte=60).count() / grades.count() * 100) 
                if grades.count() > 0 else 0, 2
            )
        }
    except Exception as e:
        logger.error(f"Teacher student analytics error: {e}")
        return {}


def get_student_academic_analytics(user, start_date):
    """Get student-specific academic analytics"""
    try:
        from students.models import Student
        from academic.models import Grade, Enrollment
        
        student = Student.objects.get(user=user)
        enrollments = Enrollment.objects.filter(student=student)
        grades = Grade.objects.filter(enrollment__student=student)
        
        return {
            'total_courses': enrollments.count(),
            'completed_courses': grades.count(),
            'current_gpa': round(grades.aggregate(avg=Avg('points'))['points__avg'] or 0, 2),
            'credits_earned': grades.filter(points__gte=60).aggregate(
                sum=Sum('enrollment__course__credits')
            )['enrollment__course__credits__sum'] or 0
        }
    except Exception as e:
        logger.error(f"Student academic analytics error: {e}")
        return {}


def get_student_course_analytics(user, start_date):
    """Get student-specific course analytics"""
    try:
        from students.models import Student
        from academic.models import Grade
        
        student = Student.objects.get(user=user)
        recent_grades = Grade.objects.filter(
            enrollment__student=student,
            date_recorded__gte=start_date
        ).order_by('-date_recorded')[:5]
        
        return {
            'recent_grades': [{
                'course': grade.enrollment.course.name,
                'grade': grade.points,
                'date': grade.date_recorded.isoformat()
            } for grade in recent_grades],
            'improvement_trend': 'stable'  # Calculate based on grade history
        }
    except Exception as e:
        logger.error(f"Student course analytics error: {e}")
        return {}


# =============================================================================
# UTILITY API VIEWS - واجهات الأدوات المساعدة
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAdminUser])
def clear_cache(request):
    """
    Clear system cache (admin only)
    مسح ذاكرة التخزين المؤقت (للمديرين فقط)
    """
    try:
        cache.clear()
        logger.info(f"Cache cleared by admin user: {request.user.username}")
        return Response({
            'message': 'Cache cleared successfully',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return Response({
            'error': 'Failed to clear cache'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def maintenance_mode_status(request):
    """
    Get maintenance mode status
    الحصول على حالة وضع الصيانة
    """
    try:
        maintenance_status = {
            'maintenance_mode': cache.get('maintenance_mode', False),
            'maintenance_message': cache.get('maintenance_message', ''),
            'timestamp': timezone.now().isoformat()
        }
        return Response(maintenance_status)
    except Exception as e:
        logger.error(f"Maintenance status check failed: {e}")
        return Response({
            'error': 'Unable to check maintenance status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def toggle_maintenance_mode(request):
    """
    Toggle maintenance mode on/off
    تبديل وضع الصيانة تشغيل/إيقاف
    """
    try:
        enabled = request.data.get('enabled', False)
        message = request.data.get('message', 'System is under maintenance')
        
        if enabled:
            cache.set('maintenance_mode', True, None)
            cache.set('maintenance_message', message, None)
            action = 'enabled'
        else:
            cache.delete('maintenance_mode')
            cache.delete('maintenance_message')
            action = 'disabled'
        
        logger.info(f"Maintenance mode {action} by admin user: {request.user.username}")
        
        return Response({
            'message': f'Maintenance mode {action}',
            'maintenance_mode': enabled,
            'maintenance_message': message if enabled else '',
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Maintenance mode toggle failed: {e}")
        return Response({
            'error': 'Unable to toggle maintenance mode'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)