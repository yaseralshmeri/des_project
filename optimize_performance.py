#!/usr/bin/env python
"""
سكريبت تحسين الأداء | Performance Optimization Script
نظام إدارة الجامعة الشامل | University Management System

يقوم هذا السكريبت بتحسين أداء النظام وتنظيف قاعدة البيانات
This script optimizes system performance and cleans the database
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
from django.core.management import execute_from_command_line


def setup_django():
    """إعداد Django"""
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    django.setup()


def print_banner():
    """طباعة شعار سكريبت التحسين"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    سكريبت تحسين الأداء                      ║
    ║               Performance Optimization Script                ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🚀 تحسين أداء النظام وسرعة الاستجابة                      ║
    ║  🧹 تنظيف قاعدة البيانات من البيانات القديمة               ║
    ║  📊 تحسين الفهارس والاستعلامات                            ║
    ║  🔧 إصلاح المشاكل الشائعة                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def clean_old_sessions():
    """تنظيف الجلسات القديمة"""
    print("🧹 تنظيف الجلسات القديمة...")
    try:
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        # Delete sessions older than 30 days
        old_sessions = Session.objects.filter(
            expire_date__lt=timezone.now() - timedelta(days=30)
        )
        count = old_sessions.count()
        old_sessions.delete()
        print(f"✅ تم حذف {count} جلسة قديمة")
    except Exception as e:
        print(f"❌ خطأ في تنظيف الجلسات: {e}")


def clean_old_notifications():
    """تنظيف الإشعارات القديمة"""
    print("🧹 تنظيف الإشعارات القديمة...")
    try:
        from notifications.models import NotificationDelivery
        from django.utils import timezone
        
        # Delete old read notifications (older than 60 days)
        old_notifications = NotificationDelivery.objects.filter(
            is_read=True,
            created_at__lt=timezone.now() - timedelta(days=60)
        )
        count = old_notifications.count()
        old_notifications.delete()
        print(f"✅ تم حذف {count} إشعار قديم")
    except Exception as e:
        print(f"❌ خطأ في تنظيف الإشعارات: {e}")


def clean_old_audit_logs():
    """تنظيف سجلات المراجعة القديمة"""
    print("🧹 تنظيف سجلات المراجعة القديمة...")
    try:
        from cyber_security.models import SecurityAuditLog
        from django.utils import timezone
        
        # Delete audit logs older than 90 days
        old_logs = SecurityAuditLog.objects.filter(
            timestamp__lt=timezone.now() - timedelta(days=90)
        )
        count = old_logs.count()
        old_logs.delete()
        print(f"✅ تم حذف {count} سجل مراجعة قديم")
    except Exception as e:
        print(f"❌ خطأ في تنظيف سجلات المراجعة: {e}")


def optimize_database():
    """تحسين قاعدة البيانات"""
    print("🔧 تحسين قاعدة البيانات...")
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # SQLite optimization commands
            if 'sqlite' in str(connection.settings_dict['ENGINE']):
                cursor.execute("VACUUM;")
                cursor.execute("ANALYZE;")
                cursor.execute("PRAGMA optimize;")
                print("✅ تم تحسين قاعدة بيانات SQLite")
            else:
                print("ℹ️  تحسين قاعدة البيانات يتطلب إجراءات يدوية لقواعد البيانات الأخرى")
    except Exception as e:
        print(f"❌ خطأ في تحسين قاعدة البيانات: {e}")


def check_disk_space():
    """فحص مساحة القرص"""
    print("💾 فحص مساحة القرص...")
    try:
        import shutil
        
        total, used, free = shutil.disk_usage(".")
        total_gb = total // (1024**3)
        used_gb = used // (1024**3)
        free_gb = free // (1024**3)
        used_percent = (used / total) * 100
        
        print(f"📊 المساحة الإجمالية: {total_gb} GB")
        print(f"📊 المساحة المستخدمة: {used_gb} GB ({used_percent:.1f}%)")
        print(f"📊 المساحة المتاحة: {free_gb} GB")
        
        if used_percent > 90:
            print("⚠️  تحذير: مساحة القرص منخفضة!")
        elif used_percent > 80:
            print("⚠️  تنبيه: مساحة القرص تقترب من النفاد")
        else:
            print("✅ مساحة القرص كافية")
            
    except Exception as e:
        print(f"❌ خطأ في فحص مساحة القرص: {e}")


