# 🚀 دليل النشر | Deployment Guide

## 📋 مقدمة | Introduction

هذا الدليل يشرح كيفية نشر نظام إدارة الجامعة المتطور في بيئات مختلفة.

## 🎯 أنواع النشر | Deployment Types

### 1. النشر المحلي (Development)
للتطوير والاختبار المحلي.

### 2. النشر على الخادم (Production)
للاستخدام الفعلي في الجامعة.

### 3. النشر السحابي (Cloud)
باستخدام خدمات AWS، Azure، أو Google Cloud.

## 🛠️ متطلبات النشر | Deployment Requirements

### الحد الأدنى للخادم
```
CPU: 2 cores
RAM: 4GB
Storage: 50GB SSD
Network: 100Mbps
OS: Ubuntu 20.04+ / CentOS 8+
```

### للاستخدام المكثف
```
CPU: 4+ cores
RAM: 8GB+
Storage: 100GB+ SSD
Network: 1Gbps
Load Balancer: Nginx/Apache
Database: PostgreSQL Cluster
Cache: Redis Cluster
```

## 🐳 النشر باستخدام Docker

### 1. إعداد ملفات Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://user:pass@db:5432/university
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=university
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

### 2. تشغيل النشر
```bash
docker-compose up -d
```

## 🌐 إعداد Nginx

### ملف التكوين
```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name your-university.edu;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

## 🗄️ إعداد قاعدة البيانات

### PostgreSQL للإنتاج
```bash
# تثبيت PostgreSQL
sudo apt install postgresql postgresql-contrib

# إنشاء قاعدة البيانات
sudo -u postgres createdb university_db
sudo -u postgres createuser --interactive
```

### إعدادات Django
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'university_db',
        'USER': 'db_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔄 النشر التلقائي | Automated Deployment

### استخدام أداة النشر المطورة
```bash
python tools/deployment/deploy_and_push.py --environment production
```

### سكريبت النشر
```bash
#!/bin/bash
# deploy.sh

echo "🚀 بدء عملية النشر..."

# سحب آخر التحديثات
git pull origin main

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل المهاجرات
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# إعادة تشغيل الخدمات
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ تم النشر بنجاح!"
```

## 📊 مراقبة النظام بعد النشر

### 1. مراقبة الأداء
```bash
# استخدام htop لمراقبة الموارد
htop

# مراقبة Django
python tools/enhanced_systems/advanced_performance_optimizer.py
```

### 2. مراقبة السجلات
```bash
# سجلات Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# سجلات Django
tail -f logs/django.log
```

### 3. مراقبة قاعدة البيانات
```sql
-- PostgreSQL monitoring
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;
```

## 🔒 إعدادات الأمان للإنتاج

### 1. إعدادات Django
```python
# settings_production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. شهادات SSL
```bash
# باستخدام Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. جدار حماية
```bash
# إعداد UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 💾 النسخ الاحتياطية | Backups

### 1. نسخ احتياطي لقاعدة البيانات
```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +"%Y%m%d_%H%M%S")
DB_NAME="university_db"
BACKUP_DIR="/backups"

pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql
```

### 2. نسخ احتياطي للملفات
```bash
#!/bin/bash
# backup_files.sh

DATE=$(date +"%Y%m%d_%H%M%S")
tar -czf /backups/files_backup_$DATE.tar.gz /app/media/
```

### 3. أتمتة النسخ الاحتياطية
```bash
# إضافة إلى crontab
# 0 2 * * * /scripts/backup_db.sh
# 0 3 * * * /scripts/backup_files.sh
```

## 🔄 التحديثات | Updates

### 1. تحديث الكود
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### 2. تحديث التبعيات
```bash
pip list --outdated
pip install --upgrade package_name
```

## 🚨 استكشاف الأخطاء | Troubleshooting

### مشاكل شائعة وحلولها

#### 1. خطأ 500 Internal Server Error
```bash
# فحص سجلات الأخطاء
tail -f /var/log/nginx/error.log
tail -f logs/django.log

# فحص إعدادات Django
python manage.py check --deploy
```

#### 2. مشاكل قاعدة البيانات
```bash
# فحص اتصال قاعدة البيانات
python manage.py dbshell

# إعادة تشغيل PostgreSQL
sudo systemctl restart postgresql
```

#### 3. مشاكل الأداء
```bash
# استخدام أداة تحسين الأداء
python tools/enhanced_systems/advanced_performance_optimizer.py
```

## ✅ قائمة مراجعة النشر | Deployment Checklist

### قبل النشر
- [ ] اختبار جميع الميزات
- [ ] تحديث التوثيق
- [ ] فحص الأمان
- [ ] نسخ احتياطية
- [ ] إعدادات الإنتاج
- [ ] شهادات SSL

### بعد النشر
- [ ] اختبار النظام المنشور
- [ ] مراقبة الأداء
- [ ] فحص السجلات
- [ ] اختبار النسخ الاحتياطية
- [ ] تدريب المستخدمين

---

**نشر ناجح = نظام موثوق! 🎯**
