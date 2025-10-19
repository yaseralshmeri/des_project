"""
Enhanced Web Views for University Management System
واجهات الويب المحسنة لنظام إدارة الجامعة
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json

from students.models import User, Student, Department
from courses.models import Course, CourseOffering
from academic.models import Enrollment, AcademicYear, Semester
from finance.models import StudentFee, Payment
from notifications.models import Notification


# Enhanced Views
def enhanced_home_view(request):
    """Enhanced home page with modern design"""
    if request.user.is_authenticated:
        return redirect('web:enhanced_dashboard')
    return render(request, 'web/enhanced_home.html')


@login_required
def enhanced_dashboard_view(request):
    """Enhanced dashboard with role-based content"""
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
        return enhanced_student_dashboard(request, context)
    elif user.is_teacher:
        return enhanced_teacher_dashboard(request, context)
    elif user.is_staff_member or user.is_admin:
        return enhanced_admin_dashboard(request, context)
    
    return render(request, 'web/enhanced_dashboard.html', context)


def enhanced_student_dashboard(request, context):
    """Enhanced student dashboard"""
    try:
        student = Student.objects.get(user=request.user)
        context['student'] = student
        
        # Get student enrollments with related data
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related('course', 'semester').prefetch_related('grades')
        context['enrollments'] = enrollments
        
        # Calculate GPA
        grades = [e.final_grade for e in enrollments if e.final_grade]
        if grades:
            context['gpa'] = sum(grades) / len(grades)
        else:
            context['gpa'] = 0.0
        
        # Get recent fees
        fees = StudentFee.objects.filter(student=student).order_by('-created_at')[:3]
        context['fees'] = fees
        
        # Calculate total pending fees
        pending_fees = StudentFee.objects.filter(
            student=student, 
            status='PENDING'
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['pending_fees'] = pending_fees
        
    except Student.DoesNotExist:
        messages.warning(request, 'لم يتم العثور على ملف الطالب')
    
    return render(request, 'web/enhanced_dashboard.html', context)


def enhanced_teacher_dashboard(request, context):
    """Enhanced teacher dashboard"""
    # Get courses taught by this teacher
    courses = CourseOffering.objects.filter(instructor=request.user)
    context['courses'] = courses
    
    # Calculate total students across all courses
    total_students = sum(course.current_enrollment for course in courses)
    context['total_students'] = total_students
    
    # Get recent enrollments for teacher's courses
    recent_enrollments = Enrollment.objects.filter(
        course__in=[c.course for c in courses]
    ).select_related('student__user').order_by('-enrollment_date')[:5]
    context['recent_enrollments'] = recent_enrollments
    
    return render(request, 'web/enhanced_dashboard.html', context)


def enhanced_admin_dashboard(request, context):
    """Enhanced admin dashboard with comprehensive stats"""
    # Get comprehensive statistics
    stats = {
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
        'active_enrollments': Enrollment.objects.filter(status='ENROLLED').count(),
        'total_fees_collected': Payment.objects.filter(
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_payments': StudentFee.objects.filter(
            status='PENDING'
        ).count(),
    }
    context['stats'] = stats
    
    # Recent activities
    recent_enrollments = Enrollment.objects.select_related(
        'student__user', 'course'
    ).order_by('-enrollment_date')[:10]
    context['recent_enrollments'] = recent_enrollments
    
    # Financial overview
    financial_stats = {
        'total_fees': StudentFee.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'collected_fees': Payment.objects.filter(
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': StudentFee.objects.filter(
            status='PENDING'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    context['financial_stats'] = financial_stats
    
    return render(request, 'web/enhanced_dashboard.html', context)


# Student-specific views
@login_required
def my_courses_view(request):
    """Student's enrolled courses"""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    student = request.user.student_profile
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course', 'semester')
    
    context = {
        'enrollments': enrollments,
        'student': student,
    }
    return render(request, 'web/my_courses.html', context)


@login_required
def my_grades_view(request):
    """Student's grades and academic progress"""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    student = request.user.student_profile
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course').prefetch_related('grades')
    
    # Calculate GPA
    total_points = 0
    total_credits = 0
    for enrollment in enrollments:
        if enrollment.final_grade:
            total_points += enrollment.final_grade * enrollment.course.credit_hours
            total_credits += enrollment.course.credit_hours
    
    gpa = total_points / total_credits if total_credits > 0 else 0
    
    context = {
        'enrollments': enrollments,
        'gpa': gpa,
        'total_credits': total_credits,
    }
    return render(request, 'web/my_grades.html', context)


@login_required
def my_schedule_view(request):
    """Student's class schedule"""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    student = request.user.student_profile
    current_enrollments = Enrollment.objects.filter(
        student=student,
        status='ENROLLED'
    ).select_related('course')
    
    context = {
        'enrollments': current_enrollments,
    }
    return render(request, 'web/my_schedule.html', context)


@login_required
def my_fees_view(request):
    """Student's fees and payment history"""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    student = request.user.student_profile
    fees = StudentFee.objects.filter(student=student).order_by('-due_date')
    payments = Payment.objects.filter(
        student_fee__student=student
    ).order_by('-payment_date')
    
    # Calculate totals
    total_fees = fees.aggregate(total=Sum('amount'))['total'] or 0
    total_paid = payments.filter(
        status='COMPLETED'
    ).aggregate(total=Sum('amount'))['total'] or 0
    pending_amount = total_fees - total_paid
    
    context = {
        'fees': fees,
        'payments': payments,
        'total_fees': total_fees,
        'total_paid': total_paid,
        'pending_amount': pending_amount,
    }
    return render(request, 'web/my_fees.html', context)


