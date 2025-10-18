#!/usr/bin/env python
"""
Script to create demo data for University Management System
سكريبت لإنشاء بيانات تجريبية لنظام إدارة الجامعة
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from students.models import Student, Department
from courses.models import Course, CourseOffering
from academic.models import AcademicYear, Semester, Enrollment, Grade, Attendance
from finance.models import FeeStructure, StudentFee, Payment, Scholarship
from notifications.models import Notification
# HR models will be added later

User = get_user_model()

def create_demo_data():
    print("🎓 إنشاء البيانات التجريبية لنظام إدارة الجامعة...")
    
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
    
    # Create Departments
    departments_data = [
        ('CS', 'علوم الحاسوب', 'قسم علوم الحاسوب وتقنية المعلومات'),
        ('ENG', 'الهندسة', 'كلية الهندسة والتكنولوجيا'),
        ('BUS', 'إدارة الأعمال', 'كلية إدارة الأعمال والاقتصاد'),
        ('MED', 'الطب', 'كلية الطب والعلوم الصحية'),
        ('LAW', 'القانون', 'كلية الحقوق والعلوم السياسية'),
    ]
    
    departments = {}
    for code, name, desc in departments_data:
        dept, created = Department.objects.get_or_create(
            code=code,
            defaults={'name': name, 'description': desc}
        )
        departments[code] = dept
        if created:
            print(f"✅ تم إنشاء القسم: {name}")
    
    # Create Academic Year and Semester
    current_year, created = AcademicYear.objects.get_or_create(
        name='2024-2025',
        defaults={
            'start_date': date(2024, 9, 1),
            'end_date': date(2025, 6, 30),
            'is_current': True
        }
    )
    if created:
        print("✅ تم إنشاء السنة الأكاديمية: 2024-2025")
    
    current_semester, created = Semester.objects.get_or_create(
        academic_year=current_year,
        name='FALL',
        defaults={
            'start_date': date(2024, 9, 1),
            'end_date': date(2024, 12, 31),
            'registration_start': date(2024, 8, 15),
            'registration_end': date(2024, 9, 15),
            'is_current': True
        }
    )
    if created:
        print("✅ تم إنشاء الفصل الدراسي: الخريف 2024")
    
    # Create Courses
    courses_data = [
        ('CS101', 'مقدمة في البرمجة', 'CS', 3, 1, 'مقدمة في مفاهيم البرمجة وحل المشاكل'),
        ('CS201', 'هياكل البيانات', 'CS', 3, 2, 'دراسة هياكل البيانات والخوارزميات'),
        ('CS301', 'هندسة البرمجيات', 'CS', 3, 3, 'مبادئ هندسة البرمجيات والتصميم'),
        ('ENG101', 'الرياضيات الهندسية', 'ENG', 4, 1, 'أساسيات الرياضيات للمهندسين'),
        ('BUS101', 'مبادئ الإدارة', 'BUS', 3, 1, 'المفاهيم الأساسية في الإدارة'),
        ('MED101', 'علم التشريح', 'MED', 5, 1, 'دراسة تشريح الجسم البشري'),
    ]
    
    courses = {}
    for code, name, dept_code, credits, semester, desc in courses_data:
        course, created = Course.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'department': departments[dept_code],
                'credits': credits,
                'semester_offered': semester,
                'description': desc,
                'max_capacity': 30,
                'is_active': True
            }
        )
        courses[code] = course
        if created:
            print(f"✅ تم إنشاء المقرر: {name}")
    
    # Create Teachers
    teachers_data = [
        ('teacher1', 'د. أحمد', 'محمد', 'ahmad@university.edu', 'teacher123'),
        ('teacher2', 'د. فاطمة', 'علي', 'fatima@university.edu', 'teacher123'),
        ('teacher3', 'د. محمد', 'السيد', 'mohamed@university.edu', 'teacher123'),
    ]
    
    teachers = {}
    for username, first_name, last_name, email, password in teachers_data:
        if not User.objects.filter(username=username).exists():
            teacher = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='TEACHER'
            )
            teachers[username] = teacher
            print(f"✅ تم إنشاء الأستاذ: {first_name} {last_name}")
    
    # Create Students
    students_data = [
        ('student1', 'أحمد', 'خالد', 'ahmed@student.edu', 'student123', 'CS', '2024001'),
        ('student2', 'فاطمة', 'محمد', 'fatima@student.edu', 'student123', 'CS', '2024002'),
        ('student3', 'محمد', 'علي', 'mohammed@student.edu', 'student123', 'ENG', '2024003'),
        ('student4', 'نور', 'أحمد', 'noor@student.edu', 'student123', 'BUS', '2024004'),
        ('student5', 'سارة', 'محمد', 'sara@student.edu', 'student123', 'MED', '2024005'),
    ]
    
    students = {}
    for username, first_name, last_name, email, password, major, student_id in students_data:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='STUDENT'
            )
            
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                enrollment_date=date(2024, 9, 1),
                major=major,
                current_semester=1,
                gpa=3.50,
                status='ACTIVE'
            )
            students[username] = student
            print(f"✅ تم إنشاء الطالب: {first_name} {last_name} - {student_id}")
    
    # Create Fee Structures
    fee_structures_data = [
        ('UNDERGRADUATE', 1, 5000, 200, 100, 50, 150),
        ('UNDERGRADUATE', 2, 5000, 200, 100, 50, 150),
        ('GRADUATE', 1, 8000, 300, 150, 75, 200),
    ]
    
    for program, semester, tuition, lab, library, sports, other in fee_structures_data:
        fee_structure, created = FeeStructure.objects.get_or_create(
            program_type=program,
            semester=semester,
            defaults={
                'tuition_fee': tuition,
                'lab_fee': lab,
                'library_fee': library,
                'sports_fee': sports,
                'other_fees': other
            }
        )
        if created:
            print(f"✅ تم إنشاء هيكل الرسوم: {program} - فصل {semester}")
    
    # Create Student Fees
    fee_structure = FeeStructure.objects.get(program_type='UNDERGRADUATE', semester=1)
    for student_key in students:
        student = students[student_key]
        student_fee, created = StudentFee.objects.get_or_create(
            student=student,
            fee_structure=fee_structure,
            academic_year=2024,
            defaults={
                'total_amount': fee_structure.total_fee,
                'paid_amount': 0,
                'discount': 0,
                'status': 'PENDING',
                'due_date': date(2024, 10, 31)
            }
        )
        if created:
            print(f"✅ تم إنشاء رسوم للطالب: {student.user.get_full_name()}")
    
    print("✅ تم تخطي إنشاء أنواع الإشعارات (نموذج مبسط)")
    
    # Create sample notifications
    if students:
        for student_key in list(students.keys())[:3]:  # First 3 students
            student = students[student_key]
            
            Notification.objects.get_or_create(
                title='مرحباً بك في الجامعة',
                message=f'مرحباً {student.user.get_full_name()}، تم تأكيد تسجيلك بنجاح في الجامعة.',
                recipient=student.user,
                sender=admin_user,
                defaults={
                    'priority': 2,
                    'is_read': False
                }
            )
    
    print("\n🎉 تم إنشاء جميع البيانات التجريبية بنجاح!")
    print("\n🔐 بيانات تسجيل الدخول:")
    print("مدير النظام: admin / admin123")
    print("أستاذ: teacher1 / teacher123")
    print("طالب: student1 / student123")
    print("\n🌐 يمكنك الآن تشغيل الخادم باستخدام: python manage.py runserver")

if __name__ == '__main__':
    create_demo_data()