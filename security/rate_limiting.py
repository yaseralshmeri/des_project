
"""
نظام تحديد معدل الطلبات المتطور
Advanced Rate Limiting System
"""

from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from functools import wraps
import time

def rate_limit(max_requests=60, window=60, key_func=None):
    """
    Decorator لتحديد معدل الطلبات
    
    Args:
        max_requests: عدد الطلبات المسموحة
        window: النافزة الزمنية بالثواني
        key_func: دالة لتوليد مفتاح فريد
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # توليد مفتاح فريد للمستخدم
            if key_func:
                cache_key = key_func(request)
            else:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
                cache_key = f"rate_limit:{ip}:{func.__name__}"
            
            # الحصول على عدد الطلبات الحالي
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= max_requests:
                return HttpResponseTooManyRequests(
                    "تم تجاوز الحد المسموح من الطلبات. حاول مرة أخرى لاحقاً."
                )
            
            # زيادة عداد الطلبات
            cache.set(cache_key, current_requests + 1, window)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator

class RateLimitMiddleware:
    """Middleware لتحديد معدل الطلبات العام"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # فحص الـ IP للطلبات المشبوهة
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        cache_key = f"global_rate_limit:{ip}"
        
        # حد أقصى 1000 طلب في الساعة لكل IP
        current_requests = cache.get(cache_key, 0)
        
        if current_requests > 1000:
            return HttpResponseTooManyRequests(
                "تم تجاوز الحد المسموح من الطلبات لهذا العنوان."
            )
        
        # تسجيل الطلب
        cache.set(cache_key, current_requests + 1, 3600)  # ساعة واحدة
        
        response = self.get_response(request)
        return response
