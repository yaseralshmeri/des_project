# FIX: Demo Data - إضافة بيانات ديمو شاملة
"""
إضافة بيانات ديمو كاملة للنظام مع دعم اللغة العربية
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Import models
from students.models import Student, StudentProfile
from courses.models import Course, Department, Semester
from academic.models import Enrollment, Grade, Schedule
from finance.models import Payment, Fee, Scholarship
from hr.models import Employee, Department as HRDepartment, Salary
from notifications.models import Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'إنشاء بيانات ديمو شاملة للنظام'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS('بدء إنشاء بيانات الديمو...'))
            
            # إنشاء المستخدمين الأساسيين
            self.create_admin_users()
            
            # إنشاء الأقسام
            self.create_departments()
            
            # إنشاء الفصول الدراسية
            self.create_semesters()
            
            # إنشاء المقررات
            self.create_courses()
            
            # إنشاء الطلاب
            self.create_students()
            
            # إنشاء الموظفين
            self.create_employees()
            
            # إنشاء التسجيلات والدرجات
            self.create_enrollments_and_grades()
            
            # إنشاء الرسوم والمدفوعات
            self.create_fees_and_payments()
            
            # إنشاء المنح الدراسية
            self.create_scholarships()
            
            # إنشاء الرواتب
            self.create_salaries()
            
            # إنشاء الإشعارات
            self.create_notifications()
            
            self.stdout.write(self.style.SUCCESS('تم إنشاء بيانات الديمو بنجاح!'))

    def create_admin_users(self):
        """إنشاء المستخدمين الإداريين"""
        # Admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                first_name='مدير',
                last_name='النظام'
            )
            self.stdout.write(f'تم إنشاء المستخدم الإداري: {admin.username}')

        # Staff user
        if not User.objects.filter(username='staff').exists():
            staff = User.objects.create_user(
                username='staff',
                email='staff@university.edu',
                password='staff123',
                first_name='موظف',
                last_name='إداري',
                is_staff=True
            )
            self.stdout.write(f'تم إنشاء الموظف الإداري: {staff.username}')

        # Teacher user
        if not User.objects.filter(username='teacher').exists():
            teacher = User.objects.create_user(
                username='teacher',
                email='teacher@university.edu',
                password='teacher123',
                first_name='أستاذ',
                last_name='محاضر'
            )
            self.stdout.write(f'تم إنشاء المدرس: {teacher.username}')

    def create_departments(self):
        """إنشاء الأقسام الأكاديمية"""
        departments_data = [
            {'name': 'قسم علوم الحاسوب', 'code': 'CS', 'description': 'قسم علوم الحاسوب وتقنية المعلومات'},
            {'name': 'قسم الهندسة', 'code': 'ENG', 'description': 'قسم الهندسة والتكنولوجيا'},
            {'name': 'قسم إدارة الأعمال', 'code': 'BUS', 'description': 'قسم إدارة الأعمال والاقتصاد'},
            {'name': 'قسم الرياضيات', 'code': 'MATH', 'description': 'قسم الرياضيات والإحصاء'},
            {'name': 'قسم الفيزياء', 'code': 'PHY', 'description': 'قسم الفيزياء والعلوم التطبيقية'},
        ]
        
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data['description']
                }
            )
            if created:
                self.stdout.write(f'تم إنشاء القسم: {dept.name}')

        # إنشاء أقسام الموارد البشرية
        hr_departments_data = [
            {'name': 'الموارد البشرية', 'description': 'إدارة الموارد البشرية'},
            {'name': 'الشؤون الأكاديمية', 'description': 'إدارة الشؤون الأكاديمية'},
            {'name': 'الشؤون المالية', 'description': 'إدارة الشؤون المالية'},
            {'name': 'تقنية المعلومات', 'description': 'إدارة تقنية المعلومات'},
        ]
        
        for hr_dept_data in hr_departments_data:
            hr_dept, created = HRDepartment.objects.get_or_create(
                name=hr_dept_data['name'],
                defaults={'description': hr_dept_data['description']}
            )
            if created:
                self.stdout.write(f'تم إنشاء قسم الموارد البشرية: {hr_dept.name}')

    def create_semesters(self):
        """إنشاء الفصول الدراسية"""
        current_year = datetime.now().year
        semesters_data = [
            {
                'name': f'الفصل الأول {current_year}',
                'start_date': datetime(current_year, 9, 1),
                'end_date': datetime(current_year, 12, 31),
                'is_active': True
            },
            {
                'name': f'الفصل الثاني {current_year}',
                'start_date': datetime(current_year + 1, 2, 1),
                'end_date': datetime(current_year + 1, 6, 30),
                'is_active': False
            },
        ]
        
        for sem_data in semesters_data:
            semester, created = Semester.objects.get_or_create(
                name=sem_data['name'],
                defaults={
                    'start_date': sem_data['start_date'],
                    'end_date': sem_data['end_date'],
                    'is_active': sem_data['is_active']
                }
            )
            if created:
                self.stdout.write(f'تم إنشاء الفصل الدراسي: {semester.name}')

    def create_courses(self):
        """إنشاء المقررات الدراسية"""
        departments = Department.objects.all()
        courses_data = [
            # Computer Science courses
            {'name': 'مقدمة في البرمجة', 'code': 'CS101', 'credits': 3, 'department': 'CS'},
            {'name': 'هياكل البيانات', 'code': 'CS201', 'credits': 3, 'department': 'CS'},
            {'name': 'قواعد البيانات', 'code': 'CS301', 'credits': 3, 'department': 'CS'},
            {'name': 'الذكاء الاصطناعي', 'code': 'CS401', 'credits': 3, 'department': 'CS'},
            
            # Engineering courses
            {'name': 'الرياضيات الهندسية', 'code': 'ENG101', 'credits': 4, 'department': 'ENG'},
            {'name': 'الفيزياء الهندسية', 'code': 'ENG102', 'credits': 4, 'department': 'ENG'},
            {'name': 'هندسة البرمجيات', 'code': 'ENG301', 'credits': 3, 'department': 'ENG'},
            
            # Business courses
            {'name': 'مبادئ الإدارة', 'code': 'BUS101', 'credits': 3, 'department': 'BUS'},
            {'name': 'المحاسبة المالية', 'code': 'BUS201', 'credits': 3, 'department': 'BUS'},
            {'name': 'التسويق', 'code': 'BUS301', 'credits': 3, 'department': 'BUS'},
            
            # Mathematics courses
            {'name': 'حساب التفاضل', 'code': 'MATH101', 'credits': 4, 'department': 'MATH'},
            {'name': 'حساب التكامل', 'code': 'MATH102', 'credits': 4, 'department': 'MATH'},
            {'name': 'الجبر الخطي', 'code': 'MATH201', 'credits': 3, 'department': 'MATH'},
            
            # Physics courses
            {'name': 'الفيزياء العامة', 'code': 'PHY101', 'credits': 4, 'department': 'PHY'},
            {'name': 'الكهرومغناطيسية', 'code': 'PHY201', 'credits': 3, 'department': 'PHY'},
        ]
        
        dept_map = {dept.code: dept for dept in departments}
        
        for course_data in courses_data:
            department = dept_map.get(course_data['department'])
            if department:
                course, created = Course.objects.get_or_create(
                    code=course_data['code'],
                    defaults={
                        'name': course_data['name'],
                        'credits': course_data['credits'],
                        'department': department,
                        'description': f'وصف مقرر {course_data["name"]}'
                    }
                )
                if created:
                    self.stdout.write(f'تم إنشاء المقرر: {course.name}')

    def create_students(self):
        """إنشاء الطلاب"""
        departments = Department.objects.all()
        
        students_data = [
            {'username': 'student1', 'first_name': 'أحمد', 'last_name': 'محمد', 'email': 'ahmed@student.edu'},
            {'username': 'student2', 'first_name': 'فاطمة', 'last_name': 'علي', 'email': 'fatima@student.edu'},
            {'username': 'student3', 'first_name': 'محمد', 'last_name': 'خالد', 'email': 'mohammed@student.edu'},
            {'username': 'student4', 'first_name': 'عائشة', 'last_name': 'حسن', 'email': 'aisha@student.edu'},
            {'username': 'student5', 'first_name': 'يوسف', 'last_name': 'إبراهيم', 'email': 'youssef@student.edu'},
            {'username': 'student6', 'first_name': 'مريم', 'last_name': 'أحمد', 'email': 'mariam@student.edu'},
            {'username': 'student7', 'first_name': 'عبدالله', 'last_name': 'عمر', 'email': 'abdullah@student.edu'},
            {'username': 'student8', 'first_name': 'خديجة', 'last_name': 'محمود', 'email': 'khadija@student.edu'},
        ]
        
        for i, student_data in enumerate(students_data):
            # إنشاء المستخدم
            user, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'email': student_data['email'],
                    'password': 'pbkdf2_sha256$600000$test$test',  # كلمة مرور مؤقتة
                }
            )
            
            if created:
                # إنشاء ملف الطالب
                department = random.choice(departments)
                student = Student.objects.create(
                    user=user,
                    student_id=f'2024{1000 + i}',
                    department=department,
                    enrollment_date=datetime.now() - timedelta(days=random.randint(30, 365))
                )
                
                # إنشاء ملف شخصي للطالب
                StudentProfile.objects.create(
                    student=student,
                    phone=f'+966 5{random.randint(10000000, 99999999)}',
                    address=f'الرياض - حي {random.choice(["النخيل", "الملز", "العليا", "الروضة"])}',
                    date_of_birth=datetime(1995 + random.randint(0, 10), random.randint(1, 12), random.randint(1, 28)),
                    nationality='سعودي',
                    gender=random.choice(['M', 'F'])
                )
                
                self.stdout.write(f'تم إنشاء الطالب: {user.get_full_name()}')

    def create_employees(self):
        """إنشاء الموظفين"""
        hr_departments = HRDepartment.objects.all()
        
        employees_data = [
            {'username': 'emp1', 'first_name': 'سالم', 'last_name': 'العتيبي', 'email': 'salem@university.edu', 'position': 'محاضر'},
            {'username': 'emp2', 'first_name': 'نورا', 'last_name': 'الشهري', 'email': 'nora@university.edu', 'position': 'أستاذ مساعد'},
            {'username': 'emp3', 'first_name': 'خالد', 'last_name': 'المطيري', 'email': 'khalid@university.edu', 'position': 'أستاذ مشارك'},
            {'username': 'emp4', 'first_name': 'هند', 'last_name': 'القحطاني', 'email': 'hind@university.edu', 'position': 'محاسب'},
            {'username': 'emp5', 'first_name': 'عبدالرحمن', 'last_name': 'الدوسري', 'email': 'abdulrahman@university.edu', 'position': 'مطور نظم'},
        ]
        
        for employee_data in employees_data:
            # إنشاء المستخدم
            user, created = User.objects.get_or_create(
                username=employee_data['username'],
                defaults={
                    'first_name': employee_data['first_name'],
                    'last_name': employee_data['last_name'],
                    'email': employee_data['email'],
                    'password': 'pbkdf2_sha256$600000$test$test',
                    'is_staff': True
                }
            )
            
            if created:
                # إنشاء ملف الموظف
                department = random.choice(hr_departments)
                Employee.objects.create(
                    user=user,
                    employee_id=f'EMP{2024}{random.randint(100, 999)}',
                    department=department,
                    position=employee_data['position'],
                    hire_date=datetime.now() - timedelta(days=random.randint(365, 1825)),
                    salary=Decimal(str(random.randint(5000, 15000)))
                )
                
                self.stdout.write(f'تم إنشاء الموظف: {user.get_full_name()}')

    def create_enrollments_and_grades(self):
        """إنشاء التسجيلات والدرجات"""
        students = Student.objects.all()
        courses = Course.objects.all()
        current_semester = Semester.objects.filter(is_active=True).first()
        
        if not current_semester:
            return
            
        for student in students:
            # تسجيل الطالب في 3-5 مقررات عشوائية
            student_courses = random.sample(list(courses), random.randint(3, 5))
            
            for course in student_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    semester=current_semester,
                    defaults={
                        'enrollment_date': datetime.now() - timedelta(days=random.randint(1, 60))
                    }
                )
                
                if created:
                    # إضافة درجات عشوائية
                    Grade.objects.create(
                        student=student,
                        course=course,
                        semester=current_semester,
                        midterm_grade=random.randint(60, 100),
                        final_grade=random.randint(60, 100),
                        assignment_grade=random.randint(70, 100),
                        participation_grade=random.randint(80, 100)
                    )
                    
                    self.stdout.write(f'تم تسجيل {student.user.get_full_name()} في {course.name}')

    def create_fees_and_payments(self):
        """إنشاء الرسوم والمدفوعات"""
        students = Student.objects.all()
        current_semester = Semester.objects.filter(is_active=True).first()
        
        if not current_semester:
            return
            
        for student in students:
            # إنشاء رسوم دراسية
            fee = Fee.objects.create(
                student=student,
                semester=current_semester,
                amount=Decimal('5000.00'),
                fee_type='tuition',
                description='رسوم دراسية',
                due_date=datetime.now() + timedelta(days=30)
            )
            
            # إنشاء دفعة جزئية
            if random.choice([True, False]):
                Payment.objects.create(
                    student=student,
                    fee=fee,
                    amount=Decimal(str(random.randint(1000, 5000))),
                    payment_method='bank_transfer',
                    payment_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                    reference_number=f'PAY{random.randint(100000, 999999)}'
                )
                
            self.stdout.write(f'تم إنشاء رسوم ومدفوعات للطالب: {student.user.get_full_name()}')

    def create_scholarships(self):
        """إنشاء المنح الدراسية"""
        students = list(Student.objects.all())
        scholarship_students = random.sample(students, min(3, len(students)))
        
        scholarship_types = [
            {'name': 'منحة التفوق الأكاديمي', 'percentage': 50},
            {'name': 'منحة الحاجة المالية', 'percentage': 75},
            {'name': 'منحة الإعاقة', 'percentage': 100},
        ]
        
        for i, student in enumerate(scholarship_students):
            scholarship_type = scholarship_types[i % len(scholarship_types)]
            Scholarship.objects.create(
                student=student,
                name=scholarship_type['name'],
                amount=Decimal('2500.00'),
                percentage=scholarship_type['percentage'],
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now() + timedelta(days=365),
                status='active'
            )
            
            self.stdout.write(f'تم منح {scholarship_type["name"]} للطالب: {student.user.get_full_name()}')

    def create_salaries(self):
        """إنشاء الرواتب"""
        employees = Employee.objects.all()
        
        for employee in employees:
            # إنشاء راتب للشهر الحالي
            Salary.objects.create(
                employee=employee,
                month=datetime.now().month,
                year=datetime.now().year,
                basic_salary=employee.salary,
                allowances=Decimal(str(random.randint(500, 2000))),
                deductions=Decimal(str(random.randint(100, 500))),
                bonus=Decimal(str(random.randint(0, 1000))),
                status='paid'
            )
            
            self.stdout.write(f'تم إنشاء راتب للموظف: {employee.user.get_full_name()}')

    def create_notifications(self):
        """إنشاء الإشعارات"""
        users = User.objects.all()
        
        notifications_data = [
            {'title': 'بداية الفصل الدراسي', 'message': 'مرحباً بكم في الفصل الدراسي الجديد'},
            {'title': 'موعد الامتحانات', 'message': 'ستبدأ امتحانات منتصف الفصل الأسبوع القادم'},
            {'title': 'تحديث النظام', 'message': 'تم تحديث نظام إدارة الجامعة بميزات جديدة'},
            {'title': 'دفع الرسوم', 'message': 'تذكير بدفع الرسوم الدراسية قبل الموعد المحدد'},
            {'title': 'نتائج الامتحانات', 'message': 'تم نشر نتائج امتحانات منتصف الفصل'},
        ]
        
        for user in users:
            # إرسال 2-3 إشعارات عشوائية لكل مستخدم
            user_notifications = random.sample(notifications_data, random.randint(2, 3))
            
            for notif_data in user_notifications:
                Notification.objects.create(
                    user=user,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    is_read=random.choice([True, False])
                )
                
        self.stdout.write(f'تم إنشاء الإشعارات لجميع المستخدمين')