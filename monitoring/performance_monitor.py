"""
نظام مراقبة الأداء المتطور
Advanced Performance Monitoring System

تم تطويره في: 2025-11-02
"""

import time
import logging
import psutil
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils import timezone


logger = logging.getLogger('performance')


class PerformanceMonitor:
    """نظام مراقبة الأداء الشامل"""
    
    def __init__(self):
        self.metrics = defaultdict(deque)
        self.alerts = []
        self.thresholds = {
            'response_time': 2.0,  # seconds
            'db_queries': 50,      # per request
            'memory_usage': 80,    # percentage
            'cpu_usage': 85,       # percentage
            'disk_usage': 90,      # percentage
        }
        self.start_monitoring()
    
    def start_monitoring(self):
        """بدء مراقبة النظام"""
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def _monitor_system(self):
        """مراقبة النظام المستمرة"""
        while True:
            try:
                # مراقبة استخدام الذاكرة
                memory = psutil.virtual_memory()
                self.record_metric('memory_usage', memory.percent)
                
                # مراقبة استخدام المعالج
                cpu = psutil.cpu_percent(interval=1)
                self.record_metric('cpu_usage', cpu)
                
                # مراقبة استخدام القرص
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.record_metric('disk_usage', disk_percent)
                
                # فحص التحذيرات
                self.check_alerts()
                
                time.sleep(10)  # كل 10 ثواني
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(30)
    
    def record_metric(self, metric_name, value):
        """تسجيل مقياس الأداء"""
        current_time = timezone.now()
        
        # الاحتفاظ بآخر 1000 قياس فقط
        if len(self.metrics[metric_name]) >= 1000:
            self.metrics[metric_name].popleft()
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': current_time
        })
        
        # حفظ في الكاش
        cache_key = f"performance_metric_{metric_name}"
        cache.set(cache_key, value, timeout=300)
    
    def check_alerts(self):
        """فحص التحذيرات"""
        for metric_name, threshold in self.thresholds.items():
            if metric_name in self.metrics and self.metrics[metric_name]:
                latest_value = self.metrics[metric_name][-1]['value']
                
                if latest_value > threshold:
                    alert = {
                        'metric': metric_name,
                        'value': latest_value,
                        'threshold': threshold,
                        'timestamp': timezone.now(),
                        'severity': 'high' if latest_value > threshold * 1.2 else 'medium'
                    }
                    
                    self.alerts.append(alert)
                    logger.warning(
                        f"Performance Alert: {metric_name} = {latest_value:.2f} "
                        f"(threshold: {threshold})"
                    )
                    
                    # الاحتفاظ بآخر 100 تحذير
                    if len(self.alerts) > 100:
                        self.alerts.pop(0)
    
    def get_metrics_summary(self, hours=1):
        """الحصول على ملخص المقاييس"""
        summary = {}
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        for metric_name, values in self.metrics.items():
            recent_values = [
                v['value'] for v in values 
                if v['timestamp'] >= cutoff_time
            ]
            
            if recent_values:
                summary[metric_name] = {
                    'avg': sum(recent_values) / len(recent_values),
                    'max': max(recent_values),
                    'min': min(recent_values),
                    'count': len(recent_values),
                    'current': recent_values[-1] if recent_values else 0
                }
        
        return summary
    
    def get_database_stats(self):
        """إحصائيات قاعدة البيانات"""
        with connection.cursor() as cursor:
            # عدد الاستعلامات
            queries_count = len(connection.queries)
            
            # حجم قاعدة البيانات (SQLite)
            if settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
                db_path = settings.DATABASES['default']['NAME']
                try:
                    import os
                    db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
                except:
                    db_size = 0
            else:
                db_size = 0
            
            return {
                'queries_count': queries_count,
                'db_size_mb': round(db_size, 2),
                'active_connections': 1  # SQLite يدعم اتصال واحد فقط
            }
    
    def get_health_status(self):
        """حالة النظام العامة"""
        summary = self.get_metrics_summary()
        alerts_count = len([a for a in self.alerts if 
                          a['timestamp'] >= timezone.now() - timedelta(minutes=30)])
        
        # تحديد حالة النظام
        if alerts_count == 0:
            status = 'healthy'
        elif alerts_count <= 5:
            status = 'warning'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'alerts_count': alerts_count,
            'uptime': self._get_uptime(),
            'last_check': timezone.now(),
            'metrics': summary
        }
    
    def _get_uptime(self):
        """وقت تشغيل النظام"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600
            return round(uptime_hours, 2)
        except:
            return 0
    
    def generate_report(self, hours=24):
        """إنشاء تقرير أداء شامل"""
        summary = self.get_metrics_summary(hours)
        db_stats = self.get_database_stats()
        health = self.get_health_status()
        
        recent_alerts = [
            a for a in self.alerts 
            if a['timestamp'] >= timezone.now() - timedelta(hours=hours)
        ]
        
        report = {
            'generated_at': timezone.now(),
            'period_hours': hours,
            'system_health': health,
            'performance_metrics': summary,
            'database_stats': db_stats,
            'alerts': recent_alerts,
            'recommendations': self._generate_recommendations(summary, recent_alerts)
        }
        
        return report
    
    def _generate_recommendations(self, summary, alerts):
        """إنشاء التوصيات"""
        recommendations = []
        
        # توصيات الذاكرة
        if 'memory_usage' in summary:
            if summary['memory_usage']['avg'] > 70:
                recommendations.append({
                    'type': 'memory',
                    'priority': 'high',
                    'message': 'استخدام الذاكرة مرتفع، يُنصح بتحسين الكاش أو زيادة الذاكرة'
                })
        
        # توصيات المعالج  
        if 'cpu_usage' in summary:
            if summary['cpu_usage']['avg'] > 75:
                recommendations.append({
                    'type': 'cpu',
                    'priority': 'medium',
                    'message': 'استخدام المعالج مرتفع، فحص العمليات المستهلكة للمعالج'
                })
        
        # توصيات قاعدة البيانات
        db_alerts = [a for a in alerts if a['metric'] == 'db_queries']
        if db_alerts:
            recommendations.append({
                'type': 'database',
                'priority': 'high', 
                'message': 'عدد استعلامات قاعدة البيانات مرتفع، يُنصح بتحسين الاستعلامات'
            })
        
        return recommendations


# إنشاء مثيل عام للمراقب
monitor = PerformanceMonitor()


class PerformanceMiddleware:
    """Middleware لمراقبة أداء الطلبات"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        start_time = time.time()
        
        # عدد الاستعلامات قبل الطلب
        queries_before = len(connection.queries)
        
        response = self.get_response(request)
        
        # حساب الأداء
        end_time = time.time()
        response_time = end_time - start_time
        queries_count = len(connection.queries) - queries_before
        
        # تسجيل المقاييس
        monitor.record_metric('response_time', response_time)
        monitor.record_metric('db_queries', queries_count)
        
        # إضافة headers للمطورين
        if settings.DEBUG:
            response['X-Response-Time'] = f"{response_time:.3f}s"
            response['X-DB-Queries'] = str(queries_count)
        
        # تحذير للاستجابات البطيئة
        if response_time > 2.0:
            logger.warning(
                f"Slow request: {request.path} took {response_time:.3f}s "
                f"with {queries_count} DB queries"
            )
        
        return response