def check_database_size():
    """فحص حجم قاعدة البيانات"""
    print("🗄️  فحص حجم قاعدة البيانات...")
    try:
        db_file = Path("db.sqlite3")
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            print(f"📊 حجم قاعدة البيانات: {size_mb:.2f} MB")
            
            if size_mb > 1000:  # 1GB
                print("⚠️  تحذير: حجم قاعدة البيانات كبير")
            elif size_mb > 500:  # 500MB
                print("⚠️  تنبيه: حجم قاعدة البيانات متوسط")
            else:
                print("✅ حجم قاعدة البيانات مناسب")
        else:
            print("ℹ️  ملف قاعدة البيانات غير موجود")
    except Exception as e:
        print(f"❌ خطأ في فحص حجم قاعدة البيانات: {e}")


def generate_performance_report():
    """إنشاء تقرير الأداء"""
    print("📊 إنشاء تقرير الأداء...")
    try:
        from django.contrib.auth import get_user_model
        from students.models import User as StudentUser
        
        User = get_user_model()
        
        # Count statistics
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'students': User.objects.filter(role='STUDENT').count(),
            'teachers': User.objects.filter(role='TEACHER').count(),
        }
        
        # Try to get more statistics from other models
        try:
            from courses.models import Course
            stats['total_courses'] = Course.objects.count()
        except:
            stats['total_courses'] = 'N/A'
        
        try:
            from notifications.models import NotificationDelivery
            stats['total_notifications'] = NotificationDelivery.objects.count()
            stats['unread_notifications'] = NotificationDelivery.objects.filter(is_read=False).count()
        except:
            stats['total_notifications'] = 'N/A'
            stats['unread_notifications'] = 'N/A'
        
        print("\n" + "="*60)
        print("📊 تقرير إحصائيات النظام | System Statistics Report")
        print("="*60)
        print(f"👥 إجمالي المستخدمين: {stats['total_users']}")
        print(f"✅ المستخدمون النشطون: {stats['active_users']}")
        print(f"🎓 الطلاب: {stats['students']}")
        print(f"👨‍🏫 الأساتذة: {stats['teachers']}")
        print(f"📚 المقررات: {stats['total_courses']}")
        print(f"🔔 الإشعارات: {stats['total_notifications']}")
        print(f"📬 الإشعارات غير المقروءة: {stats['unread_notifications']}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء تقرير الأداء: {e}")


def backup_database():
    """نسخ احتياطي لقاعدة البيانات"""
    print("💾 إنشاء نسخة احتياطية...")
    try:
        from django.core.management import call_command
        from io import StringIO
        import json
        
        # Create backup directory
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"database_backup_{timestamp}.json"
        
        # Create backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            call_command('dumpdata', stdout=f, indent=2)
        
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
        
        # Keep only last 5 backups
        backup_files = sorted(backup_dir.glob("database_backup_*.json"))
        if len(backup_files) > 5:
            for old_backup in backup_files[:-5]:
                old_backup.unlink()
                print(f"🗑️  تم حذف النسخة الاحتياطية القديمة: {old_backup.name}")
                
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")


def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # Setup Django
    setup_django()
    
    print("🚀 بدء عملية تحسين الأداء...")
    print("-" * 60)
    
    # Performance optimizations
    clean_old_sessions()
    clean_old_notifications()
    clean_old_audit_logs()
    optimize_database()
    
    # System checks
    check_disk_space()
    check_database_size()
    
    # Generate reports
    generate_performance_report()
    
    # Create backup
    backup_database()
    
    print("\n" + "="*60)
    print("✅ تم الانتهاء من تحسين الأداء بنجاح!")
    print("🎉 النظام الآن محسن ويعمل بأفضل أداء")
    print("="*60)


if __name__ == '__main__':
    main()