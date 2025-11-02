"""
نظام الأمان المطور والموحد
Enhanced and Unified Security System

تم تطويره في: 2025-11-02
يدمج جميع أنظمة الأمان في نظام واحد متطور
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet
import json

logger = logging.getLogger('security')
User = get_user_model()


class SecurityManager:
    """مدير الأمان الشامل"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self):
        """إنشاء أو الحصول على مفتاح التشفير"""
        key = cache.get('encryption_key')
        if not key:
            key = Fernet.generate_key()
            cache.set('encryption_key', key, timeout=86400)  # 24 ساعة
        return key
    
    def encrypt_data(self, data):
        """تشفير البيانات"""
        try:
            if isinstance(data, str):
                data = data.encode()
            encrypted = self.cipher_suite.encrypt(data)
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """فك تشفير البيانات"""
        try:
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def generate_secure_token(self, length=32):
        """إنشاء رمز آمن"""
        return secrets.token_urlsafe(length)
    
    def hash_password_advanced(self, password, salt=None):
        """تشفير كلمة المرور المتطور"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # استخدام PBKDF2 مع SHA-256
        from django.contrib.auth.hashers import PBKDF2PasswordHasher
        hasher = PBKDF2PasswordHasher()
        return hasher.encode(password, salt)
    
    def verify_password_strength(self, password):
        """فحص قوة كلمة المرور"""
        issues = []
        score = 0
        
        if len(password) < 8:
            issues.append("كلمة المرور قصيرة جداً (أقل من 8 أحرف)")
        else:
            score += 1
            
        if not any(c.isupper() for c in password):
            issues.append("يجب أن تحتوي على حرف كبير")
        else:
            score += 1
            
        if not any(c.islower() for c in password):
            issues.append("يجب أن تحتوي على حرف صغير")
        else:
            score += 1
            
        if not any(c.isdigit() for c in password):
            issues.append("يجب أن تحتوي على رقم")
        else:
            score += 1
            
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("يجب أن تحتوي على رمز خاص")
        else:
            score += 1
        
        # فحص التكرار
        if len(set(password)) < len(password) * 0.7:
            issues.append("كلمة المرور تحتوي على تكرار مفرط")
        else:
            score += 1
        
        strength_levels = {
            0: 'ضعيف جداً',
            1: 'ضعيف',
            2: 'مقبول',
            3: 'جيد', 
            4: 'قوي',
            5: 'قوي جداً',
            6: 'ممتاز'
        }
        
        return {
            'score': score,
            'strength': strength_levels.get(score, 'غير محدد'),
            'issues': issues,
            'is_strong': score >= 4
        }


class LoginAttemptTracker:
    """تتبع محاولات تسجيل الدخول"""
    
    def __init__(self):
        self.max_attempts = 5
        self.lockout_duration = 1800  # 30 دقيقة
        
    def record_failed_attempt(self, identifier, ip_address=None):
        """تسجيل محاولة فاشلة"""
        cache_key = f"failed_attempts_{identifier}"
        ip_key = f"failed_attempts_ip_{ip_address}" if ip_address else None
        
        # تسجيل للمعرف (البريد/اسم المستخدم)
        attempts = cache.get(cache_key, [])
        attempts.append(timezone.now().isoformat())
        cache.set(cache_key, attempts, timeout=self.lockout_duration)
        
        # تسجيل للـ IP
        if ip_key:
            ip_attempts = cache.get(ip_key, [])
            ip_attempts.append(timezone.now().isoformat())
            cache.set(ip_key, ip_attempts, timeout=self.lockout_duration)
        
        logger.warning(f"Failed login attempt for {identifier} from IP {ip_address}")
        
        # فحص الحظر
        return self.is_locked(identifier, ip_address)
    
    def is_locked(self, identifier, ip_address=None):
        """فحص ما إذا كان الحساب أو IP محظور"""
        # فحص المعرف
        cache_key = f"failed_attempts_{identifier}"
        attempts = cache.get(cache_key, [])
        
        # تصفية المحاولات القديمة
        cutoff_time = timezone.now() - timedelta(seconds=self.lockout_duration)
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.fromisoformat(attempt) > cutoff_time
        ]
        
        if len(recent_attempts) >= self.max_attempts:
            return True, 'account'
        
        # فحص الـ IP
        if ip_address:
            ip_key = f"failed_attempts_ip_{ip_address}"
            ip_attempts = cache.get(ip_key, [])
            recent_ip_attempts = [
                attempt for attempt in ip_attempts
                if datetime.fromisoformat(attempt) > cutoff_time
            ]
            
            if len(recent_ip_attempts) >= self.max_attempts * 2:  # حد أعلى للـ IP
                return True, 'ip'
        
        return False, None
    
    def clear_attempts(self, identifier, ip_address=None):
        """مسح محاولات تسجيل الدخول بعد النجاح"""
        cache_key = f"failed_attempts_{identifier}"
        cache.delete(cache_key)
        
        if ip_address:
            ip_key = f"failed_attempts_ip_{ip_address}"
            cache.delete(ip_key)


class TwoFactorAuth:
    """نظام المصادقة الثنائية"""
    
    def __init__(self):
        self.code_length = 6
        self.code_expiry = 300  # 5 دقائق
    
    def generate_code(self, user):
        """إنشاء رمز التحقق"""
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(self.code_length)])
        
        cache_key = f"2fa_code_{user.id}"
        cache.set(cache_key, code, timeout=self.code_expiry)
        
        logger.info(f"2FA code generated for user {user.username}")
        return code
    
    def verify_code(self, user, provided_code):
        """التحقق من الرمز"""
        cache_key = f"2fa_code_{user.id}"
        stored_code = cache.get(cache_key)
        
        if not stored_code:
            return False, "انتهت صلاحية الرمز"
        
        if stored_code == provided_code:
            cache.delete(cache_key)  # حذف الرمز بعد الاستخدام
            logger.info(f"2FA verification successful for user {user.username}")
            return True, "تم التحقق بنجاح"
        else:
            logger.warning(f"Invalid 2FA code attempt for user {user.username}")
            return False, "رمز غير صحيح"
    
    def is_enabled_for_user(self, user):
        """فحص ما إذا كانت المصادقة الثنائية مفعلة للمستخدم"""
        return getattr(user, 'two_factor_enabled', False)


class SecurityAudit:
    """نظام تدقيق الأمان"""
    
    def __init__(self):
        self.audit_events = []
    
    def log_security_event(self, event_type, user, details, ip_address=None, severity='medium'):
        """تسجيل حدث أمني"""
        event = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'user': str(user) if user else 'Anonymous',
            'user_id': user.id if user and hasattr(user, 'id') else None,
            'details': details,
            'ip_address': ip_address,
            'severity': severity
        }
        
        self.audit_events.append(event)
        
        # الاحتفاظ بآخر 10000 حدث
        if len(self.audit_events) > 10000:
            self.audit_events.pop(0)
        
        # تسجيل في اللوج
        log_level = logging.INFO
        if severity == 'high':
            log_level = logging.ERROR
        elif severity == 'critical':
            log_level = logging.CRITICAL
        
        logger.log(log_level, f"Security Event: {event_type} - {details}")
        
        # حفظ في الكاش للوصول السريع
        cache_key = f"security_events_{event_type}"
        events = cache.get(cache_key, [])
        events.append(event)
        if len(events) > 100:  # الاحتفاظ بآخر 100 حدث لكل نوع
            events.pop(0)
        cache.set(cache_key, events, timeout=86400)  # 24 ساعة
    
    def get_recent_events(self, event_type=None, hours=24):
        """الحصول على الأحداث الأخيرة"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        if event_type:
            cache_key = f"security_events_{event_type}"
            events = cache.get(cache_key, [])
        else:
            events = self.audit_events
        
        # تصفية الأحداث حسب الوقت
        recent_events = [
            event for event in events
            if datetime.fromisoformat(event['timestamp']) >= cutoff_time
        ]
        
        return recent_events
    
    def generate_security_report(self, days=7):
        """إنشاء تقرير أمني"""
        cutoff_time = timezone.now() - timedelta(days=days)
        
        # جمع الأحداث
        events = [
            event for event in self.audit_events
            if datetime.fromisoformat(event['timestamp']) >= cutoff_time
        ]
        
        # تصنيف الأحداث
        event_types = {}
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        users_involved = set()
        
        for event in events:
            event_type = event['event_type']
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
            
            severity_counts[event['severity']] += 1
            
            if event['user_id']:
                users_involved.add(event['user_id'])
        
        report = {
            'period_days': days,
            'total_events': len(events),
            'event_types': event_types,
            'severity_distribution': severity_counts,
            'users_involved': len(users_involved),
            'recent_critical_events': [
                event for event in events[-50:]  # آخر 50 حدث
                if event['severity'] == 'critical'
            ],
            'generated_at': timezone.now().isoformat()
        }
        
        return report


