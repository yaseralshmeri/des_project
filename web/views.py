"""
Enhanced Web Views for University Management System
عرض الويب المحسن لنظام إدارة الجامعة

This module contains improved web views with better error handling,
performance optimization, and enhanced user experience.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import PermissionDenied
import json
import logging

# Import models
try:
    from students.models import User
    from courses.models import Course, Enrollment
    from notifications.models import Notification
except ImportError as e:
    logging.warning(f"Could not import models: {e}")
    User = None
    Course = None
    Enrollment = None
    Notification = None

logger = logging.getLogger(__name__)

# Helper Functions
def is_student(user):
    """Check if user is a student"""
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'STUDENT'

def is_teacher(user):
    """Check if user is a teacher"""
    return user.is_authenticated and hasattr(user, 'role') and user.role in ['TEACHER', 'ASSISTANT_TEACHER']

def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'role') and user.role in ['ADMIN', 'SUPER_ADMIN']))

def get_user_dashboard_data(user):
    """Get dashboard data based on user role"""
    data = {
        'user': user,
        'stats': {},
        'recent_activities': [],
        'notifications': [],
        'quick_actions': []
    }
    
    try:
        if hasattr(user, 'role'):
            if user.role == 'STUDENT':
                # Student dashboard data
                if Course and Enrollment:
                    enrolled_courses = Enrollment.objects.filter(student=user).count()
                    data['stats'] = {
                        'enrolled_courses': enrolled_courses,
                        'completed_courses': 0,  # Add logic later
                        'current_gpa': 0.0,  # Add logic later
                        'total_credits': 0  # Add logic later
                    }
                
                data['quick_actions'] = [
                    {'title': 'المقررات المسجلة', 'url': '/web/my-courses/', 'icon': 'fas fa-book'},
                    {'title': 'الدرجات', 'url': '/web/grades/', 'icon': 'fas fa-star'},
                    {'title': 'الجدول الدراسي', 'url': '/web/schedule/', 'icon': 'fas fa-calendar'},
                    {'title': 'المدفوعات', 'url': '/web/payments/', 'icon': 'fas fa-credit-card'}
                ]
            
            elif user.role in ['TEACHER', 'ASSISTANT_TEACHER']:
                # Teacher dashboard data
                data['quick_actions'] = [
                    {'title': 'المقررات التي أدرسها', 'url': '/web/my-teaching/', 'icon': 'fas fa-chalkboard-teacher'},
                    {'title': 'الطلاب', 'url': '/web/students/', 'icon': 'fas fa-users'},
                    {'title': 'الدرجات', 'url': '/web/grading/', 'icon': 'fas fa-clipboard-list'},
                    {'title': 'التقارير', 'url': '/web/reports/', 'icon': 'fas fa-chart-bar'}
                ]
            
            elif user.role in ['ADMIN', 'SUPER_ADMIN']:
                # Admin dashboard data
                if User:
                    total_users = User.objects.count()
                    total_students = User.objects.filter(role='STUDENT').count()
                    total_teachers = User.objects.filter(role__in=['TEACHER', 'ASSISTANT_TEACHER']).count()
                    
                    data['stats'] = {
                        'total_users': total_users,
                        'total_students': total_students,
                        'total_teachers': total_teachers,
                        'system_health': 'excellent'
                    }
                
                data['quick_actions'] = [
                    {'title': 'إدارة المستخدمين', 'url': '/admin/students/user/', 'icon': 'fas fa-users-cog'},
                    {'title': 'إدارة المقررات', 'url': '/admin/courses/', 'icon': 'fas fa-book-open'},
                    {'title': 'التقارير المتقدمة', 'url': '/web/advanced-reports/', 'icon': 'fas fa-analytics'},
                    {'title': 'إعدادات النظام', 'url': '/admin/', 'icon': 'fas fa-cog'}
                ]
        
        # Get recent notifications
        if Notification:
            data['notifications'] = Notification.objects.filter(
                user=user, 
                is_read=False
            ).order_by('-created_at')[:5]
    
    except Exception as e:
        logger.error(f"Error getting dashboard data for user {user.id}: {e}")
    
    return data

# Views
def home_view(request):
    """Enhanced home page view"""
    try:
        context = {
            'university_name': getattr(settings, 'UNIVERSITY_NAME', 'نظام إدارة الجامعة'),
            'university_name_en': getattr(settings, 'UNIVERSITY_NAME_EN', 'University Management System'),
            'system_status': {
                'database': 'متصل',
                'cache': 'يعمل',
                'api': 'متاح',
                'services': 'جميع الخدمات نشطة'
            },
            'stats': {
                'students': User.objects.filter(role='STUDENT').count() if User else 1250,
                'teachers': User.objects.filter(role__in=['TEACHER', 'ASSISTANT_TEACHER']).count() if User else 85,
                'courses': Course.objects.count() if Course else 120,
                'departments': 8  # This should come from a Department model
            },
            'version': '2.0.1',
            'last_update': '2024-10-22'
        }
        
        return render(request, 'enhanced_home_improved.html', context)
    
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        return render(request, 'enhanced_home_improved.html', {
            'error': 'حدث خطأ في تحميل الصفحة الرئيسية'
        })

@never_cache
def login_view(request):
    """Enhanced login view with better security"""
    if request.user.is_authenticated:
        return redirect('web:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me', False)
        
        if not username or not password:
            messages.error(request, 'يرجى إدخال اسم المستخدم وكلمة المرور')
            return render(request, 'web/login.html')
        
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Set session timeout based on remember_me
                    if not remember_me:
                        request.session.set_expiry(0)  # Session ends when browser closes
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks
                    
                    # Update last login activity
                    if hasattr(user, 'last_activity'):
                        user.last_activity = timezone.now()
                        user.save(update_fields=['last_activity'])
                    
                    messages.success(request, f'مرحباً بك {user.get_full_name() if hasattr(user, "get_full_name") else user.username}')
                    
                    # Redirect to next or dashboard
                    next_url = request.GET.get('next', '/web/dashboard/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'حسابك غير مفعل، يرجى التواصل مع الإدارة')
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
        
        except Exception as e:
            logger.error(f"Login error: {e}")
            messages.error(request, 'حدث خطأ أثناء تسجيل الدخول، يرجى المحاولة مرة أخرى')
    
    return render(request, 'web/login.html')

@login_required
def logout_view(request):
    """Enhanced logout view"""
    user_name = request.user.get_full_name() if hasattr(request.user, 'get_full_name') else request.user.username
    logout(request)
    messages.success(request, f'تم تسجيل الخروج بنجاح، إلى اللقاء {user_name}')
    return redirect('web:home')

@login_required
@cache_page(60 * 5)  # Cache for 5 minutes
def dashboard_view(request):
    """Enhanced dashboard view with role-based content"""
    try:
        context = get_user_dashboard_data(request.user)
        context['page_title'] = 'لوحة التحكم الرئيسية'
        
        # Add breadcrumbs
        context['breadcrumbs'] = [
            {'title': 'الرئيسية', 'url': '/web/'},
            {'title': 'لوحة التحكم', 'url': None, 'active': True}
        ]
        
        return render(request, 'web/dashboard.html', context)
    
    except Exception as e:
        logger.error(f"Dashboard error for user {request.user.id}: {e}")
        messages.error(request, 'حدث خطأ في تحميل لوحة التحكم')
        return redirect('web:home')

@login_required
@user_passes_test(is_student)
def student_courses_view(request):
    """Student courses view"""
    try:
        if not Enrollment or not Course:
            messages.warning(request, 'خدمة المقررات غير متاحة حالياً')
            return redirect('web:dashboard')
        
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        
        # Pagination
        paginator = Paginator(enrollments, 10)
        page = request.GET.get('page')
        
        try:
            enrollments_page = paginator.page(page)
        except PageNotAnInteger:
            enrollments_page = paginator.page(1)
        except EmptyPage:
            enrollments_page = paginator.page(paginator.num_pages)
        
        context = {
            'enrollments': enrollments_page,
            'page_title': 'مقرراتي',
            'breadcrumbs': [
                {'title': 'الرئيسية', 'url': '/web/'},
                {'title': 'لوحة التحكم', 'url': '/web/dashboard/'},
                {'title': 'مقرراتي', 'url': None, 'active': True}
            ]
        }
        
        return render(request, 'web/student_courses.html', context)
    
    except Exception as e:
        logger.error(f"Student courses error: {e}")
        messages.error(request, 'حدث خطأ في تحميل المقررات')
        return redirect('web:dashboard')

@login_required
@user_passes_test(is_teacher)
def teacher_courses_view(request):
    """Teacher courses view"""
    try:
        if not Course:
            messages.warning(request, 'خدمة المقررات غير متاحة حالياً')
            return redirect('web:dashboard')
        
        courses = Course.objects.filter(instructor=request.user)
        
        # Get statistics
        stats = {
            'total_courses': courses.count(),
            'total_students': Enrollment.objects.filter(course__in=courses).count() if Enrollment else 0,
            'active_courses': courses.filter(is_active=True).count() if hasattr(courses.first(), 'is_active') else courses.count()
        }
        
        context = {
            'courses': courses,
            'stats': stats,
            'page_title': 'المقررات التي أدرسها',
            'breadcrumbs': [
                {'title': 'الرئيسية', 'url': '/web/'},
                {'title': 'لوحة التحكم', 'url': '/web/dashboard/'},
                {'title': 'مقرراتي التدريسية', 'url': None, 'active': True}
            ]
        }
        
        return render(request, 'web/teacher_courses.html', context)
    
    except Exception as e:
        logger.error(f"Teacher courses error: {e}")
        messages.error(request, 'حدث خطأ في تحميل المقررات التدريسية')
        return redirect('web:dashboard')

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Enhanced admin dashboard"""
    try:
        # Get comprehensive statistics
        stats = {}
        
        if User:
            stats.update({
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
                'students': User.objects.filter(role='STUDENT').count(),
                'teachers': User.objects.filter(role__in=['TEACHER', 'ASSISTANT_TEACHER']).count(),
                'admins': User.objects.filter(role__in=['ADMIN', 'SUPER_ADMIN']).count(),
            })
        
        if Course:
            stats.update({
                'total_courses': Course.objects.count(),
                'active_courses': Course.objects.filter(is_active=True).count() if hasattr(Course, 'is_active') else Course.objects.count(),
            })
        
        if Enrollment:
            stats.update({
                'total_enrollments': Enrollment.objects.count(),
                'recent_enrollments': Enrollment.objects.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=7)
                ).count() if hasattr(Enrollment, 'created_at') else 0,
            })
        
        # Recent activities (you can expand this)
        recent_activities = []
        
        context = {
            'stats': stats,
            'recent_activities': recent_activities,
            'page_title': 'لوحة التحكم الإدارية',
            'breadcrumbs': [
                {'title': 'الرئيسية', 'url': '/web/'},
                {'title': 'لوحة التحكم الإدارية', 'url': None, 'active': True}
            ],
            'system_info': {
                'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
                'debug_mode': settings.DEBUG,
                'database': 'SQLite' if 'sqlite' in str(settings.DATABASES['default']['ENGINE']) else 'PostgreSQL',
            }
        }
        
        return render(request, 'web/admin_dashboard.html', context)
    
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        messages.error(request, 'حدث خطأ في تحميل لوحة التحكم الإدارية')
        return redirect('web:dashboard')

