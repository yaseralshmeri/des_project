from django.db import models
from students.models import User, Student
from django.core.validators import MinValueValidator

class FeeStructure(models.Model):
    """
    Fee structure for different programs and semesters.
    """
    PROGRAM_CHOICES = [
        ('UNDERGRADUATE', 'Undergraduate'),
        ('GRADUATE', 'Graduate'),
        ('DOCTORATE', 'Doctorate'),
    ]
    
    program_type = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    semester = models.IntegerField(validators=[MinValueValidator(1)])
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sports_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_structures'
        unique_together = ['program_type', 'semester']
    
    def __str__(self):
        return f"{self.program_type} - Semester {self.semester}"
    
    @property
    def total_fee(self):
        return (self.tuition_fee + self.lab_fee + self.library_fee + 
                self.sports_fee + self.other_fees)


class StudentFee(models.Model):
    """
    Fee records for individual students.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
        ('OVERDUE', 'Overdue'),
        ('WAIVED', 'Waived'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name='student_fees')
    academic_year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_fees'
        ordering = ['-academic_year', '-due_date']
        unique_together = ['student', 'fee_structure', 'academic_year']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.academic_year} - {self.status}"
    
    @property
    def outstanding_amount(self):
        return self.total_amount - self.paid_amount - self.discount


class Payment(models.Model):
    """
    Payment transactions.
    """
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('ONLINE', 'Online Payment'),
        ('CHEQUE', 'Cheque'),
    ]
    
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                 validators=[MinValueValidator(0.01)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                    related_name='received_payments')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"


class Scholarship(models.Model):
    """
    Scholarship programs.
    """
    TYPE_CHOICES = [
        ('MERIT', 'Merit-based'),
        ('NEED', 'Need-based'),
        ('SPORTS', 'Sports'),
        ('RESEARCH', 'Research'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    scholarship_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    eligibility_criteria = models.TextField()
    application_deadline = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scholarships'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ScholarshipApplication(models.Model):
    """
    Student scholarship applications.
    """
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarship_applications')
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications')
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUBMITTED')
    documents = models.TextField(blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='reviewed_scholarships')
    review_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scholarship_applications'
        unique_together = ['student', 'scholarship']
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.scholarship.name}"
