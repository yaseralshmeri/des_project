# نظام إدارة المقررات الذكي والمتطور
# Enhanced Intelligent Course Management System

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from students.models import User, Student
from .models import Department
import json

class Semester(models.Model):
    """الفصول الدراسية"""
    
    SEMESTER_TYPES = [
        ('FALL', 'الخريف'),
        ('SPRING', 'الربيع'),
        ('SUMMER', 'الصيف'),
    ]
    
    STATUS_CHOICES = [
        ('UPCOMING', 'قادم'),
        ('CURRENT', 'حالي'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم الفصل")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز الفصل")
    semester_type = models.CharField(max_length=10, choices=SEMESTER_TYPES, verbose_name="نوع الفصل")
    year = models.IntegerField(validators=[MinValueValidator(2020)], verbose_name="السنة")
    
    # تواريخ مهمة
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    
    # فترات التسجيل
    registration_start = models.DateTimeField(verbose_name="بداية التسجيل")
    registration_end = models.DateTimeField(verbose_name="نهاية التسجيل")
    add_drop_deadline = models.DateField(verbose_name="آخر موعد للإضافة والحذف")
    withdrawal_deadline = models.DateField(verbose_name="آخر موعد للانسحاب")
    
    # فترات الامتحانات
    midterm_start = models.DateField(null=True, blank=True, verbose_name="بداية امتحانات المنتصف")
    midterm_end = models.DateField(null=True, blank=True, verbose_name="نهاية امتحانات المنتصف")
    final_start = models.DateField(null=True, blank=True, verbose_name="بداية الامتحانات النهائية")
    final_end = models.DateField(null=True, blank=True, verbose_name="نهاية الامتحانات النهائية")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPCOMING',
                            verbose_name="حالة الفصل")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "فصل دراسي"
        verbose_name_plural = "الفصول الدراسية"
        ordering = ['-year', '-semester_type']
        unique_together = ['semester_type', 'year']
    
    def __str__(self):
        return f"{self.get_semester_type_display()} {self.year}"
    
    @property
    def is_current(self):
        """فحص إذا كان الفصل الحالي"""
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date
    
    @property
    def is_registration_open(self):
        """فحص إذا كان التسجيل مفتوح"""
        now = timezone.now()
        return self.registration_start <= now <= self.registration_end

