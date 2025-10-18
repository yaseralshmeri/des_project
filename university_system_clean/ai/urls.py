from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerformancePredictionViewSet, CourseRecommendationViewSet, StudyPatternViewSet
from . import ml_predictions

router = DefaultRouter()
router.register(r'predictions', PerformancePredictionViewSet, basename='performanceprediction')
router.register(r'recommendations', CourseRecommendationViewSet, basename='courserecommendation')
router.register(r'study-patterns', StudyPatternViewSet, basename='studypattern')

urlpatterns = [
    path('', include(router.urls)),
    
    # AI/ML Prediction endpoints
    path('predict-performance/', ml_predictions.predict_student_performance, name='predict-performance'),
    path('recommend-courses/', ml_predictions.recommend_courses, name='recommend-courses'),
    path('analyze-study-patterns/', ml_predictions.analyze_study_patterns, name='analyze-study-patterns'),
]
