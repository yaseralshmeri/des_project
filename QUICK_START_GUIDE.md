# 🚀 دليل التشغيل السريع - نظام إدارة الجامعة الذكي

## 📦 التثبيت السريع

### 1. استنساخ المشروع
```bash
git clone https://github.com/yaseralshmeri/des_project.git
cd des_project
```

### 2. إعداد البيئة الافتراضية
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد قاعدة البيانات
```bash
python manage.py migrate
python create_demo_data.py
```

### 5. تشغيل النظام
```bash
python manage.py runserver
```

## 🌐 الوصول للنظام

### الواجهات الرئيسية:
- **الصفحة الرئيسية**: http://localhost:8000/
- **لوحة الإدارة**: http://localhost:8000/admin/
- **واجهات API**: http://localhost:8000/api/
- **توثيق API**: http://localhost:8000/api/docs/

### بيانات الدخول الافتراضية:
```
مدير النظام:
Username: admin
Password: admin123

أستاذ:
Username: teacher1  
Password: teacher123

طالب:
Username: student1
Password: student123
```

## 🧠 الميزات الذكية الجديدة

### 1. الذكاء الاصطناعي
- **التنبؤ بالأداء**: `/smart-ai/predict-performance/`
- **التوصيات الذكية**: `/smart-ai/recommendations/`
- **المساعد الذكي**: `/smart-ai/chat/`
- **الجدولة الذكية**: `/smart-ai/scheduling/`

### 2. الأمان السيبراني
- **مراقبة الأمان**: `/cyber-security/dashboard/`
- **تحليل التهديدات**: `/cyber-security/threats/`
- **سجلات الأمان**: `/cyber-security/audit-logs/`

### 3. نظام الحضور QR
- **إنشاء جلسة**: `/attendance-qr/create-session/`
- **مسح QR Code**: `/attendance-qr/scan/`
- **إحصائيات الحضور**: `/attendance-qr/statistics/`

## 📱 تطبيق الموبايل

### Flutter App Setup:
```bash
cd mobile_app/university_app
flutter pub get
flutter run
```

### المتطلبات:
- Flutter 3.10+
- Dart SDK 3.0+
- Android Studio / VS Code

## 🐳 التشغيل بـ Docker

```bash
# بناء وتشغيل
docker-compose up --build

# في الخلفية
docker-compose up -d

# إيقاف
docker-compose down
```

## 🔧 الإعدادات المتقدمة

### متغيرات البيئة (.env):
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379

# AI Settings
ENABLE_AI_FEATURES=True
AI_MODEL_PATH=/path/to/models/

# Security Settings  
ENABLE_SECURITY_MONITORING=True
SECURITY_ALERT_EMAIL=security@university.edu

# QR Settings
QR_CODE_VALIDITY_MINUTES=15
LOCATION_RADIUS_METERS=100
```

### إعداد PostgreSQL للإنتاج:
```bash
# إنشاء قاعدة البيانات
createdb university_db

# تحديث الإعدادات
DATABASE_URL=postgresql://user:password@localhost/university_db
```

## 📊 المراقبة والصيانة

### فحص حالة النظام:
```bash
python manage.py check
python manage.py test
```

### النسخ الاحتياطية:
```bash
python manage.py dumpdata > backup.json
```

### تحديث النظام:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

## 🆘 استكشاف الأخطاء

### مشاكل شائعة:

#### 1. خطأ في قاعدة البيانات:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 2. مشاكل الأذونات:
```bash
python manage.py createsuperuser
```

#### 3. مشاكل الملفات الثابتة:
```bash
python manage.py collectstatic --noinput
```

#### 4. مشاكل QR Code:
```bash
pip install qrcode[pil]
```

## 📚 موارد إضافية

### التوثيق:
- [دليل المطور الشامل](./DEVELOPMENT_GUIDE.md)
- [تقرير التطوير](./COMPREHENSIVE_AI_DEVELOPMENT_REPORT.md)
- [دليل الأمان](./SECURITY_GUIDE.md)

### الدعم:
- **GitHub Issues**: للمشاكل التقنية
- **Wiki**: للدروس والشروحات
- **Community**: للنقاشات والأسئلة

---

## ✅ قائمة مراجعة سريعة

قبل البدء، تأكد من:

- [ ] Python 3.9+ مثبت
- [ ] pip محدث لآخر إصدار
- [ ] Git مُكون بشكل صحيح
- [ ] متغيرات البيئة مُعدة
- [ ] قاعدة البيانات تعمل
- [ ] المتطلبات مثبتة بنجاح

---

<div align="center">

**🎓 نظام إدارة الجامعة الذكي - جاهز للعمل! 🎓**

**🚀 ابدأ رحلتك مع الذكاء الاصطناعي في التعليم 🚀**

</div>