class Course(models.Model):
    """المقررات الدراسية"""
    
    COURSE_TYPES = [
        ('CORE', 'مقرر أساسي'),
        ('ELECTIVE', 'مقرر اختياري'),
        ('PREREQUISITE', 'مقرر متطلب'),
        ('GENERAL', 'مقرر عام'),
        ('SPECIALIZATION', 'مقرر تخصصي'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'مبتدئ'),
        ('INTERMEDIATE', 'متوسط'),
        ('ADVANCED', 'متقدم'),
        ('EXPERT', 'خبير'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('ARCHIVED', 'مؤرشف'),
        ('UNDER_REVIEW', 'قيد المراجعة'),
    ]
    
    # معلومات أساسية
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز المقرر")
    title = models.CharField(max_length=200, verbose_name="اسم المقرر")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(verbose_name="وصف المقرر")
    
    # التصنيف الأكاديمي
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                 related_name='courses', verbose_name="القسم")
    course_type = models.CharField(max_length=20, choices=COURSE_TYPES, 
                                 default='CORE', verbose_name="نوع المقرر")
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS,
                                      default='INTERMEDIATE', verbose_name="مستوى الصعوبة")
    
    # الساعات والوحدات
    credit_hours = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                     verbose_name="الساعات المعتمدة")
    theory_hours = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                     verbose_name="ساعات نظرية")
    practical_hours = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                        verbose_name="ساعات عملية")
    
    # المتطلبات
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True,
                                         related_name='required_for', verbose_name="المتطلبات السابقة")
    corequisites = models.ManyToManyField('self', symmetrical=True, blank=True,
                                        related_name='corequisite_courses', verbose_name="المتطلبات المتزامنة")
    
    # إعدادات المقرر
    max_capacity = models.IntegerField(default=30, validators=[MinValueValidator(1)],
                                     verbose_name="الحد الأقصى للطلاب")
    min_capacity = models.IntegerField(default=5, validators=[MinValueValidator(1)],
                                     verbose_name="الحد الأدنى للطلاب")
    
    # معلومات إضافية
    syllabus = models.TextField(blank=True, verbose_name="المنهج التفصيلي")
    learning_outcomes = models.JSONField(default=list, blank=True, verbose_name="مخرجات التعلم")
    assessment_methods = models.JSONField(default=list, blank=True, verbose_name="طرق التقييم")
    required_textbooks = models.JSONField(default=list, blank=True, verbose_name="المراجع المطلوبة")
    recommended_readings = models.JSONField(default=list, blank=True, verbose_name="القراءات المقترحة")
    
    # معلومات تقنية
    has_lab = models.BooleanField(default=False, verbose_name="يحتوي على مختبر")
    requires_computer = models.BooleanField(default=False, verbose_name="يتطلب حاسوب")
    online_component = models.BooleanField(default=False, verbose_name="يحتوي على جزء إلكتروني")
    
    # الحالة والمراجعة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="حالة المقرر")
    
    # معلومات الإنشاء والتحديث
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_courses', verbose_name="أنشئ بواسطة")
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                       related_name='modified_courses', verbose_name="آخر تعديل بواسطة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "مقرر"
        verbose_name_plural = "المقررات"
        ordering = ['code']
        indexes = [
            models.Index(fields=['code', 'status']),
            models.Index(fields=['department', 'course_type']),
            models.Index(fields=['credit_hours']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    @property
    def total_hours(self):
        """إجمالي الساعات النظرية والعملية"""
        return self.theory_hours + self.practical_hours
    
    def can_enroll(self, student):
        """فحص إمكانية تسجيل الطالب في المقرر"""
        # فحص المتطلبات السابقة
        for prereq in self.prerequisites.all():
            if not student.completed_courses.filter(course=prereq, grade__gte='C').exists():
                return False, f"يتطلب إنجاز مقرر {prereq.code}"
        
        return True, "يمكن التسجيل"

class Building(models.Model):
    """المباني الجامعية"""
    
    name = models.CharField(max_length=100, verbose_name="اسم المبنى")
    code = models.CharField(max_length=10, unique=True, verbose_name="رمز المبنى")
    description = models.TextField(blank=True, verbose_name="وصف المبنى")
    
    # الموقع
    address = models.TextField(blank=True, verbose_name="العنوان")
    floors_count = models.IntegerField(default=1, validators=[MinValueValidator(1)],
                                     verbose_name="عدد الطوابق")
    
    # معلومات إضافية
    has_elevator = models.BooleanField(default=False, verbose_name="يحتوي على مصعد")
    has_parking = models.BooleanField(default=False, verbose_name="يحتوي على موقف")
    has_wifi = models.BooleanField(default=True, verbose_name="يحتوي على واي فاي")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Room(models.Model):
    """القاعات والغرف"""
    
    ROOM_TYPES = [
        ('CLASSROOM', 'قاعة دراسية'),
        ('LABORATORY', 'مختبر'),
        ('LECTURE_HALL', 'قاعة محاضرات'),
        ('SEMINAR_ROOM', 'قاعة ندوات'),
        ('COMPUTER_LAB', 'مختبر حاسوب'),
        ('LIBRARY', 'مكتبة'),
        ('OFFICE', 'مكتب'),
        ('CONFERENCE_ROOM', 'قاعة اجتماعات'),
        ('AUDITORIUM', 'قاعة كبرى'),
    ]
    
    building = models.ForeignKey(Building, on_delete=models.CASCADE, 
                               related_name='rooms', verbose_name="المبنى")
    number = models.CharField(max_length=20, verbose_name="رقم القاعة")
    name = models.CharField(max_length=100, blank=True, verbose_name="اسم القاعة")
    
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, 
                               default='CLASSROOM', verbose_name="نوع القاعة")
    floor = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="الطابق")
    
    # المعلومات التقنية
    capacity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="السعة")
    area = models.FloatField(null=True, blank=True, verbose_name="المساحة (متر مربع)")
    
    # التجهيزات
    has_projector = models.BooleanField(default=False, verbose_name="يحتوي على بروجكتر")
    has_microphone = models.BooleanField(default=False, verbose_name="يحتوي على ميكروفون")
    has_whiteboard = models.BooleanField(default=True, verbose_name="يحتوي على سبورة")
    has_smartboard = models.BooleanField(default=False, verbose_name="يحتوي على سبورة ذكية")
    has_computer = models.BooleanField(default=False, verbose_name="يحتوي على حاسوب")
    has_air_conditioning = models.BooleanField(default=False, verbose_name="يحتوي على تكييف")
    
    # حالة القاعة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_bookable = models.BooleanField(default=True, verbose_name="قابل للحجز")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "قاعة"
        verbose_name_plural = "القاعات"
        ordering = ['building', 'floor', 'number']
        unique_together = ['building', 'number']
        indexes = [
            models.Index(fields=['building', 'room_type']),
            models.Index(fields=['capacity', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.building.code}-{self.number}" + (f" ({self.name})" if self.name else "")

class TimeSlot(models.Model):
    """الفترات الزمنية للجدول الدراسي"""
    
    DAYS_OF_WEEK = [
        ('SATURDAY', 'السبت'),
        ('SUNDAY', 'الأحد'),
        ('MONDAY', 'الاثنين'),
        ('TUESDAY', 'الثلاثاء'),
        ('WEDNESDAY', 'الأربعاء'),
        ('THURSDAY', 'الخميس'),
        ('FRIDAY', 'الجمعة'),
    ]
    
    name = models.CharField(max_length=50, verbose_name="اسم الفترة")
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, verbose_name="يوم الأسبوع")
    start_time = models.TimeField(verbose_name="وقت البداية")
    end_time = models.TimeField(verbose_name="وقت النهاية")
    
    # ترتيب الفترة في اليوم
    order = models.IntegerField(default=1, verbose_name="الترتيب")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "فترة زمنية"
        verbose_name_plural = "الفترات الزمنية"
        ordering = ['day_of_week', 'start_time']
        unique_together = ['day_of_week', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"
    
    @property
    def duration_minutes(self):
        """مدة الفترة بالدقائق"""
        import datetime
        start = datetime.datetime.combine(datetime.date.today(), self.start_time)
        end = datetime.datetime.combine(datetime.date.today(), self.end_time)
        return int((end - start).total_seconds() / 60)

class CourseOffering(models.Model):
    """عرض المقرر في فصل دراسي معين"""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, 
                             related_name='offerings', verbose_name="المقرر")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                               related_name='course_offerings', verbose_name="الفصل الدراسي")
    
    # معلومات الشعبة
    section = models.CharField(max_length=10, default='A', verbose_name="الشعبة")
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 limit_choices_to={'role__in': ['TEACHER', 'ASSISTANT_TEACHER']},
                                 related_name='taught_offerings', verbose_name="المدرس")
    
    # إعدادات التسجيل
    max_enrollment = models.IntegerField(validators=[MinValueValidator(1)],
                                       verbose_name="الحد الأقصى للتسجيل")
    current_enrollment = models.IntegerField(default=0, verbose_name="العدد المسجل حالياً")
    
    # إعدادات إضافية
    is_online = models.BooleanField(default=False, verbose_name="مقرر إلكتروني")
    is_hybrid = models.BooleanField(default=False, verbose_name="مقرر مختلط")
    
    # حالة العرض
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_cancelled = models.BooleanField(default=False, verbose_name="ملغي")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "عرض مقرر"
        verbose_name_plural = "عروض المقررات"
        unique_together = ['course', 'semester', 'section']
        ordering = ['course__code', 'section']
        indexes = [
            models.Index(fields=['semester', 'is_active']),
            models.Index(fields=['instructor', 'semester']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.section} ({self.semester})"
    
    @property
    def available_spots(self):
        """عدد المقاعد المتاحة"""
        return max(0, self.max_enrollment - self.current_enrollment)
    
    @property
    def is_full(self):
        """فحص إذا كان العرض ممتلئ"""
        return self.current_enrollment >= self.max_enrollment
    
    @property
    def enrollment_percentage(self):
        """نسبة التسجيل"""
        if self.max_enrollment > 0:
            return (self.current_enrollment / self.max_enrollment) * 100
        return 0

class CourseSchedule(models.Model):
    """جدول المقرر"""
    
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE,
                               related_name='schedules', verbose_name="عرض المقرر")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE,
                                related_name='scheduled_courses', verbose_name="الفترة الزمنية")
    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                           related_name='scheduled_courses', verbose_name="القاعة")
    
    # معلومات إضافية
    is_lecture = models.BooleanField(default=True, verbose_name="محاضرة")
    is_lab = models.BooleanField(default=False, verbose_name="مختبر")
    is_tutorial = models.BooleanField(default=False, verbose_name="تطبيق")
    
    # فترة صالحية الجدول
    effective_date = models.DateField(default=timezone.now, verbose_name="تاريخ السريان")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "جدول مقرر"
        verbose_name_plural = "جداول المقررات"
        unique_together = ['time_slot', 'room', 'effective_date']
        ordering = ['time_slot__day_of_week', 'time_slot__start_time']
        indexes = [
            models.Index(fields=['offering', 'is_active']),
            models.Index(fields=['room', 'time_slot']),
        ]
    
    def __str__(self):
        return f"{self.offering} - {self.time_slot} - {self.room}"
    
    def clean(self):
        """تحقق من عدم تعارض الجداول"""
        from django.core.exceptions import ValidationError
        
        # فحص تعارض القاعة
        conflicting_schedules = CourseSchedule.objects.filter(
            time_slot=self.time_slot,
            room=self.room,
            is_active=True,
            effective_date__lte=self.effective_date
        ).exclude(pk=self.pk)
        
        if self.end_date:
            conflicting_schedules = conflicting_schedules.filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.effective_date)
            )
        
        if conflicting_schedules.exists():
            raise ValidationError("تعارض في استخدام القاعة في نفس الوقت")
        
        # فحص تعارض المدرس
        if self.offering.instructor:
            instructor_conflicts = CourseSchedule.objects.filter(
                time_slot=self.time_slot,
                offering__instructor=self.offering.instructor,
                is_active=True,
                effective_date__lte=self.effective_date
            ).exclude(pk=self.pk)
            
            if self.end_date:
                instructor_conflicts = instructor_conflicts.filter(
                    models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.effective_date)
                )
            
            if instructor_conflicts.exists():
                raise ValidationError("تعارض في جدول المدرس")

