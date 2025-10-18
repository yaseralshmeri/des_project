from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    TEMPLATE_TYPES = [
        ('ENROLLMENT_CONFIRMATION', 'Enrollment Confirmation'),
        ('GRADE_POSTED', 'Grade Posted'),
        ('ASSIGNMENT_DUE', 'Assignment Due Reminder'),
        ('PAYMENT_DUE', 'Payment Due Notice'),
        ('PAYMENT_RECEIVED', 'Payment Received Confirmation'),
        ('ATTENDANCE_WARNING', 'Attendance Warning'),
        ('SEMESTER_START', 'Semester Start Notice'),
        ('REGISTRATION_OPEN', 'Registration Open'),
        ('ACADEMIC_WARNING', 'Academic Warning'),
        ('GRADUATION_REMINDER', 'Graduation Reminder'),
        ('GENERAL_ANNOUNCEMENT', 'General Announcement'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, unique=True)
    subject_template = models.CharField(max_length=200)
    email_template = models.TextField()
    sms_template = models.TextField(blank=True, help_text="Keep under 160 characters")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Notification(models.Model):
    """Individual notification records"""
    NOTIFICATION_TYPES = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('ALERT', 'Alert'),
        ('SUCCESS', 'Success'),
        ('ERROR', 'Error'),
    ]
    
    DELIVERY_METHODS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('IN_APP', 'In-App Notification'),
        ('PUSH', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('READ', 'Read'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='INFO')
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHODS, default='IN_APP')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    scheduled_for = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata for context
    related_object_type = models.CharField(max_length=50, blank=True)  # e.g., 'enrollment', 'grade', 'payment'
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Additional data for template rendering
    context_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['scheduled_for', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} -> {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.status = 'READ'
            self.save(update_fields=['read_at', 'status'])
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.sent_at = timezone.now()
        self.status = 'SENT'
        self.save(update_fields=['sent_at', 'status'])
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    @property
    def is_sent(self):
        return self.sent_at is not None


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_enrollment = models.BooleanField(default=True)
    email_grades = models.BooleanField(default=True)
    email_payments = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=True)
    email_announcements = models.BooleanField(default=True)
    
    # SMS preferences
    sms_enabled = models.BooleanField(default=False)
    sms_urgent_only = models.BooleanField(default=True)
    sms_payments = models.BooleanField(default=True)
    sms_reminders = models.BooleanField(default=False)
    
    # In-app preferences
    in_app_enabled = models.BooleanField(default=True)
    in_app_sound = models.BooleanField(default=True)
    
    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_grades = models.BooleanField(default=True)
    push_reminders = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"


class Announcement(models.Model):
    """University-wide or targeted announcements"""
    AUDIENCE_CHOICES = [
        ('ALL', 'All Users'),
        ('STUDENTS', 'All Students'),
        ('TEACHERS', 'All Teachers'),
        ('STAFF', 'All Staff'),
        ('SPECIFIC_ROLES', 'Specific Roles'),
        ('SPECIFIC_USERS', 'Specific Users'),
        ('DEPARTMENT', 'Department'),
        ('PROGRAM', 'Academic Program'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('NORMAL', 'Normal Priority'),
        ('HIGH', 'High Priority'),
        ('URGENT', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=15, choices=AUDIENCE_CHOICES, default='ALL')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    
    # Targeting options
    target_roles = models.JSONField(default=list, blank=True)  # For SPECIFIC_ROLES
    target_users = models.ManyToManyField(User, blank=True)  # For SPECIFIC_USERS
    target_department = models.ForeignKey('students.Department', on_delete=models.CASCADE, 
                                         null=True, blank=True)  # For DEPARTMENT
    target_program = models.ForeignKey('academic.AcademicProgram', on_delete=models.CASCADE,
                                      null=True, blank=True)  # For PROGRAM
    
    # Scheduling
    publish_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', 'publish_at']),
            models.Index(fields=['audience', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
    
    @property
    def is_active(self):
        """Check if announcement is currently active"""
        now = timezone.now()
        if not self.is_published:
            return False
        if self.publish_at > now:
            return False
        if self.expire_at and self.expire_at < now:
            return False
        return True


class NotificationQueue(models.Model):
    """Queue for batch notification processing"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)  # Higher number = higher priority
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    last_attempt = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_queue'
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return f"Queue: {self.notification.title}"


class EmailLog(models.Model):
    """Log of sent emails for tracking and debugging"""
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=[
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ])
    
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.recipient_email} - {self.subject} ({self.status})"