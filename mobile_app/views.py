# تطبيق الهاتف المحمول - العروض
# Mobile App - Views

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    MobileDevice, MobileAppSession, MobilePushNotification,
    MobileAppFeedback, MobileAppAnalytics
)
from .serializers import (
    MobileDeviceSerializer, MobileAppSessionSerializer,
    MobilePushNotificationSerializer, MobileAppFeedbackSerializer,
    MobileAppAnalyticsSerializer, MobileDeviceCreateSerializer,
    MobileAppFeedbackCreateSerializer
)


class MobileDeviceViewSet(viewsets.ModelViewSet):
    """إدارة الأجهزة المحمولة"""
    
    queryset = MobileDevice.objects.all()
    serializer_class = MobileDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.select_related('user')
        return self.queryset.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MobileDeviceCreateSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'])
    def trust_device(self, request, pk=None):
        """وضع الجهاز كموثوق"""
        device = self.get_object()
        device.is_trusted = True
        device.save()
        return Response({'status': 'device_trusted'})
    
    @action(detail=True, methods=['post'])
    def untrust_device(self, request, pk=None):
        """إلغاء الثقة من الجهاز"""
        device = self.get_object()
        device.is_trusted = False
        device.save()
        return Response({'status': 'device_untrusted'})
    
    @action(detail=True, methods=['post'])
    def update_last_seen(self, request, pk=None):
        """تحديث آخر ظهور للجهاز"""
        device = self.get_object()
        device.update_last_seen()
        return Response({'status': 'last_seen_updated'})
    
    @action(detail=False, methods=['get'])
    def my_devices(self, request):
        """أجهزة المستخدم الحالي"""
        devices = MobileDevice.objects.filter(user=request.user)
        serializer = self.get_serializer(devices, many=True)
        return Response(serializer.data)


class MobileAppSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """عرض جلسات التطبيق المحمول"""
    
    queryset = MobileAppSession.objects.all()
    serializer_class = MobileAppSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.select_related('device__user')
        return self.queryset.filter(device__user=user)
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """جلسات المستخدم الحالي"""
        sessions = MobileAppSession.objects.filter(
            device__user=request.user
        ).order_by('-start_time')[:20]
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """الجلسات النشطة"""
        active_sessions = MobileAppSession.objects.filter(
            device__user=request.user,
            end_time__isnull=True
        )
        
        serializer = self.get_serializer(active_sessions, many=True)
        return Response(serializer.data)


