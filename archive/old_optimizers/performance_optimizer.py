#!/usr/bin/env python3
"""
نظام تحسين الأداء المتقدم للمشروع الجامعي
Advanced Performance Optimizer for University System
Created: 2024-11-02
"""

import os
import sys
import django
import time
from pathlib import Path

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.core.cache import cache
from django.conf import settings


class PerformanceOptimizer:
    """محسن الأداء المتقدم"""
    
    def __init__(self):
        self.results = {
            'database': [],
            'cache': [],
            'static_files': [],
            'code_quality': [],
            'security': []
        }
    
    def optimize_database(self):
        """تحسين قاعدة البيانات"""
        print("🔧 تحسين قاعدة البيانات...")
        
        # فحص الجداول
        with connection.cursor() as cursor:
            # إحصائيات الجداول
            cursor.execute("""
                SELECT name, type FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = cursor.fetchall()
            self.results['database'].append(f"عدد الجداول: {len(tables)}")
            
            # فحص الفهارس
            for table_name, _ in tables:
                cursor.execute(f"PRAGMA index_list('{table_name}')")
                indexes = cursor.fetchall()
                if len(indexes) < 2:  # أقل من فهرسين
                    self.results['database'].append(f"⚠️ الجدول {table_name} يحتاج المزيد من الفهارس")
        
        # تنظيف قاعدة البيانات
        with connection.cursor() as cursor:
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            self.results['database'].append("✅ تم تنظيف قاعدة البيانات")
    
    def optimize_cache(self):
        """تحسين التخزين المؤقت"""
        print("⚡ تحسين التخزين المؤقت...")
        
        # اختبار سرعة Cache
        start_time = time.time()
        cache.set('performance_test', 'test_value', 30)
        cache.get('performance_test')
        cache_speed = time.time() - start_time
        
        self.results['cache'].append(f"سرعة Cache: {cache_speed:.4f} ثانية")
        
        if cache_speed > 0.01:
            self.results['cache'].append("⚠️ Cache بطيء - يُنصح بـ Redis")
        else:
            self.results['cache'].append("✅ Cache سريع")
    
    def optimize_static_files(self):
        """تحسين الملفات الثابتة"""
        print("📁 تحسين الملفات الثابتة...")
        
        static_dirs = [
            Path(settings.BASE_DIR) / 'static',
            Path(settings.BASE_DIR) / 'staticfiles'
        ]
        
        total_size = 0
        file_count = 0
        
        for static_dir in static_dirs:
            if static_dir.exists():
                for file_path in static_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
        
        total_size_mb = total_size / (1024 * 1024)
        self.results['static_files'].append(f"عدد الملفات الثابتة: {file_count}")
        self.results['static_files'].append(f"حجم الملفات الثابتة: {total_size_mb:.2f} MB")
        
        if total_size_mb > 50:
            self.results['static_files'].append("⚠️ الملفات الثابتة كبيرة - يُنصح بالضغط")
        else:
            self.results['static_files'].append("✅ حجم الملفات الثابتة مناسب")
    
    def check_code_quality(self):
        """فحص جودة الكود"""
        print("🔍 فحص جودة الكود...")
        
        python_files = list(Path('.').glob('**/*.py'))
        self.results['code_quality'].append(f"عدد ملفات Python: {len(python_files)}")
        
        # فحص الملفات الطويلة
        long_files = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                    if line_count > 1000:
                        long_files.append(f"{py_file}: {line_count} سطر")
            except:
                continue
        
        if long_files:
            self.results['code_quality'].append("⚠️ ملفات طويلة تحتاج تقسيم:")
            self.results['code_quality'].extend(long_files[:5])  # أول 5 ملفات
        else:
            self.results['code_quality'].append("✅ أحجام الملفات مناسبة")
    
    def check_security(self):
        """فحص الأمان"""
        print("🔐 فحص الأمان...")
        
        security_issues = []
        
        # فحص DEBUG في الإنتاج
        if settings.DEBUG:
            security_issues.append("⚠️ DEBUG=True في الإنتاج")
        
        # فحص SECRET_KEY
        if 'django-insecure' in settings.SECRET_KEY:
            security_issues.append("⚠️ SECRET_KEY غير آمن")
        
        # فحص ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            security_issues.append("⚠️ ALLOWED_HOSTS يحتوي على '*'")
        
        if security_issues:
            self.results['security'].extend(security_issues)
        else:
            self.results['security'].append("✅ الإعدادات الأمنية جيدة")
    
    def generate_recommendations(self):
        """إنشاء توصيات التحسين"""
        recommendations = []
        
        # توصيات قاعدة البيانات
        recommendations.append("📊 توصيات قاعدة البيانات:")
        recommendations.append("- إضافة فهارس للجداول الكبيرة")
        recommendations.append("- استخدام connection pooling")
        recommendations.append("- تحديث إحصائيات الجداول دورياً")
        
        # توصيات الأداء
        recommendations.append("\n⚡ توصيات الأداء:")
        recommendations.append("- استخدام Redis للـ Cache")
        recommendations.append("- تفعيل Gzip compression")
        recommendations.append("- استخدام CDN للملفات الثابتة")
        
        # توصيات الأمان
        recommendations.append("\n🔐 توصيات الأمان:")
        recommendations.append("- تحديث جميع المكتبات")
        recommendations.append("- تفعيل HTTPS في الإنتاج")
        recommendations.append("- استخدام WAF (Web Application Firewall)")
        
        return recommendations
    
    def run_optimization(self):
        """تشغيل جميع التحسينات"""
        print("🚀 بدء تحسين المشروع...")
        print("=" * 50)
        
        start_time = time.time()
        
        # تشغيل جميع التحسينات
        self.optimize_database()
        self.optimize_cache()
        self.optimize_static_files()
        self.check_code_quality()
        self.check_security()
        
        end_time = time.time()
        
        # طباعة النتائج
        print("\n📋 تقرير التحسين:")
        print("=" * 50)
        
        for category, results in self.results.items():
            if results:
                print(f"\n{category.upper()}:")
                for result in results:
                    print(f"  {result}")
        
        print(f"\n⏱️ وقت التنفيذ: {end_time - start_time:.2f} ثانية")
        
        # طباعة التوصيات
        print("\n💡 توصيات التحسين:")
        print("=" * 50)
        recommendations = self.generate_recommendations()
        for rec in recommendations:
            print(rec)
        
        print("\n✅ اكتمل تحسين المشروع!")


def main():
    """الدالة الرئيسية"""
    optimizer = PerformanceOptimizer()
    optimizer.run_optimization()


if __name__ == "__main__":
    main()