"""
Courses App ViewSets for DRF API
ViewSets لتطبيق المقررات في DRF API
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Course, CourseOffering
from .serializers import CourseSerializer, CourseOfferingSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course model
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Course.objects.all()
        
        # Filter by active status for students
        if self.request.user.is_student:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search courses"""
        query = request.query_params.get('q', '')
        department = request.query_params.get('department', '')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(description__icontains=query)
            )
        
        if department:
            queryset = queryset.filter(department__name__icontains=department)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get students enrolled in this course"""
        course = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin or request.user.is_staff_member or 
                request.user.is_teacher and course.instructor == request.user):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get enrolled students (implement based on your enrollment model)
        try:
            from academic.models import Enrollment
            enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
            students_data = []
            
            for enrollment in enrollments:
                students_data.append({
                    'student_id': enrollment.student.student_id,
                    'name': enrollment.student.user.get_full_name(),
                    'email': enrollment.student.user.email,
                    'enrollment_date': enrollment.date_enrolled,
                    'status': enrollment.status,
                })
            
            return Response(students_data)
        except ImportError:
            return Response([])
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get courses grouped by department"""
        departments = self.get_queryset().values('department__name').annotate(
            course_count=Count('id')
        ).order_by('department__name')
        
        result = {}
        for dept in departments:
            dept_name = dept['department__name']
            dept_courses = self.get_queryset().filter(department__name=dept_name)
            result[dept_name] = self.get_serializer(dept_courses, many=True).data
        
        return Response(result)


class CourseOfferingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CourseOffering model
    """
    serializer_class = CourseOfferingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        return CourseOffering.objects.all()
    
    @action(detail=False, methods=['get'])
    def current_semester(self, request):
        """Get course offerings for current semester"""
        try:
            from academic.models import Semester
            current_semester = Semester.objects.filter(is_current=True).first()
            
            if not current_semester:
                return Response([])
            
            queryset = self.get_queryset().filter(semester=current_semester)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ImportError:
            return Response([])
    
    @action(detail=False, methods=['get'])
    def by_instructor(self, request):
        """Get course offerings by instructor"""
        instructor_id = request.query_params.get('instructor_id')
        
        if not instructor_id:
            return Response(
                {'error': 'instructor_id parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(instructor_id=instructor_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get schedule for this course offering"""
        offering = self.get_object()
        
        # Return schedule data (implement based on your schedule model)
        schedule_data = {
            'course_code': offering.course.code,
            'course_name': offering.course.name,
            'instructor': offering.instructor.get_full_name() if offering.instructor else None,
            'semester': str(offering.semester),
            'capacity': offering.max_capacity,
            'enrolled': offering.enrolled_students_count if hasattr(offering, 'enrolled_students_count') else 0,
            'schedule': 'Schedule details would go here'  # Implement based on your schedule model
        }
        
        return Response(schedule_data)