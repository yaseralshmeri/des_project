#!/usr/bin/env python3
"""
محسن قاعدة البيانات المتقدم
Advanced Database Optimizer
"""

import os
import sys
import time
import django
from pathlib import Path
from datetime import datetime

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection, transaction
from django.core.management import call_command
from django.apps import apps


class DatabaseOptimizer:
    """محسن قاعدة البيانات المتطور"""
    
    def __init__(self):
        self.optimizations_applied = []
        self.performance_gains = {}
    
    def analyze_tables(self):
        """تحليل الجداول وتحديد المشاكل"""
        print("🔍 تحليل الجداول...")
        
        with connection.cursor() as cursor:
            # الحصول على جميع الجداول
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            table_analysis = {}
            
            for table in tables:
                # تحليل كل جدول
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                row_count = cursor.fetchone()[0]
                
                # فحص الفهارس
                cursor.execute(f"PRAGMA index_list('{table}')")
                indexes = cursor.fetchall()
                index_count = len(indexes)
                
                # حساب حجم الجدول
                cursor.execute(f"PRAGMA table_info('{table}')")
                columns = cursor.fetchall()
                column_count = len(columns)
                
                table_analysis[table] = {
                    'rows': row_count,
                    'indexes': index_count,
                    'columns': column_count
                }
                
                # التوصيات
                if row_count > 1000 and index_count < 2:
                    self.optimizations_applied.append(
                        f"⚠️ الجدول {table} ({row_count:,} سطر) يحتاج المزيد من الفهارس"
                    )
                
                if row_count > 10000 and index_count < 3:
                    self.optimizations_applied.append(
                        f"🔥 الجدول {table} ({row_count:,} سطر) يحتاج فهرسة متقدمة"
                    )
            
            print(f"✅ تم تحليل {len(tables)} جدول")
            return table_analysis
    
    def create_missing_indexes(self):
        """إنشاء الفهارس المفقودة"""
        print("📊 إنشاء الفهارس المفقودة...")
        
        # فهارس مقترحة للأداء
        suggested_indexes = [
            # فهارس للبحث والترتيب
            "CREATE INDEX IF NOT EXISTS idx_user_email ON students_user(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_username ON students_user(username)",
            "CREATE INDEX IF NOT EXISTS idx_user_date_joined ON students_user(date_joined)",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON students_user(role)",
            
            # فهارس للجداول الكبيرة
            "CREATE INDEX IF NOT EXISTS idx_attendance_session_date ON attendance_qr_attendancesession(scheduled_start_time)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_record_date ON attendance_qr_attendancerecord(recorded_at)",
            "CREATE INDEX IF NOT EXISTS idx_security_event_date ON cyber_security_securityevent(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_security_event_severity ON cyber_security_securityevent(severity)",
            
            # فهارس للعلاقات الخارجية
            "CREATE INDEX IF NOT EXISTS idx_attendance_record_student ON attendance_qr_attendancerecord(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_record_session ON attendance_qr_attendancerecord(attendance_session_id)",
            "CREATE INDEX IF NOT EXISTS idx_security_event_user ON cyber_security_securityevent(affected_user_id)",
        ]
        
        created_count = 0
        with connection.cursor() as cursor:
            for index_sql in suggested_indexes:
                try:
                    cursor.execute(index_sql)
                    created_count += 1
                    index_name = index_sql.split()[4]  # استخراج اسم الفهرس
                    self.optimizations_applied.append(f"✅ تم إنشاء الفهرس: {index_name}")
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"⚠️ خطأ في إنشاء الفهرس: {e}")
        
        print(f"✅ تم إنشاء {created_count} فهرس جديد")
        return created_count
    
    def optimize_queries(self):
        """تحسين الاستعلامات الشائعة"""
        print("⚡ تحسين الاستعلامات...")
        
        # تحليل الاستعلامات البطيئة المحتملة
        slow_queries = []
        
        with connection.cursor() as cursor:
            # فحص الجداول الكبيرة
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                row_count = cursor.fetchone()[0]
                
                if row_count > 1000:
                    # اختبار سرعة استعلام بسيط
                    start_time = time.time()
                    cursor.execute(f"SELECT * FROM `{table}` LIMIT 10")
                    cursor.fetchall()
                    query_time = time.time() - start_time
                    
                    if query_time > 0.01:  # أكثر من 10ms
                        slow_queries.append({
                            'table': table,
                            'rows': row_count,
                            'time_ms': round(query_time * 1000, 2)
                        })
        
        if slow_queries:
            self.optimizations_applied.append("🐌 استعلامات بطيئة تم اكتشافها:")
            for query in slow_queries[:5]:  # أول 5 استعلامات
                self.optimizations_applied.append(
                    f"   {query['table']}: {query['rows']:,} سطر - {query['time_ms']}ms"
                )
        
        return len(slow_queries)
    
    def vacuum_and_analyze(self):
        """تنظيف وتحليل قاعدة البيانات"""
        print("🧹 تنظيف قاعدة البيانات...")
        
        with connection.cursor() as cursor:
            # حفظ حجم قاعدة البيانات قبل التنظيف
            db_path = Path(connection.settings_dict['NAME'])
            size_before = db_path.stat().st_size if db_path.exists() else 0
            
            # تنظيف قاعدة البيانات
            start_time = time.time()
            cursor.execute("VACUUM")
            vacuum_time = time.time() - start_time
            
            # تحليل الجداول
            start_time = time.time()
            cursor.execute("ANALYZE")
            analyze_time = time.time() - start_time
            
            # حساب المساحة المحررة
            size_after = db_path.stat().st_size if db_path.exists() else 0
            space_saved = size_before - size_after
            
            self.optimizations_applied.extend([
                f"🧹 VACUUM: {vacuum_time:.2f} ثانية",
                f"📊 ANALYZE: {analyze_time:.2f} ثانية",
                f"💾 مساحة محررة: {space_saved / 1024:.1f} KB"
            ])
            
            self.performance_gains['vacuum_time'] = vacuum_time
            self.performance_gains['space_saved_kb'] = space_saved / 1024
    
    def update_table_statistics(self):
        """تحديث إحصائيات الجداول"""
        print("📈 تحديث الإحصائيات...")
        
        with connection.cursor() as cursor:
            # تحديث إحصائيات SQLite
            cursor.execute("PRAGMA optimize")
            self.optimizations_applied.append("✅ تم تحديث إحصائيات الجداول")
    
    def check_foreign_keys(self):
        """فحص المفاتيح الخارجية"""
        print("🔗 فحص المفاتيح الخارجية...")
        
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_key_check")
            fk_errors = cursor.fetchall()
            
            if fk_errors:
                self.optimizations_applied.append(f"⚠️ {len(fk_errors)} خطأ في المفاتيح الخارجية")
                for error in fk_errors[:5]:  # أول 5 أخطاء
                    self.optimizations_applied.append(f"   خطأ: {error}")
            else:
                self.optimizations_applied.append("✅ جميع المفاتيح الخارجية سليمة")
    
    def optimize_django_settings(self):
        """تحسين إعدادات Django"""
        print("⚙️ فحص إعدادات Django...")
        
        from django.conf import settings
        
        # فحص إعدادات قاعدة البيانات
        db_config = settings.DATABASES['default']
        
        optimizations = []
        
        # فحص conn_max_age
        if 'conn_max_age' not in db_config or db_config.get('conn_max_age', 0) == 0:
            optimizations.append("💡 يُنصح بتفعيل connection pooling (conn_max_age)")
        
        # فحص DEBUG
        if settings.DEBUG:
            optimizations.append("⚠️ DEBUG=True يؤثر على الأداء في الإنتاج")
        
        # فحص CACHE
        cache_config = getattr(settings, 'CACHES', {}).get('default', {})
        if cache_config.get('BACKEND') == 'django.core.cache.backends.locmem.LocMemCache':
            optimizations.append("💡 يُنصح بـ Redis بدلاً من LocMemCache")
        
        self.optimizations_applied.extend(optimizations)
        return len(optimizations)
    
    def generate_optimization_report(self):
        """إنشاء تقرير التحسين"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_applied': self.optimizations_applied,
            'performance_gains': self.performance_gains,
            'recommendations': [
                "💡 استخدم Redis للـ Cache في الإنتاج",
                "💡 فعّل connection pooling",
                "💡 راقب استعلامات Django الطويلة",
                "💡 استخدم select_related() و prefetch_related()",
                "💡 أضف فهارس للحقول المستخدمة في WHERE و ORDER BY"
            ]
        }
        
        # حفظ التقرير
        report_dir = Path('database_reports')
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'optimization_report_{timestamp}.json'
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_file, report
    
    def run_full_optimization(self):
        """تشغيل التحسين الشامل"""
        print("🚀 بدء تحسين قاعدة البيانات الشامل...")
        print("=" * 60)
        
        start_time = time.time()
        
        # تشغيل جميع التحسينات
        table_analysis = self.analyze_tables()
        indexes_created = self.create_missing_indexes()
        slow_queries = self.optimize_queries()
        self.vacuum_and_analyze()
        self.update_table_statistics()
        self.check_foreign_keys()
        django_optimizations = self.optimize_django_settings()
        
        # إنشاء التقرير
        report_file, report = self.generate_optimization_report()
        
        end_time = time.time()
        
        # طباعة النتائج
        print("\n📋 تقرير تحسين قاعدة البيانات:")
        print("=" * 60)
        
        print(f"⏱️ وقت التحسين: {end_time - start_time:.2f} ثانية")
        print(f"📊 فهارس جديدة: {indexes_created}")
        print(f"🐌 استعلامات بطيئة: {slow_queries}")
        print(f"⚙️ توصيات Django: {django_optimizations}")
        
        if self.performance_gains:
            print(f"💾 مساحة محررة: {self.performance_gains.get('space_saved_kb', 0):.1f} KB")
        
        print(f"\n📁 تم حفظ التقرير: {report_file}")
        
        print("\n🔧 التحسينات المطبقة:")
        for opt in self.optimizations_applied:
            print(f"   {opt}")
        
        print("\n✅ اكتمل تحسين قاعدة البيانات!")


def main():
    """الدالة الرئيسية"""
    optimizer = DatabaseOptimizer()
    optimizer.run_full_optimization()


if __name__ == "__main__":
    main()