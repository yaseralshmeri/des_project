# نماذج الطلاب المطورة والشاملة
# Enhanced Student Models for University Management System

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from PIL import Image
import os

class User(AbstractUser):
    """نموذج المستخدم المخصص مع نظام الأدوار المتطور"""
    
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'مدير النظام الرئيسي'),
        ('ADMIN', 'مدير النظام'),
        ('DEAN', 'عميد الكلية'),
        ('HEAD_OF_DEPARTMENT', 'رئيس القسم'),
        ('TEACHER', 'أستاذ'),
        ('ASSISTANT_TEACHER', 'مساعد تدريس'),
        ('STUDENT', 'طالب'),
        ('ACCOUNTANT', 'محاسب'),
        ('HR_MANAGER', 'مدير الموارد البشرية'),
        ('REGISTRAR', 'مسجل أكاديمي'),
        ('LIBRARIAN', 'أمين المكتبة'),
        ('IT_SUPPORT', 'دعم تقني'),
        ('SECURITY_OFFICER', 'ضابط أمن'),
        ('GUEST', 'زائر'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('SUSPENDED', 'موقوف'),
        ('GRADUATED', 'متخرج'),
        ('TRANSFERRED', 'محول'),
    ]
    
    # معلومات أساسية
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT',
                          verbose_name="الدور الوظيفي")
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True,
                                 verbose_name="رقم الموظف")
    
    # معلومات شخصية
    arabic_first_name = models.CharField(max_length=50, blank=True, verbose_name="الاسم الأول بالعربية")
    arabic_last_name = models.CharField(max_length=50, blank=True, verbose_name="اسم العائلة بالعربية")
    phone = models.CharField(max_length=20, blank=True, null=True,
                           validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
                           verbose_name="رقم الهاتف")
    phone_secondary = models.CharField(max_length=20, blank=True, null=True,
                                     verbose_name="رقم هاتف ثانوي")
    
    # العنوان مفصل
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    city = models.CharField(max_length=100, blank=True, verbose_name="المدينة")
    state = models.CharField(max_length=100, blank=True, verbose_name="المحافظة/الولاية")
    country = models.CharField(max_length=100, default='العراق', verbose_name="البلد")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="الرمز البريدي")
    
    # معلومات شخصية إضافية
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="تاريخ الميلاد")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True,
                            verbose_name="الجنس")
    nationality = models.CharField(max_length=100, default='عراقي', verbose_name="الجنسية")
    religion = models.CharField(max_length=50, blank=True, verbose_name="الديانة")
    
    # الوثائق والمعرفات
    national_id = models.CharField(max_length=50, unique=True, null=True, blank=True,
                                 verbose_name="رقم البطاقة الوطنية")
    passport_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الجواز")
    
    # معلومات الاتصال الطارئ
    emergency_contact_name = models.CharField(max_length=100, blank=True,
                                            verbose_name="اسم جهة الاتصال الطارئ")
    emergency_contact_phone = models.CharField(max_length=20, blank=True,
                                             verbose_name="هاتف جهة الاتصال الطارئ")
    emergency_contact_relation = models.CharField(max_length=50, blank=True,
                                                verbose_name="صلة القرابة")
    
    # صورة الملف الشخصي
    profile_picture = models.ImageField(upload_to='profiles/%Y/%m/', blank=True, null=True,
                                      verbose_name="صورة الملف الشخصي")
    
    # حالة المستخدم
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="حالة المستخدم")
    
    # معلومات تقنية
    preferred_language = models.CharField(max_length=10, choices=[
        ('ar', 'العربية'),
        ('en', 'English'),
    ], default='ar', verbose_name="اللغة المفضلة")
    
    # إعدادات الخصوصية
    allow_email_notifications = models.BooleanField(default=True,
                                                  verbose_name="السماح بإشعارات البريد")
    allow_sms_notifications = models.BooleanField(default=True,
                                                verbose_name="السماح بإشعارات SMS")
    profile_visibility = models.CharField(max_length=20, choices=[
        ('PUBLIC', 'عام'),
        ('UNIVERSITY', 'داخل الجامعة فقط'),
        ('PRIVATE', 'خاص'),
    ], default='UNIVERSITY', verbose_name="مستوى رؤية الملف الشخصي")
    
    # معلومات آخر نشاط
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # التحقق والأمان
    email_verified = models.BooleanField(default=False, verbose_name="البريد موثق")
    phone_verified = models.BooleanField(default=False, verbose_name="الهاتف موثق")
    two_factor_enabled = models.BooleanField(default=False, verbose_name="التحقق الثنائي مفعل")
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['national_id']),
        ]
    
    def __str__(self):
        full_name = self.get_full_name() or self.username
        return f"{full_name} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص مع معالجة الصورة"""
        super().save(*args, **kwargs)
        
        # ضغط وتحسين الصورة الشخصية
        if self.profile_picture:
            img_path = self.profile_picture.path
            if os.path.exists(img_path):
                with Image.open(img_path) as img:
                    # تحويل إلى RGB إذا كان PNG
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # تصغير الصورة إذا كانت كبيرة
                    max_size = (400, 400)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # حفظ بجودة محسنة
                    img.save(img_path, 'JPEG', quality=85, optimize=True)
    
    @property
    def full_arabic_name(self):
        """الاسم الكامل بالعربية"""
        if self.arabic_first_name and self.arabic_last_name:
            return f"{self.arabic_first_name} {self.arabic_last_name}"
        return self.get_full_name()
    
    @property
    def age(self):
        """حساب العمر"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    # خصائص فحص الأدوار
    @property
    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN'
    
    @property
    def is_admin(self):
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    @property
    def is_dean(self):
        return self.role == 'DEAN'
    
    @property
    def is_head_of_department(self):
        return self.role == 'HEAD_OF_DEPARTMENT'
    
    @property
    def is_teacher(self):
        return self.role in ['TEACHER', 'ASSISTANT_TEACHER']
    
    @property
    def is_student(self):
        return self.role == 'STUDENT'
    
    @property
    def is_staff_member(self):
        return self.role in ['ACCOUNTANT', 'HR_MANAGER', 'REGISTRAR', 'LIBRARIAN', 'IT_SUPPORT']

class University(models.Model):
    """نموذج الجامعة"""
    
    name = models.CharField(max_length=200, verbose_name="اسم الجامعة")
    name_en = models.CharField(max_length=200, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=10, unique=True, verbose_name="رمز الجامعة")
    
    # معلومات الاتصال
    address = models.TextField(verbose_name="العنوان")
    city = models.CharField(max_length=100, verbose_name="المدينة")
    country = models.CharField(max_length=100, verbose_name="البلد")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="الرمز البريدي")
    
    phone = models.CharField(max_length=20, verbose_name="الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    website = models.URLField(blank=True, verbose_name="الموقع الإلكتروني")
    
    # الشعار والهوية البصرية
    logo = models.ImageField(upload_to='university/', blank=True, verbose_name="الشعار")
    favicon = models.ImageField(upload_to='university/', blank=True, verbose_name="أيقونة المتصفح")
    
    # معلومات إضافية
    established_year = models.IntegerField(validators=[MinValueValidator(1800)],
                                        verbose_name="سنة التأسيس")
    description = models.TextField(blank=True, verbose_name="نبذة عن الجامعة")
    vision = models.TextField(blank=True, verbose_name="الرؤية")
    mission = models.TextField(blank=True, verbose_name="الرسالة")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "جامعة"
        verbose_name_plural = "الجامعات"
    
    def __str__(self):
        return self.name

class College(models.Model):
    """نموذج الكلية"""
    
    university = models.ForeignKey(University, on_delete=models.CASCADE, 
                                 related_name='colleges', verbose_name="الجامعة")
    name = models.CharField(max_length=200, verbose_name="اسم الكلية")
    name_en = models.CharField(max_length=200, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=10, verbose_name="رمز الكلية")
    
    dean = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           limit_choices_to={'role': 'DEAN'}, 
                           related_name='dean_of_colleges', verbose_name="العميد")
    
    # معلومات الكلية
    description = models.TextField(blank=True, verbose_name="وصف الكلية")
    established_year = models.IntegerField(validators=[MinValueValidator(1800)],
                                        verbose_name="سنة التأسيس")
    
    # معلومات الاتصال
    building = models.CharField(max_length=100, blank=True, verbose_name="المبنى")
    floor = models.CharField(max_length=50, blank=True, verbose_name="الطابق")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "كلية"
        verbose_name_plural = "الكليات"
        unique_together = ['university', 'code']
    
    def __str__(self):
        return f"{self.name} - {self.university.name}"

class Department(models.Model):
    """نموذج القسم"""
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, 
                              related_name='departments', verbose_name="الكلية")
    name = models.CharField(max_length=200, verbose_name="اسم القسم")
    name_en = models.CharField(max_length=200, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=10, verbose_name="رمز القسم")
    
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           limit_choices_to={'role': 'HEAD_OF_DEPARTMENT'},
                           related_name='head_of_departments', verbose_name="رئيس القسم")
    
    # معلومات القسم
    description = models.TextField(blank=True, verbose_name="وصف القسم")
    
    # معلومات الاتصال
    office_location = models.CharField(max_length=100, blank=True, verbose_name="موقع المكتب")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        unique_together = ['college', 'code']
    
    def __str__(self):
        return f"{self.name} - {self.college.name}"

class AcademicProgram(models.Model):
    """البرامج الأكاديمية"""
    
    PROGRAM_TYPES = [
        ('DIPLOMA', 'دبلوم'),
        ('BACHELOR', 'بكالوريوس'),
        ('MASTER', 'ماجستير'),
        ('DOCTORATE', 'دكتوراه'),
        ('CERTIFICATE', 'شهادة'),
    ]
    
    STUDY_MODES = [
        ('FULL_TIME', 'دوام كامل'),
        ('PART_TIME', 'دوام جزئي'),
        ('EVENING', 'مسائي'),
        ('WEEKEND', 'نهاية الأسبوع'),
        ('ONLINE', 'عن بعد'),
        ('HYBRID', 'مختلط'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                 related_name='programs', verbose_name="القسم")
    
    name = models.CharField(max_length=200, verbose_name="اسم البرنامج")
    name_en = models.CharField(max_length=200, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز البرنامج")
    
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES,
                                  verbose_name="نوع البرنامج")
    study_mode = models.CharField(max_length=20, choices=STUDY_MODES,
                                default='FULL_TIME', verbose_name="نمط الدراسة")
    
    # تفاصيل البرنامج
    description = models.TextField(blank=True, verbose_name="وصف البرنامج")
    duration_semesters = models.IntegerField(validators=[MinValueValidator(1)],
                                           verbose_name="عدد الفصول الدراسية")
    total_credit_hours = models.IntegerField(validators=[MinValueValidator(1)],
                                           verbose_name="إجمالي الساعات المعتمدة")
    
    # متطلبات القبول
    admission_requirements = models.TextField(blank=True, verbose_name="متطلبات القبول")
    minimum_gpa = models.FloatField(default=2.0, validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
                                  verbose_name="أقل معدل للقبول")
    
    # رسوم البرنامج
    tuition_fee_per_semester = models.DecimalField(max_digits=10, decimal_places=2,
                                                 verbose_name="الرسوم الدراسية لكل فصل")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "برنامج أكاديمي"
        verbose_name_plural = "البرامج الأكاديمية"
        unique_together = ['department', 'code']
    
    def __str__(self):
        return f"{self.name} ({self.get_program_type_display()})"

class Student(models.Model):
    """نموذج الطالب المطور"""
    
    STUDENT_STATUS = [
        ('ENROLLED', 'مسجل'),
        ('ON_HOLD', 'موقوف'),
        ('GRADUATED', 'متخرج'),
        ('TRANSFERRED', 'محول'),
        ('DROPPED', 'منسحب'),
        ('DISMISSED', 'مفصول'),
    ]
    
    STUDY_MODES = [
        ('FULL_TIME', 'دوام كامل'),
        ('PART_TIME', 'دوام جزئي'),
        ('EVENING', 'مسائي'),
        ('WEEKEND', 'نهاية الأسبوع'),
    ]
    
    # ربط مع المستخدم
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile',
                               limit_choices_to={'role': 'STUDENT'}, verbose_name="المستخدم")
    
    # معلومات أكاديمية أساسية
    student_id = models.CharField(max_length=20, unique=True, verbose_name="رقم الطالب")
    program = models.ForeignKey(AcademicProgram, on_delete=models.CASCADE,
                              related_name='students', verbose_name="البرنامج الأكاديمي")
    
    # معلومات التسجيل
    admission_date = models.DateField(verbose_name="تاريخ القبول")
    admission_year = models.IntegerField(verbose_name="سنة القبول")
    admission_semester = models.CharField(max_length=20, choices=[
        ('FALL', 'الخريف'),
        ('SPRING', 'الربيع'),
        ('SUMMER', 'الصيف'),
    ], verbose_name="فصل القبول")
    
    # الحالة الأكاديمية
    status = models.CharField(max_length=20, choices=STUDENT_STATUS, default='ENROLLED',
                            verbose_name="حالة الطالب")
    study_mode = models.CharField(max_length=20, choices=STUDY_MODES, default='FULL_TIME',
                                verbose_name="نمط الدراسة")
    
    # معلومات التقدم الأكاديمي
    current_semester = models.IntegerField(default=1, validators=[MinValueValidator(1)],
                                         verbose_name="الفصل الحالي")
    current_level = models.CharField(max_length=20, choices=[
        ('FRESHMAN', 'السنة الأولى'),
        ('SOPHOMORE', 'السنة الثانية'),
        ('JUNIOR', 'السنة الثالثة'),
        ('SENIOR', 'السنة الرابعة'),
        ('GRADUATE', 'دراسات عليا'),
    ], default='FRESHMAN', verbose_name="المستوى الأكاديمي")
    
    # المعدلات والدرجات
    cumulative_gpa = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
                                     verbose_name="المعدل التراكمي")
    semester_gpa = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
                                   verbose_name="معدل الفصل")
    total_credit_hours_completed = models.IntegerField(default=0, verbose_name="الساعات المكتملة")
    total_credit_hours_attempted = models.IntegerField(default=0, verbose_name="الساعات المحاولة")
    
    # معلومات المستشار الأكاديمي
    academic_advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       limit_choices_to={'role__in': ['TEACHER', 'ASSISTANT_TEACHER']},
                                       related_name='advised_students', verbose_name="المستشار الأكاديمي")
    
    # معلومات التخرج
    expected_graduation_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التخرج المتوقع")
    graduation_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التخرج الفعلي")
    
    # معلومات إضافية
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    is_honors_student = models.BooleanField(default=False, verbose_name="طالب متفوق")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"
        ordering = ['student_id']
        indexes = [
            models.Index(fields=['student_id', 'status']),
            models.Index(fields=['program', 'admission_year']),
            models.Index(fields=['cumulative_gpa']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص مع حساب التواريخ المتوقعة"""
        if not self.expected_graduation_date and self.program:
            # حساب تاريخ التخرج المتوقع
            from datetime import date
            from dateutil.relativedelta import relativedelta
            
            duration_months = self.program.duration_semesters * 6  # كل فصل 6 أشهر
            self.expected_graduation_date = self.admission_date + relativedelta(months=duration_months)
        
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """الاسم الكامل للطالب"""
        return self.user.get_full_name() or self.user.username
    
    @property
    def completion_percentage(self):
        """نسبة الإنجاز من البرنامج"""
        if self.program and self.program.total_credit_hours > 0:
            return min(100, (self.total_credit_hours_completed / self.program.total_credit_hours) * 100)
        return 0
    
    @property
    def is_on_probation(self):
        """فحص إذا كان الطالب تحت المراقبة الأكاديمية"""
        return self.cumulative_gpa < 2.0 and self.total_credit_hours_completed > 12
    
    @property
    def academic_standing(self):
        """التقييم الأكاديمي للطالب"""
        gpa = self.cumulative_gpa
        if gpa >= 3.75:
            return "ممتاز مع مرتبة الشرف"
        elif gpa >= 3.5:
            return "ممتاز"
        elif gpa >= 3.0:
            return "جيد جداً"
        elif gpa >= 2.5:
            return "جيد"
        elif gpa >= 2.0:
            return "مقبول"
        else:
            return "ضعيف"

