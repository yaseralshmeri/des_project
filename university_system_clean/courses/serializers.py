from rest_framework import serializers
from .models import Course, CourseOffering, Assignment


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'description', 'department', 'department_name',
            'credits', 'semester_offered', 'max_capacity', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CourseOfferingSerializer(serializers.ModelSerializer):
    """Serializer for CourseOffering model"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseOffering
        fields = [
            'id', 'course', 'course_name', 'course_code', 'instructor', 'instructor_name',
            'semester', 'academic_year', 'schedule_day', 'start_time', 'end_time',
            'room', 'current_enrollment', 'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_full']
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    course_name = serializers.CharField(source='course_offering.course.name', read_only=True)
    course_code = serializers.CharField(source='course_offering.course.code', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course_offering', 'course_name', 'course_code', 'title', 'description',
            'assignment_type', 'max_score', 'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']