#!/usr/bin/env python3
"""
نص إنشاء مستخدم إداري
"""
import os
import sys
import django

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

django.setup()

from students.models import User

def create_admin():
    """إنشاء مستخدم إداري"""
    if not User.objects.filter(is_superuser=True).exists():
        admin = User.objects.create_user(
            username='admin',
            email='admin@university.edu',
            password='admin123',
            role='SUPER_ADMIN',
            first_name='مدير',
            last_name='النظام',
            is_superuser=True,
            is_staff=True
        )
        print(f"تم إنشاء المستخدم الإداري: {admin.username}")
    else:
        print("يوجد مستخدم إداري بالفعل")

if __name__ == "__main__":
    create_admin()
