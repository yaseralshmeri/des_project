#!/usr/bin/env python
"""
Create demo users and data for University Management System
إنشاء بيانات تجريبية لنظام إدارة الجامعة
"""

import os
import sys
import django
from datetime import datetime, date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from students.models import User

def create_demo_users():
    """إنشاء المستخدمين التجريبيين"""
    
    print("🎓 إنشاء البيانات التجريبية لنظام إدارة الجامعة...")
    
    # Create Superuser Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@university.edu.sa',
            password='admin123',
            first_name_ar='مدير',
            last_name_ar='النظام',
            first_name_en='System',
            last_name_en='Administrator',
            role='SUPER_ADMIN',
            gender='M',
            date_of_birth=date(1980, 1, 1),
            place_of_birth='الرياض',
            nationality='سعودي',
            phone_number='+966501234567',
            address_line_1='شارع الملك فهد',
            city='الرياض',
            state_province='الرياض',
            country='السعودية',
            employee_id='EMP001'
        )
        print(f"✅ تم إنشاء المدير العام: {admin.username}")
    
    # Create Dean
    if not User.objects.filter(username='dean').exists():
        dean = User.objects.create_user(
            username='dean',
            email='dean@university.edu.sa',
            password='dean123',
            first_name_ar='أحمد',
            last_name_ar='المالكي',
            first_name_en='Ahmed',
            last_name_en='Al-Malki',
            role='DEAN',
            gender='M',
            date_of_birth=date(1975, 5, 15),
            place_of_birth='جدة',
            nationality='سعودي',
            phone_number='+966502345678',
            address_line_1='حي الملقا',
            city='الرياض',
            state_province='الرياض',
            country='السعودية',
            employee_id='EMP002'
        )
        print(f"✅ تم إنشاء عميد الكلية: {dean.username}")
    
    # Create Teachers
    teachers_data = [
        {
            'username': 'teacher1',
            'email': 'teacher1@university.edu.sa',
            'first_name_ar': 'محمد',
            'last_name_ar': 'العبدالله',
            'first_name_en': 'Mohammed',
            'last_name_en': 'Al-Abdullah',
            'gender': 'M',
            'employee_id': 'EMP003'
        },
        {
            'username': 'teacher2',
            'email': 'teacher2@university.edu.sa',
            'first_name_ar': 'فاطمة',
            'last_name_ar': 'الزهراني',
            'first_name_en': 'Fatima',
            'last_name_en': 'Al-Zahrani',
            'gender': 'F',
            'employee_id': 'EMP004'
        },
        {
            'username': 'teacher3',
            'email': 'teacher3@university.edu.sa',
            'first_name_ar': 'عبدالرحمن',
            'last_name_ar': 'القحطاني',
            'first_name_en': 'Abdulrahman',
            'last_name_en': 'Al-Qahtani',
            'gender': 'M',
            'employee_id': 'EMP005'
        }
    ]
    
    for i, teacher_data in enumerate(teachers_data, 1):
        if not User.objects.filter(username=teacher_data['username']).exists():
            teacher = User.objects.create_user(
                username=teacher_data['username'],
                email=teacher_data['email'],
                password='teacher123',
                first_name_ar=teacher_data['first_name_ar'],
                last_name_ar=teacher_data['last_name_ar'],
                first_name_en=teacher_data['first_name_en'],
                last_name_en=teacher_data['last_name_en'],
                role='TEACHER',
                gender=teacher_data['gender'],
                date_of_birth=date(1980 + i, 3, 10 + i),
                place_of_birth='الرياض',
                nationality='سعودي',
                phone_number=f'+96650{3000000 + i}',
                address_line_1=f'حي النرجس {i}',
                city='الرياض',
                state_province='الرياض',
                country='السعودية',
                employee_id=teacher_data['employee_id']
            )
            print(f"✅ تم إنشاء الأستاذ: {teacher.username}")
    
    # Create Students
    students_data = [
        {
            'username': 'student1',
            'email': 'student1@university.edu.sa',
            'first_name_ar': 'سارة',
            'last_name_ar': 'الأحمد',
            'first_name_en': 'Sarah',
            'last_name_en': 'Al-Ahmad',
            'gender': 'F',
            'student_id': 'STU001'
        },
        {
            'username': 'student2',
            'email': 'student2@university.edu.sa',
            'first_name_ar': 'خالد',
            'last_name_ar': 'المطيري',
            'first_name_en': 'Khalid',
            'last_name_en': 'Al-Mutairi',
            'gender': 'M',
            'student_id': 'STU002'
        },
        {
            'username': 'student3',
            'email': 'student3@university.edu.sa',
            'first_name_ar': 'نورة',
            'last_name_ar': 'السلمي',
            'first_name_en': 'Noorah',
            'last_name_en': 'Al-Salmi',
            'gender': 'F',
            'student_id': 'STU003'
        },
        {
            'username': 'student4',
            'email': 'student4@university.edu.sa',
            'first_name_ar': 'عبدالله',
            'last_name_ar': 'الشمري',
            'first_name_en': 'Abdullah',
            'last_name_en': 'Al-Shamri',
            'gender': 'M',
            'student_id': 'STU004'
        },
        {
            'username': 'student5',
            'email': 'student5@university.edu.sa',
            'first_name_ar': 'مريم',
            'last_name_ar': 'العتيبي',
            'first_name_en': 'Maryam',
            'last_name_en': 'Al-Otaibi',
            'gender': 'F',
            'student_id': 'STU005'
        }
    ]
    
    for i, student_data in enumerate(students_data, 1):
        if not User.objects.filter(username=student_data['username']).exists():
            student = User.objects.create_user(
                username=student_data['username'],
                email=student_data['email'],
                password='student123',
                first_name_ar=student_data['first_name_ar'],
                last_name_ar=student_data['last_name_ar'],
                first_name_en=student_data['first_name_en'],
                last_name_en=student_data['last_name_en'],
                role='STUDENT',
                gender=student_data['gender'],
                date_of_birth=date(2000 + i, 6, 15 + i),
                place_of_birth='الرياض',
                nationality='سعودي',
                phone_number=f'+96655{0000000 + i}',
                address_line_1=f'حي الرمال {i}',
                city='الرياض',
                state_province='الرياض',
                country='السعودية',
                student_id=student_data['student_id'],
                enrollment_date=date(2024, 9, 1),
                academic_level='البكالوريوس'
            )
            print(f"✅ تم إنشاء الطالب: {student.username}")
    
    # Create Staff
    staff_data = [
        {
            'username': 'registrar',
            'email': 'registrar@university.edu.sa',
            'first_name_ar': 'عمر',
            'last_name_ar': 'البقمي',
            'role': 'REGISTRAR',
            'employee_id': 'EMP006'
        },
        {
            'username': 'accountant',
            'email': 'accountant@university.edu.sa',
            'first_name_ar': 'هند',
            'last_name_ar': 'الدوسري',
            'role': 'ACCOUNTANT',
            'employee_id': 'EMP007'
        },
        {
            'username': 'hr_manager',
            'email': 'hr@university.edu.sa',
            'first_name_ar': 'سلمان',
            'last_name_ar': 'الحربي',
            'role': 'HR_MANAGER',
            'employee_id': 'EMP008'
        }
    ]
    
    for staff in staff_data:
        if not User.objects.filter(username=staff['username']).exists():
            staff_user = User.objects.create_user(
                username=staff['username'],
                email=staff['email'],
                password='staff123',
                first_name_ar=staff['first_name_ar'],
                last_name_ar=staff['last_name_ar'],
                first_name_en=staff['first_name_ar'],  # Simple mapping
                last_name_en=staff['last_name_ar'],
                role=staff['role'],
                gender='M' if staff['first_name_ar'] in ['عمر', 'سلمان'] else 'F',
                date_of_birth=date(1985, 1, 1),
                place_of_birth='الرياض',
                nationality='سعودي',
                phone_number='+966501111111',
                address_line_1='شارع العليا',
                city='الرياض',
                state_province='الرياض',
                country='السعودية',
                employee_id=staff['employee_id']
            )
            print(f"✅ تم إنشاء الموظف: {staff_user.username}")
    
    print(f"\n🎉 تم إنشاء {User.objects.count()} مستخدم بنجاح!")
    print("\n📋 بيانات تسجيل الدخول:")
    print("=" * 50)
    print("👑 مدير النظام:")
    print("   اسم المستخدم: admin")
    print("   كلمة المرور: admin123")
    print("\n👨‍🏫 الأساتذة:")
    print("   اسم المستخدم: teacher1/teacher2/teacher3")
    print("   كلمة المرور: teacher123")
    print("\n🎓 الطلاب:")
    print("   اسم المستخدم: student1/student2/student3/student4/student5")
    print("   كلمة المرور: student123")
    print("\n👨‍💼 الموظفين:")
    print("   اسم المستخدم: registrar/accountant/hr_manager")
    print("   كلمة المرور: staff123")
    print("=" * 50)

if __name__ == '__main__':
    create_demo_users()