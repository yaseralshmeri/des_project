# 🚀 دليل التشغيل السريع - نظام إدارة الجامعة الذكي المتقدم
## Quick Start Guide - Advanced Smart University Management System

**الإصدار**: 2.0.0 Advanced Edition  
**تاريخ التحديث**: 2025-10-20

---

## ⚡ التشغيل السريع (5 دقائق)

### 1. المتطلبات الأساسية
```bash
# تثبيت Python 3.11+
python --version  # يجب أن يكون 3.11 أو أحدث

# تثبيت Node.js 18+ (للواجهات الحديثة)
node --version    # يجب أن يكون 18 أو أحدث

# تثبيت PostgreSQL 15+ (اختياري - SQLite متضمن)
psql --version    # اختياري للإنتاج

# تثبيت Redis (للتخزين المؤقت)
redis-server --version  # مطلوب للأداء الأمثل
```

### 2. تثبيت وتشغيل النظام
```bash
# 1. استنساخ المشروع
git clone https://github.com/yaseralshmeri/des_project.git
cd des_project

# 2. إنشاء البيئة الافتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو venv\Scripts\activate  # Windows

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. إعداد قاعدة البيانات
python manage.py migrate

# 5. إنشاء مستخدم مدير
python manage.py createsuperuser

# 6. تشغيل النظام
python manage.py runserver
```

### 3. الوصول للنظام
```
🌐 الواجهة الرئيسية: http://localhost:8000
👨‍💼 لوحة الإدارة: http://localhost:8000/admin
📚 توثيق API: http://localhost:8000/api/docs
🔒 لوحة الأمان: http://localhost:8000/api/v1/cyber-security/dashboard
🤖 الذكاء الاصطناعي: http://localhost:8000/api/v1/smart-ai
```

---

## 🎯 الميزات الجديدة المتقدمة

### 1. الذكاء الاصطناعي المدمج 🧠

#### أ. المساعد الذكي
```python
# استخدام المساعد الذكي
POST /api/v1/smart-ai/assistant/
{
    "message": "ما هي درجاتي الأخيرة؟",
    "chat_type": "student_support"
}

# الرد المتوقع
{
    "response": "إليك درجاتك الأخيرة:\n• الرياضيات: 85/100\n• الفيزياء: 92/100\n...",
    "confidence": 0.9,
    "suggestions": ["عرض تفاصيل المقررات", "نصائح لتحسين الدرجات"]
}
```

#### ب. التنبؤ بالأداء
```python
# التنبؤ بأداء الطالب
POST /api/v1/smart-ai/predict-performance/
{
    "student_id": 123,
    "course_id": 456,
    "attendance_rate": 85.0,
    "assignment_completion": 90.0
}

# النتيجة
{
    "predicted_grade": 87.5,
    "letter_grade": "B+",
    "success_probability": 89.2,
    "risk_level": "low",
    "recommendations": [...]
}
```

#### ج. التوصيات الذكية
```python
# الحصول على توصيات مخصصة
GET /api/v1/smart-ai/recommendations/

# الاستجابة
{
    "recommendations": [
        {
            "type": "course_selection",
            "title": "مقررات موصى بها",
            "priority_score": 85,
            "recommended_items": ["CS301", "MATH201"]
        }
    ]
}
```

### 2. الأمان السيبراني المتطور 🔒

#### أ. مراقبة التهديدات
```python
# لوحة تحكم الأمان
GET /api/v1/cyber-security/dashboard/

{
    "total_events": 1247,
    "critical_events": 3,
    "recent_events": 45,
    "threat_stats": [
        {"event_type": "sql_injection", "count": 12},
        {"event_type": "brute_force", "count": 8}
    ]
}
```

#### ب. تحليل السلوك
```python
# تحليل سلوك مستخدم معين
GET /api/v1/cyber-security/behavior-analysis/

{
    "suspicious_users": [
        {
            "user_id": 789,
            "username": "student123",
            "risk_score": 0.75,
            "anomaly_score": 0.68
        }
    ]
}
```

### 3. نظام الحضور الذكي 📱

#### أ. إنشاء جلسة حضور
```python
# إنشاء جلسة حضور جديدة
POST /api/v1/attendance/create-session/
{
    "course_id": 101,
    "session_name": "محاضرة الرياضيات - الأسبوع 5",
    "start_time": "08:00",
    "end_time": "09:30",
    "location_required": true,
    "qr_valid_duration": 15
}
```

#### ب. مسح QR Code
```python
# تسجيل الحضور عبر QR
POST /api/v1/attendance/scan-qr/
{
    "session_code": "uuid-code-here",
    "student_location": {
        "latitude": 24.7136,
        "longitude": 46.6753
    }
}
```

---

## 🔧 إعداد البيئة المتقدمة

### 1. تكوين قاعدة البيانات
```python
# في settings.py أو .env
DATABASE_URL=postgresql://user:password@localhost:5432/university_db

# أو للتطوير
DATABASE_URL=sqlite:///db.sqlite3
```

### 2. إعداد Redis للتخزين المؤقت
```python
# في .env
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 3. تكوين الأمان المتقدم
```python
# إعدادات الأمان في .env
SECRET_KEY=your-super-secure-secret-key
DEBUG=False  # للإنتاج
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# إعدادات الأمان السيبراني
SECURITY_WHITELISTED_IPS=127.0.0.1,192.168.1.0/24
ENABLE_THREAT_DETECTION=True
ENABLE_BEHAVIOR_ANALYSIS=True
```

### 4. تشغيل Celery (للمهام الخلفية)
```bash
# في نافذة طرفية منفصلة
celery -A university_system worker -l info

