#!/usr/bin/env python
"""
Enhanced Django Management Script for University Management System
إدارة محسنة لنظام إدارة الجامعة
"""
import os
import sys
import subprocess
from pathlib import Path

def colored_print(message, color_code):
    """Print colored text to terminal"""
    print(f"\033[{color_code}m{message}\033[0m")

def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🎓 نظام إدارة الجامعة الشامل 🎓                ║
║              University Management System                     ║
║                      Enhanced Version                        ║
╚══════════════════════════════════════════════════════════════╝
    """
    colored_print(banner, "36")  # Cyan

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import django
        colored_print("✅ Django is installed", "32")  # Green
        
        # Check Django version
        django_version = django.get_version()
        colored_print(f"   Django version: {django_version}", "33")  # Yellow
        
        return True
    except ImportError:
        colored_print("❌ Django is not installed", "31")  # Red
        colored_print("   Please run: pip install -r requirements.txt", "33")
        return False

def setup_environment():
    """Set up environment variables"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        colored_print("⚠️  .env file not found, creating default...", "33")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("""# University Management System Environment Variables
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# University Information
UNIVERSITY_NAME=جامعة المستقبل
UNIVERSITY_NAME_EN=Future University
UNIVERSITY_CODE=FU
UNIVERSITY_SHORT_NAME=UMS

# API Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
""")
        colored_print("✅ Default .env file created", "32")

def run_migrations():
    """Run database migrations"""
    colored_print("🔄 Running database migrations...", "34")  # Blue
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        colored_print("✅ Database migrations completed", "32")
        return True
    except subprocess.CalledProcessError:
        colored_print("❌ Migration failed", "31")
        return False

def create_superuser():
    """Create superuser if doesn't exist"""
    colored_print("👤 Checking for superuser...", "34")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            colored_print("Creating default superuser...", "33")
            subprocess.run([
                sys.executable, 'manage.py', 'shell', '-c',
                """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@university.edu', 'admin123')
    print('Superuser created: admin/admin123')
                """
            ], check=True)
            colored_print("✅ Default superuser created (admin/admin123)", "32")
        else:
            colored_print("✅ Superuser already exists", "32")
        return True
    except Exception as e:
        colored_print(f"❌ Failed to create superuser: {e}", "31")
        return False

def collect_static():
    """Collect static files"""
    colored_print("📁 Collecting static files...", "34")
    try:
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
        colored_print("✅ Static files collected", "32")
        return True
    except subprocess.CalledProcessError:
        colored_print("❌ Failed to collect static files", "31")
        return False

def main():
    """Enhanced Django management with setup automation"""
    print_banner()
    
    # Check if this is a setup command
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        colored_print("🚀 Setting up University Management System...", "35")  # Magenta
        
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Setup environment
        setup_environment()
        
        # Import Django after setting up environment
        try:
            import django
            from django.conf import settings
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            colored_print(f"❌ Django import error: {exc}", "31")
            sys.exit(1)
        
        django.setup()
        
        # Run setup steps
        success = True
        success &= run_migrations()
        success &= create_superuser()
        success &= collect_static()
        
        if success:
            colored_print("\n🎉 Setup completed successfully!", "32")
            colored_print("🌐 You can now run: python enhanced_manage.py runserver", "36")
            colored_print("📊 Access the system at: http://localhost:8000", "36")
        else:
            colored_print("\n❌ Setup completed with errors", "31")
        
        return
    
    # Regular Django management
    setup_environment()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Show helpful messages for common commands
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'runserver':
            colored_print("🚀 Starting University Management System server...", "35")
            colored_print("🌐 Access URLs:", "36")
            colored_print("   • Main System: http://localhost:8000", "37")
            colored_print("   • Enhanced UI: http://localhost:8000/web/enhanced/", "37")
            colored_print("   • Admin Panel: http://localhost:8000/admin/", "37")
            colored_print("   • API Docs: http://localhost:8000/api/docs/", "37")
            print()
        elif command == 'migrate':
            colored_print("🔄 Running database migrations...", "34")
        elif command == 'createsuperuser':
            colored_print("👤 Creating superuser...", "34")
        elif command == 'collectstatic':
            colored_print("📁 Collecting static files...", "34")
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()