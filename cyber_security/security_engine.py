# محرك الأمان السيبراني المتقدم
# Advanced Cyber Security Engine

import hashlib
import hmac
import time
import json
import re
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
import requests
import socket

# إعداد نظام التسجيل الأمني
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger('security')

class SecurityThreatDetector:
    """كاشف التهديدات الأمنية المتقدم"""
    
    def __init__(self):
        self.suspicious_patterns = {
            'sql_injection': [
                r"union\s+select", r"drop\s+table", r"delete\s+from",
                r"insert\s+into", r"update\s+set", r"exec\s*\(",
                r"script\s*>", r"<\s*script", r"javascript:",
                r"'.*or.*'.*=.*'", r"'.*and.*'.*=.*'"
            ],
            'xss_attempt': [
                r"<script[^>]*>.*?</script>", r"javascript:", r"on\w+\s*=",
                r"<iframe", r"<object", r"<embed", r"<form",
                r"eval\s*\(", r"document\.cookie", r"window\.location"
            ],
            'path_traversal': [
                r"\.\.\/", r"\.\.\\", r"\/etc\/passwd", r"\/windows\/system32",
                r"config\.php", r"web\.config", r"\.htaccess"
            ],
            'command_injection': [
                r";\s*(cat|ls|dir|type|more)\s", r"\|\s*(nc|netcat|telnet)",
                r"&\s*(wget|curl|ping)", r"`.*`", r"\$\(.*\)"
            ]
        }
        
        self.threat_levels = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        # قائمة الـ IPs المشبوهة (يمكن تحديثها من مصادر خارجية)
        self.suspicious_ips = set()
        self.blocked_ips = set()
        
        # عدادات للهجمات
        self.attack_counters = defaultdict(lambda: defaultdict(int))
        
    def analyze_request(self, request_data: Dict) -> Dict:
        """تحليل طلب HTTP للكشف عن التهديدات"""
        
        threats_detected = []
        risk_score = 0
        
        try:
            # تحليل IP address
            ip_analysis = self._analyze_ip(request_data.get('ip_address', ''))
            if ip_analysis['is_suspicious']:
                threats_detected.append(ip_analysis)
                risk_score += ip_analysis['risk_score']
            
            # تحليل URL والمعاملات
            url_analysis = self._analyze_url(request_data.get('path', ''))
            if url_analysis['threats_found']:
                threats_detected.extend(url_analysis['threats_found'])
                risk_score += url_analysis['risk_score']
            
            # تحليل بيانات POST
            if request_data.get('post_data'):
                post_analysis = self._analyze_post_data(request_data['post_data'])
                if post_analysis['threats_found']:
                    threats_detected.extend(post_analysis['threats_found'])
                    risk_score += post_analysis['risk_score']
            
            # تحليل User Agent
            ua_analysis = self._analyze_user_agent(request_data.get('user_agent', ''))
            if ua_analysis['is_suspicious']:
                threats_detected.append(ua_analysis)
                risk_score += ua_analysis['risk_score']
            
            # تحليل أنماط الطلبات
            pattern_analysis = self._analyze_request_patterns(request_data)
            if pattern_analysis['is_suspicious']:
                threats_detected.append(pattern_analysis)
                risk_score += pattern_analysis['risk_score']
            
            # تحديد مستوى الخطر الإجمالي
            threat_level = self._calculate_threat_level(risk_score)
            
            return {
                'has_threats': len(threats_detected) > 0,
                'threats_detected': threats_detected,
                'total_risk_score': risk_score,
                'threat_level': threat_level,
                'should_block': threat_level in ['high', 'critical'],
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            security_logger.error(f"Error in security analysis: {str(e)}")
            return {
                'has_threats': False,
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _analyze_ip(self, ip_address: str) -> Dict:
        """تحليل عنوان IP للكشف عن التهديدات"""
        
        if not ip_address:
            return {'is_suspicious': False, 'risk_score': 0}
        
        try:
            # التحقق من IP المحلي
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private:
                return {'is_suspicious': False, 'risk_score': 0, 'reason': 'Private IP'}
            
            # التحقق من القائمة السوداء
            if ip_address in self.blocked_ips:
                return {
                    'is_suspicious': True,
                    'risk_score': 50,
                    'threat_type': 'blocked_ip',
                    'reason': 'IP in blacklist'
                }
            
            # التحقق من معدل الطلبات
            request_count = self._get_request_count(ip_address)
            if request_count > 100:  # أكثر من 100 طلب في الدقيقة
                return {
                    'is_suspicious': True,
                    'risk_score': 30,
                    'threat_type': 'rate_limit_exceeded',
                    'reason': f'High request rate: {request_count}/min'
                }
            
            # فحص الموقع الجغرافي (اختياري)
            geo_info = self._get_ip_geolocation(ip_address)
            if geo_info and geo_info.get('country') in ['CN', 'RU', 'NK']:  # بلدان عالية المخاطر
                return {
                    'is_suspicious': True,
                    'risk_score': 20,
                    'threat_type': 'suspicious_location',
                    'reason': f"Request from high-risk country: {geo_info.get('country')}"
                }
            
            return {'is_suspicious': False, 'risk_score': 0}
            
        except Exception as e:
            return {'is_suspicious': False, 'risk_score': 0, 'error': str(e)}
    
    def _analyze_url(self, url_path: str) -> Dict:
        """تحليل URL للكشف عن أنماط الهجمات"""
        
        threats_found = []
        total_risk = 0
        
        if not url_path:
            return {'threats_found': [], 'risk_score': 0}
        
        url_lower = url_path.lower()
        
        # فحص أنماط SQL Injection
        for pattern in self.suspicious_patterns['sql_injection']:
            if re.search(pattern, url_lower, re.IGNORECASE):
                threats_found.append({
                    'threat_type': 'sql_injection',
                    'pattern_matched': pattern,
                    'risk_score': 40,
                    'description': 'Possible SQL injection attempt detected'
                })
                total_risk += 40
        
        # فحص أنماط XSS
        for pattern in self.suspicious_patterns['xss_attempt']:
            if re.search(pattern, url_path, re.IGNORECASE):
                threats_found.append({
                    'threat_type': 'xss_attempt',
                    'pattern_matched': pattern,
                    'risk_score': 35,
                    'description': 'Possible XSS attempt detected'
                })
                total_risk += 35
        
        # فحص Path Traversal
        for pattern in self.suspicious_patterns['path_traversal']:
            if re.search(pattern, url_path, re.IGNORECASE):
                threats_found.append({
                    'threat_type': 'path_traversal',
                    'pattern_matched': pattern,
                    'risk_score': 45,
                    'description': 'Possible path traversal attempt detected'
                })
                total_risk += 45
        
        # فحص Command Injection
        for pattern in self.suspicious_patterns['command_injection']:
            if re.search(pattern, url_path, re.IGNORECASE):
                threats_found.append({
                    'threat_type': 'command_injection',
                    'pattern_matched': pattern,
                    'risk_score': 50,
                    'description': 'Possible command injection attempt detected'
                })
                total_risk += 50
        
        return {
            'threats_found': threats_found,
            'risk_score': min(total_risk, 100)  # حد أقصى 100
        }
    
    def _analyze_post_data(self, post_data: str) -> Dict:
        """تحليل بيانات POST للكشف عن التهديدات"""
        
        threats_found = []
        total_risk = 0
        
        if not post_data:
            return {'threats_found': [], 'risk_score': 0}
        
        # تحويل لنص صغير للفحص
        data_lower = post_data.lower()
        
        # فحص أنماط مختلفة من الهجمات
        for attack_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, data_lower, re.IGNORECASE):
                    risk_score = 30 if attack_type == 'xss_attempt' else 40
                    threats_found.append({
                        'threat_type': attack_type,
                        'pattern_matched': pattern,
                        'risk_score': risk_score,
                        'description': f'Possible {attack_type.replace("_", " ")} in POST data'
                    })
                    total_risk += risk_score
        
        # فحص أحجام البيانات غير الطبيعية
        if len(post_data) > 10000:  # أكثر من 10KB
            threats_found.append({
                'threat_type': 'oversized_request',
                'risk_score': 20,
                'description': f'Unusually large POST data: {len(post_data)} bytes'
            })
            total_risk += 20
        
        return {
            'threats_found': threats_found,
            'risk_score': min(total_risk, 100)
        }
    
    def _analyze_user_agent(self, user_agent: str) -> Dict:
        """تحليل User Agent للكشف عن الأنشطة المشبوهة"""
        
        if not user_agent:
            return {
                'is_suspicious': True,
                'risk_score': 25,
                'reason': 'Missing User-Agent header'
            }
        
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'wget', 'curl',
            'python-requests', 'bot', 'crawler', 'spider', 'scraper'
        ]
        
        ua_lower = user_agent.lower()
        
        for suspicious in suspicious_agents:
            if suspicious in ua_lower:
                return {
                    'is_suspicious': True,
                    'risk_score': 30,
                    'threat_type': 'suspicious_user_agent',
                    'reason': f'Suspicious User-Agent: {suspicious}'
                }
        
        # فحص User Agents غير طبيعية
        if len(user_agent) < 10 or len(user_agent) > 500:
            return {
                'is_suspicious': True,
                'risk_score': 15,
                'reason': 'Unusual User-Agent length'
            }
        
        return {'is_suspicious': False, 'risk_score': 0}
    
    def _analyze_request_patterns(self, request_data: Dict) -> Dict:
        """تحليل أنماط الطلبات للكشف عن الهجمات"""
        
        ip_address = request_data.get('ip_address', '')
        current_time = time.time()
        
        # عداد الطلبات لكل IP
        cache_key = f'request_count_{ip_address}'
        request_times = cache.get(cache_key, [])
        
        # إضافة الوقت الحالي
        request_times.append(current_time)
        
        # إزالة الطلبات القديمة (أقدم من دقيقة)
        request_times = [t for t in request_times if current_time - t < 60]
        
        # حفظ في الـ cache
        cache.set(cache_key, request_times, 300)  # 5 دقائق
        
        # فحص معدل الطلبات
        requests_per_minute = len(request_times)
        
        if requests_per_minute > 60:  # أكثر من 60 طلب في الدقيقة
            return {
                'is_suspicious': True,
                'risk_score': 40,
                'threat_type': 'brute_force_attempt',
                'reason': f'High request rate: {requests_per_minute} requests/minute'
            }
        elif requests_per_minute > 30:
            return {
                'is_suspicious': True,
                'risk_score': 20,
                'threat_type': 'suspicious_activity',
                'reason': f'Elevated request rate: {requests_per_minute} requests/minute'
            }
        
        return {'is_suspicious': False, 'risk_score': 0}
    
    def _calculate_threat_level(self, risk_score: int) -> str:
        """حساب مستوى التهديد بناءً على النقاط"""
        
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'high'
        elif risk_score >= 30:
            return 'medium'
        else:
            return 'low'
    
    def _get_request_count(self, ip_address: str) -> int:
        """الحصول على عدد الطلبات من IP معين"""
        
        cache_key = f'request_count_{ip_address}'
        request_times = cache.get(cache_key, [])
        current_time = time.time()
        
        # إزالة الطلبات القديمة
        recent_requests = [t for t in request_times if current_time - t < 60]
        
        return len(recent_requests)
    
    def _get_ip_geolocation(self, ip_address: str) -> Optional[Dict]:
        """الحصول على الموقع الجغرافي لـ IP (اختياري)"""
        
        try:
            # يمكن استخدام خدمات مثل MaxMind أو IP-API
            # هذا مثال مبسط
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return None