class StudentDocument(models.Model):
    """وثائق الطالب"""
    
    DOCUMENT_TYPES = [
        ('TRANSCRIPT', 'كشف الدرجات'),
        ('ID_COPY', 'صورة الهوية'),
        ('PASSPORT_COPY', 'صورة الجواز'),
        ('PHOTO', 'صورة شخصية'),
        ('BIRTH_CERTIFICATE', 'شهادة الميلاد'),
        ('HIGH_SCHOOL_CERTIFICATE', 'شهادة الثانوية'),
        ('MEDICAL_REPORT', 'تقرير طبي'),
        ('OTHER', 'أخرى'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, 
                               related_name='documents', verbose_name="الطالب")
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES,
                                   verbose_name="نوع الوثيقة")
    title = models.CharField(max_length=200, verbose_name="عنوان الوثيقة")
    description = models.TextField(blank=True, verbose_name="الوصف")
    
    file = models.FileField(upload_to='student_documents/%Y/%m/', verbose_name="الملف")
    file_size = models.IntegerField(default=0, verbose_name="حجم الملف")
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='uploaded_documents', verbose_name="تم الرفع بواسطة")
    
    is_verified = models.BooleanField(default=False, verbose_name="موثق")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='verified_documents', verbose_name="تم التوثيق بواسطة")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التوثيق")
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")
    
    class Meta:
        verbose_name = "وثيقة طالب"
        verbose_name_plural = "وثائق الطلاب"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لحساب حجم الملف"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)