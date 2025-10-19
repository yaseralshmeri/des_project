#!/usr/bin/env python3
"""
Enhanced University Management System Startup Script
سكريبت تشغيل محسن لنظام إدارة الجامعة

This script provides an enhanced startup experience with automatic
system checks, database setup, and development utilities.
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_system.settings')

# Import Django after setting environment
django.setup()

from django.core.management import execute_from_command_line
from django.core.management.commands.runserver import Command as RunServerCommand
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()


def print_banner():
    """Print a beautiful banner for the system"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                  ║
    ║    🎓 نظام إدارة الجامعة الشامل | University Management System 🎓               ║
    ║                                                                                  ║
    ║    ✨ Enhanced Version with Modern UI & Advanced Features ✨                     ║
    ║                                                                                  ║
    ║    🚀 Ready to launch with all improvements and optimizations! 🚀                ║
    ║                                                                                  ║
    ╚══════════════════════════════════════════════════════════════════════════════════╝
    """
    
    print("\033[96m" + banner + "\033[0m")


def check_database():
    """Check database connection and status"""
    print("\n🔍 Checking database connection...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_migrations():
    """Check if all migrations are applied"""
    print("\n📦 Checking migrations...")
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠️  Found {len(plan)} unapplied migrations")
            return False
        else:
            print("✅ All migrations applied")
            return True
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False


def apply_migrations():
    """Apply pending migrations"""
    print("\n🔄 Applying migrations...")
    
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def check_superuser():
    """Check if superuser exists"""
    print("\n👑 Checking admin user...")
    
    try:
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Admin user exists")
            return True
        else:
            print("⚠️  No admin user found")
            return False
    except Exception as e:
        print(f"❌ Admin user check failed: {e}")
        return False


def create_demo_user():
    """Create demo admin user"""
    print("\n👤 Creating demo admin user...")
    
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='ADMIN'
            )
            print("✅ Demo admin user created")
            print("   Username: admin")
            print("   Password: admin123")
        else:
            print("✅ Demo admin user already exists")
        return True
    except Exception as e:
        print(f"❌ Demo user creation failed: {e}")
        return False


def collect_static():
    """Collect static files"""
    print("\n📁 Collecting static files...")
    
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False


def check_system_requirements():
    """Check system requirements and dependencies"""
    print("\n🔧 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 9:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️  Python version: {python_version.major}.{python_version.minor}.{python_version.micro} (Recommended: 3.9+)")
    
    # Check required directories
    required_dirs = ['static', 'media', 'templates', 'logs']
    for dir_name in required_dirs:
        dir_path = BASE_DIR / dir_name
        if dir_path.exists():
            print(f"✅ Directory {dir_name}: OK")
        else:
            print(f"📁 Creating directory: {dir_name}")
            dir_path.mkdir(exist_ok=True)
    
    return True


def print_access_info():
    """Print access information"""
    print("\n" + "="*80)
    print("🌐 ACCESS INFORMATION | معلومات الوصول")
    print("="*80)
    print("🏠 Main Website:      http://localhost:8000/")
    print("🔧 Admin Panel:       http://localhost:8000/admin/")
    print("📚 API Documentation: http://localhost:8000/api/docs/")
    print("📊 Dashboard:         http://localhost:8000/web/enhanced/dashboard/")
    print("="*80)
    print("🔐 DEFAULT LOGIN CREDENTIALS | بيانات الدخول الافتراضية")
    print("="*80)
    print("👑 Admin:    Username: admin     | Password: admin123")
    print("👨‍🏫 Teacher:  Username: teacher1  | Password: teacher123")
    print("🎓 Student:  Username: student1  | Password: student123")
    print("="*80)
    print("✨ Enhanced Features Available:")
    print("   • Modern Arabic/English UI with RTL support")
    print("   • Real-time dashboard with statistics")
    print("   • Advanced course management")
    print("   • Student enrollment system")
    print("   • Grade management for teachers")
    print("   • Financial tracking system")
    print("   • Notification system")
    print("   • RESTful API with documentation")
    print("   • Responsive design for all devices")
    print("="*80)


def run_development_server():
    """Start the development server"""
    print("\n🚀 Starting enhanced development server...")
    print("📝 Press Ctrl+C to stop the server")
    print("🔄 The server will automatically reload on code changes")
    
    try:
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using University Management System!")
        print("🎓 Made with ❤️ for Arabic Education")


def main():
    """Main function to run the enhanced startup process"""
    print_banner()
    
    # System checks
    print("\n🔍 SYSTEM CHECKS | فحص النظام")
    print("-" * 50)
    
    all_good = True
    
    # Check system requirements
    if not check_system_requirements():
        all_good = False
    
    # Check database
    if not check_database():
        print("❌ Database check failed. Please ensure your database is properly configured.")
        return
    
    # Check and apply migrations
    if not check_migrations():
        if not apply_migrations():
            print("❌ Failed to apply migrations. Please check your database configuration.")
            return
    
    # Check superuser
    if not check_superuser():
        if not create_demo_user():
            print("⚠️  No admin user available. You may need to create one manually.")
    
    # Collect static files in production
    if not os.environ.get('DEBUG', 'True').lower() == 'true':
        collect_static()
    
    if all_good:
        print("\n✅ All system checks passed!")
    else:
        print("\n⚠️  Some checks failed, but the system should still work.")
    
    # Print access information
    print_access_info()
    
    # Start server
    run_development_server()


if __name__ == '__main__':
    main()