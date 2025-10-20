"""
Django Settings for University Management System - Enhanced Final Version
إعدادات موحدة ومُحسنة نهائية لنظام إدارة الجامعة

This is the unified, enhanced, and final settings file for the University Management System.
Features:
- Enhanced security configurations
- Performance optimizations
- Complete error handling
- Production-ready configurations
- Arabic and English support
"""

from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import dj_database_url
import os
import secrets
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# =============================================================================
# SECURITY SETTINGS - إعدادات الأمان المحسنة والمتقدمة
# =============================================================================

# Generate secure SECRET_KEY with validation
SECRET_KEY = config(
    'SECRET_KEY', 
    default='university-mgmt-system-2024-dev-key-' + secrets.token_urlsafe(32)
)

# Debug settings with validation
DEBUG = config('DEBUG', default=True, cast=bool)

# Environment detection
ENVIRONMENT = config('ENVIRONMENT', default='development').lower()
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_STAGING = ENVIRONMENT == 'staging'
IS_DEVELOPMENT = ENVIRONMENT == 'development'

# Allowed hosts with secure defaults
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*', cast=Csv())

# Security Headers - Enhanced
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# HSTS Settings
if IS_PRODUCTION:
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# HTTPS Settings for Production
if IS_PRODUCTION or IS_STAGING:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Additional security settings
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SAMESITE = 'Strict'

# =============================================================================
# INSTALLED APPS - التطبيقات المُوحدة والمُحسنة
# =============================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # For better number formatting
]

THIRD_PARTY_APPS = [
    # API & Documentation
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'drf_spectacular',
    
    # Security & Performance
    'corsheaders',
    'django_filters',
    'django_extensions',
    'django_ratelimit',
    'csp',
    
    # Monitoring & Health
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    
    # Background Tasks
    'django_celery_beat',
    'django_celery_results',
    
    # Development Tools (only in development)
    *(['debug_toolbar'] if DEBUG else []),
]

LOCAL_APPS = [
    'students.apps.StudentsConfig',
    'courses.apps.CoursesConfig',
    'finance.apps.FinanceConfig',
    'hr.apps.HrConfig',
    'reports.apps.ReportsConfig',
    'academic.apps.AcademicConfig',
    'notifications.apps.NotificationsConfig',
    'ai.apps.AiConfig',
    'web.apps.WebConfig',
    'admin_control.apps.AdminControlConfig',
    'roles_permissions.apps.RolesPermissionsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE - الوسائط المُرتبة بعناية للأداء والأمان
# =============================================================================

MIDDLEWARE = [
    # Security middleware first
    'django.middleware.security.SecurityMiddleware',
    
    # Debug toolbar (development only)
    *(['debug_toolbar.middleware.DebugToolbarMiddleware'] if DEBUG else []),
    
    # Static files middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Session and CORS
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Localization
    'django.middleware.locale.LocaleMiddleware',
    
    # Common middleware
    'django.middleware.common.CommonMiddleware',
    
    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Messages
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # CSP (Content Security Policy)
    'csp.middleware.CSPMiddleware',
    
    # Custom middleware (if any)
    # 'path.to.custom.middleware.CustomMiddleware',
]

ROOT_URLCONF = 'university_system.urls'

# =============================================================================
# TEMPLATES - إعدادات القوالب المُحسنة
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'templates/admin',
            BASE_DIR / 'templates/student',
            BASE_DIR / 'templates/teacher',
            BASE_DIR / 'templates/staff',
            BASE_DIR / 'templates/web',
            BASE_DIR / 'templates/errors',
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
        },
    },
]

WSGI_APPLICATION = 'university_system.wsgi.application'

# =============================================================================
# DATABASE - إعداد قاعدة البيانات المُحسن
# =============================================================================

# Default database configuration
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Database optimization settings
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS'].update({
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4',
        'use_unicode': True,
    })

# =============================================================================
# AUTHENTICATION & AUTHORIZATION - المصادقة والصلاحيات
# =============================================================================

AUTH_USER_MODEL = 'students.User'

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

# Login/Logout URLs
LOGIN_URL = '/web/login/'
LOGIN_REDIRECT_URL = '/web/enhanced/dashboard/'
LOGOUT_REDIRECT_URL = '/web/enhanced/'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# =============================================================================
# REST FRAMEWORK & API SETTINGS - إعدادات API المُحسنة
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
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
    },
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# API Documentation Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'University Management System API',
    'DESCRIPTION': 'Complete API for University Management System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# =============================================================================
# INTERNATIONALIZATION - الدعم متعدد اللغات
# =============================================================================

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Additional language settings
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Number and date formatting
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = (3, 0)

# =============================================================================
# STATIC FILES & MEDIA - الملفات الثابتة والوسائط
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'web' / 'static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Static files compression and optimization
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# CACHING - التخزين المؤقت المُحسن
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'university_system',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Fallback to local memory cache if Redis is not available
try:
    import redis
    redis.Redis.from_url(CACHES['default']['LOCATION']).ping()
except:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'university_system_cache',
        }
    }

# Cache timeout settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'university_system'

# =============================================================================
# EMAIL CONFIGURATION - إعداد البريد الإلكتروني
# =============================================================================

