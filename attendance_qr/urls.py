"""
Attendance QR URLs Configuration
إعدادات روابط حضور الQR
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()

# Register viewsets with the router
# router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
# router.register(r'qr-codes', views.QRCodeViewSet, basename='qrcode')

app_name = 'attendance_qr'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    
    # Web interface routes (placeholder)
    # path('', views.AttendanceListView.as_view(), name='attendance-list'),
    # path('generate-qr/', views.GenerateQRView.as_view(), name='generate-qr'),
    # path('scan/', views.ScanQRView.as_view(), name='scan-qr'),
]