"""
Advanced API Views for University Management System
وجهات API متطورة لنظام إدارة الجامعة
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from students.models import Student
from courses.models import Course
from finance.models import Payment, StudentFee
from ai.models import StudentPerformancePrediction, EarlyWarningSystem
from notifications.models import Notification
from admin_control.models import UserActivity, SystemAlert
from roles_permissions.models import Role, Permission, UserRole

import logging
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class
    فئة التصفح القياسية
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseAPIViewSet(viewsets.ModelViewSet):
    """
    Base viewset with common functionality
    ViewSet أساسي مع وظائف مشتركة
    """
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_permissions(self):
        """
        Get permissions based on action
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Override create to log activity"""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            self.log_activity('CREATE', request, response.data.get('id'))
        
        return response
    
    def update(self, request, *args, **kwargs):
        """Override update to log activity"""
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            self.log_activity('UPDATE', request, kwargs.get('pk'))
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to log activity"""
        obj_id = kwargs.get('pk')
        response = super().destroy(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.log_activity('DELETE', request, obj_id)
        
        return response
    
    def log_activity(self, action, request, object_id=None):
        """Log user activity"""
        try:
            UserActivity.objects.create(
                user=request.user,
                action=action,
                model_name=self.queryset.model.__name__.lower(),
                object_id=str(object_id) if object_id else '',
                description=f"{action} {self.queryset.model.__name__}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000]
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class StudentViewSet(BaseAPIViewSet):
    """
    Student management API
    واجهة إدارة الطلاب
    """
    queryset = Student.objects.select_related('user').all()
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'major']
    filterset_fields = ['current_semester', 'status', 'major']
    ordering_fields = ['enrollment_date', 'gpa', 'current_semester']
    ordering = ['-enrollment_date']
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get student performance data"""
        student = self.get_object()
        
        # Get performance predictions
        predictions = StudentPerformancePrediction.objects.filter(
            student=student
        ).order_by('-prediction_date')[:10]
        
        # Get early warnings
        warnings = EarlyWarningSystem.objects.filter(
            student=student,
            status='ACTIVE'
        )
        
        # Calculate performance metrics
        performance_data = {
            'student_id': student.student_id,
            'current_gpa': float(student.gpa),
            'current_semester': student.current_semester,
            'status': student.status,
            'predictions': [
                {
                    'type': p.prediction_type,
                    'predicted_value': p.predicted_value,
                    'confidence_score': p.confidence_score,
                    'risk_level': p.risk_level,
                    'date': p.prediction_date
                } for p in predictions
            ],
            'warnings': [
                {
                    'type': w.warning_type,
                    'severity': w.severity_level,
                    'title': w.title,
                    'description': w.description,
                    'date': w.created_at
                } for w in warnings
            ]
        }
        
        return Response(performance_data)
    
    @action(detail=True, methods=['get'])
    def financial_status(self, request, pk=None):
        """Get student financial status"""
        student = self.get_object()
        
        # Get financial data
        fees = StudentFee.objects.filter(student=student)
        payments = Payment.objects.filter(student=student)
        
        total_fees = fees.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_paid = payments.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        outstanding = total_fees - total_paid
        
        financial_data = {
            'total_fees': float(total_fees),
            'total_paid': float(total_paid),
            'outstanding_amount': float(outstanding),
            'payment_history': [
                {
                    'amount': float(p.amount),
                    'date': p.payment_date,
                    'method': p.payment_method,
                    'status': p.status
                } for p in payments.order_by('-payment_date')[:10]
            ]
        }
        
        return Response(financial_data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get student statistics"""
        cache_key = 'student_statistics'
        stats = cache.get(cache_key)
        
        if not stats:
            total_students = Student.objects.count()
            active_students = Student.objects.filter(status='ACTIVE').count()
            graduated_students = Student.objects.filter(status='GRADUATED').count()
            
            # GPA distribution
            gpa_ranges = {
                'excellent': Student.objects.filter(gpa__gte=3.5).count(),
                'good': Student.objects.filter(gpa__gte=2.5, gpa__lt=3.5).count(),
                'average': Student.objects.filter(gpa__gte=2.0, gpa__lt=2.5).count(),
                'below_average': Student.objects.filter(gpa__lt=2.0).count()
            }
            
            # Semester distribution
            semester_distribution = Student.objects.values('current_semester').annotate(
                count=Count('id')
            ).order_by('current_semester')
            
            stats = {
                'total_students': total_students,
                'active_students': active_students,
                'graduated_students': graduated_students,
                'average_gpa': Student.objects.aggregate(avg_gpa=Avg('gpa'))['avg_gpa'],
                'gpa_distribution': gpa_ranges,
                'semester_distribution': list(semester_distribution)
            }
            
            # Cache for 30 minutes
            cache.set(cache_key, stats, 30 * 60)
        
        return Response(stats)


class DashboardAPIViewSet(viewsets.ViewSet):
    """
    Dashboard API for admin interface
    واجهة لوحة التحكم للإدارة
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get dashboard overview data"""
        cache_key = f'dashboard_overview_{request.user.id}'
        overview_data = cache.get(cache_key)
        
        if not overview_data:
            # Basic statistics
            total_students = Student.objects.count()
            total_courses = Course.objects.count() if hasattr(Course, 'objects') else 0
            total_users = User.objects.count()
            active_warnings = EarlyWarningSystem.objects.filter(status='ACTIVE').count()
            
            # Recent activities
            recent_activities = UserActivity.objects.select_related('user').order_by('-created_at')[:10]
            
            # Financial overview
            this_month = timezone.now().replace(day=1)
            monthly_revenue = Payment.objects.filter(
                payment_date__gte=this_month,
                status='COMPLETED'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # AI insights
            high_risk_students = EarlyWarningSystem.objects.filter(
                severity_level='HIGH',
                status='ACTIVE'
            ).count()
            
            overview_data = {
                'statistics': {
                    'total_students': total_students,
                    'total_courses': total_courses,
                    'total_users': total_users,
                    'active_warnings': active_warnings,
                    'high_risk_students': high_risk_students,
                    'monthly_revenue': float(monthly_revenue)
                },
                'recent_activities': [
                    {
                        'user': activity.user.get_full_name() or activity.user.username,
                        'action': activity.action,
                        'model': activity.model_name,
                        'description': activity.description,
                        'timestamp': activity.created_at
                    } for activity in recent_activities
                ]
            }
            
            # Cache for 10 minutes
            cache.set(cache_key, overview_data, 10 * 60)
        
        return Response(overview_data)
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get system alerts"""
        alerts = SystemAlert.objects.filter(
            is_active=True
        ).order_by('-created_at')[:20]
        
        alert_data = [
            {
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'alert_type': alert.alert_type,
                'created_at': alert.created_at
            } for alert in alerts
        ]
        
        return Response(alert_data)
    
    @action(detail=False, methods=['get'])
    def performance_metrics(self, request):
        """Get system performance metrics"""
        # Get performance data for charts
        last_30_days = timezone.now() - timedelta(days=30)
        
        # Student registrations over time
        student_registrations = Student.objects.filter(
            enrollment_date__gte=last_30_days
        ).extra(
            select={'day': 'date(enrollment_date)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Payment trends
        payment_trends = Payment.objects.filter(
            payment_date__gte=last_30_days,
            status='COMPLETED'
        ).extra(
            select={'day': 'date(payment_date)'}
        ).values('day').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('day')
        
        # Warning trends
        warning_trends = EarlyWarningSystem.objects.filter(
            created_at__gte=last_30_days
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        metrics_data = {
            'student_registrations': list(student_registrations),
            'payment_trends': [
                {
                    'day': item['day'],
                    'total_amount': float(item['total'] or 0),
                    'transaction_count': item['count']
                } for item in payment_trends
            ],
            'warning_trends': list(warning_trends)
        }
        
        return Response(metrics_data)


class NotificationAPIViewSet(BaseAPIViewSet):
    """
    Notification management API
    واجهة إدارة الإشعارات
    """
    queryset = Notification.objects.select_related('recipient', 'channel').all()
    search_fields = ['subject', 'message']
    filterset_fields = ['status', 'priority', 'channel']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter notifications for current user"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular users only see their own notifications
            queryset = queryset.filter(recipient=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        
        if notification.recipient != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.mark_as_read()
        
        return Response({'status': 'marked_as_read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count for current user"""
        count = Notification.objects.filter(
            recipient=request.user,
            status__in=['SENT', 'DELIVERED']
        ).count()
        
        return Response({'count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for current user"""
        updated = Notification.objects.filter(
            recipient=request.user,
            status__in=['SENT', 'DELIVERED']
        ).update(
            status='READ',
            read_at=timezone.now()
        )
        
        return Response({'updated_count': updated})


class AIAnalyticsAPIViewSet(viewsets.ViewSet):
    """
    AI Analytics API
    واجهة تحليلات الذكاء الاصطناعي
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def student_risk_analysis(self, request):
        """Get student risk analysis"""
        # Get at-risk students
        high_risk_students = EarlyWarningSystem.objects.filter(
            severity_level__in=['HIGH', 'CRITICAL'],
            status='ACTIVE'
        ).select_related('student__user')
        
        risk_data = []
        for warning in high_risk_students:
            student_data = {
                'student_id': warning.student.student_id,
                'student_name': warning.student.user.get_full_name(),
                'warning_type': warning.warning_type,
                'severity': warning.severity_level,
                'title': warning.title,
                'confidence_score': warning.confidence_score,
                'created_at': warning.created_at,
                'recommended_actions': warning.recommended_actions
            }
            risk_data.append(student_data)
        
        return Response({
            'high_risk_count': len(risk_data),
            'students': risk_data
        })
    
    @action(detail=False, methods=['get'])
    def performance_predictions(self, request):
        """Get performance predictions summary"""
        # Get recent predictions
        predictions = StudentPerformancePrediction.objects.filter(
            prediction_date__gte=timezone.now() - timedelta(days=30)
        ).select_related('student__user')
        
        # Group by prediction type
        prediction_summary = {}
        for prediction in predictions:
            pred_type = prediction.prediction_type
            if pred_type not in prediction_summary:
                prediction_summary[pred_type] = {
                    'count': 0,
                    'average_confidence': 0,
                    'risk_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
                }
            
            prediction_summary[pred_type]['count'] += 1
            prediction_summary[pred_type]['average_confidence'] += prediction.confidence_score
            
            if prediction.risk_level:
                prediction_summary[pred_type]['risk_distribution'][prediction.risk_level] += 1
        
        # Calculate averages
        for pred_type in prediction_summary:
            if prediction_summary[pred_type]['count'] > 0:
                prediction_summary[pred_type]['average_confidence'] /= prediction_summary[pred_type]['count']
        
        return Response(prediction_summary)
    
    @action(detail=False, methods=['post'])
    def generate_insights(self, request):
        """Trigger AI insight generation"""
        # This would typically trigger background tasks
        # For now, we'll return a simple response
        
        return Response({
            'status': 'initiated',
            'message': 'AI insight generation started',
            'estimated_completion': timezone.now() + timedelta(minutes=10)
        })


class SystemManagementAPIViewSet(viewsets.ViewSet):
    """
    System management API
    واجهة إدارة النظام
    """
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def health_check(self, request):
        """System health check"""
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now(),
            'database': 'connected',
            'cache': 'available',
            'version': '2.0.0'
        }
        
        # Test database connection
        try:
            User.objects.count()
        except Exception as e:
            health_data['database'] = f'error: {str(e)}'
            health_data['status'] = 'unhealthy'
        
        # Test cache
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') != 'ok':
                raise Exception('Cache not working')
        except Exception as e:
            health_data['cache'] = f'error: {str(e)}'
            health_data['status'] = 'unhealthy'
        
        return Response(health_data)
    
    @action(detail=False, methods=['get'])
    def system_stats(self, request):
        """Get system statistics"""
        stats = {
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'staff': User.objects.filter(is_staff=True).count()
            },
            'students': {
                'total': Student.objects.count(),
                'active': Student.objects.filter(status='ACTIVE').count()
            },
            'activities': {
                'today': UserActivity.objects.filter(
                    created_at__date=timezone.now().date()
                ).count(),
                'this_week': UserActivity.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count()
            }
        }
        
        return Response(stats)


class RolePermissionAPIViewSet(BaseAPIViewSet):
    """
    Role and Permission management API
    واجهة إدارة الأدوار والصلاحيات
    """
    queryset = Role.objects.all()
    search_fields = ['name', 'display_name', 'description']
    filterset_fields = ['role_type', 'is_active']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get role permissions"""
        role = self.get_object()
        permissions = role.get_all_permissions()
        
        permission_data = [
            {
                'id': perm.permission.id,
                'name': perm.permission.name,
                'display_name': perm.permission.display_name,
                'permission_type': perm.permission.permission_type,
                'resource_name': perm.permission.resource_name,
                'is_active': perm.is_active,
                'granted_at': perm.granted_at
            } for perm in permissions
        ]
        
        return Response(permission_data)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users with this role"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(
            role=role,
            is_active=True
        ).select_related('user')
        
        user_data = [
            {
                'id': ur.user.id,
                'username': ur.user.username,
                'full_name': ur.user.get_full_name(),
                'email': ur.user.email,
                'assigned_at': ur.created_at,
                'effective_from': ur.effective_from,
                'effective_until': ur.effective_until
            } for ur in user_roles
        ]
        
        return Response(user_data)


# Simple API functions for basic endpoints
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db import connection

@api_view(['GET'])
def api_root(request):
    """
    API Root endpoint
    نقطة البداية للواجهة البرمجية
    """
    return Response({
        'message': 'مرحباً بك في واجهة برمجة تطبيقات نظام إدارة الجامعة',
        'version': '2.0.1',
        'endpoints': {
            'documentation': '/api/docs/',
            'health': '/api/health/',
        },
        'status': 'active'
    })


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    نقطة فحص صحة النظام
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = True
    except Exception:
        db_status = False
    
    return Response({
        'status': 'healthy' if db_status else 'unhealthy',
        'timestamp': timezone.now(),
        'database': 'connected' if db_status else 'disconnected',
        'version': '2.0.1'
    })