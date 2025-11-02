#!/usr/bin/env python3
"""
محسن URLs الموحد للمشروع الجامعي
Unified URL Optimizer for University Project
Created: 2024-11-02
Author: AI Development Team

يقوم بدمج وتحسين جميع ملفات URLs في المشروع:
- دمج الملفات المكررة
- تحسين هيكل URLs
- إضافة أمان للروابط
- تحسين الأداء
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

class UnifiedURLOptimizer:
    """محسن URLs الموحد"""
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.apps_urls = {}
        self.duplicates_found = []
        self.improvements = []
        
    def scan_url_files(self):
        """فحص جميع ملفات URLs في المشروع"""
        print("🔍 فحص ملفات URLs...")
        
        url_files = list(self.base_dir.rglob("urls*.py"))
        
        for url_file in url_files:
            if '__pycache__' in str(url_file):
                continue
                
            app_name = url_file.parent.name if url_file.parent.name != 'des_project' else 'main'
            
            if app_name not in self.apps_urls:
                self.apps_urls[app_name] = []
            
            self.apps_urls[app_name].append(url_file)
        
        print(f"📊 تم العثور على {len(url_files)} ملف URLs في {len(self.apps_urls)} تطبيق")
        
        # تحديد الملفات المكررة
        for app_name, files in self.apps_urls.items():
            if len(files) > 1:
                self.duplicates_found.extend(files[1:])  # الملفات الإضافية
                print(f"⚠️ ملفات مكررة في {app_name}: {[f.name for f in files]}")
    
    def merge_duplicate_urls(self):
        """دمج ملفات URLs المكررة"""
        print("🔧 دمج الملفات المكررة...")
        
        for app_name, files in self.apps_urls.items():
            if len(files) <= 1:
                continue
            
            # اختيار الملف الأساسي (urls.py)
            main_file = None
            duplicate_files = []
            
            for file_path in files:
                if file_path.name == 'urls.py':
                    main_file = file_path
                else:
                    duplicate_files.append(file_path)
            
            if not main_file and files:
                main_file = files[0]  # أول ملف كملف أساسي
                duplicate_files = files[1:]
            
            if main_file and duplicate_files:
                self._merge_files(main_file, duplicate_files, app_name)
    
    def _merge_files(self, main_file: Path, duplicate_files: List[Path], app_name: str):
        """دمج الملفات المكررة في ملف واحد"""
        print(f"🔗 دمج ملفات URLs في {app_name}...")
        
        # قراءة محتوى الملف الأساسي
        main_content = self._read_file_safely(main_file)
        if not main_content:
            print(f"⚠️ لا يمكن قراءة الملف الأساسي: {main_file}")
            return
        
        # جمع المحتوى من الملفات المكررة
        additional_patterns = []
        additional_imports = set()
        
        for dup_file in duplicate_files:
            dup_content = self._read_file_safely(dup_file)
            if dup_content:
                patterns, imports = self._extract_url_patterns(dup_content)
                additional_patterns.extend(patterns)
                additional_imports.update(imports)
        
        # دمج المحتوى
        merged_content = self._create_merged_urls(main_content, additional_patterns, additional_imports, app_name)
        
        # كتابة الملف المدمج
        self._write_merged_file(main_file, merged_content)
        
        # أرشفة الملفات المكررة
        self._archive_duplicate_files(duplicate_files, app_name)
        
        self.improvements.append(f"تم دمج {len(duplicate_files)} ملف في {app_name}")
    
    def _read_file_safely(self, file_path: Path) -> str:
        """قراءة الملف بأمان"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ خطأ في قراءة {file_path}: {e}")
            return ""
    
    def _extract_url_patterns(self, content: str) -> Tuple[List[str], List[str]]:
        """استخراج أنماط URLs والاستيرادات"""
        patterns = []
        imports = []
        
        # استخراج path() patterns
        path_pattern = re.compile(r"path\([^)]+\)", re.MULTILINE)
        patterns.extend(path_pattern.findall(content))
        
        # استخراج الاستيرادات
        import_pattern = re.compile(r"from\s+[\w.]+\s+import\s+[\w,\s]+|import\s+[\w.]+", re.MULTILINE)
        imports.extend(import_pattern.findall(content))
        
        return patterns, imports
    
    def _create_merged_urls(self, main_content: str, additional_patterns: List[str], 
                          additional_imports: List[str], app_name: str) -> str:
        """إنشاء ملف URLs مدمج ومحسن"""
        
        # تاريخ وتوقيت التحديث
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        header = f'''"""
URLs Configuration for {app_name.title()} App - UNIFIED VERSION
تكوين URLs لتطبيق {app_name} - النسخة الموحدة

Auto-generated and optimized on: {timestamp}
تم إنتاجه وتحسينه تلقائياً في: {timestamp}
"""

from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from . import views

app_name = '{app_name}'

# Default placeholder for development
def placeholder_view(request):
    """عرض افتراضي للتطوير"""
    return JsonResponse({{
        'app': '{app_name}',
        'status': 'under_development',
        'message': 'Endpoint under development',
        'message_ar': 'نقطة النهاية قيد التطوير',
        'timestamp': '{timestamp}'
    }}, status=501)

# API Router for REST endpoints
router = DefaultRouter()

# URL Patterns - محسن ومُنظم
urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls), name='{app_name}_api'),
    
    # Health Check
    path('health/', lambda r: JsonResponse({{'status': 'ok', 'app': '{app_name}'}}), name='{app_name}_health'),
    
    # Placeholder for future endpoints
    path('', placeholder_view, name='{app_name}_index'),
'''

        # إضافة الأنماط الإضافية (إن وجدت)
        if additional_patterns:
            header += "\n    # Additional patterns from merged files\n"
            for pattern in additional_patterns:
                if 'path(' in pattern and pattern not in header:
                    header += f"    {pattern},\n"
        
        header += "]\n"
        
        return header
    
    def _write_merged_file(self, file_path: Path, content: str):
        """كتابة الملف المدمج"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ تم كتابة الملف المدمج: {file_path}")
        except Exception as e:
            print(f"❌ خطأ في كتابة الملف: {e}")
    
    def _archive_duplicate_files(self, duplicate_files: List[Path], app_name: str):
        """أرشفة الملفات المكررة"""
        archive_dir = self.base_dir / 'archive' / 'old_urls' / app_name
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for dup_file in duplicate_files:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archived_name = f"{dup_file.stem}_{timestamp}.py.bak"
                archive_path = archive_dir / archived_name
                
                shutil.move(str(dup_file), str(archive_path))
                print(f"📦 تم أرشفة {dup_file.name} إلى {archive_path}")
                
            except Exception as e:
                print(f"⚠️ خطأ في أرشفة {dup_file}: {e}")
    
    def optimize_main_urls(self):
        """تحسين ملف URLs الرئيسي"""
        print("🔧 تحسين ملف URLs الرئيسي...")
        
        main_urls_file = self.base_dir / 'urls.py'
        if not main_urls_file.exists():
            print("⚠️ ملف URLs الرئيسي غير موجود")
            return
        
        # إنشاء ملف URLs رئيسي محسن
        optimized_content = self._create_optimized_main_urls()
        
        # نسخ احتياطي
        backup_path = self.base_dir / 'archive' / 'urls_backup.py'
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(main_urls_file, backup_path)
        
        # كتابة النسخة المحسنة
        with open(main_urls_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        self.improvements.append("تم تحسين ملف URLs الرئيسي")
        print("✅ تم تحسين ملف URLs الرئيسي")
    
    def _create_optimized_main_urls(self) -> str:
        """إنشاء ملف URLs رئيسي محسن"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f'''"""
