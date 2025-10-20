# وسائط الأمان السيبراني المتقدم
# Advanced Cyber Security Middleware

import json
import time
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

from .security_engine import threat_detector, behavior_analyzer
from .models import SecurityEvent, SecurityIncident, UserBehaviorProfile, SecurityAuditLog

User = get_user_model()
security_logger = logging.getLogger('security')

class SecurityThreatDetectionMiddleware(MiddlewareMixin):
    """وسائط كشف التهديدات الأمنية"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
        # قائمة المسارات المستثناة من الفحص
        self.excluded_paths = [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
            '/admin/jsi18n/'
        ]
        
        # قائمة الـ IPs المعتمدة (whitelist)
        self.whitelisted_ips = getattr(settings, 'SECURITY_WHITELISTED_IPS', [
            '127.0.0.1', '::1', 'localhost'
        ])
    
    def process_request(self, request):
        """معالجة الطلب قبل الوصول للعرض"""
        
        # تخطي المسارات المستثناة
        if any(request.path.startswith(path) for path in self.excluded_paths):
            return None
        
        # الحصول على معلومات الطلب
        request_data = self._extract_request_data(request)
        
        # فحص الـ IP المعتمد
        if request_data['ip_address'] in self.whitelisted_ips:
            return None
        
        # تحليل التهديدات
        threat_analysis = threat_detector.analyze_request(request_data)
        
        # إذا تم اكتشاف تهديدات خطيرة، نحظر الطلب
        if threat_analysis.get('should_block', False):
            self._handle_security_threat(request, threat_analysis)
            return self._create_security_response(threat_analysis)
        
        # إذا كانت هناك تهديدات أقل خطورة، نسجلها فقط
        elif threat_analysis.get('has_threats', False):
            self._log_security_event(request, threat_analysis)
        
        # إضافة معلومات التحليل للطلب
        request.security_analysis = threat_analysis
        
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة بعد العرض"""
        
        # تسجيل نشاط المستخدم إذا كان مسجلاً للدخول
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._log_user_activity(request, response)
        
        return response
    
    def _extract_request_data(self, request) -> dict:
        """استخراج بيانات الطلب للتحليل"""
        
        # الحصول على عنوان IP الحقيقي
        ip_address = self._get_client_ip(request)
        
        # الحصول على بيانات POST إذا وجدت
        post_data = ''
        if request.method == 'POST':
            try:
                if hasattr(request, 'body'):
                    post_data = request.body.decode('utf-8', errors='ignore')[:1000]  # أول 1000 حرف
            except:
                post_data = str(request.POST)[:1000]
        
        return {
            'ip_address': ip_address,
            'path': request.get_full_path(),
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'post_data': post_data,
            'timestamp': datetime.now().isoformat(),
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
        }
    
    def _get_client_ip(self, request) -> str:
        """الحصول على عنوان IP الحقيقي للعميل"""
        
        # فحص العناوين المختلفة بالترتيب
        for header in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_X_FORWARDED', 'REMOTE_ADDR']:
            ip = request.META.get(header)
            if ip:
                # في حالة وجود عدة IPs، نأخذ الأول
                return ip.split(',')[0].strip()
        
        return '0.0.0.0'
    
    def _handle_security_threat(self, request, threat_analysis):
        """التعامل مع التهديد الأمني المكتشف"""
        
        try:
            request_data = self._extract_request_data(request)
            
            # إنشاء حدث أمني
            security_event = SecurityEvent.objects.create(
                event_type=self._determine_event_type(threat_analysis),
                threat_level=threat_analysis.get('threat_level', 'medium'),
                title=f"Security threat detected from {request_data['ip_address']}",
                description=self._create_threat_description(threat_analysis),
                ip_address=request_data['ip_address'],
                user_agent=request_data['user_agent'],
                request_path=request_data['path'],
                request_method=request_data['method'],
                metadata={'analysis': threat_analysis},
                affected_user_id=request_data.get('user_id')
            )
            
            # إضافة IP للقائمة السوداء المؤقتة إذا كان التهديد حرجاً
            if threat_analysis.get('threat_level') == 'critical':
                self._add_to_temporary_blacklist(request_data['ip_address'])
            
            # إشعار فريق الأمان إذا لزم الأمر
            if threat_analysis.get('threat_level') in ['high', 'critical']:
                self._notify_security_team(security_event)
            
            security_logger.warning(
                f"Security threat blocked: {threat_analysis.get('threat_level')} "
                f"from {request_data['ip_address']} - {threat_analysis.get('threats_detected', [])}"
            )
            
        except Exception as e:
            security_logger.error(f"Error handling security threat: {str(e)}")
    
    def _log_security_event(self, request, threat_analysis):
        """تسجيل حدث أمني غير حرج"""
        
        try:
            request_data = self._extract_request_data(request)
            
            SecurityEvent.objects.create(
                event_type=self._determine_event_type(threat_analysis),
                threat_level=threat_analysis.get('threat_level', 'low'),
                title=f"Security anomaly detected from {request_data['ip_address']}",
                description=self._create_threat_description(threat_analysis),
                ip_address=request_data['ip_address'],
                user_agent=request_data['user_agent'],
                request_path=request_data['path'],
                request_method=request_data['method'],
                metadata={'analysis': threat_analysis},
                affected_user_id=request_data.get('user_id')
            )
            
        except Exception as e:
            security_logger.error(f"Error logging security event: {str(e)}")
    
    def _log_user_activity(self, request, response):
        """تسجيل نشاط المستخدم"""
        
        try:
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return
            
            # تخطي طلبات AJAX البسيطة
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return
            
            request_data = self._extract_request_data(request)
            
            # تحديد نوع الإجراء
            action_type = self._determine_action_type(request.method, request.path)
            
            # إنشاء سجل مراجعة
            SecurityAuditLog.objects.create(
                user=request.user,
                action_type=action_type,
                description=f"{request.method} {request.path}",
                ip_address=request_data['ip_address'],
                user_agent=request_data['user_agent'],
                success=200 <= response.status_code < 400
            )
            
        except Exception as e:
            security_logger.error(f"Error logging user activity: {str(e)}")
    
    def _determine_event_type(self, threat_analysis) -> str:
        """تحديد نوع الحدث الأمني"""
        
        threats = threat_analysis.get('threats_detected', [])
        
        if not threats:
            return 'suspicious_activity'
        
        # البحث عن أخطر نوع تهديد
        threat_types = []
        for threat in threats:
            if isinstance(threat, dict):
                threat_types.append(threat.get('threat_type', 'unknown'))
        
        if 'sql_injection' in threat_types:
            return 'sql_injection'
        elif 'xss_attempt' in threat_types:
            return 'xss_attempt'
        elif 'command_injection' in threat_types:
            return 'command_injection'
        elif 'path_traversal' in threat_types:
            return 'path_traversal'
        elif 'brute_force_attempt' in threat_types:
            return 'brute_force'
        else:
            return 'suspicious_activity'
    
    def _create_threat_description(self, threat_analysis) -> str:
        """إنشاء وصف للتهديد المكتشف"""
        
        threats = threat_analysis.get('threats_detected', [])
        total_risk = threat_analysis.get('total_risk_score', 0)
        
        if not threats:
            return f"Suspicious activity detected with risk score: {total_risk}"
        
        descriptions = []
        for threat in threats:
            if isinstance(threat, dict):
                threat_type = threat.get('threat_type', 'unknown')
                description = threat.get('description', f'{threat_type} detected')
                descriptions.append(description)
        
        return '; '.join(descriptions[:3])  # أول 3 تهديدات
    
    def _determine_action_type(self, method: str, path: str) -> str:
        """تحديد نوع الإجراء للتسجيل"""
        
        if method == 'GET':
            return 'read'
        elif method == 'POST':
            if 'login' in path:
                return 'login'
            elif 'logout' in path:
                return 'logout'
            else:
                return 'create'
        elif method == 'PUT' or method == 'PATCH':
            return 'update'
        elif method == 'DELETE':
            return 'delete'
        else:
            return 'unknown'
    
    def _add_to_temporary_blacklist(self, ip_address: str):
        """إضافة IP للقائمة السوداء المؤقتة"""
        
        cache_key = f'blacklisted_ip_{ip_address}'
        cache.set(cache_key, True, 3600)  # ساعة واحدة
        
        security_logger.info(f"IP {ip_address} added to temporary blacklist")
    
    def _notify_security_team(self, security_event):
        """إشعار فريق الأمان بالتهديد"""
        
        # يمكن إرسال إيميل أو إشعار فوري
        # هذا مثال بسيط
        security_logger.critical(
            f"CRITICAL SECURITY ALERT: {security_event.title} - "
            f"Event ID: {security_event.id}"
        )
    
    def _create_security_response(self, threat_analysis):
        """إنشاء استجابة للتهديد الأمني"""
        
        if threat_analysis.get('threat_level') == 'critical':
            return HttpResponseForbidden(
                json.dumps({
                    'error': 'Security threat detected. Access denied.',
                    'threat_level': 'critical',
                    'timestamp': datetime.now().isoformat()
                }),
                content_type='application/json'
            )
        else:
            return JsonResponse({
                'error': 'Suspicious activity detected.',
                'threat_level': threat_analysis.get('threat_level', 'medium'),
                'timestamp': datetime.now().isoformat()
            }, status=403)

