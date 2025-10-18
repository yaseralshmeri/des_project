from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, TeacherViewSet, AttendanceViewSet, LeaveViewSet, SalaryViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'salaries', SalaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
