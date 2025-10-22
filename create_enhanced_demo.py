#!/usr/bin/env python
"""
إنشاء بيانات تجريبية محسنة لنظام إدارة الجامعة
Enhanced Demo Data Creation for University Management System
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_minimal')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

def create_enhanced_demo_data():
    """إنشاء بيانات تجريبية شاملة"""
    print("🚀 بدء إنشاء البيانات التجريبية المحسنة...")
    
    with transaction.atomic():
        
        # 1. إنشاء المستخدم الإداري الرئيسي
        print("👤 إنشاء المستخدمين الإداريين...")
        
        # مدير النظام الرئيسي
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                role='SUPER_ADMIN',
                first_name_ar='مدير',
                last_name_ar='النظام',
                first_name_en='System',
                last_name_en='Administrator'
            )
            print(f"✅ تم إنشاء المدير الرئيسي: {admin.username}")
        
        # مدير أكاديمي
        if not User.objects.filter(username='academic_admin').exists():
            academic_admin = User.objects.create_user(
                username='academic_admin',
                email='academic@university.edu',
                password='admin123',
                role='ADMIN',
                first_name_ar='أحمد',
                last_name_ar='الأكاديمي',
                first_name_en='Ahmed',
                last_name_en='Academic',
                is_staff=True
            )
            print(f"✅ تم إنشاء المدير الأكاديمي: {academic_admin.username}")
        
        # 2. إنشاء الأساتذة
        print("👨‍🏫 إنشاء أعضاء هيئة التدريس...")
        
        teachers_data = [
            {
                'username': 'dr_mohammed',
                'email': 'mohammed@university.edu',
                'password': 'teacher123',
                'role': 'TEACHER',
                'first_name_ar': 'محمد',
                'last_name_ar': 'العلوي',
                'first_name_en': 'Mohammed',
                'last_name_en': 'Al-Alawi',
                'employee_id': 'T001'
            },
            {
                'username': 'dr_fatima',
                'email': 'fatima@university.edu',
                'password': 'teacher123',
                'role': 'TEACHER',
                'first_name_ar': 'فاطمة',
                'last_name_ar': 'الزهراني',
                'first_name_en': 'Fatima',
                'last_name_en': 'Al-Zahrani',
                'employee_id': 'T002'
            },
            {
                'username': 'dr_abdullah',
                'email': 'abdullah@university.edu',
                'password': 'teacher123',
                'role': 'TEACHER',
                'first_name_ar': 'عبدالله',
                'last_name_ar': 'القحطاني',
                'first_name_en': 'Abdullah',
                'last_name_en': 'Al-Qahtani',
                'employee_id': 'T003'
            }
        ]
        
        for teacher_data in teachers_data:
            if not User.objects.filter(username=teacher_data['username']).exists():
                teacher = User.objects.create_user(**teacher_data)
                print(f"✅ تم إنشاء الأستاذ: {teacher.first_name_ar} {teacher.last_name_ar}")
        
        # 3. إنشاء الطلاب
        print("🎓 إنشاء الطلاب...")
        
        students_data = [
            {
                'username': 'student001',
                'email': 'ali@students.university.edu',
                'password': 'student123',
                'role': 'STUDENT',
                'first_name_ar': 'علي',
                'last_name_ar': 'محمد',
                'first_name_en': 'Ali',
                'last_name_en': 'Mohammed',
                'student_id': 'S2024001',
                'academic_level': 'السنة الأولى'
            },
            {
                'username': 'student002',
                'email': 'sara@students.university.edu',
                'password': 'student123',
                'role': 'STUDENT',
                'first_name_ar': 'سارة',
                'last_name_ar': 'أحمد',
                'first_name_en': 'Sara',
                'last_name_en': 'Ahmed',
                'student_id': 'S2024002',
                'academic_level': 'السنة الثانية'
            },
            {
                'username': 'student003',
                'email': 'omar@students.university.edu',
                'password': 'student123',
                'role': 'STUDENT',
                'first_name_ar': 'عمر',
                'last_name_ar': 'خالد',
                'first_name_en': 'Omar',
                'last_name_en': 'Khalid',
                'student_id': 'S2024003',
                'academic_level': 'السنة الثالثة'
            },
            {
                'username': 'student004',
                'email': 'maryam@students.university.edu',
                'password': 'student123',
                'role': 'STUDENT',
                'first_name_ar': 'مريم',
                'last_name_ar': 'عبدالرحمن',
                'first_name_en': 'Maryam',
                'last_name_en': 'Abdulrahman',
                'student_id': 'S2024004',
                'academic_level': 'السنة الأولى'
            },
            {
                'username': 'student005',
                'email': 'yousef@students.university.edu',
                'password': 'student123',
                'role': 'STUDENT',
                'first_name_ar': 'يوسف',
                'last_name_ar': 'العتيبي',
                'first_name_en': 'Yousef',
                'last_name_en': 'Al-Otaibi',
                'student_id': 'S2024005',
                'academic_level': 'السنة الرابعة'
            }
        ]
        
        for student_data in students_data:
            if not User.objects.filter(username=student_data['username']).exists():
                student = User.objects.create_user(**student_data)
                print(f"✅ تم إنشاء الطالب: {student.first_name_ar} {student.last_name_ar}")
        
        # 4. إنشاء موظفين إضافيين
        print("💼 إنشاء الموظفين الإداريين...")
        
        staff_data = [
            {
                'username': 'registrar',
                'email': 'registrar@university.edu',
                'password': 'staff123',
                'role': 'REGISTRAR',
                'first_name_ar': 'سعد',
                'last_name_ar': 'المسجل',
                'first_name_en': 'Saad',
                'last_name_en': 'Al-Musajjal',
                'employee_id': 'R001'
            },
            {
                'username': 'accountant',
                'email': 'finance@university.edu',
                'password': 'staff123',
                'role': 'ACCOUNTANT',
                'first_name_ar': 'نورا',
                'last_name_ar': 'المالية',
                'first_name_en': 'Nora',
                'last_name_en': 'Finance',
                'employee_id': 'F001'
            },
            {
                'username': 'hr_manager',
                'email': 'hr@university.edu',
                'password': 'staff123',
                'role': 'HR_MANAGER',
                'first_name_ar': 'خالد',
                'last_name_ar': 'الموارد',
                'first_name_en': 'Khalid',
                'last_name_en': 'HR',
                'employee_id': 'H001'
            }
        ]
        
        for staff_member in staff_data:
            if not User.objects.filter(username=staff_member['username']).exists():
                staff = User.objects.create_user(**staff_member)
                staff.is_staff = True
                staff.save()
                print(f"✅ تم إنشاء الموظف: {staff.first_name_ar} {staff.last_name_ar}")
        
        # 5. تحديث المستخدم الموجود student1 إذا وُجد
        try:
            student1 = User.objects.get(username='student1')
            student1.first_name_ar = 'الطالب'
            student1.last_name_ar = 'الأول'
            student1.first_name_en = 'First'
            student1.last_name_en = 'Student'
            student1.student_id = 'S2024000'
            student1.role = 'STUDENT'
            student1.save()
            print(f"✅ تم تحديث الطالب الموجود: {student1.username}")
        except User.DoesNotExist:
            pass
        
        # 6. إحصائيات نهائية
        print("\n📊 إحصائيات البيانات المنشأة:")
        print(f"👥 إجمالي المستخدمين: {User.objects.count()}")
        print(f"🎓 الطلاب: {User.objects.filter(role='STUDENT').count()}")
        print(f"👨‍🏫 أعضاء هيئة التدريس: {User.objects.filter(role='TEACHER').count()}")
        print(f"👨‍💼 الإداريين: {User.objects.filter(role__in=['ADMIN', 'SUPER_ADMIN']).count()}")
        print(f"💼 الموظفين: {User.objects.filter(role__in=['REGISTRAR', 'ACCOUNTANT', 'HR_MANAGER']).count()}")
        
        print("\n🔐 بيانات تسجيل الدخول:")
        print("=" * 50)
        print("مدير النظام:")
        print("  المستخدم: admin")
        print("  كلمة المرور: admin123")
        print("\nأستاذ:")
        print("  المستخدم: dr_mohammed")
        print("  كلمة المرور: teacher123")
        print("\nطالب:")
        print("  المستخدم: student001")
        print("  كلمة المرور: student123")
        print("\nموظف:")
        print("  المستخدم: registrar")
        print("  كلمة المرور: staff123")
        print("=" * 50)
        
        print("\n✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
        print("🌐 يمكنك الآن الوصول للنظام عبر: http://localhost:8001/")
        print("🔧 لوحة الإدارة: http://localhost:8001/admin/")

if __name__ == '__main__':
    try:
        create_enhanced_demo_data()
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات التجريبية: {e}")
        sys.exit(1)