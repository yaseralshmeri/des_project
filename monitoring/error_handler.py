"""
نظام إدارة الأخطاء المتطور
Advanced Error Handling System

تم تطويره في: 2025-11-02
"""

import sys
import traceback
import logging
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.core.cache import cache


logger = logging.getLogger('university')
security_logger = logging.getLogger('security')


class ErrorTracker:
    """تتبع الأخطاء والإحصائيات"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_details = []
        
    def track_error(self, error_type, error_message, request=None, extra_data=None):
        """تتبع خطأ جديد"""
        error_key = f"{error_type}_{hash(error_message)}"
        current_time = timezone.now()
        
        # إحصائيات الأخطاء
        if error_key not in self.error_counts:
            self.error_counts[error_key] = {
                'count': 0,
                'first_seen': current_time,
                'last_seen': current_time,
                'error_type': error_type,
                'message': error_message
            }
        
        self.error_counts[error_key]['count'] += 1
        self.error_counts[error_key]['last_seen'] = current_time
        
        # تفاصيل الخطأ
        error_detail = {
            'timestamp': current_time,
            'type': error_type,
            'message': error_message,
            'traceback': traceback.format_exc(),
            'request_data': self._extract_request_data(request) if request else None,
            'extra_data': extra_data or {}
        }
        
        self.error_details.append(error_detail)
        
        # الاحتفاظ بآخر 1000 خطأ فقط
        if len(self.error_details) > 1000:
            self.error_details.pop(0)
        
        # تسجيل في اللوج
        logger.error(
            f"Error tracked: {error_type} - {error_message}",
            extra={'request': request, 'extra_data': extra_data}
        )
        
        # إشعار للأخطاء الحرجة
        if error_type in ['DatabaseError', 'SecurityError', 'SystemError']:
            self._send_critical_error_alert(error_detail)
    
    def _extract_request_data(self, request):
        """استخراج بيانات الطلب المهمة"""
        try:
            return {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                'ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
            }
        except:
            return {}
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _send_critical_error_alert(self, error_detail):
        """إرسال تنبيه للأخطاء الحرجة"""
        if not settings.DEBUG and hasattr(settings, 'ADMINS'):
            try:
                subject = f"خطأ حرج في النظام - {error_detail['type']}"
                message = f"""
                وقع خطأ حرج في النظام:
                
                النوع: {error_detail['type']}
                الرسالة: {error_detail['message']}
                الوقت: {error_detail['timestamp']}
                
                تفاصيل الطلب:
                {json.dumps(error_detail.get('request_data', {}), indent=2, ensure_ascii=False)}
                
                التفاصيل التقنية:
                {error_detail['traceback']}
                """
                
                admin_emails = [admin[1] for admin in settings.ADMINS]
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
                
            except Exception as e:
                logger.error(f"Failed to send error alert: {e}")
    
    def get_error_statistics(self, hours=24):
        """إحصائيات الأخطاء"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # أخطاء الفترة المحددة
        recent_errors = [
            error for error in self.error_details 
            if error['timestamp'] >= cutoff_time
        ]
        
        # إحصائيات حسب النوع
        error_types = {}
        for error in recent_errors:
            error_type = error['type']
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        # أكثر الأخطاء تكراراً
        frequent_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return {
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'frequent_errors': frequent_errors,
            'recent_errors': recent_errors[-20:],  # آخر 20 خطأ
            'period_hours': hours
        }


# مثيل عام لتتبع الأخطاء
error_tracker = ErrorTracker()


