from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """
    Custom User model with role-based permissions.
    Roles: ADMIN, STAFF, TEACHER, STUDENT
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('STAFF', 'Staff Member'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_staff_member(self):
        return self.role == 'STAFF'
    
    @property
    def is_teacher(self):
        return self.role == 'TEACHER'
    
    @property
    def is_student(self):
        return self.role == 'STUDENT'


class Student(models.Model):
    """
    Student profile extending the User model.
    Contains academic information specific to students.
    """
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('GRADUATED', 'Graduated'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    major = models.CharField(max_length=100)
    current_semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, 
                              validators=[MinValueValidator(0.00), MaxValueValidator(4.00)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


class Department(models.Model):
    """
    Academic departments in the university.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                          null=True, blank=True, 
                                          related_name='headed_departments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