class MobilePushNotificationViewSet(viewsets.ModelViewSet):
    """إدارة إشعارات الدفع المحمولة"""
    
    queryset = MobilePushNotification.objects.all()
    serializer_class = MobilePushNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.select_related('device__user')
        return self.queryset.filter(device__user=user)
    
    @action(detail=False, methods=['get'])
    def my_notifications(self, request):
        """إشعارات المستخدم الحالي"""
        notifications = MobilePushNotification.objects.filter(
            device__user=request.user
        ).order_by('-created_at')[:50]
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_clicked(self, request, pk=None):
        """وضع علامة نقر على الإشعار"""
        notification = self.get_object()
        notification.status = 'CLICKED'
        notification.clicked_at = timezone.now()
        notification.save()
        return Response({'status': 'marked_as_clicked'})
    
    @action(detail=False, methods=['post'])
    def send_notification(self, request):
        """إرسال إشعار جديد"""
        # هذا للمديرين فقط
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # منطق إرسال الإشعار
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            # هنا يمكن إضافة منطق إرسال الإشعار فعلياً
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MobileAppFeedbackViewSet(viewsets.ModelViewSet):
    """إدارة ملاحظات التطبيق المحمول"""
    
    queryset = MobileAppFeedback.objects.all()
    serializer_class = MobileAppFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.select_related('user', 'device')
        return self.queryset.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MobileAppFeedbackCreateSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """ملاحظات المستخدم الحالي"""
        feedback = MobileAppFeedback.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def respond_to_feedback(self, request, pk=None):
        """الرد على الملاحظة (للمديرين فقط)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = self.get_object()
        response_text = request.data.get('response', '')
        
        feedback.response = response_text
        feedback.status = 'RESOLVED'
        feedback.resolved_at = timezone.now()
        feedback.assigned_to = request.user
        feedback.save()
        
        return Response({'status': 'response_sent'})


class MobileAppAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """عرض تحليلات التطبيق المحمول"""
    
    queryset = MobileAppAnalytics.objects.all()
    serializer_class = MobileAppAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.select_related('device__user')
        return self.queryset.filter(device__user=user)
    
    @action(detail=False, methods=['get'])
    def app_usage_stats(self, request):
        """إحصائيات استخدام التطبيق"""
        user = request.user
        
        # الحصول على البيانات للأيام الـ30 الماضية
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        if user.is_staff:
            # إحصائيات عامة للمديرين
            analytics = MobileAppAnalytics.objects.filter(
                timestamp__gte=thirty_days_ago
            )
        else:
            # إحصائيات المستخدم الحالي فقط
            analytics = MobileAppAnalytics.objects.filter(
                device__user=user,
                timestamp__gte=thirty_days_ago
            )
        
        stats = {
            'total_events': analytics.count(),
            'events_by_type': dict(
                analytics.values('event_type').annotate(
                    count=Count('id')
                ).values_list('event_type', 'count')
            ),
            'average_load_time': analytics.filter(
                load_time__isnull=False
            ).aggregate(avg_load=Avg('load_time'))['avg_load'],
            'most_used_screens': dict(
                analytics.filter(
                    screen_name__isnull=False
                ).values('screen_name').annotate(
                    count=Count('id')
                ).order_by('-count')[:10].values_list('screen_name', 'count')
            ),
            'crash_count': analytics.filter(event_type='CRASH').count(),
            'error_count': analytics.filter(event_type='ERROR').count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def track_event(self, request):
        """تسجيل حدث جديد"""
        # التحقق من وجود جهاز للمستخدم
        device = MobileDevice.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).first()
        
        if not device:
            return Response(
                {'error': 'No active device found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data.copy()
        data['device'] = device.id
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# عروض إضافية للإحصائيات
class MobileAppStatsViewSet(viewsets.ViewSet):
    """إحصائيات التطبيق المحمول"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """إحصائيات لوحة التحكم"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_devices': MobileDevice.objects.count(),
            'active_devices': MobileDevice.objects.filter(status='ACTIVE').count(),
            'trusted_devices': MobileDevice.objects.filter(is_trusted=True).count(),
            'pending_feedback': MobileAppFeedback.objects.filter(
                status__in=['NEW', 'REVIEWING']
            ).count(),
            'total_sessions_today': MobileAppSession.objects.filter(
                start_time__date=timezone.now().date()
            ).count(),
            'device_types': dict(
                MobileDevice.objects.values('device_type').annotate(
                    count=Count('id')
                ).values_list('device_type', 'count')
            ),
            'app_versions': dict(
                MobileDevice.objects.exclude(
                    app_version=''
                ).values('app_version').annotate(
                    count=Count('id')
                ).values_list('app_version', 'count')
            )
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """إحصائيات المستخدم"""
        user = request.user
        
        user_devices = MobileDevice.objects.filter(user=user)
        user_sessions = MobileAppSession.objects.filter(device__user=user)
        user_feedback = MobileAppFeedback.objects.filter(user=user)
        
        stats = {
            'total_devices': user_devices.count(),
            'active_devices': user_devices.filter(status='ACTIVE').count(),
            'total_sessions': user_sessions.count(),
            'last_session': user_sessions.order_by('-start_time').first(),
            'feedback_count': user_feedback.count(),
            'pending_feedback': user_feedback.filter(
                status__in=['NEW', 'REVIEWING']
            ).count(),
        }
        
        return Response(stats)