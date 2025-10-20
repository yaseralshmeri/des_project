"""
Celery Tasks for University Management System
مهام Celery لنظام إدارة الجامعة

This file contains background tasks for email notifications, report generation,
data backup, system maintenance, and other asynchronous operations.
"""

import os
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction
from django.core.cache import cache

import pandas as pd
from io import BytesIO
import json

logger = logging.getLogger(__name__)
User = get_user_model()


# =============================================================================
# EMAIL AND NOTIFICATION TASKS - مهام البريد الإلكتروني والإشعارات
# =============================================================================

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, recipient_email, subject, message, html_message=None, attachment_path=None):
    """
    Send email notification with retry mechanism
    إرسال إشعار بريد إلكتروني مع آلية إعادة المحاولة
    """
    try:
        if html_message:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            msg.attach_alternative(html_message, "text/html")
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                msg.attach_file(attachment_path)
            
            msg.send()
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False
            )
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return {"status": "success", "recipient": recipient_email}
        
    except Exception as exc:
        logger.error(f"Email sending failed: {exc}")
        if self.request.retries < self.max_retries:
            # Retry after exponential backoff
            countdown = 2 ** self.request.retries
            raise self.retry(exc=exc, countdown=countdown)
        else:
            return {"status": "failed", "error": str(exc)}


