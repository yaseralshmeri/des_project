"""
API URLs Configuration
تكوين روابط واجهة برمجة التطبيقات
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# API root view
app_name = 'api'

urlpatterns = [
    # API Root
    path('', views.api_root, name='api_root'),
    
    # Health check endpoint
    path('health/', views.health_check, name='api_health_check'),
    
    # Include router URLs
    path('', include(router.urls)),
]