EMAIL_BACKEND = config(
    'EMAIL_BACKEND', 
    default='django.core.mail.backends.console.EmailBackend'
)

if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', 
    default='noreply@university.edu'
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# =============================================================================
# LOGGING CONFIGURATION - إعداد السجلات المُحسن
# =============================================================================

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
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
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
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'university_system.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'university_system': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# =============================================================================
# CELERY CONFIGURATION - إعداد المهام الخلفية
# =============================================================================

# Celery settings
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery beat settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Task routing
CELERY_TASK_ROUTES = {
    'university_system.tasks.send_email': {'queue': 'email'},
    'university_system.tasks.generate_report': {'queue': 'reports'},
    'university_system.tasks.backup_database': {'queue': 'maintenance'},
}

# =============================================================================
# CORS SETTINGS - إعدادات CORS
# =============================================================================

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development

CORS_ALLOWED_HEADERS = [
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
# CONTENT SECURITY POLICY - سياسة أمان المحتوى
# =============================================================================

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.jsdelivr.net", "https://code.jquery.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'",)

# =============================================================================
# UNIVERSITY SPECIFIC SETTINGS - إعدادات خاصة بالجامعة
# =============================================================================

# University Information
UNIVERSITY_NAME = config('UNIVERSITY_NAME', default='جامعة المستقبل')
UNIVERSITY_NAME_EN = config('UNIVERSITY_NAME_EN', default='Future University')
UNIVERSITY_CODE = config('UNIVERSITY_CODE', default='FU')

# Academic Settings
CURRENT_ACADEMIC_YEAR = config('CURRENT_ACADEMIC_YEAR', default='2024-2025')
CURRENT_SEMESTER = config('CURRENT_SEMESTER', default='1')

# GPA Settings
GPA_SCALE = 4.0
PASSING_GRADE = 60.0

# Course Settings
MAX_CREDITS_PER_SEMESTER = 21
MIN_CREDITS_PER_SEMESTER = 12

# Fee Settings
LATE_PAYMENT_FEE = 100.0  # in the university's currency
CURRENCY_SYMBOL = 'ر.س'
CURRENCY_CODE = 'SAR'

# =============================================================================
# DEVELOPMENT SETTINGS - إعدادات التطوير
# =============================================================================

if DEBUG:
    # Debug toolbar settings
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Debug toolbar panels
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
    
    # Email backend for development
    if EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# PERFORMANCE SETTINGS - إعدادات الأداء
# =============================================================================

# Database connection pooling
if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 600

# Template caching
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# Session optimization
if not DEBUG:
    SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# MONITORING & ERROR TRACKING - المراقبة وتتبع الأخطاء
# =============================================================================

# Sentry configuration (if available)
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN and not DEBUG:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(
                    transaction_style='url',
                ),
                CeleryIntegration(
                    monitor_beat_tasks=True,
                ),
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
            environment=ENVIRONMENT,
            release=config('APP_VERSION', default='1.0.0'),
        )
    except ImportError:
        pass

# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CUSTOM SETTINGS VALIDATION
# =============================================================================

def validate_settings():
    """Validate critical settings"""
    errors = []
    
    # Check SECRET_KEY security
    if len(SECRET_KEY) < 50:
        errors.append("SECRET_KEY should be at least 50 characters long")
    
    if 'django-insecure' in SECRET_KEY and IS_PRODUCTION:
        errors.append("Using insecure SECRET_KEY in production")
    
    # Check database configuration
    if IS_PRODUCTION and 'sqlite' in DATABASES['default']['ENGINE']:
        errors.append("SQLite should not be used in production")
    
    # Check email configuration
    if IS_PRODUCTION and EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        errors.append("Console email backend should not be used in production")
    
    if errors:
        import sys
        print("⚠️  Configuration Warnings:")
        for error in errors:
            print(f"   - {error}")
        if IS_PRODUCTION:
            print("⚠️  Please fix these issues before deploying to production!")

# Run validation
validate_settings()

# =============================================================================
# FEATURE FLAGS - خيارات الميزات
# =============================================================================

FEATURE_FLAGS = {
    'ENABLE_AI_PREDICTIONS': config('ENABLE_AI_PREDICTIONS', default=True, cast=bool),
    'ENABLE_NOTIFICATIONS': config('ENABLE_NOTIFICATIONS', default=True, cast=bool),
    'ENABLE_ADVANCED_REPORTS': config('ENABLE_ADVANCED_REPORTS', default=True, cast=bool),
    'ENABLE_API_THROTTLING': config('ENABLE_API_THROTTLING', default=True, cast=bool),
    'ENABLE_AUDIT_LOGGING': config('ENABLE_AUDIT_LOGGING', default=True, cast=bool),
    'ENABLE_BACKUP_TASKS': config('ENABLE_BACKUP_TASKS', default=False, cast=bool),
}

print(f"🎓 University Management System - Configuration Loaded Successfully!")
print(f"📊 Environment: {ENVIRONMENT.upper()}")
print(f"🔒 Security: {'Enabled' if not DEBUG else 'Development Mode'}")
print(f"🏫 University: {UNIVERSITY_NAME} ({UNIVERSITY_CODE})")
print(f"📅 Academic Year: {CURRENT_ACADEMIC_YEAR}")