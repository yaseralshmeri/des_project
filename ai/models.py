from django.db import models
from students.models import Student
from courses.models import Course

class PerformancePrediction(models.Model):
    """
    AI-based performance predictions for students.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performance_predictions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='performance_predictions')
    predicted_grade = models.CharField(max_length=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    factors = models.JSONField(help_text="Factors influencing the prediction")
    recommendations = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'performance_predictions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.course.course_code} - {self.predicted_grade}"


class CourseRecommendation(models.Model):
    """
    AI-based course recommendations for students.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_recommendations')
    recommended_course = models.ForeignKey(Course, on_delete=models.CASCADE, 
                                          related_name='recommended_to_students')
    recommendation_score = models.DecimalField(max_digits=5, decimal_places=2)
    reasoning = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_recommendations'
        ordering = ['-recommendation_score']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.recommended_course.course_code}"


class StudyPattern(models.Model):
    """
    AI-analyzed study patterns and behaviors.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='study_patterns')
    analysis_period_start = models.DateField()
    analysis_period_end = models.DateField()
    pattern_data = models.JSONField(help_text="Analyzed study pattern data")
    strengths = models.TextField()
    weaknesses = models.TextField()
    improvement_suggestions = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'study_patterns'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.analysis_period_start} to {self.analysis_period_end}"
