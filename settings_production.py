"""
Production Settings for University Management System
إعدادات الإنتاج لنظام إدارة الجامعة

This file contains all production-specific settings.
Use environment variables for sensitive information.
"""

from .settings import *
import os
from decouple import config

# =============================================================================
# PRODUCTION OVERRIDE SETTINGS
# =============================================================================

# Security - NEVER use DEBUG=True in production
DEBUG = False

# Allowed hosts - Update with your domain names
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='yourdomain.com,www.yourdomain.com,api.yourdomain.com',
    cast=Csv()
)

# Security Headers - Enhanced for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Additional security headers
X_FRAME_OPTIONS = 'DENY'
SECURE_FRAME_DENY = True

# =============================================================================
# DATABASE CONFIGURATION - Production
# =============================================================================

# Use PostgreSQL for production
DATABASES = {
    'default': dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default='postgresql://username:password@localhost:5432/university_db'
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Database connection pooling
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
}

# =============================================================================
# CACHE CONFIGURATION - Production Redis
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'TIMEOUT': 300,  # 5 minutes default timeout
        'VERSION': 1,
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour

# =============================================================================
# LOGGING CONFIGURATION - Production
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} - {message}',
            'style': '{',
        },
        'json': {
            '()': 'structlog.stdlib.ProcessorFormatter',
            'processor': 'structlog.dev.ConsoleRenderer',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/university_system.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/university_system_error.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins', 'sentry'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file', 'mail_admins', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'university_system': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'students': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'courses': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'academic': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# EMAIL CONFIGURATION - Production
# =============================================================================

EMAIL_BACKEND = 'django_anymail.backends.sendgrid.EmailBackend'

# Email settings with environment variables
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Email addresses
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@yourdomain.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='admin@yourdomain.com')
ADMINS = [
    ('System Admin', config('ADMIN_EMAIL', default='admin@yourdomain.com')),
]
MANAGERS = ADMINS

# =============================================================================
# STATIC AND MEDIA FILES - Production
# =============================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Optional: Use AWS S3 for static and media files
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Static files on S3
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files on S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# =============================================================================
# CELERY CONFIGURATION - Production
# =============================================================================

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')

# Celery optimization for production
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Task routing
CELERY_TASK_ROUTES = {
    'students.tasks.*': {'queue': 'students'},
    'courses.tasks.*': {'queue': 'courses'},
    'reports.tasks.*': {'queue': 'reports'},
    'notifications.tasks.*': {'queue': 'notifications'},
}

# Worker configuration
CELERY_WORKER_CONCURRENCY = config('CELERY_WORKER_CONCURRENCY', default=4, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# Task time limits
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600      # 10 minutes

# =============================================================================
# MONITORING AND ERROR TRACKING - Production
# =============================================================================

# Sentry configuration for error tracking
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            CeleryIntegration(monitor_beat_tasks=True),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config('ENVIRONMENT', default='production'),
        release=config('RELEASE_VERSION', default='1.0.0'),
    )

# =============================================================================
# API RATE LIMITING - Production
# =============================================================================

# Enhanced rate limiting for production
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# DRF Throttling
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '50/hour',      # Anonymous users
    'user': '500/hour',     # Authenticated users
    'student': '200/hour',  # Students
    'teacher': '300/hour',  # Teachers
    'admin': '1000/hour',   # Administrators
    'login': '10/hour',     # Login attempts
}

# =============================================================================
# CORS CONFIGURATION - Production
# =============================================================================

# CORS settings for production
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://yourdomain.com,https://www.yourdomain.com,https://api.yourdomain.com',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# =============================================================================
# PERFORMANCE OPTIMIZATIONS
# =============================================================================

# Database query optimization
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['OPTIONS'].update({
    'CONN_HEALTH_CHECKS': True,
    'AUTOCOMMIT': True,
})

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# BACKUP AND MAINTENANCE
# =============================================================================

# Backup settings
BACKUP_ENABLED = config('BACKUP_ENABLED', default=True, cast=bool)
BACKUP_RETENTION_DAYS = config('BACKUP_RETENTION_DAYS', default=30, cast=int)

# Maintenance mode
MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)

# =============================================================================
# CUSTOM PRODUCTION SETTINGS
# =============================================================================

# University specific settings for production
UNIVERSITY_NAME = config('UNIVERSITY_NAME', default='جامعة المستقبل')
UNIVERSITY_NAME_EN = config('UNIVERSITY_NAME_EN', default='Future University')
UNIVERSITY_CODE = config('UNIVERSITY_CODE', default='FU')
UNIVERSITY_DOMAIN = config('UNIVERSITY_DOMAIN', default='yourdomain.com')

# Academic year settings
CURRENT_ACADEMIC_YEAR = config('CURRENT_ACADEMIC_YEAR', default='2024-2025')
CURRENT_SEMESTER = config('CURRENT_SEMESTER', default='1')

# System limits
MAX_STUDENTS_PER_COURSE = config('MAX_STUDENTS_PER_COURSE', default=50, cast=int)
MAX_COURSES_PER_STUDENT = config('MAX_COURSES_PER_STUDENT', default=8, cast=int)

# Feature flags
ENABLE_AI_FEATURES = config('ENABLE_AI_FEATURES', default=True, cast=bool)
ENABLE_NOTIFICATIONS = config('ENABLE_NOTIFICATIONS', default=True, cast=bool)
ENABLE_REPORTS = config('ENABLE_REPORTS', default=True, cast=bool)

print("🚀 Production settings loaded successfully!")