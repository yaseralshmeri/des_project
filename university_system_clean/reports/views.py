# FIX: Performance Issues - عالي
# إصلاح مشاكل الأداء وإضافة تحسينات للتقارير

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
import logging

from .models import StudentPerformanceReport, CourseAnalytics, EnrollmentStatistics
from .serializers import (StudentPerformanceReportSerializer, CourseAnalyticsSerializer,
                          EnrollmentStatisticsSerializer)
from students.permissions import IsAdminOrStaff
from students.models import Student
from academic.models import Semester, Enrollment, Grade

logger = logging.getLogger(__name__)

class StudentPerformanceReportViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization with caching and query optimization
    """
    serializer_class = StudentPerformanceReportSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['student', 'semester', 'created_at']
    queryset = StudentPerformanceReport.objects.select_related(
        'student',
        'student__user',
        'semester',
        'semester__academic_year'
    ).order_by('-created_at')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related to avoid N+1 queries"""
        return self.queryset
    
    @method_decorator(cache_page(1800))  # Cache for 30 minutes
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view"""
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def generate_batch_reports(self, request):
        """
        FIX: Add bulk report generation with optimized queries
        """
        semester_id = request.query_params.get('semester_id')
        if not semester_id:
            return Response(
                {'error': 'semester_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f"batch_reports_{semester_id}"
        reports_data = cache.get(cache_key)
        
        if not reports_data:
            try:
                # FIX: Use optimized bulk query instead of individual student queries
                enrollments = Enrollment.objects.filter(
                    semester_id=semester_id
                ).select_related(
                    'student', 'student__user', 'course'
                ).prefetch_related(
                    'grades', 'attendance_records'
                )
                
                reports = []
                for enrollment in enrollments:
                    # Calculate performance metrics
                    grades = enrollment.grades.all()
                    attendance = enrollment.attendance_records.all()
                    
                    total_grades = len(grades)
                    avg_grade = sum(g.points_earned for g in grades) / total_grades if total_grades else 0
                    
                    total_classes = len(attendance)
                    present_count = len([a for a in attendance if a.status == 'PRESENT'])
                    attendance_rate = (present_count / total_classes * 100) if total_classes else 0
                    
                    reports.append({
                        'student_id': enrollment.student.student_id,
                        'student_name': enrollment.student.user.get_full_name(),
                        'course': enrollment.course.name,
                        'avg_grade': round(avg_grade, 2),
                        'attendance_rate': round(attendance_rate, 2),
                        'total_assignments': total_grades
                    })
                
                reports_data = reports
                cache.set(cache_key, reports_data, 3600)  # Cache for 1 hour
                
            except Exception as e:
                logger.error(f"Failed to generate batch reports: {str(e)}")
                return Response(
                    {'error': 'Failed to generate reports'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(reports_data)

class CourseAnalyticsViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for course analytics
    """
    serializer_class = CourseAnalyticsSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['course_offering', 'created_at']
    queryset = CourseAnalytics.objects.select_related(
        'course_offering',
        'course_offering__course'
    ).order_by('-created_at')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related to avoid N+1 queries"""
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def course_performance_summary(self, request):
        """
        FIX: Add optimized course performance endpoint
        """
        semester_id = request.query_params.get('semester_id')
        cache_key = f"course_performance_{semester_id or 'all'}"
        summary = cache.get(cache_key)
        
        if not summary:
            try:
                # FIX: Use aggregation queries for better performance
                enrollments_query = Enrollment.objects.select_related('course')
                
                if semester_id:
                    enrollments_query = enrollments_query.filter(semester_id=semester_id)
                
                # Get course statistics
                course_stats = enrollments_query.values(
                    'course__name', 'course__code'
                ).annotate(
                    enrollment_count=Count('id'),
                    avg_grade=Avg('grades__points_earned'),
                    completion_rate=Count('id', filter=Q(status='COMPLETED')) * 100.0 / Count('id')
                ).order_by('-enrollment_count')[:20]  # Top 20 courses
                
                summary = {
                    'total_courses': course_stats.count(),
                    'course_statistics': list(course_stats)
                }
                
                cache.set(cache_key, summary, 1800)  # Cache for 30 minutes
                
            except Exception as e:
                logger.error(f"Failed to generate course performance summary: {str(e)}")
                return Response(
                    {'error': 'Failed to generate summary'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(summary)

class EnrollmentStatisticsViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for enrollment statistics
    """
    serializer_class = EnrollmentStatisticsSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['academic_year', 'semester', 'created_at']
    queryset = EnrollmentStatistics.objects.select_related(
    ).order_by('-created_at')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related to avoid N+1 queries"""
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def enrollment_trends(self, request):
        """
        FIX: Add optimized enrollment trends endpoint
        """
        cache_key = "enrollment_trends"
        trends = cache.get(cache_key)
        
        if not trends:
            try:
                # FIX: Use aggregation for enrollment trends over last 6 semesters
                recent_semesters = Semester.objects.select_related(
                    'academic_year'
                ).order_by('-start_date')[:6]
                
                trends_data = []
                for semester in recent_semesters:
                    # Get enrollment statistics for this semester
                    enrollment_stats = Enrollment.objects.filter(
                        semester=semester
                    ).aggregate(
                        total_enrollments=Count('id'),
                        active_enrollments=Count('id', filter=Q(status='ENROLLED')),
                        completed_enrollments=Count('id', filter=Q(status='COMPLETED')),
                        dropped_enrollments=Count('id', filter=Q(status='DROPPED'))
                    )
                    
                    trends_data.append({
                        'semester': f"{semester.academic_year.name} - {semester.name}",
                        'semester_id': semester.id,
                        'start_date': semester.start_date,
                        **enrollment_stats
                    })
                
                trends = {
                    'trends': trends_data,
                    'total_semesters': len(trends_data)
                }
                
                cache.set(cache_key, trends, 3600)  # Cache for 1 hour
                
            except Exception as e:
                logger.error(f"Failed to generate enrollment trends: {str(e)}")
                return Response(
                    {'error': 'Failed to generate trends'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(trends)
    
    @action(detail=False, methods=['get'])
    def student_demographics(self, request):
        """
        FIX: Add optimized student demographics endpoint
        """
        cache_key = "student_demographics"
        demographics = cache.get(cache_key)
        
        if not demographics:
            try:
                # FIX: Use aggregation queries for demographics
                total_students = Student.objects.count()
                
                # Status breakdown
                status_breakdown = Student.objects.values('status').annotate(
                    count=Count('id')
                ).order_by('status')
                
                # Semester breakdown
                semester_breakdown = Student.objects.values('current_semester').annotate(
                    count=Count('id')
                ).order_by('current_semester')
                
                # Major breakdown (top 10)
                major_breakdown = Student.objects.values('major').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]
                
                # GPA distribution
                gpa_ranges = [
                    ('0.00-1.00', Q(gpa__gte=0.0, gpa__lt=1.0)),
                    ('1.00-2.00', Q(gpa__gte=1.0, gpa__lt=2.0)),
                    ('2.00-3.00', Q(gpa__gte=2.0, gpa__lt=3.0)),
                    ('3.00-4.00', Q(gpa__gte=3.0, gpa__lte=4.0)),
                ]
                
                gpa_distribution = []
                for range_name, range_filter in gpa_ranges:
                    count = Student.objects.filter(range_filter).count()
                    gpa_distribution.append({
                        'range': range_name,
                        'count': count,
                        'percentage': round((count / total_students * 100), 2) if total_students else 0
                    })
                
                demographics = {
                    'total_students': total_students,
                    'status_breakdown': list(status_breakdown),
                    'semester_breakdown': list(semester_breakdown),
                    'major_breakdown': list(major_breakdown),
                    'gpa_distribution': gpa_distribution
                }
                
                cache.set(cache_key, demographics, 3600)  # Cache for 1 hour
                
            except Exception as e:
                logger.error(f"Failed to generate student demographics: {str(e)}")
                return Response(
                    {'error': 'Failed to generate demographics'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(demographics)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            stats = serializer.save()
            logger.info(f"Enrollment statistics created for semester: {stats.semester}")
        except Exception as e:
            logger.error(f"Failed to create enrollment statistics: {str(e)}")
            raise