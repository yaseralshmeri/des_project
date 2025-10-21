from rest_framework import serializers
from .models import (
    University, College, Department, Major, Course, 
    CourseOffering, Assignment, AcademicYear, Semester,
    CourseInstructor, MajorCourse
)


class UniversitySerializer(serializers.ModelSerializer):
    """Serializer for University model"""
    
    class Meta:
        model = University
        fields = [
            'id', 'name_ar', 'name_en', 'code', 'founded_year', 
            'university_type', 'address', 'phone', 'email', 'website',
            'academic_calendar_type', 'grading_system', 'logo', 
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CollegeSerializer(serializers.ModelSerializer):
    """Serializer for College model"""
    university_name = serializers.CharField(source='university.name_ar', read_only=True)
    dean_name = serializers.SerializerMethodField()
    
    class Meta:
        model = College
        fields = [
            'id', 'university', 'university_name', 'name_ar', 'name_en', 
            'code', 'dean', 'dean_name', 'vice_dean_academic', 
            'vice_dean_graduate', 'established_year', 'building', 
            'floor', 'phone', 'email', 'website', 'total_departments',
            'total_students', 'total_faculty', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_departments', 
                           'total_students', 'total_faculty']
    
    def get_dean_name(self, obj):
        return obj.dean.get_full_name() if obj.dean else None


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    college_name = serializers.CharField(source='college.name_ar', read_only=True)
    head_name = serializers.SerializerMethodField()
    vice_head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'college', 'college_name', 'name_ar', 'name_en', 
            'code', 'head', 'head_name', 'vice_head', 'vice_head_name',
            'established_year', 'location', 'phone', 'email', 'website',
            'objectives', 'total_students', 'total_faculty', 'total_majors',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_students', 
                           'total_faculty', 'total_majors']
    
    def get_head_name(self, obj):
        return obj.head.get_full_name() if obj.head else None
    
    def get_vice_head_name(self, obj):
        return obj.vice_head.get_full_name() if obj.vice_head else None


class MajorSerializer(serializers.ModelSerializer):
    """Serializer for Major model"""
    department_name = serializers.CharField(source='department.name_ar', read_only=True)
    
    class Meta:
        model = Major
        fields = [
            'id', 'department', 'department_name', 'name_ar', 'name_en',
            'code', 'degree_type', 'duration_years', 'total_credit_hours',
            'min_gpa_requirement', 'max_students_per_year', 'description',
            'career_prospects', 'admission_requirements', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    department_name = serializers.CharField(source='department.name_ar', read_only=True)
    coordinator_name = serializers.SerializerMethodField()
    prerequisites_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name_ar', 'name_en', 'department', 'department_name',
            'course_type', 'credit_hours', 'theory_hours', 'practical_hours',
            'academic_level', 'difficulty_level', 'delivery_method',
            'description', 'objectives', 'learning_outcomes', 'course_outline',
            'prerequisites_list', 'min_gpa_required', 'assessment_methods',
            'has_final_exam', 'has_midterm_exam', 'textbook', 'references',
            'online_resources', 'max_enrollment', 'min_enrollment',
            'allows_waitlist', 'coordinator', 'coordinator_name',
            'is_active', 'is_offered_online', 'requires_lab', 'requires_field_work',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'prerequisites_list']
    
    def get_coordinator_name(self, obj):
        return obj.coordinator.get_full_name() if obj.coordinator else None
    
    def get_prerequisites_list(self, obj):
        return [{'code': p.code, 'name': p.name_ar} for p in obj.prerequisites.all()]


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializer for AcademicYear model"""
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'year', 'start_date', 'end_date', 'is_current', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SemesterSerializer(serializers.ModelSerializer):
    """Serializer for Semester model"""
    academic_year_display = serializers.CharField(source='academic_year.year', read_only=True)
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Semester
        fields = [
            'id', 'academic_year', 'academic_year_display', 'semester_type',
            'display_name', 'start_date', 'end_date', 'registration_start_date',
            'registration_end_date', 'add_drop_deadline', 'withdrawal_deadline',
            'midterm_start_date', 'midterm_end_date', 'final_exam_start_date',
            'final_exam_end_date', 'is_current', 'is_active', 'registration_open',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'display_name']


class CourseOfferingSerializer(serializers.ModelSerializer):
    """Serializer for CourseOffering model"""
    course_name = serializers.CharField(source='course.name_ar', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    semester_display = serializers.CharField(source='semester.display_name', read_only=True)
    
    class Meta:
        model = CourseOffering
        fields = [
            'id', 'course', 'course_name', 'course_code', 'semester', 
            'semester_display', 'section_number', 'section_name',
            'instructor', 'instructor_name', 'schedule_days', 'start_time',
            'end_time', 'classroom', 'building', 'max_enrollment',
            'current_enrollment', 'waitlist_capacity', 'current_waitlist',
            'status', 'is_active', 'registration_open', 'special_notes',
            'prerequisites_enforced', 'is_full', 'available_spots',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_full', 
                           'available_spots', 'current_enrollment', 'current_waitlist']
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    course_name = serializers.CharField(source='course_offering.course.name_ar', read_only=True)
    course_code = serializers.CharField(source='course_offering.course.code', read_only=True)
    section_number = serializers.CharField(source='course_offering.section_number', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course_offering', 'course_name', 'course_code', 'section_number',
            'title', 'description', 'assignment_type', 'max_score', 
            'weight_percentage', 'published_date', 'due_date', 
            'late_submission_allowed', 'late_penalty_per_day', 'status',
            'is_group_assignment', 'max_group_size', 'instructions_file',
            'submission_format', 'rubric', 'estimated_time_hours',
            'is_overdue', 'days_until_due', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_overdue', 
                           'days_until_due', 'is_published']


class CourseInstructorSerializer(serializers.ModelSerializer):
    """Serializer for CourseInstructor model"""
    instructor_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='course_offering.course.name_ar', read_only=True)
    course_code = serializers.CharField(source='course_offering.course.code', read_only=True)
    
    class Meta:
        model = CourseInstructor
        fields = [
            'id', 'course_offering', 'course_name', 'course_code',
            'instructor', 'instructor_name', 'role', 'can_grade',
            'can_manage_assignments', 'can_manage_attendance', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None


class MajorCourseSerializer(serializers.ModelSerializer):
    """Serializer for MajorCourse model"""
    major_name = serializers.CharField(source='major.name_ar', read_only=True)
    course_name = serializers.CharField(source='course.name_ar', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = MajorCourse
        fields = [
            'id', 'major', 'major_name', 'course', 'course_name', 'course_code',
            'is_required', 'semester_offered', 'year_offered', 'sequence_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']