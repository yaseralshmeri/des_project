"""
Django Settings for University Management System - ENHANCED SECURE VERSION
إعدادات Django محسنة وآمنة لنظام إدارة الجامعة
Created: 2024-11-02
Version: Enhanced Security Edition
"""

from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import dj_database_url
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# =============================================================================
# SECURITY SETTINGS - إعدادات الأمان المحسنة
# =============================================================================

# Secret Key - مفتاح آمن مُحدث
SECRET_KEY = config('SECRET_KEY', default='0VTU-zPxmkNEXv-1pGiE7bk1yJjRBcmPbFEejkneuVMZ7DyR4rMGE5cCkR_Zmy3XtkmovNQ_2Obmrxt7Z7rrCA')

# Debug Mode - وضع التطوير
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed Hosts - النطاقات المسموحة
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'], cast=Csv())

# Security Headers - محسنة وآمنة
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Content Security Policy
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'", "https://fonts.gstatic.com"]

# =============================================================================
# INSTALLED APPS - التطبيقات المحسنة
# =============================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'corsheaders',
    'django_filters',
    'django_extensions',
]

LOCAL_APPS = [
    'students',
    'courses',
    'academic',
    'finance',
    'hr',
    'reports',
    'notifications',
    'ai',
    'smart_ai',
    'cyber_security',
    'attendance_qr',
    'admin_control',
    'roles_permissions',
    'web',
    'mobile_app',
    'management',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE - محسن للأمان والأداء
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# إضافة Rate Limiting في الإنتاج
if not DEBUG:
    MIDDLEWARE.insert(2, 'django_ratelimit.middleware.RatelimitMiddleware')

# =============================================================================
# URL & ROUTING CONFIGURATION
# =============================================================================

ROOT_URLCONF = 'urls'

# =============================================================================
# TEMPLATES CONFIGURATION - محسن
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'templates' / 'web',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
            # تحسينات أمان القوالب
            'string_if_invalid': '' if not DEBUG else 'INVALID_VARIABLE:%s',
        },
    },
]

# =============================================================================
# WSGI/ASGI CONFIGURATION
# =============================================================================

WSGI_APPLICATION = 'university_system.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION - محسنة للأداء والأمان
# =============================================================================

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Database Security Settings
DATABASES['default']['OPTIONS'] = {
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
} if 'mysql' in DATABASES['default']['ENGINE'] else {}

# =============================================================================
# AUTHENTICATION CONFIGURATION - محسن للأمان
# =============================================================================

AUTH_USER_MODEL = 'students.User'
LOGIN_URL = '/web/login/'
LOGIN_REDIRECT_URL = '/web/dashboard/'
LOGOUT_REDIRECT_URL = '/web/'

# Session Security
SESSION_COOKIE_NAME = 'university_sessionid'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 28800  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Protection
CSRF_COOKIE_NAME = 'university_csrftoken'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True

# =============================================================================
# PASSWORD VALIDATION - محسن وقوي
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # زيادة الحد الأدنى
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# INTERNATIONALIZATION & LOCALIZATION
# =============================================================================

LANGUAGE_CODE = 'ar'
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =============================================================================
# STATIC FILES CONFIGURATION - محسن للأداء
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Whitenoise Configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# =============================================================================
# MEDIA FILES CONFIGURATION - آمن
# =============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Allowed file types for uploads
ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.xls', '.xlsx']

# =============================================================================
# DEFAULT AUTO FIELD
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION - محسن
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer' if DEBUG else 'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# =============================================================================
# JWT CONFIGURATION - آمن ومحسن
# =============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # مدة أقصر
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),     # مدة أقصر
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'university-system',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# =============================================================================
# CORS CONFIGURATION - آمن
# =============================================================================

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default=[], cast=Csv())

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =============================================================================
# CACHE CONFIGURATION - محسن للأداء
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' if DEBUG else 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1') if not DEBUG else '',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        } if not DEBUG else {},
        'KEY_PREFIX': 'university',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Cache for sessions in production
if not DEBUG:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# EMAIL CONFIGURATION - محسن وآمن
# =============================================================================

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@university.edu')
    SERVER_EMAIL = config('SERVER_EMAIL', default='server@university.edu')

# Email Security
EMAIL_TIMEOUT = 10
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None

# =============================================================================
# LOGGING CONFIGURATION - محسن ومفصل
# =============================================================================

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'security': {
            'format': 'SECURITY {asctime} {levelname} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'security',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['error_file'],
    },
}

