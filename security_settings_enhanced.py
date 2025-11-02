"""
إعدادات الأمان المحسنة - Enhanced Security Settings
تم إنشاؤها تلقائياً بواسطة نظام الأمان الموحد
Created: 2025-11-02T22:17:43.234532
"""

# Security Headers - رؤوس الأمان
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_HSTS_SECONDS = 31536000  # سنة كاملة
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Settings - إعدادات HTTPS
SECURE_SSL_REDIRECT = True  # فعّل في الإنتاج فقط
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session Security - أمان الجلسات
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # ساعة واحدة

# CSRF Protection - حماية CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Content Security Policy - سياسة أمان المحتوى
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'none'"]

# Password Security - أمان كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Rate Limiting - تحديد معدل الطلبات
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Logging Security - أمان السجلات
LOGGING_SECURITY = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Database Security - أمان قاعدة البيانات
DATABASES_SECURITY_OPTIONS = {
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
}

# Additional Security Settings - إعدادات أمان إضافية
SECURITY_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# تحذير: هذه الإعدادات مقترحة - اختبرها قبل التطبيق في الإنتاج
