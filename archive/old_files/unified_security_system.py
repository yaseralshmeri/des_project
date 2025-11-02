#!/usr/bin/env python3
"""
نظام الأمان الموحد للمشروع الجامعي
Unified Security System for University Project
Created: 2024-11-02
Author: AI Development Team

يدمج جميع وظائف الأمان في مكان واحد:
- فحص إعدادات الأمان
- مراقبة الثغرات الأمنية  
- إدارة كلمات المرور
- مراقبة الأنشطة المشبوهة
- تشفير البيانات الحساسة
"""

import os
import sys
import re
import hashlib
import secrets
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, connection
from django.core.management import call_command
from django.utils import timezone


class UnifiedSecuritySystem:
    """نظام الأمان الموحد الشامل"""
    
    def __init__(self):
        self.security_report = {
            'scan_time': datetime.now().isoformat(),
            'issues': [],
            'improvements': [],
            'recommendations': [],
            'user_analysis': {},
            'system_status': {},
            'threat_level': 'unknown',
            'security_score': 0
        }
        self.base_dir = Path(__file__).resolve().parent
        self.setup_logging()
    
    def setup_logging(self):
        """إعداد نظام التسجيل الأمني"""
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'security.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SecuritySystem')
    
    def log_security_event(self, level: str, message: str, details: Dict = None):
        """تسجيل الأحداث الأمنية"""
        event = {
            'level': level,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        if level == 'critical':
            self.logger.critical(f"🚨 {message}")
            self.security_report['issues'].append(event)
        elif level == 'warning':
            self.logger.warning(f"⚠️ {message}")
            self.security_report['issues'].append(event)
        elif level == 'info':
            self.logger.info(f"ℹ️ {message}")
            self.security_report['improvements'].append(event)
        
        print(f"{level.upper()}: {message}")
    
    # =============================================================================
    # DJANGO SECURITY SETTINGS - فحص إعدادات Django الأمنية
    # =============================================================================
    
    def check_django_security(self):
        """فحص شامل لإعدادات الأمان في Django"""
        print("🔒 فحص إعدادات الأمان في Django...")
        
        security_checks = [
            self._check_debug_setting,
            self._check_secret_key,
            self._check_allowed_hosts,
            self._check_https_settings,
            self._check_session_security,
            self._check_csrf_protection,
            self._check_xss_protection,
            self._check_middleware_security
        ]
        
        for check in security_checks:
            try:
                check()
            except Exception as e:
                self.log_security_event('warning', f'خطأ في فحص الأمان: {check.__name__}', {'error': str(e)})
    
    def _check_debug_setting(self):
        """فحص إعداد DEBUG"""
        if settings.DEBUG:
            self.log_security_event('critical', 
                'DEBUG=True في الإنتاج - يكشف معلومات حساسة',
                {'recommendation': 'تعيين DEBUG=False في الإنتاج'})
        else:
            self.log_security_event('info', 'DEBUG=False - إعداد آمن')
    
    def _check_secret_key(self):
        """فحص SECRET_KEY"""
        if ('django-insecure' in settings.SECRET_KEY or 
            len(settings.SECRET_KEY) < 50 or
            settings.SECRET_KEY == 'django-insecure-minimal-2024'):
            
            self.log_security_event('critical',
                'SECRET_KEY غير آمن أو افتراضي',
                {'recommendation': 'استخدام SECRET_KEY قوي ومعقد'})
        else:
            self.log_security_event('info', 'SECRET_KEY آمن')
    
    def _check_allowed_hosts(self):
        """فحص ALLOWED_HOSTS"""
        if '*' in settings.ALLOWED_HOSTS:
            self.log_security_event('warning',
                'ALLOWED_HOSTS يسمح بجميع النطاقات',
                {'recommendation': 'تحديد نطاقات محددة في ALLOWED_HOSTS'})
        elif not settings.ALLOWED_HOSTS:
            self.log_security_event('warning',
                'ALLOWED_HOSTS فارغ',
                {'recommendation': 'تحديد النطاقات المسموحة'})
        else:
            self.log_security_event('info', 'ALLOWED_HOSTS محدد بشكل صحيح')
    
    def _check_https_settings(self):
        """فحص إعدادات HTTPS"""
        https_settings = [
            ('SECURE_SSL_REDIRECT', 'إعادة توجيه HTTPS'),
            ('SECURE_HSTS_SECONDS', 'HSTS Headers'),
            ('SESSION_COOKIE_SECURE', 'Secure Session Cookies'),
            ('CSRF_COOKIE_SECURE', 'Secure CSRF Cookies')
        ]
        
        for setting_name, description in https_settings:
            if not getattr(settings, setting_name, False):
                self.log_security_event('warning',
                    f'{description} غير مفعل',
                    {'recommendation': f'تفعيل {setting_name} للإنتاج'})
    
    def _check_session_security(self):
        """فحص أمان الجلسات"""
        if not getattr(settings, 'SESSION_COOKIE_HTTPONLY', True):
            self.log_security_event('warning',
                'Session cookies غير محمية من JavaScript',
                {'recommendation': 'تفعيل SESSION_COOKIE_HTTPONLY'})
        
        session_age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)  # default 2 weeks
        if session_age > 86400:  # more than 1 day
            self.log_security_event('warning',
                f'مدة انتهاء الجلسة طويلة: {session_age/3600:.1f} ساعة',
                {'recommendation': 'تقليل مدة انتهاء الجلسة'})
    
    def _check_csrf_protection(self):
        """فحص حماية CSRF"""
        if 'django.middleware.csrf.CsrfViewMiddleware' not in settings.MIDDLEWARE:
            self.log_security_event('critical',
                'حماية CSRF غير مفعلة',
                {'recommendation': 'إضافة CsrfViewMiddleware'})
        else:
            self.log_security_event('info', 'حماية CSRF مفعلة')
    
    def _check_xss_protection(self):
        """فحص حماية XSS"""
        if not getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False):
            self.log_security_event('warning',
                'حماية XSS غير مفعلة',
                {'recommendation': 'تفعيل SECURE_BROWSER_XSS_FILTER'})
    
    def _check_middleware_security(self):
        """فحص middleware الأمان"""
        security_middleware = [
            ('django.middleware.security.SecurityMiddleware', 'Security Middleware'),
            ('django.middleware.clickjacking.XFrameOptionsMiddleware', 'Clickjacking Protection')
        ]
        
        for middleware, description in security_middleware:
            if middleware not in settings.MIDDLEWARE:
                self.log_security_event('warning',
                    f'{description} غير مفعل',
                    {'recommendation': f'إضافة {middleware}'})
    
    # =============================================================================
    # USER SECURITY ANALYSIS - تحليل أمان المستخدمين
    # =============================================================================
    
    def analyze_user_security(self):
        """تحليل شامل لأمان المستخدمين"""
        print("👥 تحليل أمان المستخدمين...")
        
        try:
            User = get_user_model()
            
            # إحصائيات المستخدمين
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            admin_users = User.objects.filter(is_superuser=True).count()
            
            self.security_report['user_analysis'] = {
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'inactive_users': total_users - active_users
            }
            
            # فحص كلمات المرور الضعيفة
            self._check_weak_passwords()
            
            # فحص المستخدمين المشبوهين
            self._check_suspicious_users()
            
            # فحص صلاحيات المديرين
            self._check_admin_privileges()
            
            self.log_security_event('info',
                f'تحليل {total_users} مستخدم اكتمل')
            
        except Exception as e:
            self.log_security_event('warning',
                'خطأ في تحليل المستخدمين',
                {'error': str(e)})
    
    def _check_weak_passwords(self):
        """فحص كلمات المرور الضعيفة"""
        User = get_user_model()
        weak_passwords = ['123456', 'password', 'admin', '123123', 'qwerty']
        weak_users = []
        
        for user in User.objects.all()[:100]:  # فحص أول 100 مستخدم
            for weak_pass in weak_passwords:
                if user.check_password(weak_pass):
                    weak_users.append(user.username)
                    break
        
        if weak_users:
            self.log_security_event('critical',
                f'اكتشاف {len(weak_users)} مستخدم بكلمات مرور ضعيفة',
                {'users': weak_users[:5], 'recommendation': 'إجبار تغيير كلمات المرور'})
    
    def _check_suspicious_users(self):
        """فحص المستخدمين المشبوهين"""
        User = get_user_model()
        
        # مستخدمين بدون بريد إلكتروني
        no_email_users = User.objects.filter(email='').count()
        if no_email_users > 0:
            self.log_security_event('warning',
                f'{no_email_users} مستخدم بدون بريد إلكتروني',
                {'recommendation': 'تحديد بريد إلكتروني للجميع'})
        
        # مستخدمين غير نشطين منذ فترة طويلة
        old_threshold = timezone.now() - timedelta(days=90)
        if hasattr(User, 'last_login'):
            old_users = User.objects.filter(
                last_login__lt=old_threshold,
                is_active=True
            ).count()
            if old_users > 0:
                self.log_security_event('warning',
                    f'{old_users} مستخدم نشط لم يسجل دخول لأكثر من 90 يوم',
                    {'recommendation': 'مراجعة وإلغاء تفعيل الحسابات القديمة'})
    
    def _check_admin_privileges(self):
        """فحص صلاحيات المديرين"""
        User = get_user_model()
        
        # عدد المديرين
        admin_count = User.objects.filter(is_superuser=True).count()
        if admin_count == 0:
            self.log_security_event('critical',
                'لا يوجد مستخدم مدير في النظام',
                {'recommendation': 'إنشاء حساب مدير'})
        elif admin_count > 5:
            self.log_security_event('warning',
                f'عدد كبير من المديرين: {admin_count}',
                {'recommendation': 'مراجعة صلاحيات المديرين'})
        else:
            self.log_security_event('info',
                f'عدد المديرين مناسب: {admin_count}')
    
    # =============================================================================
    # VULNERABILITY SCANNING - فحص الثغرات الأمنية
    # =============================================================================
    
    def scan_vulnerabilities(self):
        """فحص شامل للثغرات الأمنية"""
        print("🔍 فحص الثغرات الأمنية...")
        
        vulnerability_checks = [
            self._check_file_permissions,
            self._check_exposed_files,
            self._check_database_security,
            self._check_dependency_vulnerabilities,
            self._check_input_validation
        ]
        
        for check in vulnerability_checks:
            try:
                check()
            except Exception as e:
                self.log_security_event('warning',
                    f'خطأ في فحص الثغرات: {check.__name__}',
                    {'error': str(e)})
    
    def _check_file_permissions(self):
        """فحص صلاحيات الملفات"""
        sensitive_files = [
            ('db.sqlite3', '600'),
            ('.env', '600'),
            ('settings.py', '644')
        ]
        
        for filename, expected_perm in sensitive_files:
            file_path = self.base_dir / filename
            if file_path.exists():
                import stat
                current_perm = oct(file_path.stat().st_mode)[-3:]
                if current_perm != expected_perm and filename != 'settings.py':
                    self.log_security_event('warning',
                        f'ملف {filename} لديه صلاحيات غير آمنة: {current_perm}',
                        {'expected': expected_perm, 'current': current_perm})
    
    def _check_exposed_files(self):
        """فحص الملفات المكشوفة"""
        exposed_patterns = [
            '*.log',
            '.env*',
            '*.sql',
            '*.bak',
            '*backup*'
        ]
        
        for pattern in exposed_patterns:
            files = list(self.base_dir.rglob(pattern))
            if files and not pattern.startswith('.env'):  # .env files are expected
                self.log_security_event('warning',
                    f'ملفات حساسة مكشوفة: {pattern}',
                    {'count': len(files), 'files': [f.name for f in files[:5]]})
    
    def _check_database_security(self):
        """فحص أمان قاعدة البيانات"""
        try:
            with connection.cursor() as cursor:
                # فحص جداول النظام
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'auth_%'
                """)
                auth_tables = cursor.fetchall()
                
                if auth_tables:
                    self.log_security_event('info',
                        f'جداول المصادقة موجودة: {len(auth_tables)}')
                else:
                    self.log_security_event('warning',
                        'جداول المصادقة غير موجودة',
                        {'recommendation': 'تشغيل المايجريشن'})
                
        except Exception as e:
            self.log_security_event('warning',
                'خطأ في فحص قاعدة البيانات',
                {'error': str(e)})
    
    def _check_dependency_vulnerabilities(self):
        """فحص ثغرات التبعيات"""
        # فحص requirements.txt للمكتبات المعروفة بثغرات
        requirements_file = self.base_dir / 'requirements.txt'
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    requirements = f.read()
                
                # قائمة مكتبات معروفة بمشاكل أمنية (مثال)
                vulnerable_packages = [
                    'django==1.',  # إصدارات قديمة
                    'requests==2.2',  # إصدارات قديمة
                ]
                
                for vuln_pkg in vulnerable_packages:
                    if vuln_pkg in requirements:
                        self.log_security_event('critical',
                            f'مكتبة معروفة بثغرات أمنية: {vuln_pkg}',
                            {'recommendation': 'تحديث المكتبة لأحدث إصدار'})
                
            except Exception as e:
                self.log_security_event('warning',
                    'خطأ في فحص التبعيات',
                    {'error': str(e)})
    
    def _check_input_validation(self):
        """فحص التحقق من المدخلات"""
        # فحص أساسي لوجود validators في النماذج
        try:
            from django.apps import apps
            
            models_without_validation = []
            
            for model in apps.get_models():
                # فحص الحقول النصية بدون validators
                for field in model._meta.fields:
                    if (isinstance(field, models.CharField) and 
                        not field.validators and 
                        field.max_length > 100):
                        models_without_validation.append(f'{model.__name__}.{field.name}')
            
            if models_without_validation:
                self.log_security_event('warning',
                    f'حقول بدون تحقق: {len(models_without_validation)}',
                    {'fields': models_without_validation[:10]})
            
        except Exception as e:
            self.log_security_event('warning',
                'خطأ في فحص التحقق من المدخلات',
                {'error': str(e)})
    
    # =============================================================================
    # SECURITY IMPROVEMENTS - تطبيق تحسينات أمنية
    # =============================================================================
    
    def apply_security_improvements(self):
        """تطبيق التحسينات الأمنية الممكنة"""
        print("🔧 تطبيق التحسينات الأمنية...")
        
        improvements = [
            self._generate_secure_secret_key,
            self._create_security_log,
            self._setup_password_policies,
            self._configure_session_security
        ]
        
        for improvement in improvements:
            try:
                improvement()
            except Exception as e:
                self.log_security_event('warning',
                    f'خطأ في تطبيق التحسين: {improvement.__name__}',
                    {'error': str(e)})
    
    def _generate_secure_secret_key(self):
        """إنتاج SECRET_KEY آمن"""
        if 'django-insecure' in settings.SECRET_KEY:
            new_key = secrets.token_urlsafe(64)
            
            # حفظ المفتاح الجديد في ملف منفصل (للمراجعة اليدوية)
            key_file = self.base_dir / 'new_secret_key.txt'
            with open(key_file, 'w') as f:
                f.write(f"# SECRET_KEY جديد آمن\n")
                f.write(f"# يرجى نسخه يدوياً إلى ملف .env\n")
                f.write(f"SECRET_KEY='{new_key}'\n")
            
            self.log_security_event('info',
                'تم إنتاج SECRET_KEY جديد آمن',
                {'file': str(key_file)})
    
    def _create_security_log(self):
        """إنشاء ملف سجل الأمان"""
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        security_log = log_dir / 'security.log'
        if not security_log.exists():
            security_log.touch()
            self.log_security_event('info', 'تم إنشاء ملف سجل الأمان')
    
    def _setup_password_policies(self):
        """إعداد سياسات كلمات المرور"""
        # فحص إعدادات كلمات المرور الحالية
        password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        
        if len(password_validators) < 3:
            self.log_security_event('warning',
                'سياسات كلمات المرور ضعيفة',
                {'current_validators': len(password_validators),
                 'recommendation': 'إضافة المزيد من validators'})
    
    def _configure_session_security(self):
        """تكوين أمان الجلسات"""
        # إعدادات الجلسة الآمنة (للمراجعة)
        secure_settings = {
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SECURE': True,  # للإنتاج فقط
            'SESSION_COOKIE_SAMESITE': 'Strict',
            'SESSION_COOKIE_AGE': 86400  # 24 ساعة
        }
        
        recommendations_file = self.base_dir / 'security_recommendations.txt'
        with open(recommendations_file, 'w', encoding='utf-8') as f:
            f.write("# توصيات الأمان للإعدادات\n\n")
            for setting, value in secure_settings.items():
                f.write(f"{setting} = {value}\n")
        
        self.log_security_event('info',
            'تم إنشاء توصيات أمان الجلسات',
            {'file': str(recommendations_file)})
    
    # =============================================================================
    # MAIN EXECUTION - التشغيل الرئيسي
    # =============================================================================
    
    def run_comprehensive_security_scan(self):
        """تشغيل الفحص الأمني الشامل"""
        print("🚨 بدء الفحص الأمني الشامل...")
        start_time = datetime.now()
        
        # تشغيل جميع فحوصات الأمان
        security_modules = [
            ('Django Security Settings', self.check_django_security),
            ('User Security Analysis', self.analyze_user_security),
            ('Vulnerability Scanning', self.scan_vulnerabilities),
            ('Security Improvements', self.apply_security_improvements)
        ]
        
        for module_name, module_func in security_modules:
            try:
                print(f"\n📋 {module_name}...")
                module_func()
            except Exception as e:
                self.log_security_event('warning',
                    f'خطأ في {module_name}',
                    {'error': str(e)})
        
        # حساب مستوى التهديد والنقاط
        self._calculate_security_score()
        
        # إنهاء الفحص
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        self.security_report['end_time'] = end_time.isoformat()
        self.security_report['execution_time'] = round(execution_time, 2)
        
        # حفظ التقرير
        self._save_security_report()
        
        # عرض النتائج
        self._display_security_summary()
        
        return self.security_report
    
    def _calculate_security_score(self):
        """حساب نقاط الأمان"""
        score = 100
        critical_issues = len([issue for issue in self.security_report['issues'] 
                             if issue.get('level') == 'critical'])
        warning_issues = len([issue for issue in self.security_report['issues'] 
                            if issue.get('level') == 'warning'])
        
        # خصم نقاط للمشاكل
        score -= (critical_issues * 20)  # 20 نقطة لكل مشكلة حرجة
        score -= (warning_issues * 5)   # 5 نقاط لكل تحذير
        
        score = max(0, min(100, score))
        
        # تحديد مستوى التهديد
        if score >= 80:
            threat_level = 'low'
        elif score >= 60:
            threat_level = 'medium'
        elif score >= 40:
            threat_level = 'high'
        else:
            threat_level = 'critical'
        
        self.security_report['security_score'] = score
        self.security_report['threat_level'] = threat_level
        self.security_report['critical_issues'] = critical_issues
        self.security_report['warning_issues'] = warning_issues
    
    def _save_security_report(self):
        """حفظ تقرير الأمان"""
        try:
            reports_dir = self.base_dir / 'database_reports'
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = reports_dir / f'security_report_{timestamp}.json'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.security_report, f, ensure_ascii=False, indent=2)
            
            self.log_security_event('info',
                f'تقرير الأمان محفوظ في: {report_file}')
            
        except Exception as e:
            self.log_security_event('warning',
                'لا يمكن حفظ تقرير الأمان',
                {'error': str(e)})
    
    def _display_security_summary(self):
        """عرض ملخص الأمان"""
        print("\n" + "="*50)
        print("📊 ملخص تقرير الأمان")
        print("="*50)
        
        score = self.security_report['security_score']
        threat = self.security_report['threat_level']
        critical = self.security_report['critical_issues']
        warnings = self.security_report['warning_issues']
        
        print(f"🎯 نقاط الأمان: {score}/100")
        print(f"⚠️ مستوى التهديد: {threat.upper()}")
        print(f"🚨 مشاكل حرجة: {critical}")
        print(f"⚠️ تحذيرات: {warnings}")
        print(f"✅ تحسينات مطبقة: {len(self.security_report['improvements'])}")
        print(f"💡 توصيات: {len(self.security_report['recommendations'])}")
        
        # عرض أهم التوصيات
        if self.security_report['recommendations']:
            print("\n📋 أهم التوصيات:")
            for i, rec in enumerate(self.security_report['recommendations'][:5], 1):
                if isinstance(rec, dict) and 'details' in rec:
                    print(f"{i}. {rec['details'].get('recommendation', 'غير محدد')}")
        
        print("="*50)


def main():
    """الدالة الرئيسية"""
    print("🛡️ نظام الأمان الموحد لنظام إدارة الجامعة")
    print("="*50)
    
    try:
        security_system = UnifiedSecuritySystem()
        results = security_system.run_comprehensive_security_scan()
        
        print(f"\n✅ الفحص الأمني اكتمل بنجاح")
        print(f"🎯 النقاط: {results['security_score']}/100")
        print(f"⚠️ التهديد: {results['threat_level'].upper()}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف الفحص الأمني بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ في الفحص الأمني: {e}")
        return None


if __name__ == '__main__':
    main()