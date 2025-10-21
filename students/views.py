# FIX: Performance Issues - عالي  
# إصلاح مشاكل N+1 queries وتحسين الأداء باستخدام select_related و prefetch_related

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

from .models import User, Student
from courses.models import Department
from .serializers import UserSerializer, UserCreateSerializer, StudentSerializer, DepartmentSerializer
from .permissions import IsAdmin, IsAdminOrStaff

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    FIX: Added performance optimizations and better error handling
    """
    serializer_class = UserSerializer
    queryset = User.objects.select_related().prefetch_related(
        'student_profile',
        'headed_departments'
    ).order_by('-date_joined')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related for better query optimization"""
        return self.queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAdminOrStaff()]
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        role = serializer.validated_data.get('role', 'STUDENT')
        if role in ['ADMIN', 'STAFF'] and not (self.request.user.is_authenticated and self.request.user.role == 'ADMIN'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can create admin or staff users")
        
        try:
            user = serializer.save()
            logger.info(f"User created: {user.username} with role {role}")
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise
    
    @transaction.atomic
    def perform_update(self, serializer):
        """FIX: Add transaction and better validation"""
        role = serializer.validated_data.get('role')
        if role and role in ['ADMIN', 'STAFF'] and not (self.request.user.is_authenticated and self.request.user.role == 'ADMIN'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can update user roles to admin or staff")
        
        try:
            user = serializer.save()
            logger.info(f"User updated: {user.username}")
        except Exception as e:
            logger.error(f"Failed to update user {serializer.instance.username}: {str(e)}")
            raise
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        FIX: Enhanced login endpoint with better security and error handling
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # FIX: Use Django's authenticate for better security
        user = authenticate(username=username, password=password)
        
        if user and user.is_active:
            try:
                refresh = RefreshToken.for_user(user)
                
                # FIX: Cache user data for better performance
                cache_key = f"user_data_{user.id}"
                user_data = cache.get(cache_key)
                if not user_data:
                    user_data = UserSerializer(user).data
                    cache.set(cache_key, user_data, 300)  # Cache for 5 minutes
                
                logger.info(f"User login successful: {username}")
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_data
                })
            except Exception as e:
                logger.error(f"Login token generation failed for {username}: {str(e)}")
                return Response(
                    {'error': 'Login failed. Please try again.'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        FIX: Get current user profile with caching
        """
        cache_key = f"user_profile_{request.user.id}"
        user_data = cache.get(cache_key)
        
        if not user_data:
            # FIX: Use select_related to avoid additional queries
            user = User.objects.select_related('student_profile').get(id=request.user.id)
            user_data = self.get_serializer(user).data
            cache.set(cache_key, user_data, 300)  # Cache for 5 minutes
        
        return Response(user_data)


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student CRUD operations.
    FIX: Major performance improvements with optimized queries
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['status', 'major', 'current_semester']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']
    queryset = Student.objects.select_related(
        'user'  # Join with User table to avoid N+1 queries
    ).prefetch_related(
        'fees',  # Prefetch related fees
        'enrollments',  # Prefetch enrollments
        'scholarship_applications'  # Prefetch scholarship applications
    ).order_by('-user__date_joined')

    def get_queryset(self):
        """FIX: Performance - Add select_related and prefetch_related to avoid N+1 queries"""
        return self.queryset

    @method_decorator(cache_page(300))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view for better performance"""
        return super().list(request, *args, **kwargs)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            student = serializer.save()
            logger.info(f"Student created: {student.student_id}")
        except Exception as e:
            logger.error(f"Failed to create student: {str(e)}")
            raise
    
    @transaction.atomic
    def perform_update(self, serializer):
        """FIX: Add transaction and logging"""
        try:
            student = serializer.save()
            logger.info(f"Student updated: {student.student_id}")
            
            # Clear related cache
            cache_key = f"user_profile_{student.user.id}"
            cache.delete(cache_key)
        except Exception as e:
            logger.error(f"Failed to update student {serializer.instance.student_id}: {str(e)}")
            raise


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department CRUD operations.
    FIX: Performance optimization with proper joins
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrStaff]
    search_fields = ['name', 'code']
    queryset = Department.objects.select_related(
        'head_of_department'  # Join with User table for department head
    ).order_by('name')
    
    def get_queryset(self):
        """FIX: Performance - Use select_related for head_of_department"""
        return self.queryset

    @method_decorator(cache_page(600))  # Cache for 10 minutes (departments change less frequently)
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view"""
        return super().list(request, *args, **kwargs)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            department = serializer.save()
            logger.info(f"Department created: {department.code}")
        except Exception as e:
            logger.error(f"Failed to create department: {str(e)}")
            raise
    
    @transaction.atomic
    def perform_update(self, serializer):
        """FIX: Add transaction and cache invalidation"""
        try:
            department = serializer.save()
            logger.info(f"Department updated: {department.code}")
            
            # Clear department list cache
            cache.delete('departments_list')
        except Exception as e:
            logger.error(f"Failed to update department {serializer.instance.code}: {str(e)}")
            raise