class GlobalExceptionMiddleware:
    """Middleware لمعالجة الأخطاء العامة"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.handle_exception(request, e)
    
    def handle_exception(self, request, exception):
        """معالجة الأخطاء"""
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # تتبع الخطأ
        error_tracker.track_error(
            error_type=error_type,
            error_message=error_message,
            request=request,
            extra_data={'exception_args': exception.args}
        )
        
        # معالجة حسب نوع الطلب
        if request.META.get('CONTENT_TYPE') == 'application/json' or request.path.startswith('/api/'):
            return self._handle_api_error(request, exception)
        else:
            return self._handle_web_error(request, exception)
    
    def _handle_api_error(self, request, exception):
        """معالجة أخطاء API"""
        error_data = {
            'error': True,
            'message': 'حدث خطأ في النظام',
            'type': type(exception).__name__,
            'timestamp': timezone.now().isoformat()
        }
        
        if settings.DEBUG:
            error_data['debug'] = {
                'message': str(exception),
                'traceback': traceback.format_exc().split('\n')
            }
        
        status_code = getattr(exception, 'status_code', 500)
        return JsonResponse(error_data, status=status_code)
    
    def _handle_web_error(self, request, exception):
        """معالجة أخطاء الويب"""
        if settings.DEBUG:
            # في وضع التطوير، اعرض الخطأ التفصيلي
            return None  # دع Django يتعامل معه
        
        # في وضع الإنتاج، اعرض صفحة خطأ مخصصة
        try:
            context = {
                'error_type': type(exception).__name__,
                'error_id': f"ERR_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(exception)) % 10000}",
                'timestamp': timezone.now(),
            }
            
            status_code = getattr(exception, 'status_code', 500)
            
            return TemplateResponse(
                request,
                'errors/500.html',
                context,
                status=status_code
            )
            
        except Exception:
            # إذا فشل عرض صفحة الخطأ المخصصة
            return HttpResponse(
                'حدث خطأ في النظام. يرجى المحاولة لاحقاً.',
                status=500,
                content_type='text/plain; charset=utf-8'
            )


class SecurityErrorHandler:
    """معالج الأخطاء الأمنية"""
    
    @staticmethod
    def handle_security_violation(request, violation_type, details):
        """معالجة انتهاك أمني"""
        security_logger.warning(
            f"Security violation: {violation_type}",
            extra={
                'request': request,
                'violation_type': violation_type,
                'details': details,
                'ip': error_tracker._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
        
        # تتبع الانتهاك
        error_tracker.track_error(
            error_type='SecurityViolation',
            error_message=f"{violation_type}: {details}",
            request=request
        )
        
        # إجراءات الحماية
        client_ip = error_tracker._get_client_ip(request)
        cache_key = f"security_violations_{client_ip}"
        violations = cache.get(cache_key, 0)
        violations += 1
        cache.set(cache_key, violations, timeout=3600)  # ساعة واحدة
        
        # حظر مؤقت بعد عدة انتهاكات
        if violations >= 5:
            cache.set(f"blocked_ip_{client_ip}", True, timeout=1800)  # 30 دقيقة
            security_logger.error(f"IP {client_ip} temporarily blocked due to security violations")
        
        return JsonResponse({
            'error': True,
            'message': 'تم رصد نشاط مشبوه',
            'code': 'SECURITY_VIOLATION'
        }, status=403)


def custom_404_handler(request, exception):
    """معالج صفحة 404 المخصص"""
    error_tracker.track_error(
        error_type='NotFound',
        error_message=f"Page not found: {request.path}",
        request=request
    )
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': True,
            'message': 'المسار المطلوب غير موجود',
            'code': 'NOT_FOUND'
        }, status=404)
    
    context = {
        'requested_path': request.path,
        'timestamp': timezone.now()
    }
    
    return TemplateResponse(request, 'errors/404.html', context, status=404)


def custom_403_handler(request, exception):
    """معالج صفحة 403 المخصص"""
    error_tracker.track_error(
        error_type='PermissionDenied',
        error_message=f"Access denied: {request.path}",
        request=request
    )
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': True,
            'message': 'ليس لديك صلاحية للوصول لهذا المورد',
            'code': 'PERMISSION_DENIED'
        }, status=403)
    
    return TemplateResponse(request, 'errors/403.html', {}, status=403)


def custom_500_handler(request):
    """معالج صفحة 500 المخصص"""
    return TemplateResponse(request, 'errors/500.html', {}, status=500)