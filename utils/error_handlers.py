# FIX: Error Handling - تحسين معالجة الأخطاء
"""
نظام شامل لمعالجة الأخطاء مع دعم اللغة العربية
"""

from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import logging
import traceback
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

class ErrorMessages:
    """رسائل الأخطاء باللغة العربية"""
    
    # أخطاء عامة
    GENERAL_ERROR = "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
    PERMISSION_DENIED = "ليس لديك صلاحية للوصول إلى هذا المحتوى."
    NOT_FOUND = "الصفحة أو المحتوى المطلوب غير موجود."
    BAD_REQUEST = "طلب غير صحيح. يرجى التحقق من البيانات المرسلة."
    
    # أخطاء المصادقة
    AUTHENTICATION_REQUIRED = "يجب تسجيل الدخول للوصول إلى هذا المحتوى."
    INVALID_CREDENTIALS = "بيانات تسجيل الدخول غير صحيحة."
    TOKEN_EXPIRED = "انتهت صلاحية رمز الدخول. يرجى تسجيل الدخول مرة أخرى."
    
    # أخطاء قاعدة البيانات
    DATABASE_ERROR = "خطأ في قاعدة البيانات. يرجى المحاولة لاحقاً."
    DUPLICATE_ENTRY = "البيانات مكررة. يرجى التحقق من المعلومات."
    CONSTRAINT_ERROR = "لا يمكن تنفيذ العملية بسبب قيود قاعدة البيانات."
    
    # أخطاء التحقق
    VALIDATION_ERROR = "خطأ في التحقق من البيانات."
    REQUIRED_FIELD = "هذا الحقل مطلوب."
    INVALID_FORMAT = "تنسيق البيانات غير صحيح."
    
    # أخطاء الملفات
    FILE_TOO_LARGE = "حجم الملف كبير جداً."
    INVALID_FILE_TYPE = "نوع الملف غير مدعوم."
    UPLOAD_ERROR = "خطأ في رفع الملف."

def custom_exception_handler(exc, context):
    """معالج الأخطاء المخصص للـ API"""
    
    # استدعاء معالج الأخطاء الافتراضي أولاً
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'error': True,
            'message': '',
            'details': {},
            'status_code': response.status_code
        }
        
        # تخصيص رسائل الأخطاء حسب نوع الخطأ
        if response.status_code == 400:
            custom_response_data['message'] = ErrorMessages.BAD_REQUEST
            custom_response_data['details'] = response.data
            
        elif response.status_code == 401:
            custom_response_data['message'] = ErrorMessages.AUTHENTICATION_REQUIRED
            
        elif response.status_code == 403:
            custom_response_data['message'] = ErrorMessages.PERMISSION_DENIED
            
        elif response.status_code == 404:
            custom_response_data['message'] = ErrorMessages.NOT_FOUND
            
        elif response.status_code == 500:
            custom_response_data['message'] = ErrorMessages.GENERAL_ERROR
            
        else:
            custom_response_data['message'] = ErrorMessages.GENERAL_ERROR
            custom_response_data['details'] = response.data
        
        # تسجيل الخطأ
        logger.error(f"API Error: {exc}", exc_info=True)
        
        response.data = custom_response_data
    
    return response

def handle_404(request, exception=None):
    """معالج خطأ 404 للصفحات"""
    context = {
        'error_title': 'الصفحة غير موجودة',
        'error_message': ErrorMessages.NOT_FOUND,
        'error_code': '404',
        'back_url': request.META.get('HTTP_REFERER', '/')
    }
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'success': False,
            'error': True,
            'message': ErrorMessages.NOT_FOUND,
            'status_code': 404
        }, status=404)
    
    return render(request, 'errors/404.html', context, status=404)

def handle_500(request):
    """معالج خطأ 500 للصفحات"""
    context = {
        'error_title': 'خطأ في الخادم',
        'error_message': ErrorMessages.GENERAL_ERROR,
        'error_code': '500',
        'back_url': request.META.get('HTTP_REFERER', '/')
    }
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'success': False,
            'error': True,
            'message': ErrorMessages.GENERAL_ERROR,
            'status_code': 500
        }, status=500)
    
    return render(request, 'errors/500.html', context, status=500)

def handle_403(request, exception=None):
    """معالج خطأ 403 للصفحات"""
    context = {
        'error_title': 'الوصول مرفوض',
        'error_message': ErrorMessages.PERMISSION_DENIED,
        'error_code': '403',
        'back_url': request.META.get('HTTP_REFERER', '/')
    }
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'success': False,
            'error': True,
            'message': ErrorMessages.PERMISSION_DENIED,
            'status_code': 403
        }, status=403)
    
    return render(request, 'errors/403.html', context, status=403)

class ErrorHandlerMixin:
    """Mixin لمعالجة الأخطاء في الـ Views"""
    
    def handle_exception(self, exc):
        """معالجة الأخطاء في الـ Views"""
        logger.error(f"View Error: {exc}", exc_info=True)
        
        if hasattr(self, 'request') and self.request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'error': True,
                'message': ErrorMessages.GENERAL_ERROR,
                'status_code': 500
            }, status=500)
        
        return HttpResponseServerError(
            render(self.request, 'errors/500.html', {
                'error_title': 'خطأ في النظام',
                'error_message': ErrorMessages.GENERAL_ERROR,
                'error_code': '500'
            })
        )

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch لمعالجة الأخطاء"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as exc:
            return self.handle_exception(exc)

def log_error(error_type, message, exc=None, extra_data=None):
    """تسجيل الأخطاء مع معلومات إضافية"""
    log_data = {
        'error_type': error_type,
        'message': message,
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    if exc:
        logger.error(f"{error_type}: {message}", exc_info=exc, extra=log_data)
    else:
        logger.error(f"{error_type}: {message}", extra=log_data)

def create_error_response(message, status_code=400, details=None):
    """إنشاء استجابة خطأ موحدة"""
    response_data = {
        'success': False,
        'error': True,
        'message': message,
        'status_code': status_code
    }
    
    if details:
        response_data['details'] = details
    
    return Response(response_data, status=status_code)

# Decorators لمعالجة الأخطاء
def handle_api_errors(view_func):
    """Decorator لمعالجة أخطاء الـ API"""
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except Exception as exc:
            logger.error(f"API Error in {view_func.__name__}: {exc}", exc_info=True)
            return create_error_response(ErrorMessages.GENERAL_ERROR, 500)
    
    return wrapper

def handle_view_errors(view_func):
    """Decorator لمعالجة أخطاء الـ Views"""
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as exc:
            logger.error(f"View Error in {view_func.__name__}: {exc}", exc_info=True)
            
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'success': False,
                    'error': True,
                    'message': ErrorMessages.GENERAL_ERROR,
                    'status_code': 500
                }, status=500)
            
            return render(request, 'errors/500.html', {
                'error_title': 'خطأ في النظام',
                'error_message': ErrorMessages.GENERAL_ERROR,
                'error_code': '500'
            }, status=500)
    
    return wrapper