#!/usr/bin/env python
"""
Simple admin user creation
إنشاء مدير بسيط
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_simple_admin():
    """إنشاء مدير بسيط"""
    
    print("🎓 إنشاء مدير النظام...")
    
    try:
        # Check if admin exists
        if User.objects.filter(username='admin').exists():
            print("ℹ️ المدير موجود بالفعل")
            admin = User.objects.get(username='admin')
        else:
            # Create simple admin
            admin = User(
                username='admin',
                email='admin@university.edu.sa',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            
            # Add custom fields if they exist
            if hasattr(admin, 'first_name_ar'):
                admin.first_name_ar = 'مدير'
                admin.last_name_ar = 'النظام'
                admin.first_name_en = 'System'
                admin.last_name_en = 'Administrator'
            
            if hasattr(admin, 'role'):
                admin.role = 'SUPER_ADMIN'
                
            if hasattr(admin, 'gender'):
                admin.gender = 'M'
                
            if hasattr(admin, 'date_of_birth'):
                admin.date_of_birth = date(1980, 1, 1)
                
            if hasattr(admin, 'nationality'):
                admin.nationality = 'سعودي'
                
            if hasattr(admin, 'phone_number'):
                admin.phone_number = '+966501234567'
                
            if hasattr(admin, 'city'):
                admin.city = 'الرياض'
                admin.country = 'السعودية'
            
            admin.set_password('admin123')
            admin.save()
            print(f"✅ تم إنشاء المدير: {admin.username}")
        
        # Create a simple student
        if not User.objects.filter(username='student1').exists():
            student = User(
                username='student1',
                email='student1@university.edu.sa',
                first_name='Student',
                last_name='One',
                is_active=True,
            )
            
            if hasattr(student, 'role'):
                student.role = 'STUDENT'
                
            if hasattr(student, 'gender'):
                student.gender = 'M'
                
            if hasattr(student, 'date_of_birth'):
                student.date_of_birth = date(2000, 1, 1)
            
            student.set_password('student123')
            student.save()
            print(f"✅ تم إنشاء الطالب: {student.username}")
        
        # Create a simple teacher
        if not User.objects.filter(username='teacher1').exists():
            teacher = User(
                username='teacher1',
                email='teacher1@university.edu.sa',
                first_name='Teacher',
                last_name='One',
                is_active=True,
            )
            
            if hasattr(teacher, 'role'):
                teacher.role = 'TEACHER'
                
            if hasattr(teacher, 'gender'):
                teacher.gender = 'M'
                
            if hasattr(teacher, 'date_of_birth'):
                teacher.date_of_birth = date(1980, 1, 1)
            
            teacher.set_password('teacher123')
            teacher.save()
            print(f"✅ تم إنشاء الأستاذ: {teacher.username}")
        
        print("\n🎉 تم إنشاء المستخدمين بنجاح!")
        print("\n📋 بيانات تسجيل الدخول:")
        print("=" * 40)
        print("👑 مدير النظام:")
        print("   اسم المستخدم: admin")
        print("   كلمة المرور: admin123")
        print("\n👨‍🏫 أستاذ:")
        print("   اسم المستخدم: teacher1")
        print("   كلمة المرور: teacher123")
        print("\n🎓 طالب:")
        print("   اسم المستخدم: student1")
        print("   كلمة المرور: student123")
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء المستخدمين: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_simple_admin()