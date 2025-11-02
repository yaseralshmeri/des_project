
"""
نظام تسجيل التدقيق المتطور
Advanced Audit Logging System
"""

import json
import logging
from datetime import datetime
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

# إعداد logger للتدقيق
audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler('logs/audit.log')
audit_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

class AuditLogger:
    """نظام تسجيل التدقيق"""
    
    @staticmethod
    def log_event(event_type, user, details, ip_address=None, user_agent=None):
        """تسجيل حدث تدقيق"""
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user': str(user) if user else 'Anonymous',
            'user_id': user.id if hasattr(user, 'id') else None,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        audit_logger.info(json.dumps(audit_entry, ensure_ascii=False))
        
        return audit_entry
    
    @staticmethod
    def log_login_success(user, request):
        """تسجيل نجاح تسجيل الدخول"""
        AuditLogger.log_event(
            'LOGIN_SUCCESS',
            user,
            f'تسجيل دخول ناجح للمستخدم {user.username}',
            request.META.get('REMOTE_ADDR'),
            request.META.get('HTTP_USER_AGENT')
        )
    
    @staticmethod
    def log_login_failed(username, request):
        """تسجيل فشل تسجيل الدخول"""
        AuditLogger.log_event(
            'LOGIN_FAILED', 
            None,
            f'محاولة تسجيل دخول فاشلة للمستخدم {username}',
            request.META.get('REMOTE_ADDR'),
            request.META.get('HTTP_USER_AGENT')
        )
    
    @staticmethod
    def log_data_change(action, user, model_instance, changes=None):
        """تسجيل تغيير البيانات"""
        
        model_name = model_instance.__class__.__name__
        
        details = {
            'action': action,  # CREATE, UPDATE, DELETE
            'model': model_name,
            'object_id': getattr(model_instance, 'id', None),
            'changes': changes or {}
        }
        
        AuditLogger.log_event(
            f'DATA_{action}',
            user,
            f'{action} في نموذج {model_name}',
            details=details
        )

# إشارات Django للتدقيق التلقائي
@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    AuditLogger.log_login_success(user, request)

@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    AuditLogger.log_event(
        'LOGOUT',
        user,
        f'تسجيل خروج للمستخدم {user.username}',
        request.META.get('REMOTE_ADDR'),
        request.META.get('HTTP_USER_AGENT')
    )

@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'Unknown')
    AuditLogger.log_login_failed(username, request)
