from django.db import models
from students.models import User, Student
from courses.models import Course, CourseOffering

class StudentPerformanceReport(models.Model):
    """
    Generated performance reports for students.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performance_reports')
    academic_year = models.IntegerField()
    semester = models.IntegerField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    total_credits = models.IntegerField()
    credits_earned = models.IntegerField()
    rank_in_class = models.IntegerField(blank=True, null=True)
    total_students = models.IntegerField(blank=True, null=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                    related_name='generated_reports')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_performance_reports'
        unique_together = ['student', 'academic_year', 'semester']
        ordering = ['-academic_year', '-semester']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.academic_year}/{self.semester}"


class CourseAnalytics(models.Model):
    """
    Analytics and statistics for course offerings.
    """
    course_offering = models.OneToOneField(CourseOffering, on_delete=models.CASCADE, 
                                          related_name='analytics')
    total_enrolled = models.IntegerField(default=0)
    average_grade = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    dropout_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    student_satisfaction_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course_offering.course.course_code} - Analytics"


class EnrollmentStatistics(models.Model):
    """
    Overall enrollment statistics.
    """
    academic_year = models.IntegerField()
    semester = models.IntegerField()
    total_students = models.IntegerField(default=0)
    new_enrollments = models.IntegerField(default=0)
    graduated_students = models.IntegerField(default=0)
    dropped_students = models.IntegerField(default=0)
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollment_statistics'
        unique_together = ['academic_year', 'semester']
        ordering = ['-academic_year', '-semester']
    
    def __str__(self):
        return f"Enrollment Stats - {self.academic_year}/{self.semester}"
