"""
URL Configuration for Notifications API
تكوين الروابط لواجهة برمجة تطبيقات الإشعارات
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet)

app_name = 'notifications'

urlpatterns = [
    path('', include(router.urls)),
    path('send/', views.send_notification, name='send_notification'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]