class Enrollment(models.Model):
    """تسجيل الطلاب في المقررات"""
    
    STATUS_CHOICES = [
        ('ENROLLED', 'مسجل'),
        ('WAITLISTED', 'في قائمة الانتظار'),
        ('DROPPED', 'منسحب'),
        ('WITHDRAWN', 'منسحب متأخر'),
        ('COMPLETED', 'مكتمل'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                              related_name='enrollments', verbose_name="الطالب")
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE,
                               related_name='enrollments', verbose_name="عرض المقرر")
    
    # معلومات التسجيل
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED',
                            verbose_name="حالة التسجيل")
    
    # الدرجات
    midterm_grade = models.FloatField(null=True, blank=True, 
                                    validators=[MinValueValidator(0), MaxValueValidator(100)],
                                    verbose_name="درجة المنتصف")
    final_grade = models.FloatField(null=True, blank=True,
                                  validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  verbose_name="الدرجة النهائية")
    assignment_grade = models.FloatField(null=True, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(100)],
                                       verbose_name="درجة المهام")
    participation_grade = models.FloatField(null=True, blank=True,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)],
                                          verbose_name="درجة المشاركة")
    
    # الدرجة الإجمالية والرمزية
    total_grade = models.FloatField(null=True, blank=True,
                                  validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  verbose_name="الدرجة الإجمالية")
    letter_grade = models.CharField(max_length=2, blank=True, verbose_name="الدرجة الرمزية")
    grade_points = models.FloatField(null=True, blank=True, verbose_name="نقاط الدرجة")
    
    # معلومات الحضور
    total_classes = models.IntegerField(default=0, verbose_name="إجمالي المحاضرات")
    attended_classes = models.IntegerField(default=0, verbose_name="المحاضرات المحضورة")
    
    # معلومات إضافية
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # التواريخ المهمة
    last_attendance_date = models.DateField(null=True, blank=True, verbose_name="آخر حضور")
    drop_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانسحاب")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "تسجيل مقرر"
        verbose_name_plural = "تسجيل المقررات"
        unique_together = ['student', 'offering']
        ordering = ['-enrollment_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['offering', 'status']),
            models.Index(fields=['letter_grade']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.offering}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لحساب الدرجات"""
        # حساب الدرجة الإجمالية
        if all([self.midterm_grade is not None, self.final_grade is not None]):
            # توزيع الدرجات: منتصف 30%، نهائي 50%، مهام 15%، مشاركة 5%
            midterm_weight = 0.30
            final_weight = 0.50
            assignment_weight = 0.15
            participation_weight = 0.05
            
            total = (
                (self.midterm_grade or 0) * midterm_weight +
                (self.final_grade or 0) * final_weight +
                (self.assignment_grade or 0) * assignment_weight +
                (self.participation_grade or 0) * participation_weight
            )
            self.total_grade = round(total, 2)
            
            # حساب الدرجة الرمزية ونقاط الدرجة
            if self.total_grade >= 90:
                self.letter_grade = 'A+'
                self.grade_points = 4.0
            elif self.total_grade >= 85:
                self.letter_grade = 'A'
                self.grade_points = 3.7
            elif self.total_grade >= 80:
                self.letter_grade = 'B+'
                self.grade_points = 3.3
            elif self.total_grade >= 75:
                self.letter_grade = 'B'
                self.grade_points = 3.0
            elif self.total_grade >= 70:
                self.letter_grade = 'C+'
                self.grade_points = 2.7
            elif self.total_grade >= 65:
                self.letter_grade = 'C'
                self.grade_points = 2.3
            elif self.total_grade >= 60:
                self.letter_grade = 'D+'
                self.grade_points = 2.0
            elif self.total_grade >= 50:
                self.letter_grade = 'D'
                self.grade_points = 1.0
            else:
                self.letter_grade = 'F'
                self.grade_points = 0.0
        
        super().save(*args, **kwargs)
    
    @property
    def attendance_percentage(self):
        """نسبة الحضور"""
        if self.total_classes > 0:
            return (self.attended_classes / self.total_classes) * 100
        return 0
    
    @property
    def is_passing(self):
        """فحص النجاح في المقرر"""
        return self.letter_grade not in ['F', ''] and self.grade_points >= 1.0

class AttendanceRecord(models.Model):
    """سجل الحضور والغياب للطلاب"""
    
    STATUS_CHOICES = [
        ('PRESENT', 'حاضر'),
        ('ABSENT', 'غائب'),
        ('LATE', 'متأخر'),
        ('EXCUSED', 'غياب مبرر'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE,
                                 related_name='attendance_records', verbose_name="التسجيل")
    schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE,
                               related_name='attendance_records', verbose_name="الجدول")
    
    date = models.DateField(verbose_name="التاريخ")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
                            default='PRESENT', verbose_name="حالة الحضور")
    
    # وقت تسجيل الحضور
    check_in_time = models.TimeField(null=True, blank=True, verbose_name="وقت الحضور")
    check_out_time = models.TimeField(null=True, blank=True, verbose_name="وقت المغادرة")
    
    # معلومات إضافية
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='recorded_attendance', verbose_name="سجل بواسطة")
    
    # معلومات QR Code (للحضور الذكي)
    qr_code_used = models.CharField(max_length=100, blank=True, verbose_name="رمز QR المستخدم")
    location_verified = models.BooleanField(default=False, verbose_name="الموقع موثق")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "سجل حضور"
        verbose_name_plural = "سجلات الحضور"
        unique_together = ['enrollment', 'schedule', 'date']
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['enrollment', 'date']),
            models.Index(fields=['schedule', 'date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.date} - {self.get_status_display()}"