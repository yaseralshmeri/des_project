# نماذج المقررات والبرامج الأكاديمية المطورة
# Enhanced Course and Academic Program Models

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class University(models.Model):
    """نموذج الجامعة"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_ar = models.CharField(max_length=200, verbose_name="اسم الجامعة - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم الجامعة - إنجليزي")
    code = models.CharField(max_length=10, unique=True, verbose_name="رمز الجامعة")
    
    # معلومات الجامعة
    founded_year = models.IntegerField(verbose_name="سنة التأسيس")
    university_type = models.CharField(max_length=20, 
                                     choices=[
                                         ('PUBLIC', 'حكومية'),
                                         ('PRIVATE', 'خاصة'),
                                         ('NONPROFIT', 'غير ربحية')
                                     ], default='PUBLIC', verbose_name="نوع الجامعة")
    
    # العنوان ومعلومات الاتصال
    address = models.TextField(verbose_name="العنوان")
    phone = models.CharField(max_length=20, verbose_name="الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    website = models.URLField(blank=True, verbose_name="الموقع الإلكتروني")
    
    # الإعدادات الأكاديمية
    academic_calendar_type = models.CharField(max_length=15,
                                            choices=[
                                                ('SEMESTER', 'فصلي'),
                                                ('QUARTER', 'ربع سنوي'),
                                                ('TRIMESTER', 'ثلاثي')
                                            ], default='SEMESTER', verbose_name="نظام التقويم الأكاديمي")
    
    grading_system = models.CharField(max_length=15,
                                    choices=[
                                        ('GPA_4', 'نظام 4.0'),
                                        ('GPA_5', 'نظام 5.0'),
                                        ('PERCENTAGE', 'النسبة المئوية')
                                    ], default='GPA_4', verbose_name="نظام التقدير")
    
    # معلومات إضافية
    logo = models.ImageField(upload_to='university_logos/', null=True, blank=True,
                           verbose_name="شعار الجامعة")
    description = models.TextField(blank=True, verbose_name="وصف الجامعة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "جامعة"
        verbose_name_plural = "الجامعات"
        ordering = ['name_ar']
    
    def __str__(self):
        return self.name_ar


class College(models.Model):
    """نموذج الكلية"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(University, on_delete=models.CASCADE, 
                                 related_name='colleges', verbose_name="الجامعة")
    
    name_ar = models.CharField(max_length=200, verbose_name="اسم الكلية - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم الكلية - إنجليزي")
    code = models.CharField(max_length=10, verbose_name="رمز الكلية")
    
    # القيادة الأكاديمية
    dean = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='colleges_as_dean', verbose_name="العميد")
    vice_dean_academic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='colleges_as_vice_dean_academic',
                                         verbose_name="وكيل الكلية للشؤون الأكاديمية")
    vice_dean_graduate = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='colleges_as_vice_dean_graduate',
                                         verbose_name="وكيل الكلية للدراسات العليا")
    
    # معلومات الكلية
    established_year = models.IntegerField(verbose_name="سنة التأسيس")
    building = models.CharField(max_length=100, blank=True, verbose_name="المبنى")
    floor = models.CharField(max_length=50, blank=True, verbose_name="الدور")
    
    # معلومات الاتصال
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    website = models.URLField(blank=True, verbose_name="الموقع الإلكتروني")
    
    # إحصائيات
    total_departments = models.IntegerField(default=0, verbose_name="عدد الأقسام")
    total_students = models.IntegerField(default=0, verbose_name="عدد الطلاب")
    total_faculty = models.IntegerField(default=0, verbose_name="عدد أعضاء هيئة التدريس")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "كلية"
        verbose_name_plural = "الكليات"
        ordering = ['university', 'name_ar']
        unique_together = ['university', 'code']
    
    def __str__(self):
        return f"{self.name_ar} - {self.university.name_ar}"


