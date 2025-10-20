# نظام الحضور والغياب باستخدام QR Code
# QR Code Attendance System

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from students.models import Student
from courses.models import Course
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import os

class AttendanceSession(models.Model):
    """جلسة الحضور"""
    
    SESSION_STATUS = [
        ('active', 'نشطة'),
        ('ended', 'منتهية'),
        ('cancelled', 'ملغية'),
    ]
    
    # معلومات الجلسة
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="المقرر")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                 related_name='attendance_sessions',
                                 verbose_name="المدرس")
    
    session_name = models.CharField(max_length=200, verbose_name="اسم الجلسة")
    session_date = models.DateField(verbose_name="تاريخ الجلسة")
    start_time = models.TimeField(verbose_name="وقت البدء")
    end_time = models.TimeField(verbose_name="وقت الانتهاء")
    
    # QR Code للجلسة
    session_code = models.UUIDField(default=uuid.uuid4, unique=True, 
                                  verbose_name="رمز الجلسة")
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True,
                                    verbose_name="صورة QR Code")
    
    # إعدادات الحضور
    location_required = models.BooleanField(default=False, verbose_name="مطلوب الموقع")
    location_latitude = models.FloatField(null=True, blank=True, verbose_name="خط العرض")
    location_longitude = models.FloatField(null=True, blank=True, verbose_name="خط الطول")
    location_radius = models.IntegerField(default=100, verbose_name="نطاق الموقع (متر)")
    
    # صلاحية QR Code
    qr_valid_duration = models.IntegerField(default=15, 
                                          verbose_name="مدة صلاحية QR (دقيقة)")
    late_threshold = models.IntegerField(default=10, 
                                       verbose_name="حد التأخير (دقيقة)")
    
    # حالة الجلسة
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active',
                            verbose_name="حالة الجلسة")
    is_auto_ended = models.BooleanField(default=False, verbose_name="انتهت تلقائياً")
    
    # الإحصائيات
    total_enrolled = models.IntegerField(default=0, verbose_name="إجمالي المسجلين")
    total_attended = models.IntegerField(default=0, verbose_name="إجمالي الحاضرين")
    attendance_rate = models.FloatField(default=0.0, verbose_name="نسبة الحضور")
    
    # التوقيتات
    created_at = models.DateTimeField(auto_now_add=True)
    qr_generated_at = models.DateTimeField(null=True, blank=True, 
                                         verbose_name="وقت إنشاء QR")
    session_started_at = models.DateTimeField(null=True, blank=True,
                                            verbose_name="وقت بدء الجلسة")
    session_ended_at = models.DateTimeField(null=True, blank=True,
                                          verbose_name="وقت انتهاء الجلسة")
    
    class Meta:
        verbose_name = "جلسة حضور"
        verbose_name_plural = "جلسات الحضور"
        ordering = ['-created_at']
    
    def generate_qr_code(self):
        """إنشاء QR Code للجلسة"""
        # بيانات QR Code
        qr_data = {
            'session_id': str(self.session_code),
            'course_id': self.course.id,
            'session_name': self.session_name,
            'timestamp': timezone.now().isoformat(),
        }
        
        # إنشاء QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        # إنشاء الصورة
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # حفظ الصورة
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        
        filename = f'qr_session_{self.session_code}.png'
        self.qr_code_image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )
        
        self.qr_generated_at = timezone.now()
        self.save()
        
        return self.qr_code_image.url
    
    def is_qr_valid(self):
        """فحص صلاحية QR Code"""
        if not self.qr_generated_at:
            return False
        
        now = timezone.now()
        valid_until = self.qr_generated_at + timezone.timedelta(
            minutes=self.qr_valid_duration
        )
        
        return now <= valid_until and self.status == 'active'
    
    def calculate_attendance_rate(self):
        """حساب نسبة الحضور"""
        if self.total_enrolled > 0:
            self.attendance_rate = (self.total_attended / self.total_enrolled) * 100
        else:
            self.attendance_rate = 0.0
        self.save()
        return self.attendance_rate
    
    def __str__(self):
        return f"{self.session_name} - {self.course.name}"

