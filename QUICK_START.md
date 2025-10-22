# 🚀 دليل التشغيل السريع | Quick Start Guide

## 🎯 لتشغيل المشروع بسرعة

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

### 4. تطبيق قاعدة البيانات
```bash
python manage.py migrate
```

### 5. إنشاء مدير النظام (اختياري)
```bash
python manage.py createsuperuser
```

### 6. تشغيل الخادم
```bash
python manage.py runserver
```

### 7. الوصول للنظام
- **الصفحة الرئيسية**: http://localhost:8000/
- **لوحة الإدارة**: http://localhost:8000/admin/
- **توثيق API**: http://localhost:8000/api/docs/

## 🔐 بيانات تسجيل الدخول

### مدير النظام (إذا كان موجود):
- **اسم المستخدم**: admin
- **كلمة المرور**: admin123

---

## ✨ المميزات الجديدة

- 🎨 **تصميم عصري ومتجاوب**
- 📱 **متوافق مع الأجهزة المحمولة**
- 🔒 **نظام أمان متطور**
- ⚡ **أداء سريع ومحسن**
- 📊 **لوحة تحكم تفاعلية**
- 🌐 **واجهة ويب محسنة**

---

## 🛠️ في حالة وجود مشاكل

1. تأكد من تثبيت Python 3.9+
2. تأكد من تفعيل البيئة الافتراضية
3. تأكد من تثبيت جميع المتطلبات
4. راجع ملف `PROJECT_FIXES_REPORT.md` للتفاصيل

---

**🎓 نظام إدارة الجامعة جاهز للاستخدام!**