class BehaviorAnalysisMiddleware(MiddlewareMixin):
    """وسائط تحليل سلوك المستخدمين"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """تحليل سلوك المستخدم عند تسجيل الدخول"""
        
        # تحليل السلوك فقط للمستخدمين المسجلين
        if not (hasattr(request, 'user') and request.user.is_authenticated):
            return None
        
        try:
            # إعداد بيانات الجلسة الحالية
            current_session = {
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': datetime.now().isoformat(),
                'path': request.path
            }
            
            # تحليل السلوك
            behavior_analysis = behavior_analyzer.analyze_user_behavior(
                request.user.id, 
                current_session
            )
            
            # إضافة التحليل للطلب
            request.behavior_analysis = behavior_analysis
            
            # إذا كان السلوك مشبوهاً جداً، نسجل تنبيهاً
            if behavior_analysis.get('is_anomalous') and behavior_analysis.get('total_anomaly_score', 0) > 0.8:
                self._handle_anomalous_behavior(request, behavior_analysis)
            
            # تحديث ملف سلوك المستخدم
            self._update_user_behavior_profile(request.user, current_session, behavior_analysis)
            
        except Exception as e:
            security_logger.error(f"Error in behavior analysis: {str(e)}")
        
        return None
    
    def _get_client_ip(self, request) -> str:
        """الحصول على عنوان IP الحقيقي"""
        
        for header in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'REMOTE_ADDR']:
            ip = request.META.get(header)
            if ip:
                return ip.split(',')[0].strip()
        return '0.0.0.0'
    
    def _handle_anomalous_behavior(self, request, behavior_analysis):
        """التعامل مع السلوك الشاذ"""
        
        try:
            # إنشاء حدث أمني
            SecurityEvent.objects.create(
                event_type='anomaly_detection',
                threat_level='high' if behavior_analysis.get('total_anomaly_score', 0) > 0.9 else 'medium',
                title=f"Anomalous behavior detected for user {request.user.username}",
                description=f"User behavior analysis detected anomaly with score: {behavior_analysis.get('total_anomaly_score', 0)}",
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_path=request.path,
                affected_user=request.user,
                metadata={'behavior_analysis': behavior_analysis}
            )
            
            security_logger.warning(
                f"Anomalous behavior detected for user {request.user.username} "
                f"(ID: {request.user.id}) with score: {behavior_analysis.get('total_anomaly_score', 0)}"
            )
            
        except Exception as e:
            security_logger.error(f"Error handling anomalous behavior: {str(e)}")
    
    def _update_user_behavior_profile(self, user, current_session, behavior_analysis):
        """تحديث ملف سلوك المستخدم"""
        
        try:
            profile, created = UserBehaviorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'typical_login_hours': [],
                    'typical_locations': [],
                    'typical_devices': [],
                    'anomaly_score': 0.0,
                    'risk_score': 0.0
                }
            )
            
            # تحديث الإحصائيات
            profile.total_logins += 1
            profile.anomaly_score = behavior_analysis.get('total_anomaly_score', 0)
            profile.risk_score = self._calculate_risk_score(behavior_analysis)
            profile.last_login_analyzed = datetime.now()
            
            # تحديث الأنماط النموذجية (مبسط)
            current_hour = datetime.now().hour
            if current_hour not in profile.typical_login_hours:
                profile.typical_login_hours.append(current_hour)
                # الاحتفاظ بآخر 10 ساعات فقط
                profile.typical_login_hours = profile.typical_login_hours[-10:]
            
            current_ip = current_session.get('ip_address', '')
            if current_ip and current_ip not in profile.typical_locations:
                profile.typical_locations.append(current_ip)
                # الاحتفاظ بآخر 5 مواقع فقط
                profile.typical_locations = profile.typical_locations[-5:]
            
            profile.save()
            
        except Exception as e:
            security_logger.error(f"Error updating user behavior profile: {str(e)}")
    
    def _calculate_risk_score(self, behavior_analysis) -> float:
        """حساب درجة المخاطر للمستخدم"""
        
        anomaly_score = behavior_analysis.get('total_anomaly_score', 0)
        risk_level = behavior_analysis.get('risk_level', 'low')
        
        # تحويل مستوى المخاطر لدرجة رقمية
        risk_multipliers = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8,
            'critical': 1.0
        }
        
        return anomaly_score * risk_multipliers.get(risk_level, 0.5)

class RateLimitingMiddleware(MiddlewareMixin):
    """وسائط تحديد معدل الطلبات"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
        # حدود المعدل الافتراضية
        self.default_limits = {
            'per_ip': 100,      # 100 طلب في الدقيقة لكل IP
            'per_user': 200,    # 200 طلب في الدقيقة لكل مستخدم
            'login_attempts': 5  # 5 محاولات دخول في الدقيقة
        }
    
    def process_request(self, request):
        """فحص حدود المعدل"""
        
        ip_address = self._get_client_ip(request)
        
        # فحص حد IP
        if not self._check_ip_rate_limit(ip_address):
            return JsonResponse({
                'error': 'Rate limit exceeded for IP address',
                'retry_after': 60
            }, status=429)
        
        # فحص حد المستخدم إذا كان مسجلاً للدخول
        if hasattr(request, 'user') and request.user.is_authenticated:
            if not self._check_user_rate_limit(request.user.id):
                return JsonResponse({
                    'error': 'Rate limit exceeded for user',
                    'retry_after': 60
                }, status=429)
        
        # فحص محاولات تسجيل الدخول
        if 'login' in request.path.lower():
            if not self._check_login_rate_limit(ip_address):
                return JsonResponse({
                    'error': 'Too many login attempts',
                    'retry_after': 300  # 5 دقائق
                }, status=429)
        
        return None
    
    def _get_client_ip(self, request) -> str:
        """الحصول على عنوان IP"""
        
        for header in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'REMOTE_ADDR']:
            ip = request.META.get(header)
            if ip:
                return ip.split(',')[0].strip()
        return '0.0.0.0'
    
    def _check_ip_rate_limit(self, ip_address: str) -> bool:
        """فحص حد معدل IP"""
        
        cache_key = f'rate_limit_ip_{ip_address}'
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.default_limits['per_ip']:
            return False
        
        # زيادة العداد
        cache.set(cache_key, current_requests + 1, 60)  # دقيقة واحدة
        return True
    
    def _check_user_rate_limit(self, user_id: int) -> bool:
        """فحص حد معدل المستخدم"""
        
        cache_key = f'rate_limit_user_{user_id}'
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.default_limits['per_user']:
            return False
        
        cache.set(cache_key, current_requests + 1, 60)
        return True
    
    def _check_login_rate_limit(self, ip_address: str) -> bool:
        """فحص حد محاولات تسجيل الدخول"""
        
        cache_key = f'login_attempts_{ip_address}'
        current_attempts = cache.get(cache_key, 0)
        
        if current_attempts >= self.default_limits['login_attempts']:
            return False
        
        cache.set(cache_key, current_attempts + 1, 300)  # 5 دقائق
        return True