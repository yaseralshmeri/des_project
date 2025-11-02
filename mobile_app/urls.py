# تطبيق الهاتف المحمول - الروابط
# Mobile App - URLs

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# إنشاء router
router = DefaultRouter()
router.register(r'devices', views.MobileDeviceViewSet)
router.register(r'sessions', views.MobileAppSessionViewSet)
router.register(r'notifications', views.MobilePushNotificationViewSet)
router.register(r'feedback', views.MobileAppFeedbackViewSet)
router.register(r'analytics', views.MobileAppAnalyticsViewSet)
router.register(r'stats', views.MobileAppStatsViewSet, basename='mobile-stats')

app_name = 'mobile_app'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here
]