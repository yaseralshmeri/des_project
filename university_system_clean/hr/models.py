from django.db import models
from students.models import User, Department
from django.core.validators import MinValueValidator

class Employee(models.Model):
    """
    Employee profile extending the User model.
    """
    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('TEMPORARY', 'Temporary'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('RESIGNED', 'Resigned'),
        ('TERMINATED', 'Terminated'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, 
                                  related_name='employees')
    position = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=15, choices=EMPLOYMENT_TYPE_CHOICES)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, 
                                 validators=[MinValueValidator(0.00)])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['-hire_date']
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class Teacher(models.Model):
    """
    Teacher profile with academic qualifications.
    """
    RANK_CHOICES = [
        ('LECTURER', 'Lecturer'),
        ('ASSISTANT_PROF', 'Assistant Professor'),
        ('ASSOCIATE_PROF', 'Associate Professor'),
        ('PROFESSOR', 'Professor'),
    ]
    
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='teacher_profile')
    academic_rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    specialization = models.CharField(max_length=200)
    qualifications = models.TextField()
    research_interests = models.TextField(blank=True)
    publications = models.TextField(blank=True)
    office_hours = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teachers'
        ordering = ['academic_rank']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.academic_rank}"


class EmployeeAttendance(models.Model):
    """
    Employee attendance records.
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
        ('ON_LEAVE', 'On Leave'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employee_attendance'
        unique_together = ['employee', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.status}"


class Leave(models.Model):
    """
    Employee leave applications.
    """
    LEAVE_TYPE_CHOICES = [
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('ANNUAL', 'Annual Leave'),
        ('MATERNITY', 'Maternity Leave'),
        ('PATERNITY', 'Paternity Leave'),
        ('UNPAID', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=15, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_leaves')
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaves'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type} ({self.start_date} to {self.end_date})"


class Salary(models.Model):
    """
    Employee salary records.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_records')
    month = models.IntegerField(validators=[MinValueValidator(1)])
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'salaries'
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.month}/{self.year}"
    
    @property
    def net_salary(self):
        return self.basic_salary + self.allowances + self.bonus - self.deductions
