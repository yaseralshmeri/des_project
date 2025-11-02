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
                    'user': {\n                        'id': user.id,\n                        'username': user.username,\n                        'email': user.email,\n                        'role': getattr(user, 'role', 'STUDENT'),\n                        'full_name': f\"{getattr(user, 'first_name_ar', '')} {getattr(user, 'last_name_ar', '')}\".strip()\n                    },\n                    'expires_in': 7200  # ساعتين\n                })\n            else:\n                return Response({\n                    'error': 'الحساب غير مفعل',\n                    'code': 'ACCOUNT_DISABLED'\n                }, status=status.HTTP_403_FORBIDDEN)\n        \n        # تسجيل محاولة فاشلة\n        log_login_attempt(None, False, client_ip, f'فشل تسجيل دخول لـ {username}')\n        \n        return Response({\n            'error': 'اسم المستخدم أو كلمة المرور غير صحيحة',\n            'code': 'INVALID_CREDENTIALS'\n        }, status=status.HTTP_401_UNAUTHORIZED)\n    \n    @action(detail=False, methods=['post'])\n    def verify_2fa(self, request):\n        \"\"\"التحقق من المصادقة الثنائية\"\"\"\n        temp_session_id = request.data.get('temp_session_id')\n        verification_code = request.data.get('code')\n        \n        if not temp_session_id or not verification_code:\n            return Response({\n                'error': 'رمز الجلسة المؤقت ورمز التحقق مطلوبان',\n                'code': 'MISSING_DATA'\n            }, status=status.HTTP_400_BAD_REQUEST)\n        \n        # الحصول على بيانات الجلسة المؤقتة\n        temp_data = cache.get(f\"temp_login_{temp_session_id}\")\n        if not temp_data:\n            return Response({\n                'error': 'انتهت صلاحية رمز التحقق',\n                'code': 'SESSION_EXPIRED'\n            }, status=status.HTTP_400_BAD_REQUEST)\n        \n        # الحصول على المستخدم\n        from django.contrib.auth import get_user_model\n        User = get_user_model()\n        \n        try:\n            user = User.objects.get(id=temp_data['user_id'])\n        except User.DoesNotExist:\n            return Response({\n                'error': 'مستخدم غير موجود',\n                'code': 'USER_NOT_FOUND'\n            }, status=status.HTTP_404_NOT_FOUND)\n        \n        # التحقق من الرمز\n        is_valid, message = two_factor_auth.verify_code(user, verification_code)\n        \n        if is_valid:\n            # تسجيل الدخول\n            login(request, user)\n            \n            # إنشاء JWT Token\n            from rest_framework_simplejwt.tokens import RefreshToken\n            refresh = RefreshToken.for_user(user)\n            \n            # حذف الجلسة المؤقتة\n            cache.delete(f\"temp_login_{temp_session_id}\")\n            \n            # تسجيل محاولة ناجحة\n            log_login_attempt(user, True, temp_data['ip_address'], 'تسجيل دخول ناجح مع مصادقة ثنائية')\n            \n            return Response({\n                'success': True,\n                'access_token': str(refresh.access_token),\n                'refresh_token': str(refresh),\n                'user': {\n                    'id': user.id,\n                    'username': user.username,\n                    'email': user.email,\n                    'role': getattr(user, 'role', 'STUDENT'),\n                    'full_name': f\"{getattr(user, 'first_name_ar', '')} {getattr(user, 'last_name_ar', '')}\".strip()\n                },\n                'expires_in': 7200\n            })\n        else:\n            return Response({\n                'error': message,\n                'code': 'INVALID_2FA_CODE'\n            }, status=status.HTTP_400_BAD_REQUEST)\n    \n    @action(detail=False, methods=['post'])\n    def logout(self, request):\n        \"\"\"تسجيل الخروج\"\"\"\n        try:\n            # تسجيل في النظام الأمني\n            security_audit.log_security_event(\n                event_type='logout',\n                user=request.user,\n                details='تسجيل خروج',\n                ip_address=self._get_client_ip(request)\n            )\n            \n            logout(request)\n            \n            return Response({\n                'success': True,\n                'message': 'تم تسجيل الخروج بنجاح'\n            })\n        except Exception as e:\n            logger.error(f\"Logout error: {e}\")\n            return Response({\n                'error': 'فشل في تسجيل الخروج',\n                'code': 'LOGOUT_FAILED'\n            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)\n    \n    @action(detail=False, methods=['post'])\n    def change_password(self, request):\n        \"\"\"تغيير كلمة المرور\"\"\"\n        if not request.user.is_authenticated:\n            return Response({\n                'error': 'يجب تسجيل الدخول أولاً',\n                'code': 'AUTHENTICATION_REQUIRED'\n            }, status=status.HTTP_401_UNAUTHORIZED)\n        \n        old_password = request.data.get('old_password')\n        new_password = request.data.get('new_password')\n        \n        if not old_password or not new_password:\n            return Response({\n                'error': 'كلمة المرور الحالية والجديدة مطلوبتان',\n                'code': 'MISSING_PASSWORDS'\n            }, status=status.HTTP_400_BAD_REQUEST)\n        \n        # التحقق من كلمة المرور الحالية\n        if not request.user.check_password(old_password):\n            return Response({\n                'error': 'كلمة المرور الحالية غير صحيحة',\n                'code': 'INVALID_OLD_PASSWORD'\n            }, status=status.HTTP_400_BAD_REQUEST)\n        \n        # فحص قوة كلمة المرور الجديدة\n        password_strength = security_manager.verify_password_strength(new_password)\n        \n        if not password_strength['is_strong']:\n            return Response({\n                'error': 'كلمة المرور ضعيفة',\n                'issues': password_strength['issues'],\n                'code': 'WEAK_PASSWORD'\n            }, status=status.HTTP_400_BAD_REQUEST)\n        \n        # تغيير كلمة المرور\n        request.user.set_password(new_password)\n        request.user.save()\n        \n        # تسجيل في النظام الأمني\n        security_audit.log_security_event(\n            event_type='password_changed',\n            user=request.user,\n            details='تم تغيير كلمة المرور',\n            ip_address=self._get_client_ip(request),\n            severity='medium'\n        )\n        \n        return Response({\n            'success': True,\n            'message': 'تم تغيير كلمة المرور بنجاح'\n        })\n    \n    def _get_client_ip(self, request):\n        \"\"\"الحصول على IP العميل\"\"\"\n        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')\n        if x_forwarded_for:\n            ip = x_forwarded_for.split(',')[0]\n        else:\n            ip = request.META.get('REMOTE_ADDR')\n        return ip\n\n\nclass SystemAPIViewSet(viewsets.GenericViewSet):\n    \"\"\"APIs النظام والمراقبة\"\"\"\n    \n    permission_classes = [permissions.IsAdminUser]\n    authentication_classes = [JWTAuthentication, TokenAuthentication]\n    \n    @action(detail=False, methods=['get'])\n    def system_status(self, request):\n        \"\"\"حالة النظام العامة\"\"\"\n        try:\n            # حالة النظام من المراقب\n            health_status = monitor.get_health_status()\n            \n            # إحصائيات قاعدة البيانات\n            db_stats = monitor.get_database_stats()\n            \n            # إحصائيات الأخطاء\n            error_stats = error_tracker.get_error_statistics(24)\n            \n            return Response({\n                'system_health': health_status,\n                'database': db_stats,\n                'errors': {\n                    'total_24h': error_stats.get('total_errors', 0),\n                    'error_types': error_stats.get('error_types', {})\n                },\n                'timestamp': timezone.now().isoformat()\n            })\n            \n        except Exception as e:\n            logger.error(f\"System status error: {e}\")\n            return Response({\n                'error': 'فشل في الحصول على حالة النظام',\n                'detail': str(e)\n            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)\n    \n    @action(detail=False, methods=['get'])\n    def performance_metrics(self, request):\n        \"\"\"مقاييس الأداء\"\"\"\n        hours = int(request.GET.get('hours', 1))\n        \n        try:\n            metrics = monitor.get_metrics_summary(hours)\n            return Response({\n                'metrics': metrics,\n                'period_hours': hours,\n                'timestamp': timezone.now().isoformat()\n            })\n            \n        except Exception as e:\n            logger.error(f\"Performance metrics error: {e}\")\n            return Response({\n                'error': 'فشل في الحصول على مقاييس الأداء',\n                'detail': str(e)\n            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)\n    \n    @action(detail=False, methods=['get'])\n    def security_events(self, request):\n        \"\"\"الأحداث الأمنية\"\"\"\n        hours = int(request.GET.get('hours', 24))\n        event_type = request.GET.get('type')\n        \n        try:\n            events = security_audit.get_recent_events(event_type, hours)\n            return Response({\n                'events': events,\n                'total': len(events),\n                'period_hours': hours,\n                'timestamp': timezone.now().isoformat()\n            })\n            \n        except Exception as e:\n            logger.error(f\"Security events error: {e}\")\n            return Response({\n                'error': 'فشل في الحصول على الأحداث الأمنية',\n                'detail': str(e)\n            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)\n\n\n@api_view(['GET'])\n@permission_classes([permissions.AllowAny])\ndef api_info(request):\n    \"\"\"معلومات API\"\"\"\n    return Response({\n        'name': 'University Management System API',\n        'version': '2.0.0',\n        'description': 'نظام إدارة الجامعة - واجهة برمجة التطبيقات المتطورة',\n        'features': [\n            'مصادقة آمنة مع JWT',\n            'مصادقة ثنائية',\n            'مراقبة الأداء',\n            'نظام تدقيق الأمان',\n            'حد معدل الطلبات',\n            'تشفير البيانات'\n        ],\n        'endpoints': {\n            'authentication': '/api/auth/',\n            'system': '/api/system/',\n            'students': '/api/students/',\n            'courses': '/api/courses/',\n            'academic': '/api/academic/',\n            'documentation': '/swagger/'\n        },\n        'timestamp': timezone.now().isoformat()\n    })\n\n\n@api_view(['GET'])\n@permission_classes([permissions.AllowAny])\n@method_decorator(cache_page(300))  # كاش لمدة 5 دقائق\ndef public_stats(request):\n    \"\"\"إحصائيات عامة للنظام\"\"\"\n    try:\n        from django.contrib.auth import get_user_model\n        User = get_user_model()\n        \n        # إحصائيات عامة (بدون تفاصيل حساسة)\n        stats = {\n            'total_users': User.objects.filter(is_active=True).count(),\n            'students_count': User.objects.filter(role='STUDENT', is_active=True).count(),\n            'teachers_count': User.objects.filter(role__in=['TEACHER', 'ASSISTANT_TEACHER'], is_active=True).count(),\n            'system_uptime_hours': monitor._get_uptime(),\n            'last_updated': timezone.now().isoformat()\n        }\n        \n        return Response(stats)\n        \n    except Exception as e:\n        logger.error(f\"Public stats error: {e}\")\n        return Response({\n            'error': 'فشل في الحصول على الإحصائيات',\n            'detail': 'خطأ في النظام'\n        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)