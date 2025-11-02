"""
نظام مراقبة الأداء المتقدم
Advanced System Performance Monitor
"""

import os
import sys
import time
import psutil
import json
from datetime import datetime, timedelta
from pathlib import Path

# إضافة مجلد المشروع لـ Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.db import connection
from django.core.cache import cache


class SystemMonitor:
    """مراقب الأداء المتقدم"""
    
    def __init__(self):
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'database': {},
            'application': {},
            'recommendations': []
        }
    
    def collect_system_metrics(self):
        """جمع مقاييس النظام"""
        print("📊 جمع مقاييس النظام...")
        
        # معلومات المعالج
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # معلومات الذاكرة
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # معلومات القرص
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)
        
        # معلومات الشبكة
        network = psutil.net_io_counters()
        
        self.metrics['system'] = {
            'cpu_usage_percent': cpu_percent,
            'cpu_cores': cpu_count,
            'memory_usage_percent': memory_percent,
            'memory_available_gb': round(memory_available_gb, 2),
            'disk_usage_percent': round(disk_percent, 2),
            'disk_free_gb': round(disk_free_gb, 2),
            'network_bytes_sent': network.bytes_sent,
            'network_bytes_recv': network.bytes_recv,
        }
        
        # إضافة تحذيرات
        if cpu_percent > 80:
            self.metrics['recommendations'].append("⚠️ استخدام المعالج عالي")
        if memory_percent > 85:
            self.metrics['recommendations'].append("⚠️ استخدام الذاكرة عالي")
        if disk_percent > 90:
            self.metrics['recommendations'].append("⚠️ مساحة القرص منخفضة")
    
    def collect_database_metrics(self):
        """جمع مقاييس قاعدة البيانات"""
        print("🗄️ جمع مقاييس قاعدة البيانات...")
        
        try:
            with connection.cursor() as cursor:
                # حجم قاعدة البيانات
                db_path = Path(connection.settings_dict['NAME'])
                db_size_mb = db_path.stat().st_size / (1024**2) if db_path.exists() else 0
                
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
                
                # اختبار سرعة قاعدة البيانات
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                db_response_time = time.time() - start_time
                
                self.metrics['database'] = {
                    'size_mb': round(db_size_mb, 2),
                    'table_count': table_count,
                    'index_count': index_count,
                    'user_count': user_count,
                    'response_time_ms': round(db_response_time * 1000, 2)
                }
                
                # إضافة توصيات
                if db_size_mb > 100:
                    self.metrics['recommendations'].append("💾 قاعدة البيانات كبيرة - تحتاج تنظيف")
                if db_response_time > 0.1:
                    self.metrics['recommendations'].append("🐌 قاعدة البيانات بطيئة - تحتاج فهرسة")
                    
        except Exception as e:
            self.metrics['database']['error'] = str(e)
    
    def collect_application_metrics(self):
        """جمع مقاييس التطبيق"""
        print("🖥️ جمع مقاييس التطبيق...")
        
        try:
            # عدد العمليات النشطة
            current_process = psutil.Process()
            process_count = len(current_process.children(recursive=True)) + 1
            
            # استخدام الذاكرة للعملية الحالية
            memory_info = current_process.memory_info()
            process_memory_mb = memory_info.rss / (1024**2)
            
            # عدد الملفات المفتوحة
            try:
                open_files = len(current_process.open_files())
            except:
                open_files = 0
            
            # اختبار Cache
            cache_start = time.time()
            cache.set('monitor_test', 'value', 60)
            cache.get('monitor_test')
            cache_response_time = time.time() - cache_start
            
            # عدد التطبيقات المثبتة
            from django.apps import apps
            installed_apps = len(apps.get_app_configs())
            
            self.metrics['application'] = {
                'process_count': process_count,
                'memory_usage_mb': round(process_memory_mb, 2),
                'open_files': open_files,
                'cache_response_time_ms': round(cache_response_time * 1000, 2),
                'installed_apps': installed_apps,
            }
            
            # إضافة توصيات
            if process_memory_mb > 500:
                self.metrics['recommendations'].append("🔋 استخدام ذاكرة التطبيق عالي")
            if cache_response_time > 0.01:
                self.metrics['recommendations'].append("⚡ Cache بطيء - يُنصح بـ Redis")
                
        except Exception as e:
            self.metrics['application']['error'] = str(e)
    
    def generate_performance_score(self):
        """حساب نقاط الأداء الإجمالي"""
        score = 100
        
        # خصم نقاط حسب الأداء
        system = self.metrics.get('system', {})
        if system.get('cpu_usage_percent', 0) > 80:
            score -= 20
        if system.get('memory_usage_percent', 0) > 85:
            score -= 20
        if system.get('disk_usage_percent', 0) > 90:
            score -= 15
        
        database = self.metrics.get('database', {})
        if database.get('response_time_ms', 0) > 100:
            score -= 15
        
        application = self.metrics.get('application', {})
        if application.get('cache_response_time_ms', 0) > 10:
            score -= 10
        
        return max(score, 0)
    
    def save_metrics(self):
        """حفظ المقاييس في ملف"""
        metrics_dir = Path('monitoring/logs')
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metrics_file = metrics_dir / f'metrics_{timestamp}.json'
        
        # إضافة نقاط الأداء
        self.metrics['performance_score'] = self.generate_performance_score()
        
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        return metrics_file
    
    def print_report(self):
        """طباعة تقرير الأداء"""
        print("\n" + "="*60)
        print("📈 تقرير مراقبة الأداء")
        print("="*60)
        
        # نقاط الأداء
        performance_score = self.generate_performance_score()
        print(f"🎯 نقاط الأداء الإجمالي: {performance_score}/100")
        
        # مقاييس النظام
        system = self.metrics.get('system', {})
        if system:
            print(f"\n💻 النظام:")
            print(f"   المعالج: {system.get('cpu_usage_percent', 0):.1f}%")
            print(f"   الذاكرة: {system.get('memory_usage_percent', 0):.1f}%")
            print(f"   القرص: {system.get('disk_usage_percent', 0):.1f}%")
        
        # مقاييس قاعدة البيانات
        database = self.metrics.get('database', {})
        if database:
            print(f"\n🗄️ قاعدة البيانات:")
            print(f"   الحجم: {database.get('size_mb', 0)} MB")
            print(f"   الجداول: {database.get('table_count', 0)}")
            print(f"   زمن الاستجابة: {database.get('response_time_ms', 0)} ms")
        
        # مقاييس التطبيق
        application = self.metrics.get('application', {})
        if application:
            print(f"\n🖥️ التطبيق:")
            print(f"   الذاكرة: {application.get('memory_usage_mb', 0)} MB")
            print(f"   التطبيقات: {application.get('installed_apps', 0)}")
            print(f"   Cache: {application.get('cache_response_time_ms', 0)} ms")
        
        # التوصيات
        recommendations = self.metrics.get('recommendations', [])
        if recommendations:
            print(f"\n💡 التوصيات:")
            for rec in recommendations:
                print(f"   {rec}")
        else:
            print(f"\n✅ الأداء ممتاز - لا توجد توصيات")
    
    def run_monitoring(self):
        """تشغيل المراقبة الكاملة"""
        print("🚀 بدء مراقبة الأداء...")
        
        start_time = time.time()
        
        # جمع جميع المقاييس
        self.collect_system_metrics()
        self.collect_database_metrics()
        self.collect_application_metrics()
        
        # حفظ وطباعة النتائج
        metrics_file = self.save_metrics()
        self.print_report()
        
        end_time = time.time()
        
        print(f"\n⏱️ وقت المراقبة: {end_time - start_time:.2f} ثانية")
        print(f"💾 تم حفظ المقاييس في: {metrics_file}")


def main():
    """الدالة الرئيسية"""
    monitor = SystemMonitor()
    monitor.run_monitoring()


if __name__ == "__main__":
    main()