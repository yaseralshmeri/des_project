#!/usr/bin/env python
"""
إنشاء مستخدم إداري فائق للنظام
Create Superuser for the System
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

def create_superuser():
    """إنشاء مستخدم إداري فائق"""
    
    # بيانات المستخدم الافتراضية
    username = 'admin'
    email = 'admin@university.edu.sa'
    password = 'admin123456'
    
    try:
        # التحقق من وجود المستخدم
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print(f'✅ المستخدم الإداري "{username}" موجود بالفعل')
            return user
        
        # إنشاء المستخدم الإداري
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name_ar='المدير',
            last_name_ar='العام',
            first_name='System',
            last_name='Administrator',
            role='SUPER_ADMIN',
            gender='M',
            phone='+966500000000',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        
        print(f'✅ تم إنشاء المستخدم الإداري بنجاح!')
        print(f'📧 اسم المستخدم: {username}')
        print(f'🔑 كلمة المرور: {password}')
        print(f'📪 البريد الإلكتروني: {email}')
        print(f'👤 الدور: مدير النظام العام')
        print(f'🆔 معرف المستخدم: {user.id}')
        
        return user
        
    except Exception as e:
        print(f'❌ خطأ في إنشاء المستخدم الإداري: {str(e)}')
        return None

def create_demo_users():
    """إنشاء مستخدمين تجريبيين"""
    
    demo_users = [
        {
            'username': 'student1',
            'email': 'student1@student.university.edu.sa',
            'password': 'student123',
            'first_name_ar': 'أحمد',
            'last_name_ar': 'محمد',
            'first_name': 'Ahmed',
            'last_name': 'Mohammed',
            'role': 'STUDENT',
            'gender': 'M'
        },
        {
            'username': 'teacher1', 
            'email': 'teacher1@university.edu.sa',
            'password': 'teacher123',
            'first_name_ar': 'فاطمة',
            'last_name_ar': 'علي',
            'first_name': 'Fatima',
            'last_name': 'Ali',
            'role': 'TEACHER',
            'gender': 'F'
        },
        {
            'username': 'registrar1',
            'email': 'registrar1@university.edu.sa', 
            'password': 'registrar123',
            'first_name_ar': 'خالد',
            'last_name_ar': 'العبدالله',
            'first_name': 'Khalid',
            'last_name': 'Al-Abdullah',
            'role': 'REGISTRAR',
            'gender': 'M'
        }
    ]
    
    created_users = []
    
    print('\n📝 إنشاء مستخدمين تجريبيين...')
    
    for user_data in demo_users:
        try:
            if User.objects.filter(username=user_data['username']).exists():
                print(f'⚠️  المستخدم "{user_data["username"]}" موجود بالفعل - تم تخطيه')
                continue
                
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name_ar=user_data['first_name_ar'],
                last_name_ar=user_data['last_name_ar'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                gender=user_data['gender'],
                is_active=True
            )
            
            created_users.append(user)
            print(f'✅ تم إنشاء: {user_data["username"]} ({user_data["role"]})')
            
        except Exception as e:
            print(f'❌ خطأ في إنشاء المستخدم {user_data["username"]}: {str(e)}')
    
    return created_users

if __name__ == '__main__':
    print('🚀 بدء إعداد النظام...')
    print('=' * 50)
    
    # إنشاء المستخدم الإداري
    superuser = create_superuser()
    
    # إنشاء مستخدمين تجريبيين
    demo_users = create_demo_users()
    
    print('\n' + '=' * 50)
    print('🎉 تم إعداد النظام بنجاح!')
    print(f'👥 إجمالي المستخدمين المُنشأين: {len(demo_users) + (1 if superuser else 0)}')
    print('\n📌 يمكنك الآن تسجيل الدخول باستخدام:')
    print('   • المدير العام: admin / admin123456')
    print('   • طالب تجريبي: student1 / student123')
    print('   • مدرس تجريبي: teacher1 / teacher123')
    print('   • مسجل أكاديمي: registrar1 / registrar123')
    print('\n🌐 لتشغيل الخادم: python manage.py runserver')