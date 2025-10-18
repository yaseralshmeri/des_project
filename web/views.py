"""
Web interface views for University Management System
واجهات الويب لنظام إدارة الجامعة
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from students.models import User, Student, Department
from courses.models import Course, CourseOffering
from academic.models import Enrollment, AcademicYear, Semester
from finance.models import StudentFee, Payment
from notifications.models import Notification


def home_view(request):
    """Home page - redirect based on user role"""
    if request.user.is_authenticated:
        return redirect('web:dashboard')
    return render(request, 'web/home.html')


def login_view(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('web:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'مرحباً بك، {user.get_full_name()}!')
            return redirect('web:dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'web/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('web:home')


@login_required
def dashboard_view(request):
    """Main dashboard - role-based content"""
    user = request.user
    context = {
        'user': user,
        'current_date': timezone.now(),
    }
    
    # Get current academic year and semester
    try:
        current_year = AcademicYear.objects.get(is_current=True)
        current_semester = Semester.objects.get(is_current=True)
        context.update({
            'current_year': current_year,
            'current_semester': current_semester,
        })
    except:
        pass
    
    if user.is_student:
        return student_dashboard(request, context)
    elif user.is_teacher:
        return teacher_dashboard(request, context)
    elif user.is_staff_member or user.is_admin:
        return admin_dashboard(request, context)
    
    return render(request, 'web/dashboard.html', context)


def student_dashboard(request, context):
    """Student-specific dashboard"""
    try:
        student = Student.objects.get(user=request.user)
        context['student'] = student
        
        # Get student enrollments
        enrollments = Enrollment.objects.filter(student=student).select_related('course', 'semester')
        context['enrollments'] = enrollments[:5]  # Latest 5
        
        # Get student fees
        fees = StudentFee.objects.filter(student=student).order_by('-created_at')
        context['fees'] = fees[:3]  # Latest 3
        
        # Get recent notifications
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
        context['notifications'] = notifications
        
    except Student.DoesNotExist:
        messages.warning(request, 'لم يتم العثور على ملف الطالب')
    
    return render(request, 'web/student_dashboard.html', context)


def teacher_dashboard(request, context):
    """Teacher-specific dashboard"""
    # Get courses taught by this teacher
    courses = CourseOffering.objects.filter(instructor=request.user)
    context['courses'] = courses
    
    # Get students count
    total_students = sum(course.current_enrollment for course in courses)
    context['total_students'] = total_students
    
    return render(request, 'web/teacher_dashboard.html', context)


def admin_dashboard(request, context):
    """Admin/Staff dashboard with statistics"""
    # Get statistics
    stats = {
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
        'active_enrollments': Enrollment.objects.filter(status='ENROLLED').count(),
    }
    context['stats'] = stats
    
    # Recent activities
    recent_enrollments = Enrollment.objects.select_related(
        'student__user', 'course'
    ).order_by('-enrollment_date')[:5]
    context['recent_enrollments'] = recent_enrollments
    
    # Financial overview
    pending_fees = StudentFee.objects.filter(status='PENDING').aggregate(
        total=Count('id')
    )['total']
    context['pending_fees'] = pending_fees
    
    return render(request, 'web/admin_dashboard.html', context)


@login_required
def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.save()
        
        messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
        return redirect('web:profile')
    
    context = {'user': request.user}
    if hasattr(request.user, 'student_profile'):
        context['student'] = request.user.student_profile
    
    return render(request, 'web/profile.html', context)


@login_required
def courses_view(request):
    """Courses listing page"""
    courses = Course.objects.all()
    
    # Filter by department if specified
    department_id = request.GET.get('department')
    if department_id:
        courses = courses.filter(department_id=department_id)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        courses = courses.filter(
            Q(name__icontains=search) | 
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    departments = Department.objects.all()
    
    context = {
        'courses': courses,
        'departments': departments,
        'current_department': department_id,
        'search_query': search,
    }
    
    return render(request, 'web/courses.html', context)


# API endpoint for AJAX requests
@login_required
def api_notifications(request):
    """Get user notifications via AJAX"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({'notifications': data})


@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id, 
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})