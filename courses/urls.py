from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CourseOfferingViewSet, AssignmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'offerings', CourseOfferingViewSet)
router.register(r'assignments', AssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]