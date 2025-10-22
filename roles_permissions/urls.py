"""
Roles & Permissions URLs Configuration
إعدادات روابط الأدوار والصلاحيات
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()

# Register viewsets with the router
# router.register(r'roles', views.RoleViewSet, basename='roles')
# router.register(r'permissions', views.PermissionViewSet, basename='permissions')

app_name = 'roles_permissions'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    
    # Web interface routes (placeholder)
    # path('', views.RolesListView.as_view(), name='roles-list'),
    # path('roles/', views.RoleManagementView.as_view(), name='role-management'),
    # path('permissions/', views.PermissionManagementView.as_view(), name='permission-management'),
]