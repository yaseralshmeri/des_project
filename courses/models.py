from django.db import models
from students.models import User, Department, Student
from django.core.validators import MinValueValidator, MaxValueValidator

class Course(models.Model):
    """
    Course model representing university courses.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ARCHIVED', 'Archived'),
    ]
    
    code = models.CharField(max_length=20, unique=True)  # Changed from course_code
    name = models.CharField(max_length=200)  # Changed from title
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    credit_hours = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])  # Alias for credits
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 limit_choices_to={'role': 'TEACHER'}, related_name='courses_taught')
    semester_offered = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    max_capacity = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)  # Changed from status
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Ensure credit_hours matches credits
        if not self.credit_hours:
            self.credit_hours = self.credits
        super().save(*args, **kwargs)


class CourseOffering(models.Model):
    """
    Represents a specific offering of a course in a particular semester.
    """
    SEMESTER_CHOICES = [
        ('FALL', 'Fall'),
        ('SPRING', 'Spring'),
        ('SUMMER', 'Summer'),
    ]
    
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                               limit_choices_to={'role': 'TEACHER'}, related_name='teaching_courses')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.IntegerField()
    schedule_day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    current_enrollment = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_offerings'
        ordering = ['-academic_year', 'semester']
        unique_together = ['course', 'semester', 'academic_year', 'instructor']
    
    def __str__(self):
        return f"{self.course.code} - {self.semester} {self.academic_year}"
    
    @property
    def is_full(self):
        return self.current_enrollment >= self.course.max_capacity


class Assignment(models.Model):
    """
    Assignments for course offerings.
    """
    TYPE_CHOICES = [
        ('HOMEWORK', 'Homework'),
        ('QUIZ', 'Quiz'),
        ('EXAM', 'Exam'),
        ('PROJECT', 'Project'),
        ('LAB', 'Lab'),
    ]
    
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    due_date = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.course_offering.course.code} - {self.title}"


# Enrollment and Grade models are now in academic app
# Import them from there when needed