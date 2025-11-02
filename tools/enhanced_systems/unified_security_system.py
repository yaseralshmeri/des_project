#!/usr/bin/env python
"""
نظام الأمان الموحد المتطور
Unified Advanced Security System

نظام شامل لتأمين نظام إدارة الجامعة
Created: 2025-11-02
Author: AI Development Assistant

يشمل: تعزيز الأمان، مراقبة التهديدات، تدقيق الأنشطة، حماية البيانات
"""

import os
import sys
import json
import logging
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
import ipaddress
from collections import defaultdict, Counter

# إعداد المسارات
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import connection
from django.core.cache import cache
from django.utils import timezone

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedSecuritySystem:
    """
    نظام الأمان الموحد المتطور
    يوفر حماية شاملة للنظام
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.security_log = []
        self.threat_patterns = self._load_threat_patterns()
        self.security_config = self._load_security_config()
        
        logger.info("🔒 تم تشغيل نظام الأمان الموحد المتطور")
    
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """تحميل أنماط التهديدات المعروفة"""
        return {
            'sql_injection': [
                r"(\bunion\b.*\bselect\b)",
                r"(\bor\b.*=.*)",
                r"(\bdrop\b.*\btable\b)",
                r"(\binsert\b.*\binto\b)",
                r"(\bupdate\b.*\bset\b)",
                r"(\bdelete\b.*\bfrom\b)",
                r"'.*(\bor\b|\band\b).*'",
                r"--.*$",
                r"/\*.*\*/"
            ],
            'xss_patterns': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>",
                r"<object[^>]*>.*?</object>",
                r"<embed[^>]*>.*?</embed>",
                r"<link[^>]*>",
                r"<meta[^>]*>"
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c",
                r"etc/passwd",
                r"windows/system32"
            ],
            'command_injection': [
                r";\s*(rm|del|format)",
                r"&&\s*(rm|del|format)",
                r"\|\s*(rm|del|format)",
                r"`.*`",
                r"\$\(.*\)",
                r"nc\s+-l",
                r"wget\s+",
                r"curl\s+"
            ]
        }
    
    def _load_security_config(self) -> Dict[str, Any]:
        """تحميل إعدادات الأمان"""
        return {
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'session_timeout_hours': 24,
            'password_min_length': 8,
            'require_2fa_for_admin': True,
            'suspicious_activity_threshold': 10,
            'rate_limit_per_minute': 60,
            'allowed_file_types': ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'],
            'max_file_size_mb': 10
        }
    
    def analyze_security_vulnerabilities(self) -> Dict[str, Any]:
        """تحليل نقاط الضعف الأمنية"""
        logger.info("🔍 تحليل نقاط الضعف الأمنية...")
        
        vulnerabilities = {
            'django_settings': self._check_django_security_settings(),
            'database_security': self._check_database_security(),
            'file_permissions': self._check_file_permissions(),
            'password_policies': self._check_password_policies(),
            'session_security': self._check_session_security(),
            'dependencies': self._check_dependencies_security()
        }
        
        # حساب نقاط الأمان العامة
        total_checks = 0
        passed_checks = 0
        
        for category, checks in vulnerabilities.items():
            if isinstance(checks, dict) and 'checks' in checks:
                for check_name, check_result in checks['checks'].items():
                    total_checks += 1
                    if check_result.get('status') == 'secure':
                        passed_checks += 1
        
        security_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        vulnerabilities['overall_security_score'] = round(security_score, 1)
        
        return vulnerabilities
    
    def _check_django_security_settings(self) -> Dict[str, Any]:
        """فحص إعدادات أمان Django"""
        checks = {}
        
        # فحص DEBUG mode
        checks['debug_mode'] = {
            'status': 'secure' if not settings.DEBUG else 'vulnerable',
            'value': settings.DEBUG,
            'recommendation': 'يجب تعطيل DEBUG في الإنتاج'
        }
        
        # فحص SECRET_KEY
        secret_key = getattr(settings, 'SECRET_KEY', '')
        checks['secret_key'] = {
            'status': 'secure' if len(secret_key) > 50 and 'django-insecure' not in secret_key else 'vulnerable',
            'length': len(secret_key),
            'recommendation': 'استخدم مفتاح سري قوي وطويل'
        }
        
        # فحص ALLOWED_HOSTS
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        checks['allowed_hosts'] = {
            'status': 'secure' if allowed_hosts and '*' not in allowed_hosts else 'vulnerable',
            'value': allowed_hosts,
            'recommendation': 'حدد نطاقات محددة في ALLOWED_HOSTS'
        }
        
        # فحص HTTPS settings
        https_settings = [
            'SECURE_BROWSER_XSS_FILTER',
            'SECURE_CONTENT_TYPE_NOSNIFF',
            'SECURE_HSTS_SECONDS',
            'SECURE_SSL_REDIRECT'
        ]
        
        https_score = 0
        for setting in https_settings:
            if getattr(settings, setting, False):
                https_score += 1
        
        checks['https_security'] = {
            'status': 'secure' if https_score >= 3 else 'needs_improvement',
            'score': f"{https_score}/{len(https_settings)}",
            'recommendation': 'فعّل جميع إعدادات HTTPS الأمنية'
        }
        
        return {
            'category': 'Django Security Settings',
            'checks': checks
        }
    
    def _check_database_security(self) -> Dict[str, Any]:
        """فحص أمان قاعدة البيانات"""
        checks = {}
        
        db_config = settings.DATABASES.get('default', {})
        
        # فحص كلمة مرور قاعدة البيانات
        db_password = db_config.get('PASSWORD', '')
        checks['database_password'] = {
            'status': 'secure' if len(db_password) > 8 else 'vulnerable',
            'has_password': bool(db_password),
            'recommendation': 'استخدم كلمة مرور قوية لقاعدة البيانات'
        }
        
        # فحص نوع قاعدة البيانات
        db_engine = db_config.get('ENGINE', '')
        checks['database_engine'] = {
            'status': 'secure' if 'sqlite' not in db_engine.lower() else 'needs_improvement',
            'engine': db_engine,
            'recommendation': 'استخدم PostgreSQL أو MySQL في الإنتاج'
        }
        
        # فحص backup
        checks['backup_strategy'] = {
            'status': 'needs_improvement',  # يحتاج تنفيذ نظام backup
            'recommendation': 'قم بتنفيذ نظام نسخ احتياطي منتظم'
        }
        
        return {
            'category': 'Database Security',
            'checks': checks
        }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """فحص صلاحيات الملفات"""
        checks = {}
        
        try:
            # فحص صلاحيات الملفات الحساسة
            sensitive_files = [
                'settings.py',
                'manage.py',
                '.env'
            ]
            
            for file_name in sensitive_files:
                file_path = BASE_DIR / file_name
                if file_path.exists():
                    file_stat = file_path.stat()
                    permissions = oct(file_stat.st_mode)[-3:]
                    
                    # يجب أن تكون الصلاحيات آمنة (644 أو 600)
                    is_secure = permissions in ['644', '600', '640']
                    
                    checks[f'{file_name}_permissions'] = {
                        'status': 'secure' if is_secure else 'vulnerable',
                        'permissions': permissions,
                        'recommendation': 'استخدم صلاحيات 644 أو 600 للملفات الحساسة'
                    }
            
        except Exception as e:
            checks['file_permissions_error'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return {
            'category': 'File Permissions',
            'checks': checks
        }
    
    def _check_password_policies(self) -> Dict[str, Any]:
        """فحص سياسات كلمات المرور"""
        checks = {}
        
        # فحص إعدادات Django لكلمات المرور
        auth_password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        
        validator_types = [v.get('NAME', '').split('.')[-1] for v in auth_password_validators]
        
        checks['password_length_validator'] = {
            'status': 'secure' if 'MinimumLengthValidator' in validator_types else 'vulnerable',
            'recommendation': 'أضف MinimumLengthValidator'
        }
        
        checks['password_common_validator'] = {
            'status': 'secure' if 'CommonPasswordValidator' in validator_types else 'vulnerable',
            'recommendation': 'أضف CommonPasswordValidator'
        }
        
        checks['password_numeric_validator'] = {
            'status': 'secure' if 'NumericPasswordValidator' in validator_types else 'vulnerable',
            'recommendation': 'أضف NumericPasswordValidator'
        }
        
        return {
            'category': 'Password Policies',
            'checks': checks
        }
    
    def _check_session_security(self) -> Dict[str, Any]:
        """فحص أمان الجلسات"""
        checks = {}
        
        # فحص إعدادات الجلسات
        session_cookie_secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
        session_cookie_httponly = getattr(settings, 'SESSION_COOKIE_HTTPONLY', True)
        session_cookie_samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', None)
        
        checks['session_cookie_secure'] = {
            'status': 'secure' if session_cookie_secure else 'vulnerable',
            'value': session_cookie_secure,
            'recommendation': 'فعّل SESSION_COOKIE_SECURE=True'
        }
        
        checks['session_cookie_httponly'] = {
            'status': 'secure' if session_cookie_httponly else 'vulnerable',
            'value': session_cookie_httponly,
            'recommendation': 'فعّل SESSION_COOKIE_HTTPONLY=True'
        }
        
        checks['session_cookie_samesite'] = {
            'status': 'secure' if session_cookie_samesite in ['Strict', 'Lax'] else 'vulnerable',
            'value': session_cookie_samesite,
            'recommendation': 'اضبط SESSION_COOKIE_SAMESITE على Strict أو Lax'
        }
        
        return {
            'category': 'Session Security',
            'checks': checks
        }
    
    def _check_dependencies_security(self) -> Dict[str, Any]:
        """فحص أمان التبعيات"""
        checks = {}
        
        try:
            # قراءة ملف requirements.txt
            requirements_file = BASE_DIR / 'requirements.txt'
            if requirements_file.exists():
                with open(requirements_file, 'r') as f:
                    requirements = f.read().splitlines()
                
                # فحص التبعيات المعروفة بمشاكل أمنية
                vulnerable_packages = [
                    'django<3.0',  # إصدارات قديمة
                    'pillow<8.0',  # إصدارات قديمة
                ]
                
                security_issues = []
                for req in requirements:
                    if req.strip() and not req.startswith('#'):
                        # فحص بسيط للإصدارات القديمة
                        if 'django' in req.lower() and '==' in req:
                            version = req.split('==')[1].strip()
                            if version.startswith(('1.', '2.', '3.0', '3.1')):
                                security_issues.append(f"إصدار Django قديم: {version}")
                
                checks['dependency_versions'] = {
                    'status': 'secure' if not security_issues else 'vulnerable',
                    'issues': security_issues,
                    'recommendation': 'حدّث التبعيات للإصدارات الآمنة'
                }
            else:
                checks['requirements_file'] = {
                    'status': 'error',
                    'error': 'ملف requirements.txt غير موجود'
                }
                
        except Exception as e:
            checks['dependencies_error'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return {
            'category': 'Dependencies Security',
            'checks': checks
        }
    
    def scan_for_threats(self) -> Dict[str, Any]:
        """فحص التهديدات الأمنية"""
        logger.info("🛡️ فحص التهديدات الأمنية...")
        
        threat_analysis = {
            'suspicious_users': self._find_suspicious_users(),
            'malicious_files': self._scan_malicious_files(),
            'unusual_activities': self._detect_unusual_activities(),
            'failed_logins': self._analyze_failed_logins(),
            'security_incidents': []
        }
        
        return threat_analysis
    
    def _find_suspicious_users(self) -> List[Dict[str, Any]]:
        """العثور على المستخدمين المشبوهين"""
        suspicious_users = []
        
        try:
            User = get_user_model()
            
            # المستخدمون بأسماء مشبوهة
            suspicious_usernames = [
                'admin', 'administrator', 'root', 'test', 'guest',
                'user', 'demo', 'temp', 'anonymous'
            ]
            
            for username in suspicious_usernames:
                users = User.objects.filter(username__icontains=username)
                for user in users:
                    if user.is_active and user.last_login:
                        suspicious_users.append({
                            'username': user.username,
                            'email': user.email,
                            'last_login': user.last_login.isoformat() if user.last_login else None,
                            'is_superuser': user.is_superuser,
                            'reason': f'اسم مستخدم مشبوه: {username}'
                        })
            
            # المستخدمون الذين لم يسجلوا دخول منذ فترة طويلة
            old_threshold = timezone.now() - timedelta(days=90)
            old_users = User.objects.filter(
                last_login__lt=old_threshold,
                is_active=True
            )[:10]  # أول 10 مستخدمين فقط
            
            for user in old_users:
                suspicious_users.append({
                    'username': user.username,
                    'email': user.email,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_superuser': user.is_superuser,
                    'reason': 'لم يسجل دخول منذ أكثر من 90 يوم'
                })
                
        except Exception as e:
            logger.error(f"خطأ في البحث عن المستخدمين المشبوهين: {e}")
        
        return suspicious_users
    
    def _scan_malicious_files(self) -> List[Dict[str, Any]]:
        """فحص الملفات الضارة"""
        malicious_files = []
        
        try:
            # أنماط الملفات الضارة
            malicious_patterns = [
                r"eval\s*\(",
                r"exec\s*\(",
                r"base64_decode",
                r"shell_exec",
                r"system\s*\(",
                r"passthru\s*\(",
                r"<script[^>]*>.*?</script>",
                r"document\.write\s*\(",
                r"unescape\s*\("
            ]
            
            # فحص ملفات Python
            for root, dirs, files in os.walk(BASE_DIR):
                # تجاهل مجلدات معينة
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if file.endswith(('.py', '.html', '.js')):
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # فحص الأنماط الضارة
                            for pattern in malicious_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    malicious_files.append({
                                        'file_path': file_path,
                                        'pattern': pattern,
                                        'risk_level': 'متوسط',
                                        'recommendation': 'راجع الملف بعناية'
                                    })
                                    break  # ملف واحد فقط لكل نمط
                                    
                        except Exception as e:
                            logger.warning(f"خطأ في فحص الملف {file_path}: {e}")
            
        except Exception as e:
            logger.error(f"خطأ في فحص الملفات الضارة: {e}")
        
        return malicious_files[:20]  # أول 20 ملف فقط
    
    def _detect_unusual_activities(self) -> List[Dict[str, Any]]:
        """اكتشاف الأنشطة غير العادية"""
        unusual_activities = []
        
        try:
            # فحص الجلسات النشطة
            active_sessions = Session.objects.filter(
                expire_date__gt=timezone.now()
            )
            
            # تحليل الجلسات
            session_ips = defaultdict(int)
            session_users = defaultdict(int)
            
            for session in active_sessions:
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                
                if user_id:
                    session_users[user_id] += 1
                    
                    # إذا كان لدى المستخدم عدة جلسات
                    if session_users[user_id] > 3:
                        unusual_activities.append({
                            'type': 'multiple_sessions',
                            'user_id': user_id,
                            'session_count': session_users[user_id],
                            'risk_level': 'منخفض',
                            'description': f'المستخدم لديه {session_users[user_id]} جلسات نشطة'
                        })
            
        except Exception as e:
            logger.error(f"خطأ في اكتشاف الأنشطة غير العادية: {e}")
        
        return unusual_activities
    
    def _analyze_failed_logins(self) -> Dict[str, Any]:
        """تحليل محاولات تسجيل الدخول الفاشلة"""
        failed_login_analysis = {
            'total_attempts': 0,
            'recent_attempts': 0,
            'suspicious_ips': [],
            'targeted_usernames': []
        }
        
        try:
            # هذا يتطلب تنفيذ نظام تسجيل محاولات تسجيل الدخول
            # حالياً سنعيد بيانات وهمية للتوضيح
            
            failed_login_analysis.update({
                'total_attempts': 0,
                'recent_attempts': 0,
                'note': 'يتطلب تنفيذ نظام تسجيل محاولات تسجيل الدخول'
            })
            
        except Exception as e:
            logger.error(f"خطأ في تحليل محاولات تسجيل الدخول: {e}")
        
        return failed_login_analysis
    
    def enhance_security_settings(self) -> Dict[str, Any]:
        """تعزيز إعدادات الأمان"""
        logger.info("⚡ تعزيز إعدادات الأمان...")
        
        enhancements = {
            'applied_fixes': [],
            'recommendations': [],
            'security_improvements': []
        }
        
        try:
            # إنشاء ملف إعدادات أمان محسن
            security_settings = self._generate_security_settings()
            
            # حفظ الإعدادات الأمنية
            security_file = BASE_DIR / 'security_settings_enhanced.py'
            with open(security_file, 'w', encoding='utf-8') as f:
                f.write(security_settings)
            
            enhancements['applied_fixes'].append('تم إنشاء ملف إعدادات الأمان المحسن')
            
            # توصيات أمنية
            enhancements['recommendations'].extend([
                'استخدم HTTPS في الإنتاج',
                'فعّل Two-Factor Authentication',
                'قم بإعداد نسخ احتياطية منتظمة',
                'راقب سجلات النظام بانتظام',
                'استخدم كلمات مرور قوية',
                'قم بتحديث التبعيات بانتظام',
                'أعد صلاحيات الملفات والمجلدات',
                'استخدم WAF (Web Application Firewall)'
            ])
            
        except Exception as e:
            logger.error(f"خطأ في تعزيز الأمان: {e}")
            enhancements['error'] = str(e)
        
        return enhancements
    
    def _generate_security_settings(self) -> str:
        """إنشاء إعدادات الأمان المحسنة"""
        return '''"""
