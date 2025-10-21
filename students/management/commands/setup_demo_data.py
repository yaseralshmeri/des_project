"""
Management command to create demo data for University Management System
Creates sample users, courses, enrollments, grades, and other test data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from students.models import User
from courses.models import Department
from courses.models import Course
from academic.models import (
    AcademicYear, Semester, Enrollment, Grade, Attendance, 
    Schedule, GradeScale, AcademicProgram, AcademicCalendar
)
from finance.models import Payment, Invoice
from notifications.models import NotificationTemplate, Announcement

User = get_user_model()


class Command(BaseCommand):
    help = 'Create comprehensive demo data for the University Management System'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing demo data before creating new data',
        )
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='Number of demo students to create (default: 50)',
        )
        parser.add_argument(
            '--teachers',
            type=int,
            default=10,
            help='Number of demo teachers to create (default: 10)',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Deleting existing demo data...')
            self.reset_data()
        
        self.stdout.write('Creating demo data for University Management System...')
        
        # Create basic data
        self.create_grade_scales()
        self.create_departments()
        self.create_academic_programs()
        self.create_academic_years()
        self.create_semesters()
        self.create_courses()
        
        # Create users
        self.create_admin_users()
        self.create_teachers(options['teachers'])
        self.create_students(options['students'])
        
        # Create academic data
        self.create_schedules()
        self.create_enrollments()
        self.create_grades()
        self.create_attendance()
        
        # Create financial data
        self.create_payments()
        
        # Create notifications
        self.create_notification_templates()
        self.create_announcements()
        
        # Create calendar events
        self.create_calendar_events()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created demo data!')
        )
    
    def reset_data(self):
        """Delete existing demo data"""
        # Delete in reverse dependency order
        Grade.objects.all().delete()
        Attendance.objects.all().delete()
        Enrollment.objects.all().delete()
        Payment.objects.filter(student__user__username__startswith='demo_').delete()
        Student.objects.filter(user__username__startswith='demo_').delete()
        User.objects.filter(username__startswith='demo_').delete()
        Course.objects.filter(code__startswith='DEMO').delete()
        Schedule.objects.all().delete()
        AcademicCalendar.objects.all().delete()
        Announcement.objects.all().delete()
        
        self.stdout.write('Demo data deleted.')
    
    def create_grade_scales(self):
        """Create standard grading scale"""
        grade_scales = [
            ('A+', 97, 100, 4.0, True),
            ('A', 93, 96, 4.0, True),
            ('A-', 90, 92, 3.7, True),
            ('B+', 87, 89, 3.3, True),
            ('B', 83, 86, 3.0, True),
            ('B-', 80, 82, 2.7, True),
            ('C+', 77, 79, 2.3, True),
            ('C', 73, 76, 2.0, True),
            ('C-', 70, 72, 1.7, True),
            ('D+', 67, 69, 1.3, True),
            ('D', 63, 66, 1.0, True),
            ('D-', 60, 62, 0.7, True),
            ('F', 0, 59, 0.0, False),
        ]
        
        for letter, min_pct, max_pct, gpa, passing in grade_scales:
            GradeScale.objects.get_or_create(
                letter_grade=letter,
                defaults={
                    'min_percentage': min_pct,
                    'max_percentage': max_pct,
                    'gpa_points': gpa,
                    'is_passing': passing
                }
            )
        
        self.stdout.write('Created grading scale.')
    
    def create_departments(self):
        """Create academic departments"""
        departments_data = [
            ('Computer Science', 'CS', 'Department of Computer Science and Engineering'),
            ('Mathematics', 'MATH', 'Department of Mathematics'),
            ('Physics', 'PHYS', 'Department of Physics'),
            ('Chemistry', 'CHEM', 'Department of Chemistry'),
            ('Biology', 'BIO', 'Department of Biology'),
            ('English', 'ENG', 'Department of English Literature'),
            ('History', 'HIST', 'Department of History'),
            ('Psychology', 'PSYC', 'Department of Psychology'),
            ('Business Administration', 'BUS', 'School of Business Administration'),
            ('Economics', 'ECON', 'Department of Economics'),
        ]
        
        for name, code, description in departments_data:
            Department.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description
                }
            )
        
        self.stdout.write('Created departments.')
    
    def create_academic_programs(self):
        """Create academic programs"""
        departments = Department.objects.all()
        
        program_types = ['BACHELOR', 'MASTER', 'DOCTORATE']
        
        for dept in departments:
            for program_type in program_types[:2]:  # Only Bachelor's and Master's for demo
                credits = 120 if program_type == 'BACHELOR' else 30
                semesters = 8 if program_type == 'BACHELOR' else 4
                
                AcademicProgram.objects.get_or_create(
                    code=f"{dept.code}_{program_type[:2]}",
                    defaults={
                        'name': f"{program_type.title()}'s in {dept.name}",
                        'degree_type': program_type,
                        'department': dept,
                        'required_credits': credits,
                        'duration_semesters': semesters,
                        'description': f"{program_type.title()} degree program in {dept.name}",
                        'is_active': True
                    }
                )
        
        self.stdout.write('Created academic programs.')
    
    def create_academic_years(self):
        """Create academic years"""
        current_year = timezone.now().year
        
        for year in range(current_year - 1, current_year + 2):
            start_date = datetime(year, 9, 1).date()
            end_date = datetime(year + 1, 5, 31).date()
            
            academic_year, created = AcademicYear.objects.get_or_create(
                name=f"{year}-{year + 1}",
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_current': year == current_year
                }
            )
        
        self.stdout.write('Created academic years.')
    
    def create_semesters(self):
        """Create semesters"""
        current_academic_year = AcademicYear.objects.filter(is_current=True).first()
        
        if current_academic_year:
            # Fall semester
            Semester.objects.get_or_create(
                academic_year=current_academic_year,
                name='FALL',
                defaults={
                    'start_date': datetime(current_academic_year.start_date.year, 9, 1).date(),
                    'end_date': datetime(current_academic_year.start_date.year, 12, 15).date(),
                    'registration_start': datetime(current_academic_year.start_date.year, 8, 1).date(),
                    'registration_end': datetime(current_academic_year.start_date.year, 8, 31).date(),
                    'is_current': True
                }
            )
            
            # Spring semester
            Semester.objects.get_or_create(
                academic_year=current_academic_year,
                name='SPRING',
                defaults={
                    'start_date': datetime(current_academic_year.end_date.year, 1, 15).date(),
                    'end_date': datetime(current_academic_year.end_date.year, 5, 15).date(),
                    'registration_start': datetime(current_academic_year.end_date.year - 1, 11, 1).date(),
                    'registration_end': datetime(current_academic_year.end_date.year - 1, 11, 30).date(),
                    'is_current': False
                }
            )
        
        self.stdout.write('Created semesters.')
    
    def create_courses(self):
        """Create sample courses"""
        departments = Department.objects.all()
        
        course_templates = [
            ('Introduction to {}', 101, 3, 'Introductory course covering fundamental concepts'),
            ('Intermediate {}', 201, 3, 'Intermediate level course building on foundational knowledge'),
            ('Advanced {}', 301, 4, 'Advanced topics and applications'),
            ('{} Research Methods', 401, 3, 'Research methodologies and techniques'),
            ('Applied {}', 451, 4, 'Practical applications and real-world projects'),
        ]
        
        for dept in departments:
            for template, course_num, credits, desc in course_templates:
                title = template.format(dept.name)
                code = f"DEMO{dept.code}{course_num}"
                
                Course.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': title,
                        'description': desc,
                        'credits': credits,
                        'department': dept,
                        'is_active': True
                    }
                )
        
        self.stdout.write('Created sample courses.')
    
    def create_admin_users(self):
        """Create admin and staff users"""
        # Super admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='ADMIN',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write('Created admin user: admin/admin123')
        
        # Staff members
        staff_data = [
            ('staff', 'Staff', 'Member', 'staff@university.edu'),
            ('registrar', 'Academic', 'Registrar', 'registrar@university.edu'),
            ('finance', 'Finance', 'Officer', 'finance@university.edu'),
        ]
        
        for username, first_name, last_name, email in staff_data:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=f'{username}123',
                    first_name=first_name,
                    last_name=last_name,
                    role='STAFF',
                    is_staff=True
                )
                self.stdout.write(f'Created staff user: {username}/{username}123')
    
    def create_teachers(self, count):
        """Create demo teachers"""
        departments = list(Department.objects.all())
        
        teacher_names = [
            ('John', 'Smith'), ('Jane', 'Doe'), ('Michael', 'Johnson'), ('Sarah', 'Williams'),
            ('David', 'Brown'), ('Emily', 'Davis'), ('Robert', 'Miller'), ('Lisa', 'Wilson'),
            ('James', 'Moore'), ('Mary', 'Taylor'), ('Christopher', 'Anderson'), ('Jennifer', 'Thomas'),
            ('Daniel', 'Jackson'), ('Patricia', 'White'), ('Matthew', 'Harris'), ('Linda', 'Martin'),
            ('Anthony', 'Thompson'), ('Barbara', 'Garcia'), ('Mark', 'Martinez'), ('Susan', 'Robinson')
        ]
        
        for i in range(min(count, len(teacher_names))):
            first_name, last_name = teacher_names[i]
            username = f'demo_teacher_{i+1:02d}'
            
            if not User.objects.filter(username=username).exists():
                teacher = User.objects.create_user(
                    username=username,
                    email=f'{username}@university.edu',
                    password='teacher123',
                    first_name=first_name,
                    last_name=last_name,
                    role='TEACHER'
                )
                
                # Assign to random department
                dept = random.choice(departments)
                if not dept.head_of_department:
                    dept.head_of_department = teacher
                    dept.save()
        
        self.stdout.write(f'Created {count} demo teachers.')
    
    def create_students(self, count):
        """Create demo students"""
        departments = list(Department.objects.all())
        
        first_names = ['Alex', 'Sam', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Blake']
        last_names = ['Johnson', 'Smith', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'demo_student_{i+1:03d}'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@student.university.edu',
                    password='student123',
                    first_name=first_name,
                    last_name=last_name,
                    role='STUDENT'
                )
                
                # Create student profile
                student = Student.objects.create(
                    user=user,
                    student_id=f'STU{i+1:06d}',
                    enrollment_date=timezone.now().date() - timedelta(days=random.randint(30, 365*2)),
                    major=random.choice(departments).name,
                    current_semester=random.randint(1, 8),
                    gpa=round(random.uniform(2.0, 4.0), 2),
                    status='ACTIVE'
                )
        
        self.stdout.write(f'Created {count} demo students.')
    
    def create_schedules(self):
        """Create class schedules"""
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            return
        
        courses = list(Course.objects.filter(code__startswith='DEMO'))
        teachers = list(User.objects.filter(role='TEACHER'))
        
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
        times = [
            ('09:00', '10:30'),
            ('11:00', '12:30'),
            ('13:30', '15:00'),
            ('15:30', '17:00'),
        ]
        rooms = ['A101', 'A102', 'B201', 'B202', 'C301', 'C302', 'Lab1', 'Lab2']
        
        for course in courses[:20]:  # Limit to first 20 courses
            teacher = random.choice(teachers)
            day = random.choice(days)
            start_time, end_time = random.choice(times)
            room = random.choice(rooms)
            
            Schedule.objects.get_or_create(
                course=course,
                semester=current_semester,
                day_of_week=day,
                start_time=start_time,
                defaults={
                    'instructor': teacher,
                    'end_time': end_time,
                    'room': room,
                    'building': 'Main Building'
                }
            )
        
        self.stdout.write('Created class schedules.')
    
    def create_enrollments(self):
        """Create student enrollments"""
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            return
        
        students = list(Student.objects.all())
        courses = list(Course.objects.filter(code__startswith='DEMO'))
        
        for student in students:
            # Enroll each student in 3-6 random courses
            num_courses = random.randint(3, 6)
            student_courses = random.sample(courses, min(num_courses, len(courses)))
            
            for course in student_courses:
                Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    semester=current_semester,
                    defaults={
                        'status': random.choices(
                            ['ENROLLED', 'COMPLETED', 'DROPPED'],
                            weights=[80, 15, 5]
                        )[0]
                    }
                )
        
        self.stdout.write('Created student enrollments.')
    
    def create_grades(self):
        """Create sample grades"""
        enrollments = Enrollment.objects.filter(status='ENROLLED')
        
        grade_types = ['ASSIGNMENT', 'QUIZ', 'MIDTERM', 'FINAL', 'PROJECT']
        
        for enrollment in enrollments:
            # Create 3-8 grades per enrollment
            num_grades = random.randint(3, 8)
            
            for i in range(num_grades):
                grade_type = random.choice(grade_types)
                points_possible = random.choice([10, 20, 50, 100])
                points_earned = random.uniform(0.6, 1.0) * points_possible  # 60-100% scores
                
                Grade.objects.create(
                    enrollment=enrollment,
                    grade_type=grade_type,
                    title=f"{grade_type.title()} {i+1}",
                    points_earned=round(points_earned, 2),
                    points_possible=points_possible,
                    weight=1.0,
                    date_assigned=timezone.now().date() - timedelta(days=random.randint(1, 60)),
                    date_due=timezone.now().date() - timedelta(days=random.randint(-30, 30)),
                    date_graded=timezone.now() - timedelta(days=random.randint(0, 30))
                )
        
        self.stdout.write('Created sample grades.')
    
    def create_attendance(self):
        """Create attendance records"""
        enrollments = Enrollment.objects.filter(status='ENROLLED')
        
        for enrollment in enrollments:
            # Create attendance for the last 30 days
            for i in range(30):
                date = timezone.now().date() - timedelta(days=i)
                
                # Skip weekends
                if date.weekday() >= 5:
                    continue
                
                status = random.choices(
                    ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED'],
                    weights=[80, 10, 8, 2]
                )[0]
                
                Attendance.objects.get_or_create(
                    enrollment=enrollment,
                    date=date,
                    defaults={
                        'status': status,
                        'recorded_by': enrollment.course.schedules.first().instructor if enrollment.course.schedules.exists() else None
                    }
                )
        
        self.stdout.write('Created attendance records.')
    
    def create_payments(self):
        """Create payment records"""
        students = Student.objects.all()
        
        payment_types = [
            ('Tuition Fee', 2500.00),
            ('Lab Fee', 150.00),
            ('Library Fee', 50.00),
            ('Registration Fee', 100.00),
            ('Technology Fee', 200.00),
        ]
        
        for student in students:
            for payment_type, amount in payment_types:
                Payment.objects.create(
                    student=student,
                    amount=amount + random.uniform(-50, 50),  # Add some variation
                    description=payment_type,
                    due_date=timezone.now().date() + timedelta(days=random.randint(-30, 60)),
                    status=random.choices(
                        ['PENDING', 'PAID', 'OVERDUE'],
                        weights=[40, 50, 10]
                    )[0],
                    payment_date=timezone.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.4 else None
                )
        
        self.stdout.write('Created payment records.')
    
    def create_notification_templates(self):
        """Create notification templates"""
        templates = [
            ('ENROLLMENT_CONFIRMATION', 'Enrollment Confirmation', 
             'Welcome to {course_name}!', 
             'You have been successfully enrolled in {course_name} ({course_code}) for {semester}.'),
            
            ('GRADE_POSTED', 'New Grade Available', 
             'Grade posted for {course_name}', 
             'Your grade for {assignment_title} has been posted: {grade}%'),
            
            ('PAYMENT_DUE', 'Payment Due Notice', 
             'Payment Due: {description}', 
             'Your payment of ${amount} for {description} is due on {due_date}.'),
            
            ('ASSIGNMENT_DUE', 'Assignment Due Reminder', 
             'Assignment Due: {assignment_title}', 
             'Your assignment {assignment_title} for {course_name} is due on {due_date}.'),
        ]
        
        for template_type, name, subject, email_content in templates:
            NotificationTemplate.objects.get_or_create(
                template_type=template_type,
                defaults={
                    'name': name,
                    'subject_template': subject,
                    'email_template': email_content,
                    'sms_template': email_content[:150],  # Truncate for SMS
                    'is_active': True
                }
            )
        
        self.stdout.write('Created notification templates.')
    
    def create_announcements(self):
        """Create sample announcements"""
        admin_user = User.objects.filter(role='ADMIN').first()
        if not admin_user:
            return
        
        announcements = [
            ('Welcome to New Semester', 'Welcome to the new academic semester! We wish all students success in their studies.', 'NORMAL', 'ALL'),
            ('Registration Deadline Approaching', 'Don\'t forget! Course registration deadline is approaching. Please complete your registration soon.', 'HIGH', 'STUDENTS'),
            ('Library Hours Extended', 'Library hours have been extended during finals week. Open 24/7 for student convenience.', 'NORMAL', 'ALL'),
            ('System Maintenance Notice', 'The student portal will be unavailable for maintenance this Saturday from 2-4 AM.', 'HIGH', 'ALL'),
            ('New Course Offerings', 'Exciting new courses have been added for next semester. Check the course catalog for details.', 'NORMAL', 'STUDENTS'),
        ]
        
        for title, content, priority, audience in announcements:
            Announcement.objects.create(
                title=title,
                content=content,
                audience=audience,
                priority=priority,
                is_published=True,
                created_by=admin_user
            )
        
        self.stdout.write('Created sample announcements.')
    
    def create_calendar_events(self):
        """Create academic calendar events"""
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            return
        
        events = [
            ('Semester Begins', 'SEMESTER_START', current_semester.start_date),
            ('Last Day to Add/Drop', 'OTHER', current_semester.start_date + timedelta(days=14)),
            ('Midterm Exams Begin', 'EXAM_PERIOD_START', current_semester.start_date + timedelta(days=60)),
            ('Midterm Exams End', 'EXAM_PERIOD_END', current_semester.start_date + timedelta(days=67)),
            ('Spring Break', 'BREAK', current_semester.start_date + timedelta(days=80)),
            ('Final Exams Begin', 'EXAM_PERIOD_START', current_semester.end_date - timedelta(days=14)),
            ('Final Exams End', 'EXAM_PERIOD_END', current_semester.end_date - timedelta(days=7)),
            ('Semester Ends', 'SEMESTER_END', current_semester.end_date),
            ('Graduation Ceremony', 'GRADUATION', current_semester.end_date + timedelta(days=7)),
        ]
        
        for title, event_type, date in events:
            AcademicCalendar.objects.get_or_create(
                title=title,
                event_type=event_type,
                date=date,
                defaults={
                    'semester': current_semester,
                    'is_holiday': event_type == 'BREAK'
                }
            )
        
        self.stdout.write('Created calendar events.')