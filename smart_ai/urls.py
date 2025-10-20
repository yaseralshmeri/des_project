# توجيهات الذكاء الاصطناعي
# AI URL Configuration

from django.urls import path, include
from . import views

app_name = 'smart_ai'

urlpatterns = [
    # واجهات المساعد الذكي
    path('assistant/', views.AIStudentAssistantView.as_view(), name='ai_assistant'),
    
    # واجهات التنبؤ بالأداء
    path('predict-performance/', views.StudentPerformancePredictionView.as_view(), name='predict_performance'),
    
    # واجهات التوصيات الذكية
    path('recommendations/', views.SmartRecommendationsView.as_view(), name='smart_recommendations'),
    path('recommendations/<int:recommendation_id>/update/', views.SmartRecommendationsView.as_view(), name='update_recommendation'),
    
    # واجهات التحليلات التنبؤية
    path('analytics/', views.PredictiveAnalyticsView.as_view(), name='predictive_analytics'),
    
    # واجهات إضافية
    path('generate-schedule/', views.generate_smart_schedule, name='generate_schedule'),
    path('dashboard-stats/', views.ai_dashboard_stats, name='dashboard_stats'),
]