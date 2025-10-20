from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'smart_ai'

urlpatterns = [
    # Student Performance Prediction APIs
    path('predict-performance/', views.predict_student_performance, name='predict_performance'),
    path('student-predictions/<int:student_id>/', views.get_student_predictions, name='student_predictions'),
    
    # Smart Recommendations APIs
    path('generate-recommendations/', views.generate_course_recommendations, name='generate_recommendations'),
    path('student-recommendations/<int:student_id>/', views.get_student_recommendations, name='student_recommendations'),
    
    # AI Chatbot APIs
    path('chat/', views.chat_with_ai, name='chat_with_ai'),
    
    # Security AI APIs
    path('security-analysis/', views.analyze_security_event, name='security_analysis'),
    
    # Smart Scheduling APIs
    path('generate-schedule/', views.generate_smart_schedule, name='generate_schedule'),
    
    # Dashboard APIs
    path('dashboard/', views.get_ai_dashboard_data, name='ai_dashboard'),
    
    # Generic Model APIs
    path('models/', views.AIAnalyticsModelListView.as_view(), name='ai_models'),
    path('predictions/', views.StudentPerformancePredictionListView.as_view(), name='predictions_list'),
    path('recommendations/', views.SmartRecommendationListView.as_view(), name='recommendations_list'),
    path('security-alerts/', views.AISecurityAlertListView.as_view(), name='security_alerts'),
]