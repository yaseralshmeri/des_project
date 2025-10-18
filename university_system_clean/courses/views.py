from rest_framework import viewsets, permissions
from .models import Course, CourseOffering, Assignment
from .serializers import CourseSerializer, CourseOfferingSerializer, AssignmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing courses"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'is_active', 'credits']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'credits', 'created_at']
    ordering = ['code']


class CourseOfferingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing course offerings"""
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course', 'instructor', 'semester', 'academic_year']
    ordering_fields = ['academic_year', 'semester', 'course__code']
    ordering = ['-academic_year', 'semester']


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assignments"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course_offering', 'assignment_type']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['due_date']