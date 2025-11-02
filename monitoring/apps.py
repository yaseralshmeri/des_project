"""
تكوين تطبيق المراقبة
Monitoring App Configuration

تم تطويره في: 2025-11-02
"""

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    """تكوين تطبيق المراقبة"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'
    verbose_name = 'نظام المراقبة'
    
    def ready(self):
        """تهيئة التطبيق عند التشغيل"""
        # استيراد الإشارات والمعالجات
        try:
            from . import performance_monitor
            from . import error_handler
            
            # بدء نظام المراقبة
            print("✅ تم تفعيل نظام المراقبة المتطور")
            
        except Exception as e:
            print(f"❌ فشل في تفعيل نظام المراقبة: {e}")