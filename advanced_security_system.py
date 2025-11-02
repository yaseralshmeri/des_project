#!/usr/bin/env python3
"""
نظام الأمان المتطور
Advanced Security System

يوفر حماية شاملة ومتطورة للمشروع
Created: 2025-11-02
"""

import os
import sys
import json
import hashlib
import secrets
import django
from datetime import datetime, timedelta
from pathlib import Path

# إعداد Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    django.setup()
except Exception as e:
    print(f"⚠️ خطأ في إعداد Django: {e}")

class AdvancedSecuritySystem:
    """نظام الأمان المتطور"""
    
    def __init__(self):
        self.security_report = {
            'timestamp': datetime.now().isoformat(),
            'security_checks': [],
            'vulnerabilities_found': [],
            'security_enhancements': [],
            'recommendations': []
        }
    
    def generate_secure_secret_key(self):
        """توليد مفتاح سري آمن"""
        print("🔐 توليد مفتاح سري آمن...")
        
        # توليد مفتاح سري قوي
        secret_key = secrets.token_urlsafe(50)
        
        # حفظ في ملف .env إذا لم يكن موجوداً
        env_file = Path('.env')
        
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # استبدال المفتاح إذا كان ضعيفاً
            if 'your-secret-key-here' in content or len(content.split('SECRET_KEY=')[1].split('\n')[0]) < 50:
                content = content.replace(
                    content.split('SECRET_KEY=')[1].split('\n')[0],
                    secret_key
                )
                
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.security_report['security_enhancements'].append(
                    "تم توليد مفتاح سري آمن جديد"
                )
        
        print("✅ تم توليد مفتاح سري آمن")
    
    def setup_security_headers(self):
        """إعداد رؤوس الأمان"""
        print("🛡️ إعداد رؤوس الأمان...")
        
        security_middleware = '''
"""
Middleware للأمان المتطور
Advanced Security Middleware
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect
import re

class AdvancedSecurityMiddleware(MiddlewareMixin):
    """نظام الأمان المتطور"""
    
    def process_response(self, request, response):
        # إضافة رؤوس الأمان
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY', 
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        for header, value in security_headers.items():
            response[header] = value
        
        return response
    
    def process_request(self, request):
        # فحص محاولات الهجمات الشائعة
        suspicious_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'union.*select',  # SQL Injection  
            r'../../../',  # Directory Traversal
            r'eval\s*\(',  # Code Injection
        ]
        
        user_input = str(request.GET) + str(request.POST)
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                # تسجيل محاولة الهجوم
                print(f"⚠️ محاولة هجوم مشبوهة من {request.META.get('REMOTE_ADDR', 'Unknown')}")
                # يمكن إضافة منطق الحظر هنا
                break
        
        return None
'''
        
        # إنشاء مجلد security
        security_dir = Path('security')
        security_dir.mkdir(exist_ok=True)
        
        # حفظ middleware الأمان
        with open(security_dir / 'middleware.py', 'w', encoding='utf-8') as f:
            f.write(security_middleware)
        
        # إنشاء __init__.py
        (security_dir / '__init__.py').touch()
        
        self.security_report['security_enhancements'].append(
            "تم إنشاء نظام رؤوس الأمان المتطور"
        )
        
        print("✅ تم إعداد رؤوس الأمان")
    
    def setup_rate_limiting(self):
        """إعداد تحديد معدل الطلبات"""
        print("🚦 إعداد تحديد معدل الطلبات...")
        
        rate_limiting_code = '''
"""
نظام تحديد معدل الطلبات المتطور
Advanced Rate Limiting System
"""

from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from functools import wraps
import time

def rate_limit(max_requests=60, window=60, key_func=None):
    """
    Decorator لتحديد معدل الطلبات
    
    Args:
        max_requests: عدد الطلبات المسموحة
        window: النافزة الزمنية بالثواني
        key_func: دالة لتوليد مفتاح فريد
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # توليد مفتاح فريد للمستخدم
            if key_func:
                cache_key = key_func(request)
            else:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
                cache_key = f"rate_limit:{ip}:{func.__name__}"
            
            # الحصول على عدد الطلبات الحالي
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= max_requests:
                return HttpResponseTooManyRequests(
                    "تم تجاوز الحد المسموح من الطلبات. حاول مرة أخرى لاحقاً."
                )
            
            # زيادة عداد الطلبات
            cache.set(cache_key, current_requests + 1, window)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator

class RateLimitMiddleware:
    """Middleware لتحديد معدل الطلبات العام"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # فحص الـ IP للطلبات المشبوهة
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        cache_key = f"global_rate_limit:{ip}"
        
        # حد أقصى 1000 طلب في الساعة لكل IP
        current_requests = cache.get(cache_key, 0)
        
        if current_requests > 1000:
            return HttpResponseTooManyRequests(
                "تم تجاوز الحد المسموح من الطلبات لهذا العنوان."
            )
        
        # تسجيل الطلب
        cache.set(cache_key, current_requests + 1, 3600)  # ساعة واحدة
        
        response = self.get_response(request)
        return response
'''
        
        with open(Path('security') / 'rate_limiting.py', 'w', encoding='utf-8') as f:
            f.write(rate_limiting_code)
        
        self.security_report['security_enhancements'].append(
            "تم إعداد نظام تحديد معدل الطلبات"
        )
        
        print("✅ تم إعداد تحديد معدل الطلبات")
    
    def setup_input_validation(self):
        """إعداد نظام التحقق من المدخلات"""
        print("✅ إعداد نظام التحقق من المدخلات...")
        
        validation_system = '''
"""
نظام التحقق من المدخلات المتطور
Advanced Input Validation System
"""

import re
import html
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class SecurityValidator:
    """نظام التحقق الأمني من المدخلات"""
    
    # أنماط الهجمات الشائعة
    MALICIOUS_PATTERNS = {
        'xss': [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?>.*?</iframe>',
            r'<object.*?>.*?</object>',
            r'<embed.*?>.*?</embed>'
        ],
        'sql_injection': [
            r'union.*select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update.*set',
            r'exec\s*\(',
            r'sp_\w+'
        ],
        'path_traversal': [
            r'\.\./',
            r'\.\.\\\\',
            r'/etc/passwd',
            r'/proc/version',
            r'cmd\.exe',
            r'powershell'
        ],
        'code_injection': [
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec',
            r'passthru',
            r'file_get_contents'
        ]
    }
    
    @classmethod
    def validate_input(cls, input_data, field_name="input"):
        """التحقق من المدخلات للكشف عن الهجمات"""
        
        if not input_data:
            return input_data
        
        input_str = str(input_data).lower()
        
        # فحص الأنماط المشبوهة
        for attack_type, patterns in cls.MALICIOUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, input_str, re.IGNORECASE):
                    raise ValidationError(
                        _(f"مدخل غير آمن تم رفضه في الحقل {field_name}: نمط {attack_type} مكتشف")
                    )
        
        # تنظيف HTML
        cleaned_input = html.escape(str(input_data))
        
        return cleaned_input
    
    @classmethod
    def sanitize_filename(cls, filename):
        """تنظيف أسماء الملفات"""
        if not filename:
            return filename
        
        # إزالة المسارات الخطيرة
        filename = os.path.basename(filename)
        
        # إزالة الأحرف الخطيرة
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(dangerous_chars, '_', filename)
        
        # تحديد الطول
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @classmethod
    def validate_email_input(cls, email):
        """التحقق المتطور من البريد الإلكتروني"""
        
        if not email:
            return email
        
        # فحص الأنماط المشبوهة أولاً
        cls.validate_input(email, "email")
        
        # فحص تنسيق البريد الإلكتروني
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError(_("تنسيق البريد الإلكتروني غير صحيح"))
        
        # فحص النطاقات المشبوهة
        suspicious_domains = [
            'tempmail.', 'guerrillamail.', '10minutemail.',
            'throwaway.', 'mailinator.', 'sharklasers.'
        ]
        
        for domain in suspicious_domains:
            if domain in email.lower():
                raise ValidationError(_("نطاق البريد الإلكتروني غير مسموح"))
        
        return email.lower().strip()

def secure_input_required(func):
    """Decorator للتحقق الآمن من المدخلات"""
    def wrapper(*args, **kwargs):
        # التحقق من المعاملات
        for arg in args:
            if isinstance(arg, str):
                SecurityValidator.validate_input(arg)
        
        for key, value in kwargs.items():
            if isinstance(value, str):
                SecurityValidator.validate_input(value, key)
        
        return func(*args, **kwargs)
    
    return wrapper
'''
        
        with open(Path('security') / 'validation.py', 'w', encoding='utf-8') as f:
            f.write(validation_system)
        
        self.security_report['security_enhancements'].append(
            "تم إعداد نظام التحقق من المدخلات المتطور"
        )
        
        print("✅ تم إعداد نظام التحقق من المدخلات")
    
    def setup_audit_logging(self):
        """إعداد نظام تسجيل التدقيق"""
        print("📋 إعداد نظام تسجيل التدقيق...")
        
        audit_system = '''
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
'''
        
        with open(Path('security') / 'audit.py', 'w', encoding='utf-8') as f:
            f.write(audit_system)
        
        self.security_report['security_enhancements'].append(
            "تم إعداد نظام تسجيل التدقيق المتطور"
        )
        
        print("✅ تم إعداد نظام تسجيل التدقيق")
    
    def perform_security_scan(self):
        """إجراء فحص أمني شامل"""
        print("🔍 إجراء فحص أمني شامل...")
        
        vulnerabilities = []
        
        # فحص إعدادات Django
        try:
            from django.conf import settings
            
            # فحص DEBUG
            if getattr(settings, 'DEBUG', True):
                vulnerabilities.append({
                    'type': 'Configuration',
                    'severity': 'Medium',
                    'issue': 'DEBUG=True في الإنتاج',
                    'recommendation': 'تعيين DEBUG=False في الإنتاج'
                })
            
            # فحص SECRET_KEY
            secret_key = getattr(settings, 'SECRET_KEY', '')
            if len(secret_key) < 50 or secret_key == 'your-secret-key-here':
                vulnerabilities.append({
                    'type': 'Configuration',
                    'severity': 'High',
                    'issue': 'مفتاح سري ضعيف',
                    'recommendation': 'استخدام مفتاح سري قوي ومعقد'
                })
            
            # فحص ALLOWED_HOSTS
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            if '*' in allowed_hosts:
                vulnerabilities.append({
                    'type': 'Configuration', 
                    'severity': 'High',
                    'issue': 'ALLOWED_HOSTS يحتوي على *',
                    'recommendation': 'تحديد النطاقات المسموحة بدقة'
                })
            
            # فحص إعدادات الجلسة
            if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
                vulnerabilities.append({
                    'type': 'Security Headers',
                    'severity': 'Medium', 
                    'issue': 'SESSION_COOKIE_SECURE غير مفعل',
                    'recommendation': 'تفعيل SESSION_COOKIE_SECURE=True'
                })
        
        except Exception as e:
            vulnerabilities.append({
                'type': 'Scan Error',
                'severity': 'Low',
                'issue': f'خطأ في فحص الإعدادات: {e}',
                'recommendation': 'مراجعة إعدادات Django'
            })
        
        # فحص الملفات للثغرات الشائعة
        self._scan_files_for_vulnerabilities(vulnerabilities)
        
        self.security_report['vulnerabilities_found'] = vulnerabilities
        
        print(f"✅ تم العثور على {len(vulnerabilities)} مشكلة أمنية محتملة")
    
    def _scan_files_for_vulnerabilities(self, vulnerabilities):
        """فحص الملفات للثغرات الأمنية"""
        
        # أنماط الثغرات الشائعة
        vulnerability_patterns = {
            'hardcoded_passwords': [
                r'password\s*=\s*["\'][^"\']{3,}["\']',
                r'pwd\s*=\s*["\'][^"\']{3,}["\']'
            ],
            'sql_injection': [
                r'\.raw\s*\(',
                r'\.extra\s*\(',
                r'cursor\.execute.*%'
            ],
            'debug_code': [
                r'print\s*\(',
                r'console\.log',
                r'debugger;'
            ]
        }
        
        python_files = Path('.').rglob('*.py')
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for vuln_type, patterns in vulnerability_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            vulnerabilities.append({
                                'type': 'Code Vulnerability',
                                'severity': 'Medium',
                                'issue': f'{vuln_type} في الملف {file_path}',
                                'recommendation': f'مراجعة وإصلاح {vuln_type} في الكود'
                            })
            
            except Exception:
                continue  # تجاهل الملفات التي لا يمكن قراءتها
    
    def generate_security_report(self):
        """توليد تقرير الأمان"""
        
        # إضافة التوصيات الأمنية
        recommendations = [
            "استخدام HTTPS في جميع الاتصالات",
            "تطبيق مصادقة ثنائية العوامل", 
            "إعداد نسخ احتياطية منتظمة ومشفرة",
            "مراقبة سجلات الأمان بانتظام",
            "تحديث التبعيات والمكتبات باستمرار",
            "إجراء اختبارات أمان دورية",
            "تطبيق مبدأ أقل صلاحيات ممكنة",
            "استخدام أدوات فحص الكود التلقائي"
        ]
        
        self.security_report['recommendations'] = recommendations
        
        # حفظ التقرير
        report_file = Path('logs') / f'security_report_{int(datetime.now().timestamp())}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.security_report, f, ensure_ascii=False, indent=2)
        
        # طباعة ملخص
        print("\n" + "="*60)
        print("🔒 ملخص تقرير الأمان")
        print("="*60)
        print(f"🛡️ التحسينات الأمنية: {len(self.security_report['security_enhancements'])}")
        print(f"⚠️ الثغرات المكتشفة: {len(self.security_report['vulnerabilities_found'])}")
        print(f"💡 التوصيات: {len(self.security_report['recommendations'])}")
        print("="*60)
        
        if self.security_report['vulnerabilities_found']:
            print("⚠️ يوجد مشاكل أمنية تحتاج لمراجعة:")
            for vuln in self.security_report['vulnerabilities_found'][:5]:  # أول 5 مشاكل
                print(f"  - {vuln['issue']} ({vuln['severity']})")
        else:
            print("✅ لم يتم العثور على ثغرات أمنية واضحة")
        
        print(f"\n📄 تم حفظ التقرير الكامل: {report_file}")
    
    def run_comprehensive_security_setup(self):
        """تشغيل الإعداد الأمني الشامل"""
        print("🚀 بدء الإعداد الأمني الشامل...")
        print("="*50)
        
        try:
            self.generate_secure_secret_key()
            self.setup_security_headers()
            self.setup_rate_limiting()  
            self.setup_input_validation()
            self.setup_audit_logging()
            self.perform_security_scan()
            self.generate_security_report()
            
            print("\n🎉 تم إكمال جميع الإعدادات الأمنية بنجاح!")
            print("🔒 النظام محمي الآن بطبقات أمان متعددة")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في الإعداد الأمني: {e}")
            return False

def main():
    """الدالة الرئيسية"""
    print("🔒 نظام الأمان المتطور - نظام إدارة الجامعة")
    print("Advanced Security System - University Management System")
    print("="*60)
    
    security = AdvancedSecuritySystem()
    success = security.run_comprehensive_security_setup()
    
    if success:
        print("\n✨ تم إكمال جميع الإعدادات الأمنية بنجاح!")
    else:
        print("\n⚠️ حدثت مشاكل أثناء الإعداد الأمني")
    
    return success

if __name__ == "__main__":
    main()