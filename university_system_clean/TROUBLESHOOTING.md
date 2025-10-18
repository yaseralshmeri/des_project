# 🔧 دليل استكشاف الأخطاء وإصلاحها
## Troubleshooting Guide - University Management System

---

## 📋 جدول المحتويات | Table of Contents

1. [مشاكل التثبيت والإعداد](#installation-issues)
2. [مشاكل قاعدة البيانات](#database-issues)
3. [مشاكل الخادم والتشغيل](#server-issues)
4. [مشاكل API والمصادقة](#api-auth-issues)
5. [مشاكل Docker](#docker-issues)
6. [مشاكل الأداء](#performance-issues)
7. [مشاكل الأمان](#security-issues)
8. [الأخطاء الشائعة](#common-errors)

---

## 🛠️ مشاكل التثبيت والإعداد {#installation-issues}

### ❌ خطأ: ModuleNotFoundError

**المشكلة:**
```bash
ModuleNotFoundError: No module named 'django'
```

**الحلول:**
```bash
# تأكد من تفعيل البيئة الافتراضية
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# إعادة تثبيت المتطلبات
pip install -r requirements.txt
```

### ❌ خطأ: Permission Denied

**المشكلة:**
```bash
PermissionError: [Errno 13] Permission denied
```

**الحلول:**
```bash
# على Linux/Mac
sudo chown -R $USER:$USER .
chmod +x manage.py
chmod +x setup.py

# على Windows - تشغيل Terminal كمدير
```

### ❌ خطأ: SECRET_KEY Missing

**المشكلة:**
```bash
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty
```

**الحلول:**
```bash
# إنشاء ملف .env من النموذج
cp .env.example .env

# توليد مفتاح آمن جديد
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))" >> .env
```

---

## 🗄️ مشاكل قاعدة البيانات {#database-issues}

### ❌ خطأ: Database Connection Failed

**المشكلة:**
```bash
django.db.utils.OperationalError: could not connect to server
```

**الحلول:**

#### لـ PostgreSQL:
```bash
# تحقق من تشغيل PostgreSQL
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # Mac

# إعادة تشغيل الخدمة
sudo systemctl start postgresql  # Linux
brew services start postgresql  # Mac

# تحقق من إعدادات الاتصال في .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

#### لـ SQLite:
```bash
# تحقق من وجود مجلد قاعدة البيانات
mkdir -p db/
chmod 755 db/

# تحديث إعدادات قاعدة البيانات في .env
DATABASE_URL=sqlite:///db.sqlite3
```

### ❌ خطأ: Migration Issues

**المشكلة:**
```bash
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**الحلول:**
```bash
# إعادة إنشاء الهجرات
python manage.py makemigrations --empty appname
python manage.py makemigrations

# تطبيق الهجرات
python manage.py migrate --fake-initial

# في حالة التعقد الشديد - إعادة تعيين كاملة
python manage.py flush
rm -rf */migrations/
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 مشاكل الخادم والتشغيل {#server-issues}

### ❌ خطأ: Port Already in Use

**المشكلة:**
```bash
Error: That port is already in use.
```

**الحلول:**
```bash
# العثور على العملية المستخدمة للمنفذ
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# إيقاف العملية
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# أو استخدام منفذ مختلف
python manage.py runserver 8001
```

### ❌ خطأ: Static Files Not Found

**المشكلة:**
```bash
The view didn't return an HttpResponse object
Static files not loading
```

**الحلول:**
```bash
# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# تحقق من إعدادات STATIC في settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# في التطوير، تأكد من DEBUG=True
DEBUG = True
```

### ❌ خطأ: ALLOWED_HOSTS

**المشكلة:**
```bash
DisallowedHost: Invalid HTTP_HOST header
```

**الحلول:**
```bash
# تحديث ALLOWED_HOSTS في .env
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# أو في settings.py للتطوير
ALLOWED_HOSTS = ['*']  # للتطوير فقط!
```

---

## 🔐 مشاكل API والمصادقة {#api-auth-issues}

### ❌ خطأ: JWT Token Invalid

**المشكلة:**
```bash
Given token not valid for any token type
```

**الحلول:**
```bash
# تحقق من صحة الرمز المميز
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/token/verify/

# الحصول على رمز جديد
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"user","password":"pass"}' \
     http://localhost:8000/api/v1/token/
```

### ❌ خطأ: CORS Issues

**المشكلة:**
```bash
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**الحلول:**
```bash
# تحديث إعدادات CORS في .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# أو في settings.py للتطوير
CORS_ALLOW_ALL_ORIGINS = True  # للتطوير فقط!
```

### ❌ خطأ: API Documentation Not Loading

**المشكلة:**
```bash
404 Not Found: /api/docs/
```

**الحلول:**
```bash
# تحقق من تثبيت drf-yasg
pip install drf-yasg

# تأكد من وجودها في INSTALLED_APPS
'drf_yasg',

# إعادة تشغيل الخادم
python manage.py runserver
```

---

## 🐳 مشاكل Docker {#docker-issues}

### ❌ خطأ: Docker Build Failed

**المشكلة:**
```bash
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**الحلول:**
```bash
# مسح ذاكرة التخزين المؤقت لـ Docker
docker system prune -a

# بناء الصورة بدون ذاكرة تخزين مؤقت
docker-compose build --no-cache

# تحقق من ملف requirements.txt
cat requirements.txt | head -10
```

### ❌ خطأ: Database Container Not Ready

**المشكلة:**
```bash
django.db.utils.OperationalError: server closed the connection unexpectedly
```

**الحلول:**
```bash
# انتظار حتى تصبح قاعدة البيانات جاهزة
docker-compose up db redis  # تشغيل قاعدة البيانات أولاً
# انتظر 30 ثانية
docker-compose up web  # ثم تشغيل التطبيق

# أو استخدام docker-compose مع depends_on
version: '3.8'
services:
  web:
    depends_on:
      db:
        condition: service_healthy
```

### ❌ خطأ: Permission Issues in Container

**المشكلة:**
```bash
PermissionError: [Errno 13] Permission denied: '/app/logs'
```

**الحلول:**
```bash
# في Dockerfile، تأكد من الأذونات الصحيحة
RUN chown -R appuser:appuser /app
USER appuser

# أو على Host
sudo chown -R 1000:1000 ./logs ./media
```

---

## ⚡ مشاكل الأداء {#performance-issues}

### ❌ مشكلة: Slow Database Queries

**الأعراض:**
- استعلامات قاعدة البيانات بطيئة
- صفحات تحميل ببطء

**الحلول:**
```python
# في settings.py، تفعيل Django Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# إضافة فهارس لقاعدة البيانات
class Meta:
    indexes = [
        models.Index(fields=['student_id']),
        models.Index(fields=['course_id']),
    ]

# استخدام select_related و prefetch_related
students = Student.objects.select_related('user').prefetch_related('courses')
```

### ❌ مشكلة: High Memory Usage

**الحلول:**
```bash
# مراقبة استخدام الذاكرة
docker stats

# تحسين إعدادات Gunicorn
gunicorn --workers 2 --max-requests 1000 --preload university_system.wsgi:application

# تحسين إعدادات قاعدة البيانات
CONN_MAX_AGE = 600
CONN_HEALTH_CHECKS = True
```

---

## 🔒 مشاكل الأمان {#security-issues}

### ❌ تحذير: DEBUG=True in Production

**المشكلة:**
```bash
You're running in DEBUG mode in production!
```

**الحلول:**
```bash
# في .env
DEBUG=False

# تحديث ALLOWED_HOSTS
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# إعداد HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### ❌ تحذير: Default SECRET_KEY

**الحلول:**
```bash
# توليد مفتاح آمن جديد
python -c "import secrets; print(secrets.token_urlsafe(50))"

# تحديث .env
SECRET_KEY=your-new-secure-key
```

---

## 🚨 الأخطاء الشائعة {#common-errors}

### 1. ImproperlyConfigured

```bash
django.core.exceptions.ImproperlyConfigured: Set the DATABASE_URL environment variable
```

**الحل:**
```bash
# في .env
DATABASE_URL=sqlite:///db.sqlite3
```

### 2. TemplateDoesNotExist

```bash
django.template.TemplateDoesNotExist: base.html
```

**الحل:**
```python
# في settings.py
TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],
        # ...
    }
]
```

### 3. Static Files 404

```bash
GET /static/admin/css/base.css - 404
```

**الحل:**
```bash
python manage.py collectstatic --noinput
```

### 4. No such table

```bash
django.db.utils.OperationalError: no such table: django_session
```

**الحل:**
```bash
python manage.py migrate
```

---

## 🆘 الحصول على المساعدة

### 📊 جمع معلومات التشخيص

```bash
# معلومات النظام
python --version
django-admin --version

# حالة الخدمات
python manage.py check
python manage.py check --deploy

# سجلات مفصلة
python manage.py runserver --verbosity=2

# في Docker
docker-compose logs -f web
```

### 📞 طلب المساعدة

1. **GitHub Issues**: [رابط المشروع]
2. **البريد الإلكتروني**: support@university-system.com
3. **التوثيق**: راجع README.md أولاً

### 📝 معلومات مطلوبة عند الإبلاغ عن خطأ

- إصدار Python و Django
- نظام التشغيل
- رسالة الخطأ الكاملة
- خطوات إعادة الإنتاج
- ملف .env (بدون كلمات مرور!)
- سجلات الخادم

---

<div align="center">

**🔧 نأمل أن يساعدك هذا الدليل في حل المشاكل!**  
**Hope this guide helps you resolve issues!**

[⬆ العودة للأعلى | Back to Top](#-دليل-استكشاف-الأخطاء-وإصلاحها)

</div>