"""
Academic App Serializers
Enhanced serializers for academic management with comprehensive field coverage
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AcademicYear, Semester, Enrollment, Grade, Attendance,
    Schedule, GradeScale, AcademicProgram, Prerequisite, AcademicCalendar
)
from students.serializers import UserSerializer, StudentSerializer
from courses.serializers import CourseSerializer

User = get_user_model()


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializer for Academic Year model"""
    semesters_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'name', 'start_date', 'end_date', 'is_current',
            'semesters_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_semesters_count(self, obj):
        return obj.semesters.count()


class SemesterSerializer(serializers.ModelSerializer):
    """Serializer for Semester model"""
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    enrollments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Semester
        fields = [
            'id', 'academic_year', 'academic_year_name', 'name', 
            'start_date', 'end_date', 'registration_start', 'registration_end',
            'is_current', 'enrollments_count'
        ]
    
    def get_enrollments_count(self, obj):
        return obj.enrollments.count()


class GradeScaleSerializer(serializers.ModelSerializer):
    """Serializer for Grade Scale model"""
    
    class Meta:
        model = GradeScale
        fields = [
            'id', 'letter_grade', 'min_percentage', 'max_percentage',
            'gpa_points', 'is_passing'
        ]


class AcademicProgramSerializer(serializers.ModelSerializer):
    """Serializer for Academic Program model"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicProgram
        fields = [
            'id', 'name', 'code', 'degree_type', 'department', 'department_name',
            'required_credits', 'duration_semesters', 'description', 'is_active',
            'students_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_students_count(self, obj):
        # This would need to be implemented based on how students are linked to programs
        return 0  # Placeholder


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Class Schedule model"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    enrolled_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'course', 'course_name', 'course_code', 'semester', 'semester_name',
            'instructor', 'instructor_name', 'day_of_week', 'start_time', 'end_time',
            'room', 'building', 'enrolled_students'
        ]
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None
    
    def get_enrolled_students(self, obj):
        return obj.course.enrollments.filter(
            semester=obj.semester,
            status='ENROLLED'
        ).count()


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Student Enrollment model"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_name = serializers.CharField(source='semester.__str__', read_only=True)
    current_grade = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'student_id', 'course', 'course_name', 
            'course_code', 'semester', 'semester_name', 'enrollment_date', 'status',
            'final_grade', 'current_grade', 'attendance_rate'
        ]
        read_only_fields = ['enrollment_date']
    
    def get_current_grade(self, obj):
        """Calculate current grade based on completed assignments"""
        grades = obj.grades.filter(date_graded__isnull=False)
        if not grades.exists():
            return None
        
        total_points = sum(grade.points_earned * grade.weight for grade in grades)
        total_possible = sum(grade.points_possible * grade.weight for grade in grades)
        
        if total_possible > 0:
            return round((total_points / total_possible) * 100, 2)
        return None
    
    def get_attendance_rate(self, obj):
        """Calculate attendance rate"""
        total_sessions = obj.attendance_records.count()
        if total_sessions == 0:
            return None
        
        present_sessions = obj.attendance_records.filter(
            status__in=['PRESENT', 'LATE']
        ).count()
        
        return round((present_sessions / total_sessions) * 100, 2)


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for Grade model"""
    student_name = serializers.CharField(source='enrollment.student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='enrollment.student.student_id', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.name', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.code', read_only=True)
    percentage = serializers.ReadOnlyField()
    letter_grade = serializers.SerializerMethodField()
    
    class Meta:
        model = Grade
        fields = [
            'id', 'enrollment', 'student_name', 'student_id', 'course_name', 'course_code',
            'grade_type', 'title', 'points_earned', 'points_possible', 'percentage',
            'letter_grade', 'weight', 'date_assigned', 'date_due', 'date_graded',
            'feedback', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'percentage']
    
    def get_letter_grade(self, obj):
        """Get letter grade based on percentage"""
        percentage = obj.percentage
        grade_scale = GradeScale.objects.filter(
            min_percentage__lte=percentage,
            max_percentage__gte=percentage
        ).first()
        return grade_scale.letter_grade if grade_scale else None


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    student_name = serializers.CharField(source='enrollment.student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='enrollment.student.student_id', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.name', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.code', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'enrollment', 'student_name', 'student_id', 'course_name', 'course_code',
            'date', 'status', 'notes', 'recorded_by', 'recorded_by_name', 'recorded_at'
        ]
        read_only_fields = ['recorded_at']
    
    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None


class PrerequisiteSerializer(serializers.ModelSerializer):
    """Serializer for Course Prerequisites model"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    prerequisite_name = serializers.CharField(source='prerequisite_course.name', read_only=True)
    prerequisite_code = serializers.CharField(source='prerequisite_course.code', read_only=True)
    
    class Meta:
        model = Prerequisite
        fields = [
            'id', 'course', 'course_name', 'course_code',
            'prerequisite_course', 'prerequisite_name', 'prerequisite_code',
            'min_grade'
        ]


class AcademicCalendarSerializer(serializers.ModelSerializer):
    """Serializer for Academic Calendar model"""
    semester_name = serializers.CharField(source='semester.__str__', read_only=True)
    days_until = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicCalendar
        fields = [
            'id', 'title', 'event_type', 'date', 'end_date', 'description',
            'is_holiday', 'semester', 'semester_name', 'days_until'
        ]
    
    def get_days_until(self, obj):
        """Calculate days until event"""
        from django.utils import timezone
        today = timezone.now().date()
        delta = obj.date - today
        return delta.days if delta.days >= 0 else None


# Detailed serializers for specific use cases

class EnrollmentDetailSerializer(EnrollmentSerializer):
    """Detailed enrollment serializer with related data"""
    grades = GradeSerializer(many=True, read_only=True)
    attendance_records = AttendanceSerializer(many=True, read_only=True)
    schedule = ScheduleSerializer(source='course.schedules', many=True, read_only=True)
    
    class Meta(EnrollmentSerializer.Meta):
        fields = EnrollmentSerializer.Meta.fields + ['grades', 'attendance_records', 'schedule']


class StudentGradeReportSerializer(serializers.ModelSerializer):
    """Serializer for student grade reports"""
    enrollments = serializers.SerializerMethodField()
    semester_gpa = serializers.SerializerMethodField()
    cumulative_gpa = serializers.ReadOnlyField(source='gpa')
    
    class Meta:
        model = Semester
        fields = [
            'id', 'name', 'academic_year', 'start_date', 'end_date',
            'enrollments', 'semester_gpa', 'cumulative_gpa'
        ]
    
    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
    
    def get_enrollments(self, obj):
        if not self.student:
            return []
        
        enrollments = Enrollment.objects.filter(
            student=self.student,
            semester=obj
        ).select_related('course')
        
        return EnrollmentSerializer(enrollments, many=True).data
    
    def get_semester_gpa(self, obj):
        if not self.student:
            return None
        
        enrollments = Enrollment.objects.filter(
            student=self.student,
            semester=obj,
            final_grade__isnull=False
        )
        
        if not enrollments.exists():
            return None
        
        total_points = 0
        total_credits = 0
        
        for enrollment in enrollments:
            grade_scale = GradeScale.objects.filter(
                min_percentage__lte=enrollment.final_grade,
                max_percentage__gte=enrollment.final_grade
            ).first()
            
            if grade_scale:
                total_points += grade_scale.gpa_points * enrollment.course.credits
                total_credits += enrollment.course.credits
        
        return round(total_points / total_credits, 2) if total_credits > 0 else None


class TeacherScheduleSerializer(serializers.ModelSerializer):
    """Serializer for teacher's class schedule"""
    schedules = ScheduleSerializer(source='schedules_teaching', many=True, read_only=True)
    total_students = serializers.SerializerMethodField()
    courses_teaching = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email',
            'schedules', 'total_students', 'courses_teaching'
        ]
    
    def get_total_students(self, obj):
        """Get total number of students across all classes"""
        from django.db.models import Sum
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            return 0
        
        schedules = obj.schedules_teaching.filter(semester=current_semester)
        courses = [schedule.course for schedule in schedules]
        
        return Enrollment.objects.filter(
            course__in=courses,
            semester=current_semester,
            status='ENROLLED'
        ).count()
    
    def get_courses_teaching(self, obj):
        """Get list of courses being taught"""
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            return []
        
        schedules = obj.schedules_teaching.filter(semester=current_semester)
        courses = list(set([schedule.course for schedule in schedules]))
        
        return CourseSerializer(courses, many=True).data