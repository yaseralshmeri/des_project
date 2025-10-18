"""
Notification views for University Management System
مشاهدات الإشعارات لنظام إدارة الجامعة
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import (
    Notification, 
    NotificationType, 
    NotificationTemplate,
    UserNotificationPreference
)
from .serializers import (
    NotificationSerializer,
    NotificationTypeSerializer,
    NotificationTemplateSerializer,
    UserNotificationPreferenceSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter notifications by recipient"""
        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'notification_type', 'sender'
        )
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type__name=notification_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all user notifications as read"""
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'status': f'{updated} notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get notification summary by priority and type"""
        notifications = Notification.objects.filter(recipient=request.user)
        
        summary = {
            'total': notifications.count(),
            'unread': notifications.filter(is_read=False).count(),
            'by_priority': {},
            'by_type': {},
        }
        
        # Count by priority
        for priority_val, priority_name in Notification.PRIORITY_CHOICES:
            count = notifications.filter(priority=priority_val).count()
            summary['by_priority'][priority_name.lower()] = count
        
        # Count by type
        types = NotificationType.objects.all()
        for ntype in types:
            count = notifications.filter(notification_type=ntype).count()
            summary['by_type'][ntype.name.lower()] = count
        
        return Response(summary)


class NotificationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notification types (read-only)
    """
    queryset = NotificationType.objects.filter(is_active=True)
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticated]


class NotificationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notification templates (read-only for regular users)
    """
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]


class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notification preferences
    """
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserNotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create user notification preferences"""
        obj, created = UserNotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    """
    Send a notification to users
    Admin/Staff only endpoint
    """
    if not (request.user.is_staff_member or request.user.is_admin):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    data = request.data
    
    # Validate required fields
    required_fields = ['title', 'message', 'recipients']
    for field in required_fields:
        if field not in data:
            return Response(
                {'error': f'Field {field} is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Get recipients
    recipients = data['recipients']
    if recipients == 'all':
        from students.models import User
        recipients = User.objects.all()
    elif isinstance(recipients, list):
        from students.models import User
        recipients = User.objects.filter(id__in=recipients)
    else:
        return Response(
            {'error': 'Invalid recipients format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get notification type
    notification_type = None
    if 'notification_type' in data:
        try:
            notification_type = NotificationType.objects.get(
                name=data['notification_type']
            )
        except NotificationType.DoesNotExist:
            pass
    
    # Create notifications
    created_count = 0
    for recipient in recipients:
        notification = Notification.objects.create(
            title=data['title'],
            message=data['message'],
            notification_type=notification_type,
            recipient=recipient,
            sender=request.user,
            priority=data.get('priority', 2),
            send_email=data.get('send_email', False),
            send_sms=data.get('send_sms', False),
            action_url=data.get('action_url', ''),
            action_text=data.get('action_text', ''),
        )
        created_count += 1
    
    return Response({
        'status': 'success',
        'created_count': created_count,
        'message': f'Sent notification to {created_count} recipients'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all user notifications as read"""
    updated = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'status': 'success',
        'updated_count': updated,
        'message': f'Marked {updated} notifications as read'
    })