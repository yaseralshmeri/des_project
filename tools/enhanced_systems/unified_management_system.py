#!/usr/bin/env python
"""
نظام الإدارة الموحد المتطور
Unified Advanced Management System

تطوير وتحسين شامل لنظام إدارة الجامعة
Created: 2025-11-02
Author: AI Development Assistant

هذا النظام يوحد جميع أدوات التحسين والإدارة في مكان واحد
ويوفر واجهة موحدة لإدارة النظام بالكامل
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import sqlite3
from typing import Dict, List, Optional, Any
import requests
import time

# إعداد المسارات
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedManagementSystem:
    """
    النظام الموحد لإدارة الجامعة المتطور
    يشمل جميع وظائف التحسين والإدارة والمراقبة
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.version = "3.0.0 Enhanced"
        self.report = {
            'start_time': self.start_time.isoformat(),
            'version': self.version,
            'operations': [],
            'errors': [],
            'statistics': {},
            'improvements': []
        }
        logger.info(f"🚀 تم تشغيل النظام الموحد إصدار {self.version}")
    
    def analyze_system_health(self) -> Dict[str, Any]:
        """فحص صحة النظام الشامل"""
        logger.info("🔍 بدء فحص صحة النظام...")
        
        health_data = {
            'django': self._check_django_health(),
            'database': self._check_database_health(),
            'applications': self._check_applications_health(),
            'static_files': self._check_static_files(),
            'security': self._check_security_status(),
            'performance': self._check_performance_metrics()
        }
        
        self.report['operations'].append({
            'operation': 'System Health Check',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'data': health_data
        })
        
        return health_data
    
    def _check_django_health(self) -> Dict[str, Any]:
        """فحص صحة Django"""
        try:
            # فحص إعدادات Django
            from django.core.management.base import BaseCommand
            from django.core import checks
            
            issues = checks.run_checks()
            
            return {
                'status': 'healthy' if not issues else 'has_issues',
                'django_version': django.get_version(),
                'debug_mode': settings.DEBUG,
                'issues_count': len(issues),
                'issues': [str(issue) for issue in issues[:5]]  # أول 5 مشاكل فقط
            }
        except Exception as e:
            logger.error(f"خطأ في فحص Django: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """فحص صحة قاعدة البيانات"""
        try:
            with connection.cursor() as cursor:
                # فحص الاتصال
                cursor.execute("SELECT 1")
                
                # إحصائيات قاعدة البيانات
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                # حجم قاعدة البيانات
                db_size = os.path.getsize(settings.DATABASES['default']['NAME'])
                
                return {
                    'status': 'connected',
                    'tables_count': len(tables),
                    'size_mb': round(db_size / 1024 / 1024, 2),
                    'engine': settings.DATABASES['default']['ENGINE']
                }
                
        except Exception as e:
            logger.error(f"خطأ في فحص قاعدة البيانات: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_applications_health(self) -> Dict[str, Any]:
        """فحص صحة التطبيقات"""
        try:
            from django.apps import apps
            
            installed_apps = list(apps.get_app_configs())
            custom_apps = [app for app in installed_apps 
                          if not app.name.startswith(('django.', 'rest_framework'))]
            
            return {
                'total_apps': len(installed_apps),
                'custom_apps': len(custom_apps),
                'custom_app_names': [app.name for app in custom_apps],
                'status': 'healthy'
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص التطبيقات: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_static_files(self) -> Dict[str, Any]:
        """فحص الملفات الثابتة"""
        try:
            static_root = getattr(settings, 'STATIC_ROOT', None)
            static_url = getattr(settings, 'STATIC_URL', '/static/')
            
            static_files_count = 0
            if static_root and os.path.exists(static_root):
                for root, dirs, files in os.walk(static_root):
                    static_files_count += len(files)
            
            return {
                'static_url': static_url,
                'static_root': str(static_root) if static_root else None,
                'files_count': static_files_count,
                'status': 'configured'
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص الملفات الثابتة: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_security_status(self) -> Dict[str, Any]:
        """فحص حالة الأمان"""
        try:
            security_checks = {
                'debug_mode': not settings.DEBUG,  # False هو آمن
                'secret_key_secure': len(getattr(settings, 'SECRET_KEY', '')) > 50,
                'https_settings': all([
                    getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
                    getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
                ]),
                'csrf_protection': 'django.middleware.csrf.CsrfViewMiddleware' in 
                                 getattr(settings, 'MIDDLEWARE', [])
            }
            
            security_score = sum(security_checks.values()) / len(security_checks) * 100
            
            return {
                'security_score': round(security_score, 1),
                'checks': security_checks,
                'status': 'secure' if security_score > 75 else 'needs_improvement'
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص الأمان: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_performance_metrics(self) -> Dict[str, Any]:
        """فحص مقاييس الأداء"""
        try:
            import psutil
            
            # معلومات النظام
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
                'disk_usage': disk.percent,
                'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                'status': 'optimal' if cpu_percent < 80 and memory.percent < 80 else 'high_usage'
            }
            
        except ImportError:
            return {'status': 'psutil_not_available'}
        except Exception as e:
            logger.error(f"خطأ في فحص الأداء: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def optimize_database(self) -> Dict[str, Any]:
        """تحسين قاعدة البيانات"""
        logger.info("🔧 بدء تحسين قاعدة البيانات...")
        
        optimization_results = {}
        
        try:
            with connection.cursor() as cursor:
                # تحسين SQLite
                if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                    # تنظيف قاعدة البيانات
                    cursor.execute("VACUUM;")
                    optimization_results['vacuum'] = 'completed'
                    
                    # إعادة تحليل الإحصائيات
                    cursor.execute("ANALYZE;")
                    optimization_results['analyze'] = 'completed'
                    
                    # فحص التكامل
                    cursor.execute("PRAGMA integrity_check;")
                    integrity_result = cursor.fetchone()
                    optimization_results['integrity_check'] = integrity_result[0]
                
                logger.info("✅ تم تحسين قاعدة البيانات بنجاح")
                
        except Exception as e:
            logger.error(f"خطأ في تحسين قاعدة البيانات: {e}")
            optimization_results['error'] = str(e)
        
        self.report['operations'].append({
            'operation': 'Database Optimization',
            'timestamp': datetime.now().isoformat(),
            'results': optimization_results
        })
        
        return optimization_results
    
    def enhance_security(self) -> Dict[str, Any]:
        """تعزيز الأمان"""
        logger.info("🔒 بدء تعزيز الأمان...")
        
        security_enhancements = []
        
        try:
            # فحص إعدادات الأمان الحالية
            current_settings = {}
            
            # تحديث إعدادات الأمان إذا لزم الأمر
            security_improvements = {
                'DEBUG': False,
                'SECURE_BROWSER_XSS_FILTER': True,
                'SECURE_CONTENT_TYPE_NOSNIFF': True,
                'X_FRAME_OPTIONS': 'SAMEORIGIN',
            }
            
            for setting, value in security_improvements.items():
                current_value = getattr(settings, setting, None)
                if current_value != value:
                    security_enhancements.append({
                        'setting': setting,
                        'current': current_value,
                        'recommended': value,
                        'action': 'should_update'
                    })
                else:
                    security_enhancements.append({
                        'setting': setting,
                        'status': 'already_secure'
                    })
            
            logger.info("✅ تم فحص إعدادات الأمان")
            
        except Exception as e:
            logger.error(f"خطأ في تعزيز الأمان: {e}")
            security_enhancements.append({'error': str(e)})
        
        self.report['operations'].append({
            'operation': 'Security Enhancement',
            'timestamp': datetime.now().isoformat(),
            'enhancements': security_enhancements
        })
        
        return {'enhancements': security_enhancements}
    
    def collect_system_statistics(self) -> Dict[str, Any]:
        """جمع إحصائيات النظام"""
        logger.info("📊 جمع إحصائيات النظام...")
        
        try:
            User = get_user_model()
            
            # إحصائيات قاعدة البيانات
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = cursor.fetchall()
            
            # إحصائيات الملفات
            file_stats = self._count_files()
            
            statistics = {
                'database': {
                    'tables_count': len(tables),
                    'users_count': User.objects.count(),
                },
                'files': file_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self.report['statistics'] = statistics
            logger.info("✅ تم جمع إحصائيات النظام")
            
            return statistics
            
        except Exception as e:
            logger.error(f"خطأ في جمع الإحصائيات: {e}")
            return {'error': str(e)}
    
    def _count_files(self) -> Dict[str, int]:
        """عد الملفات في المشروع"""
        file_counts = {
            'python_files': 0,
            'html_files': 0,
            'css_files': 0,
            'js_files': 0,
            'total_files': 0
        }
        
        for root, dirs, files in os.walk(BASE_DIR):
            # تجاهل مجلدات معينة
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                file_counts['total_files'] += 1
                
                if file.endswith('.py'):
                    file_counts['python_files'] += 1
                elif file.endswith('.html'):
                    file_counts['html_files'] += 1
                elif file.endswith('.css'):
                    file_counts['css_files'] += 1
                elif file.endswith('.js'):
                    file_counts['js_files'] += 1
        
        return file_counts
    
    def generate_comprehensive_report(self) -> str:
        """إنشاء تقرير شامل"""
        logger.info("📄 إنشاء التقرير الشامل...")
        
        # إكمال التقرير
        self.report['end_time'] = datetime.now().isoformat()
        self.report['duration_seconds'] = (datetime.now() - self.start_time).total_seconds()
        
        # إنشاء ملف التقرير
        report_path = BASE_DIR / 'logs' / f'comprehensive_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # إنشاء مجلد logs إذا لم يكن موجوداً
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ تم إنشاء التقرير: {report_path}")
        
        return str(report_path)
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """تشغيل التحليل الشامل"""
        logger.info("🎯 بدء التحليل الشامل للنظام...")
        
        results = {}
        
        try:
            # 1. فحص صحة النظام
            results['health_check'] = self.analyze_system_health()
            
            # 2. تحسين قاعدة البيانات
            results['database_optimization'] = self.optimize_database()
            
            # 3. تعزيز الأمان
            results['security_enhancement'] = self.enhance_security()
            
            # 4. جمع الإحصائيات
            results['statistics'] = self.collect_system_statistics()
            
            # 5. إنشاء التقرير
            results['report_path'] = self.generate_comprehensive_report()
            
            logger.info("🏆 تم إكمال التحليل الشامل بنجاح!")
            
        except Exception as e:
            logger.error(f"خطأ في التحليل الشامل: {e}")
            results['error'] = str(e)
        
        return results

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("🎓 نظام الإدارة الموحد المتطور للجامعة")
    print("   Unified Advanced University Management System")
    print("="*60)
    
    try:
        # إنشاء نظام الإدارة
        management_system = UnifiedManagementSystem()
        
        # تشغيل التحليل الشامل
        results = management_system.run_comprehensive_analysis()
        
        # عرض النتائج
        print("\n📊 ملخص النتائج:")
        print("-" * 40)
        
        if 'health_check' in results:
            health = results['health_check']
            print(f"✅ Django: {health.get('django', {}).get('status', 'unknown')}")
            print(f"✅ Database: {health.get('database', {}).get('status', 'unknown')}")
            print(f"✅ Applications: {health.get('applications', {}).get('total_apps', 0)} apps")
        
        if 'statistics' in results:
            stats = results['statistics']
            print(f"📊 Tables: {stats.get('database', {}).get('tables_count', 0)}")
            print(f"📊 Files: {stats.get('files', {}).get('total_files', 0)}")
        
        if 'report_path' in results:
            print(f"📄 Report: {results['report_path']}")
        
        print("\n🎉 تم إكمال النظام بنجاح!")
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل النظام: {e}")
        print(f"❌ خطأ: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())