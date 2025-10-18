# 🎓 University Management System
## نظام إدارة الجامعة الشامل

> **الإصدار النهائي المُوحد والمُحسن** - This is the official consolidated version
> 
> جميع الإصدارات السابقة تم دمجها وتحسينها في هذا الإصدار النهائي

---

## 📋 نظرة عامة | Overview

نظام إدارة جامعي شامل ومتطور مبني بـ Django يوفر واجهة ويب حديثة، واجهات برمجية RESTful، تحليلات ذكية، وإمكانيات إدارة أكاديمية متقدمة.

A comprehensive, modern university management system built with Django, featuring a web interface, RESTful APIs, AI analytics, and advanced academic management capabilities.

---

## ✨ الميزات الرئيسية | Key Features

### 🎯 الوظائف الأساسية | Core Functionality
- **🔐 نظام متعدد الأدوار**: طلاب، أساتذة، موظفين، ومديرين
- **📚 الإدارة الأكاديمية**: المقررات، التسجيل، الدرجات، الحضور، الجداول
- **💰 الإدارة المالية**: المدفوعات، الفواتير، تتبع الرسوم
- **🔔 الإشعارات الفورية**: البريد الإلكتروني، داخل التطبيق، SMS
- **🤖 التحليلات الذكية**: تحليلات تنبؤية لأداء الطلاب
- **📊 التقارير الشاملة**: تقارير أكاديمية ومالية
- **💻 واجهة ويب حديثة**: متجاوبة، متوافقة مع الجوال

### 👥 الأدوار والصلاحيات | User Roles & Capabilities

#### 🎓 الطلاب | Students
- عرض المقررات المسجلة والجداول الدراسية
- مراجعة الدرجات والتقدم الأكاديمي
- تتبع سجلات الحضور
- إدارة المدفوعات المالية
- استقبال الإشعارات والإعلانات
- تحديث البيانات الشخصية

#### 👨‍🏫 الأساتذة | Teachers
- إدارة جداول الصفوف
- تسجيل الدرجات والحضور
- عرض تقدم الطلاب
- الوصول لتحليلات التدريس
- إرسال إشعارات للطلاب

#### 👨‍💼 الموظفين والمديرين | Staff & Administrators
- إدارة المستخدمين الكاملة
- الإشراف على البرامج الأكاديمية
- التقارير المالية
- تحليلات وإحصائيات النظام
- إدارة الإشعارات
- إدارة المقررات والأقسام

### 🔧 الميزات التقنية | Technical Features
- **📡 RESTful API**: واجهة برمجية شاملة مع توثيق Swagger
- **🔑 JWT Authentication**: مصادقة آمنة قائمة على الرموز المميزة
- **📱 تصميم متجاوب**: Bootstrap 5 مع تصميم مخصص
- **🗄️ مرونة قاعدة البيانات**: SQLite (تطوير) / PostgreSQL (إنتاج)
- **🐳 دعم Docker**: حاويات كاملة
- **🤖 تكامل الذكاء الاصطناعي**: التنبؤ بأداء الطلاب
- **⚡ التحديثات الفورية**: دعم WebSocket للإشعارات
- **📁 إدارة الملفات**: الصور الشخصية ورفع المستندات

---

## 🚀 التثبيت والتشغيل | Installation & Setup

### 📋 المتطلبات الأساسية | Prerequisites

- Python 3.9+
- Node.js 16+ (للواجهة الأمامية)
- PostgreSQL 13+ (للإنتاج)
- Redis 6+ (للتخزين المؤقت والمهام الخلفية)

### 🛠️ التثبيت السريع | Quick Installation

#### 1. استنساخ المشروع | Clone the Project
```bash
git clone https://github.com/your-username/university-management-system.git
cd university-management-system
```

#### 2. إنشاء البيئة الافتراضية | Create Virtual Environment
```bash
python -m venv venv

# على Windows | Windows
venv\Scripts\activate

# على Linux/Mac | Linux/Mac
source venv/bin/activate
```

#### 3. تثبيت المتطلبات | Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. إعداد متغيرات البيئة | Environment Configuration
```bash
# انسخ ملف البيئة النموذجي | Copy example environment file
cp .env.example .env

# قم بتحديث القيم في ملف .env | Update values in .env file
# خاصة SECRET_KEY, DEBUG, DATABASE_URL
```

#### 5. إعداد قاعدة البيانات | Database Setup
```bash
# إنشاء وتطبيق الهجرات | Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# إنشاء مستخدم إداري | Create superuser
python manage.py createsuperuser

# تحميل البيانات الأولية (اختياري) | Load initial data (optional)
python manage.py loaddata initial_data.json
```

#### 6. جمع الملفات الثابتة | Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### 7. تشغيل الخادم | Run Development Server
```bash
python manage.py runserver
```

### 🐳 التشغيل باستخدام Docker

#### التشغيل السريع | Quick Start
```bash
# بناء وتشغيل جميع الخدمات | Build and run all services
docker-compose up --build

# التشغيل في الخلفية | Run in background
docker-compose up -d
```

#### أوامر Docker مفيدة | Useful Docker Commands
```bash
# عرض السجلات | View logs
docker-compose logs -f web

# تنفيذ أوامر Django | Execute Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# إيقاف الخدمات | Stop services
docker-compose down

# إعادة بناء الصور | Rebuild images
docker-compose build --no-cache
```

---

## 🔧 الإعدادات والتكوين | Configuration

### 📁 الإعدادات الأساسية | Basic Configuration

