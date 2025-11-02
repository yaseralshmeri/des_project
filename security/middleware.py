
"""
Middleware للأمان المتطور
Advanced Security Middleware
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect
import re

class AdvancedSecurityMiddleware(MiddlewareMixin):
    """نظام الأمان المتطور"""
    
    def process_response(self, request, response):
        # إضافة رؤوس الأمان
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY', 
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        for header, value in security_headers.items():
            response[header] = value
        
        return response
    
    def process_request(self, request):
        # فحص محاولات الهجمات الشائعة
        suspicious_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'union.*select',  # SQL Injection  
            r'../../../',  # Directory Traversal
            r'eval\s*\(',  # Code Injection
        ]
        
        user_input = str(request.GET) + str(request.POST)
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                # تسجيل محاولة الهجوم
                print(f"⚠️ محاولة هجوم مشبوهة من {request.META.get('REMOTE_ADDR', 'Unknown')}")
                # يمكن إضافة منطق الحظر هنا
                break
        
        return None
