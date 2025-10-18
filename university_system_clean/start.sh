#!/bin/bash

# University Management System - Quick Start Script
# سكريبت بدء التشغيل السريع لنظام إدارة الجامعة

set -e  # Exit on any error

echo "🎓 مرحباً بك في نظام إدارة الجامعة"
echo "   University Management System - Quick Start"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 غير مثبت | Python 3 is not installed"
    exit 1
fi

print_status "تم العثور على Python | Python found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_info "إنشاء البيئة الافتراضية | Creating virtual environment..."
    python3 -m venv venv
    print_status "تم إنشاء البيئة الافتراضية | Virtual environment created"
fi

# Activate virtual environment
print_info "تفعيل البيئة الافتراضية | Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
print_info "تحديث pip | Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
if [ -f "requirements.txt" ]; then
    print_info "تثبيت المتطلبات | Installing requirements..."
    pip install -r requirements.txt --quiet
    print_status "تم تثبيت المتطلبات | Requirements installed"
else
    print_warning "ملف requirements.txt غير موجود | requirements.txt not found"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "إنشاء ملف .env | Creating .env file..."
        cp .env.example .env
        
        # Generate secure secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
        sed -i.bak "s/SECRET_KEY=change-this-to-a-secure-secret-key-in-production/SECRET_KEY=$SECRET_KEY/" .env
        rm .env.bak 2>/dev/null || true
        
        print_status "تم إنشاء ملف .env مع مفتاح آمن | .env file created with secure key"
    else
        print_warning "ملف .env.example غير موجود | .env.example not found"
    fi
fi

# Create necessary directories
print_info "إنشاء المجلدات الضرورية | Creating necessary directories..."
mkdir -p logs media staticfiles
print_status "تم إنشاء المجلدات | Directories created"

# Run migrations
print_info "تطبيق هجرات قاعدة البيانات | Applying database migrations..."
if python manage.py migrate --check &> /dev/null; then
    python manage.py migrate --verbosity=0
    print_status "تم تطبيق الهجرات | Migrations applied"
else
    print_info "إنشاء الهجرات | Creating migrations..."
    python manage.py makemigrations --verbosity=0
    python manage.py migrate --verbosity=0
    print_status "تم إنشاء وتطبيق الهجرات | Migrations created and applied"
fi

# Collect static files
print_info "جمع الملفات الثابتة | Collecting static files..."
python manage.py collectstatic --noinput --verbosity=0
print_status "تم جمع الملفات الثابتة | Static files collected"

# Check for superuser
if ! python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')
" 2>/dev/null | grep -q "exists"; then
    echo ""
    print_warning "لا يوجد مستخدم إداري | No superuser found"
    read -p "هل تريد إنشاء مستخدم إداري الآن؟ (y/n) | Create superuser now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py createsuperuser
        print_status "تم إنشاء المستخدم الإداري | Superuser created"
    fi
fi

echo ""
echo "🎉 تم إعداد النظام بنجاح | System setup completed successfully!"
echo "=================================================="
print_info "تشغيل الخادم | Starting development server..."
echo ""
print_status "🌐 الخادم يعمل على | Server running at:"
print_info "   • الصفحة الرئيسية | Homepage: http://127.0.0.1:8000/"
print_info "   • لوحة الإدارة | Admin Panel: http://127.0.0.1:8000/admin/"
print_info "   • توثيق API | API Docs: http://127.0.0.1:8000/api/docs/"
echo ""
print_warning "للإيقاف اضغط Ctrl+C | Press Ctrl+C to stop"
echo ""

# Start development server
python manage.py runserver