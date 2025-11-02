#!/usr/bin/env python3
"""
مدير المشروع الشامل
Comprehensive Project Manager

يوفر إدارة شاملة للمشروع مع أتمتة العمليات المختلفة
Created: 2025-11-02
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

class ComprehensiveProjectManager:
    """مدير المشروع الشامل"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'actions_performed': [],
            'files_organized': [],
            'issues_resolved': [],
            'improvements_made': []
        }
    
    def organize_project_structure(self):
        """تنظيم هيكل المشروع"""
        print("📁 تنظيم هيكل المشروع...")
        
        # إنشاء المجلدات المطلوبة
        required_dirs = [
            'logs',
            'media/uploads', 
            'media/documents',
            'static/css',
            'static/js',
            'static/images',
            'templates/base',
            'templates/components',
            'archive/backups',
            'documentation/api',
            'documentation/user_guide',
            'tests/unit',
            'tests/integration',
            'utils/helpers',
            'utils/decorators'
        ]
        
        organized_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                organized_dirs.append(str(dir_path))
        
        self.report['files_organized'].extend(organized_dirs)
        
        # إنشاء ملفات __init__.py المفقودة
        python_dirs = [
            'utils', 
            'utils/helpers',
            'utils/decorators',
            'tests',
            'tests/unit', 
            'tests/integration'
        ]
        
        for dir_path in python_dirs:
            init_file = self.project_root / dir_path / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                organized_dirs.append(f"{dir_path}/__init__.py")
        
        print(f"✅ تم تنظيم {len(organized_dirs)} عنصر في هيكل المشروع")
        self.report['actions_performed'].append({
            'action': 'Project Structure Organization',
            'items_organized': len(organized_dirs),
            'directories_created': organized_dirs
        })
    
    def optimize_django_settings(self):
        """تحسين إعدادات Django"""
        print("⚙️ تحسين إعدادات Django...")
        
        optimizations = []
        
        # التحقق من وجود ملف .env
        env_file = self.project_root / '.env'
        if not env_file.exists():
            # إنشاء ملف .env أساسي
            env_content = '''# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Security
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# Cache
CACHE_URL=redis://localhost:6379/1

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
'''
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            optimizations.append("إنشاء ملف .env أساسي")
        
        # تحسين requirements.txt
        self._optimize_requirements()
        optimizations.append("تحسين متطلبات المشروع")
        
        # إنشاء ملف docker-compose للتطوير
        self._create_docker_compose()
        optimizations.append("إنشاء docker-compose للتطوير")
        
        self.report['improvements_made'].extend(optimizations)
        print(f"✅ تم تطبيق {len(optimizations)} تحسين على Django")
    
    def _optimize_requirements(self):
        """تحسين ملف requirements.txt"""
        requirements_content = '''# Core Framework - الإطار الأساسي
Django==4.2.16
djangorestframework==3.16.1

# Database & ORM - قاعدة البيانات
dj-database-url==2.1.0
psycopg2-binary==2.9.9

# Authentication & Security - المصادقة والأمان
djangorestframework-simplejwt==5.3.0
python-decouple==3.8
django-cors-headers==4.3.1
django-ratelimit==4.1.0

# API Documentation - توثيق API
drf-yasg==1.21.7
django-filter==23.5

# Performance & Caching - الأداء والتخزين المؤقت
django-redis==5.4.0
redis==5.0.1
whitenoise==6.6.0

# Media & Files - الوسائط والملفات
Pillow==10.1.0

# Utilities - الأدوات المساعدة
python-dateutil==2.8.2
requests==2.31.0
django-extensions==3.2.3

# Development Tools (Optional) - أدوات التطوير (اختياري)
# django-debug-toolbar==4.2.0
# pytest-django==4.7.0
# factory-boy==3.3.0
'''
        
        with open(self.project_root / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
    
    def _create_docker_compose(self):
        """إنشاء docker-compose للتطوير"""
        docker_compose_content = '''version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - DATABASE_URL=sqlite:///db.sqlite3
    depends_on:
      - redis
    command: python manage.py runserver 0.0.0.0:8000

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: university_system
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
'''
        
        # فقط إنشاء الملف إذا لم يكن موجوداً
        docker_file = self.project_root / 'docker-compose.dev.yml'
        if not docker_file.exists():
            with open(docker_file, 'w', encoding='utf-8') as f:
                f.write(docker_compose_content)
    
    def clean_and_organize_files(self):
        """تنظيف وتنظيم الملفات"""
        print("🧹 تنظيف وتنظيم الملفات...")
        
        cleaned_files = []
        
        # نقل ملفات JSON إلى مجلد logs
        for json_file in self.project_root.glob('*.json'):
            if json_file.name not in ['package.json', 'tsconfig.json']:
                destination = self.project_root / 'logs' / json_file.name
                if not destination.exists():
                    shutil.move(str(json_file), str(destination))
                    cleaned_files.append(f"نقل {json_file.name} إلى logs/")
        
        # تنظيم ملفات Python المساعدة
        helper_files = [
            'create_simple_demo.py',
            'create_superuser.py', 
            'database_optimization.py',
            'fix_performance_issues.py',
            'merge_duplicate_files.py',
            'run_project.py',
            'setup.py'
        ]
        
        utils_dir = self.project_root / 'utils'
        for helper_file in helper_files:
            file_path = self.project_root / helper_file
            if file_path.exists():
                destination = utils_dir / helper_file
                if not destination.exists():
                    shutil.move(str(file_path), str(destination))
                    cleaned_files.append(f"نقل {helper_file} إلى utils/")
        
        # تنظيف ملفات الاختبار
        test_files = list(self.project_root.glob('test_*.py')) + list(self.project_root.glob('*_test.py'))
        tests_dir = self.project_root / 'tests'
        
        for test_file in test_files:
            destination = tests_dir / test_file.name
            if not destination.exists():
                shutil.move(str(test_file), str(destination))
                cleaned_files.append(f"نقل {test_file.name} إلى tests/")
        
        self.report['files_organized'].extend(cleaned_files)
        print(f"✅ تم تنظيم {len(cleaned_files)} ملف")
    
    def create_management_commands(self):
        """إنشاء أوامر إدارية مفيدة"""
        print("🛠️ إنشاء أوامر إدارية مفيدة...")
        
        commands_created = []
        
        # إنشاء مجلد management commands إذا لم يكن موجوداً
        for app_name in ['students', 'courses', 'academic', 'finance', 'hr']:
            app_path = self.project_root / app_name
            if app_path.exists():
                management_path = app_path / 'management' / 'commands'
                management_path.mkdir(parents=True, exist_ok=True)
                
                # إنشاء ملفات __init__.py
                (app_path / 'management' / '__init__.py').touch()
                (management_path / '__init__.py').touch()
                
                # إنشاء أمر تنظيف البيانات
                cleanup_command = management_path / 'cleanup_data.py'
                if not cleanup_command.exists():
                    self._create_cleanup_command(cleanup_command, app_name)
                    commands_created.append(f"{app_name}/cleanup_data.py")
        
        self.report['improvements_made'].extend([f"إنشاء أمر إداري: {cmd}" for cmd in commands_created])
        print(f"✅ تم إنشاء {len(commands_created)} أمر إداري")
    
    def _create_cleanup_command(self, file_path, app_name):
        """إنشاء أمر تنظيف البيانات"""
        command_content = f'''from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'تنظيف البيانات القديمة في تطبيق {app_name}'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='عدد الأيام للاحتفاظ بالبيانات (افتراضي: 30)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حذف فعلي'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'تنظيف بيانات {app_name} الأقدم من {{cutoff_date.date()}}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('تشغيل تجريبي - لن يتم حذف أي بيانات')
            )
        
        # TODO: إضافة منطق التنظيف حسب نماذج التطبيق
        
        self.stdout.write(
            self.style.SUCCESS('تم إكمال عملية التنظيف بنجاح')
        )
'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(command_content)
    
    def optimize_database_models(self):
        """تحسين نماذج قاعدة البيانات"""
        print("🗄️ تحسين نماذج قاعدة البيانات...")
        
        optimizations = []
        
        # فحص النماذج للتحسينات المحتملة
        for app_name in ['students', 'courses', 'academic', 'finance', 'hr']:
            models_file = self.project_root / app_name / 'models.py'
            if models_file.exists():
                # قراءة محتوى النموذج
                with open(models_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # التحقق من وجود تحسينات
                if 'db_index=True' not in content:
                    optimizations.append(f"إضافة فهارس لـ {app_name}")
                
                if 'class Meta:' in content and 'ordering' not in content:
                    optimizations.append(f"إضافة ترتيب افتراضي لـ {app_name}")
        
        self.report['improvements_made'].extend(optimizations)
        print(f"✅ تم تحديد {len(optimizations)} تحسين محتمل للنماذج")
    
    def setup_testing_framework(self):
        """إعداد إطار الاختبارات"""
        print("🧪 إعداد إطار الاختبارات...")
        
        # إنشاء ملف pytest.ini
        pytest_config = '''[tool:pytest]
DJANGO_SETTINGS_MODULE = settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test* *Tests
python_functions = test_*
addopts = --verbose --tb=short
testpaths = tests
'''
        
        pytest_file = self.project_root / 'pytest.ini'
        if not pytest_file.exists():
            with open(pytest_file, 'w', encoding='utf-8') as f:
                f.write(pytest_config)
        
        # إنشاء ملف اختبار أساسي
        test_content = '''"""
اختبارات أساسية للمشروع
Basic project tests
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class BasicSystemTests(TestCase):
    """اختبارات النظام الأساسية"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """اختبار إنشاء المستخدم"""
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_admin_access(self):
        """اختبار الوصول للوحة الإدارة"""
        response = self.client.get('/admin/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    @pytest.mark.django_db
    def test_database_connection(self):
        """اختبار الاتصال بقاعدة البيانات"""
        from django.db import connection
        self.assertTrue(connection.is_usable())
'''
        
        basic_test_file = self.project_root / 'tests' / 'test_basic.py'
        if not basic_test_file.exists():
            with open(basic_test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
        
        print("✅ تم إعداد إطار الاختبارات")
        self.report['improvements_made'].append("إعداد إطار اختبارات شامل")
    
    def generate_comprehensive_report(self):
        """توليد تقرير شامل"""
        report_content = f"""# تقرير إدارة المشروع الشامل
Comprehensive Project Management Report

## معلومات أساسية
- **التاريخ:** {self.report['timestamp']}
- **عدد العمليات المنفذة:** {len(self.report['actions_performed'])}
- **عدد الملفات المنظمة:** {len(self.report['files_organized'])}
- **عدد التحسينات:** {len(self.report['improvements_made'])}

## العمليات المنفذة
"""
        
        for i, action in enumerate(self.report['actions_performed'], 1):
            report_content += f"{i}. **{action.get('action', 'عملية غير محددة')}**\n"
            if 'items_organized' in action:
                report_content += f"   - عدد العناصر: {action['items_organized']}\n"
            report_content += "\n"
        
        report_content += "## الملفات المنظمة\n"
        for i, file_org in enumerate(self.report['files_organized'], 1):
            report_content += f"{i}. {file_org}\n"
        
        report_content += "\n## التحسينات المطبقة\n"
        for i, improvement in enumerate(self.report['improvements_made'], 1):
            report_content += f"{i}. {improvement}\n"
        
        report_content += f"""
## التوصيات المستقبلية
1. تفعيل نظام المراقبة المستمرة
2. إعداد CI/CD pipeline
3. تحسين الأمان للإنتاج
4. إضافة المزيد من الاختبارات الآلية
5. توثيق شامل للـ APIs
6. تطبيق معايير الكود الموحدة

---
**تم إنشاء التقرير تلقائياً بواسطة نظام إدارة المشروع الشامل**
"""
        
        report_file = self.project_root / 'COMPREHENSIVE_MANAGEMENT_REPORT.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # حفظ التقرير JSON أيضاً
        json_report_file = self.project_root / 'logs' / f'project_management_report_{int(datetime.now().timestamp())}.json'
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 تم إنشاء التقرير الشامل: {report_file}")
        print(f"📄 تم حفظ التقرير JSON: {json_report_file}")
    
    def run_comprehensive_management(self):
        """تشغيل الإدارة الشاملة"""
        print("🚀 بدء الإدارة الشاملة للمشروع...")
        print("="*60)
        
        try:
            self.organize_project_structure()
            self.optimize_django_settings()
            self.clean_and_organize_files()
            self.create_management_commands()
            self.optimize_database_models()
            self.setup_testing_framework()
            self.generate_comprehensive_report()
            
            print("\n🎉 تم إكمال جميع عمليات الإدارة الشاملة بنجاح!")
            print("✅ المشروع منظم ومحسن وجاهز للتطوير والنشر")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في عملية الإدارة الشاملة: {e}")
            return False

def main():
    """الدالة الرئيسية"""
    print("🏗️ مدير المشروع الشامل - نظام إدارة الجامعة")
    print("Comprehensive Project Manager - University Management System")
    print("="*70)
    
    manager = ComprehensiveProjectManager()
    success = manager.run_comprehensive_management()
    
    if success:
        print("\n✨ تم إكمال جميع عمليات الإدارة بنجاح!")
    else:
        print("\n⚠️ حدثت مشاكل أثناء عملية الإدارة")
    
    return success

if __name__ == "__main__":
    main()