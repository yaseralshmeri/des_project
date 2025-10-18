from rest_framework import viewsets
from .models import PerformancePrediction, CourseRecommendation, StudyPattern
from .serializers import (PerformancePredictionSerializer, CourseRecommendationSerializer,
                          StudyPatternSerializer)
from students.permissions import IsAdminOrStaff

class PerformancePredictionViewSet(viewsets.ModelViewSet):
    queryset = PerformancePrediction.objects.all()
    serializer_class = PerformancePredictionSerializer
    permission_classes = [IsAdminOrStaff]

class CourseRecommendationViewSet(viewsets.ModelViewSet):
    queryset = CourseRecommendation.objects.all()
    serializer_class = CourseRecommendationSerializer
    permission_classes = [IsAdminOrStaff]

class StudyPatternViewSet(viewsets.ModelViewSet):
    queryset = StudyPattern.objects.all()
    serializer_class = StudyPatternSerializer
    permission_classes = [IsAdminOrStaff]
