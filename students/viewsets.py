"""
Students App ViewSets for DRF API
ViewSets لتطبيق الطلاب في DRF API
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Student
from .serializers import UserSerializer, StudentSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        if user.is_admin or user.is_staff_member:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Invalid old password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student model
    """
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        if user.is_admin or user.is_staff_member or user.is_teacher:
            return Student.objects.all()
        elif user.is_student:
            return Student.objects.filter(user=user)
        else:
            return Student.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current student profile"""
        try:
            student = Student.objects.get(user=request.user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def academic_record(self, request, pk=None):
        """Get student academic record"""
        student = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin or request.user.is_staff_member or 
                request.user.is_teacher or request.user == student.user):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get academic data (implement based on your models)
        data = {
            'student': StudentSerializer(student).data,
            'gpa': student.gpa,
            'total_credits': student.total_credits_earned,
            'academic_status': student.academic_status,
            # Add more academic data as needed
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search students"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        
        queryset = self.get_queryset().filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(user__email__icontains=query)
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)