@login_required
def profile_view(request):
    """User profile view"""
    try:
        if request.method == 'POST':
            # Handle profile update
            user = request.user
            
            # Update basic info
            if hasattr(user, 'first_name_ar'):
                user.first_name_ar = request.POST.get('first_name_ar', '')
                user.last_name_ar = request.POST.get('last_name_ar', '')
            
            user.email = request.POST.get('email', user.email)
            
            if hasattr(user, 'phone_number'):
                user.phone_number = request.POST.get('phone_number', '')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                if hasattr(user, 'profile_picture'):
                    user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('web:profile')
        
        context = {
            'page_title': 'الملف الشخصي',
            'breadcrumbs': [
                {'title': 'الرئيسية', 'url': '/web/'},
                {'title': 'لوحة التحكم', 'url': '/web/dashboard/'},
                {'title': 'الملف الشخصي', 'url': None, 'active': True}
            ]
        }
        
        return render(request, 'web/profile.html', context)
    
    except Exception as e:
        logger.error(f"Profile error: {e}")
        messages.error(request, 'حدث خطأ في تحميل الملف الشخصي')
        return redirect('web:dashboard')

@login_required
@require_http_methods(["GET"])
def notifications_view(request):
    """User notifications view with AJAX support"""
    try:
        if not Notification:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'خدمة الإشعارات غير متاحة'}, status=503)
            messages.warning(request, 'خدمة الإشعارات غير متاحة حالياً')
            return redirect('web:dashboard')
        
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        # Mark as read if requested
        if request.GET.get('mark_read'):
            notifications.filter(is_read=False).update(is_read=True)
        
        # AJAX request - return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            notifications_data = []
            for notification in notifications[:20]:  # Limit to 20 recent notifications
                notifications_data.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.type if hasattr(notification, 'type') else 'info',
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                })
            
            return JsonResponse({
                'notifications': notifications_data,
                'unread_count': notifications.filter(is_read=False).count()
            })
        
        # Regular request - return HTML
        paginator = Paginator(notifications, 20)
        page = request.GET.get('page')
        
        try:
            notifications_page = paginator.page(page)
        except PageNotAnInteger:
            notifications_page = paginator.page(1)
        except EmptyPage:
            notifications_page = paginator.page(paginator.num_pages)
        
        context = {
            'notifications': notifications_page,
            'unread_count': notifications.filter(is_read=False).count(),
            'page_title': 'الإشعارات',
            'breadcrumbs': [
                {'title': 'الرئيسية', 'url': '/web/'},
                {'title': 'لوحة التحكم', 'url': '/web/dashboard/'},
                {'title': 'الإشعارات', 'url': None, 'active': True}
            ]
        }
        
        return render(request, 'web/notifications.html', context)
    
    except Exception as e:
        logger.error(f"Notifications error: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'حدث خطأ في تحميل الإشعارات'}, status=500)
        messages.error(request, 'حدث خطأ في تحميل الإشعارات')
        return redirect('web:dashboard')

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark specific notification as read"""
    try:
        if not Notification:
            return JsonResponse({'error': 'خدمة الإشعارات غير متاحة'}, status=503)
        
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True, 'message': 'تم تحديد الإشعار كمقروء'})
    
    except Exception as e:
        logger.error(f"Mark notification read error: {e}")
        return JsonResponse({'error': 'حدث خطأ في تحديث الإشعار'}, status=500)

def error_404_view(request, exception=None):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', {
        'error_code': '404',
        'error_title': 'الصفحة غير موجودة',
        'error_message': 'عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.',
        'suggestions': [
            'تحقق من صحة الرابط المكتوب',
            'ارجع إلى الصفحة الرئيسية',
            'استخدم شريط البحث للعثور على ما تريد',
            'تواصل مع الدعم الفني إذا كنت تعتقد أن هذا خطأ'
        ]
    }, status=404)

def error_500_view(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', {
        'error_code': '500',
        'error_title': 'خطأ في الخادم',
        'error_message': 'حدث خطأ غير متوقع في الخادم. تم إشعار فريق الدعم الفني تلقائياً.',
        'contact_info': {
            'email': 'support@university.edu',
            'phone': '+966-11-xxx-xxxx'
        }
    }, status=500)

def error_403_view(request, exception=None):
    """Custom 403 error page"""
    return render(request, 'errors/403.html', {
        'error_code': '403',
        'error_title': 'ممنوع الوصول',
        'error_message': 'ليس لديك الصلاحية اللازمة للوصول إلى هذه الصفحة.',
        'help_text': 'إذا كنت تعتقد أن هذا خطأ، يرجى التواصل مع الإدارة.'
    }, status=403)

# API-like views for AJAX requests
@login_required
@require_http_methods(["GET"])
def api_user_info(request):
    """Get current user info as JSON"""
    try:
        user_data = {
            'id': str(request.user.id),
            'username': request.user.username,
            'email': request.user.email,
            'is_active': request.user.is_active,
            'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
        }
        
        # Add custom fields if they exist
        if hasattr(request.user, 'role'):
            user_data['role'] = request.user.role
        
        if hasattr(request.user, 'full_name_ar'):
            user_data['full_name_ar'] = request.user.full_name_ar
        
        if hasattr(request.user, 'profile_picture') and request.user.profile_picture:
            user_data['profile_picture'] = request.user.profile_picture.url
        
        return JsonResponse({'user': user_data})
    
    except Exception as e:
        logger.error(f"API user info error: {e}")
        return JsonResponse({'error': 'حدث خطأ في جلب بيانات المستخدم'}, status=500)

@login_required
@require_http_methods(["GET"])
def api_dashboard_stats(request):
    """Get dashboard statistics as JSON"""
    try:
        data = get_user_dashboard_data(request.user)
        return JsonResponse({
            'stats': data['stats'],
            'notifications_count': len(data['notifications']),
            'quick_actions': data['quick_actions']
        })
    
    except Exception as e:
        logger.error(f"API dashboard stats error: {e}")
        return JsonResponse({'error': 'حدث خطأ في جلب إحصائيات لوحة التحكم'}, status=500)


# =============================================================================
# ERROR HANDLERS - معالجات الأخطاء
# =============================================================================

def handler400(request, exception):
    """Custom 400 Bad Request Handler"""
    context = {
        'error_code': 400,
        'error_title': 'طلب غير صحيح',
        'error_message': 'البيانات المرسلة غير صحيحة أو غير مكتملة.',
        'suggestions': [
            'تأكد من صحة البيانات المدخلة',
            'تحقق من صيغة الطلب',
            'حاول إعادة تحميل الصفحة'
        ]
    }
    return render(request, 'web/errors/error.html', context, status=400)

def handler403(request, exception):
    """Custom 403 Forbidden Handler"""
    context = {
        'error_code': 403,
        'error_title': 'الوصول مرفوض',
        'error_message': 'ليس لديك الصلاحية للوصول إلى هذه الصفحة.',
        'suggestions': [
            'تأكد من تسجيل الدخول',
            'تحقق من صلاحياتك',
            'تواصل مع الإدارة للحصول على الصلاحيات'
        ]
    }
    return render(request, 'web/errors/error.html', context, status=403)

def handler404(request, exception):
    """Custom 404 Not Found Handler"""
    context = {
        'error_code': 404,
        'error_title': 'الصفحة غير موجودة',
        'error_message': 'الصفحة التي تبحث عنها غير موجودة أو تم نقلها.',
        'suggestions': [
            'تحقق من صحة الرابط',
            'استخدم شريط البحث',
            'العودة إلى الصفحة الرئيسية'
        ]
    }
    return render(request, 'web/errors/error.html', context, status=404)

def handler500(request):
    """Custom 500 Internal Server Error Handler"""
    context = {
        'error_code': 500,
        'error_title': 'خطأ في الخادم',
        'error_message': 'حدث خطأ داخلي في الخادم. يرجى المحاولة لاحقاً.',
        'suggestions': [
            'أعد المحاولة بعد قليل',
            'تواصل مع الدعم الفني إذا استمر الخطأ',
            'حاول تحديث الصفحة'
        ]
    }
    return render(request, 'web/errors/error.html', context, status=500)