class AttendanceRecord(models.Model):
    """سجل الحضور"""
    
    ATTENDANCE_STATUS = [
        ('present', 'حاضر'),
        ('late', 'متأخر'),
        ('absent', 'غائب'),
        ('excused', 'معذور'),
    ]
    
    ATTENDANCE_METHOD = [
        ('qr_code', 'QR Code'),
        ('manual', 'يدوي'),
        ('biometric', 'بيومترية'),
        ('card', 'بطاقة'),
    ]
    
    # معلومات الحضور
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE,
                              related_name='attendance_records',
                              verbose_name="الجلسة")
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                              verbose_name="الطالب")
    
    # حالة الحضور
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS,
                            verbose_name="حالة الحضور")
    attendance_method = models.CharField(max_length=20, choices=ATTENDANCE_METHOD,
                                       default='qr_code', verbose_name="طريقة الحضور")
    
    # وقت الحضور
    check_in_time = models.DateTimeField(null=True, blank=True, 
                                       verbose_name="وقت الحضور")
    minutes_late = models.IntegerField(default=0, verbose_name="دقائق التأخير")
    
    # معلومات إضافية
    ip_address = models.GenericIPAddressField(null=True, blank=True,
                                            verbose_name="عنوان IP")
    device_info = models.TextField(blank=True, verbose_name="معلومات الجهاز")
    location_latitude = models.FloatField(null=True, blank=True, 
                                        verbose_name="خط العرض")
    location_longitude = models.FloatField(null=True, blank=True, 
                                         verbose_name="خط الطول")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name="تم التحقق بواسطة")
    
    # معلومات النظام
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "سجل حضور"
        verbose_name_plural = "سجلات الحضور"
        unique_together = ['session', 'student']
        ordering = ['-created_at']
    
    def calculate_lateness(self):
        """حساب دقائق التأخير"""
        if self.check_in_time and self.session.start_time:
            session_start = timezone.datetime.combine(
                self.session.session_date, 
                self.session.start_time
            )
            session_start = timezone.make_aware(session_start)
            
            if self.check_in_time > session_start:
                late_duration = self.check_in_time - session_start
                self.minutes_late = int(late_duration.total_seconds() / 60)
                
                # تحديد حالة الحضور حسب التأخير
                if self.minutes_late > self.session.late_threshold:
                    self.status = 'late'
                else:
                    self.status = 'present'
            else:
                self.minutes_late = 0
                self.status = 'present'
        
        self.save()
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.session.session_name}"

class AttendanceStatistics(models.Model):
    """إحصائيات الحضور"""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                              verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                             verbose_name="المقرر")
    
    # إحصائيات الحضور
    total_sessions = models.IntegerField(default=0, verbose_name="إجمالي الجلسات")
    attended_sessions = models.IntegerField(default=0, verbose_name="الجلسات المحضورة")
    late_sessions = models.IntegerField(default=0, verbose_name="الجلسات المتأخرة")
    absent_sessions = models.IntegerField(default=0, verbose_name="الجلسات الغائبة")
    excused_sessions = models.IntegerField(default=0, verbose_name="الجلسات المعذورة")
    
    # النسب المئوية
    attendance_percentage = models.FloatField(default=0.0, verbose_name="نسبة الحضور")
    lateness_percentage = models.FloatField(default=0.0, verbose_name="نسبة التأخير")
    
    # متوسط التأخير
    average_lateness = models.FloatField(default=0.0, verbose_name="متوسط التأخير (دقيقة)")
    
    # اتجاه الحضور
    attendance_trend = models.CharField(max_length=20, choices=[
        ('improving', 'يتحسن'),
        ('declining', 'يتراجع'),
        ('stable', 'مستقر'),
    ], default='stable', verbose_name="اتجاه الحضور")
    
    # آخر تحديث
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "إحصائية حضور"
        verbose_name_plural = "إحصائيات الحضور"
        unique_together = ['student', 'course']
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        # جلب جميع سجلات الحضور للطالب في هذا المقرر
        records = AttendanceRecord.objects.filter(
            student=self.student,
            session__course=self.course
        )
        
        self.total_sessions = records.count()
        if self.total_sessions > 0:
            self.attended_sessions = records.filter(status='present').count()
            self.late_sessions = records.filter(status='late').count()
            self.absent_sessions = records.filter(status='absent').count()
            self.excused_sessions = records.filter(status='excused').count()
            
            # حساب النسب
            present_and_late = self.attended_sessions + self.late_sessions
            self.attendance_percentage = (present_and_late / self.total_sessions) * 100
            self.lateness_percentage = (self.late_sessions / self.total_sessions) * 100
            
            # حساب متوسط التأخير
            late_records = records.filter(status='late', minutes_late__gt=0)
            if late_records.exists():
                total_late_minutes = sum(r.minutes_late for r in late_records)
                self.average_lateness = total_late_minutes / late_records.count()
            
            # تحديد الاتجاه (بناءً على آخر 5 جلسات مقابل الـ 5 قبلها)
            recent_records = records.order_by('-session__session_date')[:5]
            previous_records = records.order_by('-session__session_date')[5:10]
            
            if recent_records.exists() and previous_records.exists():
                recent_rate = recent_records.filter(
                    status__in=['present', 'late']
                ).count() / recent_records.count()
                previous_rate = previous_records.filter(
                    status__in=['present', 'late']
                ).count() / previous_records.count()
                
                if recent_rate > previous_rate + 0.1:
                    self.attendance_trend = 'improving'
                elif recent_rate < previous_rate - 0.1:
                    self.attendance_trend = 'declining'
                else:
                    self.attendance_trend = 'stable'
        
        self.save()