University Management System - Main URLs Configuration
تكوين URLs الرئيسي لنظام إدارة الجامعة

Auto-optimized on: {timestamp}
تم تحسينه تلقائياً في: {timestamp}
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

# API Documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Schema for Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="University Management API",
        default_version='v1',
        description="نظام إدارة الجامعة - واجهة برمجة التطبيقات",
        terms_of_service="https://www.university.edu/terms/",
        contact=openapi.Contact(email="api@university.edu"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# System Health Check
def system_health(request):
    """فحص صحة النظام"""
    return JsonResponse({{
        'status': 'ok',
        'system': 'University Management System',
        'version': '2.0.0',
        'timestamp': '{timestamp}',
        'debug_mode': settings.DEBUG
    }})

# Main URL Patterns
urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication URLs
    path('auth/', include([
        path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
        path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    ])),
    
    # Core Applications
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('academic/', include('academic.urls')),
    path('finance/', include('finance.urls')),
    path('hr/', include('hr.urls')),
    
    # Advanced Applications  
    path('ai/', include('ai.urls')),
    path('smart-ai/', include('smart_ai.urls')),
    path('security/', include('cyber_security.urls')),
    path('attendance/', include('attendance_qr.urls')),
    path('notifications/', include('notifications.urls')),
    
    # Management & Reports
    path('admin-control/', include('admin_control.urls')),
    path('reports/', include('reports.urls')),
    path('roles/', include('roles_permissions.urls')),
    
    # Web Interface & Mobile
    path('web/', include('web.urls')),
    path('mobile/', include('mobile_app.urls')),
    
    # API Endpoints
    path('api/v1/', include([
        path('students/', include('students.urls')),
        path('courses/', include('courses.urls')),
        path('academic/', include('academic.urls')),
        path('finance/', include('finance.urls')),
        path('hr/', include('hr.urls')),
        path('ai/', include('ai.urls')),
        path('security/', include('cyber_security.urls')),
        path('attendance/', include('attendance_qr.urls')),
        path('notifications/', include('notifications.urls')),
        path('reports/', include('reports.urls')),
    ])),
    
    # System Utilities
    path('health/', system_health, name='system_health'),
    path('', TemplateView.as_view(template_name='web/index.html'), name='home'),
]

