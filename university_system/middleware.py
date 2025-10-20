"""
Custom Middleware for University Management System
وسائط مخصصة لنظام إدارة الجامعة

This file contains custom middleware classes for enhanced functionality,
security, logging, and performance monitoring.
"""

import json
import time
import logging
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
User = get_user_model()


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Enhanced security headers middleware
    وسائط رؤوس الأمان المحسنة
    """
    
    def process_response(self, request, response):
        """Add security headers to all responses"""
        
        # Enhanced security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }
        
        # Add HSTS headers for HTTPS
        if request.is_secure():
            security_headers.update({
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            })
        
        # Add CSP header for enhanced security
        if not settings.DEBUG:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net",
                "img-src 'self' data: https:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'"
            ]
            security_headers['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Apply headers
        for header, value in security_headers.items():
            response[header] = value
        
        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Performance monitoring and logging middleware
    وسائط مراقبة الأداء والتسجيل
    """
    
    def process_request(self, request):
        """Start timing the request"""
        request.start_time = time.time()
        request.start_timestamp = timezone.now()
        
        # Log request details
        if settings.DEBUG:
            logger.info(f"Request started: {request.method} {request.path}")
    
    def process_response(self, request, response):
        """Log response time and details"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Add performance headers
            response['X-Response-Time'] = f"{duration:.3f}s"
            response['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
            
            # Log slow requests
            if duration > 2.0:  # Log requests taking more than 2 seconds
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.3f}s - Status: {response.status_code}"
                )
            
            # Log to cache for monitoring
            if hasattr(request, 'user') and request.user.is_authenticated:
                cache_key = f"perf_{request.user.id}_{int(time.time() // 300)}"  # 5-minute buckets
                performance_data = cache.get(cache_key, [])
                performance_data.append({
                    'path': request.path,
                    'method': request.method,
                    'duration': duration,
                    'status': response.status_code,
                    'timestamp': request.start_timestamp.isoformat()
                })
                cache.set(cache_key, performance_data, 600)  # Keep for 10 minutes
        
        return response


class UserActivityMiddleware(MiddlewareMixin):
    """
    Track user activity and last seen status
    تتبع نشاط المستخدم وآخر ظهور
    """
    
    def process_request(self, request):
        """Track user activity"""
        if request.user.is_authenticated:
            # Update last activity
            cache_key = f"user_activity_{request.user.id}"
            activity_data = {
                'last_seen': timezone.now().isoformat(),
                'last_path': request.path,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
            }
            cache.set(cache_key, activity_data, 3600)  # Keep for 1 hour
            
            # Update user model (less frequently)
            last_update_key = f"user_last_update_{request.user.id}"
            if not cache.get(last_update_key):
                try:
                    User.objects.filter(id=request.user.id).update(last_login=timezone.now())
                    cache.set(last_update_key, True, 300)  # Update max once per 5 minutes
                except Exception as e:
                    logger.error(f"Error updating user last_login: {e}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting for API endpoints
    تحديد معدل الطلبات لنقاط API
    """
    
    def process_request(self, request):
        """Check rate limits for API requests"""
        if not request.path.startswith('/api/'):
            return None
        
        # Get client identifier
        if request.user.is_authenticated:
            client_id = f"user_{request.user.id}"
            rate_limit = 1000  # 1000 requests per hour for authenticated users
        else:
            client_id = f"ip_{self.get_client_ip(request)}"
            rate_limit = 100   # 100 requests per hour for anonymous users
        
        # Check rate limit
        cache_key = f"rate_limit_{client_id}_{int(time.time() // 3600)}"  # Per hour
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= rate_limit:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 3600 - (int(time.time()) % 3600)
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 3600)
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Comprehensive request logging middleware
    وسائط تسجيل الطلبات الشاملة
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_headers = {
            'HTTP_AUTHORIZATION', 'HTTP_COOKIE', 'HTTP_X_CSRF_TOKEN'
        }
        super().__init__(get_response)
    
    def process_request(self, request):
        """Log incoming requests"""
        # Generate request ID
        request.request_id = f"{int(time.time() * 1000000)}"
        
        # Prepare log data
        log_data = {
            'request_id': request.request_id,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'timestamp': timezone.now().isoformat()
        }
        
        # Log POST data (excluding sensitive data)
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                post_data = json.loads(request.body.decode('utf-8'))
                # Remove sensitive fields
                sanitized_data = self.sanitize_data(post_data)
                log_data['post_data'] = sanitized_data
            except (json.JSONDecodeError, UnicodeDecodeError):
                log_data['post_data'] = 'Invalid JSON or binary data'
        
        # Log headers (excluding sensitive ones)
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_') and key not in self.sensitive_headers:
                headers[key] = value[:200]  # Truncate long headers
        log_data['headers'] = headers
        
        logger.info(f"Request: {json.dumps(log_data, ensure_ascii=False)}")
    
    def process_response(self, request, response):
        """Log response details"""
        if hasattr(request, 'request_id'):
            log_data = {
                'request_id': request.request_id,
                'status_code': response.status_code,
                'content_type': response.get('Content-Type', 'unknown'),
                'content_length': len(response.content) if hasattr(response, 'content') else 0
            }
            
            # Log error responses
            if response.status_code >= 400:
                log_data['error'] = True
                if hasattr(response, 'content') and response.content:
                    try:
                        content = response.content.decode('utf-8')[:500]
                        log_data['response_content'] = content
                    except UnicodeDecodeError:
                        log_data['response_content'] = 'Binary content'
            
            logger.info(f"Response: {json.dumps(log_data, ensure_ascii=False)}")
        
        return response
    
    def sanitize_data(self, data):
        """Remove sensitive data from logs"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['password', 'token', 'secret', 'key', 'authorization']:
                    sanitized[key] = '***REDACTED***'
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self.sanitize_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        else:
            return data
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Maintenance mode middleware
    وسائط وضع الصيانة
    """
    
    def process_request(self, request):
        """Check if system is in maintenance mode"""
        maintenance_mode = cache.get('maintenance_mode', False)
        
        if maintenance_mode:
            # Allow access to admin and certain paths
            allowed_paths = ['/admin/', '/health/', '/api/health/']
            allowed_users = []
            
            # Allow superusers
            if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
                return None
            
            # Check if path is allowed
            if any(request.path.startswith(path) for path in allowed_paths):
                return None
            
            # Return maintenance page
            maintenance_message = cache.get('maintenance_message', 'System is under maintenance. Please try again later.')
            
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Maintenance mode',
                    'message': maintenance_message,
                    'status': 'maintenance'
                }, status=503)
            else:
                # Return HTML maintenance page
                from django.template.response import TemplateResponse
                return TemplateResponse(request, 'errors/maintenance.html', {
                    'message': maintenance_message
                }, status=503)
        
        return None