# في نافذة أخرى للمهام المجدولة
celery -A university_system beat -l info
```

---

## 📱 تشغيل تطبيق الموبايل

### 1. إعداد Flutter
```bash
# تثبيت Flutter
flutter --version  # يجب أن يكون 3.16 أو أحدث

# الانتقال لمجلد التطبيق
cd mobile_app

# تثبيت التبعيات
flutter pub get

# تشغيل التطبيق
flutter run
```

### 2. بناء التطبيق للإنتاج
```bash
# لنظام Android
flutter build apk --release

# لنظام iOS (على Mac فقط)
flutter build ios --release

# للويب
flutter build web
```

---

## 🌟 الاستخدام الأساسي

### 1. تسجيل الدخول
- **المدير**: استخدم الحساب الذي أنشأته بـ `createsuperuser`
- **الطلاب**: يتم إنشاؤهم من لوحة الإدارة أو عبر API
- **الأساتذة**: نفس الطريقة مع تحديد الدور

### 2. إضافة بيانات تجريبية
```bash
# تشغيل script البيانات التجريبية
python create_demo_data.py

# أو البيانات البسيطة
python create_simple_demo.py
```

### 3. استخدام المساعد الذكي
1. سجل دخول كطالب
2. اذهب لصفحة المساعد الذكي
3. اكتب سؤالك (مثل: "ما هي درجاتي؟")
4. احصل على إجابة ذكية مخصصة

### 4. مراقبة الأمان
1. سجل دخول كمدير
2. اذهب لـ `/api/v1/cyber-security/dashboard/`
3. راقب التهديدات والأحداث الأمنية
4. قم بحظر IPs مشبوهة عند الحاجة

---

## 🚨 استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ في الاتصال بقاعدة البيانات
```bash
# تأكد من تشغيل PostgreSQL
sudo service postgresql start

# أو استخدم SQLite (افتراضي)
# لا حاجة لأي إعداد إضافي
```

#### 2. خطأ في Redis
```bash
# تشغيل Redis
redis-server

# أو تعطيل Cache في الإعدادات
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

#### 3. أخطاء الذكاء الاصطناعي
```bash
# تأكد من تثبيت المكتبات المطلوبة
pip install scikit-learn numpy pandas

# إعادة تدريب النماذج إذا لزم الأمر
python manage.py shell
>>> from smart_ai.ai_engine import university_ai
>>> # النماذج ستتدرب تلقائياً عند أول استخدام
```

#### 4. مشاكل QR Code
```bash
# تأكد من تثبيت مكتبة QR
pip install qrcode[pil]

# تأكد من إعدادات MEDIA_ROOT
python manage.py collectstatic
```

---

## 📊 مراقبة الأداء

### 1. مراقبة السجلات
```bash
# عرض السجلات المباشرة
tail -f logs/django.log

# سجلات الأمان
tail -f logs/security.log
```

### 2. فحص الأداء
```python
# في Django shell
python manage.py shell

# فحص حالة الذكاء الاصطناعي
>>> from smart_ai.ai_engine import university_ai
>>> print("AI Engine Status: Ready" if university_ai else "Not Ready")

# فحص الأمان
>>> from cyber_security.security_engine import threat_detector
>>> print(f"Security Engine: {threat_detector}")
```

### 3. Health Check
```
GET /health/
{
    "status": "healthy",
    "database": "ok",
    "cache": "ok",
    "disk_usage": "45%"
}
```

---

## 🎯 النصائح والحيل

### 1. تحسين الأداء
```python
# في production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# استخدم Gunicorn
gunicorn university_system.wsgi:application --bind 0.0.0.0:8000
```

### 2. الأمان في الإنتاج
- غيّر `SECRET_KEY` لقيمة فريدة
- استخدم HTTPS دائماً
- فعّل جميع middleware الأمان
- راقب السجلات بانتظام

### 3. النسخ الاحتياطي
```bash
# نسخ احتياطي من قاعدة البيانات
python manage.py dumpdata > backup.json

# استرداد النسخة الاحتياطية
python manage.py loaddata backup.json
```

---

## 📞 الدعم والمساعدة

### الموارد المفيدة
- 📖 **التوثيق الكامل**: `/api/docs/`
- 🔧 **API Reference**: `/api/redoc/`
- 🛡️ **دليل الأمان**: `SECURITY.md`
- 🤖 **دليل الذكاء الاصطناعي**: `AI_GUIDE.md`

### التواصل
- 📧 **البريد الإلكتروني**: support@university.edu
- 📱 **الهاتف**: +966123456789
- 🌐 **الموقع**: https://university.edu
- 📋 **المشاكل**: GitHub Issues

---

## 🎉 مبروك!

لقد نجحت في تشغيل **نظام إدارة الجامعة الذكي المتقدم**! 

النظام الآن جاهز مع:
- ✅ ذكاء اصطناعي متكامل
- ✅ أمان سيبراني متطور
- ✅ تطبيق موبايل عصري
- ✅ واجهات API محسنة
- ✅ نظام حضور ذكي

**استمتع بالاستخدام واستكشف الميزات المتقدمة!** 🚀

---

*تم إعداد هذا الدليل بواسطة نظام الذكاء الاصطناعي المتقدم*  
*آخر تحديث: 2025-10-20*