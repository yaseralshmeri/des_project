# نماذج الطلاب المطورة والموحدة
# Enhanced and Unified Student Models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from PIL import Image
import os
import uuid

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT',
                          verbose_name="الدور الوظيفي")
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True,
                                 verbose_name="رقم الموظف")
    student_id = models.CharField(max_length=15, unique=True, null=True, blank=True,
                                verbose_name="رقم الطالب")
    
    # معلومات شخصية مطورة
    first_name_ar = models.CharField(max_length=50, blank=True, verbose_name="الاسم الأول - عربي")
    last_name_ar = models.CharField(max_length=50, blank=True, verbose_name="اسم العائلة - عربي")
    first_name_en = models.CharField(max_length=50, blank=True, verbose_name="الاسم الأول - إنجليزي")
    last_name_en = models.CharField(max_length=50, blank=True, verbose_name="اسم العائلة - إنجليزي")
    
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="الاسم الأوسط")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="الجنس")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="تاريخ الميلاد")
    place_of_birth = models.CharField(max_length=100, blank=True, verbose_name="مكان الميلاد")
    nationality = models.CharField(max_length=50, blank=True, verbose_name="الجنسية")
    
    # معلومات الاتصال المحسنة
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="رقم الهاتف يجب أن يكون بالصيغة: '+966501234567'. الحد الأقصى 15 رقم."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True,
                                  verbose_name="رقم الهاتف")
    phone_number_2 = models.CharField(validators=[phone_regex], max_length=17, 
                                    blank=True, verbose_name="رقم هاتف إضافي")
    
    # العنوان الكامل
    address_line_1 = models.CharField(max_length=255, blank=True, verbose_name="العنوان - السطر الأول")
    address_line_2 = models.CharField(max_length=255, blank=True, verbose_name="العنوان - السطر الثاني")
    city = models.CharField(max_length=100, blank=True, verbose_name="المدينة")
    state_province = models.CharField(max_length=100, blank=True, verbose_name="المنطقة/المحافظة")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="الرمز البريدي")
    country = models.CharField(max_length=100, default="السعودية", verbose_name="البلد")
    
    # معلومات أكاديمية للطلاب
    enrollment_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التسجيل")
    expected_graduation = models.DateField(null=True, blank=True, verbose_name="تاريخ التخرج المتوقع")
    academic_level = models.CharField(max_length=20, blank=True, verbose_name="المستوى الأكاديمي")
    
    # الحالة والإعدادات
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="الحالة")
    is_verified = models.BooleanField(default=False, verbose_name="مُوثق")
    verification_token = models.CharField(max_length=255, blank=True, verbose_name="رمز التوثيق")
    
    # الصورة الشخصية
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True,
                                      verbose_name="الصورة الشخصية")
    
    # معلومات حالة الحساب
    last_activity = models.DateTimeField(auto_now=True, verbose_name="آخر نشاط")
    failed_login_attempts = models.IntegerField(default=0, verbose_name="محاولات تسجيل دخول فاشلة")
    account_locked_until = models.DateTimeField(null=True, blank=True, 
                                              verbose_name="مُغلق حتى")
    
    # إعدادات الخصوصية والإشعارات
    privacy_settings = models.JSONField(default=dict, verbose_name="إعدادات الخصوصية")
    notification_preferences = models.JSONField(default=dict, verbose_name="تفضيلات الإشعارات")
    language_preference = models.CharField(max_length=5, default='ar', 
                                         choices=[('ar', 'العربية'), ('en', 'English')],
                                         verbose_name="لغة الواجهة")
    
    # معلومات إضافية
    emergency_contact_name = models.CharField(max_length=100, blank=True, 
                                            verbose_name="اسم جهة الاتصال للطوارئ")
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, 
                                             blank=True, verbose_name="هاتف جهة الاتصال للطوارئ")
    emergency_contact_relation = models.CharField(max_length=50, blank=True, 
                                                verbose_name="صلة القرابة لجهة الاتصال")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_users', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        ordering = ['first_name_ar', 'last_name_ar']
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['student_id']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        if self.language_preference == 'ar':
            return f"{self.first_name_ar} {self.last_name_ar}"
        return f"{self.first_name_en} {self.last_name_en}"
    
    @property
    def full_name_ar(self):
        return f"{self.first_name_ar} {self.middle_name} {self.last_name_ar}".strip()
    
    @property
    def full_name_en(self):
        return f"{self.first_name_en} {self.middle_name} {self.last_name_en}".strip()
    
    @property
    def display_name(self):
        return self.full_name_ar if self.language_preference == 'ar' else self.full_name_en
    
    @property
    def is_student(self):
        return self.role == 'STUDENT'
    
    @property
    def is_teacher(self):
        return self.role in ['TEACHER', 'ASSISTANT_TEACHER']
    
    @property
    def is_admin(self):
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    @property
    def is_staff_member(self):
        return self.role in ['DEAN', 'HEAD_OF_DEPARTMENT', 'REGISTRAR', 'ACCOUNTANT', 'HR_MANAGER']
    
    def save(self, *args, **kwargs):
        # Auto-generate student/employee ID
        if not self.student_id and self.role == 'STUDENT':
            self.student_id = self.generate_student_id()
        elif not self.employee_id and self.role != 'STUDENT':
            self.employee_id = self.generate_employee_id()
        
        # Resize profile picture
        super().save(*args, **kwargs)
        if self.profile_picture:
            self.resize_profile_picture()
    
    def generate_student_id(self):
        """توليد رقم طالب تلقائي"""
        year = timezone.now().year
        count = User.objects.filter(role='STUDENT', student_id__startswith=str(year)).count()
        return f"{year}{count + 1:06d}"
    
    def generate_employee_id(self):
        """توليد رقم موظف تلقائي"""
        count = User.objects.filter(employee_id__isnull=False).count()
        return f"EMP{count + 1:06d}"
    
    def resize_profile_picture(self):
        """تصغير الصورة الشخصية"""
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)


