"""
Academic App Signals
Handle automatic updates when academic records are modified
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db.models import Avg
from django.utils import timezone

from .models import Grade, Enrollment, Attendance
from students.models import Student


@receiver(post_save, sender=Grade)
def update_enrollment_grade(sender, instance, created, **kwargs):
    """
    Update enrollment final grade when a new grade is added or updated
    """
    if instance.date_graded:
        enrollment = instance.enrollment
        
        # Calculate weighted average of all graded assignments
        grades = Grade.objects.filter(
            enrollment=enrollment,
            date_graded__isnull=False
        )
        
        if grades.exists():
            total_points = sum(grade.points_earned * grade.weight for grade in grades)
            total_possible = sum(grade.points_possible * grade.weight for grade in grades)
            
            if total_possible > 0:
                final_grade = (total_points / total_possible) * 100
                enrollment.final_grade = round(final_grade, 2)
                enrollment.save(update_fields=['final_grade'])
                
                # Update student GPA
                update_student_gpa(enrollment.student)


@receiver(post_save, sender=Enrollment)
def update_student_gpa_on_enrollment(sender, instance, created, **kwargs):
    """
    Update student GPA when enrollment status or final grade changes
    """
    if instance.final_grade is not None:
        update_student_gpa(instance.student)


def update_student_gpa(student):
    """
    Calculate and update student's cumulative GPA
    """
    from .models import GradeScale
    
    # Get all completed enrollments with final grades
    completed_enrollments = Enrollment.objects.filter(
        student=student,
        final_grade__isnull=False,
        status__in=['COMPLETED', 'ENROLLED']
    ).select_related('course')
    
    if not completed_enrollments.exists():
        return
    
    total_grade_points = 0
    total_credit_hours = 0
    
    for enrollment in completed_enrollments:
        # Find corresponding grade scale
        grade_scale = GradeScale.objects.filter(
            min_percentage__lte=enrollment.final_grade,
            max_percentage__gte=enrollment.final_grade
        ).first()
        
        if grade_scale:
            grade_points = grade_scale.gpa_points * enrollment.course.credits
            total_grade_points += grade_points
            total_credit_hours += enrollment.course.credits
    
    if total_credit_hours > 0:
        new_gpa = total_grade_points / total_credit_hours
        student.gpa = round(new_gpa, 2)
        student.save(update_fields=['gpa'])


@receiver(post_save, sender=Attendance)
def check_attendance_warnings(sender, instance, created, **kwargs):
    """
    Check if student needs attendance warning
    """
    if created:
        enrollment = instance.enrollment
        
        # Calculate attendance rate
        total_sessions = Attendance.objects.filter(enrollment=enrollment).count()
        present_sessions = Attendance.objects.filter(
            enrollment=enrollment,
            status__in=['PRESENT', 'LATE']
        ).count()
        
        if total_sessions > 0:
            attendance_rate = (present_sessions / total_sessions) * 100
            
            # Send warning if attendance is below 75%
            if attendance_rate < 75 and total_sessions >= 5:  # At least 5 sessions recorded
                # This would trigger a notification
                # Implementation depends on your notification system
                pass


@receiver(pre_delete, sender=Grade)
def recalculate_grade_on_delete(sender, instance, **kwargs):
    """
    Recalculate enrollment grade when a grade is deleted
    """
    enrollment = instance.enrollment
    
    # Get remaining grades (excluding the one being deleted)
    remaining_grades = Grade.objects.filter(
        enrollment=enrollment,
        date_graded__isnull=False
    ).exclude(id=instance.id)
    
    if remaining_grades.exists():
        total_points = sum(grade.points_earned * grade.weight for grade in remaining_grades)
        total_possible = sum(grade.points_possible * grade.weight for grade in remaining_grades)
        
        if total_possible > 0:
            final_grade = (total_points / total_possible) * 100
            enrollment.final_grade = round(final_grade, 2)
        else:
            enrollment.final_grade = None
    else:
        enrollment.final_grade = None
    
    enrollment.save(update_fields=['final_grade'])
    
    # Update student GPA
    update_student_gpa(enrollment.student)