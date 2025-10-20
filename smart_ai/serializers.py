from rest_framework import serializers
from .models import (
    AIAnalyticsModel, StudentPerformancePrediction, AIChatBot,
    ChatMessage, SmartRecommendation, PredictiveAnalytics,
    AISecurityAlert, SmartScheduling
)

class AIAnalyticsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalyticsModel
        fields = '__all__'

class StudentPerformancePredictionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = StudentPerformancePrediction
        fields = '__all__'

class AIChatBotSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AIChatBot
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class SmartRecommendationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = SmartRecommendation
        fields = '__all__'

class PredictiveAnalyticsSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = PredictiveAnalytics
        fields = '__all__'

class AISecurityAlertSerializer(serializers.ModelSerializer):
    affected_user_name = serializers.CharField(source='affected_user.get_full_name', read_only=True)
    
    class Meta:
        model = AISecurityAlert
        fields = '__all__'

class SmartSchedulingSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = SmartScheduling
        fields = '__all__'