class HealthCheckMiddleware(MiddlewareMixin):
    """
    System health monitoring middleware
    وسائط مراقبة صحة النظام
    """
    
    def process_request(self, request):
        """Monitor system health"""
        # Check database connection
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            cache.set('system_health_db', False, 60)
        else:
            cache.set('system_health_db', True, 60)
        
        # Check cache connection
        try:
            cache.set('health_check_cache', 'ok', 30)
            cache_status = cache.get('health_check_cache') == 'ok'
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            cache_status = False
        
        cache.set('system_health_cache', cache_status, 60)
        
        return None


# Utility functions for middleware
def enable_maintenance_mode(message="System is under maintenance"):
    """Enable maintenance mode"""
    cache.set('maintenance_mode', True, None)  # No expiration
    cache.set('maintenance_message', message, None)
    logger.info("Maintenance mode enabled")


def disable_maintenance_mode():
    """Disable maintenance mode"""
    cache.delete('maintenance_mode')
    cache.delete('maintenance_message')
    logger.info("Maintenance mode disabled")


def get_system_health():
    """Get system health status"""
    return {
        'database': cache.get('system_health_db', True),
        'cache': cache.get('system_health_cache', True),
        'maintenance_mode': cache.get('maintenance_mode', False),
        'timestamp': timezone.now().isoformat()
    }


def get_user_activity(user_id):
    """Get user activity data"""
    cache_key = f"user_activity_{user_id}"
    return cache.get(cache_key, {})


def get_performance_stats(user_id=None, time_window=300):
    """Get performance statistics"""
    if user_id:
        cache_key = f"perf_{user_id}_{int(time.time() // time_window)}"
        return cache.get(cache_key, [])
    else:
        # Aggregate stats for all users (implement as needed)
        return []