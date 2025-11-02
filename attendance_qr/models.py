# نظام الحضور والغياب المتطور مع QR Code
# Advanced Attendance System with QR Code Technology

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import json
import qrcode
import secrets
from io import BytesIO
from django.core.files.base import ContentFile
import hashlib

User = get_user_model()

class AttendanceSession(models.Model):
    """جلسة الحضور والغياب"""
    
    SESSION_TYPES = [
        ('LECTURE', 'محاضرة'),
        ('LAB', 'معمل'),
        ('TUTORIAL', 'تطبيق'),
        ('SEMINAR', 'ندوة'),
        ('EXAM', 'امتحان'),
        ('EVENT', 'فعالية'),
        ('OTHER', 'أخرى'),
    ]
    
    SESSION_STATUS = [
        ('SCHEDULED', 'مُجدولة'),
        ('ACTIVE', 'نشطة'),
        ('COMPLETED', 'مكتملة'),
        ('CANCELLED', 'ملغية'),
        ('POSTPONED', 'مؤجلة'),
    ]
    
    QR_CODE_TYPES = [
        ('STATIC', 'ثابت'),
        ('DYNAMIC', 'ديناميكي'),
        ('TIME_BASED', 'مؤقت'),
        ('LOCATION_BASED', 'مكاني'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الجلسة الأساسية
    session_name = models.CharField(max_length=200, verbose_name="اسم الجلسة")
    session_type = models.CharField(max_length=15, choices=SESSION_TYPES,
                                  default='LECTURE', verbose_name="نوع الجلسة")
    
    # المقرر والمدرس
    course_offering = models.ForeignKey('courses.CourseOffering', on_delete=models.CASCADE,
                                      related_name='attendance_sessions',
                                      verbose_name="عرض المقرر")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='taught_attendance_sessions',
                                 verbose_name="المدرس")
    
    # التوقيت والمكان
    scheduled_start_time = models.DateTimeField(verbose_name="وقت البداية المُجدول")
    scheduled_end_time = models.DateTimeField(verbose_name="وقت النهاية المُجدول")
    actual_start_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت البداية الفعلي")
    actual_end_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت النهاية الفعلي")
    
    classroom = models.ForeignKey('courses.Classroom', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name="القاعة الدراسية")
    location_coordinates = models.CharField(max_length=100, blank=True,
                                          verbose_name="إحداثيات الموقع")
    
    # إعدادات الحضور
    attendance_window_minutes = models.IntegerField(default=15,
                                                  validators=[MinValueValidator(1), MaxValueValidator(60)],
                                                  verbose_name="نافزة الحضور (دقائق)")
    late_threshold_minutes = models.IntegerField(default=10,
                                               validators=[MinValueValidator(0), MaxValueValidator(30)],
                                               verbose_name="حد التأخير (دقائق)")
    
    # إعدادات QR Code
    qr_code_type = models.CharField(max_length=15, choices=QR_CODE_TYPES,
                                  default='DYNAMIC', verbose_name="نوع رمز QR")
    qr_code_refresh_minutes = models.IntegerField(default=5,
                                                validators=[MinValueValidator(1), MaxValueValidator(30)],
                                                verbose_name="تحديث رمز QR (دقائق)")
    qr_code_range_meters = models.IntegerField(default=50,
                                             validators=[MinValueValidator(10), MaxValueValidator(500)],
                                             verbose_name="نطاق رمز QR (متر)")
    
    # الحالة
    status = models.CharField(max_length=15, choices=SESSION_STATUS, default='SCHEDULED',
                            verbose_name="حالة الجلسة")
    
    # الإحصائيات
    total_students = models.IntegerField(default=0, verbose_name="إجمالي الطلاب")
    present_count = models.IntegerField(default=0, verbose_name="عدد الحاضرين")
    late_count = models.IntegerField(default=0, verbose_name="عدد المتأخرين")
    absent_count = models.IntegerField(default=0, verbose_name="عدد الغائبين")
    
    # ملاحظات ووصف
    description = models.TextField(blank=True, verbose_name="وصف الجلسة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "جلسة حضور وغياب"
        verbose_name_plural = "جلسات الحضور والغياب"
        ordering = ['-scheduled_start_time']
        indexes = [
            models.Index(fields=['course_offering', 'status']),
            models.Index(fields=['instructor']),
            models.Index(fields=['scheduled_start_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.session_name} - {self.course_offering.course.name_ar}"
    
    @property
    def duration_minutes(self):
        """مدة الجلسة بالدقائق"""
        if self.actual_start_time and self.actual_end_time:
            return (self.actual_end_time - self.actual_start_time).total_seconds() / 60
        return (self.scheduled_end_time - self.scheduled_start_time).total_seconds() / 60
    
    @property
    def attendance_rate(self):
        """معدل الحضور"""
        if self.total_students > 0:
            return (self.present_count / self.total_students) * 100
        return 0
    
    @property
    def is_active(self):
        """هل الجلسة نشطة"""
        return self.status == 'ACTIVE'
    
    @property
    def can_take_attendance(self):
        """هل يمكن أخذ الحضور"""
        now = timezone.now()
        window_start = self.scheduled_start_time - timezone.timedelta(minutes=self.attendance_window_minutes)
        window_end = self.scheduled_end_time + timezone.timedelta(minutes=self.attendance_window_minutes)
        return window_start <= now <= window_end and self.status == 'ACTIVE'
    
    def start_session(self):
        """بدء الجلسة"""
        self.status = 'ACTIVE'
        self.actual_start_time = timezone.now()
        self.save(update_fields=['status', 'actual_start_time'])
    
    def end_session(self):
        """إنهاء الجلسة"""
        self.status = 'COMPLETED'
        self.actual_end_time = timezone.now()
        self.save(update_fields=['status', 'actual_end_time'])
        self.update_statistics()
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        records = self.attendance_records.all()
        self.total_students = records.count()
        self.present_count = records.filter(status='PRESENT').count()
        self.late_count = records.filter(status='LATE').count()
        self.absent_count = records.filter(status='ABSENT').count()
        self.save(update_fields=['total_students', 'present_count', 'late_count', 'absent_count'])


class QRCode(models.Model):
    """رموز QR للحضور"""
    
    QR_STATUS = [
        ('ACTIVE', 'نشط'),
        ('EXPIRED', 'منتهي'),
        ('USED', 'مُستخدم'),
        ('DISABLED', 'معطل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الجلسة المرتبطة
    attendance_session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE,
                                         related_name='qr_codes', verbose_name="جلسة الحضور")
    
    # معلومات الرمز
    qr_code_id = models.CharField(max_length=100, unique=True, verbose_name="معرف رمز QR")
    qr_data = models.TextField(verbose_name="بيانات رمز QR")
    secret_key = models.CharField(max_length=255, verbose_name="المفتاح السري")
    
    # التوقيت
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    expires_at = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    
    # الحالة والاستخدام
    status = models.CharField(max_length=15, choices=QR_STATUS, default='ACTIVE',
                            verbose_name="حالة الرمز")
    usage_count = models.IntegerField(default=0, verbose_name="عدد مرات الاستخدام")
    max_usage = models.IntegerField(default=1, verbose_name="الحد الأقصى للاستخدام")
    
    # معلومات الموقع
    valid_location_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True,
                                                verbose_name="خط العرض الصالح")
    valid_location_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True,
                                                 verbose_name="خط الطول الصالح")
    location_radius_meters = models.IntegerField(default=50, verbose_name="نطاق الموقع (متر)")
    
    # ملف الصورة
    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True,
                               verbose_name="صورة رمز QR")
    
    class Meta:
        verbose_name = "رمز QR"
        verbose_name_plural = "رموز QR"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['attendance_session', 'status']),
            models.Index(fields=['qr_code_id']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"QR-{self.qr_code_id}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code_id:
            self.qr_code_id = self.generate_qr_id()
        if not self.secret_key:
            self.secret_key = self.generate_secret_key()
        if not self.qr_data:
            self.qr_data = self.generate_qr_data()
        
        super().save(*args, **kwargs)
        
        # إنشاء صورة QR Code
        if not self.qr_image:
            self.create_qr_image()
    
    def generate_qr_id(self):
        """توليد معرف رمز QR فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_part = secrets.token_hex(4)
        return f"{timestamp}-{random_part}"
    
    def generate_secret_key(self):
        """توليد مفتاح سري"""
        return secrets.token_urlsafe(32)
    
    def generate_qr_data(self):
        """توليد بيانات رمز QR"""
        data = {
            'session_id': str(self.attendance_session.id),
            'qr_id': self.qr_code_id,
            'secret': self.secret_key,
            'timestamp': timezone.now().isoformat(),
            'expires': self.expires_at.isoformat() if self.expires_at else None,
        }
        return json.dumps(data)
    
    def create_qr_image(self):
        """إنشاء صورة رمز QR"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_data)
        qr.make(fit=True)
        
        # إنشاء الصورة
        img = qr.make_image(fill_color="black", back_color="white")
        
        # حفظ في الذاكرة
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # حفظ في قاعدة البيانات
        filename = f"qr_{self.qr_code_id}.png"
        self.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        self.save(update_fields=['qr_image'])
    
    @property
    def is_valid(self):
        """هل الرمز صالح"""
        now = timezone.now()
        return (self.status == 'ACTIVE' and 
                now <= self.expires_at and 
                self.usage_count < self.max_usage)
    
    @property
    def is_expired(self):
        """هل الرمز منتهي"""
        return timezone.now() > self.expires_at
    
    def verify_location(self, user_latitude, user_longitude):
        """التحقق من صحة الموقع"""
        if not self.valid_location_latitude or not self.valid_location_longitude:
            return True  # لا يوجد قيد مكاني
        
        # حساب المسافة بين الموقعين
        from math import radians, cos, sin, asin, sqrt
        
        # تحويل إلى راديان
        lat1, lon1 = radians(float(self.valid_location_latitude)), radians(float(self.valid_location_longitude))
        lat2, lon2 = radians(user_latitude), radians(user_longitude)
        
        # حساب المسافة باستخدام Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        distance_km = 2 * asin(sqrt(a)) * 6371  # نصف قطر الأرض بالكيلومتر
        distance_meters = distance_km * 1000
        
        return distance_meters <= self.location_radius_meters
    
    def use_code(self):
        """استخدام الرمز"""
        self.usage_count += 1
        if self.usage_count >= self.max_usage:
            self.status = 'USED'
        self.save(update_fields=['usage_count', 'status'])


class AttendanceRecord(models.Model):
    """سجل الحضور والغياب"""
    
    ATTENDANCE_STATUS = [
        ('PRESENT', 'حاضر'),
        ('ABSENT', 'غائب'),
        ('LATE', 'متأخر'),
        ('EXCUSED', 'معذور'),
        ('EARLY_DEPARTURE', 'انصراف مبكر'),
    ]
    
    ATTENDANCE_METHOD = [
        ('QR_CODE', 'رمز QR'),
        ('MANUAL', 'يدوي'),
        ('FACIAL_RECOGNITION', 'التعرف على الوجه'),
        ('FINGERPRINT', 'بصمة الإصبع'),
        ('RFID', 'RFID'),
        ('PROXIMITY', 'القرب'),
        ('OTHER', 'أخرى'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الجلسة والطالب
    attendance_session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE,
                                         related_name='attendance_records',
                                         verbose_name="جلسة الحضور")
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='attendance_records', verbose_name="الطالب")
    
    # حالة الحضور
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS,
                            verbose_name="حالة الحضور")
    attendance_method = models.CharField(max_length=20, choices=ATTENDANCE_METHOD,
                                       default='QR_CODE', verbose_name="طريقة الحضور")
    
    # التوقيت
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت التسجيل")
    arrival_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الوصول")
    departure_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الانصراف")
    
    # تفاصيل المسح
    qr_code = models.ForeignKey(QRCode, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='attendance_records', verbose_name="رمز QR")
    scan_location_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True,
                                               verbose_name="خط عرض المسح")
    scan_location_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True,
                                                verbose_name="خط طول المسح")
    device_info = models.JSONField(default=dict, verbose_name="معلومات الجهاز")
    
    # المعالجة والتحقق
    is_verified = models.BooleanField(default=False, verbose_name="مُتحقق منه")
    verification_method = models.CharField(max_length=100, blank=True, verbose_name="طريقة التحقق")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='verified_attendance_records',
                                  verbose_name="تم التحقق بواسطة")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التحقق")
    
    # الدرجات والنقاط
    attendance_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                          verbose_name="نقاط الحضور")
    bonus_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                     verbose_name="نقاط إضافية")
    penalty_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                       verbose_name="نقاط الخصم")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    excuse_reason = models.TextField(blank=True, verbose_name="سبب العذر")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "سجل حضور وغياب"
        verbose_name_plural = "سجلات الحضور والغياب"
        ordering = ['-recorded_at']
        unique_together = ['attendance_session', 'student']
        indexes = [
            models.Index(fields=['attendance_session', 'status']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['recorded_at']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.student.display_name} - {self.attendance_session.session_name} - {self.get_status_display()}"
    
    @property
    def minutes_late(self):
        """دقائق التأخير"""
        if self.arrival_time and self.attendance_session.scheduled_start_time:
            if self.arrival_time > self.attendance_session.scheduled_start_time:
                return (self.arrival_time - self.attendance_session.scheduled_start_time).total_seconds() / 60
        return 0
    
    @property
    def total_points(self):
        """إجمالي النقاط"""
        return self.attendance_points + self.bonus_points - self.penalty_points
    
    def calculate_points(self):
        """حساب نقاط الحضور"""
        if self.status == 'PRESENT':
            self.attendance_points = 10.0
        elif self.status == 'LATE':
            # خصم نقاط حسب دقائق التأخير
            late_minutes = self.minutes_late
            if late_minutes <= 5:
                self.attendance_points = 8.0
            elif late_minutes <= 10:
                self.attendance_points = 6.0
            elif late_minutes <= 15:
                self.attendance_points = 4.0
            else:
                self.attendance_points = 2.0
        elif self.status == 'EXCUSED':
            self.attendance_points = 5.0
        else:  # ABSENT
            self.attendance_points = 0.0
        
        self.save(update_fields=['attendance_points'])


class AttendanceException(models.Model):
    """استثناءات الحضور والغياب"""
    
    EXCEPTION_TYPES = [
        ('MEDICAL', 'طبي'),
        ('EMERGENCY', 'طارئ'),
        ('OFFICIAL', 'رسمي'),
        ('TECHNICAL', 'تقني'),
        ('OTHER', 'أخرى'),
    ]
    
    EXCEPTION_STATUS = [
        ('PENDING', 'في الانتظار'),
        ('APPROVED', 'موافق عليه'),
        ('REJECTED', 'مرفوض'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الطالب والجلسة
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='attendance_exceptions', verbose_name="الطالب")
    attendance_session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE,
                                         related_name='attendance_exceptions',
                                         verbose_name="جلسة الحضور")
    
    # نوع الاستثناء
    exception_type = models.CharField(max_length=15, choices=EXCEPTION_TYPES,
                                    verbose_name="نوع الاستثناء")
    reason = models.TextField(verbose_name="سبب الاستثناء")
    
    # المستندات المرفقة
    supporting_documents = models.JSONField(default=list, verbose_name="المستندات الداعمة")
    
    # التوقيت
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقديم")
    effective_date = models.DateField(verbose_name="تاريخ السريان")
    
    # المراجعة والموافقة
    status = models.CharField(max_length=15, choices=EXCEPTION_STATUS, default='PENDING',
                            verbose_name="حالة الطلب")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='reviewed_attendance_exceptions',
                                  verbose_name="راجعه")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    reviewer_comments = models.TextField(blank=True, verbose_name="تعليقات المراجع")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "استثناء حضور وغياب"
        verbose_name_plural = "استثناءات الحضور والغياب"
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['attendance_session']),
            models.Index(fields=['exception_type']),
        ]
    
    def __str__(self):
        return f"{self.student.display_name} - {self.get_exception_type_display()}"


