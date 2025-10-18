# FIX: Performance Optimization - تحسين الأداء
"""
أدوات تحسين الأداء مع دعم اللغة العربية
"""

from django.core.cache import cache
from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.contrib.auth.decorators import login_required
from functools import wraps
import time
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """فئة لتحسين الأداء"""
    
    @staticmethod
    def cache_queryset(queryset, cache_key: str, timeout: int = 3600):
        """تخزين نتائج الاستعلام في الكاش"""
        try:
            # محاولة الحصول على البيانات من الكاش
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"تم استرداد البيانات من الكاش: {cache_key}")
                return cached_data
            
            # تقييم الاستعلام وتخزينه في الكاش
            data = list(queryset)
            cache.set(cache_key, data, timeout)
            logger.info(f"تم تخزين البيانات في الكاش: {cache_key}")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في تخزين البيانات في الكاش: {e}")
            return list(queryset)
    
    @staticmethod
    def optimize_queryset(queryset):
        """تحسين الاستعلام باستخدام select_related و prefetch_related"""
        model = queryset.model
        
        # تحديد العلاقات الأجنبية
        foreign_keys = []
        many_to_many = []
        
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                foreign_keys.append(field.name)
            elif isinstance(field, (models.ManyToManyField, models.OneToManyField)):
                many_to_many.append(field.name)
        
        # تطبيق select_related للعلاقات الأجنبية
        if foreign_keys:
            queryset = queryset.select_related(*foreign_keys[:5])  # أول 5 علاقات فقط
        
        # تطبيق prefetch_related للعلاقات متعددة
        if many_to_many:
            queryset = queryset.prefetch_related(*many_to_many[:3])  # أول 3 علاقات فقط
        
        return queryset
    
    @staticmethod
    def get_cache_key(prefix: str, **kwargs) -> str:
        """إنشاء مفتاح كاش فريد"""
        key_parts = [prefix]
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}_{value}")
        return "_".join(key_parts)
    
    @staticmethod
    def invalidate_cache(pattern: str):
        """إلغاء الكاش بناءً على نمط معين"""
        try:
            from django.core.cache.utils import make_template_fragment_key
            cache.delete_many(cache.keys(f"*{pattern}*"))
            logger.info(f"تم إلغاء الكاش للنمط: {pattern}")
        except Exception as e:
            logger.error(f"خطأ في إلغاء الكاش: {e}")

def performance_cache(timeout: int = 3600, key_prefix: str = ""):
    """ديكوريتر لتخزين نتائج الدوال في الكاش"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح كاش
            cache_key = f"{key_prefix}_{func.__name__}_"
            cache_key += "_".join([str(arg) for arg in args[:3]])  # أول 3 معاملات فقط
            cache_key += "_".join([f"{k}_{v}" for k, v in sorted(kwargs.items())])
            
            # محاولة الحصول على النتيجة من الكاش
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"تم استرداد نتيجة الدالة من الكاش: {func.__name__}")
                return result
            
            # تنفيذ الدالة وتخزين النتيجة
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # تخزين النتيجة في الكاش
            cache.set(cache_key, result, timeout)
            logger.info(f"تم تنفيذ الدالة {func.__name__} في {execution_time:.2f} ثانية وتخزينها في الكاش")
            
            return result
        return wrapper
    return decorator

def measure_performance(func: Callable) -> Callable:
    """قياس أداء الدالة"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:  # تحذير إذا كان الوقت أكثر من ثانية
            logger.warning(f"الدالة {func.__name__} استغرقت {execution_time:.2f} ثانية - قد تحتاج تحسين")
        else:
            logger.debug(f"الدالة {func.__name__} تم تنفيذها في {execution_time:.2f} ثانية")
        
        return result
    return wrapper

