# تحسينات الأمان المقترحة
# Suggested Security Improvements
# Generated: 2025-11-02T20:39:33.762680

## إعدادات Django الآمنة
## Secure Django Settings

# في settings.py أو .env.production
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# مفتاح أمان جديد
SECRET_KEY = 'zIjb2FUdXJD3Ar3aAQsxGznW5p4aucdM4DU317Q-nJB3QGG3Nh8nXQ5WnA4lYadteo8'

# إعدادات HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# أمان Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# حماية إضافية
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

## إعدادات كلمات المرور المحسنة
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

## إعدادات Session محسنة
SESSION_COOKIE_AGE = 3600  # ساعة واحدة
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = 'university_sessionid'

## إعدادات CORS آمنة
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = False

## Middleware الأمان
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... باقي middleware
]
