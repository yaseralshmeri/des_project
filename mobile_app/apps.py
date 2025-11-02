# تكوين تطبيق الهاتف المحمول
# Mobile App Configuration

from django.apps import AppConfig


class MobileAppConfig(AppConfig):
    """تكوين تطبيق الهاتف المحمول"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_app'
    verbose_name = 'تطبيق الهاتف المحمول'
    verbose_name_plural = 'تطبيقات الهاتف المحمول'