إعدادات الأمان المحسنة - Enhanced Security Settings
تم إنشاؤها تلقائياً بواسطة نظام الأمان الموحد
Created: ''' + datetime.now().isoformat() + '''
"""

# Security Headers - رؤوس الأمان
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_HSTS_SECONDS = 31536000  # سنة كاملة
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Settings - إعدادات HTTPS
SECURE_SSL_REDIRECT = True  # فعّل في الإنتاج فقط
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session Security - أمان الجلسات
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # ساعة واحدة

# CSRF Protection - حماية CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Content Security Policy - سياسة أمان المحتوى
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'none'"]

# Password Security - أمان كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Rate Limiting - تحديد معدل الطلبات
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Logging Security - أمان السجلات
LOGGING_SECURITY = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Database Security - أمان قاعدة البيانات
DATABASES_SECURITY_OPTIONS = {
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
}

# Additional Security Settings - إعدادات أمان إضافية
SECURITY_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# تحذير: هذه الإعدادات مقترحة - اختبرها قبل التطبيق في الإنتاج
'''
    
    def generate_security_report(self) -> Dict[str, Any]:
        """إنشاء تقرير الأمان الشامل"""
        logger.info("📊 إنشاء تقرير الأمان الشامل...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'scan_duration': (datetime.now() - self.start_time).total_seconds(),
            'vulnerability_analysis': self.analyze_security_vulnerabilities(),
            'threat_scan': self.scan_for_threats(),
            'security_enhancements': self.enhance_security_settings(),
            'recommendations': self._generate_security_recommendations()
        }
        
        # حفظ التقرير
        report_path = BASE_DIR / 'logs' / f'security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        report['report_saved_to'] = str(report_path)
        logger.info(f"✅ تم حفظ تقرير الأمان: {report_path}")
        
        return report
    
    def _generate_security_recommendations(self) -> List[str]:
        """إنشاء توصيات الأمان"""
        return [
            "🔐 استخدم كلمات مرور قوية ومعقدة لجميع الحسابات",
            "🔄 فعّل المصادقة الثنائية (2FA) لجميع المستخدمين الإداريين",
            "🛡️ قم بتحديث Django والتبعيات بانتظام",
            "📊 راقب سجلات النظام وتنبيهات الأمان يومياً",
            "🔒 استخدم HTTPS في جميع البيئات",
            "💾 قم بإعداد نسخ احتياطية مشفرة ومجدولة",
            "🚫 قم بتعطيل DEBUG mode في الإنتاج",
            "🔍 افحص الثغرات الأمنية شهرياً",
            "👥 راجع صلاحيات المستخدمين بانتظام",
            "🏗️ استخدم WAF وأنظمة الحماية المتقدمة"
        ]
    
    def run_comprehensive_security_scan(self) -> Dict[str, Any]:
        """تشغيل الفحص الأمني الشامل"""
        logger.info("🎯 بدء الفحص الأمني الشامل...")
        
        try:
            report = self.generate_security_report()
            
            logger.info("🏆 تم إكمال الفحص الأمني الشامل!")
            return report
            
        except Exception as e:
            logger.error(f"خطأ في الفحص الأمني الشامل: {e}")
            return {'error': str(e)}

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("🔒 نظام الأمان الموحد المتطور")
    print("   Unified Advanced Security System")
    print("="*60)
    
    try:
        security_system = UnifiedSecuritySystem()
        results = security_system.run_comprehensive_security_scan()
        
        # عرض ملخص النتائج
        print("\n📊 ملخص الفحص الأمني:")
        print("-" * 40)
        
        if 'vulnerability_analysis' in results:
            vuln_analysis = results['vulnerability_analysis']
            security_score = vuln_analysis.get('overall_security_score', 0)
            print(f"🔍 نقاط الأمان العامة: {security_score}%")
            
            if security_score >= 80:
                print("✅ مستوى الأمان: ممتاز")
            elif security_score >= 60:
                print("⚠️ مستوى الأمان: جيد (يحتاج تحسين)")
            else:
                print("❌ مستوى الأمان: ضعيف (يتطلب إجراءات فورية)")
        
        if 'threat_scan' in results:
            threat_scan = results['threat_scan']
            suspicious_users = len(threat_scan.get('suspicious_users', []))
            malicious_files = len(threat_scan.get('malicious_files', []))
            
            print(f"👥 مستخدمون مشبوهون: {suspicious_users}")
            print(f"📁 ملفات مشبوهة: {malicious_files}")
        
        if 'report_saved_to' in results:
            print(f"📄 تم حفظ التقرير: {results['report_saved_to']}")
        
        print("\n🎉 تم إكمال الفحص الأمني بنجاح!")
        
        return 0
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل النظام: {e}")
        print(f"❌ خطأ: {e}")
        return 1

if __name__ == "__main__":
    exit(main())