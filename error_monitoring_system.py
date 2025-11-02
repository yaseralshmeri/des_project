#!/usr/bin/env python3
"""
نظام مراقبة الأخطاء المتطور
Advanced Error Monitoring System

يوفر مراقبة شاملة للأخطاء والاستثناءات في النظام
Created: 2025-11-02
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any
import django
from django.conf import settings

# إعداد Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    django.setup()
except Exception as e:
    print(f"⚠️ خطأ في إعداد Django: {e}")

class AdvancedErrorMonitor:
    """نظام مراقبة الأخطاء المتطور"""
    
    def __init__(self):
        self.error_log = []
        self.warning_log = []
        self.info_log = []
        
        # إعداد التسجيل
        self.setup_logging()
        
        # إحصائيات المراقبة
        self.stats = {
            'total_errors': 0,
            'critical_errors': 0,
            'warnings': 0,
            'info_messages': 0,
            'start_time': datetime.now().isoformat(),
            'system_status': 'monitoring'
        }
    
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        # إنشاء مجلد logs
        os.makedirs('logs', exist_ok=True)
        
        # إعداد logger الرئيسي
        self.logger = logging.getLogger('university_system')
        self.logger.setLevel(logging.DEBUG)
        
        # إنشاء handler للملفات
        file_handler = logging.FileHandler('logs/system_errors.log', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        
        # إنشاء handler للشاشة
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # إعداد التنسيق
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # إضافة handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(self, error: Exception, context: str = "", severity: str = "ERROR"):
        """تسجيل خطأ"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'severity': severity,
            'traceback': traceback.format_exc() if severity == "CRITICAL" else None
        }
        
        if severity == "CRITICAL":
            self.error_log.append(error_info)
            self.stats['critical_errors'] += 1
            self.logger.critical(f"{context}: {error}")
        elif severity == "ERROR":
            self.error_log.append(error_info)
            self.stats['total_errors'] += 1
            self.logger.error(f"{context}: {error}")
        elif severity == "WARNING":
            self.warning_log.append(error_info)
            self.stats['warnings'] += 1
            self.logger.warning(f"{context}: {error}")
        
        return error_info
    
    def log_info(self, message: str, context: str = ""):
        """تسجيل معلومة"""
        info = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'context': context
        }
        
        self.info_log.append(info)
        self.stats['info_messages'] += 1
        self.logger.info(f"{context}: {message}")
        
        return info
    
    def check_django_configuration(self):
        """فحص إعدادات Django"""
        print("🔍 فحص إعدادات Django...")
        
        issues = []
        
        try:
            # فحص INSTALLED_APPS
            if not hasattr(settings, 'INSTALLED_APPS'):
                issues.append("INSTALLED_APPS غير معرف")
            else:
                # فحص التطبيقات المطلوبة
                required_apps = [
                    'django.contrib.admin',
                    'django.contrib.auth', 
                    'django.contrib.contenttypes',
                    'django.contrib.sessions',
                    'django.contrib.messages',
                    'django.contrib.staticfiles'
                ]
                
                for app in required_apps:
                    if app not in settings.INSTALLED_APPS:
                        issues.append(f"التطبيق المطلوب {app} غير موجود في INSTALLED_APPS")
            
            # فحص قاعدة البيانات
            if not hasattr(settings, 'DATABASES'):
                issues.append("إعدادات قاعدة البيانات غير معرفة")
            
            # فحص SECRET_KEY
            if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
                issues.append("SECRET_KEY غير معرف أو فارغ")
            
            # فحص المتغيرات المهمة
            important_settings = ['DEBUG', 'ALLOWED_HOSTS', 'TIME_ZONE']
            for setting_name in important_settings:
                if not hasattr(settings, setting_name):
                    issues.append(f"المتغير {setting_name} غير معرف")
            
            if issues:
                for issue in issues:
                    self.log_error(Exception(issue), "Django Configuration", "WARNING")
            else:
                self.log_info("جميع إعدادات Django صحيحة", "Django Configuration")
        
        except Exception as e:
            self.log_error(e, "Django Configuration Check", "ERROR")
        
        return issues
    
    def check_database_connection(self):
        """فحص الاتصال بقاعدة البيانات"""
        print("🗄️ فحص الاتصال بقاعدة البيانات...")
        
        try:
            from django.db import connection
            from django.core.management.color import no_style
            style = no_style()
            
            # اختبار الاتصال
            connection.ensure_connection()
            
            if connection.is_usable():
                self.log_info("الاتصال بقاعدة البيانات ناجح", "Database Connection")
                return True
            else:
                self.log_error(Exception("قاعدة البيانات غير قابلة للاستخدام"), "Database Connection", "ERROR")
                return False
                
        except Exception as e:
            self.log_error(e, "Database Connection Check", "CRITICAL")
            return False
    
    def check_static_files_configuration(self):
        """فحص إعدادات الملفات الثابتة"""
        print("📁 فحص إعدادات الملفات الثابتة...")
        
        issues = []
        
        try:
            # فحص STATIC_URL
            if not hasattr(settings, 'STATIC_URL'):
                issues.append("STATIC_URL غير معرف")
            
            # فحص STATIC_ROOT
            if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
                if not os.path.exists(settings.STATIC_ROOT):
                    issues.append(f"مجلد STATIC_ROOT غير موجود: {settings.STATIC_ROOT}")
            
            # فحص STATICFILES_DIRS
            if hasattr(settings, 'STATICFILES_DIRS'):
                for static_dir in settings.STATICFILES_DIRS:
                    if not os.path.exists(static_dir):
                        issues.append(f"مجلد الملفات الثابتة غير موجود: {static_dir}")
            
            if issues:
                for issue in issues:
                    self.log_error(Exception(issue), "Static Files Configuration", "WARNING")
            else:
                self.log_info("إعدادات الملفات الثابتة صحيحة", "Static Files Configuration")
        
        except Exception as e:
            self.log_error(e, "Static Files Configuration Check", "ERROR")
        
        return issues
    
    def check_security_settings(self):
        """فحص الإعدادات الأمنية"""
        print("🔒 فحص الإعدادات الأمنية...")
        
        warnings = []
        
        try:
            # فحص DEBUG في الإنتاج
            if getattr(settings, 'DEBUG', True):
                warnings.append("تحذير: DEBUG=True في الإنتاج يمكن أن يكون خطراً أمنياً")
            
            # فحص ALLOWED_HOSTS
            if hasattr(settings, 'ALLOWED_HOSTS') and not settings.ALLOWED_HOSTS:
                warnings.append("ALLOWED_HOSTS فارغ - قد يسبب مشاكل في الإنتاج")
            
            # فحص CSRF settings
            if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
                warnings.append("CSRF_COOKIE_SECURE=False - يفضل True في الإنتاج")
            
            # فحص SESSION settings
            if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
                warnings.append("SESSION_COOKIE_SECURE=False - يفضل True في الإنتاج")
            
            if warnings:
                for warning in warnings:
                    self.log_error(Exception(warning), "Security Settings", "WARNING")
            else:
                self.log_info("الإعدادات الأمنية آمنة", "Security Settings")
        
        except Exception as e:
            self.log_error(e, "Security Settings Check", "ERROR")
        
        return warnings
    
    def run_comprehensive_check(self):
        """تشغيل الفحص الشامل"""
        print("🚀 بدء الفحص الشامل للنظام...")
        print("="*50)
        
        # فحص إعدادات Django
        django_issues = self.check_django_configuration()
        
        # فحص قاعدة البيانات  
        db_status = self.check_database_connection()
        
        # فحص الملفات الثابتة
        static_issues = self.check_static_files_configuration()
        
        # فحص الأمان
        security_warnings = self.check_security_settings()
        
        # تحديث حالة النظام
        if self.stats['critical_errors'] > 0:
            self.stats['system_status'] = 'critical_errors'
        elif self.stats['total_errors'] > 0:
            self.stats['system_status'] = 'errors_detected'
        elif self.stats['warnings'] > 0:
            self.stats['system_status'] = 'warnings_detected'
        else:
            self.stats['system_status'] = 'healthy'
        
        return {
            'django_issues': django_issues,
            'database_status': db_status,
            'static_issues': static_issues,
            'security_warnings': security_warnings,
            'system_status': self.stats['system_status']
        }
    
    def generate_report(self):
        """توليد تقرير شامل"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_status': self.stats['system_status'],
            'statistics': self.stats,
            'errors': self.error_log,
            'warnings': self.warning_log,
            'info_messages': self.info_log[-10:],  # آخر 10 رسائل معلومات
            'recommendations': self._generate_recommendations()
        }
        
        # حفظ التقرير
        report_file = f'logs/error_monitoring_report_{int(datetime.now().timestamp())}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 تم حفظ تقرير المراقبة في: {report_file}")
        
        # طباعة ملخص
        self._print_summary()
        
        return report
    
    def _generate_recommendations(self):
        """توليد توصيات بناءً على الأخطاء المكتشفة"""
        recommendations = []
        
        if self.stats['critical_errors'] > 0:
            recommendations.append("إصلاح الأخطاء الحرجة فوراً قبل النشر")
        
        if self.stats['total_errors'] > 5:
            recommendations.append("مراجعة وإصلاح الأخطاء المتراكمة")
        
        if self.stats['warnings'] > 10:
            recommendations.append("مراجعة التحذيرات وتحسين الإعدادات")
        
        # توصيات عامة
        recommendations.extend([
            "تفعيل مراقبة الأداء المستمرة",
            "إعداد نظام تنبيهات للأخطاء الحرجة",
            "مراجعة دورية للأمان والأداء",
            "عمل نسخ احتياطية منتظمة"
        ])
        
        return recommendations
    
    def _print_summary(self):
        """طباعة ملخص التقرير"""
        print("\n" + "="*60)
        print("📊 ملخص مراقبة النظام")
        print("="*60)
        print(f"📈 حالة النظام: {self.stats['system_status']}")
        print(f"🔴 أخطاء حرجة: {self.stats['critical_errors']}")
        print(f"⚠️ أخطاء عامة: {self.stats['total_errors']}")
        print(f"🟡 تحذيرات: {self.stats['warnings']}")
        print(f"ℹ️ رسائل معلومات: {self.stats['info_messages']}")
        print("="*60)
        
        if self.stats['system_status'] == 'healthy':
            print("✅ النظام يعمل بصحة جيدة!")
        else:
            print("⚠️ يوجد مشاكل تحتاج لمراجعة")

def main():
    """الدالة الرئيسية"""
    print("🔍 نظام مراقبة الأخطاء المتطور")
    print("Advanced Error Monitoring System")
    print("="*50)
    
    monitor = AdvancedErrorMonitor()
    
    # تشغيل الفحص الشامل
    check_results = monitor.run_comprehensive_check()
    
    # توليد التقرير
    report = monitor.generate_report()
    
    print("\n✨ تم إكمال عملية المراقبة والفحص")
    
    return report

if __name__ == "__main__":
    main()