class StudentProfile(models.Model):
    """الملف الشخصي الأكاديمي للطالب"""
    
    STUDY_STATUS_CHOICES = [
        ('REGULAR', 'نظامي'),
        ('PART_TIME', 'جزئي'),
        ('DISTANCE', 'تعليم عن بُعد'),
        ('EXCHANGE', 'طالب تبادل'),
    ]
    
    ACADEMIC_STANDING_CHOICES = [
        ('EXCELLENT', 'ممتاز'),
        ('VERY_GOOD', 'جيد جداً'),
        ('GOOD', 'جيد'),
        ('SATISFACTORY', 'مقبول'),
        ('PROBATION', 'تحت المراقبة'),
        ('ACADEMIC_WARNING', 'إنذار أكاديمي'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                               related_name='student_profile', verbose_name="الطالب")
    
    # معلومات أكاديمية
    student_id_display = models.CharField(max_length=15, unique=True, verbose_name="رقم الطالب")
    college = models.ForeignKey('courses.College', on_delete=models.PROTECT, 
                               verbose_name="الكلية")
    department = models.ForeignKey('courses.Department', on_delete=models.PROTECT,
                                  verbose_name="القسم")
    major = models.ForeignKey('courses.Major', on_delete=models.PROTECT,
                             verbose_name="التخصص")
    minor = models.ForeignKey('courses.Major', on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='minor_students',
                             verbose_name="التخصص الفرعي")
    
    # الحالة الأكاديمية
    study_status = models.CharField(max_length=15, choices=STUDY_STATUS_CHOICES,
                                  default='REGULAR', verbose_name="نوع الدراسة")
    academic_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)],
                                       verbose_name="المستوى الأكاديمي")
    current_semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)],
                                         verbose_name="الفصل الدراسي الحالي")
    academic_year = models.CharField(max_length=9, verbose_name="السنة الأكاديمية")
    
    # المعدلات والإحصائيات
    cumulative_gpa = models.DecimalField(max_digits=4, decimal_places=3, default=0.000,
                                       validators=[MinValueValidator(0), MaxValueValidator(4)],
                                       verbose_name="المعدل التراكمي")
    semester_gpa = models.DecimalField(max_digits=4, decimal_places=3, default=0.000,
                                     validators=[MinValueValidator(0), MaxValueValidator(4)],
                                     verbose_name="معدل الفصل")
    total_credit_hours = models.IntegerField(default=0, verbose_name="إجمالي الساعات المكتسبة")
    completed_credit_hours = models.IntegerField(default=0, verbose_name="الساعات المكتملة")
    required_credit_hours = models.IntegerField(default=132, verbose_name="الساعات المطلوبة للتخرج")
    
    # الحالة الأكاديمية
    academic_standing = models.CharField(max_length=20, choices=ACADEMIC_STANDING_CHOICES,
                                       default='SATISFACTORY', verbose_name="المستوى الأكاديمي")
    warnings_count = models.IntegerField(default=0, verbose_name="عدد الإنذارات")
    is_on_probation = models.BooleanField(default=False, verbose_name="تحت المراقبة")
    probation_start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ بداية المراقبة")
    
    # معلومات التخرج
    expected_graduation_date = models.DateField(null=True, blank=True, 
                                              verbose_name="تاريخ التخرج المتوقع")
    graduation_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التخرج الفعلي")
    is_graduated = models.BooleanField(default=False, verbose_name="متخرج")
    graduation_gpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                       verbose_name="معدل التخرج")
    graduation_honors = models.CharField(max_length=50, blank=True, verbose_name="مراتب الشرف")
    
    # معلومات المستشار الأكاديمي
    academic_advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='advised_students', verbose_name="المستشار الأكاديمي")
    advisor_assignment_date = models.DateField(null=True, blank=True, 
                                             verbose_name="تاريخ تعيين المستشار")
    
    # إعدادات وملاحظات
    special_needs = models.TextField(blank=True, verbose_name="احتياجات خاصة")
    medical_conditions = models.TextField(blank=True, verbose_name="حالات طبية")
    notes = models.TextField(blank=True, verbose_name="ملاحظات إضافية")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "الملف الأكاديمي للطالب"
        verbose_name_plural = "الملفات الأكاديمية للطلاب"
        ordering = ['student_id_display']
        indexes = [
            models.Index(fields=['college', 'department', 'major']),
            models.Index(fields=['academic_level', 'current_semester']),
            models.Index(fields=['cumulative_gpa']),
            models.Index(fields=['academic_standing']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.student_id_display}"
    
    @property
    def completion_percentage(self):
        """نسبة الإكمال الأكاديمي"""
        if self.required_credit_hours > 0:
            return min((self.completed_credit_hours / self.required_credit_hours) * 100, 100)
        return 0
    
    @property
    def remaining_credit_hours(self):
        """الساعات المتبقية للتخرج"""
        return max(self.required_credit_hours - self.completed_credit_hours, 0)
    
    @property
    def is_eligible_for_graduation(self):
        """مؤهل للتخرج"""
        return (self.completed_credit_hours >= self.required_credit_hours and 
                self.cumulative_gpa >= 2.000 and
                not self.is_on_probation)
    
    def update_gpa(self):
        """تحديث المعدل التراكمي"""
        # سيتم تنفيذ هذه الدالة في نموذج الدرجات
        pass
    
    def add_warning(self, reason=""):
        """إضافة إنذار أكاديمي"""
        self.warnings_count += 1
        if self.warnings_count >= 2:
            self.is_on_probation = True
            self.probation_start_date = timezone.now().date()
        self.save()
    
    def remove_probation(self):
        """إزالة المراقبة الأكاديمية"""
        self.is_on_probation = False
        self.probation_start_date = None
        self.save()


class TeacherProfile(models.Model):
    """الملف الشخصي للأستاذ"""
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'دوام كامل'),
        ('PART_TIME', 'دوام جزئي'),
        ('VISITING', 'أستاذ زائر'),
        ('ADJUNCT', 'مساعد تدريس'),
        ('EMERITUS', 'أستاذ متقاعد'),
    ]
    
    ACADEMIC_RANK_CHOICES = [
        ('PROFESSOR', 'أستاذ'),
        ('ASSOCIATE_PROFESSOR', 'أستاذ مشارك'),
        ('ASSISTANT_PROFESSOR', 'أستاذ مساعد'),
        ('LECTURER', 'محاضر'),
        ('TEACHING_ASSISTANT', 'معيد'),
        ('INSTRUCTOR', 'مدرس'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                               related_name='teacher_profile', verbose_name="الأستاذ")
    
    # معلومات أكاديمية
    employee_id_display = models.CharField(max_length=20, unique=True, verbose_name="رقم الموظف")
    college = models.ForeignKey('courses.College', on_delete=models.PROTECT, 
                               verbose_name="الكلية")
    department = models.ForeignKey('courses.Department', on_delete=models.PROTECT,
                                  verbose_name="القسم")
    
    # الرتبة الأكاديمية والتوظيف
    academic_rank = models.CharField(max_length=25, choices=ACADEMIC_RANK_CHOICES,
                                   verbose_name="الرتبة الأكاديمية")
    employment_type = models.CharField(max_length=15, choices=EMPLOYMENT_TYPE_CHOICES,
                                     default='FULL_TIME', verbose_name="نوع التوظيف")
    hire_date = models.DateField(verbose_name="تاريخ التوظيف")
    tenure_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الحصول على الثبات")
    
    # المؤهلات العلمية
    highest_degree = models.CharField(max_length=50, verbose_name="أعلى مؤهل علمي")
    degree_institution = models.CharField(max_length=200, verbose_name="مؤسسة المؤهل")
    degree_year = models.IntegerField(verbose_name="سنة الحصول على المؤهل")
    specialization = models.CharField(max_length=200, verbose_name="التخصص الدقيق")
    
    # معلومات التدريس
    office_number = models.CharField(max_length=20, blank=True, verbose_name="رقم المكتب")
    office_phone = models.CharField(max_length=20, blank=True, verbose_name="هاتف المكتب")
    office_hours = models.TextField(blank=True, verbose_name="ساعات المكتب")
    
    # إحصائيات التدريس
    total_courses_taught = models.IntegerField(default=0, verbose_name="إجمالي المقررات المُدرسة")
    current_teaching_load = models.IntegerField(default=0, verbose_name="العبء التدريسي الحالي")
    max_teaching_load = models.IntegerField(default=12, verbose_name="الحد الأقصى للعبء التدريسي")
    
    # البحث العلمي
    research_interests = models.TextField(blank=True, verbose_name="الاهتمامات البحثية")
    publications_count = models.IntegerField(default=0, verbose_name="عدد المنشورات العلمية")
    research_projects = models.TextField(blank=True, verbose_name="المشاريع البحثية")
    
    # التقييمات والجوائز
    teaching_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)],
                                        verbose_name="تقييم التدريس")
    awards = models.TextField(blank=True, verbose_name="الجوائز والتكريمات")
    
    # معلومات إضافية
    bio = models.TextField(blank=True, verbose_name="السيرة الذاتية المختصرة")
    languages_spoken = models.CharField(max_length=200, blank=True, verbose_name="اللغات المتقنة")
    
    # الحالة والإعدادات
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    can_supervise_thesis = models.BooleanField(default=False, verbose_name="يمكنه الإشراف على الرسائل")
    max_thesis_supervision = models.IntegerField(default=5, verbose_name="الحد الأقصى للإشراف")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "ملف أكاديمي - أستاذ"
        verbose_name_plural = "الملفات الأكاديمية - الأساتذة"
        ordering = ['academic_rank', 'user__first_name_ar']
        indexes = [
            models.Index(fields=['college', 'department']),
            models.Index(fields=['academic_rank']),
            models.Index(fields=['employment_type']),
        ]
    
    def __str__(self):
        return f"{self.get_academic_rank_display()} {self.user.display_name}"
    
    @property
    def years_of_service(self):
        """سنوات الخدمة"""
        return (timezone.now().date() - self.hire_date).days // 365
    
    @property
    def is_available_for_new_courses(self):
        """متاح لمقررات جديدة"""
        return self.current_teaching_load < self.max_teaching_load
    
    @property
    def available_teaching_hours(self):
        """الساعات التدريسية المتاحة"""
        return max(self.max_teaching_load - self.current_teaching_load, 0)


