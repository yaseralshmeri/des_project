from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from students.models import User, Student, Department
from courses.models import Course, CourseOffering
from hr.models import Employee, Teacher

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@university.edu',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            role='ADMIN',
            phone='+1234567890'
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.username}'))
        
        cs_dept = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Department of Computer Science',
            head_of_department=admin
        )
        math_dept = Department.objects.create(
            name='Mathematics',
            code='MATH',
            description='Department of Mathematics'
        )
        self.stdout.write(self.style.SUCCESS(f'Created departments: CS, MATH'))
        
        teacher1_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@university.edu',
            password='teacher123',
            first_name='John',
            last_name='Smith',
            role='TEACHER',
            phone='+1234567891'
        )
        teacher1_emp = Employee.objects.create(
            user=teacher1_user,
            employee_id='EMP001',
            department=cs_dept,
            position='Professor',
            employment_type='FULL_TIME',
            hire_date=date(2015, 9, 1),
            salary=75000.00,
            status='ACTIVE'
        )
        teacher1 = Teacher.objects.create(
            employee=teacher1_emp,
            academic_rank='PROFESSOR',
            specialization='Software Engineering',
            qualifications='PhD in Computer Science',
            office_hours='Mon-Wed 2-4 PM'
        )
        
        teacher2_user = User.objects.create_user(
            username='teacher2',
            email='teacher2@university.edu',
            password='teacher123',
            first_name='Sarah',
            last_name='Johnson',
            role='TEACHER',
            phone='+1234567892'
        )
        teacher2_emp = Employee.objects.create(
            user=teacher2_user,
            employee_id='EMP002',
            department=math_dept,
            position='Associate Professor',
            employment_type='FULL_TIME',
            hire_date=date(2018, 9, 1),
            salary=65000.00,
            status='ACTIVE'
        )
        teacher2 = Teacher.objects.create(
            employee=teacher2_emp,
            academic_rank='ASSOCIATE_PROF',
            specialization='Calculus',
            qualifications='PhD in Mathematics',
            office_hours='Tue-Thu 3-5 PM'
        )
        self.stdout.write(self.style.SUCCESS(f'Created teachers: teacher1, teacher2'))
        
        students_data = [
            {'username': 'student1', 'first': 'Alice', 'last': 'Brown', 'id': 'STU001', 'major': 'Computer Science'},
            {'username': 'student2', 'first': 'Bob', 'last': 'Davis', 'id': 'STU002', 'major': 'Computer Science'},
            {'username': 'student3', 'first': 'Charlie', 'last': 'Wilson', 'id': 'STU003', 'major': 'Mathematics'},
            {'username': 'student4', 'first': 'Diana', 'last': 'Moore', 'id': 'STU004', 'major': 'Computer Science'},
            {'username': 'student5', 'first': 'Eve', 'last': 'Taylor', 'id': 'STU005', 'major': 'Mathematics'},
        ]
        
        for i, student_data in enumerate(students_data, 1):
            user = User.objects.create_user(
                username=student_data['username'],
                email=f"{student_data['username']}@university.edu",
                password='student123',
                first_name=student_data['first'],
                last_name=student_data['last'],
                role='STUDENT',
                phone=f'+123456789{i+2}'
            )
            Student.objects.create(
                user=user,
                student_id=student_data['id'],
                enrollment_date=date(2024, 9, 1),
                major=student_data['major'],
                current_semester=1,
                gpa=3.5,
                status='ACTIVE',
                guardian_name=f'Guardian of {student_data["first"]}',
                guardian_phone=f'+987654321{i}'
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created 5 students'))
        
        course1 = Course.objects.create(
            course_code='CS101',
            title='Introduction to Programming',
            description='Basic programming concepts',
            department=cs_dept,
            credits=3,
            semester_offered=1,
            max_capacity=30,
            status='ACTIVE'
        )
        
        course2 = Course.objects.create(
            course_code='MATH101',
            title='Calculus I',
            description='Differential and Integral Calculus',
            department=math_dept,
            credits=4,
            semester_offered=1,
            max_capacity=40,
            status='ACTIVE'
        )
        
        CourseOffering.objects.create(
            course=course1,
            teacher=teacher1_user,
            semester='FALL',
            academic_year=2024,
            schedule_day='MON',
            start_time='09:00',
            end_time='10:30',
            room='CS-101',
            current_enrollment=0
        )
        
        CourseOffering.objects.create(
            course=course2,
            teacher=teacher2_user,
            semester='FALL',
            academic_year=2024,
            schedule_day='TUE',
            start_time='10:00',
            end_time='11:30',
            room='MATH-201',
            current_enrollment=0
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created courses and offerings'))
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
        self.stdout.write(self.style.WARNING('Login credentials:'))
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Teachers: username=teacher1/teacher2, password=teacher123')
        self.stdout.write('  Students: username=student1/student2/student3/student4/student5, password=student123')
