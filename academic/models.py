from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from courses.models import Course
from students.models import Student

User = get_user_model()


class AcademicYear(models.Model):
    """Academic Year model for organizing semesters"""
    name = models.CharField(max_length=20, unique=True)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'academic'
        db_table = 'academic_years'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one academic year is current
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Semester(models.Model):
    """Semester model"""
    SEMESTER_CHOICES = [
        ('FALL', 'Fall Semester'),
        ('SPRING', 'Spring Semester'),
        ('SUMMER', 'Summer Semester'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    name = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_start = models.DateField()
    registration_end = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'semesters'
        unique_together = ('academic_year', 'name')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.academic_year.name} - {self.get_name_display()}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one semester is current
            Semester.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Enrollment(models.Model):
    """Student course enrollment"""
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('DROPPED', 'Dropped'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ENROLLED')
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ('student', 'course', 'semester')
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.course.code} ({self.semester})"


class Grade(models.Model):
    """Individual assignment/exam grades"""
    GRADE_TYPE_CHOICES = [
        ('ASSIGNMENT', 'Assignment'),
        ('QUIZ', 'Quiz'),
        ('MIDTERM', 'Midterm Exam'),
        ('FINAL', 'Final Exam'),
        ('PROJECT', 'Project'),
        ('PARTICIPATION', 'Class Participation'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    grade_type = models.CharField(max_length=15, choices=GRADE_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2,
                                       validators=[MinValueValidator(0)])
    points_possible = models.DecimalField(max_digits=5, decimal_places=2,
                                         validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=1.0,
                                validators=[MinValueValidator(0), MaxValueValidator(1)])
    date_assigned = models.DateField()
    date_due = models.DateField(null=True, blank=True)
    date_graded = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        ordering = ['-date_assigned']
    
    def __str__(self):
        return f"{self.enrollment} - {self.title}"
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.points_possible > 0:
            return (self.points_earned / self.points_possible) * 100
        return 0


class Attendance(models.Model):
    """Student attendance tracking"""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused Absence'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance'
        unique_together = ('enrollment', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.enrollment} - {self.date} ({self.status})"


class Schedule(models.Model):
    """Class schedule"""
    DAYS_OF_WEEK = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='schedules')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  limit_choices_to={'role': 'TEACHER'})
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    building = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'schedules'
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.course.code} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class GradeScale(models.Model):
    """University grading scale configuration"""
    letter_grade = models.CharField(max_length=2)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    gpa_points = models.DecimalField(max_digits=3, decimal_places=2,
                                    validators=[MinValueValidator(0), MaxValueValidator(4)])
    is_passing = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'grade_scales'
        ordering = ['-min_percentage']
    
    def __str__(self):
        return f"{self.letter_grade} ({self.min_percentage}%-{self.max_percentage}%)"


class AcademicProgram(models.Model):
    """Academic programs/majors offered by the university"""
    DEGREE_TYPES = [
        ('BACHELOR', 'Bachelor\'s Degree'),
        ('MASTER', 'Master\'s Degree'),
        ('DOCTORATE', 'Doctorate Degree'),
        ('CERTIFICATE', 'Certificate Program'),
        ('DIPLOMA', 'Diploma Program'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    degree_type = models.CharField(max_length=15, choices=DEGREE_TYPES)
    department = models.ForeignKey('students.Department', on_delete=models.CASCADE, related_name='programs')
    required_credits = models.IntegerField(validators=[MinValueValidator(1)])
    duration_semesters = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_programs'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_degree_type_display()})"


class Prerequisite(models.Model):
    """Course prerequisites"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisite_for')
    min_grade = models.DecimalField(max_digits=5, decimal_places=2, default=60.0,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        db_table = 'prerequisites'
        unique_together = ('course', 'prerequisite_course')
    
    def __str__(self):
        return f"{self.course.code} requires {self.prerequisite_course.code} (min {self.min_grade}%)"


class AcademicCalendar(models.Model):
    """University academic calendar events"""
    EVENT_TYPES = [
        ('SEMESTER_START', 'Semester Start'),
        ('SEMESTER_END', 'Semester End'),
        ('REGISTRATION_START', 'Registration Starts'),
        ('REGISTRATION_END', 'Registration Ends'),
        ('EXAM_PERIOD_START', 'Exam Period Starts'),
        ('EXAM_PERIOD_END', 'Exam Period Ends'),
        ('HOLIDAY', 'Holiday'),
        ('BREAK', 'Academic Break'),
        ('GRADUATION', 'Graduation Ceremony'),
        ('OTHER', 'Other Event'),
    ]
    
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # For multi-day events
    description = models.TextField(blank=True)
    is_holiday = models.BooleanField(default=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'academic_calendar'
        ordering = ['date']
    
    def __str__(self):
        return f"{self.title} - {self.date}"