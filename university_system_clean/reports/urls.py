from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentPerformanceReportViewSet, CourseAnalyticsViewSet, EnrollmentStatisticsViewSet

router = DefaultRouter()
router.register(r'student-reports', StudentPerformanceReportViewSet)
router.register(r'course-analytics', CourseAnalyticsViewSet)
router.register(r'enrollment-stats', EnrollmentStatisticsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