class AttendanceReport(models.Model):
    """تقارير الحضور والغياب"""
    
    REPORT_TYPES = [
        ('STUDENT_SUMMARY', 'ملخص طالب'),
        ('COURSE_SUMMARY', 'ملخص مقرر'),
        ('INSTRUCTOR_SUMMARY', 'ملخص مدرس'),
        ('DAILY_REPORT', 'تقرير يومي'),
        ('WEEKLY_REPORT', 'تقرير أسبوعي'),
        ('MONTHLY_REPORT', 'تقرير شهري'),
        ('SEMESTER_REPORT', 'تقرير فصلي'),
        ('CUSTOM_REPORT', 'تقرير مخصص'),
    ]
    
    REPORT_STATUS = [
        ('GENERATING', 'قيد الإنتاج'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'فاشل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات التقرير
    report_name = models.CharField(max_length=200, verbose_name="اسم التقرير")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES,
                                 verbose_name="نوع التقرير")
    
    # الفترة والنطاق
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    
    # المرشحات
    course_offerings = models.ManyToManyField('courses.CourseOffering', blank=True,
                                            verbose_name="عروض المقررات")
    students = models.ManyToManyField(User, blank=True, related_name='attendance_reports',
                                    verbose_name="الطلاب")
    instructors = models.ManyToManyField(User, blank=True, related_name='instructor_attendance_reports',
                                       verbose_name="المدرسون")
    
    # البيانات الإحصائية
    total_sessions = models.IntegerField(default=0, verbose_name="إجمالي الجلسات")
    total_students = models.IntegerField(default=0, verbose_name="إجمالي الطلاب")
    average_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                                 verbose_name="متوسط معدل الحضور")
    
    # بيانات التقرير
    report_data = models.JSONField(default=dict, verbose_name="بيانات التقرير")
    
    # الحالة والملف
    status = models.CharField(max_length=15, choices=REPORT_STATUS, default='GENERATING',
                            verbose_name="حالة التقرير")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الملف")
    
    # معلومات الإنتاج
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='generated_attendance_reports',
                                   verbose_name="أُنتج بواسطة")
    generated_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإنتاج")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تقرير حضور وغياب"
        verbose_name_plural = "تقارير الحضور والغياب"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['generated_by']),
        ]
    
    def __str__(self):
        return f"{self.report_name} - {self.get_report_type_display()}"