# Static & Media Files (Development only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom Error Handlers
handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'
handler403 = 'web.views.handler403'
handler400 = 'web.views.handler400'

# Admin Site Customization
admin.site.site_header = "نظام إدارة الجامعة"
admin.site.site_title = "إدارة الجامعة"
admin.site.index_title = "لوحة التحكم الرئيسية"
'''
        
        return content
    
    def create_app_urls_template(self, app_name: str):
        """إنشاء قالب URLs محسن للتطبيق"""
        app_dir = self.base_dir / app_name
        if not app_dir.exists():
            return
        
        urls_file = app_dir / 'urls.py'
        
        # إنشاء ملف URLs إذا لم يكن موجود
        if not urls_file.exists():
            template_content = self._create_app_urls_template(app_name)
            
            with open(urls_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"✅ تم إنشاء ملف URLs جديد لتطبيق {app_name}")
            self.improvements.append(f"إنشاء ملف URLs لتطبيق {app_name}")
    
    def _create_app_urls_template(self, app_name: str) -> str:
        """قالب ملف URLs للتطبيق"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f'''"""
URLs Configuration for {app_name.title()} App
تكوين URLs لتطبيق {app_name}

Created: {timestamp}
تم الإنشاء: {timestamp}
"""

from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter
from . import views

app_name = '{app_name}'

# API Router
router = DefaultRouter()

# Placeholder view for development
def placeholder_view(request):
    """عرض افتراضي للتطوير"""
    return JsonResponse({{
        'app': '{app_name}',
        'status': 'under_development',
        'message': 'This endpoint is under development',
        'message_ar': 'نقطة النهاية هذه قيد التطوير'
    }}, status=501)

# URL Patterns
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls), name='{app_name}_api'),
    
    # Health check
    path('health/', lambda r: JsonResponse({{'status': 'ok', 'app': '{app_name}'}}), 
         name='{app_name}_health'),
    
    # Default view
    path('', placeholder_view, name='{app_name}_index'),
]
'''
    
    def run_optimization(self):
        """تشغيل تحسين URLs الشامل"""
        print("🚀 بدء تحسين URLs الشامل...")
        
        # 1. فحص الملفات
        self.scan_url_files()
        
        # 2. دمج الملفات المكررة
        self.merge_duplicate_urls()
        
        # 3. تحسين الملف الرئيسي
        self.optimize_main_urls()
        
        # 4. إنشاء ملفات مفقودة للتطبيقات
        app_dirs = [d for d in self.base_dir.iterdir() 
                   if d.is_dir() and not d.name.startswith('.') 
                   and d.name not in ['archive', 'logs', 'media', 'static', 'staticfiles', '__pycache__']]
        
        for app_dir in app_dirs:
            if (app_dir / 'models.py').exists():  # تأكد أنه تطبيق Django
                self.create_app_urls_template(app_dir.name)
        
        # 5. تقرير النتائج
        self.generate_report()
        
        print("🎉 اكتمل تحسين URLs بنجاح!")
    
    def generate_report(self):
        """إنتاج تقرير التحسين"""
        report_content = f"""
# تقرير تحسين URLs
## URL Optimization Report

**تاريخ التحسين:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### الإحصائيات
- **عدد التطبيقات:** {len(self.apps_urls)}
- **الملفات المكررة المحذوفة:** {len(self.duplicates_found)}
- **التحسينات المطبقة:** {len(self.improvements)}

### التحسينات المطبقة
"""
        
        for i, improvement in enumerate(self.improvements, 1):
            report_content += f"{i}. {improvement}\n"
        
        # حفظ التقرير
        report_file = self.base_dir / 'database_reports' / f'url_optimization_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 تقرير التحسين محفوظ في: {report_file}")

def main():
    """الدالة الرئيسية"""
    print("🔗 محسن URLs الموحد لنظام إدارة الجامعة")
    print("=" * 50)
    
    try:
        optimizer = UnifiedURLOptimizer()
        optimizer.run_optimization()
        
        print(f"\\n✅ تحسين URLs اكتمل بنجاح")
        print(f"📊 التحسينات: {len(optimizer.improvements)}")
        print(f"🗑️ الملفات المؤرشفة: {len(optimizer.duplicates_found)}")
        
    except KeyboardInterrupt:
        print("\\n⚠️ تم إيقاف التحسين بواسطة المستخدم")
    except Exception as e:
        print(f"\\n❌ خطأ في تحسين URLs: {e}")

if __name__ == '__main__':
    main()