from django.contrib import admin
from .models import (
    AIModel, StudentAIProfile, TeacherAIProfile, 
    AIRecommendation, PredictiveAnalytics,
    SmartAssistant, ConversationLog, LearningAnalytics
)

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'model_type', 'accuracy', 'is_active', 'status']
    list_filter = ['model_type', 'is_active', 'status']
    search_fields = ['name_ar', 'name_en', 'description']

@admin.register(StudentAIProfile)
class StudentAIProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'predicted_gpa', 'dropout_risk', 'learning_style']
    list_filter = ['dropout_risk', 'learning_style', 'stress_level']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(TeacherAIProfile)
class TeacherAIProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'teaching_effectiveness', 'student_satisfaction_avg', 'course_success_rate']
    list_filter = ['teaching_effectiveness']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation_type', 'title', 'priority', 'status']
    list_filter = ['recommendation_type', 'priority', 'status']
    search_fields = ['user__username', 'title']

@admin.register(SmartAssistant)
class SmartAssistantAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'assistant_type', 'capability_level', 'is_active']
    list_filter = ['assistant_type', 'capability_level', 'is_active']
    search_fields = ['name_ar', 'name_en']

@admin.register(PredictiveAnalytics)
class PredictiveAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['name', 'prediction_type', 'confidence_level', 'is_active']
    list_filter = ['prediction_type', 'is_active']
    search_fields = ['name', 'description']

@admin.register(ConversationLog)
class ConversationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'assistant', 'message_type', 'sentiment', 'timestamp']
    list_filter = ['message_type', 'sentiment', 'timestamp']
    search_fields = ['user__username', 'conversation_id']

@admin.register(LearningAnalytics)
class LearningAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'analytics_type', 'engagement_score', 'progress_percentage']
    list_filter = ['analytics_type']
    search_fields = ['user__username']