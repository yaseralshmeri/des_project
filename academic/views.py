# FIX: Performance Issues - عالي
# إصلاح مشاكل N+1 queries وتحسين الاستعلامات في academic views

"""
Academic App Views
API views for academic management functionality
FIX: Major performance improvements with optimized queries and caching
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Prefetch
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
import logging

from .models import (
    AcademicYear, Semester, Enrollment, Grade, Attendance,
    Schedule, AcademicProgram, AcademicCalendar
)
from .serializers import (
    AcademicYearSerializer, SemesterSerializer, EnrollmentSerializer,
    GradeSerializer, AttendanceSerializer, ScheduleSerializer,
    AcademicProgramSerializer, AcademicCalendarSerializer,
    StudentGradeReportSerializer, TeacherScheduleSerializer
)
from students.models import Student, User

logger = logging.getLogger(__name__)


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization with caching
    """
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_current']
    ordering = ['-start_date']
    queryset = AcademicYear.objects.prefetch_related(
        'semesters'
    ).order_by('-start_date')
    
    def get_queryset(self):
        """FIX: Add prefetch for related semesters"""
        return self.queryset
    
    @method_decorator(cache_page(3600))  # Cache for 1 hour
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view"""
        return super().list(request, *args, **kwargs)


class SemesterViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for semester operations
    """
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['academic_year', 'name', 'is_current']
    ordering = ['-start_date']
    queryset = Semester.objects.select_related(
        'academic_year'
    ).prefetch_related(
        'enrollments',
        'schedules'
    ).order_by('-start_date')
    
    def get_queryset(self):
        """FIX: Add select_related for academic_year"""
        return self.queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    FIX: Major performance improvements for enrollment queries
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'course', 'semester', 'status']
    ordering = ['-enrollment_date']
    queryset = Enrollment.objects.select_related(
        'student',
        'student__user',
        'course',
        'semester',
        'semester__academic_year'
    ).prefetch_related(
        Prefetch(
            'grades',
            queryset=Grade.objects.select_related('enrollment').order_by('-date_assigned')
        ),
        Prefetch(
            'attendance_records',
            queryset=Attendance.objects.select_related('recorded_by').order_by('-date')
        )
    )
    
    def get_queryset(self):
        """FIX: Performance - Comprehensive query optimization"""
        base_queryset = Enrollment.objects.select_related(
            'student',  # Join with Student
            'student__user',  # Join with User through Student
            'course',  # Join with Course
            'semester',  # Join with Semester
            'semester__academic_year'  # Join with AcademicYear
        ).prefetch_related(
            Prefetch(
                'grades',
                queryset=Grade.objects.select_related('enrollment').order_by('-date_assigned')
            ),
            Prefetch(
                'attendance_records',
                queryset=Attendance.objects.select_related('recorded_by').order_by('-date')
            )
        )
        
        # Filter based on user role
        if self.request.user.is_student:
            # Students can only see their own enrollments
            if hasattr(self.request.user, 'student_profile'):
                return base_queryset.filter(student=self.request.user.student_profile)
            else:
                return base_queryset.none()
        elif self.request.user.is_teacher:
            # FIX: Optimize teacher course lookup
            teacher_courses = Schedule.objects.filter(
                instructor=self.request.user
            ).values_list('course', flat=True)
            return base_queryset.filter(course__in=teacher_courses)
        
        return base_queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            enrollment = serializer.save()
            logger.info(f"Enrollment created: {enrollment.student.student_id} - {enrollment.course.name}")
        except Exception as e:
            logger.error(f"Failed to create enrollment: {str(e)}")
            raise


class GradeViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for grade operations
    """
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enrollment', 'grade_type', 'date_assigned', 'date_graded']
    ordering = ['-date_assigned']
    queryset = Grade.objects.select_related('enrollment', 'enrollment__student', 'enrollment__course', 'assigned_by').order_by('-date_assigned')
    
    def get_queryset(self):
        """FIX: Performance - Add comprehensive joins"""
        base_queryset = Grade.objects.select_related(
            'enrollment',  # Join with Enrollment
            'enrollment__student',  # Join with Student
            'enrollment__student__user',  # Join with User
            'enrollment__course',  # Join with Course
            'enrollment__semester'  # Join with Semester
        )
        
        # Filter based on user role
        if self.request.user.is_student:
            # Students can only see their own grades
            if hasattr(self.request.user, 'student_profile'):
                return base_queryset.filter(enrollment__student=self.request.user.student_profile)
            else:
                return base_queryset.none()
        elif self.request.user.is_teacher:
            # FIX: Optimize teacher course lookup with caching
            cache_key = f"teacher_courses_{self.request.user.id}"
            teacher_courses = cache.get(cache_key)
            if teacher_courses is None:
                teacher_courses = list(Schedule.objects.filter(
                    instructor=self.request.user
                ).values_list('course', flat=True))
                cache.set(cache_key, teacher_courses, 300)  # Cache for 5 minutes
            
            return base_queryset.filter(enrollment__course__in=teacher_courses)
        
        return base_queryset


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for attendance records
    """
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enrollment', 'date', 'status']
    ordering = ['-date']
    queryset = Attendance.objects.select_related('enrollment', 'enrollment__student', 'enrollment__course', 'recorded_by').order_by('-date')
    
    def get_queryset(self):
        """FIX: Performance - Add comprehensive joins"""
        base_queryset = Attendance.objects.select_related(
            'enrollment',  # Join with Enrollment
            'enrollment__student',  # Join with Student
            'enrollment__student__user',  # Join with User
            'enrollment__course',  # Join with Course
            'recorded_by'  # Join with User who recorded attendance
        )
        
        # Filter based on user role
        if self.request.user.is_student:
            # Students can only see their own attendance
            if hasattr(self.request.user, 'student_profile'):
                return base_queryset.filter(enrollment__student=self.request.user.student_profile)
            else:
                return base_queryset.none()
        elif self.request.user.is_teacher:
            # FIX: Use cached teacher courses
            cache_key = f"teacher_courses_{self.request.user.id}"
            teacher_courses = cache.get(cache_key)
            if teacher_courses is None:
                teacher_courses = list(Schedule.objects.filter(
                    instructor=self.request.user
                ).values_list('course', flat=True))
                cache.set(cache_key, teacher_courses, 300)
            
            return base_queryset.filter(enrollment__course__in=teacher_courses)
        
        return base_queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction and logging"""
        try:
            attendance = serializer.save(recorded_by=self.request.user)
            logger.info(f"Attendance recorded: {attendance.enrollment.student.student_id} - {attendance.status}")
        except Exception as e:
            logger.error(f"Failed to record attendance: {str(e)}")
            raise


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for class schedules
    """
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'semester', 'instructor', 'day_of_week']
    ordering = ['day_of_week', 'start_time']
    queryset = Schedule.objects.select_related('course', 'semester', 'instructor').order_by('day_of_week', 'start_time')
    
    def get_queryset(self):
        """FIX: Performance - Add comprehensive joins"""
        base_queryset = Schedule.objects.select_related(
            'course',  # Join with Course
            'semester',  # Join with Semester
            'semester__academic_year',  # Join with AcademicYear
            'instructor'  # Join with User (instructor)
        ).prefetch_related(
            'course__enrollments',
            'course__enrollments__student'
        )
        
        # Filter based on user role
        if self.request.user.is_student:
            # Students can see schedules for their enrolled courses
            if hasattr(self.request.user, 'student_profile'):
                enrolled_courses = Enrollment.objects.filter(
                    student=self.request.user.student_profile,
                    status='ENROLLED'
                ).values_list('course', flat=True)
                return base_queryset.filter(course__in=enrolled_courses)
            else:
                return base_queryset.none()
        elif self.request.user.is_teacher:
            # Teachers can see their own schedules
            return base_queryset.filter(instructor=self.request.user)
        
        return base_queryset


