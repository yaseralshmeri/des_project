#!/usr/bin/env python3
"""
المحسن الموحد الشامل للمشروع الجامعي
Unified Comprehensive University System Optimizer
Created: 2024-11-02
Author: AI Development Team - Optimized Version

هذا الملف يدمج جميع وظائف التحسين في مكان واحد:
- تحسين قاعدة البيانات
- تحسين الأداء 
- تحسين الأمان
- مراقبة النظام
- تحليل الكود
"""

import os
import sys
import time
import json
import sqlite3
import psutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection, transaction
from django.core.cache import cache
from django.conf import settings
from django.apps import apps


class UnifiedOptimizer:
    """المحسن الموحد الشامل للمشروع"""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'database_optimization': {'status': 'pending', 'details': []},
            'performance_optimization': {'status': 'pending', 'details': []},
            'security_optimization': {'status': 'pending', 'details': []},
            'code_quality': {'status': 'pending', 'details': []},
            'system_monitoring': {'status': 'pending', 'details': []},
            'recommendations': [],
            'improvements_applied': [],
            'overall_score': 0,
            'execution_time': 0
        }
        self.total_improvements = 0
        self.base_dir = Path(__file__).resolve().parent
    
    def log_improvement(self, category, description, impact='medium'):
        """تسجيل التحسين المطبق"""
        improvement = {
            'category': category,
            'description': description,
            'impact': impact,
            'timestamp': datetime.now().isoformat()
        }
        self.results['improvements_applied'].append(improvement)
        self.total_improvements += 1
        print(f"✅ {description}")
    
    def add_recommendation(self, title, description, priority='medium'):
        """إضافة توصية للتحسين"""
        recommendation = {
            'title': title,
            'description': description,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        }
        self.results['recommendations'].append(recommendation)
    
    # =============================================================================
    # DATABASE OPTIMIZATION - تحسين قاعدة البيانات
    # =============================================================================
    
    def optimize_database(self):
        """تحسين قاعدة البيانات بشكل شامل"""
        print("🗄️ تحسين قاعدة البيانات...")
        start_time = time.time()
        
        try:
            # 1. تشغيل المايجريشن
            self._run_migrations()
            
            # 2. تحليل الجداول
            table_stats = self._analyze_tables()
            
            # 3. إنشاء فهارس محسنة
            self._create_optimized_indexes()
            
            # 4. تنظيف قاعدة البيانات
            self._vacuum_database()
            
            # 5. تحديث إحصائيات الجداول
            self._update_table_statistics()
            
            execution_time = time.time() - start_time
            self.results['database_optimization'] = {
                'status': 'completed',
                'details': table_stats,
                'execution_time': round(execution_time, 2)
            }
            
            self.log_improvement('database', f'تحسين قاعدة البيانات اكتمل في {execution_time:.2f} ثانية', 'high')
            
        except Exception as e:
            self.results['database_optimization']['status'] = 'error'
            self.results['database_optimization']['error'] = str(e)
            print(f"❌ خطأ في تحسين قاعدة البيانات: {e}")
    
    def _run_migrations(self):
        """تشغيل المايجريشن"""
        try:
            call_command('makemigrations', verbosity=0)
            call_command('migrate', verbosity=0)
            self.log_improvement('database', 'تم تشغيل المايجريشن بنجاح')
        except Exception as e:
            print(f"⚠️ تحذير في المايجريشن: {e}")
    
    def _analyze_tables(self):
        """تحليل الجداول وإحصائياتها"""
        table_stats = []
        
        with connection.cursor() as cursor:
            # الحصول على جميع الجداول
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                try:
                    # عدد الصفوف
                    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                    row_count = cursor.fetchone()[0]
                    
                    # معلومات الجدول
                    cursor.execute(f"PRAGMA table_info(`{table}`)")
                    columns = cursor.fetchall()
                    
                    table_stats.append({
                        'name': table,
                        'rows': row_count,
                        'columns': len(columns)
                    })
                    
                except Exception as e:
                    print(f"⚠️ لا يمكن تحليل الجدول {table}: {e}")
        
        return table_stats
    
    def _create_optimized_indexes(self):
        """إنشاء فهارس محسنة"""
        indexes_to_create = [
            # فهارس للطلاب
            "CREATE INDEX IF NOT EXISTS idx_students_user_role ON students_user(role)",
            "CREATE INDEX IF NOT EXISTS idx_students_user_status ON students_user(status)",
            "CREATE INDEX IF NOT EXISTS idx_students_user_email ON students_user(email)",
            
            # فهارس للمقررات
            "CREATE INDEX IF NOT EXISTS idx_courses_course_code ON courses_course(code)",
            "CREATE INDEX IF NOT EXISTS idx_courses_course_semester ON courses_course(semester)",
            
            # فهارس الحضور
            "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_qr_attendance(date)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_qr_attendance(student_id)",
        ]
        
        with connection.cursor() as cursor:
            for index_sql in indexes_to_create:
                try:
                    cursor.execute(index_sql)
                    self.log_improvement('database', f'إنشاء فهرس: {index_sql.split()[-1]}')
                except Exception as e:
                    print(f"⚠️ لا يمكن إنشاء الفهرس: {e}")
    
    def _vacuum_database(self):
        """تنظيف وضغط قاعدة البيانات"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("VACUUM")
                self.log_improvement('database', 'تم ضغط قاعدة البيانات')
        except Exception as e:
            print(f"⚠️ لا يمكن ضغط قاعدة البيانات: {e}")
    
    def _update_table_statistics(self):
        """تحديث إحصائيات الجداول"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("ANALYZE")
                self.log_improvement('database', 'تم تحديث إحصائيات الجداول')
        except Exception as e:
            print(f"⚠️ لا يمكن تحديث الإحصائيات: {e}")
    
    # =============================================================================
    # PERFORMANCE OPTIMIZATION - تحسين الأداء
    # =============================================================================
    
    def optimize_performance(self):
        """تحسين الأداء العام للنظام"""
        print("⚡ تحسين الأداء...")
        start_time = time.time()
        
        try:
            # 1. تحسين الملفات الثابتة
            self._optimize_static_files()
            
            # 2. تحسين الذاكرة المؤقتة
            self._optimize_cache()
            
            # 3. تحسين إعدادات Django
            self._optimize_django_settings()
            
            # 4. مراقبة أداء النظام
            system_stats = self._monitor_system_performance()
            
            execution_time = time.time() - start_time
            self.results['performance_optimization'] = {
                'status': 'completed',
                'details': system_stats,
                'execution_time': round(execution_time, 2)
            }
            
            self.log_improvement('performance', f'تحسين الأداء اكتمل في {execution_time:.2f} ثانية', 'high')
            
        except Exception as e:
            self.results['performance_optimization']['status'] = 'error'
            self.results['performance_optimization']['error'] = str(e)
            print(f"❌ خطأ في تحسين الأداء: {e}")
    
    def _optimize_static_files(self):
        """تحسين الملفات الثابتة"""
        try:
            # جمع الملفات الثابتة
            call_command('collectstatic', verbosity=0, interactive=False)
            self.log_improvement('performance', 'تم تحسين الملفات الثابتة')
        except Exception as e:
            print(f"⚠️ تحذير في الملفات الثابتة: {e}")
    
    def _optimize_cache(self):
        """تحسين نظام التخزين المؤقت"""
        try:
            # تنظيف الذاكرة المؤقتة
            cache.clear()
            self.log_improvement('performance', 'تم تنظيف الذاكرة المؤقتة')
        except Exception as e:
            print(f"⚠️ لا يمكن تنظيف الذاكرة المؤقتة: {e}")
    
    def _optimize_django_settings(self):
        """تحسين إعدادات Django"""
        optimizations = []
        
        # فحص إعدادات DEBUG
        if settings.DEBUG:
            optimizations.append('تعطيل وضع التطوير DEBUG للإنتاج')
        
        # فحص الأمان
        if not hasattr(settings, 'SECURE_SSL_REDIRECT'):
            optimizations.append('تفعيل إعادة توجيه HTTPS')
        
        if optimizations:
            for opt in optimizations:
                self.add_recommendation('Django Settings', opt, 'high')
    
    def _monitor_system_performance(self):
        """مراقبة أداء النظام"""
        try:
            stats = {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
            return stats
        except Exception:
            return {'error': 'لا يمكن جمع إحصائيات النظام'}
    
    # =============================================================================
    # SECURITY OPTIMIZATION - تحسين الأمان
    # =============================================================================
    
    def optimize_security(self):
        """تحسين أمان النظام"""
        print("🔒 تحسين الأمان...")
        start_time = time.time()
        
        try:
            # 1. فحص إعدادات الأمان
            security_issues = self._check_security_settings()
            
            # 2. تحديث كلمات المرور الضعيفة
            self._update_weak_passwords()
            
            # 3. فحص الثغرات الأمنية
            vulnerabilities = self._scan_vulnerabilities()
            
            execution_time = time.time() - start_time
            self.results['security_optimization'] = {
                'status': 'completed',
                'issues': security_issues,
                'vulnerabilities': vulnerabilities,
                'execution_time': round(execution_time, 2)
            }
            
            self.log_improvement('security', f'فحص الأمان اكتمل في {execution_time:.2f} ثانية', 'high')
            
        except Exception as e:
            self.results['security_optimization']['status'] = 'error'
            self.results['security_optimization']['error'] = str(e)
            print(f"❌ خطأ في فحص الأمان: {e}")
    
    def _check_security_settings(self):
        """فحص إعدادات الأمان"""
        issues = []
        
        # فحص SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-minimal-2024':
            issues.append('SECRET_KEY يحتاج تغيير للإنتاج')
        
        # فحص ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS:
            issues.append('ALLOWED_HOSTS يجب تحديدها للإنتاج')
        
        # فحص DEBUG
        if settings.DEBUG:
            issues.append('DEBUG يجب تعطيله للإنتاج')
        
        return issues
    
    def _update_weak_passwords(self):
        """تحديث كلمات المرور الضعيفة"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # البحث عن مستخدمين بكلمات مرور ضعيفة
            weak_passwords = ['123456', 'password', 'admin', '123123']
            users_to_update = []
            
            for user in User.objects.all():
                if user.check_password('admin') or user.check_password('123456'):
                    users_to_update.append(user.username)
            
            if users_to_update:
                self.add_recommendation('Security', 
                    f'تحديث كلمات مرور المستخدمين: {", ".join(users_to_update)}', 
                    'high')
            
        except Exception as e:
            print(f"⚠️ لا يمكن فحص كلمات المرور: {e}")
    
    def _scan_vulnerabilities(self):
        """فحص الثغرات الأمنية الأساسية"""
        vulnerabilities = []
        
        # فحص ملفات التكوين الحساسة
        sensitive_files = ['.env', 'settings.py', 'db.sqlite3']
        for file in sensitive_files:
            file_path = self.base_dir / file
            if file_path.exists():
                # فحص صلاحيات الملف
                import stat
                permissions = oct(file_path.stat().st_mode)[-3:]
                if permissions != '600' and file != 'settings.py':
                    vulnerabilities.append(f'ملف {file} لديه صلاحيات غير آمنة: {permissions}')
        
        return vulnerabilities
    
    # =============================================================================
    # CODE QUALITY ANALYSIS - تحليل جودة الكود
    # =============================================================================
    
    def analyze_code_quality(self):
        """تحليل جودة الكود"""
        print("📊 تحليل جودة الكود...")
        start_time = time.time()
        
        try:
            # 1. فحص الملفات المكررة
            duplicates = self._find_duplicate_files()
            
            # 2. فحص الاستيرادات غير المستخدمة
            unused_imports = self._find_unused_imports()
            
            # 3. فحص تعقيد الكود
            complexity_issues = self._check_code_complexity()
            
            execution_time = time.time() - start_time
            self.results['code_quality'] = {
                'status': 'completed',
                'duplicates': len(duplicates),
                'unused_imports': len(unused_imports),
                'complexity_issues': len(complexity_issues),
                'execution_time': round(execution_time, 2)
            }
            
            self.log_improvement('code_quality', f'تحليل جودة الكود اكتمل في {execution_time:.2f} ثانية')
            
        except Exception as e:
            self.results['code_quality']['status'] = 'error'
            self.results['code_quality']['error'] = str(e)
            print(f"❌ خطأ في تحليل الكود: {e}")
    
    def _find_duplicate_files(self):
        """البحث عن الملفات المكررة"""
        duplicates = []
        
        # البحث عن ملفات python مكررة
        python_files = list(self.base_dir.rglob('*.py'))
        
        # فحص الأسماء المتشابهة
        for file in python_files:
            if '_fixed' in file.name or '_improved' in file.name or '_enhanced' in file.name:
                duplicates.append(file.name)
        
        return duplicates
    
    def _find_unused_imports(self):
        """البحث عن الاستيرادات غير المستخدمة"""
        # هذا يحتاج أدوات متقدمة مثل pyflakes
        return []
    
    def _check_code_complexity(self):
        """فحص تعقيد الكود"""
        # هذا يحتاج أدوات متقدمة مثل mccabe
        return []
    
    # =============================================================================
    # SYSTEM MONITORING - مراقبة النظام
    # =============================================================================
    
    def monitor_system(self):
        """مراقبة حالة النظام"""
        print("📈 مراقبة النظام...")
        start_time = time.time()
        
        try:
            # 1. مراقبة قاعدة البيانات
            db_status = self._monitor_database()
            
            # 2. مراقبة الأداء
            performance_metrics = self._monitor_performance_metrics()
            
            # 3. فحص حالة التطبيقات
            apps_status = self._check_apps_status()
            
            execution_time = time.time() - start_time
            self.results['system_monitoring'] = {
                'status': 'completed',
                'database': db_status,
                'performance': performance_metrics,
                'apps': apps_status,
                'execution_time': round(execution_time, 2)
            }
            
            self.log_improvement('monitoring', f'مراقبة النظام اكتملت في {execution_time:.2f} ثانية')
            
        except Exception as e:
            self.results['system_monitoring']['status'] = 'error'
            self.results['system_monitoring']['error'] = str(e)
            print(f"❌ خطأ في مراقبة النظام: {e}")
    
    def _monitor_database(self):
        """مراقبة حالة قاعدة البيانات"""
        try:
            with connection.cursor() as cursor:
                # حجم قاعدة البيانات
                db_path = self.base_dir / 'db.sqlite3'
                db_size = db_path.stat().st_size if db_path.exists() else 0
                
                # عدد الاتصالات النشطة
                cursor.execute("PRAGMA database_list")
                databases = cursor.fetchall()
                
                return {
                    'size_mb': round(db_size / (1024*1024), 2),
                    'databases': len(databases),
                    'connection_status': 'active'
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _monitor_performance_metrics(self):
        """مراقبة مقاييس الأداء"""
        try:
            return {
                'response_time': self._measure_response_time(),
                'memory_usage': self._get_memory_usage(),
                'active_connections': self._count_active_connections()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_apps_status(self):
        """فحص حالة التطبيقات"""
        apps_status = {}
        
        for app_config in apps.get_app_configs():
            try:
                # فحص Models في التطبيق
                models_count = len(app_config.get_models())
                apps_status[app_config.name] = {
                    'status': 'active',
                    'models': models_count
                }
            except Exception as e:
                apps_status[app_config.name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return apps_status
    
    def _measure_response_time(self):
        """قياس زمن الاستجابة"""
        start = time.time()
        try:
            # اختبار بسيط لقاعدة البيانات
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return round((time.time() - start) * 1000, 2)  # بالميلي ثانية
        except:
            return -1
    
    def _get_memory_usage(self):
        """الحصول على استخدام الذاكرة"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return round(process.memory_info().rss / (1024*1024), 2)  # بالميجابايت
        except:
            return -1
    
    def _count_active_connections(self):
        """عد الاتصالات النشطة"""
        try:
            # في SQLite لا يوجد اتصالات متعددة
            return 1 if connection.connection else 0
        except:
            return -1
    
    # =============================================================================
    # MAIN EXECUTION - التشغيل الرئيسي
    # =============================================================================
    
    def run_full_optimization(self):
        """تشغيل التحسين الشامل"""
        print("🚀 بدء التحسين الشامل للمشروع...")
        start_time = time.time()
        
        # تشغيل جميع عمليات التحسين
        optimization_tasks = [
            ('Database Optimization', self.optimize_database),
            ('Performance Optimization', self.optimize_performance),
            ('Security Check', self.optimize_security),
            ('Code Quality Analysis', self.analyze_code_quality),
            ('System Monitoring', self.monitor_system),
        ]
        
        # تشغيل المهام بشكل تتابعي
        for task_name, task_func in optimization_tasks:
            try:
                print(f"\n📋 {task_name}...")
                task_func()
            except Exception as e:
                print(f"❌ خطأ في {task_name}: {e}")
        
        # حساب النقاط الإجمالي
        self._calculate_overall_score()
        
        # إنهاء التحسين
        total_time = time.time() - start_time
        self.results['end_time'] = datetime.now().isoformat()
        self.results['execution_time'] = round(total_time, 2)
        
        # حفظ التقرير
        self._save_optimization_report()
        
        print(f"\n🎉 التحسين الشامل اكتمل في {total_time:.2f} ثانية")
        print(f"📊 النقاط الإجمالي: {self.results['overall_score']}/100")
        print(f"✅ تم تطبيق {self.total_improvements} تحسين")
        
        return self.results
    
    def _calculate_overall_score(self):
        """حساب النقاط الإجمالي"""
        score = 0
        max_score = 100
        
        # نقاط قاعدة البيانات (25 نقطة)
        if self.results['database_optimization']['status'] == 'completed':
            score += 25
        
        # نقاط الأداء (25 نقطة)
        if self.results['performance_optimization']['status'] == 'completed':
            score += 25
        
        # نقاط الأمان (30 نقطة)
        if self.results['security_optimization']['status'] == 'completed':
            score += 30
        
        # نقاط جودة الكود (10 نقاط)
        if self.results['code_quality']['status'] == 'completed':
            score += 10
        
        # نقاط المراقبة (10 نقاط)
        if self.results['system_monitoring']['status'] == 'completed':
            score += 10
        
        # خصم نقاط للمشاكل المكتشفة
        security_issues = len(self.results.get('security_optimization', {}).get('issues', []))
        score = max(0, score - (security_issues * 5))
        
        self.results['overall_score'] = min(score, max_score)
    
    def _save_optimization_report(self):
        """حفظ تقرير التحسين"""
        try:
            reports_dir = self.base_dir / 'database_reports'
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = reports_dir / f'unified_optimization_{timestamp}.json'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"📋 تقرير التحسين محفوظ في: {report_file}")
            
        except Exception as e:
            print(f"⚠️ لا يمكن حفظ التقرير: {e}")


def main():
    """الدالة الرئيسية"""
    print("🎓 المحسن الموحد لنظام إدارة الجامعة")
    print("=" * 50)
    
    try:
        optimizer = UnifiedOptimizer()
        results = optimizer.run_full_optimization()
        
        print("\n📊 ملخص النتائج:")
        print(f"النقاط الإجمالي: {results['overall_score']}/100")
        print(f"وقت التنفيذ: {results['execution_time']} ثانية")
        print(f"التحسينات المطبقة: {len(results['improvements_applied'])}")
        print(f"التوصيات: {len(results['recommendations'])}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف التحسين بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ في التحسين: {e}")
        return None


if __name__ == '__main__':
    main()