# =============================================================================
# API DOCUMENTATION (Swagger) - محسن
# =============================================================================

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
}

# =============================================================================
# CELERY CONFIGURATION - محسن للأداء
# =============================================================================

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery Security
CELERY_TASK_ALWAYS_EAGER = DEBUG  # Execute tasks synchronously in debug mode
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_LOG_COLOR = DEBUG

# =============================================================================
# CUSTOM UNIVERSITY SETTINGS - محسن
# =============================================================================

UNIVERSITY_NAME = config('UNIVERSITY_NAME', default='جامعة المستقبل')
UNIVERSITY_NAME_EN = config('UNIVERSITY_NAME_EN', default='Future University')
UNIVERSITY_CODE = config('UNIVERSITY_CODE', default='FU')
CURRENT_ACADEMIC_YEAR = config('CURRENT_ACADEMIC_YEAR', default='2024-2025')
CURRENT_SEMESTER = config('CURRENT_SEMESTER', default='1')

# Performance Settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000  # Reduced for security
DATA_UPLOAD_MAX_NUMBER_FILES = 5      # Reduced for security

# Localization Settings
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3
THOUSAND_SEPARATOR = ','
DECIMAL_SEPARATOR = '.'

# =============================================================================
# PRODUCTION SPECIFIC SETTINGS
# =============================================================================

if not DEBUG:
    # Error Reporting
    ADMINS = [('System Admin', config('ADMIN_EMAIL', default='admin@university.edu'))]
    MANAGERS = ADMINS
    
    # Security Enhancements
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    
    # Compression
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    
    # Database Connection Pooling
    DATABASES['default']['CONN_MAX_AGE'] = 600
    
# =============================================================================
# DEVELOPMENT SPECIFIC SETTINGS
# =============================================================================

if DEBUG:
    # Debug toolbar
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(-1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1', '::1', '0.0.0.0']
        
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
            'SHOW_COLLAPSED': True,
        }
    except ImportError:
        pass
    
    # Additional development logging
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    LOGGING['handlers']['console']['level'] = 'DEBUG'

# =============================================================================
# CUSTOM CONTEXT PROCESSORS
# =============================================================================

def university_context(request):
    """Add university information to all templates"""
    return {
        'UNIVERSITY_NAME': UNIVERSITY_NAME,
        'UNIVERSITY_NAME_EN': UNIVERSITY_NAME_EN,
        'UNIVERSITY_CODE': UNIVERSITY_CODE,
        'CURRENT_ACADEMIC_YEAR': CURRENT_ACADEMIC_YEAR,
        'CURRENT_SEMESTER': CURRENT_SEMESTER,
        'current_year': 2024,
        'is_production': not DEBUG,
    }

# Add custom context processor
TEMPLATES[0]['OPTIONS']['context_processors'].append(__name__ + '.university_context')

# =============================================================================
# HEALTH CHECKS & MONITORING
# =============================================================================

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,     # in MB
}

# =============================================================================
# RATE LIMITING
# =============================================================================

RATELIMIT_ENABLE = not DEBUG
RATELIMIT_USE_CACHE = 'default'

# API Rate Limits
API_THROTTLE_RATES = {
    'login': '5/min',
    'password_reset': '3/hour',
    'registration': '3/hour',
}

# =============================================================================
# BACKUP & MAINTENANCE
# =============================================================================

BACKUP_ENABLED = True
BACKUP_SCHEDULE = {
    'daily': True,
    'weekly': True,
    'monthly': True,
}

MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)

# =============================================================================
# MONITORING & ANALYTICS
# =============================================================================

# Sentry for error tracking (production only)
if not DEBUG and config('SENTRY_DSN', default=None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                monitor_celery_beat_tasks=True,
            ),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production' if not DEBUG else 'development',
    )

# =============================================================================
# FEATURE FLAGS
# =============================================================================

FEATURES = {
    'AI_RECOMMENDATIONS': True,
    'ADVANCED_SECURITY': True,
    'MOBILE_APP_API': True,
    'REAL_TIME_NOTIFICATIONS': True,
    'ADVANCED_REPORTS': True,
    'QR_ATTENDANCE': True,
    'FINANCIAL_MANAGEMENT': True,
}

print(f"🔧 إعدادات Django محملة - الوضع: {'تطوير' if DEBUG else 'إنتاج'}")