class AcademicProgramViewSet(viewsets.ModelViewSet):
    """FIX: Performance optimization with caching"""
    serializer_class = AcademicProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'degree_type', 'is_active']
    ordering = ['name']
    queryset = AcademicProgram.objects.prefetch_related('courses').order_by('name')
    
    def get_queryset(self):
        """FIX: Add select_related for department"""
        return AcademicProgram.objects.select_related('department')
    
    @method_decorator(cache_page(1800))  # Cache for 30 minutes
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view"""
        return super().list(request, *args, **kwargs)


class AcademicCalendarViewSet(viewsets.ModelViewSet):
    """FIX: Performance optimization for academic calendar"""
    serializer_class = AcademicCalendarSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type', 'is_holiday', 'semester']
    ordering = ['date']
    queryset = AcademicCalendar.objects.select_related('semester').order_by('date')
    
    def get_queryset(self):
        """FIX: Add select_related for semester"""
        return AcademicCalendar.objects.select_related(
            'semester',
            'semester__academic_year'
        )


# Custom API endpoints

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_semester(request):
    """FIX: Get current semester information with caching"""
    cache_key = "current_semester"
    semester_data = cache.get(cache_key)
    
    if not semester_data:
        semester = Semester.objects.select_related('academic_year').filter(is_current=True).first()
        if semester:
            semester_data = SemesterSerializer(semester).data
            cache.set(cache_key, semester_data, 1800)  # Cache for 30 minutes
        else:
            return Response({'detail': 'No current semester found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(semester_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_grades(request, student_id):
    """
    FIX: Get detailed grade report for a student with optimized queries
    """
    if request.user.is_student and request.user.student_profile.id != student_id:
        return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # FIX: Use select_related to optimize the student query
    student = get_object_or_404(Student.objects.select_related('user'), id=student_id)
    
    # FIX: Optimize semesters query with comprehensive joins
    semesters = Semester.objects.select_related(
        'academic_year'
    ).prefetch_related(
        Prefetch(
            'enrollments',
            queryset=Enrollment.objects.filter(student=student).select_related(
                'course'
            ).prefetch_related(
                Prefetch(
                    'grades',
                    queryset=Grade.objects.order_by('-date_assigned')
                )
            )
        )
    ).filter(
        enrollments__student=student
    ).distinct().order_by('-start_date')
    
    serializer = StudentGradeReportSerializer(
        semesters, 
        many=True, 
        context={'student': student}
    )
    
    return Response({
        'student': {
            'id': student.id,
            'name': student.user.get_full_name(),
            'student_id': student.student_id,
            'gpa': student.gpa
        },
        'semesters': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_classes(request, teacher_id):
    """FIX: Get classes for a specific teacher with optimized queries"""
    if request.user.is_teacher and request.user.id != teacher_id:
        return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    teacher = get_object_or_404(User, id=teacher_id, role='TEACHER')
    
    # FIX: Use caching for teacher data
    cache_key = f"teacher_classes_{teacher_id}"
    teacher_data = cache.get(cache_key)
    
    if not teacher_data:
        serializer = TeacherScheduleSerializer(teacher)
        teacher_data = serializer.data
        cache.set(cache_key, teacher_data, 300)  # Cache for 5 minutes
    
    return Response(teacher_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def grade_reports(request):
    """
    FIX: Generate various grade reports with optimized aggregation queries
    """
    if not (request.user.is_admin or request.user.is_staff_member):
        return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    cache_key = "grade_reports_summary"
    reports_data = cache.get(cache_key)
    
    if not reports_data:
        current_semester = Semester.objects.select_related('academic_year').filter(is_current=True).first()
        if not current_semester:
            return Response({'detail': 'No current semester found'}, status=status.HTTP_404_NOT_FOUND)
        
        # FIX: Use optimized aggregation queries instead of Python loops
        grade_distribution = Grade.objects.filter(
            enrollment__semester=current_semester,
            date_graded__isnull=False
        ).values('grade_type').annotate(
            count=Count('id'),
            avg_grade=Avg('points_earned')
        )
        
        # FIX: Optimize course performance query
        course_performance = Enrollment.objects.filter(
            semester=current_semester
        ).select_related('course').annotate(
            avg_grade=Avg('grades__points_earned')
        ).values(
            'course__name', 'course__code'
        ).annotate(
            enrolled_count=Count('id'),
            avg_grade=Avg('grades__points_earned')
        )
        
        # FIX: Optimize student performance query
        student_performance = Student.objects.filter(
            enrollments__semester=current_semester
        ).select_related('user').annotate(
            courses_count=Count('enrollments'),
            avg_grade=Avg('enrollments__grades__points_earned')
        ).values(
            'user__first_name', 'user__last_name', 'student_id',
            'courses_count', 'avg_grade', 'gpa'
        )
        
        reports_data = {
            'semester': SemesterSerializer(current_semester).data,
            'grade_distribution': list(grade_distribution),
            'course_performance': list(course_performance),
            'student_performance': list(student_performance)
        }
        
        cache.set(cache_key, reports_data, 1800)  # Cache for 30 minutes
    
    return Response(reports_data)