#!/usr/bin/env python
"""
مشغل المشروع المحسن | Enhanced Project Runner
نظام إدارة الجامعة الشامل | University Management System

هذا المشغل يوفر واجهة موحدة لإدارة المشروع
This runner provides a unified interface to manage the project
"""

import os
import sys
import subprocess
from pathlib import Path
import django
from django.conf import settings
from django.core.management import execute_from_command_line


def print_banner():
    """طباعة شعار المشروع"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                نظام إدارة الجامعة الشامل                    ║
    ║           University Management System v2.1                  ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🎓 نظام متكامل لإدارة جميع العمليات الأكاديمية والإدارية    ║
    ║  📚 إدارة الطلاب والمقررات والتسجيل والدرجات               ║
    ║  💰 النظام المالي والمدفوعات والمنح الدراسية               ║
    ║  🔔 نظام الإشعارات المتطور                                  ║
    ║  🤖 تحليلات ذكية وتوصيات شخصية                           ║
    ║  🔐 نظام أمان متقدم وحماية البيانات                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_requirements():
    """فحص المتطلبات الأساسية"""
    print("🔍 فحص المتطلبات الأساسية...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ يتطلب Python 3.9 أو أحدث")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  تحذير: لم يتم تفعيل البيئة الافتراضية")
    
    # Check if requirements are installed
    try:
        import django
        print(f"✅ Django {django.get_version()} مثبت")
    except ImportError:
        print("❌ Django غير مثبت. قم بتشغيل: pip install -r requirements.txt")
        return False
    
    return True


def run_system_check():
    """تشغيل فحص النظام"""
    print("🔍 فحص النظام...")
    result = subprocess.run([sys.executable, 'manage.py', 'check'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ النظام يعمل بشكل صحيح")
        return True
    else:
        print("❌ توجد مشاكل في النظام:")
        print(result.stderr)
        return False


def apply_migrations():
    """تطبيق الهجرات"""
    print("🔧 تطبيق هجرات قاعدة البيانات...")
    result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ تم تطبيق جميع الهجرات بنجاح")
        return True
    else:
        print("❌ فشل في تطبيق الهجرات:")
        print(result.stderr)
        return False


def collect_static():
    """جمع الملفات الثابتة"""
    print("📁 جمع الملفات الثابتة...")
    result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ تم جمع الملفات الثابتة بنجاح")
        return True
    else:
        print("⚠️  تحذير: لم يتم جمع الملفات الثابتة")
        return False


def create_superuser_if_needed():
    """إنشاء مستخدم إداري إذا لم يكن موجوداً"""
    print("👤 فحص المستخدم الإداري...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    django.setup()
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        print("⚠️  لا يوجد مستخدم إداري. تشغيل سكريبت إنشاء المستخدم الإداري...")
        subprocess.run([sys.executable, 'create_superuser.py'])
    else:
        print("✅ المستخدم الإداري موجود")


def show_access_info():
    """عرض معلومات الوصول للنظام"""
    print("\n" + "="*60)
    print("🌐 معلومات الوصول للنظام | System Access Information")
    print("="*60)
    print("🏠 الصفحة الرئيسية | Home: http://localhost:8000/")
    print("⚙️  لوحة الإدارة | Admin Panel: http://localhost:8000/admin/")
    print("📚 توثيق API | API Documentation: http://localhost:8000/api/docs/")
    print("🩺 فحص صحة النظام | Health Check: http://localhost:8000/health/")
    print("ℹ️  معلومات النظام | System Info: http://localhost:8000/system/info/")
    print("\n🔐 بيانات تسجيل الدخول الافتراضية | Default Login Credentials:")
    print("   👨‍💼 المدير | Admin: admin / admin123")
    print("   👨‍🏫 الأستاذ | Teacher: teacher1 / teacher123")
    print("   🎓 الطالب | Student: student1 / student123")
    print("="*60)


def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Run system check
    if not run_system_check():
        print("❌ فشل فحص النظام. يرجى إصلاح المشاكل أولاً.")
        return 1
    
    # Apply migrations
    if not apply_migrations():
        print("❌ فشل في تطبيق هجرات قاعدة البيانات.")
        return 1
    
    # Collect static files (optional)
    collect_static()
    
    # Create superuser if needed
    try:
        create_superuser_if_needed()
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم فحص المستخدم الإداري: {e}")
    
    # Show access information
    show_access_info()
    
    # Start development server
    print("\n🚀 تشغيل خادم التطوير...")
    print("⏹️  للإيقاف، اضغط Ctrl+C")
    print("-" * 60)
    
    try:
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف الخادم بنجاح!")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل الخادم: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())