class DataProtection:
    """نظام حماية البيانات الحساسة"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        
    def mask_sensitive_data(self, data, field_type='general'):
        """إخفاء البيانات الحساسة"""
        if not data:
            return data
        
        data_str = str(data)
        
        if field_type == 'email':
            if '@' in data_str:
                username, domain = data_str.split('@')
                masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
                return f"{masked_username}@{domain}"
        
        elif field_type == 'phone':
            if len(data_str) >= 4:
                return '*' * (len(data_str) - 4) + data_str[-4:]
        
        elif field_type == 'id_number':
            if len(data_str) >= 4:
                return data_str[:2] + '*' * (len(data_str) - 4) + data_str[-2:]
        
        else:  # general masking
            if len(data_str) >= 4:
                return data_str[:1] + '*' * (len(data_str) - 2) + data_str[-1:]
        
        return '*' * len(data_str)
    
    def sanitize_input(self, input_data):
        """تطهير المدخلات من المحتوى الضار"""
        if not isinstance(input_data, str):
            return input_data
        
        # إزالة HTML tags خطيرة
        import re
        
        # إزالة script tags
        input_data = re.sub(r'<script.*?</script>', '', input_data, flags=re.IGNORECASE | re.DOTALL)
        
        # إزالة javascript: URLs
        input_data = re.sub(r'javascript\s*:', '', input_data, flags=re.IGNORECASE)
        
        # إزالة on* attributes (onclick, onload, etc.)
        input_data = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', input_data, flags=re.IGNORECASE)
        
        return input_data.strip()


# إنشاء مثائل عامة للاستخدام
security_manager = SecurityManager()
login_tracker = LoginAttemptTracker()
two_factor_auth = TwoFactorAuth()
security_audit = SecurityAudit()
data_protection = DataProtection()


def log_login_attempt(user, success, ip_address, details=None):
    """تسجيل محاولة تسجيل دخول"""
    event_type = 'login_success' if success else 'login_failed'
    severity = 'low' if success else 'medium'
    
    details_text = details or ('تسجيل دخول ناجح' if success else 'فشل في تسجيل الدخول')
    
    security_audit.log_security_event(
        event_type=event_type,
        user=user,
        details=details_text,
        ip_address=ip_address,
        severity=severity
    )
    
    if not success:
        is_locked, lock_type = login_tracker.record_failed_attempt(
            user.username if user else 'unknown',
            ip_address
        )
        
        if is_locked:
            security_audit.log_security_event(
                event_type='account_locked',
                user=user,
                details=f"حساب محظور بسبب محاولات فاشلة متكررة ({lock_type})",
                ip_address=ip_address,
                severity='high'
            )
    else:
        # مسح المحاولات الفاشلة عند النجاح
        login_tracker.clear_attempts(user.username, ip_address)


def check_security_violations(request):
    """فحص الانتهاكات الأمنية في الطلب"""
    violations = []
    
    # فحص حجم البيانات
    if hasattr(request, 'body') and len(request.body) > 10 * 1024 * 1024:  # 10MB
        violations.append('oversized_request')
    
    # فحص User-Agent المشبوه
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    suspicious_agents = ['bot', 'crawler', 'scanner', 'hack', 'inject']
    if any(agent in user_agent for agent in suspicious_agents):
        violations.append('suspicious_user_agent')
    
    # فحص معدل الطلبات
    ip_address = get_client_ip(request)
    cache_key = f"request_rate_{ip_address}"
    request_count = cache.get(cache_key, 0)
    
    if request_count > 100:  # أكثر من 100 طلب في الدقيقة
        violations.append('rate_limit_exceeded')
    
    cache.set(cache_key, request_count + 1, timeout=60)
    
    return violations


def get_client_ip(request):
    """الحصول على IP العميل"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_security_headers(response):
    """إضافة headers أمنية للاستجابة"""
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'DENY'
    response['X-XSS-Protection'] = '1; mode=block'
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    if not settings.DEBUG:
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response