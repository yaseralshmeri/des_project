"""
نظام إدارة قاعدة البيانات المطور
Enhanced Database Management System

تم تطويره في: 2025-11-02
يوفر أدوات متقدمة لتحسين وإدارة قاعدة البيانات
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.core.cache import cache
import json

logger = logging.getLogger('university')


class DatabaseOptimizer:
    """مُحسن قاعدة البيانات"""
    
    def __init__(self):
        self.db_path = settings.DATABASES['default']['NAME']
        self.backup_dir = os.path.join(settings.BASE_DIR, 'database_backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def analyze_database(self):
        """تحليل شامل لقاعدة البيانات"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'database_info': self._get_database_info(),
            'table_analysis': self._analyze_tables(),
            'index_analysis': self._analyze_indexes(),
            'performance_metrics': self._get_performance_metrics(),
            'recommendations': []
        }
        
        # إنشاء التوصيات
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _get_database_info(self):
        """معلومات قاعدة البيانات العامة"""
        try:
            # حجم الملف
            db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            
            with connection.cursor() as cursor:
                # عدد الجداول
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                table_count = cursor.fetchone()[0]
                
                # عدد الفهارس
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                index_count = cursor.fetchone()[0]
                
                # إعدادات SQLite
                pragma_info = {}
                pragmas = ['journal_mode', 'synchronous', 'cache_size', 'temp_store']
                for pragma in pragmas:
                    cursor.execute(f"PRAGMA {pragma}")
                    result = cursor.fetchone()
                    pragma_info[pragma] = result[0] if result else None
            
            return {
                'size_mb': round(db_size, 2),
                'table_count': table_count,
                'index_count': index_count,
                'sqlite_version': sqlite3.sqlite_version,
                'pragma_settings': pragma_info
            }
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}
    
    def _analyze_tables(self):
        """تحليل الجداول"""
        table_analysis = {}
        
        try:
            with connection.cursor() as cursor:
                # الحصول على قائمة الجداول
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    try:
                        # عدد الصفوف
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        row_count = cursor.fetchone()[0]
                        
                        # معلومات الجدول
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = cursor.fetchall()
                        
                        # حجم الجدول (تقريبي)
                        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                        sample_row = cursor.fetchone()
                        estimated_size = 0
                        if sample_row:
                            estimated_size = len(str(sample_row)) * row_count / (1024 * 1024)  # MB
                        
                        table_analysis[table] = {
                            'row_count': row_count,
                            'column_count': len(columns),
                            'estimated_size_mb': round(estimated_size, 3),
                            'columns': [{'name': col[1], 'type': col[2], 'notnull': bool(col[3])} for col in columns]
                        }
                        
                    except Exception as e:
                        logger.error(f"Error analyzing table {table}: {e}")
                        table_analysis[table] = {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Error in table analysis: {e}")
        
        return table_analysis
    
    def _analyze_indexes(self):
        """تحليل الفهارس"""
        index_analysis = {}
        
        try:
            with connection.cursor() as cursor:
                # الحصول على قائمة الفهارس
                cursor.execute("""
                    SELECT name, tbl_name, sql FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                    ORDER BY tbl_name, name
                """)
                indexes = cursor.fetchall()
                
                for index in indexes:
                    index_name, table_name, sql = index
                    
                    try:
                        # معلومات الفهرس
                        cursor.execute(f"PRAGMA index_info({index_name})")
                        index_info = cursor.fetchall()
                        
                        index_analysis[index_name] = {
                            'table': table_name,
                            'sql': sql,
                            'columns': [{'seqno': info[0], 'cid': info[1], 'name': info[2]} for info in index_info],
                            'column_count': len(index_info)
                        }
                        
                    except Exception as e:
                        logger.error(f"Error analyzing index {index_name}: {e}")
                        index_analysis[index_name] = {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Error in index analysis: {e}")
        
        return index_analysis
    
    def _get_performance_metrics(self):
        """مقاييس الأداء"""
        try:
            with connection.cursor() as cursor:
                # إحصائيات عامة
                cursor.execute("PRAGMA compile_options")
                compile_options = [row[0] for row in cursor.fetchall()]
                
                # فحص التجزئة
                cursor.execute("PRAGMA integrity_check(10)")
                integrity_results = [row[0] for row in cursor.fetchall()]
                
                # حجم الصفحة
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                
                # عدد الصفحات
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                
                return {
                    'page_size': page_size,
                    'page_count': page_count,
                    'integrity_check': integrity_results[:5],  # أول 5 نتائج
                    'compile_options': compile_options[:10]   # أول 10 خيارات
                }
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def _generate_recommendations(self, analysis):
        """إنشاء توصيات التحسين"""
        recommendations = []
        
        # توصيات حجم قاعدة البيانات
        db_size = analysis['database_info'].get('size_mb', 0)
        if db_size > 100:  # أكبر من 100MB
            recommendations.append({
                'type': 'size',
                'priority': 'medium',
                'message': f'حجم قاعدة البيانات كبير ({db_size} MB). يُنصح بأرشفة البيانات القديمة.',
                'action': 'archive_old_data'
            })
        
        # توصيات الجداول
        table_analysis = analysis.get('table_analysis', {})
        for table_name, table_info in table_analysis.items():
            if 'row_count' in table_info:
                row_count = table_info['row_count']
                
                # جداول كبيرة بدون فهارس كافية
                if row_count > 10000:
                    index_analysis = analysis.get('index_analysis', {})
                    table_indexes = [idx for idx, info in index_analysis.items() 
                                   if info.get('table') == table_name]
                    
                    if len(table_indexes) < 2:  # أقل من فهرسين
                        recommendations.append({
                            'type': 'index',
                            'priority': 'high',
                            'message': f'الجدول {table_name} يحتوي على {row_count} صف لكن فهارس قليلة',
                            'action': f'add_indexes_to_{table_name}'
                        })
        
        # توصيات إعدادات SQLite
        pragma_settings = analysis['database_info'].get('pragma_settings', {})
        if pragma_settings.get('journal_mode') != 'WAL':
            recommendations.append({
                'type': 'configuration',
                'priority': 'medium',
                'message': 'يُنصح بتفعيل WAL mode لتحسين الأداء',
                'action': 'enable_wal_mode'
            })
        
        if isinstance(pragma_settings.get('cache_size'), int) and pragma_settings.get('cache_size') < 5000:
            recommendations.append({
                'type': 'configuration',
                'priority': 'low',
                'message': 'يمكن زيادة حجم cache_size لتحسين الأداء',
                'action': 'increase_cache_size'
            })
        
        return recommendations
    
    def apply_optimizations(self, optimizations=None):
        """تطبيق التحسينات"""
        if optimizations is None:
            optimizations = ['vacuum', 'analyze', 'wal_mode', 'cache_optimization']
        
        results = {}
        
        try:
            with connection.cursor() as cursor:
                # VACUUM لإعادة تنظيم قاعدة البيانات
                if 'vacuum' in optimizations:
                    logger.info("Running VACUUM...")
                    cursor.execute("VACUUM")
                    results['vacuum'] = 'success'
                
                # ANALYZE لتحديث الإحصائيات
                if 'analyze' in optimizations:
                    logger.info("Running ANALYZE...")
                    cursor.execute("ANALYZE")
                    results['analyze'] = 'success'
                
                # تفعيل WAL mode
                if 'wal_mode' in optimizations:
                    logger.info("Enabling WAL mode...")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    results['wal_mode'] = 'success'
                
                # تحسين الكاش
                if 'cache_optimization' in optimizations:
                    logger.info("Optimizing cache settings...")
                    cursor.execute("PRAGMA cache_size=10000")  # 10MB
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    results['cache_optimization'] = 'success'
                
                # إعدادات أداء إضافية
                if 'performance_settings' in optimizations:
                    logger.info("Applying performance settings...")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                    results['performance_settings'] = 'success'
                
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
            results['error'] = str(e)
        
        return results
    
    def create_backup(self, backup_name=None):
        """إنشاء نسخة احتياطية"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # نسخ ملف قاعدة البيانات
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # ضغط النسخة الاحتياطية
            import gzip
            with open(backup_path, 'rb') as f_in:
                with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # حذف النسخة غير المضغوطة
            os.remove(backup_path)
            
            backup_info = {
                'name': f"{backup_name}.gz",
                'path': f"{backup_path}.gz",
                'size': os.path.getsize(f"{backup_path}.gz"),
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"Backup created: {backup_info['name']}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def clean_old_backups(self, keep_days=30):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.db.gz'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {filename}")
            
            return {'deleted_backups': deleted_count}
            
        except Exception as e:
            logger.error(f"Error cleaning old backups: {e}")
            return {'error': str(e)}


class DatabaseMonitor:
    """مراقب قاعدة البيانات"""
    
    def __init__(self):
        self.query_log = []
        self.slow_query_threshold = 1.0  # ثانية واحدة
    
    def log_query(self, query, execution_time, params=None):
        """تسجيل الاستعلام"""
        query_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query[:500],  # أول 500 حرف
            'execution_time': execution_time,
            'params': str(params)[:200] if params else None,
            'is_slow': execution_time > self.slow_query_threshold
        }
        
        self.query_log.append(query_entry)
        
        # الاحتفاظ بآخر 1000 استعلام
        if len(self.query_log) > 1000:
            self.query_log.pop(0)
        
        # تسجيل الاستعلامات البطيئة
        if execution_time > self.slow_query_threshold:
            logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
    
    def get_slow_queries(self, limit=20):
        """الحصول على الاستعلامات البطيئة"""
        slow_queries = [q for q in self.query_log if q['is_slow']]
        return sorted(slow_queries, key=lambda x: x['execution_time'], reverse=True)[:limit]
    
    def get_query_statistics(self):
        """إحصائيات الاستعلامات"""
        if not self.query_log:
            return {}
        
        total_queries = len(self.query_log)
        slow_queries = len([q for q in self.query_log if q['is_slow']])
        
        execution_times = [q['execution_time'] for q in self.query_log]
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        
        return {
            'total_queries': total_queries,
            'slow_queries': slow_queries,
            'slow_percentage': (slow_queries / total_queries) * 100,
            'average_execution_time': round(avg_time, 3),
            'max_execution_time': round(max_time, 3),
            'queries_per_minute': self._calculate_queries_per_minute()
        }
    
    def _calculate_queries_per_minute(self):
        """حساب عدد الاستعلامات في الدقيقة"""
        if len(self.query_log) < 2:
            return 0
        
        # حساب الفترة الزمنية
        start_time = datetime.fromisoformat(self.query_log[0]['timestamp'])
        end_time = datetime.fromisoformat(self.query_log[-1]['timestamp'])
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        if duration_minutes == 0:
            return 0
        
        return round(len(self.query_log) / duration_minutes, 2)


# إنشاء مثائل عامة
db_optimizer = DatabaseOptimizer()
db_monitor = DatabaseMonitor()


def run_database_maintenance():
    """تشغيل صيانة دورية لقاعدة البيانات"""
    logger.info("Starting database maintenance...")
    
    results = {
        'started_at': datetime.now().isoformat(),
        'backup_created': False,
        'optimizations_applied': False,
        'old_backups_cleaned': False
    }
    
    try:
        # إنشاء نسخة احتياطية
        backup_info = db_optimizer.create_backup()
        if backup_info:
            results['backup_created'] = True
            results['backup_info'] = backup_info
        
        # تطبيق التحسينات
        optimization_results = db_optimizer.apply_optimizations()
        if 'error' not in optimization_results:
            results['optimizations_applied'] = True
            results['optimization_results'] = optimization_results
        
        # تنظيف النسخ الاحتياطية القديمة
        cleanup_results = db_optimizer.clean_old_backups()
        if 'error' not in cleanup_results:
            results['old_backups_cleaned'] = True
            results['cleanup_results'] = cleanup_results
        
        results['completed_at'] = datetime.now().isoformat()
        results['success'] = True
        
        logger.info("Database maintenance completed successfully")
        
    except Exception as e:
        logger.error(f"Database maintenance failed: {e}")
        results['error'] = str(e)
        results['success'] = False
    
    return results