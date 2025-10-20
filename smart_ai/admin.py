from django.contrib import admin
from .models import (
    AIAnalyticsModel, StudentPerformancePrediction, AIChatBot, 
    ChatMessage, SmartRecommendation, PredictiveAnalytics,
    AISecurityAlert, SmartScheduling
)

@admin.register(AIAnalyticsModel)
class AIAnalyticsModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'accuracy_score', 'is_active', 'last_trained']
    list_filter = ['model_type', 'is_active']
    search_fields = ['name', 'description']

@admin.register(StudentPerformancePrediction)
class StudentPerformancePredictionAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'predicted_grade', 'success_probability', 'risk_level']
    list_filter = ['risk_level', 'prediction_date']
    search_fields = ['student__user__username', 'course__name']

@admin.register(AIChatBot)
class AIChatBotAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_type', 'session_id', 'is_active', 'created_at']
    list_filter = ['chat_type', 'is_active']
    search_fields = ['user__username', 'session_id']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chatbot', 'user_intent', 'confidence_score', 'is_resolved', 'timestamp']
    list_filter = ['is_resolved', 'timestamp']
    search_fields = ['message', 'response']

@admin.register(SmartRecommendation)
class SmartRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'recommendation_type', 'title', 'priority_score', 'is_accepted']
    list_filter = ['recommendation_type', 'is_viewed', 'is_accepted']
    search_fields = ['student__user__username', 'title']

@admin.register(PredictiveAnalytics)
class PredictiveAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['title', 'analysis_type', 'created_by', 'is_approved', 'analysis_date']
    list_filter = ['analysis_type', 'is_approved']
    search_fields = ['title', 'created_by__username']

@admin.register(AISecurityAlert)
class AISecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'is_resolved', 'detected_at']
    list_filter = ['alert_type', 'severity', 'is_resolved']
    search_fields = ['title', 'ip_address']
    
    def get_readonly_fields(self, request, obj=None):
        return ['detected_at', 'ip_address', 'user_agent']

@admin.register(SmartScheduling)
class SmartSchedulingAdmin(admin.ModelAdmin):
    list_display = ['name', 'semester', 'algorithm_used', 'fitness_score', 'is_optimal', 'is_approved']
    list_filter = ['algorithm_used', 'is_optimal', 'is_approved']
    search_fields = ['name', 'semester']