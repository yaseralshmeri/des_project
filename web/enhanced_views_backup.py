"""
Enhanced Views for University Management System
ملفات العرض المحسنة لنظام إدارة الجامعة

This file contains all the enhanced views with better functionality,
improved error handling, and comprehensive features.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import json
import logging

# Import models from different apps
from students.models import User, Student, Department
from courses.models import Course
from academic.models import Enrollment, Grade, Semester, AcademicYear
# from finance.models import Fee, Payment, Scholarship
from notifications.models import Notification

logger = logging.getLogger(__name__)


def enhanced_home_view(request):
    """
    Enhanced home page view with better content and statistics
    الصفحة الرئيسية المحسنة مع محتوى وإحصائيات أفضل
    """
    try:
        # Get basic statistics for the home page
        context = {
            'total_students': Student.objects.filter(status='ACTIVE').count(),
            'total_teachers': User.objects.filter(role='TEACHER', is_active=True).count(),
            'total_courses': Course.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.count(),
        }
        
        # Add cache for better performance
        cache_key = 'home_stats'
        cached_stats = cache.get(cache_key)
        
        if not cached_stats:
            cache.set(cache_key, context, 300)  # Cache for 5 minutes
        
        return render(request, 'enhanced_home.html', context)
        
    except Exception as e:
        logger.error(f"Error in enhanced_home_view: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل الصفحة الرئيسية')
        return render(request, 'enhanced_home.html', {})


@login_required
def enhanced_dashboard_view(request):
    """
    Enhanced dashboard with role-based content and real-time data
    لوحة التحكم المحسنة مع محتوى حسب الدور وبيانات فورية
    """
    try:
        user = request.user
        context = {
            'user': user,
            'current_time': timezone.now(),
        }
        
        # Role-specific dashboard content
        if user.role == 'STUDENT':
            context.update(_get_student_dashboard_data(user))
        elif user.role == 'TEACHER':
            context.update(_get_teacher_dashboard_data(user))
        elif user.role in ['ADMIN', 'STAFF']:
            context.update(_get_admin_dashboard_data(user))
        
        # Get recent notifications (limit to 5)
        recent_notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).order_by('-created_at')[:5]
        
        context['recent_notifications'] = recent_notifications
        context['unread_notifications_count'] = recent_notifications.count()
        
        return render(request, 'enhanced_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in enhanced_dashboard_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل لوحة التحكم')
        return render(request, 'enhanced_dashboard.html', {'user': request.user})


def _get_student_dashboard_data(user):
    """Get dashboard data specific to students"""
    try:
        student = user.student_profile
        
        # Get enrolled courses
        enrollments = Enrollment.objects.filter(
            student=student,
            is_active=True
        ).select_related('course')
        
        # Calculate attendance rate
        total_classes = 0
        attended_classes = 0
        for enrollment in enrollments:
            # This would typically involve attendance records
            total_classes += 20  # Assuming 20 classes per course
            attended_classes += 18  # Mock data
        
        attendance_rate = (attended_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Get pending fees (mock data for now)
        pending_fees = 15000  # Mock data
        
        return {
            'enrolled_courses_count': enrollments.count(),
            'current_gpa': float(student.gpa),
            'attendance_rate': round(attendance_rate, 1),
            'pending_fees': pending_fees,
            'enrolled_courses': enrollments[:5],  # Show only 5 recent courses
        }
        
    except Exception as e:
        logger.error(f"Error getting student dashboard data: {str(e)}")
        return {}


def _get_teacher_dashboard_data(user):
    """Get dashboard data specific to teachers"""
    try:
        # Get courses taught by this teacher
        teaching_courses = Course.objects.filter(
            instructor=user,
            is_active=True
        )
        
        # Count total students across all courses
        total_students = Enrollment.objects.filter(
            course__in=teaching_courses,
            is_active=True
        ).count()
        
        # Count pending grades (grades not yet submitted)
        pending_grades = Grade.objects.filter(
            enrollment__course__in=teaching_courses,
            grade__isnull=True
        ).count()
        
        # Calculate weekly teaching hours
        weekly_hours = teaching_courses.aggregate(
            total_hours=Sum('credit_hours')
        )['total_hours'] or 0
        
        return {
            'teaching_courses_count': teaching_courses.count(),
            'total_students': total_students,
            'pending_grades': pending_grades,
            'weekly_hours': weekly_hours,
            'teaching_courses': teaching_courses[:5],  # Show only 5 recent courses
        }
        
    except Exception as e:
        logger.error(f"Error getting teacher dashboard data: {str(e)}")
        return {}


def _get_admin_dashboard_data(user):
    """Get dashboard data specific to admin/staff"""
    try:
        # System-wide statistics
        total_students = Student.objects.filter(status='ACTIVE').count()
        total_faculty = User.objects.filter(role='TEACHER', is_active=True).count()
        total_courses = Course.objects.filter(is_active=True).count()
        total_departments = Department.objects.count()
        
        # Recent registrations (last 30 days)
        recent_students = Student.objects.filter(
            enrollment_date__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        # Financial summary (mock data for now)
        total_fees_collected = 5000000  # Mock data
        pending_fees = 1500000  # Mock data
        
        return {
            'total_students': total_students,
            'total_faculty': total_faculty,
            'total_courses': total_courses,
            'total_departments': total_departments,
            'recent_students': recent_students,
            'total_fees_collected': total_fees_collected,
            'pending_fees': pending_fees,
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard data: {str(e)}")
        return {}


@login_required
def my_courses_view(request):
    """
    Student's enrolled courses view
    عرض المقررات المسجلة للطالب
    """
    if request.user.role != 'STUDENT':
        messages.error(request, 'هذه الصفحة مخصصة للطلاب فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        student = request.user.student_profile
        
        # Get current semester enrollments
        current_enrollments = Enrollment.objects.filter(
            student=student,
            is_active=True
        ).select_related('course', 'course__instructor').order_by('course__name')
        
        # Add pagination
        paginator = Paginator(current_enrollments, 6)  # 6 courses per page
        page_number = request.GET.get('page')
        enrollments = paginator.get_page(page_number)
        
        context = {
            'enrollments': enrollments,
            'student': student,
            'total_credit_hours': sum(e.course.credit_hours for e in current_enrollments),
        }
        
        return render(request, 'student/my_courses.html', context)
        
    except Exception as e:
        logger.error(f"Error in my_courses_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل المقررات')
        return redirect('web:enhanced_dashboard')


@login_required
def my_grades_view(request):
    """
    Student's grades view with GPA calculation
    عرض درجات الطالب مع حساب المعدل
    """
    if request.user.role != 'STUDENT':
        messages.error(request, 'هذه الصفحة مخصصة للطلاب فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        student = request.user.student_profile
        
        # Get all grades for the student
        grades = Grade.objects.filter(
            enrollment__student=student
        ).select_related(
            'enrollment__course',
            'enrollment__course__instructor'
        ).order_by('-enrollment__semester__start_date')
        
        # Group grades by semester (simplified for now)
        grades_by_semester = {}
        for grade in grades:
            semester = getattr(grade.enrollment, 'semester', 'Fall 2024')
            if semester not in grades_by_semester:
                grades_by_semester[semester] = []
            grades_by_semester[semester].append(grade)
        
        # Calculate semester GPAs
        semester_gpas = {}
        for semester, semester_grades in grades_by_semester.items():
            total_points = 0
            total_hours = 0
            for grade in semester_grades:
                if grade.grade is not None:
                    total_points += float(grade.grade) * grade.enrollment.course.credit_hours
                    total_hours += grade.enrollment.course.credit_hours
            
            semester_gpa = total_points / total_hours if total_hours > 0 else 0
            semester_gpas[semester] = round(semester_gpa, 2)
        
        context = {
            'grades_by_semester': grades_by_semester,
            'semester_gpas': semester_gpas,
            'student': student,
            'current_gpa': float(student.gpa),
        }
        
        return render(request, 'student/my_grades.html', context)
        
    except Exception as e:
        logger.error(f"Error in my_grades_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل الدرجات')
        return redirect('web:enhanced_dashboard')


@login_required
def my_schedule_view(request):
    """
    Student's class schedule view
    عرض الجدول الدراسي للطالب
    """
    if request.user.role != 'STUDENT':
        messages.error(request, 'هذه الصفحة مخصصة للطلاب فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        student = request.user.student_profile
        
        # Get current enrollments with schedule information
        enrollments = Enrollment.objects.filter(
            student=student,
            is_active=True
        ).select_related('course', 'course__instructor')
        
        # Organize schedule by days and times
        schedule = {}
        days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
        times = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']
        
        for day in days:
            schedule[day] = {}
            for time in times:
                schedule[day][time] = None
        
        # This would typically involve a Schedule model
        # For now, we'll create mock schedule data
        for i, enrollment in enumerate(enrollments[:5]):  # Limit to 5 courses for demo
            day = days[i % len(days)]
            time = times[i % len(times)]
            schedule[day][time] = {
                'course': enrollment.course,
                'instructor': enrollment.course.instructor,
                'room': f'قاعة {100 + i}',  # Mock room data
            }
        
        context = {
            'schedule': schedule,
            'days': days,
            'times': times,
            'student': student,
        }
        
        return render(request, 'student/my_schedule.html', context)
        
    except Exception as e:
        logger.error(f"Error in my_schedule_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل الجدول الدراسي')
        return redirect('web:enhanced_dashboard')


@login_required
def my_fees_view(request):
    """
    Student's financial information view
    عرض المعلومات المالية للطالب
    """
    if request.user.role != 'STUDENT':
        messages.error(request, 'هذه الصفحة مخصصة للطلاب فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        student = request.user.student_profile
        
        # Mock data for fees (until finance models are implemented)
        fees = []  # Mock data
        payments = []  # Mock data
        scholarships = []  # Mock data
        
        # Calculate totals (mock data)
        total_fees = 45000
        paid_fees = 30000
        pending_fees = 15000
        
        context = {
            'fees': fees,
            'payments': payments[:10],  # Show last 10 payments
            'scholarships': scholarships,
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'pending_fees': pending_fees,
            'student': student,
        }
        
        return render(request, 'student/my_fees.html', context)
        
    except Exception as e:
        logger.error(f"Error in my_fees_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل المعلومات المالية')
        return redirect('web:enhanced_dashboard')


@login_required
def teaching_view(request):
    """
    Teacher's courses and classes view
    عرض المقررات والصفوف للأستاذ
    """
    if request.user.role != 'TEACHER':
        messages.error(request, 'هذه الصفحة مخصصة للأساتذة فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        # Get courses taught by this teacher
        courses = Course.objects.filter(
            instructor=request.user,
            is_active=True
        ).order_by('name')
        
        # Get course statistics
        course_stats = []
        for course in courses:
            enrollments = Enrollment.objects.filter(course=course, is_active=True)
            stats = {
                'course': course,
                'total_students': enrollments.count(),
                'avg_grade': Grade.objects.filter(
                    enrollment__course=course,
                    grade__isnull=False
                ).aggregate(avg=Avg('grade'))['avg'] or 0,
                'completion_rate': 85,  # Mock data - would calculate from attendance
            }
            course_stats.append(stats)
        
        context = {
            'course_stats': course_stats,
            'total_courses': courses.count(),
            'total_students': sum(stat['total_students'] for stat in course_stats),
        }
        
        return render(request, 'teacher/teaching.html', context)
        
    except Exception as e:
        logger.error(f"Error in teaching_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل بيانات التدريس')
        return redirect('web:enhanced_dashboard')


@login_required
def students_view(request):
    """
    Teacher's view of students in their courses
    عرض الطلاب في مقررات الأستاذ
    """
    if request.user.role != 'TEACHER':
        messages.error(request, 'هذه الصفحة مخصصة للأساتذة فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        # Get all students enrolled in teacher's courses
        teacher_courses = Course.objects.filter(instructor=request.user, is_active=True)
        
        enrollments = Enrollment.objects.filter(
            course__in=teacher_courses,
            is_active=True
        ).select_related('student__user', 'course').order_by('student__user__first_name')
        
        # Filter by course if specified
        course_filter = request.GET.get('course')
        if course_filter:
            enrollments = enrollments.filter(course_id=course_filter)
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            enrollments = enrollments.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__student_id__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(enrollments, 20)
        page_number = request.GET.get('page')
        students = paginator.get_page(page_number)
        
        context = {
            'students': students,
            'teacher_courses': teacher_courses,
            'search_query': search_query,
            'course_filter': course_filter,
        }
        
        return render(request, 'teacher/students.html', context)
        
    except Exception as e:
        logger.error(f"Error in students_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل بيانات الطلاب')
        return redirect('web:enhanced_dashboard')


@login_required
def grade_management_view(request):
    """
    Teacher's grade management interface
    واجهة إدارة الدرجات للأستاذ
    """
    if request.user.role != 'TEACHER':
        messages.error(request, 'هذه الصفحة مخصصة للأساتذة فقط')
        return redirect('web:enhanced_dashboard')
    
    try:
        # Get teacher's courses
        teacher_courses = Course.objects.filter(instructor=request.user, is_active=True)
        
        # Get selected course
        selected_course_id = request.GET.get('course')
        selected_course = None
        grades = []
        
        if selected_course_id:
            selected_course = get_object_or_404(teacher_courses, id=selected_course_id)
            
            # Get all enrollments for the selected course
            enrollments = Enrollment.objects.filter(
                course=selected_course,
                is_active=True
            ).select_related('student__user')
            
            # Get or create grades for each enrollment
            grades = []
            for enrollment in enrollments:
                grade, created = Grade.objects.get_or_create(
                    enrollment=enrollment,
                    defaults={'grade': None}
                )
                grades.append(grade)
        
        context = {
            'teacher_courses': teacher_courses,
            'selected_course': selected_course,
            'grades': grades,
        }
        
        return render(request, 'teacher/grade_management.html', context)
        
    except Exception as e:
        logger.error(f"Error in grade_management_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل إدارة الدرجات')
        return redirect('web:enhanced_dashboard')


@login_required
def admin_panel_view(request):
    """
    Admin panel with system overview
    لوحة الإدارة مع نظرة عامة على النظام
    """
    if request.user.role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect('web:enhanced_dashboard')
    
    try:
        # System statistics
        stats = {
            'total_users': User.objects.count(),
            'active_students': Student.objects.filter(status='ACTIVE').count(),
            'total_teachers': User.objects.filter(role='TEACHER', is_active=True).count(),
            'total_courses': Course.objects.count(),
            'active_courses': Course.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.count(),
        }
        
        # Recent activities (mock data - would come from activity logs)
        recent_activities = [
            {'action': 'تم إنشاء مستخدم جديد', 'user': 'أحمد محمد', 'time': '10 دقائق'},
            {'action': 'تم تحديث معلومات المقرر', 'user': 'فاطمة أحمد', 'time': 'ساعة واحدة'},
            {'action': 'تم إضافة قسم جديد', 'user': 'محمد علي', 'time': '3 ساعات'},
        ]
        
        context = {
            'stats': stats,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'admin/admin_panel.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin_panel_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل لوحة الإدارة')
        return redirect('web:enhanced_dashboard')


@login_required
def user_management_view(request):
    """
    User management interface for admins
    واجهة إدارة المستخدمين للمديرين
    """
    if request.user.role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect('web:enhanced_dashboard')
    
    try:
        # Get all users with search and filter functionality
        users = User.objects.all().order_by('-date_joined')
        
        # Role filter
        role_filter = request.GET.get('role')
        if role_filter:
            users = users.filter(role=role_filter)
        
        # Status filter  
        status_filter = request.GET.get('status')
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(users, 20)
        page_number = request.GET.get('page')
        users_page = paginator.get_page(page_number)
        
        # Role choices for filter dropdown
        role_choices = User.ROLE_CHOICES
        
        context = {
            'users': users_page,
            'role_choices': role_choices,
            'search_query': search_query,
            'role_filter': role_filter,
            'status_filter': status_filter,
        }
        
        return render(request, 'admin/user_management.html', context)
        
    except Exception as e:
        logger.error(f"Error in user_management_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل إدارة المستخدمين')
        return redirect('web:enhanced_dashboard')


@login_required
def system_stats_view(request):
    """
    System statistics and analytics view
    عرض إحصائيات النظام والتحليلات
    """
    if request.user.role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect('web:enhanced_dashboard')
    
    try:
        # Comprehensive system statistics
        stats = {
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'students': User.objects.filter(role='STUDENT').count(),
                'teachers': User.objects.filter(role='TEACHER').count(),
                'staff': User.objects.filter(role='STAFF').count(),
                'admins': User.objects.filter(role='ADMIN').count(),
            },
            'academic': {
                'total_courses': Course.objects.count(),
                'active_courses': Course.objects.filter(is_active=True).count(),
                'total_enrollments': Enrollment.objects.count(),
                'active_enrollments': Enrollment.objects.filter(is_active=True).count(),
                'departments': Department.objects.count(),
            },
            'financial': {
                'total_fees': Fee.objects.aggregate(total=Sum('amount'))['total'] or 0,
                'paid_fees': Fee.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0,
                'pending_fees': Fee.objects.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0,
                'total_payments': Payment.objects.aggregate(total=Sum('amount'))['total'] or 0,
            }
        }
        
        # Calculate additional metrics
        stats['users']['active_percentage'] = (
            stats['users']['active'] / stats['users']['total'] * 100
        ) if stats['users']['total'] > 0 else 0
        
        stats['academic']['enrollment_rate'] = (
            stats['academic']['active_enrollments'] / stats['users']['students'] * 100
        ) if stats['users']['students'] > 0 else 0
        
        stats['financial']['collection_rate'] = (
            stats['financial']['paid_fees'] / stats['financial']['total_fees'] * 100
        ) if stats['financial']['total_fees'] > 0 else 0
        
        context = {
            'stats': stats,
        }
        
        return render(request, 'admin/system_stats.html', context)
        
    except Exception as e:
        logger.error(f"Error in system_stats_view for user {request.user.id}: {str(e)}")
        messages.error(request, 'حدث خطأ في تحميل إحصائيات النظام')
        return redirect('web:enhanced_dashboard')


@login_required
@require_http_methods(["GET"])
def api_dashboard_stats(request):
    """
    API endpoint for dashboard statistics
    نقطة API للحصول على إحصائيات لوحة التحكم
    """
    try:
        user = request.user
        stats = {}
        
        if user.role == 'STUDENT':
            stats = _get_student_dashboard_data(user)
        elif user.role == 'TEACHER':
            stats = _get_teacher_dashboard_data(user)
        elif user.role in ['ADMIN', 'STAFF']:
            stats = _get_admin_dashboard_data(user)
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error in api_dashboard_stats for user {request.user.id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في تحميل الإحصائيات'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_search(request):
    """
    Global search API endpoint
    نقطة API للبحث الشامل
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'يرجى إدخال كلمة البحث'
            })
        
        results = []
        
        # Search in different models based on user role
        if request.user.role in ['ADMIN', 'STAFF']:
            # Search users
            users = User.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query)
            )[:5]
            
            for user in users:
                results.append({
                    'type': 'user',
                    'title': user.get_full_name() or user.username,
                    'subtitle': f"({user.get_role_display()})",
                    'url': f'/admin/users/{user.id}/'
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
                    'subtitle': f"كود المقرر: {course.code}",
                    'url': f'/admin/courses/{course.id}/'
                })
        
        elif request.user.role == 'TEACHER':
            # Search teacher's courses
            courses = Course.objects.filter(
                instructor=request.user,
                name__icontains=query
            )[:5]
            
            for course in courses:
                results.append({
                    'type': 'course',
                    'title': course.name,
                    'subtitle': f"عدد الطلاب: {course.enrollments.count()}",
                    'url': f'/teacher/courses/{course.id}/'
                })
        
        elif request.user.role == 'STUDENT':
            # Search student's courses
            enrollments = Enrollment.objects.filter(
                student=request.user.student_profile,
                course__name__icontains=query,
                is_active=True
            )[:5]
            
            for enrollment in enrollments:
                results.append({
                    'type': 'course',
                    'title': enrollment.course.name,
                    'subtitle': f"الأستاذ: {enrollment.course.instructor.get_full_name()}",
                    'url': f'/student/courses/{enrollment.course.id}/'
                })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in api_search for user {request.user.id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في البحث'
        }, status=500)