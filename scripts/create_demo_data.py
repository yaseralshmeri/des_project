#!/usr/bin/env python3
"""
نص إنشاء بيانات تجريبية
"""
import os
import sys
import django
from datetime import datetime, timedelta

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

django.setup()

from students.models import User

def create_demo_data():
    """إنشاء بيانات تجريبية مبسطة"""
    
    # إنشاء طلاب تجريبيين فقط
    students_created = 0
    for i in range(1, 6):
        student, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'email': f'student{i}@university.edu',
                'role': 'STUDENT',
                'first_name': f'طالب{i}',
                'last_name': 'تجريبي',
                'student_id': f'2024{i:04d}'
            }
        )
        if created:
            student.set_password('student123')
            student.save()
            students_created += 1
    
    # إنشاء أساتذة تجريبيين
    teachers_created = 0
    for i in range(1, 4):
        teacher, created = User.objects.get_or_create(
            username=f'teacher{i}',
            defaults={
                'email': f'teacher{i}@university.edu',
                'role': 'TEACHER',
                'first_name': f'أستاذ{i}',
                'last_name': 'تجريبي',
                'employee_id': f'T{i:04d}'
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            teachers_created += 1
    
    print(f"تم إنشاء البيانات التجريبية بنجاح!")
    print(f"الطلاب الجدد: {students_created}")
    print(f"الأساتذة الجدد: {teachers_created}")
    print("يمكنك الآن تسجيل الدخول بـ:")
    print("- طالب: student1 / student123")
    print("- أستاذ: teacher1 / teacher123")
    print("- إداري: admin / admin123")

if __name__ == "__main__":
    create_demo_data()
