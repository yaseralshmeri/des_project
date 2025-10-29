"""
Advanced Admin Control Panel Models
نماذج لوحة التحكم الإدارية المتطورة
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class SystemConfiguration(models.Model):
    """
    System-wide configuration settings
    إعدادات النظام العامة
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='general')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'system_configurations'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category}.{self.key}"
    
    def get_value(self):
        """Parse JSON values or return string"""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value


class UserActivity(models.Model):
    """
    Track all user activities in the system
    تتبع أنشطة المستخدمين في النظام
    """
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('DOWNLOAD', 'Download'),
        ('UPLOAD', 'Upload'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    session_key = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['model_name', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"


class SystemAlert(models.Model):
    """
    System-wide alerts and notifications
    تنبيهات وإشعارات النظام
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    TYPE_CHOICES = [
        ('SYSTEM', 'System'),
        ('SECURITY', 'Security'),
        ('MAINTENANCE', 'Maintenance'),
        ('ACADEMIC', 'Academic'),
        ('FINANCIAL', 'Financial'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    auto_dismiss_after = models.DurationField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'system_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'severity']),
            models.Index(fields=['alert_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.severity} - {self.title}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class AdminDashboardWidget(models.Model):
    """
    Customizable dashboard widgets for admin panel
    ويدجت قابلة للتخصيص للوحة الإدارة
    """
    WIDGET_TYPES = [
        ('CHART', 'Chart'),
        ('STAT', 'Statistics'),
        ('TABLE', 'Data Table'),
        ('CALENDAR', 'Calendar'),
        ('ACTIVITY', 'Activity Feed'),
        ('ALERT', 'Alert List'),
    ]
    
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    height = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    is_active = models.BooleanField(default=True)
    requires_permission = models.CharField(max_length=100, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_dashboard_widgets'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.name} - {self.widget_type}"


class MaintenanceMode(models.Model):
    """
    System maintenance mode control
    التحكم في وضع الصيانة
    """
    is_enabled = models.BooleanField(default=False)
    title = models.CharField(max_length=200, default="System Under Maintenance")
    message = models.TextField(default="We are currently performing system maintenance. Please try again later.")
    estimated_completion = models.DateTimeField(null=True, blank=True)
    allowed_ips = models.TextField(blank=True, help_text="Comma-separated list of IP addresses allowed during maintenance")
    allowed_users = models.ManyToManyField(User, blank=True, help_text="Users allowed during maintenance")
    
    enabled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='maintenance_enabled')
    enabled_at = models.DateTimeField(null=True, blank=True)
    disabled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='maintenance_disabled')
    disabled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_mode'
    
    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"Maintenance Mode - {status}"
    
    def get_allowed_ips_list(self):
        if self.allowed_ips:
            return [ip.strip() for ip in self.allowed_ips.split(',')]
        return []


class BackupLog(models.Model):
    """
    Database backup logs
    سجلات نسخ احتياطية لقاعدة البيانات
    """
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    backup_type = models.CharField(max_length=20, choices=[('FULL', 'Full'), ('PARTIAL', 'Partial')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'backup_logs'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.backup_type} Backup - {self.status} - {self.started_at}"
    
    @property
    def duration(self):
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None


class SystemMetrics(models.Model):
    """
    System performance metrics
    مقاييس أداء النظام
    """
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=50, default='performance')
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_name', '-recorded_at']),
            models.Index(fields=['category', '-recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.unit}"


class AdminAction(models.Model):
    """
    Critical admin actions log
    سجل الإجراءات الإدارية الحرجة
    """
    ACTION_TYPES = [
        ('USER_CREATE', 'User Created'),
        ('USER_DELETE', 'User Deleted'),
        ('USER_ROLE_CHANGE', 'User Role Changed'),
        ('SYSTEM_CONFIG', 'System Configuration Changed'),
        ('BACKUP_RESTORE', 'Backup/Restore Operation'),
        ('MAINTENANCE_MODE', 'Maintenance Mode Toggle'),
        ('BULK_OPERATION', 'Bulk Operation'),
        ('DATA_EXPORT', 'Data Export'),
        ('DATA_IMPORT', 'Data Import'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField()
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_actions')
    ip_address = models.GenericIPAddressField()
    
    before_data = models.JSONField(blank=True, null=True)
    after_data = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin_user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action_type} - {self.created_at}"