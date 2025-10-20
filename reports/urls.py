from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

def placeholder_view(request):
    return JsonResponse({'message': 'Endpoint under development'}, status=501)

router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
]
