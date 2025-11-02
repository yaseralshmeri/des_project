#!/usr/bin/env python
"""
سكريبت تحديث النظام | System Update Script
نظام إدارة الجامعة الشامل | University Management System

يقوم هذا السكريبت بتحديث النظام وتطبيق أحدث التحسينات
This script updates the system and applies the latest improvements
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def print_banner():
    """طباعة شعار سكريبت التحديث"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    سكريبت تحديث النظام                      ║
    ║                 System Update Script                         ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🔄 تحديث المتطلبات والمكتبات                              ║
    ║  🗄️  تطبيق هجرات قاعدة البيانات الجديدة                   ║
    ║  🧹 تنظيف الملفات المؤقتة                                  ║
    ║  ✅ فحص سلامة النظام                                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_command(command, description):
    """تشغيل أمر وعرض النتيجة"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - تم بنجاح")
            return True, result.stdout
        else:
            print(f"❌ {description} - فشل")
            print(f"خطأ: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - خطأ: {e}")
        return False, str(e)


def check_python_version():
    """فحص إصدار Python"""
    print("🐍 فحص إصدار Python...")
    version = sys.version_info
    if version >= (3, 9):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - متوافق")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - يتطلب Python 3.9+")
        return False


def update_requirements():
    """تحديث المتطلبات"""
    print("📦 تحديث المتطلبات...")
    
    # Upgrade pip first
    success, _ = run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "ترقية pip"
    )
    
    if not success:
        return False
    
    # Install/upgrade requirements
    success, _ = run_command(
        f"{sys.executable} -m pip install -r requirements.txt --upgrade",
        "تحديث المتطلبات"
    )
    
    return success


def make_migrations():
    """إنشاء هجرات جديدة"""
    print("🗄️  فحص الهجرات الجديدة...")
    
    # Check for changes
    success, output = run_command(
        f"{sys.executable} manage.py makemigrations --dry-run",
        "فحص التغييرات في النماذج"
    )
    
    if "No changes detected" in output:
        print("ℹ️  لا توجد تغييرات جديدة في النماذج")
        return True
    
    # Create migrations
    success, _ = run_command(
        f"{sys.executable} manage.py makemigrations",
        "إنشاء هجرات جديدة"
    )
    
    return success


def apply_migrations():
    """تطبيق الهجرات"""
    success, _ = run_command(
        f"{sys.executable} manage.py migrate",
        "تطبيق هجرات قاعدة البيانات"
    )
    
    return success


def collect_static_files():
    """جمع الملفات الثابتة"""
    success, _ = run_command(
        f"{sys.executable} manage.py collectstatic --noinput",
        "جمع الملفات الثابتة"
    )
    
    return success


def run_system_check():
    """فحص النظام"""
    success, _ = run_command(
        f"{sys.executable} manage.py check",
        "فحص سلامة النظام"
    )
    
    return success


def clean_temp_files():
    """تنظيف الملفات المؤقتة"""
    print("🧹 تنظيف الملفات المؤقتة...")
    
    # Clean Python cache
    success, _ = run_command(
        "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true",
        "تنظيف ملفات Python المؤقتة"
    )
    
    # Clean .pyc files
    success, _ = run_command(
        "find . -name '*.pyc' -delete 2>/dev/null || true",
        "حذف ملفات .pyc"
    )
    
    # Clean .pyo files
    success, _ = run_command(
        "find . -name '*.pyo' -delete 2>/dev/null || true",
        "حذف ملفات .pyo"
    )
    
    print("✅ تم تنظيف الملفات المؤقتة")


def create_update_log():
    """إنشاء سجل التحديث"""
    print("📝 إنشاء سجل التحديث...")
    
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create update log
        log_file = logs_dir / "system_updates.log"
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "action": "system_update",
            "status": "completed",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "description": "System update completed successfully"
        }
        
        # Append to log file
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        
        logs.append(log_entry)
        
        # Keep only last 50 entries
        logs = logs[-50:]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ تم إنشاء سجل التحديث: {log_file}")
        
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم إنشاء سجل التحديث: {e}")


def check_security_updates():
    """فحص التحديثات الأمنية"""
    print("🔒 فحص التحديثات الأمنية...")
    
    try:
        # Check for known security vulnerabilities
        success, output = run_command(
            f"{sys.executable} -m pip list --outdated",
            "فحص المكتبات القديمة"
        )
        
        if success and output.strip():
            print("⚠️  تحذير: توجد مكتبات قديمة قد تحتوي على ثغرات أمنية")
            print("يُنصح بتحديثها باستخدام: pip install --upgrade <package_name>")
        else:
            print("✅ جميع المكتبات محدثة")
            
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم فحص التحديثات الأمنية: {e}")


def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🚀 بدء عملية تحديث النظام...")
    print("-" * 60)
    
    # Check Python version
    if not check_python_version():
        print("❌ إصدار Python غير متوافق. يرجى ترقية Python إلى 3.9 أو أحدث.")
        return 1
    
    # Update requirements
    if not update_requirements():
        print("❌ فشل في تحديث المتطلبات.")
        return 1
    
    # Create migrations
    if not make_migrations():
        print("⚠️  تحذير: مشكلة في إنشاء الهجرات")
    
    # Apply migrations
    if not apply_migrations():
        print("❌ فشل في تطبيق الهجرات.")
        return 1
    
    # Collect static files
    if not collect_static_files():
        print("⚠️  تحذير: مشكلة في جمع الملفات الثابتة")
    
    # Run system check
    if not run_system_check():
        print("❌ فشل فحص النظام.")
        return 1
    
    # Clean temporary files
    clean_temp_files()
    
    # Check security updates
    check_security_updates()
    
    # Create update log
    create_update_log()
    
    print("\n" + "="*60)
    print("✅ تم تحديث النظام بنجاح!")
    print("🎉 النظام الآن يعمل بأحدث إصدار مع جميع التحسينات")
    print("\n🔄 يُنصح بإعادة تشغيل النظام لتطبيق جميع التحديثات")
    print("استخدم: python run_project.py لبدء النظام")
    print("="*60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())