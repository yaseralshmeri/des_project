"""
Basic Views for University Management System
ملفات العرض الأساسية لنظام إدارة الجامعة

This file contains basic views with improved functionality and error handling.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import logging

# Import models
from students.models import User, Student
from notifications.models import Notification

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Basic home page view
    الصفحة الرئيسية الأساسية
    """
    try:
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect('web:enhanced_dashboard')
        
        return render(request, 'home.html')
        
    except Exception as e:
        logger.error(f"Error in home_view: {str(e)}")
        return render(request, 'home.html')


def login_view(request):
    """
    Enhanced login view with better error handling
    صفحة تسجيل الدخول المحسنة
    """
    if request.user.is_authenticated:
        return redirect('web:enhanced_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'يرجى إدخال اسم المستخدم وكلمة المرور')
            return render(request, 'enhanced_login.html')
        
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Log successful login
                    logger.info(f"User {username} logged in successfully")
                    
                    # Redirect based on user role
                    next_url = request.GET.get('next', 'web:enhanced_dashboard')
                    messages.success(request, f'مرحباً بك {user.get_full_name() or user.username}!')
                    
                    return redirect(next_url)
                else:
                    messages.error(request, 'حسابك غير مفعل. يرجى التواصل مع الإدارة')
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
                logger.warning(f"Failed login attempt for username: {username}")
                
        except Exception as e:
            logger.error(f"Login error for user {username}: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء تسجيل الدخول. يرجى المحاولة مرة أخرى')
    
    return render(request, 'enhanced_login.html')


@login_required
def logout_view(request):
    """
    Enhanced logout view
    صفحة تسجيل الخروج المحسنة
    """
    try:
        username = request.user.username
        logout(request)
        
        logger.info(f"User {username} logged out successfully")
        messages.success(request, 'تم تسجيل الخروج بنجاح')
        
        return redirect('web:home')
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return redirect('web:home')


@login_required
def dashboard_view(request):
    """
    Basic dashboard view - redirects to enhanced version
    لوحة التحكم الأساسية - تحويل للنسخة المحسنة
    """
    return redirect('web:enhanced_dashboard')


@login_required
def profile_view(request):
    """
    User profile view with update functionality
    عرض الملف الشخصي مع إمكانية التحديث
    """
    try:
        user = request.user
        
        if request.method == 'POST':
            # Update user profile
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            
            # Basic validation
            if not first_name or not last_name:
                messages.error(request, 'الاسم الأول والأخير مطلوبان')
                return render(request, 'profile.html', {'user': user})
            
            # Update user fields
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            user.address = address
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            
            logger.info(f"Profile updated for user {user.username}")
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            
            return redirect('web:profile')
        
        context = {
            'user': user,
        }
        
        # Add student-specific data if user is a student
        if user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            context['student'] = user.student_profile
        
        return render(request, 'profile.html', context)
        
    except Exception as e:
        logger.error(f"Error in profile_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل الملف الشخصي')
        return render(request, 'profile.html', {'user': request.user})


@login_required
def courses_view(request):
    """
    Basic courses view - redirects based on user role
    عرض المقررات الأساسي - يحول حسب دور المستخدم
    """
    if request.user.role == 'STUDENT':
        return redirect('web:my_courses')
    elif request.user.role == 'TEACHER':
        return redirect('web:teaching')
    else:
        return redirect('web:enhanced_dashboard')


@login_required
@require_http_methods(["GET"])
def api_notifications(request):
    """
    API endpoint to get user notifications
    نقطة API للحصول على إشعارات المستخدم
    """
    try:
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat(),
                'is_read': notification.is_read,
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'count': notifications.count()
        })
        
    except Exception as e:
        logger.error(f"Error in api_notifications for user {request.user.id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في تحميل الإشعارات'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    تعيين الإشعار كمقروء
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        
        notification.is_read = True
        notification.save()
        
        logger.info(f"Notification {notification_id} marked as read by user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'تم تعيين الإشعار كمقروء'
        })
        
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'الإشعار غير موجود'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في تحديث الإشعار'
        }, status=500)


def handler403(request, exception):
    """
    Custom 403 error handler
    معالج خطأ 403 المخصص
    """
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception):
    """
    Custom 404 error handler
    معالج خطأ 404 المخصص
    """
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """
    Custom 500 error handler
    معالج خطأ 500 المخصص
    """
    return render(request, 'errors/500.html', status=500)


# Context processor for global template variables
def global_context(request):
    """
    Global context processor to add common variables to all templates
    معالج السياق العام لإضافة متغيرات مشتركة لجميع القوالب
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Get unread notifications count
            unread_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            
            context['unread_notifications_count'] = unread_count
            
        except Exception as e:
            logger.error(f"Error in global_context for user {request.user.id}: {str(e)}")
            context['unread_notifications_count'] = 0
    
    return context