class CacheManager:
    """مدير الكاش المتقدم"""
    
    def __init__(self, default_timeout: int = 3600):
        self.default_timeout = default_timeout
    
    def get_or_set(self, key: str, callable_func: Callable, timeout: Optional[int] = None) -> Any:
        """الحصول على قيمة من الكاش أو تعيينها"""
        timeout = timeout or self.default_timeout
        
        try:
            result = cache.get(key)
            if result is not None:
                return result
            
            result = callable_func()
            cache.set(key, result, timeout)
            return result
            
        except Exception as e:
            logger.error(f"خطأ في إدارة الكاش: {e}")
            return callable_func()
    
    def invalidate_pattern(self, pattern: str):
        """إلغاء الكاش بناءً على نمط"""
        try:
            keys = cache.keys(f"*{pattern}*")
            if keys:
                cache.delete_many(keys)
                logger.info(f"تم إلغاء {len(keys)} مفتاح كاش للنمط: {pattern}")
        except Exception as e:
            logger.error(f"خطأ في إلغاء الكاش: {e}")
    
    def get_stats(self) -> dict:
        """إحصائيات الكاش"""
        try:
            from django.core.cache import caches
            default_cache = caches['default']
            
            if hasattr(default_cache, 'get_stats'):
                return default_cache.get_stats()
            else:
                return {"message": "إحصائيات الكاش غير متوفرة"}
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الكاش: {e}")
            return {"error": str(e)}

class QueryOptimizer:
    """محسن الاستعلامات"""
    
    @staticmethod
    def optimize_list_queries(queryset, relations: list = None):
        """تحسين استعلامات القوائم"""
        if relations:
            # فصل العلاقات الأجنبية عن العلاقات المتعددة
            foreign_keys = []
            many_relations = []
            
            for relation in relations:
                try:
                    field = queryset.model._meta.get_field(relation)
                    if isinstance(field, models.ForeignKey):
                        foreign_keys.append(relation)
                    else:
                        many_relations.append(relation)
                except:
                    continue
            
            if foreign_keys:
                queryset = queryset.select_related(*foreign_keys)
            if many_relations:
                queryset = queryset.prefetch_related(*many_relations)
        
        return queryset
    
    @staticmethod
    def add_pagination_optimization(queryset, page_size: int = 20):
        """تحسين التصفح"""
        # إضافة فهرسة للترتيب
        if hasattr(queryset.model._meta, 'ordering'):
            queryset = queryset.order_by(*queryset.model._meta.ordering)
        
        # تحديد الحقول المطلوبة فقط
        essential_fields = ['id', 'created_at', 'updated_at']
        model_fields = [f.name for f in queryset.model._meta.fields]
        
        # إضافة حقول إضافية حسب النموذج
        if 'name' in model_fields:
            essential_fields.append('name')
        if 'title' in model_fields:
            essential_fields.append('title')
        if 'status' in model_fields:
            essential_fields.append('status')
        
        return queryset.only(*essential_fields)

# ديكوريتر للتحسين التلقائي للصفحات
def optimize_page_cache(timeout: int = 300):
    """تحسين كاش الصفحات مع دعم المصادقة"""
    def decorator(view_func):
        @login_required
        @vary_on_headers('User-Agent', 'Accept-Language')
        @cache_page(timeout)
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# فئة لمراقبة الأداء
class PerformanceMonitor:
    """مراقب الأداء"""
    
    def __init__(self):
        self.metrics = {}
    
    def track_query_time(self, query_name: str, execution_time: float):
        """تتبع وقت تنفيذ الاستعلام"""
        if query_name not in self.metrics:
            self.metrics[query_name] = []
        
        self.metrics[query_name].append(execution_time)
        
        # تحذير إذا كان الاستعلام بطيئاً
        if execution_time > 2.0:
            logger.warning(f"الاستعلام {query_name} استغرق {execution_time:.2f} ثانية")
    
    def get_slow_queries(self, threshold: float = 1.0) -> dict:
        """الحصول على الاستعلامات البطيئة"""
        slow_queries = {}
        
        for query_name, times in self.metrics.items():
            avg_time = sum(times) / len(times)
            if avg_time > threshold:
                slow_queries[query_name] = {
                    'average_time': avg_time,
                    'total_executions': len(times),
                    'max_time': max(times),
                    'min_time': min(times)
                }
        
        return slow_queries
    
    def reset_metrics(self):
        """إعادة تعيين المقاييس"""
        self.metrics = {}
        logger.info("تم إعادة تعيين مقاييس الأداء")

# إنشاء مثيل عام لمراقب الأداء
performance_monitor = PerformanceMonitor()

# إعدادات التحسين الافتراضية
DEFAULT_CACHE_TIMEOUT = 3600  # ساعة واحدة
SLOW_QUERY_THRESHOLD = 1.0    # ثانية واحدة
MAX_CACHE_KEYS = 10000        # أقصى عدد مفاتيح كاش