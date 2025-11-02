#!/usr/bin/env python
"""
نظام تحسين الأداء المتطور
Advanced Performance Optimization System

تطوير شامل لتحسين أداء نظام إدارة الجامعة
Created: 2025-11-02
Author: AI Development Assistant

يشمل تحسين قاعدة البيانات، الذاكرة، الشبكة، والملفات
"""

import os
import sys
import json
import logging
import time
import gc
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sqlite3
from collections import defaultdict
import hashlib
import shutil

# إعداد المسارات
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.conf import settings
from django.db import connection, transaction
from django.core.cache import cache
from django.core.management import call_command
from django.apps import apps

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedPerformanceOptimizer:
    """
    نظام تحسين الأداء المتطور
    يوفر تحسينات شاملة للنظام
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.optimization_log = []
        self.performance_metrics = {}
        
        logger.info("🚀 تم تشغيل نظام تحسين الأداء المتطور")
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """تحليل أداء قاعدة البيانات"""
        logger.info("🔍 تحليل أداء قاعدة البيانات...")
        
        analysis = {
            'tables': {},
            'indexes': [],
            'queries': [],
            'size_analysis': {},
            'recommendations': []
        }
        
        try:
            with connection.cursor() as cursor:
                # تحليل الجداول
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    # حجم الجدول
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    # معلومات الأعمدة
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    analysis['tables'][table] = {
                        'row_count': row_count,
                        'column_count': len(columns),
                        'columns': [col[1] for col in columns]
                    }
                
                # تحليل الفهارس
                cursor.execute("""
                    SELECT name, sql FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                
                indexes = cursor.fetchall()
                analysis['indexes'] = [{'name': idx[0], 'sql': idx[1]} for idx in indexes]
                
                # حجم قاعدة البيانات
                db_path = settings.DATABASES['default']['NAME']
                if os.path.exists(db_path):
                    db_size = os.path.getsize(db_path)
                    analysis['size_analysis'] = {
                        'size_bytes': db_size,
                        'size_mb': round(db_size / 1024 / 1024, 2)
                    }
                
        except Exception as e:
            logger.error(f"خطأ في تحليل قاعدة البيانات: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def optimize_database_indexes(self) -> Dict[str, Any]:
        """تحسين فهارس قاعدة البيانات"""
        logger.info("📊 تحسين فهارس قاعدة البيانات...")
        
        optimization_results = {
            'created_indexes': [],
            'analyzed_tables': [],
            'performance_improvements': {}
        }
        
        try:
            with connection.cursor() as cursor:
                # فهارس مقترحة للتحسين
                suggested_indexes = [
                    # فهارس للجداول الشائعة
                    "CREATE INDEX IF NOT EXISTS idx_auth_user_username ON auth_user(username)",
                    "CREATE INDEX IF NOT EXISTS idx_auth_user_email ON auth_user(email)",
                    "CREATE INDEX IF NOT EXISTS idx_django_session_expire_date ON django_session(expire_date)",
                ]
                
                # الحصول على جداول Django models
                app_models = []
                for app_config in apps.get_app_configs():
                    for model in app_config.get_models():
                        table_name = model._meta.db_table
                        app_models.append((table_name, model))
                
                # إنشاء فهارس للجداول المخصصة
                for table_name, model in app_models:
                    # فهرس للمفتاح الأساسي إذا لم يكن موجوداً
                    pk_field = model._meta.pk.column
                    if pk_field != 'id':  # ID عادة يكون له فهرس تلقائي
                        suggested_indexes.append(
                            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{pk_field} ON {table_name}({pk_field})"
                        )
                    
                    # فهارس للمفاتيح الأجنبية
                    for field in model._meta.get_fields():
                        if hasattr(field, 'related_model') and field.related_model:
                            column_name = field.column
                            suggested_indexes.append(
                                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name}({column_name})"
                            )
                
                # إنشاء الفهارس
                for index_sql in suggested_indexes:
                    try:
                        cursor.execute(index_sql)
                        optimization_results['created_indexes'].append(index_sql)
                        logger.info(f"✅ تم إنشاء الفهرس: {index_sql}")
                    except Exception as e:
                        logger.warning(f"تحذير في إنشاء الفهرس: {e}")
                
                # تحليل الجداول
                cursor.execute("ANALYZE")
                optimization_results['analyzed_tables'].append("جميع الجداول")
                
                logger.info("✅ تم تحسين فهارس قاعدة البيانات")
                
        except Exception as e:
            logger.error(f"خطأ في تحسين الفهارس: {e}")
            optimization_results['error'] = str(e)
        
        return optimization_results
    
    def clean_database(self) -> Dict[str, Any]:
        """تنظيف قاعدة البيانات"""
        logger.info("🧹 تنظيف قاعدة البيانات...")
        
        cleaning_results = {
            'operations': [],
            'space_saved': 0,
            'errors': []
        }
        
        try:
            with connection.cursor() as cursor:
                # قياس حجم قاعدة البيانات قبل التنظيف
                db_path = settings.DATABASES['default']['NAME']
                size_before = os.path.getsize(db_path) if os.path.exists(db_path) else 0
                
                # تنظيف الجلسات منتهية الصلاحية
                cursor.execute("DELETE FROM django_session WHERE expire_date < datetime('now')")
                deleted_sessions = cursor.rowcount
                cleaning_results['operations'].append(f"حذف {deleted_sessions} جلسة منتهية الصلاحية")
                
                # تنظيف admin logs القديمة (أكثر من 30 يوم)
                cursor.execute("""
                    DELETE FROM django_admin_log 
                    WHERE action_time < datetime('now', '-30 days')
                """)
                deleted_logs = cursor.rowcount
                cleaning_results['operations'].append(f"حذف {deleted_logs} سجل إداري قديم")
                
                # تحسين قاعدة البيانات
                cursor.execute("VACUUM")
                cleaning_results['operations'].append("تم تحسين وضغط قاعدة البيانات (VACUUM)")
                
                # قياس حجم قاعدة البيانات بعد التنظيف
                size_after = os.path.getsize(db_path) if os.path.exists(db_path) else 0
                space_saved = size_before - size_after
                cleaning_results['space_saved'] = space_saved
                
                logger.info(f"✅ تم توفير {space_saved / 1024:.2f} KB من المساحة")
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف قاعدة البيانات: {e}")
            cleaning_results['errors'].append(str(e))
        
        return cleaning_results
    
    def optimize_static_files(self) -> Dict[str, Any]:
        """تحسين الملفات الثابتة"""
        logger.info("📁 تحسين الملفات الثابتة...")
        
        optimization_results = {
            'collected_files': 0,
            'compressed_files': [],
            'duplicates_removed': [],
            'size_optimization': {}
        }
        
        try:
            # جمع الملفات الثابتة
            call_command('collectstatic', '--noinput', verbosity=0)
            
            # عد الملفات المجمعة
            static_root = getattr(settings, 'STATIC_ROOT', None)
            if static_root and os.path.exists(static_root):
                file_count = sum(len(files) for _, _, files in os.walk(static_root))
                optimization_results['collected_files'] = file_count
                
                # تحسين الملفات CSS و JS (ضغط أساسي)
                self._optimize_css_js_files(static_root, optimization_results)
                
                # إزالة الملفات المكررة
                self._remove_duplicate_files(static_root, optimization_results)
            
            logger.info("✅ تم تحسين الملفات الثابتة")
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الملفات الثابتة: {e}")
            optimization_results['error'] = str(e)
        
        return optimization_results
    
    def _optimize_css_js_files(self, static_root: str, results: Dict[str, Any]):
        """تحسين ملفات CSS و JS"""
        try:
            for root, dirs, files in os.walk(static_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # تحسين ملفات CSS
                    if file.endswith('.css') and not file.endswith('.min.css'):
                        original_size = os.path.getsize(file_path)
                        self._minify_css_file(file_path)
                        new_size = os.path.getsize(file_path)
                        
                        if new_size < original_size:
                            results['compressed_files'].append({
                                'file': file,
                                'type': 'css',
                                'original_size': original_size,
                                'new_size': new_size,
                                'savings': original_size - new_size
                            })
                    
                    # تحسين ملفات JS
                    elif file.endswith('.js') and not file.endswith('.min.js'):
                        original_size = os.path.getsize(file_path)
                        self._minify_js_file(file_path)
                        new_size = os.path.getsize(file_path)
                        
                        if new_size < original_size:
                            results['compressed_files'].append({
                                'file': file,
                                'type': 'js',
                                'original_size': original_size,
                                'new_size': new_size,
                                'savings': original_size - new_size
                            })
                            
        except Exception as e:
            logger.warning(f"تحذير في تحسين CSS/JS: {e}")
    
    def _minify_css_file(self, file_path: str):
        """ضغط ملف CSS (تحسين بسيط)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تحسينات بسيطة للـ CSS
            # إزالة التعليقات
            import re
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # إزالة المسافات الزائدة
            content = re.sub(r'\s+', ' ', content)
            # إزالة المسافات حول الرموز
            content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
                
        except Exception as e:
            logger.warning(f"خطأ في ضغط CSS {file_path}: {e}")
    
    def _minify_js_file(self, file_path: str):
        """ضغط ملف JS (تحسين بسيط)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تحسينات بسيطة للـ JS
            import re
            # إزالة التعليقات الخطية
            content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
            # إزالة التعليقات متعددة الأسطر
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # إزالة المسافات الزائدة
            content = re.sub(r'\s+', ' ', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
                
        except Exception as e:
            logger.warning(f"خطأ في ضغط JS {file_path}: {e}")
    
    def _remove_duplicate_files(self, static_root: str, results: Dict[str, Any]):
        """إزالة الملفات المكررة"""
        try:
            file_hashes = defaultdict(list)
            
            # حساب hash لكل ملف
            for root, dirs, files in os.walk(static_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hashes[file_hash].append(file_path)
            
            # إزالة الملفات المكررة
            for file_hash, file_paths in file_hashes.items():
                if len(file_paths) > 1:
                    # الاحتفاظ بالملف الأول وحذف الباقي
                    for duplicate_path in file_paths[1:]:
                        os.remove(duplicate_path)
                        results['duplicates_removed'].append(duplicate_path)
                        
        except Exception as e:
            logger.warning(f"خطأ في إزالة الملفات المكررة: {e}")
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """تحسين استخدام الذاكرة"""
        logger.info("🧠 تحسين استخدام الذاكرة...")
        
        memory_optimization = {
            'before_gc': {},
            'after_gc': {},
            'cache_cleared': False,
            'optimizations_applied': []
        }
        
        try:
            # قياس الذاكرة قبل التحسين
            try:
                import psutil
                process = psutil.Process()
                memory_optimization['before_gc']['memory_mb'] = round(
                    process.memory_info().rss / 1024 / 1024, 2
                )
            except ImportError:
                memory_optimization['before_gc']['memory_mb'] = 'psutil not available'
            
            # مسح الكاش
            try:
                cache.clear()
                memory_optimization['cache_cleared'] = True
                memory_optimization['optimizations_applied'].append('cache_cleared')
            except Exception as e:
                logger.warning(f"تحذير في مسح الكاش: {e}")
            
            # تشغيل جامع القمامة
            collected = gc.collect()
            memory_optimization['garbage_collected'] = collected
            memory_optimization['optimizations_applied'].append('garbage_collection')
            
            # قياس الذاكرة بعد التحسين
            try:
                import psutil
                process = psutil.Process()
                memory_optimization['after_gc']['memory_mb'] = round(
                    process.memory_info().rss / 1024 / 1024, 2
                )
                
                # حساب التوفير
                before = memory_optimization['before_gc']['memory_mb']
                after = memory_optimization['after_gc']['memory_mb']
                if isinstance(before, (int, float)) and isinstance(after, (int, float)):
                    memory_optimization['memory_saved_mb'] = round(before - after, 2)
                    
            except ImportError:
                memory_optimization['after_gc']['memory_mb'] = 'psutil not available'
            
            logger.info("✅ تم تحسين استخدام الذاكرة")
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الذاكرة: {e}")
            memory_optimization['error'] = str(e)
        
        return memory_optimization
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """إنشاء تقرير الأداء الشامل"""
        logger.info("📊 إنشاء تقرير الأداء...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'optimization_duration': time.time() - self.start_time,
            'database_analysis': self.analyze_database_performance(),
            'database_optimization': self.optimize_database_indexes(),
            'database_cleaning': self.clean_database(),
            'static_files_optimization': self.optimize_static_files(),
            'memory_optimization': self.optimize_memory_usage(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """إنشاء توصيات التحسين"""
        recommendations = [
            "تشغيل تحسين قاعدة البيانات بشكل دوري (أسبوعياً)",
            "مراقبة حجم قاعدة البيانات ومسح البيانات غير المستخدمة",
            "استخدام Redis أو Memcached للتخزين المؤقت في الإنتاج",
            "ضغط الملفات الثابتة واستخدام CDN",
            "تفعيل GZIP compression في الخادم",
            "مراقبة استخدام الذاكرة وإعادة تشغيل الخدمة عند الحاجة",
            "استخدام connection pooling لقاعدة البيانات",
            "تحسين استعلامات قاعدة البيانات وتجنب N+1 queries"
        ]
        
        return recommendations
    
    def run_full_optimization(self) -> Dict[str, Any]:
        """تشغيل التحسين الشامل"""
        logger.info("🎯 بدء التحسين الشامل للأداء...")
        
        try:
            report = self.generate_performance_report()
            
            # حفظ التقرير
            report_path = BASE_DIR / 'logs' / f'performance_optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ تم حفظ تقرير الأداء: {report_path}")
            report['report_saved_to'] = str(report_path)
            
            logger.info("🏆 تم إكمال التحسين الشامل للأداء!")
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في التحسين الشامل: {e}")
            return {'error': str(e)}

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("⚡ نظام تحسين الأداء المتطور")
    print("   Advanced Performance Optimization System")
    print("="*60)
    
    try:
        optimizer = AdvancedPerformanceOptimizer()
        results = optimizer.run_full_optimization()
        
        # عرض ملخص النتائج
        print("\n📊 ملخص التحسين:")
        print("-" * 40)
        
        if 'database_optimization' in results:
            db_opt = results['database_optimization']
            print(f"✅ تم إنشاء {len(db_opt.get('created_indexes', []))} فهرس جديد")
        
        if 'database_cleaning' in results:
            db_clean = results['database_cleaning']
            space_saved = db_clean.get('space_saved', 0)
            print(f"✅ تم توفير {space_saved / 1024:.2f} KB من المساحة")
        
        if 'static_files_optimization' in results:
            static_opt = results['static_files_optimization']
            files_count = static_opt.get('collected_files', 0)
            print(f"✅ تم تحسين {files_count} ملف ثابت")
        
        if 'memory_optimization' in results:
            memory_opt = results['memory_optimization']
            saved = memory_opt.get('memory_saved_mb', 0)
            if isinstance(saved, (int, float)) and saved > 0:
                print(f"✅ تم توفير {saved} MB من الذاكرة")
        
        if 'report_saved_to' in results:
            print(f"📄 تم حفظ التقرير: {results['report_saved_to']}")
        
        print("\n🎉 تم إكمال تحسين الأداء بنجاح!")
        
        return 0
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل النظام: {e}")
        print(f"❌ خطأ: {e}")
        return 1

if __name__ == "__main__":
    exit(main())