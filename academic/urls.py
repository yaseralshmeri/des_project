"""
Academic App URLs
API endpoints for academic management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import enrollment_views

router = DefaultRouter()
router.register(r'academic-years', views.AcademicYearViewSet, basename='academicyear')
router.register(r'semesters', views.SemesterViewSet, basename='semester')
router.register(r'enrollments', views.EnrollmentViewSet, basename='enrollment')
router.register(r'grades', views.GradeViewSet, basename='grade')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')
router.register(r'programs', views.AcademicProgramViewSet, basename='academicprogram')
router.register(r'calendar', views.AcademicCalendarViewSet, basename='academiccalendar')

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom endpoints
    path('current-semester/', views.current_semester, name='current-semester'),
    path('student-grades/<int:student_id>/', views.student_grades, name='student-grades'),
    path('teacher-classes/<int:teacher_id>/', views.teacher_classes, name='teacher-classes'),
    path('grade-reports/', views.grade_reports, name='grade-reports'),
    
    # Advanced Enrollment endpoints
    path('enroll/', enrollment_views.enroll_in_course, name='enroll-course'),
    path('drop/', enrollment_views.drop_course, name='drop-course'),
    path('available-courses/', enrollment_views.get_available_courses, name='available-courses'),
    path('student-schedule/', enrollment_views.get_student_schedule, name='student-schedule'),
]