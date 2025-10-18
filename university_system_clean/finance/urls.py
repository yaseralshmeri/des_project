from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, StudentFeeViewSet, PaymentViewSet, ScholarshipViewSet, ScholarshipApplicationViewSet

router = DefaultRouter()
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'student-fees', StudentFeeViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'scholarships', ScholarshipViewSet)
router.register(r'scholarship-applications', ScholarshipApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