class QRCodeTemplate(models.Model):
    """قوالب QR Code"""
    
    name = models.CharField(max_length=200, verbose_name="اسم القالب")
    description = models.TextField(verbose_name="وصف القالب")
    
    # إعدادات التصميم
    background_color = models.CharField(max_length=7, default='#FFFFFF', 
                                      verbose_name="لون الخلفية")
    foreground_color = models.CharField(max_length=7, default='#000000', 
                                      verbose_name="لون المقدمة")
    logo_image = models.ImageField(upload_to='qr_logos/', blank=True, null=True,
                                 verbose_name="صورة الشعار")
    
    # إعدادات QR Code
    error_correction = models.CharField(max_length=1, choices=[
        ('L', 'منخفض (~7%)'),
        ('M', 'متوسط (~15%)'),
        ('Q', 'ربع عالي (~25%)'),
        ('H', 'عالي (~30%)'),
    ], default='M', verbose_name="تصحيح الأخطاء")
    
    box_size = models.IntegerField(default=10, verbose_name="حجم المربع")
    border_size = models.IntegerField(default=4, verbose_name="حجم الإطار")
    
    # الاستخدام
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "قالب QR Code"
        verbose_name_plural = "قوالب QR Code"
    
    def save(self, *args, **kwargs):
        # التأكد من وجود قالب افتراضي واحد فقط
        if self.is_default:
            QRCodeTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class AttendanceNotification(models.Model):
    """إشعارات الحضور"""
    
    NOTIFICATION_TYPES = [
        ('session_started', 'بدء الجلسة'),
        ('session_ending', 'انتهاء الجلسة قريباً'),
        ('attendance_marked', 'تم تسجيل الحضور'),
        ('attendance_warning', 'تحذير حضور'),
        ('attendance_report', 'تقرير حضور'),
    ]
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES,
                                       verbose_name="نوع الإشعار")
    
    # المرسل إليه
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                verbose_name="المستقبل")
    
    # محتوى الإشعار
    title = models.CharField(max_length=200, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    
    # البيانات المرتبطة
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE,
                              null=True, blank=True, verbose_name="الجلسة")
    attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE,
                                        null=True, blank=True, verbose_name="سجل الحضور")
    
    # حالة الإشعار
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    is_sent = models.BooleanField(default=False, verbose_name="مرسل")
    
    # طرق الإرسال
    send_email = models.BooleanField(default=True, verbose_name="إرسال بريد")
    send_sms = models.BooleanField(default=False, verbose_name="إرسال SMS")
    send_push = models.BooleanField(default=True, verbose_name="إشعار فوري")
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإرسال")
    
    class Meta:
        verbose_name = "إشعار حضور"
        verbose_name_plural = "إشعارات الحضور"
        ordering = ['-created_at']