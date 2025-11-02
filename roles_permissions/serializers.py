# نظام الأدوار والصلاحيات - المسلسلات
# Roles and Permissions System - Serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Role, Permission, RolePermission, UserRole,
    PermissionGroup, RoleHierarchy, AccessLog,
    ResourceAccess, DynamicPermission
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """مسلسل المستخدم الأساسي"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class PermissionSerializer(serializers.ModelSerializer):
    """مسلسل الصلاحيات"""
    
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    
    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionGroupSerializer(serializers.ModelSerializer):
    """مسلسل مجموعات الصلاحيات"""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = PermissionGroup
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class RolePermissionSerializer(serializers.ModelSerializer):
    """مسلسل ربط الأدوار بالصلاحيات"""
    
    permission = PermissionSerializer(read_only=True)
    granted_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = RolePermission
        fields = '__all__'
        read_only_fields = ['id', 'granted_at']


class RoleSerializer(serializers.ModelSerializer):
    """مسلسل الأدوار"""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    role_permissions = RolePermissionSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    total_permissions = serializers.SerializerMethodField()
    active_permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_permissions(self, obj):
        return obj.role_permissions.count()
    
    def get_active_permissions(self, obj):
        return obj.role_permissions.filter(is_active=True).count()


class UserRoleSerializer(serializers.ModelSerializer):
    """مسلسل ربط المستخدمين بالأدوار"""
    
    user = UserBasicSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    assigned_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class RoleHierarchySerializer(serializers.ModelSerializer):
    """مسلسل التسلسل الهرمي للأدوار"""
    
    parent_role = RoleSerializer(read_only=True)
    child_role = RoleSerializer(read_only=True)
    
    class Meta:
        model = RoleHierarchy
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AccessLogSerializer(serializers.ModelSerializer):
    """مسلسل سجل الوصول"""
    
    user = UserBasicSerializer(read_only=True)
    permission = PermissionSerializer(read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = AccessLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class ResourceAccessSerializer(serializers.ModelSerializer):
    """مسلسل الوصول للموارد"""
    
    permission = PermissionSerializer(read_only=True)
    
    class Meta:
        model = ResourceAccess
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DynamicPermissionSerializer(serializers.ModelSerializer):
    """مسلسل الصلاحيات الديناميكية"""
    
    user = UserBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = DynamicPermission
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# مسلسلات مبسطة للإنشاء والتحديث
class RoleCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء دور جديد"""
    
    permissions = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ['name', 'display_name', 'description', 'role_type', 'is_active', 'permissions']
    
    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        request = self.context.get('request')
        
        if request and request.user:
            validated_data['created_by'] = request.user
        
        role = super().create(validated_data)
        
        # ربط الصلاحيات بالدور
        for permission_id in permissions:
            try:
                permission = Permission.objects.get(id=permission_id)
                RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    granted_by=request.user if request else None,
                    is_active=True
                )
            except Permission.DoesNotExist:
                continue
        
        return role


class PermissionCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء صلاحية جديدة"""
    
    class Meta:
        model = Permission
        fields = [
            'name', 'display_name', 'description', 'permission_type',
            'resource_name', 'is_active'
        ]


class UserRoleAssignSerializer(serializers.ModelSerializer):
    """مسلسل تعيين دور للمستخدم"""
    
    user_id = serializers.UUIDField(write_only=True)
    role_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = UserRole
        fields = ['user_id', 'role_id', 'effective_from', 'effective_until', 'notes']
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        role_id = validated_data.pop('role_id')
        
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
        except (User.DoesNotExist, Role.DoesNotExist):
            raise serializers.ValidationError("المستخدم أو الدور غير موجود")
        
        validated_data['user'] = user
        validated_data['role'] = role
        
        request = self.context.get('request')
        if request and request.user:
            validated_data['assigned_by'] = request.user
        
        return super().create(validated_data)


class RolePermissionAssignSerializer(serializers.ModelSerializer):
    """مسلسل تعيين صلاحية للدور"""
    
    role_id = serializers.UUIDField(write_only=True)
    permission_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['role_id', 'permission_id', 'is_active', 'conditions']
    
    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
        permission_id = validated_data.pop('permission_id')
        
        try:
            role = Role.objects.get(id=role_id)
            permission = Permission.objects.get(id=permission_id)
        except (Role.DoesNotExist, Permission.DoesNotExist):
            raise serializers.ValidationError("الدور أو الصلاحية غير موجودة")
        
        validated_data['role'] = role
        validated_data['permission'] = permission
        
        request = self.context.get('request')
        if request and request.user:
            validated_data['granted_by'] = request.user
        
        return super().create(validated_data)


# مسلسلات للتقارير والإحصائيات
class UserPermissionsReportSerializer(serializers.Serializer):
    """مسلسل تقرير صلاحيات المستخدم"""
    
    user = UserBasicSerializer()
    roles = RoleSerializer(many=True)
    total_permissions = serializers.IntegerField()
    direct_permissions = serializers.ListField()
    inherited_permissions = serializers.ListField()
    effective_permissions = serializers.ListField()


class RoleUsageReportSerializer(serializers.Serializer):
    """مسلسل تقرير استخدام الأدوار"""
    
    role = RoleSerializer()
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    recent_assignments = serializers.IntegerField()
    usage_percentage = serializers.FloatField()


class PermissionAuditSerializer(serializers.Serializer):
    """مسلسل مراجعة الصلاحيات"""
    
    permission = PermissionSerializer()
    total_roles = serializers.IntegerField()
    total_users = serializers.IntegerField()
    last_used = serializers.DateTimeField()
    usage_frequency = serializers.IntegerField()


class AccessStatisticsSerializer(serializers.Serializer):
    """مسلسل إحصائيات الوصول"""
    
    total_access_attempts = serializers.IntegerField()
    successful_accesses = serializers.IntegerField()
    failed_accesses = serializers.IntegerField()
    most_accessed_resources = serializers.ListField()
    access_by_hour = serializers.DictField()
    access_by_user = serializers.DictField()


# مسلسلات للتصفية والبحث
class RoleFilterSerializer(serializers.Serializer):
    """مسلسل تصفية الأدوار"""
    
    role_type = serializers.ChoiceField(choices=Role.ROLE_TYPES, required=False)
    is_active = serializers.BooleanField(required=False)
    created_from = serializers.DateTimeField(required=False)
    created_to = serializers.DateTimeField(required=False)


class PermissionFilterSerializer(serializers.Serializer):
    """مسلسل تصفية الصلاحيات"""
    
    permission_type = serializers.ChoiceField(choices=Permission.PERMISSION_TYPES, required=False)
    resource_name = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)


class UserRoleFilterSerializer(serializers.Serializer):
    """مسلسل تصفية تعيين الأدوار"""
    
    user_id = serializers.UUIDField(required=False)
    role_id = serializers.UUIDField(required=False)
    is_active = serializers.BooleanField(required=False)
    effective_date = serializers.DateTimeField(required=False)