class Department(models.Model):
    """نموذج القسم الأكاديمي"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, 
                              related_name='departments', verbose_name="الكلية")
    
    name_ar = models.CharField(max_length=200, verbose_name="اسم القسم - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم القسم - إنجليزي")
    code = models.CharField(max_length=10, verbose_name="رمز القسم")
    
    # القيادة الأكاديمية
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='departments_as_head', verbose_name="رئيس القسم")
    vice_head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='departments_as_vice_head', verbose_name="نائب رئيس القسم")
    
    # معلومات القسم
    established_year = models.IntegerField(verbose_name="سنة التأسيس")
    location = models.CharField(max_length=200, blank=True, verbose_name="الموقع")
    
    # معلومات الاتصال
    phone = models.CharField(max_length=20, blank=True, verbose_name="هاتف القسم")
    email = models.EmailField(blank=True, verbose_name="بريد القسم الإلكتروني")
    website = models.URLField(blank=True, verbose_name="موقع القسم")
    
    # الأهداف والرؤية
    objectives = models.TextField(blank=True, verbose_name="أهداف القسم")
    
    # إحصائيات
    total_students = models.IntegerField(default=0, verbose_name="عدد الطلاب")
    total_faculty = models.IntegerField(default=0, verbose_name="عدد أعضاء هيئة التدريس")
    total_majors = models.IntegerField(default=0, verbose_name="عدد التخصصات")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "قسم أكاديمي"
        verbose_name_plural = "الأقسام الأكاديمية"
        ordering = ['college', 'name_ar']
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} - {self.college.name_ar}"


class Major(models.Model):
    """نموذج التخصص"""
    
    DEGREE_TYPE_CHOICES = [
        ('DIPLOMA', 'دبلوم'),
        ('ASSOCIATE', 'درجة مشارك'),
        ('BACHELOR', 'بكالوريوس'),
        ('MASTER', 'ماجستير'),
        ('DOCTORATE', 'دكتوراه'),
        ('CERTIFICATE', 'شهادة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                 related_name='majors', verbose_name="القسم")
    
    name_ar = models.CharField(max_length=200, verbose_name="اسم التخصص - عربي") 
    name_en = models.CharField(max_length=200, verbose_name="اسم التخصص - إنجليزي")
    code = models.CharField(max_length=15, verbose_name="رمز التخصص")
    
    # نوع الدرجة والمدة
    degree_type = models.CharField(max_length=15, choices=DEGREE_TYPE_CHOICES,
                                 verbose_name="نوع الدرجة")
    duration_years = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)],
                                       verbose_name="مدة الدراسة بالسنوات")
    total_credit_hours = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(200)],
                                           verbose_name="إجمالي الساعات المعتمدة")
    
    # متطلبات القبول
    min_gpa_requirement = models.DecimalField(max_digits=4, decimal_places=3, default=0.000,
                                            verbose_name="الحد الأدنى للمعدل المطلوب")
    max_students_per_year = models.IntegerField(default=100, verbose_name="الحد الأقصى للطلاب سنوياً")
    
    # الوصف والمعلومات
    description = models.TextField(verbose_name="وصف التخصص")
    career_prospects = models.TextField(blank=True, verbose_name="الفرص الوظيفية")
    admission_requirements = models.TextField(blank=True, verbose_name="متطلبات القبول")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تخصص"
        verbose_name_plural = "التخصصات"
        ordering = ['department', 'degree_type', 'name_ar']
        unique_together = ['department', 'code']
        indexes = [
            models.Index(fields=['department', 'degree_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} ({self.get_degree_type_display()}) - {self.department.name_ar}"


class Classroom(models.Model):
    """نموذج القاعة الدراسية"""
    
    CLASSROOM_TYPES = [
        ('LECTURE', 'قاعة محاضرات'),
        ('LAB', 'مختبر'),
        ('COMPUTER_LAB', 'مختبر حاسوب'),
        ('SEMINAR', 'قاعة ندوات'),
        ('AUDITORIUM', 'مدرج'),
        ('WORKSHOP', 'ورشة'),
        ('STUDIO', 'استوديو'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات القاعة
    name = models.CharField(max_length=100, verbose_name="اسم القاعة")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز القاعة")
    classroom_type = models.CharField(max_length=15, choices=CLASSROOM_TYPES,
                                    verbose_name="نوع القاعة")
    
    # الموقع
    building = models.CharField(max_length=100, verbose_name="المبنى")
    floor = models.CharField(max_length=50, verbose_name="الطابق")
    room_number = models.CharField(max_length=20, verbose_name="رقم الغرفة")
    
    # السعة والمواصفات
    capacity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="السعة")
    area_sqm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                 verbose_name="المساحة (متر مربع)")
    
    # التجهيزات
    has_projector = models.BooleanField(default=False, verbose_name="يحتوي على بروجيكتر")
    has_computer = models.BooleanField(default=False, verbose_name="يحتوي على حاسوب")
    has_whiteboard = models.BooleanField(default=True, verbose_name="يحتوي على لوح أبيض")
    has_blackboard = models.BooleanField(default=False, verbose_name="يحتوي على لوح أسود")
    has_ac = models.BooleanField(default=True, verbose_name="يحتوي على تكييف")
    has_wifi = models.BooleanField(default=True, verbose_name="يحتوي على واي فاي")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    is_available = models.BooleanField(default=True, verbose_name="متاحة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "قاعة دراسية"
        verbose_name_plural = "القاعات الدراسية"
        ordering = ['building', 'floor', 'room_number']
        unique_together = ['building', 'floor', 'room_number']
        indexes = [
            models.Index(fields=['classroom_type', 'is_active']),
            models.Index(fields=['building', 'floor']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.building} - {self.room_number})"
    
    @property
    def full_location(self):
        return f"{self.building} - الطابق {self.floor} - غرفة {self.room_number}"
    
    @property
    def equipment_list(self):
        equipment = []
        if self.has_projector:
            equipment.append('بروجيكتر')
        if self.has_computer:
            equipment.append('حاسوب')
        if self.has_whiteboard:
            equipment.append('لوح أبيض')
        if self.has_blackboard:
            equipment.append('لوح أسود')
        if self.has_ac:
            equipment.append('تكييف')
        if self.has_wifi:
            equipment.append('واي فاي')
        return equipment


class Course(models.Model):
    """نموذج المقرر الدراسي"""
    
    COURSE_TYPE_CHOICES = [
        ('CORE', 'متطلب أساسي'),
        ('MAJOR_REQUIRED', 'متطلب تخصص'),
        ('MAJOR_ELECTIVE', 'اختياري تخصص'),
        ('UNIVERSITY_REQUIRED', 'متطلب جامعة'),
        ('UNIVERSITY_ELECTIVE', 'اختياري جامعة'),
        ('FREE_ELECTIVE', 'اختياري حر'),
        ('REMEDIAL', 'استدراكي'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('FACE_TO_FACE', 'وجهاً لوجه'),
        ('ONLINE', 'إلكتروني'),
        ('HYBRID', 'مختلط'),
        ('LABORATORY', 'معملي'),
        ('FIELD_WORK', 'عمل ميداني'),
    ]
    
    DIFFICULTY_LEVEL_CHOICES = [
        ('BEGINNER', 'مبتدئ'),
        ('INTERMEDIATE', 'متوسط'),
        ('ADVANCED', 'متقدم'),
        ('EXPERT', 'خبير'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المقرر الأساسية
    code = models.CharField(max_length=15, unique=True, verbose_name="رمز المقرر")
    name_ar = models.CharField(max_length=200, verbose_name="اسم المقرر - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم المقرر - إنجليزي")
    
    # التصنيف الأكاديمي
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                 related_name='courses', verbose_name="القسم")
    majors = models.ManyToManyField(Major, through='MajorCourse', 
                                  related_name='courses', verbose_name="التخصصات")
    
    # خصائص المقرر
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES,
                                 verbose_name="نوع المقرر")
    credit_hours = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                     verbose_name="الساعات المعتمدة")
    theory_hours = models.IntegerField(default=0, verbose_name="الساعات النظرية")
    practical_hours = models.IntegerField(default=0, verbose_name="الساعات العملية")
    
    # المستوى والصعوبة
    academic_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)],
                                       verbose_name="المستوى الأكاديمي")
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_LEVEL_CHOICES,
                                      default='INTERMEDIATE', verbose_name="مستوى الصعوبة")
    
    # طريقة التدريس
    delivery_method = models.CharField(max_length=15, choices=DELIVERY_METHOD_CHOICES,
                                     default='FACE_TO_FACE', verbose_name="طريقة التدريس")
    
    # المحتوى والوصف
    description = models.TextField(verbose_name="وصف المقرر")
    objectives = models.TextField(verbose_name="أهداف المقرر")
    learning_outcomes = models.TextField(verbose_name="مخرجات التعلم")
    course_outline = models.TextField(blank=True, verbose_name="مفردات المقرر")
    
    # المتطلبات
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True,
                                         related_name='course_prerequisite_for',
                                         verbose_name="المتطلبات السابقة")
    corequisites = models.ManyToManyField('self', symmetrical=False, blank=True,
                                        related_name='corequisite_for',
                                        verbose_name="المتطلبات المصاحبة")
    min_gpa_required = models.DecimalField(max_digits=4, decimal_places=3, default=0.000,
                                         verbose_name="الحد الأدنى للمعدل المطلوب")
    
    # التقييم
    assessment_methods = models.JSONField(default=dict, verbose_name="طرق التقييم")
    has_final_exam = models.BooleanField(default=True, verbose_name="يحتوي على امتحان نهائي")
    has_midterm_exam = models.BooleanField(default=True, verbose_name="يحتوي على امتحان منتصف الفصل")
    
    # المصادر التعليمية
    textbook = models.TextField(blank=True, verbose_name="الكتاب المقرر")
    references = models.TextField(blank=True, verbose_name="المراجع")
    online_resources = models.URLField(blank=True, verbose_name="المصادر الإلكترونية")
    
    # إعدادات التسجيل
    max_enrollment = models.IntegerField(default=50, verbose_name="الحد الأقصى للتسجيل")
    min_enrollment = models.IntegerField(default=10, verbose_name="الحد الأدنى للتسجيل")
    allows_waitlist = models.BooleanField(default=True, verbose_name="يسمح بقائمة الانتظار")
    
    # الحالة والإعدادات
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_offered_online = models.BooleanField(default=False, verbose_name="متاح إلكترونياً")
    requires_lab = models.BooleanField(default=False, verbose_name="يتطلب معمل")
    requires_field_work = models.BooleanField(default=False, verbose_name="يتطلب عمل ميداني")
    
    # منسق المقرر
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='coordinated_courses', verbose_name="منسق المقرر")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_courses', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "مقرر دراسي"
        verbose_name_plural = "المقررات الدراسية"
        ordering = ['department', 'academic_level', 'code']
        indexes = [
            models.Index(fields=['department', 'course_type', 'is_active']),
            models.Index(fields=['academic_level']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name_ar}"
    
    @property
    def full_name(self):
        return f"{self.code} - {self.name_ar}"
    
    @property
    def prerequisites_list(self):
        return list(self.prerequisites.values_list('code', flat=True))
    
    @property
    def total_hours_per_week(self):
        return self.theory_hours + self.practical_hours


class AcademicYear(models.Model):
    """السنة الأكاديمية"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.CharField(max_length=9, unique=True, verbose_name="السنة الأكاديمية")  # 2024-2025
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    
    # الحالة
    is_current = models.BooleanField(default=False, verbose_name="السنة الحالية")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "سنة أكاديمية"
        verbose_name_plural = "السنوات الأكاديمية"
        ordering = ['-year']
    
    def __str__(self):
        return self.year
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # إزالة is_current من السنوات الأخرى
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Semester(models.Model):
    """الفصل الدراسي"""
    
    SEMESTER_TYPE_CHOICES = [
        ('FALL', 'الفصل الأول'),
        ('SPRING', 'الفصل الثاني'),
        ('SUMMER', 'الفصل الصيفي'),
        ('INTENSIVE', 'فصل مكثف'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                    related_name='semesters', verbose_name="السنة الأكاديمية")
    semester_type = models.CharField(max_length=10, choices=SEMESTER_TYPE_CHOICES,
                                   verbose_name="نوع الفصل")
    
    # التواريخ المهمة
    start_date = models.DateField(verbose_name="تاريخ بداية الفصل")
    end_date = models.DateField(verbose_name="تاريخ نهاية الفصل")
    
    # تواريخ التسجيل
    registration_start_date = models.DateField(verbose_name="تاريخ بداية التسجيل")
    registration_end_date = models.DateField(verbose_name="تاريخ نهاية التسجيل")
    add_drop_deadline = models.DateField(verbose_name="آخر موعد للإضافة والحذف")
    withdrawal_deadline = models.DateField(verbose_name="آخر موعد للانسحاب")
    
    # تواريخ الامتحانات
    midterm_start_date = models.DateField(null=True, blank=True, verbose_name="بداية امتحانات منتصف الفصل")
    midterm_end_date = models.DateField(null=True, blank=True, verbose_name="نهاية امتحانات منتصف الفصل")
    final_exam_start_date = models.DateField(null=True, blank=True, verbose_name="بداية الامتحانات النهائية")
    final_exam_end_date = models.DateField(null=True, blank=True, verbose_name="نهاية الامتحانات النهائية")
    
    # الحالة
    is_current = models.BooleanField(default=False, verbose_name="الفصل الحالي")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    registration_open = models.BooleanField(default=False, verbose_name="التسجيل مفتوح")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "فصل دراسي"
        verbose_name_plural = "الفصول الدراسية"
        ordering = ['-academic_year__year', 'semester_type']
        unique_together = ['academic_year', 'semester_type']
        indexes = [
            models.Index(fields=['academic_year', 'is_current']),
            models.Index(fields=['registration_open']),
        ]
    
    def __str__(self):
        return f"{self.get_semester_type_display()} - {self.academic_year.year}"
    
    @property
    def display_name(self):
        return f"{self.get_semester_type_display()} {self.academic_year.year}"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # إزالة is_current من الفصول الأخرى
            Semester.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class CourseOffering(models.Model):
    """عرض المقرر في فصل معين"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'مجدول'),
        ('ACTIVE', 'نشط'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                             related_name='offerings', verbose_name="المقرر")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                               related_name='course_offerings', verbose_name="الفصل الدراسي")
    
    # معلومات الشعبة
    section_number = models.CharField(max_length=10, verbose_name="رقم الشعبة")
    section_name = models.CharField(max_length=100, blank=True, verbose_name="اسم الشعبة")
    
    # أعضاء هيئة التدريس
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='course_offerings', verbose_name="المدرس")
    co_instructors = models.ManyToManyField(User, through='CourseInstructor',
                                          related_name='co_instructor_offerings', blank=True,
                                          verbose_name="المدرسون المساعدون")
    
    # التوقيت والمكان
    schedule_days = models.JSONField(default=list, verbose_name="أيام التدريس")  # ['SUNDAY', 'TUESDAY']
    start_time = models.TimeField(verbose_name="وقت البداية")
    end_time = models.TimeField(verbose_name="وقت النهاية")
    classroom = models.CharField(max_length=50, blank=True, verbose_name="القاعة")
    building = models.CharField(max_length=50, blank=True, verbose_name="المبنى")
    
    # إعدادات التسجيل
    max_enrollment = models.IntegerField(verbose_name="الحد الأقصى للتسجيل")
    current_enrollment = models.IntegerField(default=0, verbose_name="عدد المسجلين الحالي")
    waitlist_capacity = models.IntegerField(default=10, verbose_name="سعة قائمة الانتظار")
    current_waitlist = models.IntegerField(default=0, verbose_name="عدد قائمة الانتظار الحالي")
    
    # الحالة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED',
                            verbose_name="الحالة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    registration_open = models.BooleanField(default=True, verbose_name="التسجيل مفتوح")
    
    # ملاحظات خاصة
    special_notes = models.TextField(blank=True, verbose_name="ملاحظات خاصة")
    prerequisites_enforced = models.BooleanField(default=True, verbose_name="فرض المتطلبات السابقة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_offerings', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "عرض مقرر"
        verbose_name_plural = "عروض المقررات"
        ordering = ['semester', 'course__code', 'section_number']
        unique_together = ['course', 'semester', 'section_number']
        indexes = [
            models.Index(fields=['semester', 'status']),
            models.Index(fields=['course', 'semester']),
            models.Index(fields=['instructor']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.section_number} ({self.semester.display_name})"
    
    @property
    def is_full(self):
        return self.current_enrollment >= self.max_enrollment
    
    @property
    def is_waitlist_full(self):
        return self.current_waitlist >= self.waitlist_capacity
    
    @property
    def available_spots(self):
        return max(0, self.max_enrollment - self.current_enrollment)
    
    @property
    def available_waitlist_spots(self):
        return max(0, self.waitlist_capacity - self.current_waitlist)


class Assignment(models.Model):
    """نموذج التكليفات والواجبات"""
    
    ASSIGNMENT_TYPE_CHOICES = [
        ('HOMEWORK', 'واجب منزلي'),
        ('PROJECT', 'مشروع'),
        ('QUIZ', 'اختبار قصير'),
        ('MIDTERM', 'امتحان منتصف الفصل'),
        ('FINAL', 'امتحان نهائي'),
        ('LAB', 'تجربة معملية'),
        ('PRESENTATION', 'عرض تقديمي'),
        ('RESEARCH', 'بحث'),
        ('CASE_STUDY', 'دراسة حالة'),
        ('GROUP_WORK', 'عمل جماعي'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'مسودة'),
        ('PUBLISHED', 'منشور'),
        ('CLOSED', 'مغلق'),
        ('GRADED', 'مصحح'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE,
                                       related_name='assignments', verbose_name="عرض المقرر")
    
    # معلومات التكليف
    title = models.CharField(max_length=200, verbose_name="عنوان التكليف")
    description = models.TextField(verbose_name="وصف التكليف")
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES,
                                     verbose_name="نوع التكليف")
    
    # التقييم
    max_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="الدرجة العظمى")
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                          verbose_name="الوزن النسبي %")
    
    # التواريخ
    published_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النشر")
    due_date = models.DateTimeField(verbose_name="تاريخ التسليم")
    late_submission_allowed = models.BooleanField(default=True, verbose_name="السماح بالتسليم المتأخر")
    late_penalty_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                             verbose_name="خصم التأخير لكل يوم")
    
    # الإعدادات
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT',
                            verbose_name="الحالة")
    is_group_assignment = models.BooleanField(default=False, verbose_name="تكليف جماعي")
    max_group_size = models.IntegerField(default=1, verbose_name="الحد الأقصى لحجم المجموعة")
    
    # الملفات والمرفقات
    instructions_file = models.FileField(upload_to='assignments/instructions/', null=True, blank=True,
                                       verbose_name="ملف التعليمات")
    submission_format = models.CharField(max_length=100, blank=True,
                                       verbose_name="تنسيق التسليم المطلوب")
    
    # معلومات إضافية
    rubric = models.JSONField(default=dict, blank=True, verbose_name="معايير التقييم")
    estimated_time_hours = models.IntegerField(default=2, verbose_name="الوقت المقدر بالساعات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_assignments', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "تكليف"
        verbose_name_plural = "التكليفات"
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['course_offering', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['assignment_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.course_offering.course.code}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date and self.status != 'CLOSED'
    
    @property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def is_published(self):
        return self.status == 'PUBLISHED' and self.published_date and self.published_date <= timezone.now()


class CourseInstructor(models.Model):
    """ربط المدرسين بعروض المقررات"""
    
    ROLE_CHOICES = [
        ('PRIMARY', 'مدرس رئيسي'),
        ('SECONDARY', 'مدرس مساعد'),
        ('ASSISTANT', 'مساعد تدريس'),
        ('GUEST', 'مدرس زائر'),
    ]
    
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE,
                                       verbose_name="عرض المقرر")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE,
                                 verbose_name="المدرس")
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='SECONDARY',
                          verbose_name="الدور")
    
    # الصلاحيات
    can_grade = models.BooleanField(default=True, verbose_name="يمكنه التقييم")
    can_manage_assignments = models.BooleanField(default=False, verbose_name="يمكنه إدارة التكليفات")
    can_manage_attendance = models.BooleanField(default=True, verbose_name="يمكنه إدارة الحضور")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "مدرس المقرر"
        verbose_name_plural = "مدرسو المقررات"
        unique_together = ['course_offering', 'instructor']
    
    def __str__(self):
        return f"{self.instructor.get_full_name() if hasattr(self.instructor, 'get_full_name') else self.instructor.username} - {self.course_offering}"


class MajorCourse(models.Model):
    """ربط التخصص بالمقرر مع تفاصيل إضافية"""
    
    major = models.ForeignKey(Major, on_delete=models.CASCADE, verbose_name="التخصص")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="المقرر")
    
    # تفاصيل العلاقة
    is_required = models.BooleanField(default=True, verbose_name="مطلوب")
    semester_offered = models.IntegerField(default=1, 
                                         validators=[MinValueValidator(1), MaxValueValidator(8)],
                                         verbose_name="الفصل المُقدم فيه")
    year_offered = models.IntegerField(default=1,
                                     validators=[MinValueValidator(1), MaxValueValidator(4)],
                                     verbose_name="السنة المُقدم فيها")
    
    # ترتيب المقرر في الخطة الدراسية
    sequence_order = models.IntegerField(default=1, verbose_name="ترتيب المتسلسل")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "مقرر التخصص"
        verbose_name_plural = "مقررات التخصصات"
        unique_together = ['major', 'course']
        ordering = ['major', 'year_offered', 'semester_offered', 'sequence_order']
        indexes = [
            models.Index(fields=['major', 'is_required']),
            models.Index(fields=['semester_offered', 'year_offered']),
        ]
    
    def __str__(self):
        return f"{self.major.name_ar} - {self.course.code}"


# استيراد نموذج التسجيل
from .enrollment import Enrollment