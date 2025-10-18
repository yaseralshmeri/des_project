# FIX: Testing - إضافة اختبارات شاملة
"""
اختبارات النماذج الأساسية للنظام
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timedelta

from students.models import Student, StudentProfile
from courses.models import Course, Department, Semester
from academic.models import Enrollment, Grade
from finance.models import Payment, Fee, Scholarship
from hr.models import Employee, Department as HRDepartment

User = get_user_model()

class UserModelTest(TestCase):
    """اختبارات نموذج المستخدم"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user_data = {
            'username': 'test_user',
            'email': 'test@university.edu',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'password': 'test_password_123'
        }
    
    def test_create_user(self):
        """اختبار إنشاء مستخدم جديد"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'test@university.edu')
        self.assertEqual(user.first_name, 'أحمد')
        self.assertEqual(user.last_name, 'محمد')
        self.assertTrue(user.check_password('test_password_123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """اختبار إنشاء مستخدم إداري"""
        admin_data = self.user_data.copy()
        admin_data['username'] = 'admin'
        admin_data['email'] = 'admin@university.edu'
        
        admin = User.objects.create_superuser(**admin_data)
        
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
    
    def test_user_string_representation(self):
        """اختبار تمثيل المستخدم كنص"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name}"
        self.assertEqual(str(user), expected)
    
    def test_user_email_validation(self):
        """اختبار التحقق من البريد الإلكتروني"""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        
        with self.assertRaises(ValidationError):
            user = User(**invalid_data)
            user.full_clean()

class DepartmentModelTest(TestCase):
    """اختبارات نموذج القسم"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.department_data = {
            'name': 'قسم علوم الحاسوب',
            'code': 'CS',
            'description': 'قسم علوم الحاسوب وتقنية المعلومات'
        }
    
    def test_create_department(self):
        """اختبار إنشاء قسم جديد"""
        department = Department.objects.create(**self.department_data)
        
        self.assertEqual(department.name, 'قسم علوم الحاسوب')
        self.assertEqual(department.code, 'CS')
        self.assertEqual(department.description, 'قسم علوم الحاسوب وتقنية المعلومات')
    
    def test_department_string_representation(self):
        """اختبار تمثيل القسم كنص"""
        department = Department.objects.create(**self.department_data)
        self.assertEqual(str(department), 'قسم علوم الحاسوب')
    
    def test_department_code_unique(self):
        """اختبار فرادة رمز القسم"""
        Department.objects.create(**self.department_data)
        
        # محاولة إنشاء قسم آخر بنفس الرمز
        duplicate_data = self.department_data.copy()
        duplicate_data['name'] = 'قسم آخر'
        
        with self.assertRaises(Exception):
            Department.objects.create(**duplicate_data)

class CourseModelTest(TestCase):
    """اختبارات نموذج المقرر"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.department = Department.objects.create(
            name='قسم علوم الحاسوب',
            code='CS',
            description='قسم علوم الحاسوب'
        )
        
        self.course_data = {
            'name': 'مقدمة في البرمجة',
            'code': 'CS101',
            'credits': 3,
            'department': self.department,
            'description': 'مقرر أساسي في البرمجة'
        }
    
    def test_create_course(self):
        """اختبار إنشاء مقرر جديد"""
        course = Course.objects.create(**self.course_data)
        
        self.assertEqual(course.name, 'مقدمة في البرمجة')
        self.assertEqual(course.code, 'CS101')
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.department, self.department)
    
    def test_course_string_representation(self):
        """اختبار تمثيل المقرر كنص"""
        course = Course.objects.create(**self.course_data)
        expected = f"{course.code} - {course.name}"
        self.assertEqual(str(course), expected)
    
    def test_course_credits_validation(self):
        """اختبار التحقق من عدد الساعات المعتمدة"""
        invalid_data = self.course_data.copy()
        invalid_data['credits'] = -1
        
        with self.assertRaises(ValidationError):
            course = Course(**invalid_data)
            course.full_clean()

class StudentModelTest(TestCase):
    """اختبارات نموذج الطالب"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username='student1',
            email='student1@university.edu',
            first_name='علي',
            last_name='أحمد',
            password='password123'
        )
        
        self.department = Department.objects.create(
            name='قسم علوم الحاسوب',
            code='CS',
            description='قسم علوم الحاسوب'
        )
        
        self.student_data = {
            'user': self.user,
            'student_id': '2024001',
            'department': self.department,
            'enrollment_date': datetime.now().date()
        }
    
    def test_create_student(self):
        """اختبار إنشاء طالب جديد"""
        student = Student.objects.create(**self.student_data)
        
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.student_id, '2024001')
        self.assertEqual(student.department, self.department)
        self.assertTrue(student.is_active)
    
    def test_student_string_representation(self):
        """اختبار تمثيل الطالب كنص"""
        student = Student.objects.create(**self.student_data)
        expected = f"{student.student_id} - {student.user.get_full_name()}"
        self.assertEqual(str(student), expected)
    
    def test_student_id_unique(self):
        """اختبار فرادة رقم الطالب"""
        Student.objects.create(**self.student_data)
        
        # إنشاء مستخدم آخر
        user2 = User.objects.create_user(
            username='student2',
            email='student2@university.edu',
            password='password123'
        )
        
        # محاولة إنشاء طالب بنفس الرقم
        duplicate_data = self.student_data.copy()
        duplicate_data['user'] = user2
        
        with self.assertRaises(Exception):
            Student.objects.create(**duplicate_data)

class EnrollmentModelTest(TestCase):
    """اختبارات نموذج التسجيل"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        # إنشاء المستخدم
        self.user = User.objects.create_user(
            username='student1',
            email='student1@university.edu',
            password='password123'
        )
        
        # إنشاء القسم
        self.department = Department.objects.create(
            name='قسم علوم الحاسوب',
            code='CS'
        )
        
        # إنشاء الطالب
        self.student = Student.objects.create(
            user=self.user,
            student_id='2024001',
            department=self.department
        )
        
        # إنشاء المقرر
        self.course = Course.objects.create(
            name='مقدمة في البرمجة',
            code='CS101',
            credits=3,
            department=self.department
        )
        
        # إنشاء الفصل الدراسي
        self.semester = Semester.objects.create(
            name='الفصل الأول 2024',
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=120),
            is_active=True
        )
    
    def test_create_enrollment(self):
        """اختبار إنشاء تسجيل جديد"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            semester=self.semester
        )
        
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.semester, self.semester)
        self.assertEqual(enrollment.status, 'enrolled')
    
    def test_enrollment_string_representation(self):
        """اختبار تمثيل التسجيل كنص"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            semester=self.semester
        )
        
        expected = f"{self.student.student_id} - {self.course.code}"
        self.assertEqual(str(enrollment), expected)