class BehaviorAnalyzer:
    """محلل السلوك الأمني للمستخدمين"""
    
    def __init__(self):
        self.normal_behavior_cache = {}
        self.anomaly_threshold = 0.7
    
    def analyze_user_behavior(self, user_id: int, current_session: Dict) -> Dict:
        """تحليل سلوك المستخدم للكشف عن الأنشطة غير الطبيعية"""
        
        try:
            # جلب السلوك التاريخي للمستخدم
            historical_behavior = self._get_user_behavior_history(user_id)
            
            # تحليل أنماط مختلفة
            login_analysis = self._analyze_login_pattern(current_session, historical_behavior)
            location_analysis = self._analyze_location_pattern(current_session, historical_behavior)
            device_analysis = self._analyze_device_pattern(current_session, historical_behavior)
            time_analysis = self._analyze_time_pattern(current_session, historical_behavior)
            
            # حساب النقاط الإجمالية للشذوذ
            total_anomaly_score = (
                login_analysis['anomaly_score'] * 0.3 +
                location_analysis['anomaly_score'] * 0.25 +
                device_analysis['anomaly_score'] * 0.25 +
                time_analysis['anomaly_score'] * 0.2
            )
            
            # تحديد ما إذا كان السلوك مشبوهاً
            is_anomalous = total_anomaly_score > self.anomaly_threshold
            
            return {
                'user_id': user_id,
                'is_anomalous': is_anomalous,
                'total_anomaly_score': round(total_anomaly_score, 3),
                'analysis_details': {
                    'login_analysis': login_analysis,
                    'location_analysis': location_analysis,
                    'device_analysis': device_analysis,
                    'time_analysis': time_analysis
                },
                'risk_level': self._calculate_behavior_risk_level(total_anomaly_score),
                'recommendations': self._generate_security_recommendations(total_anomaly_score, is_anomalous),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            security_logger.error(f"Error in behavior analysis for user {user_id}: {str(e)}")
            return {
                'user_id': user_id,
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _get_user_behavior_history(self, user_id: int) -> Dict:
        """جلب السلوك التاريخي للمستخدم"""
        
        # في التطبيق الحقيقي، هذه البيانات تأتي من قاعدة البيانات
        # هنا نستخدم بيانات افتراضية
        
        cache_key = f'user_behavior_{user_id}'
        cached_behavior = cache.get(cache_key)
        
        if cached_behavior:
            return cached_behavior
        
        # بيانات افتراضية للتجربة
        behavior = {
            'typical_login_hours': [8, 9, 10, 14, 15, 16, 17, 18],
            'typical_locations': ['192.168.1.0/24'],  # شبكة محلية
            'typical_devices': ['Chrome 91.0', 'Firefox 89.0'],
            'typical_pages': ['/dashboard/', '/courses/', '/grades/'],
            'average_session_duration': 45,  # دقيقة
            'login_frequency': 1.2  # مرات في اليوم
        }
        
        cache.set(cache_key, behavior, 3600)  # ساعة واحدة
        return behavior
    
    def _analyze_login_pattern(self, current_session: Dict, historical: Dict) -> Dict:
        """تحليل نمط تسجيل الدخول"""
        
        current_hours = [datetime.now().hour]
        typical_hours = historical.get('typical_login_hours', [])
        
        # حساب مدى الاختلاف عن الأوقات المعتادة
        hour_match = any(abs(h - current_hours[0]) <= 2 for h in typical_hours)
        
        anomaly_score = 0.0 if hour_match else 0.8
        
        return {
            'anomaly_score': anomaly_score,
            'current_hour': current_hours[0],
            'typical_hours': typical_hours,
            'is_unusual_time': not hour_match
        }
    
    def _analyze_location_pattern(self, current_session: Dict, historical: Dict) -> Dict:
        """تحليل نمط الموقع الجغرافي"""
        
        current_ip = current_session.get('ip_address', '')
        typical_locations = historical.get('typical_locations', [])
        
        # فحص ما إذا كان الـ IP ضمن النطاقات المعتادة
        is_familiar_location = False
        
        try:
            current_ip_obj = ipaddress.ip_address(current_ip)
            for location in typical_locations:
                if '/' in location:  # CIDR notation
                    network = ipaddress.ip_network(location, strict=False)
                    if current_ip_obj in network:
                        is_familiar_location = True
                        break
                elif current_ip == location:
                    is_familiar_location = True
                    break
        except:
            pass
        
        anomaly_score = 0.2 if is_familiar_location else 0.9
        
        return {
            'anomaly_score': anomaly_score,
            'current_ip': current_ip,
            'is_familiar_location': is_familiar_location,
            'typical_locations': typical_locations
        }
    
    def _analyze_device_pattern(self, current_session: Dict, historical: Dict) -> Dict:
        """تحليل نمط الجهاز المستخدم"""
        
        current_user_agent = current_session.get('user_agent', '')
        typical_devices = historical.get('typical_devices', [])
        
        # استخراج معلومات المتصفح الأساسية
        browser_info = self._extract_browser_info(current_user_agent)
        
        # فحص التشابه مع الأجهزة المعتادة
        is_familiar_device = any(
            device.lower() in current_user_agent.lower() 
            for device in typical_devices
        )
        
        anomaly_score = 0.1 if is_familiar_device else 0.6
        
        return {
            'anomaly_score': anomaly_score,
            'current_device': browser_info,
            'is_familiar_device': is_familiar_device,
            'typical_devices': typical_devices
        }
    
    def _analyze_time_pattern(self, current_session: Dict, historical: Dict) -> Dict:
        """تحليل النمط الزمني للاستخدام"""
        
        current_time = datetime.now()
        
        # فحص ما إذا كان الوقت ضمن ساعات العمل الطبيعية
        is_business_hours = 8 <= current_time.hour <= 18
        is_weekend = current_time.weekday() >= 5
        
        # حساب درجة الشذوذ
        anomaly_score = 0.0
        
        if not is_business_hours:
            anomaly_score += 0.3
        
        if is_weekend:
            anomaly_score += 0.2
        
        return {
            'anomaly_score': min(anomaly_score, 1.0),
            'current_time': current_time.isoformat(),
            'is_business_hours': is_business_hours,
            'is_weekend': is_weekend
        }
    
    def _extract_browser_info(self, user_agent: str) -> str:
        """استخراج معلومات المتصفح من User Agent"""
        
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
        
        for browser in browsers:
            if browser.lower() in user_agent.lower():
                # محاولة استخراج رقم الإصدار
                version_match = re.search(f'{browser}/([0-9.]+)', user_agent, re.IGNORECASE)
                if version_match:
                    return f"{browser} {version_match.group(1)}"
                return browser
        
        return "Unknown Browser"
    
    def _calculate_behavior_risk_level(self, anomaly_score: float) -> str:
        """حساب مستوى مخاطر السلوك"""
        
        if anomaly_score >= 0.8:
            return 'critical'
        elif anomaly_score >= 0.6:
            return 'high'
        elif anomaly_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_security_recommendations(self, anomaly_score: float, is_anomalous: bool) -> List[str]:
        """إنتاج توصيات أمنية"""
        
        recommendations = []
        
        if is_anomalous:
            if anomaly_score >= 0.8:
                recommendations.extend([
                    'إجراء تحقق إضافي من هوية المستخدم',
                    'طلب تأكيد عبر البريد الإلكتروني أو الهاتف',
                    'تسجيل النشاط في سجل الأمان',
                    'إشعار فريق الأمان فوراً'
                ])
            elif anomaly_score >= 0.6:
                recommendations.extend([
                    'مراقبة إضافية لنشاط المستخدم',
                    'طلب إعادة تأكيد كلمة المرور',
                    'تسجيل النشاط في سجل المراقبة'
                ])
            else:
                recommendations.extend([
                    'مراقبة عادية مع تسجيل النشاط',
                    'إشعار المستخدم بالنشاط الجديد'
                ])
        
        return recommendations

# إنشاء مثيلات عامة
threat_detector = SecurityThreatDetector()
behavior_analyzer = BehaviorAnalyzer()