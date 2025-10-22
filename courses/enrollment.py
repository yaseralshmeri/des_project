# نموذج التسجيل في المقررات
# Course Enrollment Model

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Enrollment(models.Model):
    """تسجيل الطلاب في المقررات"""
    
    STATUS_CHOICES = [
        ('ENROLLED', 'مسجل'),
        ('WAITLISTED', 'قائمة انتظار'),
        ('DROPPED', 'منسحب'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'راسب'),
        ('WITHDRAWN', 'منسحب نهائياً'),
    ]
    
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D+', 'D+'),
        ('D', 'D'),
        ('F', 'F'),
        ('I', 'غير مكتمل'),
        ('W', 'منسحب'),
        ('P', 'ناجح'),
        ('NP', 'راسب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الطالب والمقرر
    student = models.ForeignKey(User, on_delete=models.CASCADE, 
                               limit_choices_to={'role': 'STUDENT'},
                               related_name='enrollments', verbose_name="الطالب")
    course_offering = models.ForeignKey('CourseOffering', on_delete=models.CASCADE,
                                       related_name='enrollments', verbose_name="عرض المقرر")
    
    # تفاصيل التسجيل
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ENROLLED',
                            verbose_name="حالة التسجيل")
    
    # الدرجات والتقييم
    midterm_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(100)],
                                       verbose_name="درجة منتصف الفصل")
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)],
                                     verbose_name="الدرجة النهائية")
    total_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)],
                                     verbose_name="الدرجة الإجمالية")
    letter_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True,
                                   verbose_name="الدرجة الحرفية")
    grade_points = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                      validators=[MinValueValidator(0), MaxValueValidator(4)],
                                      verbose_name="نقاط الدرجة")
    
    # معلومات الحضور
    total_absences = models.IntegerField(default=0, verbose_name="إجمالي الغياب")
    excused_absences = models.IntegerField(default=0, verbose_name="الغياب المعذور")
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)],
                                              verbose_name="نسبة الحضور")
    
    # التواريخ المهمة
    drop_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الحذف")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    enrolled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='processed_enrollments',
                                   verbose_name="مُسجل بواسطة")
    
    class Meta:
        verbose_name = "تسجيل مقرر"
        verbose_name_plural = "تسجيلات المقررات"
        ordering = ['-enrollment_date']
        unique_together = ['student', 'course_offering']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course_offering', 'status']),
            models.Index(fields=['enrollment_date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course_offering}"
    
    @property
    def is_passing(self):
        """هل الطالب ناجح"""
        if self.total_grade is not None:
            return float(self.total_grade) >= 60
        return False
    
    @property
    def gpa_contribution(self):
        """مساهمة المقرر في المعدل"""
        if self.grade_points is not None:
            return float(self.grade_points) * self.course_offering.course.credit_hours
        return 0
    
    @property
    def is_active(self):
        """هل التسجيل نشط"""
        return self.status in ['ENROLLED', 'WAITLISTED']