class GradeModelTest(TestCase):
    """اختبارات نموذج الدرجات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        # إعداد البيانات الأساسية
        self.user = User.objects.create_user(
            username='student1',
            email='student1@university.edu',
            password='password123'
        )
        
        self.department = Department.objects.create(
            name='قسم علوم الحاسوب',
            code='CS'
        )
        
        self.student = Student.objects.create(
            user=self.user,
            student_id='2024001',
            department=self.department
        )
        
        self.course = Course.objects.create(
            name='مقدمة في البرمجة',
            code='CS101',
            credits=3,
            department=self.department
        )
        
        self.semester = Semester.objects.create(
            name='الفصل الأول 2024',
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=120),
            is_active=True
        )
    
    def test_create_grade(self):
        """اختبار إنشاء درجة جديدة"""
        grade = Grade.objects.create(
            student=self.student,
            course=self.course,
            semester=self.semester,
            midterm_grade=85,
            final_grade=90,
            assignment_grade=88,
            participation_grade=95
        )
        
        self.assertEqual(grade.student, self.student)
        self.assertEqual(grade.course, self.course)
        self.assertEqual(grade.midterm_grade, 85)
        self.assertEqual(grade.final_grade, 90)
    
    def test_grade_calculation(self):
        """اختبار حساب الدرجة الإجمالية"""
        grade = Grade.objects.create(
            student=self.student,
            course=self.course,
            semester=self.semester,
            midterm_grade=80,
            final_grade=90,
            assignment_grade=85,
            participation_grade=95
        )
        
        # افتراض أن النظام يحسب المتوسط المرجح
        expected_total = (80 * 0.3) + (90 * 0.4) + (85 * 0.2) + (95 * 0.1)
        self.assertAlmostEqual(grade.calculate_total_grade(), expected_total, places=2)

class PaymentModelTest(TestCase):
    """اختبارات نموذج المدفوعات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username='student1',
            email='student1@university.edu',
            password='password123'
        )
        
        self.department = Department.objects.create(
            name='قسم علوم الحاسوب',
            code='CS'
        )
        
        self.student = Student.objects.create(
            user=self.user,
            student_id='2024001',
            department=self.department
        )
        
        self.semester = Semester.objects.create(
            name='الفصل الأول 2024',
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=120),
            is_active=True
        )
        
        self.fee = Fee.objects.create(
            student=self.student,
            semester=self.semester,
            amount=Decimal('5000.00'),
            fee_type='tuition',
            description='رسوم دراسية'
        )
    
    def test_create_payment(self):
        """اختبار إنشاء دفعة جديدة"""
        payment = Payment.objects.create(
            student=self.student,
            fee=self.fee,
            amount=Decimal('2500.00'),
            payment_method='bank_transfer',
            reference_number='PAY123456'
        )
        
        self.assertEqual(payment.student, self.student)
        self.assertEqual(payment.fee, self.fee)
        self.assertEqual(payment.amount, Decimal('2500.00'))
        self.assertEqual(payment.payment_method, 'bank_transfer')
    
    def test_payment_amount_validation(self):
        """اختبار التحقق من مبلغ الدفعة"""
        with self.assertRaises(ValidationError):
            payment = Payment(
                student=self.student,
                fee=self.fee,
                amount=Decimal('-100.00'),  # مبلغ سالب
                payment_method='cash'
            )
            payment.full_clean()

class EmployeeModelTest(TestCase):
    """اختبارات نموذج الموظف"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username='employee1',
            email='employee1@university.edu',
            password='password123',
            first_name='محمد',
            last_name='سالم'
        )
        
        self.hr_department = HRDepartment.objects.create(
            name='الموارد البشرية',
            description='إدارة الموارد البشرية'
        )
    
    def test_create_employee(self):
        """اختبار إنشاء موظف جديد"""
        employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP2024001',
            department=self.hr_department,
            position='محاسب',
            salary=Decimal('8000.00')
        )
        
        self.assertEqual(employee.user, self.user)
        self.assertEqual(employee.employee_id, 'EMP2024001')
        self.assertEqual(employee.department, self.hr_department)
        self.assertEqual(employee.position, 'محاسب')
        self.assertEqual(employee.salary, Decimal('8000.00'))
    
    def test_employee_string_representation(self):
        """اختبار تمثيل الموظف كنص"""
        employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP2024001',
            department=self.hr_department,
            position='محاسب',
            salary=Decimal('8000.00')
        )
        
        expected = f"{employee.employee_id} - {employee.user.get_full_name()}"
        self.assertEqual(str(employee), expected)