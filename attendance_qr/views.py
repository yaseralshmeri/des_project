# نظام الحضور بالرمز المربع
# QR Code Attendance System Views

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AttendanceSession, AttendanceRecord
from courses.models import CourseOffering
import json


@login_required
def create_attendance_session(request):
    """إنشاء جلسة حضور جديدة"""
    if request.method == 'POST':
        try:
            course_offering_id = request.POST.get('course_offering_id')
            duration_minutes = int(request.POST.get('duration_minutes', 15))
            
            course_offering = get_object_or_404(CourseOffering, id=course_offering_id)
            
            # التحقق من صلاحية المدرس
            if request.user != course_offering.instructor and request.user not in course_offering.co_instructors.all():
                messages.error(request, 'ليس لديك صلاحية لإنشاء جلسة حضور لهذا المقرر')
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # إنشاء جلسة جديدة
            session = AttendanceSession.objects.create(
                course_offering=course_offering,
                instructor=request.user,
                duration_minutes=duration_minutes,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.id),
                'qr_code_url': session.qr_code.url if session.qr_code else None,
                'expires_at': session.expires_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """تسجيل الحضور باستخدام الرمز المربع"""
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({'error': 'معرف الجلسة مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
        
        session = get_object_or_404(AttendanceSession, id=session_id)
        
        # التحقق من أن الجلسة نشطة ولم تنته
        if not session.is_active or session.is_expired:
            return Response({'error': 'الجلسة غير نشطة أو منتهية'}, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من أن الطالب مسجل في المقرر
        # يمكن إضافة هذا التحقق لاحقاً
        
        # تسجيل الحضور
        attendance_record, created = AttendanceRecord.objects.get_or_create(
            session=session,
            student=request.user,
            defaults={
                'status': 'PRESENT',
                'marked_at': timezone.now()
            }
        )
        
        if not created:
            return Response({'message': 'تم تسجيل حضورك بالفعل'}, status=status.HTTP_200_OK)
        
        return Response({
            'success': True,
            'message': 'تم تسجيل الحضور بنجاح',
            'marked_at': attendance_record.marked_at.isoformat()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def attendance_session_detail(request, session_id):
    """تفاصيل جلسة الحضور"""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # التحقق من الصلاحية
    if (request.user != session.instructor and 
        request.user not in session.course_offering.co_instructors.all() and
        not request.user.is_staff):
        messages.error(request, 'ليس لديك صلاحية لعرض هذه الجلسة')
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    attendance_records = session.attendance_records.all().order_by('marked_at')
    
    context = {
        'session': session,
        'attendance_records': attendance_records,
        'total_present': attendance_records.filter(status='PRESENT').count(),
        'total_absent': attendance_records.filter(status='ABSENT').count(),
    }
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'session_id': str(session.id),
            'course_name': session.course_offering.course.name_ar,
            'instructor': session.instructor.get_full_name(),
            'created_at': session.created_at.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'is_active': session.is_active,
            'total_present': context['total_present'],
            'total_absent': context['total_absent'],
            'attendance_records': [
                {
                    'student_name': record.student.get_full_name(),
                    'status': record.status,
                    'marked_at': record.marked_at.isoformat() if record.marked_at else None
                }
                for record in attendance_records
            ]
        })
    
    return render(request, 'attendance_qr/session_detail.html', context)


@login_required
def instructor_sessions(request):
    """جلسات الحضور للمدرس"""
    sessions = AttendanceSession.objects.filter(
        instructor=request.user
    ).order_by('-created_at')
    
    context = {
        'sessions': sessions
    }
    
    return render(request, 'attendance_qr/instructor_sessions.html', context)


@login_required 
def student_attendance(request):
    """سجل حضور الطالب"""
    attendance_records = AttendanceRecord.objects.filter(
        student=request.user
    ).order_by('-session__created_at')
    
    context = {
        'attendance_records': attendance_records
    }
    
    return render(request, 'attendance_qr/student_attendance.html', context)


@csrf_exempt
def qr_scan_page(request, session_id):
    """صفحة مسح الرمز المربع"""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    context = {
        'session': session
    }
    
    return render(request, 'attendance_qr/qr_scan.html', context)


@api_view(['GET'])
def session_status(request, session_id):
    """حالة جلسة الحضور"""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    return Response({
        'session_id': str(session.id),
        'is_active': session.is_active,
        'is_expired': session.is_expired,
        'expires_at': session.expires_at.isoformat(),
        'duration_minutes': session.duration_minutes,
        'course_name': session.course_offering.course.name_ar
    })


@login_required
def deactivate_session(request, session_id):
    """إنهاء جلسة الحضور"""
    if request.method == 'POST':
        session = get_object_or_404(AttendanceSession, id=session_id)
        
        # التحقق من الصلاحية
        if request.user != session.instructor:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        session.is_active = False
        session.save()
        
        return JsonResponse({'success': True, 'message': 'تم إنهاء الجلسة'})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)