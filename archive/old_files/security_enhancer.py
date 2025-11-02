#!/usr/bin/env python3
"""
محسن الأمان المتقدم للمشروع
Advanced Security Enhancer
"""

import os
import sys
import re
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model


class SecurityEnhancer:
    """محسن الأمان المتطور"""
    
    def __init__(self):
        self.security_issues = []
        self.improvements = []
        self.recommendations = []
    
    def check_django_security_settings(self):
        """فحص إعدادات الأمان في Django"""
        print("🔒 فحص إعدادات الأمان...")
        
        # فحص DEBUG
        if settings.DEBUG:
            self.security_issues.append("⚠️ DEBUG=True في الإنتاج - خطر أمني")
            self.recommendations.append("تعيين DEBUG=False في الإنتاج")
        else:
            self.improvements.append("✅ DEBUG=False - جيد")
        
        # فحص SECRET_KEY
        if 'django-insecure' in settings.SECRET_KEY or len(settings.SECRET_KEY) < 50:
            self.security_issues.append("⚠️ SECRET_KEY غير آمن")
            self.recommendations.append("استخدام SECRET_KEY قوي ومعقد")
        else:
            self.improvements.append("✅ SECRET_KEY آمن")
        
        # فحص ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            self.security_issues.append("⚠️ ALLOWED_HOSTS يحتوي على '*' في الإنتاج")
            self.recommendations.append("تحديد ALLOWED_HOSTS بدقة")
        else:
            self.improvements.append("✅ ALLOWED_HOSTS محدد بشكل آمن")
        
        # فحص HTTPS settings
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False) and not settings.DEBUG:
            self.security_issues.append("⚠️ SECURE_SSL_REDIRECT غير مفعل")
            self.recommendations.append("تفعيل HTTPS إجبارياً")
        
        if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            self.security_issues.append("⚠️ HSTS غير مفعل")
            self.recommendations.append("تفعيل HTTP Strict Transport Security")
        
        # فحص Session security
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False) and not settings.DEBUG:
            self.security_issues.append("⚠️ SESSION_COOKIE_SECURE غير مفعل")
        
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False) and not settings.DEBUG:
            self.security_issues.append("⚠️ CSRF_COOKIE_SECURE غير مفعل")
    
    def check_password_security(self):
        """فحص أمان كلمات المرور"""
        print("🔐 فحص أمان كلمات المرور...")
        
        User = get_user_model()
        
        # فحص المستخدمين بكلمات مرور ضعيفة
        weak_passwords = ['password', '123456', 'admin', 'test', '12345678']
        weak_users = []
        
        try:
            users = User.objects.all()[:100]  # فحص أول 100 مستخدم
            
            for user in users:
                # لا يمكن فحص كلمات المرور المشفرة مباشرة
                # لكن يمكن فحص إذا كانت من النماذج الشائعة
                if user.check_password('password') or user.check_password('123456'):
                    weak_users.append(user.username)
            
            if weak_users:
                self.security_issues.append(f"⚠️ {len(weak_users)} مستخدم بكلمات مرور ضعيفة")
                self.recommendations.append("إجبار المستخدمين على تغيير كلمات المرور الضعيفة")
            else:
                self.improvements.append("✅ لا توجد كلمات مرور ضعيفة واضحة")
                
        except Exception as e:
            self.security_issues.append(f"⚠️ خطأ في فحص كلمات المرور: {str(e)}")
        
        # فحص إعدادات التحقق من كلمات المرور
        password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        if len(password_validators) < 3:
            self.security_issues.append("⚠️ محققات كلمات المرور غير كافية")
            self.recommendations.append("إضافة المزيد من محققات كلمات المرور")
        else:
            self.improvements.append("✅ محققات كلمات المرور كافية")
    
    def check_file_permissions(self):
        """فحص أذونات الملفات"""
        print("📁 فحص أذونات الملفات...")
        
        critical_files = [
            'settings.py',
            '.env',
            '.env.production',
            'manage.py',
            'db.sqlite3'
        ]
        
        for file_name in critical_files:
            file_path = Path(file_name)
            if file_path.exists():
                # فحص الأذونات (Unix/Linux)
                stat_info = file_path.stat()
                permissions = oct(stat_info.st_mode)[-3:]
                
                # ملف قاعدة البيانات يجب أن يكون محمي
                if file_name == 'db.sqlite3' and permissions != '600':
                    self.security_issues.append(f"⚠️ {file_name} أذونات غير آمنة: {permissions}")
                    self.recommendations.append(f"تعيين أذونات آمنة لـ {file_name}: chmod 600")
                
                # ملفات الإعدادات
                elif file_name in ['.env', '.env.production', 'settings.py']:
                    if permissions not in ['600', '644']:
                        self.security_issues.append(f"⚠️ {file_name} أذونات قد تكون غير آمنة: {permissions}")
                
                self.improvements.append(f"✓ فحص {file_name}: {permissions}")
    
    def check_dependency_vulnerabilities(self):
        """فحص ثغرات المكتبات"""
        print("📦 فحص ثغرات المكتبات...")
        
        requirements_file = Path('requirements.txt')
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                requirements = f.readlines()
            
            # مكتبات قديمة أو بها ثغرات معروفة
            vulnerable_packages = {
                'django<4.0': 'Django أقل من 4.0 قد يحتوي على ثغرات',
                'pillow<8.0': 'Pillow أقل من 8.0 قد يحتوي على ثغرات',
                'requests<2.25': 'Requests أقل من 2.25 قد يحتوي على ثغرات'
            }
            
            found_vulnerabilities = []
            for req in requirements:
                req = req.strip().lower()
                for vuln_pattern, message in vulnerable_packages.items():
                    if vuln_pattern.split('<')[0] in req:
                        # فحص الإصدار
                        if '==' in req:
                            version = req.split('==')[1].strip()
                            min_version = vuln_pattern.split('<')[1]
                            # مقارنة بسيطة للإصدارات
                            if version < min_version:
                                found_vulnerabilities.append(message)
            
            if found_vulnerabilities:
                self.security_issues.extend([f"⚠️ {vuln}" for vuln in found_vulnerabilities])
                self.recommendations.append("تحديث المكتبات إلى أحدث الإصدارات الآمنة")
            else:
                self.improvements.append("✅ لا توجد ثغرات واضحة في المكتبات")
        else:
            self.security_issues.append("⚠️ ملف requirements.txt غير موجود")
    
    def check_sql_injection_patterns(self):
        """فحص أنماط حقن SQL المحتملة"""
        print("💉 فحص أنماط حقن SQL...")
        
        dangerous_patterns = [
            r'cursor\.execute\([^,)]*%[^,)]*\)',  # استخدام % formatting في SQL
            r'\.extra\([^)]*select[^)]*\)',       # Django .extra() مع select
            r'\.raw\([^)]*%[^)]*\)',              # Django .raw() مع % formatting
        ]
        
        python_files = list(Path('.').rglob('*.py'))
        potential_issues = []
        
        for py_file in python_files:
            if 'venv' in str(py_file) or 'migrations' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in dangerous_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        potential_issues.append(f"{py_file}: {len(matches)} نمط محتمل")
                        
            except Exception:
                continue
        
        if potential_issues:
            self.security_issues.append("⚠️ أنماط SQL محتملة الخطر:")
            self.security_issues.extend([f"   {issue}" for issue in potential_issues[:5]])
            self.recommendations.append("مراجعة استعلامات SQL واستخدام parameterized queries")
        else:
            self.improvements.append("✅ لا توجد أنماط SQL خطيرة واضحة")
    
    def check_xss_protection(self):
        """فحص حماية XSS"""
        print("🛡️ فحص حماية XSS...")
        
        # فحص استخدام |safe في القوالب
        template_files = list(Path('.').rglob('*.html'))
        unsafe_usage = []
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # البحث عن استخدام |safe أو {% autoescape off %}
                safe_count = len(re.findall(r'\|\s*safe', content))
                autoescape_off = len(re.findall(r'autoescape\s+off', content))
                
                if safe_count > 3 or autoescape_off > 0:
                    unsafe_usage.append(f"{template_file}: {safe_count} |safe, {autoescape_off} autoescape off")
                    
            except Exception:
                continue
        
        if unsafe_usage:
            self.security_issues.append("⚠️ استخدام محتمل غير آمن للقوالب:")
            self.security_issues.extend([f"   {usage}" for usage in unsafe_usage[:5]])
            self.recommendations.append("مراجعة استخدام |safe و autoescape في القوالب")
        else:
            self.improvements.append("✅ لا يوجد استخدام مفرط لـ |safe")
    
    def generate_security_key(self):
        """إنشاء مفتاح أمان قوي"""
        return secrets.token_urlsafe(50)
    
    def create_security_improvements_file(self):
        """إنشاء ملف تحسينات الأمان"""
        print("📋 إنشاء ملف التحسينات...")
        
        improvements_content = f"""# تحسينات الأمان المقترحة
# Suggested Security Improvements
# Generated: {datetime.now().isoformat()}

## إعدادات Django الآمنة
## Secure Django Settings

# في settings.py أو .env.production
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# مفتاح أمان جديد
SECRET_KEY = '{self.generate_security_key()}'

# إعدادات HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# أمان Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# حماية إضافية
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

## إعدادات كلمات المرور المحسنة
AUTH_PASSWORD_VALIDATORS = [
    {{
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {{'min_length': 12}},
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }},
]

## إعدادات Session محسنة
SESSION_COOKIE_AGE = 3600  # ساعة واحدة
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = 'university_sessionid'

## إعدادات CORS آمنة
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = False

## Middleware الأمان
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... باقي middleware
]
"""
        
        improvements_file = Path('security_improvements.py')
        with open(improvements_file, 'w', encoding='utf-8') as f:
            f.write(improvements_content)
        
        return improvements_file
    
    def run_security_audit(self):
        """تشغيل مراجعة الأمان الشاملة"""
        print("🔐 بدء مراجعة الأمان الشاملة...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # تشغيل جميع فحوصات الأمان
        self.check_django_security_settings()
        self.check_password_security()
        self.check_file_permissions()
        self.check_dependency_vulnerabilities()
        self.check_sql_injection_patterns()
        self.check_xss_protection()
        
        # إنشاء ملف التحسينات
        improvements_file = self.create_security_improvements_file()
        
        end_time = datetime.now()
        
        # طباعة النتائج
        print(f"\n🛡️ تقرير مراجعة الأمان:")
        print("=" * 60)
        
        if self.security_issues:
            print(f"\n⚠️ مشاكل الأمان ({len(self.security_issues)}):")
            for issue in self.security_issues:
                print(f"   {issue}")
        
        if self.improvements:
            print(f"\n✅ نقاط قوة ({len(self.improvements)}):")
            for improvement in self.improvements:
                print(f"   {improvement}")
        
        if self.recommendations:
            print(f"\n💡 توصيات التحسين:")
            for rec in self.recommendations:
                print(f"   • {rec}")
        
        print(f"\n📁 ملف التحسينات: {improvements_file}")
        print(f"⏱️ وقت المراجعة: {(end_time - start_time).total_seconds():.2f} ثانية")
        
        # تقييم الأمان العام
        total_checks = len(self.security_issues) + len(self.improvements)
        if total_checks > 0:
            security_score = (len(self.improvements) / total_checks) * 100
            print(f"\n🎯 نقاط الأمان: {security_score:.1f}/100")
            
            if security_score >= 80:
                print("🟢 مستوى الأمان: ممتاز")
            elif security_score >= 60:
                print("🟡 مستوى الأمان: جيد")
            else:
                print("🔴 مستوى الأمان: يحتاج تحسين")
        
        print("\n✅ اكتملت مراجعة الأمان!")


def main():
    """الدالة الرئيسية"""
    enhancer = SecurityEnhancer()
    enhancer.run_security_audit()


if __name__ == "__main__":
    main()