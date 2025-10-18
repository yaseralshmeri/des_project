"""
Advanced Enrollment Management Views
Handles course registration, prerequisites checking, and enrollment management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import datetime

from students.models import Student
from courses.models import Course
from .models import (
    Semester, Enrollment, Prerequisite, AcademicYear, 
    Schedule, GradeScale
)
from .serializers import EnrollmentSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_course(request):
    """
    Enroll student in a course with prerequisite checking
    """
    if not request.user.is_student:
        return Response(
            {'error': 'Only students can enroll in courses'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    course_id = request.data.get('course_id')
    semester_id = request.data.get('semester_id')
    
    if not course_id or not semester_id:
        return Response(
            {'error': 'course_id and semester_id are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        course = get_object_or_404(Course, id=course_id)
        semester = get_object_or_404(Semester, id=semester_id)
        student = request.user.student_profile
        
        # Check if registration period is open
        if not semester.is_current:
            return Response(
                {'error': 'Registration is not open for this semester'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_date = timezone.now().date()
        if not (semester.registration_start <= current_date <= semester.registration_end):
            return Response(
                {'error': 'Registration period has ended or not yet started'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=student, course=course, semester=semester).exists():
            return Response(
                {'error': 'Already enrolled in this course for this semester'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check prerequisites
        prerequisites_met, missing_prereqs = check_prerequisites(student, course)
        if not prerequisites_met:
            return Response({
                'error': 'Prerequisites not met',
                'missing_prerequisites': [
                    {
                        'course_code': prereq.code,
                        'course_name': prereq.name,
                        'min_grade': missing_prereqs[prereq.id]
                    } for prereq in Course.objects.filter(id__in=missing_prereqs.keys())
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check course capacity
        current_enrollment = Enrollment.objects.filter(
            course=course, 
            semester=semester,
            status='ENROLLED'
        ).count()
        
        if current_enrollment >= course.max_capacity:
            return Response(
                {'error': 'Course is full'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check schedule conflicts
        conflicts = check_schedule_conflicts(student, course, semester)
        if conflicts:
            return Response({
                'error': 'Schedule conflict detected',
                'conflicting_courses': [
                    {
                        'course_code': conflict.course.code,
                        'course_name': conflict.course.name,
                        'time': f"{conflict.day_of_week} {conflict.start_time}-{conflict.end_time}"
                    } for conflict in conflicts
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create enrollment
        with transaction.atomic():
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                semester=semester,
                status='ENROLLED'
            )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response({
            'message': 'Successfully enrolled in course',
            'enrollment': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Enrollment failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def drop_course(request):
    """
    Drop a course (withdraw from enrollment)
    """
    if not request.user.is_student:
        return Response(
            {'error': 'Only students can drop courses'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    enrollment_id = request.data.get('enrollment_id')
    if not enrollment_id:
        return Response(
            {'error': 'enrollment_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        student = request.user.student_profile
        enrollment = get_object_or_404(
            Enrollment, 
            id=enrollment_id, 
            student=student,
            status='ENROLLED'
        )
        
        # Check if drop period is still open
        semester = enrollment.semester
        current_date = timezone.now().date()
        
        # Allow dropping within first 2 weeks of semester
        drop_deadline = semester.start_date + timezone.timedelta(days=14)
        if current_date > drop_deadline:
            return Response(
                {'error': 'Drop period has ended'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update enrollment status
        enrollment.status = 'DROPPED'
        enrollment.save()
        
        return Response({
            'message': 'Successfully dropped from course',
            'enrollment_id': enrollment.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Drop failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def check_prerequisites(student, course):
    """
    Check if student has met all prerequisites for a course
    Returns: (bool, dict) - (prerequisites_met, missing_prerequisites)
    """
    prerequisites = Prerequisite.objects.filter(course=course)
    missing_prereqs = {}
    
    for prereq in prerequisites:
        # Check if student has completed prerequisite course with minimum grade
        completed = Enrollment.objects.filter(
            student=student,
            course=prereq.prerequisite_course,
            status='COMPLETED',
            final_grade__gte=prereq.min_grade
        ).exists()
        
        if not completed:
            missing_prereqs[prereq.prerequisite_course.id] = prereq.min_grade
    
    return len(missing_prereqs) == 0, missing_prereqs


def check_schedule_conflicts(student, course, semester):
    """
    Check for schedule conflicts with student's existing enrollments
    """
    # Get student's current schedules for the semester
    current_enrollments = Enrollment.objects.filter(
        student=student,
        semester=semester,
        status='ENROLLED'
    )
    
    current_schedules = Schedule.objects.filter(
        course__in=[e.course for e in current_enrollments],
        semester=semester
    )
    
    # Get schedules for the new course
    new_schedules = Schedule.objects.filter(
        course=course,
        semester=semester
    )
    
    conflicts = []
    for new_schedule in new_schedules:
        for current_schedule in current_schedules:
            if (new_schedule.day_of_week == current_schedule.day_of_week and
                time_overlap(new_schedule.start_time, new_schedule.end_time,
                           current_schedule.start_time, current_schedule.end_time)):
                conflicts.append(current_schedule)
    
    return conflicts


def time_overlap(start1, end1, start2, end2):
    """
    Check if two time periods overlap
    """
    return not (end1 <= start2 or end2 <= start1)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_courses(request):
    """
    Get list of courses available for enrollment for current student
    """
    if not request.user.is_student:
        return Response(
            {'error': 'Only students can view available courses'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student = request.user.student_profile
        current_semester = Semester.objects.filter(is_current=True).first()
        
        if not current_semester:
            return Response(
                {'error': 'No active semester found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all active courses
        all_courses = Course.objects.filter(is_active=True)
        
        # Filter out courses already enrolled in
        enrolled_courses = Enrollment.objects.filter(
            student=student,
            semester=current_semester,
            status__in=['ENROLLED', 'COMPLETED']
        ).values_list('course_id', flat=True)
        
        available_courses = all_courses.exclude(id__in=enrolled_courses)
        
        # Add prerequisite check and capacity info
        course_data = []
        for course in available_courses:
            prerequisites_met, missing_prereqs = check_prerequisites(student, course)
            
            current_enrollment = Enrollment.objects.filter(
                course=course, 
                semester=current_semester,
                status='ENROLLED'
            ).count()
            
            course_info = {
                'id': course.id,
                'code': course.code,
                'name': course.name,
                'description': course.description,
                'credits': course.credits,
                'max_capacity': course.max_capacity,
                'current_enrollment': current_enrollment,
                'spots_available': course.max_capacity - current_enrollment,
                'prerequisites_met': prerequisites_met
            }
            
            if not prerequisites_met:
                course_info['missing_prerequisites'] = [
                    Course.objects.get(id=prereq_id).code 
                    for prereq_id in missing_prereqs.keys()
                ]
            
            course_data.append(course_info)
        
        return Response({
            'semester': {
                'id': current_semester.id,
                'name': str(current_semester),
                'registration_start': current_semester.registration_start,
                'registration_end': current_semester.registration_end
            },
            'available_courses': course_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get available courses: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_schedule(request):
    """
    Get current semester schedule for student
    """
    if not request.user.is_student:
        return Response(
            {'error': 'Only students can view their schedule'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student = request.user.student_profile
        current_semester = Semester.objects.filter(is_current=True).first()
        
        if not current_semester:
            return Response(
                {'error': 'No active semester found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollments = Enrollment.objects.filter(
            student=student,
            semester=current_semester,
            status='ENROLLED'
        )
        
        schedules = Schedule.objects.filter(
            course__in=[e.course for e in enrollments],
            semester=current_semester
        ).order_by('day_of_week', 'start_time')
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'course_code': schedule.course.code,
                'course_name': schedule.course.name,
                'day_of_week': schedule.day_of_week,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'room': schedule.room,
                'building': schedule.building,
                'instructor': schedule.instructor.get_full_name() if schedule.instructor else 'TBA'
            })
        
        return Response({
            'semester': str(current_semester),
            'schedule': schedule_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get schedule: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )