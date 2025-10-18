from rest_framework import serializers
from .models import PerformancePrediction, CourseRecommendation, StudyPattern

class PerformancePredictionSerializer(serializers.ModelSerializer):
    """
    Serializer for the PerformancePrediction model.
    """
    class Meta:
        model = PerformancePrediction
        fields = ['id', 'student', 'course', 'predicted_grade', 'confidence_score', 
                 'factors', 'recommendations', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseRecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseRecommendation model.
    """
    class Meta:
        model = CourseRecommendation
        fields = ['id', 'student', 'recommended_course', 'recommendation_score', 
                 'reasoning', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudyPatternSerializer(serializers.ModelSerializer):
    """
    Serializer for the StudyPattern model.
    """
    class Meta:
        model = StudyPattern
        fields = ['id', 'student', 'analysis_period_start', 'analysis_period_end', 
                 'pattern_data', 'strengths', 'weaknesses', 'improvement_suggestions', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