class UserActivity(models.Model):
    """سجل نشاطات المستخدم"""
    
    ACTION_CHOICES = [
        ('LOGIN', 'تسجيل دخول'),
        ('LOGOUT', 'تسجيل خروج'),
        ('VIEW', 'عرض'),
        ('CREATE', 'إنشاء'),
        ('UPDATE', 'تحديث'),
        ('DELETE', 'حذف'),
        ('DOWNLOAD', 'تحميل'),
        ('UPLOAD', 'رفع ملف'),
        ('EXPORT', 'تصدير'),
        ('PRINT', 'طباعة'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities',
                           verbose_name="المستخدم")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="الإجراء")
    description = models.CharField(max_length=255, verbose_name="الوصف")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    # للربط مع أي نموذج آخر
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name = "نشاط المستخدم"
        verbose_name_plural = "نشاطات المستخدمين"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.get_action_display()} - {self.timestamp}"


class UserPreferences(models.Model):
    """تفضيلات المستخدم"""
    
    THEME_CHOICES = [
        ('light', 'فاتح'),
        ('dark', 'داكن'),
        ('auto', 'تلقائي'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                               related_name='preferences', verbose_name="المستخدم")
    
    # إعدادات الواجهة
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light',
                           verbose_name="المظهر")
    language = models.CharField(max_length=5, choices=[('ar', 'العربية'), ('en', 'English')],
                              default='ar', verbose_name="اللغة")
    timezone = models.CharField(max_length=50, default='Asia/Riyadh', verbose_name="المنطقة الزمنية")
    
    # إعدادات الإشعارات
    email_notifications = models.BooleanField(default=True, verbose_name="إشعارات البريد الإلكتروني")
    sms_notifications = models.BooleanField(default=False, verbose_name="إشعارات الرسائل النصية")
    push_notifications = models.BooleanField(default=True, verbose_name="إشعارات فورية")
    
    # إعدادات لوحة التحكم
    dashboard_layout = models.JSONField(default=dict, verbose_name="تخطيط لوحة التحكم")
    favorite_widgets = models.JSONField(default=list, verbose_name="الأدوات المفضلة")
    
    # إعدادات الخصوصية
    profile_visibility = models.CharField(max_length=10, 
                                        choices=[('public', 'عام'), ('private', 'خاص')],
                                        default='private', verbose_name="مستوى الخصوصية")
    show_online_status = models.BooleanField(default=True, verbose_name="إظهار الحالة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تفضيلات المستخدم"
        verbose_name_plural = "تفضيلات المستخدمين"
    
    def __str__(self):
        return f"تفضيلات {self.user.display_name}"


# Legacy compatibility - Student model alias
Student = StudentProfile