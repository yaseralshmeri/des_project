"""
Advanced Role-Based Access Control System
نظام تحكم بالأدوار والصلاحيات المتطور
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.cache import cache
from django.utils import timezone
import json

User = get_user_model()


class Department(models.Model):
    """
    Enhanced Department model with hierarchy support
    نموذج القسم المحسن مع دعم التسلسل الهرمي
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_departments')
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    budget_code = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_full_hierarchy(self):
        """Get full department hierarchy path"""
        hierarchy = [self.name]
        parent = self.parent_department
        while parent:
            hierarchy.insert(0, parent.name)
            parent = parent.parent_department
        return ' > '.join(hierarchy)
    
    def get_all_subdepartments(self):
        """Get all subdepartments recursively"""
        subdepts = list(self.sub_departments.all())
        for subdept in self.sub_departments.all():
            subdepts.extend(subdept.get_all_subdepartments())
        return subdepts


class Role(models.Model):
    """
    Advanced role system with hierarchical permissions
    نظام أدوار متطور مع صلاحيات هرمية
    """
    ROLE_TYPES = [
        ('SYSTEM', 'System Role'),
        ('DEPARTMENT', 'Department Role'),
        ('CUSTOM', 'Custom Role'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField()
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default='CUSTOM')
    
    # Hierarchy support
    parent_role = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_roles')
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority")
    
    # Department association
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='roles')
    
    # Role settings
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(null=True, blank=True, help_text="Maximum users that can have this role")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['role_type', 'is_active']),
            models.Index(fields=['department', 'is_active']),
        ]
    
    def __str__(self):
        return self.display_name
    
    def get_all_permissions(self):
        """Get all permissions including inherited from parent roles"""
        permissions = set(self.role_permissions.filter(is_active=True))
        
        # Add permissions from parent roles
        parent = self.parent_role
        while parent:
            permissions.update(parent.role_permissions.filter(is_active=True))
            parent = parent.parent_role
        
        return permissions
    
    def can_assign_to_user(self, user):
        """Check if role can be assigned to user"""
        if not self.is_active:
            return False
        
        if self.max_users:
            current_users = UserRole.objects.filter(role=self, is_active=True).count()
            if current_users >= self.max_users:
                return False
        
        # Check department restrictions
        if self.department and hasattr(user, 'employee_profile'):
            return user.employee_profile.department == self.department
        
        return True


class Permission(models.Model):
    """
    Granular permission system
    نظام صلاحيات مفصل
    """
    PERMISSION_TYPES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'), 
        ('DELETE', 'Delete'),
        ('EXECUTE', 'Execute'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('MANAGE', 'Manage'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField()
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    
    # Resource association
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    resource_name = models.CharField(max_length=100, help_text="e.g., 'students', 'courses', 'reports'")
    
    # Permission constraints
    conditions = models.JSONField(default=dict, blank=True, help_text="Additional conditions for permission")
    is_system_permission = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permissions'
        ordering = ['resource_name', 'permission_type']
        unique_together = [['resource_name', 'permission_type']]
        indexes = [
            models.Index(fields=['resource_name', 'permission_type']),
            models.Index(fields=['content_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.permission_type} {self.resource_name}"
    
    def check_conditions(self, user, obj=None):
        """Check if permission conditions are met"""
        if not self.conditions:
            return True
        
        # Implement condition checking logic
        # This can be extended based on specific requirements
        return True


class RolePermission(models.Model):
    """
    Association between roles and permissions
    ربط الأدوار بالصلاحيات
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')
    
    # Permission constraints
    constraints = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = [['role', 'permission']]
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UserRole(models.Model):
    """
    User role assignments with time-based controls
    تعيين أدوار المستخدمين مع ضوابط زمنية
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    
    # Time-based controls
    effective_from = models.DateTimeField(default=timezone.now)
    effective_until = models.DateTimeField(null=True, blank=True)
    
    # Assignment context
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    reason = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = [['user', 'role', 'department']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['effective_from', 'effective_until']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    @property
    def is_effective(self):
        """Check if role assignment is currently effective"""
        now = timezone.now()
        return (
            self.is_active and
            self.effective_from <= now and
            (not self.effective_until or self.effective_until > now)
        )


class UserPermission(models.Model):
    """
    Direct user permissions (overrides role permissions)
    صلاحيات مباشرة للمستخدم (تتجاوز صلاحيات الأدوار)
    """
    PERMISSION_ACTION = [
        ('GRANT', 'Grant'),
        ('DENY', 'Deny'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='user_permissions')
    action = models.CharField(max_length=10, choices=PERMISSION_ACTION, default='GRANT')
    
    # Scope limitation
    object_id = models.CharField(max_length=100, blank=True, help_text="Specific object ID if permission is object-specific")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    constraints = models.JSONField(default=dict, blank=True)
    
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_permissions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['permission', 'action']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} {self.permission.name}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class AccessLog(models.Model):
    """
    Comprehensive access logging
    سجل شامل للوصول
    """
    ACCESS_TYPES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PERMISSION_CHECK', 'Permission Check'),
        ('RESOURCE_ACCESS', 'Resource Access'),
        ('DENIED_ACCESS', 'Denied Access'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    resource = models.CharField(max_length=100, blank=True)
    permission_checked = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Request details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Access result
    access_granted = models.BooleanField()
    denial_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'access_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['access_type', '-created_at']),
            models.Index(fields=['access_granted', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.access_type} - {self.created_at}"


class SessionManager(models.Model):
    """
    Advanced session management
    إدارة الجلسات المتقدمة
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_sessions')
    session_key = models.CharField(max_length=100, unique=True)
    
    # Session details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_fingerprint = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Session control
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    max_idle_time = models.DurationField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'session_manager'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key', 'is_active']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key[:8]}..."
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        if self.max_idle_time:
            return timezone.now() > self.last_activity + self.max_idle_time
        return False
    
    def terminate_session(self):
        """Terminate the session"""
        self.is_active = False
        self.save()
        # Clear from cache if exists
        cache.delete(f"session:{self.session_key}")