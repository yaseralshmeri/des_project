#!/usr/bin/env python
"""
Simple demo data creation script
سكريبت مبسط لإنشاء البيانات التجريبية
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from students.models import Student, Department

User = get_user_model()

def create_simple_demo():
    print("🎓 إنشاء البيانات التجريبية الأساسية...")
    
    # Create Superuser
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@university.edu',
            password='admin123',
            first_name='مدير',
            last_name='النظام',
            role='ADMIN'
        )
        print("✅ تم إنشاء المستخدم الإداري: admin / admin123")
    
    # Create a department
    dept, created = Department.objects.get_or_create(
        code='CS',
        defaults={
            'name': 'علوم الحاسوب',
            'description': 'قسم علوم الحاسوب وتقنية المعلومات'
        }
    )
    if created:
        print("✅ تم إنشاء القسم: علوم الحاسوب")
    
    # Create a teacher
    if not User.objects.filter(username='teacher1').exists():
        teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@university.edu',
            password='teacher123',
            first_name='د. أحمد',
            last_name='محمد',
            role='TEACHER'
        )
        print("✅ تم إنشاء الأستاذ: د. أحمد محمد")
    
    # Create a student
    if not User.objects.filter(username='student1').exists():
        user = User.objects.create_user(
            username='student1',
            email='student@university.edu',
            password='student123',
            first_name='أحمد',
            last_name='خالد',
            role='STUDENT'
        )
        
        student = Student.objects.create(
            user=user,
            student_id='2024001',
            enrollment_date=date(2024, 9, 1),
            major='علوم الحاسوب',
            current_semester=1,
            gpa=3.50,
            status='ACTIVE'
        )
        print("✅ تم إنشاء الطالب: أحمد خالد - 2024001")
    
    print("\n🎉 تم إنشاء البيانات التجريبية الأساسية بنجاح!")
    print("\n🔐 بيانات تسجيل الدخول:")
    print("مدير النظام: admin / admin123")
    print("أستاذ: teacher1 / teacher123")
    print("طالب: student1 / student123")
    print("\n🌐 يمكنك الآن تشغيل الخادم باستخدام: python manage.py runserver")

if __name__ == '__main__':
    create_simple_demo()