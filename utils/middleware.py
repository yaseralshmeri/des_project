"""
Advanced Middleware for Security, Activity Tracking, and Performance
وسائط متطورة للأمان وتتبع النشاط والأداء
"""
import time
import json
import logging
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from admin_control.models import UserActivity, SystemAlert, MaintenanceMode
from roles_permissions.models import AccessLog, SessionManager
import ipaddress

User = get_user_model()
logger = logging.getLogger(__name__)


class ActivityTrackingMiddleware:
    """
    Track all user activities in the system
    تتبع جميع أنشطة المستخدمين في النظام
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip tracking for certain paths
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/health/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # Track request start time
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Track activity if user is authenticated
        if request.user and not isinstance(request.user, AnonymousUser):
            try:
                self.log_activity(request, response, start_time)
            except Exception as e:
                logger.error(f"Error logging activity: {e}")
        
        return response
    
    def log_activity(self, request, response, start_time):
        """Log user activity"""
        action = self.determine_action(request.method, request.path, response.status_code)
        
        # Get IP address
        ip_address = self.get_client_ip(request)
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:1000]
        
        # Determine model and object from URL
        model_name, object_id = self.extract_model_info(request.path)
        
        # Create activity log
        try:
            with transaction.atomic():
                UserActivity.objects.create(
                    user=request.user,
                    action=action,
                    model_name=model_name,
                    object_id=str(object_id) if object_id else '',
                    description=f"{action} {request.path}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_key=request.session.session_key or ''
                )
        except Exception as e:
            logger.error(f"Failed to create activity log: {e}")
    
    def determine_action(self, method, path, status_code):
        """Determine action type based on HTTP method and path"""
        if method == 'GET':
            return 'VIEW'
        elif method == 'POST':
            if 'login' in path:
                return 'LOGIN'
            elif 'logout' in path:
                return 'LOGOUT'
            return 'CREATE'
        elif method == 'PUT' or method == 'PATCH':
            return 'UPDATE'
        elif method == 'DELETE':
            return 'DELETE'
        else:
            return 'VIEW'
    
    def extract_model_info(self, path):
        """Extract model name and object ID from URL path"""
        path_parts = path.strip('/').split('/')
        model_name = ''
        object_id = None
        
        # Try to identify model from URL patterns
        if len(path_parts) >= 2:
            if path_parts[0] in ['api']:
                model_name = path_parts[1] if len(path_parts) > 1 else ''
                if len(path_parts) > 2 and path_parts[2].isdigit():
                    object_id = int(path_parts[2])
            else:
                model_name = path_parts[0]
                if len(path_parts) > 1 and path_parts[1].isdigit():
                    object_id = int(path_parts[1])
        
        return model_name, object_id
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceModeMiddleware:
    """
    Handle system maintenance mode
    التعامل مع وضع صيانة النظام
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if maintenance mode is enabled
        maintenance = cache.get('maintenance_mode')
        if maintenance is None:
            try:
                maintenance = MaintenanceMode.objects.first()
                cache.set('maintenance_mode', maintenance, 300)  # Cache for 5 minutes
            except:
                maintenance = None
        
        if maintenance and maintenance.is_enabled:
            # Check if user is allowed during maintenance
            if self.is_user_allowed(request, maintenance):
                return self.get_response(request)
            
            # Check if IP is allowed
            client_ip = self.get_client_ip(request)
            if client_ip in maintenance.get_allowed_ips_list():
                return self.get_response(request)
            
            # Return maintenance page
            return self.render_maintenance_page(maintenance)
        
        return self.get_response(request)
    
    def is_user_allowed(self, request, maintenance):
        """Check if user is allowed during maintenance"""
        if request.user and not isinstance(request.user, AnonymousUser):
            return maintenance.allowed_users.filter(id=request.user.id).exists()
        return False
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def render_maintenance_page(self, maintenance):
        """Render maintenance mode page"""
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>النظام تحت الصيانة</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    color: white;
                }}
                .container {{
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 3rem;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    max-width: 600px;
                    margin: 2rem;
                }}
                h1 {{
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                    color: #fff;
                }}
                p {{
                    font-size: 1.2rem;
                    line-height: 1.6;
                    margin-bottom: 1.5rem;
                    color: #f0f0f0;
                }}
                .icon {{
                    font-size: 4rem;
                    margin-bottom: 2rem;
                }}
                .estimated-time {{
                    background: rgba(255, 255, 255, 0.2);
                    padding: 1rem;
                    border-radius: 10px;
                    margin-top: 2rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🔧</div>
                <h1>{maintenance.title}</h1>
                <p>{maintenance.message}</p>
                {'<div class="estimated-time"><strong>الوقت المتوقع للانتهاء:</strong><br>' + str(maintenance.estimated_completion) + '</div>' if maintenance.estimated_completion else ''}
                <p>نعتذر عن أي إزعاج قد يسببه هذا.</p>
            </div>
        </body>
        </html>
        """
        return JsonResponse({
            'status': 'maintenance',
            'message': maintenance.message,
            'estimated_completion': maintenance.estimated_completion
        }, status=503)


class SecurityMiddleware:
    """
    Enhanced security middleware
    وسائط أمان محسنة
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            'union select', 'drop table', 'insert into', 'delete from',
            'script>', '<iframe', 'javascript:', 'vbscript:',
            '../', '..\\', 'passwd', 'shadow', 'cmd.exe'
        ]
    
    def __call__(self, request):
        # Check for suspicious activity
        if self.is_suspicious_request(request):
            self.log_security_event(request, 'SUSPICIOUS_REQUEST')
            return HttpResponseForbidden('Suspicious activity detected')
        
        # Check rate limiting
        if self.is_rate_limited(request):
            self.log_security_event(request, 'RATE_LIMIT_EXCEEDED')
            return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
        
        # Process request
        response = self.get_response(request)
        
        # Add security headers
        response = self.add_security_headers(response)
        
        return response
    
    def is_suspicious_request(self, request):
        """Check for suspicious request patterns"""
        # Check query parameters
        query_string = request.META.get('QUERY_STRING', '').lower()
        for pattern in self.suspicious_patterns:
            if pattern in query_string:
                return True
        
        # Check POST data
        if hasattr(request, 'body'):
            try:
                body = request.body.decode('utf-8').lower()
                for pattern in self.suspicious_patterns:
                    if pattern in body:
                        return True
            except:
                pass
        
        # Check user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['sqlmap', 'nmap', 'nikto', 'dirb', 'burp']
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        return False
    
    def is_rate_limited(self, request):
        """Check if request should be rate limited"""
        if not request.user or isinstance(request.user, AnonymousUser):
            # Rate limit anonymous users more strictly
            cache_key = f"rate_limit_anon_{self.get_client_ip(request)}"
            request_count = cache.get(cache_key, 0)
            if request_count > 60:  # 60 requests per minute for anonymous
                return True
            cache.set(cache_key, request_count + 1, 60)
        else:
            # Rate limit authenticated users
            cache_key = f"rate_limit_user_{request.user.id}"
            request_count = cache.get(cache_key, 0)
            if request_count > 300:  # 300 requests per minute for authenticated
                return True
            cache.set(cache_key, request_count + 1, 60)
        
        return False
    
    def log_security_event(self, request, event_type):
        """Log security events"""
        try:
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create security alert
            SystemAlert.objects.create(
                title=f"Security Event: {event_type}",
                message=f"Suspicious activity detected from IP {ip_address}",
                severity='HIGH',
                alert_type='SECURITY'
            )
            
            # Log access attempt
            if request.user and not isinstance(request.user, AnonymousUser):
                AccessLog.objects.create(
                    user=request.user,
                    access_type='DENIED_ACCESS',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_path=request.path,
                    request_method=request.method,
                    access_granted=False,
                    denial_reason=event_type
                )
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionSecurityMiddleware:
    """
    Enhanced session security
    أمان الجلسات المحسن
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Track session for authenticated users
        if request.user and not isinstance(request.user, AnonymousUser):
            self.update_session_tracking(request)
        
        response = self.get_response(request)
        return response
    
    def update_session_tracking(self, request):
        """Update session tracking information"""
        try:
            session_key = request.session.session_key
            if not session_key:
                return
            
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Get or create session manager record
            session_manager, created = SessionManager.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'user': request.user,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'device_fingerprint': self.generate_device_fingerprint(request),
                }
            )
            
            if not created:
                # Update last activity
                session_manager.last_activity = timezone.now()
                
                # Check for session hijacking
                if session_manager.ip_address != ip_address:
                    self.handle_suspicious_session(request, session_manager)
                    return
                
                session_manager.save()
            
        except Exception as e:
            logger.error(f"Failed to update session tracking: {e}")
    
    def generate_device_fingerprint(self, request):
        """Generate a simple device fingerprint"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
        fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}"
        
        import hashlib
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def handle_suspicious_session(self, request, session_manager):
        """Handle potentially hijacked session"""
        try:
            # Log security event
            ip_address = self.get_client_ip(request)
            
            SystemAlert.objects.create(
                title="Potential Session Hijacking",
                message=f"User {request.user.username} session accessed from different IP: {ip_address} (original: {session_manager.ip_address})",
                severity='CRITICAL',
                alert_type='SECURITY'
            )
            
            # Terminate the session
            session_manager.terminate_session()
            
            # Force logout
            from django.contrib.auth import logout
            logout(request)
            
        except Exception as e:
            logger.error(f"Failed to handle suspicious session: {e}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware:
    """
    Monitor application performance
    مراقبة أداء التطبيق
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log slow requests
        if response_time > 2.0:  # Requests taking more than 2 seconds
            self.log_slow_request(request, response_time)
        
        # Add performance headers
        response['X-Response-Time'] = f"{response_time:.3f}s"
        
        return response
    
    def log_slow_request(self, request, response_time):
        """Log slow requests for performance monitoring"""
        try:
            logger.warning(
                f"Slow request detected: {request.method} {request.path} "
                f"took {response_time:.3f} seconds"
            )
            
            # You could also store this in the database for analysis
            from admin_control.models import SystemMetrics
            SystemMetrics.objects.create(
                metric_name='slow_request_time',
                metric_value=response_time,
                unit='seconds',
                category='performance'
            )
            
        except Exception as e:
            logger.error(f"Failed to log slow request: {e}")


class APIVersioningMiddleware:
    """
    Handle API versioning
    التعامل مع إصدارات API
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this is an API request
        if request.path.startswith('/api/'):
            # Extract version from URL or header
            version = self.get_api_version(request)
            request.api_version = version
            
            # Check if version is supported
            if not self.is_version_supported(version):
                return JsonResponse({
                    'error': 'Unsupported API version',
                    'version': version,
                    'supported_versions': ['v1', 'v2']
                }, status=400)
        
        return self.get_response(request)
    
    def get_api_version(self, request):
        """Extract API version from request"""
        # Try to get from URL path
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) > 1 and path_parts[1].startswith('v'):
            return path_parts[1]
        
        # Try to get from header
        version = request.META.get('HTTP_API_VERSION')
        if version:
            return version
        
        # Default to v1
        return 'v1'
    
    def is_version_supported(self, version):
        """Check if API version is supported"""
        supported_versions = ['v1', 'v2']
        return version in supported_versions