#### ملف `.env` | Environment File
```env
# الأمان | Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# قاعدة البيانات | Database
DATABASE_URL=postgresql://user:password@localhost:5432/university_db

# البريد الإلكتروني | Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis للتخزين المؤقت | Redis for Caching
REDIS_URL=redis://localhost:6379/1

# Celery للمهام الخلفية | Celery for Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 🎯 إعدادات الجامعة | University Settings
```env
# معلومات الجامعة | University Information
UNIVERSITY_NAME=جامعة المستقبل
UNIVERSITY_NAME_EN=Future University
UNIVERSITY_CODE=FU

# العام الأكاديمي | Academic Year
CURRENT_ACADEMIC_YEAR=2024-2025
CURRENT_SEMESTER=1
```

---

## 📊 استخدام النظام | System Usage

### 🌐 الواجهات الرئيسية | Main Interfaces

#### لوحة التحكم الرئيسية | Main Dashboard
```
http://localhost:8000/
```

#### لوحة الإدارة | Admin Panel
```
http://localhost:8000/admin/
```

#### واجهة برمجة التطبيقات | API Documentation
```
http://localhost:8000/api/docs/          # Swagger UI
http://localhost:8000/api/redoc/         # ReDoc
```

#### المراقبة والصحة | Health & Monitoring
```
http://localhost:8000/health/            # Health Check
http://localhost:8000/api/health/        # API Health
```

### 🔑 التسجيل والمصادقة | Authentication

#### تسجيل الدخول | Login
```bash
POST /api/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}
```

#### الحصول على رمز | Get Token
```bash
POST /api/token/
{
    "username": "your_username", 
    "password": "your_password"
}
```

---

## 🧪 الاختبارات | Testing

### تشغيل الاختبارات | Running Tests
```bash
# تشغيل جميع الاختبارات | Run all tests
python manage.py test

# تشغيل اختبارات محددة | Run specific tests
python manage.py test students.tests

# اختبارات مع التغطية | Tests with coverage
pytest --cov=. --cov-report=html

# اختبارات التكامل | Integration tests
pytest tests/integration/
```

### إنشاء بيانات اختبار | Creating Test Data
```bash
# تشغيل script إنشاء البيانات | Run data generation script
python manage.py shell < scripts/create_test_data.py
```

---

## 🚀 النشر في الإنتاج | Production Deployment

### 🐳 النشر باستخدام Docker

#### 1. إعداد البيئة للإنتاج | Production Environment Setup
```bash
# انسخ إعدادات الإنتاج | Copy production settings
cp .env.production .env

# حديث قاعدة البيانات والإعدادات | Update database and settings
```

#### 2. النشر | Deployment
```bash
# بناء ونشر في الإنتاج | Build and deploy for production
docker-compose -f docker-compose.prod.yml up -d

# تطبيق الهجرات | Apply migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# جمع الملفات الثابتة | Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### ☁️ النشر السحابي | Cloud Deployment

#### على AWS | AWS Deployment
- استخدم **Elastic Beanstalk** للنشر السريع
- **RDS** لقاعدة البيانات
- **ElastiCache** لـ Redis
- **S3** للملفات الثابتة

#### على Google Cloud | Google Cloud Deployment
- استخدم **Cloud Run** للحاويات
- **Cloud SQL** لقاعدة البيانات
- **Memorystore** لـ Redis
- **Cloud Storage** للملفات

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### 🚨 المشاكل الشائعة | Common Issues

#### مشكلة قاعدة البيانات | Database Issues
```bash
# إعادة إنشاء قاعدة البيانات | Reset database
python manage.py flush
python manage.py migrate
```

#### مشاكل الملفات الثابتة | Static Files Issues
```bash
# إعادة جمع الملفات الثابتة | Recollect static files
python manage.py collectstatic --clear --noinput
```

#### مشاكل Redis/Celery | Redis/Celery Issues
```bash
# التحقق من حالة Redis | Check Redis status
redis-cli ping

# إعادة تشغيل Celery | Restart Celery
celery -A university_system worker -l info
```

### 📝 السجلات | Logs
```bash
# عرض سجلات Django | View Django logs
tail -f logs/django.log

# عرض سجلات Docker | View Docker logs
docker-compose logs -f web
```

---

## 🤝 المساهمة | Contributing

### 📝 إرشادات المساهمة | Contribution Guidelines

1. **Fork** المشروع
2. إنشاء **branch** جديد للميزة (`git checkout -b feature/AmazingFeature`)
3. **Commit** التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. **Push** إلى الـ branch (`git push origin feature/AmazingFeature`)
5. فتح **Pull Request**

### 🎨 معايير الكود | Code Standards
- اتبع **PEP 8** لـ Python
- استخدم **Black** لتنسيق الكود
- اكتب **اختبارات** للميزات الجديدة
- حديث **التوثيق**

---

## 📜 الترخيص | License

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 الدعم والتواصل | Support & Contact

### 🐛 الإبلاغ عن الأخطاء | Bug Reports
يرجى استخدام [GitHub Issues](https://github.com/your-repo/issues) للإبلاغ عن الأخطاء.

### 💡 طلب ميزات جديدة | Feature Requests  
استخدم [GitHub Issues](https://github.com/your-repo/issues) مع تصنيف "enhancement".

### 📧 التواصل | Contact
- البريد الإلكتروني: support@university-system.com
- الموقع: https://university-system.com
- التوثيق: https://docs.university-system.com

---

## 🙏 شكر وتقدير | Acknowledgments

- **Django Community** للإطار الرائع
- **Bootstrap** للتصميم المتجاوب
- **جميع المساهمين** في هذا المشروع

---

<div align="center">

**صُنع بـ ❤️ للتعليم العربي**  
**Made with ❤️ for Arabic Education**

[⬆ العودة للأعلى | Back to Top](#-university-management-system)

</div>