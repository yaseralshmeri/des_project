"""
Advanced Notification and Messaging System
نظام إشعارات ورسائل متطور
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from students.models import Student
import json

User = get_user_model()


class NotificationTemplate(models.Model):
    """
    Reusable notification templates
    قوالب إشعارات قابلة لإعادة الاستخدام
    """
    TEMPLATE_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
        ('SYSTEM', 'System Alert'),
    ]
    
    CATEGORIES = [
        ('ACADEMIC', 'Academic'),
        ('FINANCIAL', 'Financial'),
        ('ADMINISTRATIVE', 'Administrative'),
        ('EMERGENCY', 'Emergency'),
        ('PROMOTIONAL', 'Promotional'),
        ('REMINDER', 'Reminder'),
        ('WELCOME', 'Welcome'),
        ('GRADUATION', 'Graduation'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Template content
    subject_template = models.CharField(max_length=500, blank=True)
    message_template = models.TextField()
    html_template = models.TextField(blank=True)
    
    # Personalization variables
    variables = models.JSONField(default=list, help_text="List of variables that can be used in templates")
    
    # Delivery settings
    priority = models.IntegerField(default=5, choices=[(i, str(i)) for i in range(1, 11)])
    is_active = models.BooleanField(default=True)
    requires_opt_in = models.BooleanField(default=False)
    
    # Languages and localization
    language = models.CharField(max_length=10, default='en')
    is_rtl = models.BooleanField(default=False)
    
    # Timing and frequency
    send_immediately = models.BooleanField(default=True)
    batch_size = models.IntegerField(default=100, help_text="Number of notifications to send per batch")
    rate_limit = models.IntegerField(default=0, help_text="Maximum notifications per minute (0 = no limit)")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    
    def render_content(self, context_data):
        """Render template with context data"""
        import re
        
        def replace_variables(text, data):
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                text = text.replace(placeholder, str(value))
            return text
        
        rendered_subject = replace_variables(self.subject_template, context_data) if self.subject_template else ""
        rendered_message = replace_variables(self.message_template, context_data)
        rendered_html = replace_variables(self.html_template, context_data) if self.html_template else ""
        
        return {
            'subject': rendered_subject,
            'message': rendered_message,
            'html': rendered_html
        }


class NotificationChannel(models.Model):
    """
    Communication channels configuration
    تكوين قنوات الاتصال
    """
    CHANNEL_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('WHATSAPP', 'WhatsApp'),
        ('TELEGRAM', 'Telegram'),
        ('SLACK', 'Slack'),
        ('DISCORD', 'Discord'),
        ('WEBHOOK', 'Webhook'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    configuration = models.JSONField(default=dict, help_text="Channel-specific configuration (API keys, endpoints, etc.)")
    
    # Status and limits
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    daily_limit = models.IntegerField(null=True, blank=True)
    hourly_limit = models.IntegerField(null=True, blank=True)
    
    # Tracking
    total_sent = models.BigIntegerField(default=0)
    total_delivered = models.BigIntegerField(default=0)
    total_failed = models.BigIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_channels'
        ordering = ['channel_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.channel_type})"
    
    @property
    def success_rate(self):
        if self.total_sent > 0:
            return (self.total_delivered / self.total_sent) * 100
        return 0


class Notification(models.Model):
    """
    Individual notifications
    إشعارات فردية
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('QUEUED', 'Queued'),
        ('SENDING', 'Sending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
        (5, 'Very Low'),
    ]
    
    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    
    # Content
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=500)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Delivery
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    
    # Context and references
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    context_data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    error_message = models.TextField(blank=True)
    
    # External tracking
    external_id = models.CharField(max_length=200, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['priority', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.username} - {self.subject[:50]}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status in ['SENT', 'DELIVERED']:
            self.status = 'READ'
            self.read_at = timezone.now()
            self.save()


class BulkNotification(models.Model):
    """
    Bulk notification campaigns
    حملات إشعارات جماعية
    """
    RECIPIENT_TYPES = [
        ('ALL_STUDENTS', 'All Students'),
        ('ALL_FACULTY', 'All Faculty'),
        ('ALL_STAFF', 'All Staff'),
        ('DEPARTMENT', 'Department'),
        ('COURSE', 'Course'),
        ('PROGRAM', 'Program'),
        ('CUSTOM_LIST', 'Custom List'),
        ('FILTERED', 'Filtered Query'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('SENDING', 'Sending'),
        ('COMPLETED', 'Completed'),
        ('PAUSED', 'Paused'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Content
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    subject = models.CharField(max_length=500)
    message = models.TextField()
    
    # Recipients
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPES)
    recipient_filter = models.JSONField(default=dict, help_text="Filter criteria for recipients")
    recipient_list = models.ManyToManyField(User, blank=True, related_name='bulk_notifications')
    
    # Delivery settings
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    priority = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bulk_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bulk_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def success_rate(self):
        if self.sent_count > 0:
            return (self.delivered_count / self.sent_count) * 100
        return 0
    
    @property
    def completion_rate(self):
        if self.total_recipients > 0:
            return (self.sent_count / self.total_recipients) * 100
        return 0


class MessageThread(models.Model):
    """
    Message threads for conversations
    خيوط الرسائل للمحادثات
    """
    THREAD_TYPES = [
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Chat'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('SUPPORT', 'Support Ticket'),
        ('ACADEMIC', 'Academic Discussion'),
    ]
    
    title = models.CharField(max_length=200)
    thread_type = models.CharField(max_length=20, choices=THREAD_TYPES, default='DIRECT')
    description = models.TextField(blank=True)
    
    # Participants
    participants = models.ManyToManyField(User, through='ThreadParticipant', related_name='message_threads')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_threads')
    
    # Thread settings
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Context
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Statistics
    message_count = models.IntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'message_threads'
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['thread_type', '-last_message_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return self.title


class ThreadParticipant(models.Model):
    """
    Thread participants with roles and permissions
    مشاركون في الخيط مع أدوار وصلاحيات
    """
    PARTICIPANT_ROLES = [
        ('OWNER', 'Owner'),
        ('ADMIN', 'Administrator'),
        ('MODERATOR', 'Moderator'),
        ('MEMBER', 'Member'),
        ('OBSERVER', 'Observer'),
    ]
    
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='thread_participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_participations')
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLES, default='MEMBER')
    
    # Permissions
    can_send_messages = models.BooleanField(default=True)
    can_add_participants = models.BooleanField(default=False)
    can_remove_participants = models.BooleanField(default=False)
    can_edit_thread = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_muted = models.BooleanField(default=False)
    last_read_at = models.DateTimeField(null=True, blank=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'thread_participants'
        unique_together = [['thread', 'user']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['thread', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} in {self.thread.title}"


class Message(models.Model):
    """
    Individual messages in threads
    رسائل فردية في الخيوط
    """
    MESSAGE_TYPES = [
        ('TEXT', 'Text Message'),
        ('IMAGE', 'Image'),
        ('FILE', 'File Attachment'),
        ('LINK', 'Link'),
        ('SYSTEM', 'System Message'),
        ('REPLY', 'Reply'),
    ]
    
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='TEXT')
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Reply to another message
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Attachments
    attachments = models.JSONField(default=list)
    
    # Status
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Tracking
    read_by = models.ManyToManyField(User, through='MessageRead', blank=True, related_name='read_messages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class MessageRead(models.Model):
    """
    Track who has read which messages
    تتبع من قرأ أي رسالة
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='message_reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reads')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reads'
        unique_together = [['message', 'user']]
        indexes = [
            models.Index(fields=['user', '-read_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} read message {self.message.id}"


class NotificationPreference(models.Model):
    """
    User notification preferences
    تفضيلات إشعارات المستخدم
    """
    FREQUENCY_CHOICES = [
        ('IMMEDIATE', 'Immediate'),
        ('HOURLY', 'Hourly Digest'),
        ('DAILY', 'Daily Digest'),
        ('WEEKLY', 'Weekly Digest'),
        ('NEVER', 'Never'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Category preferences
    academic_notifications = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='IMMEDIATE')
    financial_notifications = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='IMMEDIATE')
    administrative_notifications = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='DAILY')
    emergency_notifications = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='IMMEDIATE')
    promotional_notifications = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='WEEKLY')
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Language and timezone
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"{self.user.username} - Notification Preferences"


class NotificationQueue(models.Model):
    """
    Queue for batch processing of notifications
    طابور لمعالجة الإشعارات بالدفعات
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('RETRYING', 'Retrying'),
    ]
    
    batch_id = models.CharField(max_length=100, unique=True)
    bulk_notification = models.ForeignKey(BulkNotification, on_delete=models.CASCADE, null=True, blank=True)
    
    # Batch details
    notification_ids = models.JSONField(default=list)
    batch_size = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Processing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Retry logic
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_queue'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['next_retry_at']),
        ]
    
    def __str__(self):
        return f"Batch {self.batch_id} - {self.status}"