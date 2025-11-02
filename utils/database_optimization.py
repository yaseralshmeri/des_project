#!/usr/bin/env python3
"""
تحسين قاعدة البيانات - إضافة فهارس محسنة
Database Optimization - Enhanced Indexes

تم إنشاؤه في: 2025-11-02
يحتوي على تحسينات الأداء وفهارس قاعدة البيانات المتقدمة
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import execute_from_command_line

class DatabaseOptimizer:
    """مُحسن قاعدة البيانات المتقدم"""
    
    def __init__(self):
        self.cursor = connection.cursor()
    
    def add_performance_indexes(self):
        """إضافة فهارس الأداء المحسنة"""
        
        # فهارس للمستخدمين والطلاب
        indexes = [
            # فهارس المستخدمين
            "CREATE INDEX IF NOT EXISTS idx_users_role_status ON students_user (role, status);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON students_user (email);",
            "CREATE INDEX IF NOT EXISTS idx_users_student_id ON students_user (student_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_employee_id ON students_user (employee_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_activity ON students_user (last_activity);",
            
            # فهارس الملفات الأكاديمية للطلاب
            "CREATE INDEX IF NOT EXISTS idx_student_profiles_gpa ON students_studentprofile (cumulative_gpa);",
            "CREATE INDEX IF NOT EXISTS idx_student_profiles_level ON students_studentprofile (academic_level, current_semester);",
            "CREATE INDEX IF NOT EXISTS idx_student_profiles_college_dept ON students_studentprofile (college_id, department_id);",
            "CREATE INDEX IF NOT EXISTS idx_student_profiles_standing ON students_studentprofile (academic_standing);",
            "CREATE INDEX IF NOT EXISTS idx_student_profiles_graduation ON students_studentprofile (expected_graduation_date);",
            
            # فهارس الأساتذة
            "CREATE INDEX IF NOT EXISTS idx_teacher_profiles_rank ON students_teacherprofile (academic_rank);",
            "CREATE INDEX IF NOT EXISTS idx_teacher_profiles_college_dept ON students_teacherprofile (college_id, department_id);",
            "CREATE INDEX IF NOT EXISTS idx_teacher_profiles_employment ON students_teacherprofile (employment_type);",
            
            # فهارس النشاطات
            "CREATE INDEX IF NOT EXISTS idx_user_activity_user_timestamp ON students_useractivity (user_id, timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_user_activity_action_timestamp ON students_useractivity (action, timestamp);",
            
            # فهارس الوثائق
            "CREATE INDEX IF NOT EXISTS idx_student_docs_type_verified ON students_studentdocument (document_type, is_verified);",
            "CREATE INDEX IF NOT EXISTS idx_student_docs_upload_date ON students_studentdocument (uploaded_at);",
        ]
        
        try:
            for index in indexes:
                print(f"إضافة فهرس: {index[:50]}...")
                self.cursor.execute(index)
            
            print("✅ تم إنشاء جميع الفهارس بنجاح!")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الفهارس: {e}")
            return False
    
    def analyze_database(self):
        """تحليل قاعدة البيانات للحصول على إحصائيات"""
        
        try:
            # إحصائيات المستخدمين
            self.cursor.execute("SELECT role, COUNT(*) FROM students_user GROUP BY role;")
            users_stats = self.cursor.fetchall()
            
            print("\n📊 إحصائيات المستخدمين:")
            for role, count in users_stats:
                print(f"  - {role}: {count}")
            
            # إحصائيات الطلاب
            self.cursor.execute("SELECT COUNT(*) FROM students_studentprofile;")
            student_count = self.cursor.fetchone()[0]
            print(f"\n🎓 إجمالي الطلاب المسجلين: {student_count}")
            
            # إحصائيات الأساتذة
            self.cursor.execute("SELECT COUNT(*) FROM students_teacherprofile;")
            teacher_count = self.cursor.fetchone()[0]
            print(f"👨‍🏫 إجمالي الأساتذة: {teacher_count}")
            
            # إحصائيات قاعدة البيانات
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in self.cursor.fetchall()]
            print(f"\n💾 عدد الجداول في قاعدة البيانات: {len(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحليل قاعدة البيانات: {e}")
            return False
    
    def optimize_queries(self):
        """تحسين الاستعلامات الشائعة"""
        
        # إعادة تنظيم الجداول (VACUUM للـ SQLite)
        try:
            print("\n🔄 تحسين قاعدة البيانات...")
            self.cursor.execute("VACUUM;")
            print("✅ تم تحسين قاعدة البيانات بنجاح!")
            
            # تحديث إحصائيات الجداول
            self.cursor.execute("ANALYZE;")
            print("✅ تم تحديث إحصائيات الجداول!")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحسين قاعدة البيانات: {e}")
            return False
    
    def run_full_optimization(self):
        """تشغيل تحسين شامل لقاعدة البيانات"""
        
        print("🚀 بدء تحسين قاعدة البيانات الشامل...")
        print("=" * 50)
        
        # تحليل قاعدة البيانات
        if not self.analyze_database():
            return False
        
        print("\n" + "=" * 50)
        
        # إضافة الفهارس
        if not self.add_performance_indexes():
            return False
        
        print("\n" + "=" * 50)
        
        # تحسين الاستعلامات
        if not self.optimize_queries():
            return False
        
        print("\n" + "=" * 50)
        print("🎉 تم تحسين قاعدة البيانات بنجاح!")
        print("\n📈 التحسينات المطبقة:")
        print("  ✅ فهارس محسنة للأداء")
        print("  ✅ تحسين الاستعلامات")
        print("  ✅ تحديث إحصائيات الجداول")
        print("  ✅ تحسين مساحة التخزين")
        
        return True
    
    def close(self):
        """إغلاق الاتصال"""
        if self.cursor:
            self.cursor.close()

def main():
    """الدالة الرئيسية"""
    optimizer = DatabaseOptimizer()
    
    try:
        success = optimizer.run_full_optimization()
        if success:
            print("\n✅ تم إكمال عملية تحسين قاعدة البيانات بنجاح!")
        else:
            print("\n❌ فشل في تحسين قاعدة البيانات!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف العملية بواسطة المستخدم")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)
    
    finally:
        optimizer.close()

if __name__ == "__main__":
    main()