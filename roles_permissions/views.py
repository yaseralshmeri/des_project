# نظام الأدوار والصلاحيات - Views
# Role-Based Access Control Views

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import (
    Role, Permission, UserRole, RolePermission, 
    SecurityPolicy, OrganizationalUnit, AccessLog
)

User = get_user_model()


def has_permission(user, permission_codename):
    """التحقق من وجود صلاحية للمستخدم"""
    if user.is_superuser:
        return True
    
    # البحث في أدوار المستخدم النشطة
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True,
        status='ACTIVE'
    ).select_related('role')
    
    for user_role in user_roles:
        if user_role.is_valid:
            permissions = user_role.role.get_all_permissions()
            if any(perm.codename == permission_codename for perm in permissions):
                return True
    
    return False


def require_permission(permission_codename):
    """ديكوريتر للتحقق من الصلاحية"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, permission_codename):
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'ليس لديك صلاحية للوصول'}, status=403)
                messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
                return JsonResponse({'error': 'Access denied'}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


@login_required
@require_permission('view_roles')
def roles_list(request):
    """قائمة الأدوار"""
    roles = Role.objects.filter(is_active=True).order_by('hierarchy_level', 'name_ar')
    
    context = {
        'roles': roles
    }
    
    return render(request, 'roles_permissions/roles_list.html', context)


@login_required
@require_permission('view_permissions')
def permissions_list(request):
    """قائمة الصلاحيات"""
    permissions = Permission.objects.filter(is_active=True).order_by('category', 'name_ar')
    
    context = {
        'permissions': permissions
    }
    
    return render(request, 'roles_permissions/permissions_list.html', context)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_roles_api(request):
    """إدارة أدوار المستخدمين عبر API"""
    
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if user_id:
            user_roles = UserRole.objects.filter(
                user_id=user_id,
                is_active=True
            ).select_related('role', 'user')
        else:
            user_roles = UserRole.objects.filter(
                is_active=True
            ).select_related('role', 'user')[:50]
        
        data = [
            {
                'id': str(ur.id),
                'user_name': ur.user.get_full_name(),
                'role_name': ur.role.name_ar,
                'assignment_type': ur.assignment_type,
                'is_primary': ur.is_primary,
                'assigned_at': ur.assigned_at.isoformat(),
                'valid_until': ur.valid_until.isoformat() if ur.valid_until else None,
                'is_valid': ur.is_valid
            }
            for ur in user_roles
        ]
        
        return Response({'user_roles': data})
    
    elif request.method == 'POST' and has_permission(request.user, 'assign_roles'):
        try:
            user_id = request.data.get('user_id')
            role_id = request.data.get('role_id')
            assignment_type = request.data.get('assignment_type', 'PERMANENT')
            is_primary = request.data.get('is_primary', False)
            valid_until = request.data.get('valid_until')
            
            if not user_id or not role_id:
                return Response({'error': 'معرف المستخدم ومعرف الدور مطلوبان'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=user_id)
            role = get_object_or_404(Role, id=role_id)
            
            # التحقق من إمكانية تعيين الدور
            if not role.can_assign_new_users:
                return Response({'error': 'لا يمكن تعيين مستخدمين جدد لهذا الدور'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # إنشاء تعيين الدور
            user_role = UserRole.objects.create(
                user=user,
                role=role,
                assignment_type=assignment_type,
                is_primary=is_primary,
                assigned_by=request.user,
                valid_until=valid_until
            )
            
            # تسجيل في سجل الوصول
            AccessLog.objects.create(
                user=request.user,
                action_type='ROLE_CHANGED',
                action_description=f'تم تعيين دور {role.name_ar} للمستخدم {user.get_full_name()}',
                role_used=role,
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                was_successful=True
            )
            
            return Response({
                'success': True,
                'message': 'تم تعيين الدور بنجاح',
                'user_role_id': str(user_role.id)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({'error': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)


@login_required
@require_permission('view_access_logs')
def access_logs(request):
    """سجلات الوصول"""
    logs = AccessLog.objects.select_related('user', 'permission_used', 'role_used').order_by('-timestamp')
    
    # فلترة
    user_id = request.GET.get('user_id')
    action_type = request.GET.get('action_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if user_id:
        logs = logs.filter(user_id=user_id)
    if action_type:
        logs = logs.filter(action_type=action_type)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    # التقسيم
    logs = logs[:100]
    
    context = {
        'logs': logs,
        'action_types': AccessLog.ACTION_TYPES,
        'users': User.objects.filter(is_active=True).order_by('first_name')
    }
    
    return render(request, 'roles_permissions/access_logs.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """صلاحيات المستخدم الحالي"""
    user_roles = UserRole.objects.filter(
        user=request.user,
        is_active=True,
        status='ACTIVE'
    ).select_related('role')
    
    all_permissions = set()
    roles_info = []
    
    for user_role in user_roles:
        if user_role.is_valid:
            role_permissions = user_role.role.get_all_permissions()
            all_permissions.update(role_permissions)
            
            roles_info.append({
                'role_name': user_role.role.name_ar,
                'role_type': user_role.role.role_type,
                'is_primary': user_role.is_primary,
                'assignment_type': user_role.assignment_type
            })
    
    permissions_data = [
        {
            'codename': perm.codename,
            'name': perm.name_ar,
            'category': perm.category,
            'level': perm.level
        }
        for perm in all_permissions
    ]
    
    return Response({
        'user_id': str(request.user.id),
        'roles': roles_info,
        'permissions': permissions_data,
        'total_permissions': len(permissions_data)
    })


@login_required
@require_permission('manage_security_policies')
def security_policies(request):
    """سياسات الأمان"""
    policies = SecurityPolicy.objects.filter(is_active=True).order_by('policy_type', 'name_ar')
    
    context = {
        'policies': policies
    }
    
    return render(request, 'roles_permissions/security_policies.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_permission(request):
    """فحص صلاحية معينة للمستخدم"""
    permission_codename = request.data.get('permission')
    
    if not permission_codename:
        return Response({'error': 'رمز الصلاحية مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
    
    has_perm = has_permission(request.user, permission_codename)
    
    # تسجيل محاولة الوصول
    AccessLog.objects.create(
        user=request.user,
        action_type='PERMISSION_USED',
        action_description=f'فحص صلاحية: {permission_codename}',
        ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        was_successful=has_perm,
        failure_reason='' if has_perm else 'الصلاحية غير متوفرة'
    )
    
    return Response({
        'has_permission': has_perm,
        'permission': permission_codename,
        'user_id': str(request.user.id)
    })


@login_required
def organizational_structure(request):
    """الهيكل التنظيمي"""
    units = OrganizationalUnit.objects.filter(is_active=True).order_by('hierarchy_level', 'name_ar')
    
    context = {
        'units': units
    }
    
    return render(request, 'roles_permissions/organizational_structure.html', context)