@shared_task
def send_bulk_notifications(user_ids, subject, message, notification_type="general"):
    """
    Send bulk notifications to multiple users
    إرسال إشعارات جماعية لعدة مستخدمين
    """
    try:
        users = User.objects.filter(id__in=user_ids)
        success_count = 0
        failed_count = 0
        
        for user in users:
            try:
                # Create in-app notification
                from notifications.models import Notification
                Notification.objects.create(
                    user=user,
                    title=subject,
                    message=message,
                    type=notification_type,
                    is_read=False
                )
                
                # Send email if user has email
                if user.email:
                    send_email_notification.delay(
                        recipient_email=user.email,
                        subject=subject,
                        message=message
                    )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send notification to user {user.id}: {e}")
                failed_count += 1
        
        logger.info(f"Bulk notification completed: {success_count} success, {failed_count} failed")
        return {
            "status": "completed",
            "success_count": success_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Bulk notification task failed: {e}")
        return {"status": "failed", "error": str(e)}


@shared_task
def send_academic_reminders():
    """
    Send academic reminders (registration deadlines, exam dates, etc.)
    إرسال تذكيرات أكاديمية (مواعيد التسجيل، مواعيد الامتحانات، إلخ)
    """
    try:
        from academic.models import Semester
        from students.models import Student
        
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            return {"status": "no_current_semester"}
        
        # Registration deadline reminder (3 days before)
        registration_deadline = current_semester.registration_end
        days_until_deadline = (registration_deadline - timezone.now().date()).days
        
        if days_until_deadline == 3:
            students = Student.objects.filter(is_active=True)
            subject = f"تذكير: انتهاء فترة التسجيل خلال 3 أيام"
            message = f"""
            عزيزي الطالب،
            
            نذكركم بأن فترة التسجيل للفصل الدراسي {current_semester.name} ستنتهي في تاريخ {registration_deadline}.
            
            يرجى إكمال عملية التسجيل في أقرب وقت ممكن.
            
            مع تحيات إدارة الجامعة
            """
            
            for student in students:
                if student.user.email:
                    send_email_notification.delay(
                        recipient_email=student.user.email,
                        subject=subject,
                        message=message
                    )
        
        return {"status": "completed", "days_until_deadline": days_until_deadline}
        
    except Exception as e:
        logger.error(f"Academic reminders task failed: {e}")
        return {"status": "failed", "error": str(e)}


# =============================================================================
# REPORT GENERATION TASKS - مهام إنتاج التقارير
# =============================================================================

@shared_task(bind=True)
def generate_academic_report(self, report_type, parameters=None):
    """
    Generate academic reports (student performance, course statistics, etc.)
    إنتاج التقارير الأكاديمية (أداء الطلاب، إحصائيات المقررات، إلخ)
    """
    try:
        from reports.models import Report
        from academic.models import Enrollment, Grade
        from students.models import Student
        from courses.models import Course
        
        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100})
        
        report_data = {}
        
        if report_type == "student_performance":
            # Generate student performance report
            students = Student.objects.filter(is_active=True)
            performance_data = []
            
            for i, student in enumerate(students):
                grades = Grade.objects.filter(enrollment__student=student)
                if grades.exists():
                    avg_grade = grades.aggregate(avg=models.Avg('points'))['avg']
                    performance_data.append({
                        'student_id': student.student_id,
                        'student_name': student.user.get_full_name(),
                        'gpa': round(avg_grade or 0, 2),
                        'total_courses': grades.count(),
                        'department': student.department.name if student.department else 'N/A'
                    })
                
                # Update progress
                progress = int((i + 1) / len(students) * 50)
                self.update_state(state='PROGRESS', meta={'current': progress, 'total': 100})
            
            report_data['students'] = performance_data
            
        elif report_type == "course_statistics":
            # Generate course statistics report
            courses = Course.objects.filter(is_active=True)
            course_stats = []
            
            for i, course in enumerate(courses):
                enrollments = Enrollment.objects.filter(course=course)
                grades = Grade.objects.filter(enrollment__course=course)
                
                course_stats.append({
                    'course_code': course.code,
                    'course_name': course.name,
                    'enrolled_students': enrollments.count(),
                    'completed_students': grades.count(),
                    'average_grade': round(grades.aggregate(avg=models.Avg('points'))['avg'] or 0, 2),
                    'pass_rate': round((grades.filter(points__gte=60).count() / grades.count() * 100) if grades.count() > 0 else 0, 2)
                })
                
                # Update progress
                progress = 50 + int((i + 1) / len(courses) * 50)
                self.update_state(state='PROGRESS', meta={'current': progress, 'total': 100})
            
            report_data['courses'] = course_stats
        
        # Save report to database
        report = Report.objects.create(
            title=f"{report_type.replace('_', ' ').title()} Report",
            type=report_type,
            data=report_data,
            generated_by=None,  # System generated
            file_format='json'
        )
        
        # Generate Excel file
        excel_path = generate_excel_report(report_data, report_type)
        
        self.update_state(state='SUCCESS', meta={
            'current': 100,
            'total': 100,
            'report_id': report.id,
            'excel_path': excel_path
        })
        
        return {
            "status": "completed",
            "report_id": report.id,
            "excel_path": excel_path,
            "data_count": len(report_data.get('students', []) + report_data.get('courses', []))
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {"status": "failed", "error": str(e)}


def generate_excel_report(data, report_type):
    """
    Generate Excel file from report data
    إنتاج ملف Excel من بيانات التقرير
    """
    try:
        # Create Excel file
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if 'students' in data:
                df_students = pd.DataFrame(data['students'])
                df_students.to_excel(writer, sheet_name='Students', index=False)
            
            if 'courses' in data:
                df_courses = pd.DataFrame(data['courses'])
                df_courses.to_excel(writer, sheet_name='Courses', index=False)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.xlsx"
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(output.getvalue())
        
        return filepath
        
    except Exception as e:
        logger.error(f"Excel generation failed: {e}")
        return None


# =============================================================================
# SYSTEM MAINTENANCE TASKS - مهام صيانة النظام
# =============================================================================

@shared_task
def cleanup_old_sessions():
    """
    Clean up expired sessions
    تنظيف الجلسات المنتهية الصلاحية
    """
    try:
        from django.core.management import call_command
        call_command('clearsessions')
        logger.info("Old sessions cleaned up successfully")
        return {"status": "completed", "message": "Old sessions cleaned up"}
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return {"status": "failed", "error": str(e)}


@shared_task
def backup_database():
    """
    Create database backup
    إنشاء نسخة احتياطية من قاعدة البيانات
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"db_backup_{timestamp}.json"
        backup_path = os.path.join(settings.BASE_DIR, 'backups', backup_filename)
        
        # Create backup directory
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Create backup
        with open(backup_path, 'w') as f:
            call_command('dumpdata', stdout=f, format='json', indent=2)
        
        # Compress backup
        import gzip
        with open(backup_path, 'rb') as f_in:
            with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove uncompressed file
        os.remove(backup_path)
        
        logger.info(f"Database backup created: {backup_path}.gz")
        return {
            "status": "completed",
            "backup_path": f"{backup_path}.gz",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return {"status": "failed", "error": str(e)}


@shared_task
def cleanup_old_logs():
    """
    Clean up old log files
    تنظيف ملفات السجل القديمة
    """
    try:
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(logs_dir):
            return {"status": "no_logs_directory"}
        
        cutoff_date = datetime.now() - timedelta(days=30)  # Keep logs for 30 days
        cleaned_files = 0
        
        for filename in os.listdir(logs_dir):
            filepath = os.path.join(logs_dir, filename)
            if os.path.isfile(filepath):
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_modified < cutoff_date:
                    os.remove(filepath)
                    cleaned_files += 1
        
        logger.info(f"Cleaned up {cleaned_files} old log files")
        return {"status": "completed", "cleaned_files": cleaned_files}
        
    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")
        return {"status": "failed", "error": str(e)}


@shared_task
def system_health_check():
    """
    Perform comprehensive system health check
    إجراء فحص شامل لصحة النظام
    """
    try:
        health_status = {
            "timestamp": timezone.now().isoformat(),
            "database": False,
            "cache": False,
            "disk_space": {},
            "memory_usage": {},
            "response_times": {}
        }
        
        # Database check
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status["database"] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["database"] = False
        
        # Cache check
        try:
            cache.set('health_check', 'ok', 30)
            health_status["cache"] = cache.get('health_check') == 'ok'
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            health_status["cache"] = False
        
        # Disk space check
        try:
            import shutil
            total, used, free = shutil.disk_usage(settings.BASE_DIR)
            health_status["disk_space"] = {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round((used / total) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
        
        # Memory usage check
        try:
            import psutil
            memory = psutil.virtual_memory()
            health_status["memory_usage"] = {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            }
        except ImportError:
            health_status["memory_usage"] = {"error": "psutil not installed"}
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
        
        # Store health status in cache
        cache.set('system_health_status', health_status, 300)  # 5 minutes
        
        # Send alert if critical issues found
        critical_issues = []
        if not health_status["database"]:
            critical_issues.append("Database connection failed")
        if not health_status["cache"]:
            critical_issues.append("Cache connection failed")
        if health_status["disk_space"].get("usage_percent", 0) > 90:
            critical_issues.append("Disk space critically low")
        
        if critical_issues:
            # Send alert to administrators
            send_system_alert.delay("Critical System Issues", critical_issues)
        
        return {
            "status": "completed",
            "health_status": health_status,
            "critical_issues": critical_issues
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {"status": "failed", "error": str(e)}


@shared_task
def send_system_alert(title, issues):
    """
    Send system alert to administrators
    إرسال تنبيه النظام للمديرين
    """
    try:
        admins = User.objects.filter(is_superuser=True)
        
        message = f"""
        تنبيه نظام مهم:
        
        {title}
        
        المشاكل المكتشفة:
        """
        
        for issue in issues:
            message += f"- {issue}\n"
        
        message += f"""
        
        يرجى التحقق من النظام في أقرب وقت ممكن.
        
        وقت التنبيه: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        for admin in admins:
            if admin.email:
                send_email_notification.delay(
                    recipient_email=admin.email,
                    subject=f"🚨 {title}",
                    message=message
                )
        
        return {"status": "completed", "notified_admins": admins.count()}
        
    except Exception as e:
        logger.error(f"System alert failed: {e}")
        return {"status": "failed", "error": str(e)}


# =============================================================================
# DATA PROCESSING TASKS - مهام معالجة البيانات
# =============================================================================

@shared_task
def process_student_grades(enrollment_ids):
    """
    Process and calculate student grades
    معالجة وحساب درجات الطلاب
    """
    try:
        from academic.models import Enrollment, Grade
        
        processed_count = 0
        
        for enrollment_id in enrollment_ids:
            try:
                enrollment = Enrollment.objects.get(id=enrollment_id)
                
                # Calculate GPA for this enrollment
                grades = Grade.objects.filter(enrollment=enrollment)
                if grades.exists():
                    total_points = sum(grade.points * grade.credit_hours for grade in grades)
                    total_credits = sum(grade.credit_hours for grade in grades)
                    
                    if total_credits > 0:
                        gpa = total_points / total_credits
                        enrollment.gpa = round(gpa, 2)
                        enrollment.save()
                
                processed_count += 1
                
            except Enrollment.DoesNotExist:
                logger.warning(f"Enrollment {enrollment_id} not found")
                continue
            except Exception as e:
                logger.error(f"Error processing enrollment {enrollment_id}: {e}")
                continue
        
        return {
            "status": "completed",
            "processed_count": processed_count,
            "total_requested": len(enrollment_ids)
        }
        
    except Exception as e:
        logger.error(f"Grade processing task failed: {e}")
        return {"status": "failed", "error": str(e)}


# =============================================================================
# SCHEDULED PERIODIC TASKS - المهام الدورية المجدولة
# =============================================================================

# These tasks should be configured in Django settings or Celery beat schedule

@shared_task
def daily_maintenance():
    """
    Daily maintenance tasks
    مهام الصيانة اليومية
    """
    logger.info("Starting daily maintenance tasks")
    
    results = {
        "session_cleanup": cleanup_old_sessions.delay(),
        "health_check": system_health_check.delay(),
        "academic_reminders": send_academic_reminders.delay()
    }
    
    return {"status": "scheduled", "tasks": list(results.keys())}


@shared_task
def weekly_maintenance():
    """
    Weekly maintenance tasks
    مهام الصيانة الأسبوعية
    """
    logger.info("Starting weekly maintenance tasks")
    
    results = {
        "database_backup": backup_database.delay(),
        "log_cleanup": cleanup_old_logs.delay(),
    }
    
    return {"status": "scheduled", "tasks": list(results.keys())}


# Task monitoring utilities
def get_task_status(task_id):
    """Get status of a specific task"""
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "info": result.info
    }