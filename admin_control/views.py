# لوحة التحكم الإدارية المتطورة
# Advanced Admin Control Panel Views

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import SystemConfiguration, UserActivity, SystemAlert
import json

User = get_user_model()


def is_admin_user(user):
    """التحقق من أن المستخدم مدير"""
    return user.is_staff or user.role in ['SUPER_ADMIN', 'ADMIN']


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """لوحة التحكم الإدارية الرئيسية"""
    
    # إحصائيات عامة
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
    
    # أنشطة المستخدمين
    recent_activities = UserActivity.objects.select_related('user').order_by('-created_at')[:10]
    
    # التنبيهات النشطة
    active_alerts = SystemAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'recent_activities': recent_activities,
        'active_alerts': active_alerts,
    }
    
    return render(request, 'admin_control/dashboard.html', context)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def system_configurations(request):
    """إدارة إعدادات النظام"""
    
    if request.method == 'GET':
        configs = SystemConfiguration.objects.filter(is_active=True).order_by('category', 'key')
        data = [
            {
                'key': config.key,
                'value': config.get_value(),
                'description': config.description,
                'category': config.category
            }
            for config in configs
        ]
        return Response({'configurations': data})
    
    elif request.method == 'POST':
        try:
            key = request.data.get('key')
            value = request.data.get('value')
            description = request.data.get('description', '')
            category = request.data.get('category', 'general')
            
            if not key or value is None:
                return Response({'error': 'المفتاح والقيمة مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)
            
            # تحويل القيمة إلى JSON إذا كانت dictionary أو list
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            config, created = SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': str(value),
                    'description': description,
                    'category': category,
                    'updated_by': request.user
                }
            )
            
            return Response({
                'success': True,
                'message': 'تم حفظ الإعداد بنجاح' if created else 'تم تحديث الإعداد بنجاح',
                'config': {
                    'key': config.key,
                    'value': config.get_value(),
                    'description': config.description,
                    'category': config.category
                }
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
@user_passes_test(is_admin_user)
def user_activities(request):
    """عرض أنشطة المستخدمين"""
    
    activities = UserActivity.objects.select_related('user').order_by('-created_at')
    
    # فلترة حسب المعاملات
    user_id = request.GET.get('user_id')
    action = request.GET.get('action')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if user_id:
        activities = activities.filter(user_id=user_id)
    if action:
        activities = activities.filter(action=action)
    if date_from:
        activities = activities.filter(created_at__date__gte=date_from)
    if date_to:
        activities = activities.filter(created_at__date__lte=date_to)
    
    # تقسيم الصفحات
    activities = activities[:100]  # الحد الأقصى 100 نشاط
    
    context = {
        'activities': activities,
        'action_choices': UserActivity.ACTION_CHOICES,
        'users': User.objects.filter(is_active=True).order_by('first_name'),
    }
    
    return render(request, 'admin_control/user_activities.html', context)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_stats(request):
    """إحصائيات النظام"""
    
    # إحصائيات المستخدمين
    user_stats = {
        'total': User.objects.count(),
        'active': User.objects.filter(is_active=True).count(),
        'staff': User.objects.filter(is_staff=True).count(),
        'students': User.objects.filter(role='STUDENT').count(),
        'teachers': User.objects.filter(role='TEACHER').count(),
    }
    
    # أنشطة المستخدمين خلال الأسبوع الماضي
    week_ago = timezone.now() - timezone.timedelta(days=7)
    activity_stats = UserActivity.objects.filter(
        created_at__gte=week_ago
    ).values('action').annotate(count=Count('id')).order_by('-count')
    
    # التنبيهات النشطة
    alert_stats = SystemAlert.objects.filter(is_active=True).values('severity').annotate(
        count=Count('id')
    ).order_by('severity')
    
    return Response({
        'user_stats': user_stats,
        'activity_stats': list(activity_stats),
        'alert_stats': list(alert_stats),
        'last_updated': timezone.now().isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_system_alert(request):
    """إنشاء تنبيه نظام"""
    try:
        title = request.data.get('title')
        message = request.data.get('message')
        severity = request.data.get('severity', 'MEDIUM')
        alert_type = request.data.get('alert_type', 'GENERAL')
        
        if not title or not message:
            return Response({'error': 'العنوان والرسالة مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)
        
        alert = SystemAlert.objects.create(
            title=title,
            message=message,
            severity=severity,
            alert_type=alert_type,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'message': 'تم إنشاء التنبيه بنجاح',
            'alert_id': alert.id
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
@user_passes_test(is_admin_user)
def system_maintenance(request):
    """صفحة صيانة النظام"""
    
    # معلومات حالة النظام
    system_info = {
        'total_users': User.objects.count(),
        'active_sessions': UserActivity.objects.filter(
            action='LOGIN',
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).count(),
        'recent_errors': SystemAlert.objects.filter(
            severity__in=['HIGH', 'CRITICAL'],
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
    }
    
    context = {
        'system_info': system_info
    }
    
    return render(request, 'admin_control/maintenance.html', context)


@staff_member_required
def export_user_data(request):
    """تصدير بيانات المستخدمين"""
    # يمكن إضافة تصدير CSV أو Excel هنا
    pass


@staff_member_required
def backup_system(request):
    """نسخ احتياطي للنظام"""
    # يمكن إضافة منطق النسخ الاحتياطي هنا
    pass