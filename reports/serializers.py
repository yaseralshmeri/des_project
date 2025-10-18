from rest_framework import serializers
from .models import StudentPerformanceReport, CourseAnalytics, EnrollmentStatistics

class StudentPerformanceReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the StudentPerformanceReport model.
    """
    class Meta:
        model = StudentPerformanceReport
        fields = ['id', 'student', 'academic_year', 'semester', 'gpa', 'total_credits', 
                 'credits_earned', 'rank_in_class', 'total_students', 'attendance_percentage', 
                 'remarks', 'generated_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseAnalytics model.
    """
    class Meta:
        model = CourseAnalytics
        fields = ['id', 'course_offering', 'total_enrolled', 'average_grade', 'pass_rate', 
                 'dropout_rate', 'student_satisfaction_score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnrollmentStatisticsSerializer(serializers.ModelSerializer):
    """
    Serializer for the EnrollmentStatistics model.
    """
    class Meta:
        model = EnrollmentStatistics
        fields = ['id', 'academic_year', 'semester', 'total_students', 'new_enrollments', 
                 'graduated_students', 'dropped_students', 'average_gpa', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