# Teacher-specific views
@login_required
def teaching_view(request):
    """Teacher's courses and classes"""
    if not request.user.is_teacher:
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    courses = CourseOffering.objects.filter(
        instructor=request.user
    ).select_related('course')
    
    context = {
        'courses': courses,
    }
    return render(request, 'web/teaching.html', context)


@login_required
def students_view(request):
    """Teacher's students across all courses"""
    if not request.user.is_teacher:
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    # Get all enrollments for teacher's courses
    teacher_courses = CourseOffering.objects.filter(
        instructor=request.user
    ).values_list('course', flat=True)
    
    enrollments = Enrollment.objects.filter(
        course__in=teacher_courses
    ).select_related('student__user', 'course')
    
    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'enrollments': page_obj,
    }
    return render(request, 'web/students.html', context)


@login_required
def grade_management_view(request):
    """Teacher's grade management interface"""
    if not request.user.is_teacher:
        messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
        return redirect('web:dashboard')
    
    # Get teacher's courses
    courses = CourseOffering.objects.filter(
        instructor=request.user
    ).select_related('course')
    
    selected_course = None
    enrollments = []
    
    if request.GET.get('course_id'):
        try:
            selected_course = courses.get(id=request.GET.get('course_id'))
            enrollments = Enrollment.objects.filter(
                course=selected_course.course
            ).select_related('student__user')
        except CourseOffering.DoesNotExist:
            messages.error(request, 'المقرر غير موجود')
    
    context = {
        'courses': courses,
        'selected_course': selected_course,
        'enrollments': enrollments,
    }
    return render(request, 'web/grade_management.html', context)


# Admin-specific views
@user_passes_test(lambda u: u.is_staff or u.is_admin)
def admin_panel_view(request):
    """Admin control panel"""
    # Comprehensive system statistics
    stats = {
        'students': {
            'total': Student.objects.count(),
            'active': Student.objects.filter(status='ACTIVE').count(),
            'new_this_month': Student.objects.filter(
                enrollment_date__gte=timezone.now() - timedelta(days=30)
            ).count(),
        },
        'courses': {
            'total': Course.objects.count(),
            'active': CourseOffering.objects.filter(
                semester__is_current=True
            ).count(),
        },
        'finances': {
            'total_fees': StudentFee.objects.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'collected': Payment.objects.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'pending': StudentFee.objects.filter(
                status='PENDING'
            ).count(),
        },
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'web/admin_panel.html', context)


@user_passes_test(lambda u: u.is_staff or u.is_admin)
def system_stats_view(request):
    """Detailed system statistics and analytics"""
    # Monthly enrollment trends
    monthly_enrollments = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = timezone.now() - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
        count = Enrollment.objects.filter(
            enrollment_date__range=[month_start, month_end]
        ).count()
        monthly_enrollments.append({
            'month': month_start.strftime('%B %Y'),
            'count': count
        })
    
    # Department statistics
    dept_stats = Department.objects.annotate(
        student_count=Count('students'),
        course_count=Count('courses')
    )
    
    context = {
        'monthly_enrollments': monthly_enrollments[::-1],  # Reverse for chronological order
        'dept_stats': dept_stats,
    }
    return render(request, 'web/system_stats.html', context)


@user_passes_test(lambda u: u.is_staff or u.is_admin)
def user_management_view(request):
    """User management interface"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Role filter
    role_filter = request.GET.get('role')
    if role_filter:
        if role_filter == 'student':
            users = users.filter(is_student=True)
        elif role_filter == 'teacher':
            users = users.filter(is_teacher=True)
        elif role_filter == 'staff':
            users = users.filter(is_staff_member=True)
        elif role_filter == 'admin':
            users = users.filter(is_admin=True)
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'users': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
    }
    return render(request, 'web/user_management.html', context)


# API endpoints
@login_required
def api_dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    user = request.user
    stats = {}
    
    if user.is_student:
        try:
            student = Student.objects.get(user=user)
            enrollments = Enrollment.objects.filter(student=student)
            stats = {
                'enrolled_courses': enrollments.count(),
                'completed_courses': enrollments.filter(status='COMPLETED').count(),
                'gpa': 3.7,  # Calculate actual GPA
                'attendance_rate': 85,  # Calculate actual attendance
            }
        except Student.DoesNotExist:
            pass
    elif user.is_teacher:
        courses = CourseOffering.objects.filter(instructor=user)
        stats = {
            'teaching_courses': courses.count(),
            'total_students': sum(c.current_enrollment for c in courses),
            'average_grade': 88,  # Calculate actual average
            'teaching_rating': 4.2,  # From evaluation system
        }
    else:
        stats = {
            'total_students': Student.objects.count(),
            'total_courses': Course.objects.count(),
            'active_enrollments': Enrollment.objects.filter(status='ENROLLED').count(),
            'pending_fees': StudentFee.objects.filter(status='PENDING').count(),
        }
    
    return JsonResponse({'stats': stats})


@login_required
def api_search(request):
    """Universal search API endpoint"""
    query = request.GET.get('q', '')
    results = []
    
    if len(query) >= 3:
        # Search students
        if request.user.is_teacher or request.user.is_staff_member or request.user.is_admin:
            students = Student.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(student_id__icontains=query)
            )[:5]
            
            for student in students:
                results.append({
                    'type': 'student',
                    'title': student.user.get_full_name(),
                    'subtitle': f'رقم الطالب: {student.student_id}',
                    'url': f'/students/{student.id}/'
                })
        
        # Search courses
        courses = Course.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:5]
        
        for course in courses:
            results.append({
                'type': 'course',
                'title': course.name,
                'subtitle': f'كود المقرر: {course.code}',
                'url': f'/courses/{course.id}/'
            })
    
    return JsonResponse({'results': results})