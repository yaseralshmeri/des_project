"""
نظام API المتطور والموحد
Enhanced and Unified API System

تم تطويره في: 2025-11-02
يوفر APIs متطورة مع مصادقة آمنة ومراقبة الأداء
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from django.utils import timezone
import json
import logging

# استيراد الأنظمة المطورة
from .security_system_enhanced import (
    security_manager, login_tracker, two_factor_auth, 
    security_audit, log_login_attempt, check_security_violations
)
from .monitoring.performance_monitor import monitor
from .monitoring.error_handler import error_tracker

logger = logging.getLogger('university')


class CustomPagination(PageNumberPagination):
    """نظام تقسيم صفحات مخصص"""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'total_count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class APIRateThrottle(UserRateThrottle):
    """تحديد معدل طلبات API"""
    scope = 'api'
    rate = '1000/hour'


class PublicAPIRateThrottle(AnonRateThrottle):
    """تحديد معدل طلبات API العامة"""
    scope = 'public_api'
    rate = '100/hour'


class SecurityMiddleware:
    """Middleware أمني للـ APIs"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # فحص الانتهاكات الأمنية
        if request.path.startswith('/api/'):
            violations = check_security_violations(request)
            
            if violations:
                security_audit.log_security_event(
                    event_type='api_security_violation',
                    user=getattr(request, 'user', None),
                    details=f"Violations: {', '.join(violations)}",
                    ip_address=self._get_client_ip(request),
                    severity='medium'
                )
                
                # حظر مؤقت للانتهاكات الخطيرة
                if 'rate_limit_exceeded' in violations:
                    return Response({
                        'error': 'تم تجاوز الحد المسموح من الطلبات',
                        'code': 'RATE_LIMIT_EXCEEDED'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuthenticationViewSet(viewsets.GenericViewSet):
    """APIs المصادقة المتطورة"""
    
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """تسجيل الدخول المتطور"""
        username = request.data.get('username')
        password = request.data.get('password')
        remember_me = request.data.get('remember_me', False)
        
        if not username or not password:
            return Response({
                'error': 'اسم المستخدم وكلمة المرور مطلوبان',
                'code': 'MISSING_CREDENTIALS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # فحص الحظر
        client_ip = self._get_client_ip(request)
        is_locked, lock_type = login_tracker.is_locked(username, client_ip)
        
        if is_locked:
            return Response({
                'error': 'الحساب محظور مؤقتاً بسبب محاولات فاشلة متكررة',
                'code': 'ACCOUNT_LOCKED'
            }, status=status.HTTP_423_LOCKED)
        
        # المصادقة
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # فحص المصادقة الثنائية
                if two_factor_auth.is_enabled_for_user(user):
                    # إنشاء رمز تحقق
                    verification_code = two_factor_auth.generate_code(user)
                    
                    # حفظ معرف الجلسة المؤقت
                    temp_session_id = security_manager.generate_secure_token()
                    cache.set(f"temp_login_{temp_session_id}", {
                        'user_id': user.id,
                        'username': username,
                        'ip_address': client_ip
                    }, timeout=300)  # 5 دقائق
                    
                    # تسجيل في الأمان
                    security_audit.log_security_event(
                        event_type='2fa_code_sent',
                        user=user,
                        details='تم إرسال رمز التحقق للمصادقة الثنائية',
                        ip_address=client_ip
                    )
                    
                    return Response({
                        'requires_2fa': True,
                        'temp_session_id': temp_session_id,
                        'message': 'تم إرسال رمز التحقق، يرجى إدخاله'
                    })
                
                # تسجيل الدخول العادي
                login(request, user)
                
                # إنشاء JWT Token
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                
                # تسجيل محاولة ناجحة
                log_login_attempt(user, True, client_ip, 'تسجيل دخول ناجح')
                
                # إعدادات الجلسة
                if remember_me:
                    request.session.set_expiry(1209600)  # أسبوعين
                else:
                    request.session.set_expiry(0)  # حتى إغلاق المتصفح
                
                return Response({
                    'success': True,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': getattr(user, 'role', 'STUDENT'),
                        'full_name': f\"{getattr(user, 'first_name_ar', '')} {getattr(user, 'last_name_ar', '')}\".strip()
                    },
                    'expires_in': 7200  # ساعتين
                })
            else:
                return Response({
                    'error': 'الحساب غير مفعل',
                    'code': 'ACCOUNT_DISABLED'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # تسجيل محاولة فاشلة
        log_login_attempt(None, False, client_ip, f'فشل تسجيل دخول لـ {username}')
        
        return Response({
            'error': 'اسم المستخدم أو كلمة المرور غير صحيحة',
            'code': 'INVALID_CREDENTIALS'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def verify_2fa(self, request):
        \"\"\"التحقق من المصادقة الثنائية\"\"\"
        temp_session_id = request.data.get('temp_session_id')
        verification_code = request.data.get('code')
        
        if not temp_session_id or not verification_code:
            return Response({
                'error': 'رمز الجلسة المؤقت ورمز التحقق مطلوبان',
                'code': 'MISSING_DATA'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على بيانات الجلسة المؤقتة
        temp_data = cache.get(f\"temp_login_{temp_session_id}\")
        if not temp_data:
            return Response({
                'error': 'انتهت صلاحية رمز التحقق',
                'code': 'SESSION_EXPIRED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على المستخدم
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=temp_data['user_id'])
        except User.DoesNotExist:
            return Response({
                'error': 'مستخدم غير موجود',
                'code': 'USER_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق من الرمز
        is_valid, message = two_factor_auth.verify_code(user, verification_code)
        
        if is_valid:
            # تسجيل الدخول
            login(request, user)
            
            # إنشاء JWT Token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            # حذف الجلسة المؤقتة
            cache.delete(f\"temp_login_{temp_session_id}\")
            
            # تسجيل محاولة ناجحة
            log_login_attempt(user, True, temp_data['ip_address'], 'تسجيل دخول ناجح مع مصادقة ثنائية')
            
            return Response({
                'success': True,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': getattr(user, 'role', 'STUDENT'),
                    'full_name': f\"{getattr(user, 'first_name_ar', '')} {getattr(user, 'last_name_ar', '')}\".strip()
                },
                'expires_in': 7200
            })
        else:
            return Response({
                'error': message,
                'code': 'INVALID_2FA_CODE'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        \"\"\"تسجيل الخروج\"\"\"
        try:
            # تسجيل في النظام الأمني
            security_audit.log_security_event(
                event_type='logout',
                user=request.user,
                details='تسجيل خروج',
                ip_address=self._get_client_ip(request)
            )
            
            logout(request)
            
            return Response({
                'success': True,
                'message': 'تم تسجيل الخروج بنجاح'
            })
        except Exception as e:
            logger.error(f\"Logout error: {e}\")
            return Response({
                'error': 'فشل في تسجيل الخروج',
                'code': 'LOGOUT_FAILED'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        \"\"\"تغيير كلمة المرور\"\"\"
        if not request.user.is_authenticated:
            return Response({
                'error': 'يجب تسجيل الدخول أولاً',
                'code': 'AUTHENTICATION_REQUIRED'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'error': 'كلمة المرور الحالية والجديدة مطلوبتان',
                'code': 'MISSING_PASSWORDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من كلمة المرور الحالية
        if not request.user.check_password(old_password):
            return Response({
                'error': 'كلمة المرور الحالية غير صحيحة',
                'code': 'INVALID_OLD_PASSWORD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # فحص قوة كلمة المرور الجديدة
        password_strength = security_manager.verify_password_strength(new_password)
        
        if not password_strength['is_strong']:
            return Response({
                'error': 'كلمة المرور ضعيفة',
                'issues': password_strength['issues'],
                'code': 'WEAK_PASSWORD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # تغيير كلمة المرور
        request.user.set_password(new_password)
        request.user.save()
        
        # تسجيل في النظام الأمني
        security_audit.log_security_event(
            event_type='password_changed',
            user=request.user,
            details='تم تغيير كلمة المرور',
            ip_address=self._get_client_ip(request),
            severity='medium'
        )
        
        return Response({
            'success': True,
            'message': 'تم تغيير كلمة المرور بنجاح'
        })
    
    def _get_client_ip(self, request):
        \"\"\"الحصول على IP العميل\"\"\"
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SystemAPIViewSet(viewsets.GenericViewSet):
    \"\"\"APIs النظام والمراقبة\"\"\"
    
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    
    @action(detail=False, methods=['get'])
    def system_status(self, request):
        \"\"\"حالة النظام العامة\"\"\"
        try:
            # حالة النظام من المراقب
            health_status = monitor.get_health_status()
            
            # إحصائيات قاعدة البيانات
            db_stats = monitor.get_database_stats()
            
            # إحصائيات الأخطاء
            error_stats = error_tracker.get_error_statistics(24)
            
            return Response({
                'system_health': health_status,
                'database': db_stats,
                'errors': {
                    'total_24h': error_stats.get('total_errors', 0),
                    'error_types': error_stats.get('error_types', {})
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f\"System status error: {e}\")
            return Response({
                'error': 'فشل في الحصول على حالة النظام',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def performance_metrics(self, request):
        \"\"\"مقاييس الأداء\"\"\"
        hours = int(request.GET.get('hours', 1))
        
        try:
            metrics = monitor.get_metrics_summary(hours)
            return Response({
                'metrics': metrics,
                'period_hours': hours,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f\"Performance metrics error: {e}\")
            return Response({
                'error': 'فشل في الحصول على مقاييس الأداء',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def security_events(self, request):
        \"\"\"الأحداث الأمنية\"\"\"
        hours = int(request.GET.get('hours', 24))
        event_type = request.GET.get('type')
        
        try:
            events = security_audit.get_recent_events(event_type, hours)
            return Response({
                'events': events,
                'total': len(events),
                'period_hours': hours,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f\"Security events error: {e}\")
            return Response({
                'error': 'فشل في الحصول على الأحداث الأمنية',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_info(request):
    \"\"\"معلومات API\"\"\"
    return Response({
        'name': 'University Management System API',
        'version': '2.0.0',
        'description': 'نظام إدارة الجامعة - واجهة برمجة التطبيقات المتطورة',
        'features': [
            'مصادقة آمنة مع JWT',
            'مصادقة ثنائية',
            'مراقبة الأداء',
            'نظام تدقيق الأمان',
            'حد معدل الطلبات',
            'تشفير البيانات'
        ],
        'endpoints': {
            'authentication': '/api/auth/',
            'system': '/api/system/',
            'students': '/api/students/',
            'courses': '/api/courses/',
            'academic': '/api/academic/',
            'documentation': '/swagger/'
        },
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@method_decorator(cache_page(300))  # كاش لمدة 5 دقائق
def public_stats(request):
    \"\"\"إحصائيات عامة للنظام\"\"\"
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # إحصائيات عامة (بدون تفاصيل حساسة)
        stats = {
            'total_users': User.objects.filter(is_active=True).count(),
            'students_count': User.objects.filter(role='STUDENT', is_active=True).count(),
            'teachers_count': User.objects.filter(role__in=['TEACHER', 'ASSISTANT_TEACHER'], is_active=True).count(),
            'system_uptime_hours': monitor._get_uptime(),
            'last_updated': timezone.now().isoformat()
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f\"Public stats error: {e}\")
        return Response({
            'error': 'فشل في الحصول على الإحصائيات',
            'detail': 'خطأ في النظام'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)