class AttendanceSettings(models.Model):
    """إعدادات نظام الحضور والغياب"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # إعدادات عامة
    default_attendance_window_minutes = models.IntegerField(default=15,
                                                          verbose_name="نافذة الحضور الافتراضية (دقائق)")
    default_late_threshold_minutes = models.IntegerField(default=10,
                                                       verbose_name="حد التأخير الافتراضي (دقائق)")
    
    # إعدادات QR Code
    qr_code_refresh_minutes = models.IntegerField(default=5,
                                                verbose_name="تحديث رمز QR (دقائق)")
    qr_code_valid_range_meters = models.IntegerField(default=50,
                                                   verbose_name="نطاق صلاحية رمز QR (متر)")
    enable_location_verification = models.BooleanField(default=True,
                                                     verbose_name="تفعيل التحقق من الموقع")
    
    # إعدادات النقاط
    present_points = models.DecimalField(max_digits=5, decimal_places=2, default=10.0,
                                       verbose_name="نقاط الحضور")
    late_points = models.DecimalField(max_digits=5, decimal_places=2, default=5.0,
                                    verbose_name="نقاط التأخير")
    excused_points = models.DecimalField(max_digits=5, decimal_places=2, default=5.0,
                                        verbose_name="نقاط العذر")
    absent_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                      verbose_name="نقاط الغياب")
    
    # إعدادات التنبيهات
    enable_attendance_reminders = models.BooleanField(default=True,
                                                    verbose_name="تفعيل تذكيرات الحضور")
    reminder_minutes_before = models.IntegerField(default=30,
                                                verbose_name="التذكير قبل (دقائق)")
    
    # إعدادات التقارير
    auto_generate_reports = models.BooleanField(default=True,
                                              verbose_name="إنتاج تقارير تلقائي")
    report_generation_frequency = models.CharField(max_length=20, default='WEEKLY',
                                                 choices=[
                                                     ('DAILY', 'يومي'),
                                                     ('WEEKLY', 'أسبوعي'),
                                                     ('MONTHLY', 'شهري'),
                                                 ], verbose_name="تكرار إنتاج التقارير")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='updated_attendance_settings',
                                 verbose_name="حُدث بواسطة")
    
    class Meta:
        verbose_name = "إعدادات الحضور والغياب"
        verbose_name_plural = "إعدادات الحضور والغياب"
    
    def __str__(self):
        return "إعدادات نظام الحضور والغياب"# QRScanLog Model - ملف مؤقت
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class QRScanLog(models.Model):
    """سجل مسح رموز QR"""
    
    SCAN_RESULTS = [
        ('SUCCESS', 'نجح'),
        ('FAILED', 'فشل'),
        ('EXPIRED', 'منتهي الصلاحية'),
        ('INVALID', 'غير صحيح'),
        ('DUPLICATE', 'مكرر'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المسح
    qr_code = models.ForeignKey('QRCode', on_delete=models.CASCADE,
                               related_name='scan_logs', verbose_name="رمز QR")
    scanned_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='qr_scans', verbose_name="مُسح بواسطة")
    
    # نتيجة المسح
    scan_result = models.CharField(max_length=15, choices=SCAN_RESULTS,
                                 verbose_name="نتيجة المسح")
    
    # معلومات إضافية
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="متصفح المستخدم")
    location_data = models.JSONField(default=dict, blank=True, verbose_name="بيانات الموقع")
    
    # التوقيت
    scanned_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت المسح")
    
    class Meta:
        verbose_name = "سجل مسح QR"
        verbose_name_plural = "سجلات مسح QR"
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['qr_code', '-scanned_at']),
            models.Index(fields=['scanned_by', '-scanned_at']),
            models.Index(fields=['scan_result']),
        ]
    
    def __str__(self):
        return f"{self.qr_code.code_id} - {self.scanned_by.username} - {self.get_scan_result_display()}"