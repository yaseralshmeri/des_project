"""
URLs مبسطة للاختبار
Minimal URLs for testing
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'System is running'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', health_check, name='home'),
]