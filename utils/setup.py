#!/usr/bin/env python3
"""
University Management System - Setup Script
سكريبت إعداد نظام إدارة الجامعة

This script helps set up the University Management System for development or production.
"""

import os
import sys
import subprocess
import secrets
import shutil
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_colored(message, color=Colors.GREEN, bold=False):
    """Print colored message to terminal"""
    style = Colors.BOLD if bold else ''
    print(f"{style}{color}{message}{Colors.END}")


def run_command(command, check=True, capture_output=False):
    """Run shell command with error handling"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=check, 
                                    capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"خطأ في تنفيذ الأمر: {command}", Colors.RED)
        print_colored(f"Error: {e}", Colors.RED)
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print_colored("🐍 فحص إصدار Python...", Colors.BLUE)
    
    if sys.version_info < (3, 9):
        print_colored("❌ يتطلب Python 3.9 أو أحدث", Colors.RED)
        sys.exit(1)
    
    print_colored(f"✅ Python {sys.version.split()[0]} متوافق", Colors.GREEN)


def create_virtual_environment():
    """Create and activate virtual environment"""
    print_colored("📦 إنشاء البيئة الافتراضية...", Colors.BLUE)
    
    if not os.path.exists('venv'):
        if not run_command(f"{sys.executable} -m venv venv"):
            print_colored("❌ فشل في إنشاء البيئة الافتراضية", Colors.RED)
            sys.exit(1)
        print_colored("✅ تم إنشاء البيئة الافتراضية", Colors.GREEN)
    else:
        print_colored("✅ البيئة الافتراضية موجودة مسبقاً", Colors.YELLOW)


def install_requirements():
    """Install Python requirements"""
    print_colored("📚 تثبيت المتطلبات...", Colors.BLUE)
    
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = 'venv\\Scripts\\pip'
    else:  # Unix/Linux/Mac
        pip_cmd = 'venv/bin/pip'
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        print_colored("❌ فشل في تثبيت المتطلبات", Colors.RED)
        sys.exit(1)
    
    print_colored("✅ تم تثبيت جميع المتطلبات", Colors.GREEN)


def create_environment_file():
    """Create .env file from template"""
    print_colored("⚙️  إنشاء ملف الإعدادات البيئية...", Colors.BLUE)
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            
            # Generate secure secret key
            secret_key = secrets.token_urlsafe(50)
            
            # Read and update .env file
            with open('.env', 'r') as f:
                content = f.read()
            
            # Replace default secret key
            content = content.replace(
                'SECRET_KEY=change-this-to-a-secure-secret-key-in-production',
                f'SECRET_KEY={secret_key}'
            )
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print_colored("✅ تم إنشاء ملف .env مع مفتاح سري آمن", Colors.GREEN)
        else:
            print_colored("❌ ملف .env.example غير موجود", Colors.RED)
    else:
        print_colored("✅ ملف .env موجود مسبقاً", Colors.YELLOW)


def setup_database():
    """Set up database with migrations"""
    print_colored("🗄️  إعداد قاعدة البيانات...", Colors.BLUE)
    
    # Determine python command
    if os.name == 'nt':  # Windows
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_cmd = 'venv/bin/python'
    
    # Create migrations
    print_colored("🔄 إنشاء الهجرات...", Colors.BLUE)
    run_command(f"{python_cmd} manage.py makemigrations")
    
    # Apply migrations
    print_colored("🔄 تطبيق الهجرات...", Colors.BLUE)
    if not run_command(f"{python_cmd} manage.py migrate"):
        print_colored("❌ فشل في تطبيق الهجرات", Colors.RED)
        return False
    
    print_colored("✅ تم إعداد قاعدة البيانات", Colors.GREEN)
    return True


def collect_static_files():
    """Collect static files"""
    print_colored("📁 جمع الملفات الثابتة...", Colors.BLUE)
    
    # Determine python command
    if os.name == 'nt':  # Windows
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_cmd = 'venv/bin/python'
    
    run_command(f"{python_cmd} manage.py collectstatic --noinput")
    print_colored("✅ تم جمع الملفات الثابتة", Colors.GREEN)


def create_superuser():
    """Create Django superuser"""
    print_colored("👤 إنشاء مستخدم إداري...", Colors.BLUE)
    
    # Determine python command
    if os.name == 'nt':  # Windows
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_cmd = 'venv/bin/python'
    
    print_colored("يرجى إدخال بيانات المستخدم الإداري:", Colors.YELLOW)
    
    try:
        run_command(f"{python_cmd} manage.py createsuperuser", check=False)
        print_colored("✅ تم إنشاء المستخدم الإداري", Colors.GREEN)
    except KeyboardInterrupt:
        print_colored("\n⏭️  تم تخطي إنشاء المستخدم الإداري", Colors.YELLOW)


def create_directories():
    """Create necessary directories"""
    print_colored("📁 إنشاء المجلدات الضرورية...", Colors.BLUE)
    
    directories = ['logs', 'media', 'staticfiles']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print_colored("✅ تم إنشاء جميع المجلدات", Colors.GREEN)


def display_completion_message():
    """Display completion message with instructions"""
    print_colored("\n🎉 تم إعداد نظام إدارة الجامعة بنجاح!", Colors.GREEN, bold=True)
    print_colored("=" * 60, Colors.BLUE)
    
    print_colored("\n🚀 لتشغيل الخادم:", Colors.BLUE, bold=True)
    
    if os.name == 'nt':  # Windows
        print_colored("   venv\\Scripts\\python manage.py runserver", Colors.YELLOW)
    else:  # Unix/Linux/Mac
        print_colored("   source venv/bin/activate", Colors.YELLOW)
        print_colored("   python manage.py runserver", Colors.YELLOW)
    
    print_colored("\n🌐 روابط مهمة:", Colors.BLUE, bold=True)
    print_colored("   • الصفحة الرئيسية: http://127.0.0.1:8000/", Colors.YELLOW)
    print_colored("   • لوحة الإدارة: http://127.0.0.1:8000/admin/", Colors.YELLOW)
    print_colored("   • توثيق API: http://127.0.0.1:8000/api/docs/", Colors.YELLOW)
    print_colored("   • فحص الصحة: http://127.0.0.1:8000/health/", Colors.YELLOW)
    
    print_colored("\n📚 ملاحظات مهمة:", Colors.BLUE, bold=True)
    print_colored("   • تأكد من تحديث ملف .env بالإعدادات المناسبة", Colors.YELLOW)
    print_colored("   • راجع README.md للمزيد من التفاصيل", Colors.YELLOW)
    print_colored("   • لإعداد Docker: docker-compose up --build", Colors.YELLOW)


def main():
    """Main setup function"""
    print_colored("\n🎓 مرحباً بك في إعداد نظام إدارة الجامعة", Colors.BLUE, bold=True)
    print_colored("University Management System Setup", Colors.BLUE, bold=True)
    print_colored("=" * 60, Colors.BLUE)
    
    try:
        # Step 1: Check Python version
        check_python_version()
        
        # Step 2: Create virtual environment
        create_virtual_environment()
        
        # Step 3: Install requirements
        install_requirements()
        
        # Step 4: Create environment file
        create_environment_file()
        
        # Step 5: Create necessary directories
        create_directories()
        
        # Step 6: Setup database
        if setup_database():
            # Step 7: Collect static files
            collect_static_files()
            
            # Step 8: Create superuser (optional)
            try:
                response = input("\nهل تريد إنشاء مستخدم إداري الآن؟ (y/n): ")
                if response.lower() in ['y', 'yes', 'نعم']:
                    create_superuser()
            except KeyboardInterrupt:
                print_colored("\n⏭️  تم تخطي إنشاء المستخدم الإداري", Colors.YELLOW)
        
        # Display completion message
        display_completion_message()
        
    except KeyboardInterrupt:
        print_colored("\n\n❌ تم إلغاء الإعداد", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ خطأ غير متوقع: {e}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()