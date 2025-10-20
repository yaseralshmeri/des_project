# نظام التقارير المتطور والشامل
# Enhanced Comprehensive Reporting System

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from students.enhanced_models import Student, AcademicProgram, College, Department
from courses.enhanced_models import Course, Semester, CourseOffering
from finance.enhanced_models import StudentAccount, Payment
import json
import uuid
from decimal import Decimal

User = get_user_model()

class ReportTemplate(models.Model):
    """قوالب التقارير"""
    
    REPORT_CATEGORIES = [
        ('ACADEMIC', 'أكاديمي'),
        ('FINANCIAL', 'مالي'),
        ('ADMINISTRATIVE', 'إداري'),
        ('STATISTICAL', 'إحصائي'),
        ('ANALYTICAL', 'تحليلي'),
        ('OPERATIONAL', 'تشغيلي'),
        ('COMPLIANCE', 'امتثال'),
        ('PERFORMANCE', 'أداء'),
    ]
    
    REPORT_TYPES = [
        ('STUDENT_TRANSCRIPT', 'كشف درجات طالب'),
        ('COURSE_ROSTER', 'قائمة طلاب مقرر'),
        ('GRADE_DISTRIBUTION', 'توزيع الدرجات'),
        ('ATTENDANCE_REPORT', 'تقرير الحضور'),
        ('FINANCIAL_STATEMENT', 'كشف حساب مالي'),
        ('ENROLLMENT_STATISTICS', 'إحصائيات التسجيل'),
        ('GRADUATION_LIST', 'قائمة الخريجين'),
        ('FACULTY_WORKLOAD', 'أعباء أعضاء هيئة التدريس'),
        ('DEPARTMENT_SUMMARY', 'ملخص القسم'),
        ('UNIVERSITY_DASHBOARD', 'لوحة معلومات الجامعة'),
        ('CUSTOM_REPORT', 'تقرير مخصص'),
    ]
    
    OUTPUT_FORMATS = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
        ('HTML', 'HTML'),
        ('JSON', 'JSON'),
        ('XML', 'XML'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم القالب")
    name_en = models.CharField(max_length=200, blank=True, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(verbose_name="وصف القالب")
    
    category = models.CharField(max_length=20, choices=REPORT_CATEGORIES, verbose_name="فئة التقرير")
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, verbose_name="نوع التقرير")
    
    # تصميم التقرير
    template_content = models.TextField(verbose_name="محتوى القالب")
    css_styles = models.TextField(blank=True, verbose_name="أنماط CSS")
    header_template = models.TextField(blank=True, verbose_name="قالب الرأس")
    footer_template = models.TextField(blank=True, verbose_name="قالب التذييل")
    
    # إعدادات التقرير
    default_format = models.CharField(max_length=10, choices=OUTPUT_FORMATS, 
                                    default='PDF', verbose_name="التنسيق الافتراضي")
    supported_formats = models.JSONField(default=list, verbose_name="التنسيقات المدعومة")
    
    # معايير التصدير
    page_size = models.CharField(max_length=10, choices=[
        ('A4', 'A4'),
        ('A3', 'A3'),
        ('LETTER', 'Letter'),
        ('LEGAL', 'Legal'),
    ], default='A4', verbose_name="حجم الصفحة")
    orientation = models.CharField(max_length=10, choices=[
        ('PORTRAIT', 'عمودي'),
        ('LANDSCAPE', 'أفقي'),
    ], default='PORTRAIT', verbose_name="اتجاه الصفحة")
    
    # الحقول والمعاملات
    required_parameters = models.JSONField(default=list, verbose_name="المعاملات المطلوبة")
    optional_parameters = models.JSONField(default=list, verbose_name="المعاملات الاختيارية")
    data_sources = models.JSONField(default=list, verbose_name="مصادر البيانات")
    
    # إعدادات الوصول
    is_public = models.BooleanField(default=False, verbose_name="عام")
    allowed_roles = models.JSONField(default=list, verbose_name="الأدوار المسموحة")
    
    # معلومات الإنشاء
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_templates', verbose_name="أنشئ بواسطة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    version = models.CharField(max_length=10, default="1.0", verbose_name="الإصدار")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "قالب تقرير"
        verbose_name_plural = "قوالب التقارير"
        ordering = ['category', 'name']
        unique_together = ['name', 'version']
    
    def __str__(self):
        return f"{self.name} (v{self.version})"

class ReportRequest(models.Model):
    """طلبات التقارير"""
    
    STATUS_CHOICES = [
        ('PENDING', 'في الانتظار'),
        ('PROCESSING', 'قيد المعالجة'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'فاشل'),
        ('CANCELLED', 'ملغي'),
        ('EXPIRED', 'منتهي الصلاحية'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('NORMAL', 'عادي'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]
    
    request_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف الطلب")
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE,
                               related_name='requests', verbose_name="قالب التقرير")
    
    # معلومات الطالب
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='report_requests', verbose_name="طلب بواسطة")
    title = models.CharField(max_length=200, verbose_name="عنوان التقرير")
    description = models.TextField(blank=True, verbose_name="وصف الطلب")
    
    # معاملات التقرير
    parameters = models.JSONField(default=dict, verbose_name="المعاملات")
    filters = models.JSONField(default=dict, verbose_name="المرشحات")
    sorting = models.JSONField(default=dict, verbose_name="الترتيب")
    
    # إعدادات الإخراج
    output_format = models.CharField(max_length=10, choices=ReportTemplate.OUTPUT_FORMATS,
                                   verbose_name="تنسيق الإخراج")
    include_charts = models.BooleanField(default=False, verbose_name="تضمين الرسوم البيانية")
    include_summary = models.BooleanField(default=True, verbose_name="تضمين الملخص")
    
    # معلومات المعالجة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="حالة الطلب")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='NORMAL',
                              verbose_name="الأولوية")
    
    # الجدولة
    schedule_type = models.CharField(max_length=20, choices=[
        ('IMMEDIATE', 'فوري'),
        ('SCHEDULED', 'مجدول'),
        ('RECURRING', 'متكرر'),
    ], default='IMMEDIATE', verbose_name="نوع الجدولة")
    
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="مجدول في")
    recurrence_pattern = models.JSONField(default=dict, blank=True, verbose_name="نمط التكرار")
    
    # نتائج المعالجة
    processing_started_at = models.DateTimeField(null=True, blank=True, verbose_name="بدء المعالجة")
    processing_completed_at = models.DateTimeField(null=True, blank=True, verbose_name="انتهاء المعالجة")
    processing_duration = models.DurationField(null=True, blank=True, verbose_name="مدة المعالجة")
    
    # الملف المولد
    generated_file = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True,
                                    verbose_name="الملف المولد")
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="حجم الملف")
    download_count = models.IntegerField(default=0, verbose_name="عدد التحميلات")
    
    # معلومات الخطأ
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    error_details = models.JSONField(default=dict, blank=True, verbose_name="تفاصيل الخطأ")
    
    # إعدادات الانتهاء
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")
    auto_delete = models.BooleanField(default=True, verbose_name="حذف تلقائي")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "طلب تقرير"
        verbose_name_plural = "طلبات التقارير"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.requested_by.username}"
    
    @property
    def is_ready(self):
        """فحص جاهزية التقرير للتحميل"""
        return self.status == 'COMPLETED' and self.generated_file
    
    @property
    def is_expired(self):
        """فحص انتهاء صلاحية التقرير"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class ReportSchedule(models.Model):
    """جدولة التقارير المتكررة"""
    
    FREQUENCY_TYPES = [
        ('DAILY', 'يومي'),
        ('WEEKLY', 'أسبوعي'),
        ('MONTHLY', 'شهري'),
        ('QUARTERLY', 'ربع سنوي'),
        ('YEARLY', 'سنوي'),
        ('CUSTOM', 'مخصص'),
    ]
    
    WEEKDAYS = [
        ('MONDAY', 'الاثنين'),
        ('TUESDAY', 'الثلاثاء'),
        ('WEDNESDAY', 'الأربعاء'),
        ('THURSDAY', 'الخميس'),
        ('FRIDAY', 'الجمعة'),
        ('SATURDAY', 'السبت'),
        ('SUNDAY', 'الأحد'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم الجدولة")
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE,
                               related_name='schedules', verbose_name="قالب التقرير")
    
    # إعدادات الجدولة
    frequency = models.CharField(max_length=20, choices=FREQUENCY_TYPES, verbose_name="التكرار")
    interval = models.IntegerField(default=1, validators=[MinValueValidator(1)],
                                 verbose_name="الفترة")
    
    # إعدادات التوقيت
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النهاية")
    time_of_day = models.TimeField(verbose_name="وقت التنفيذ")
    
    # إعدادات أسبوعية
    weekdays = models.JSONField(default=list, blank=True, verbose_name="أيام الأسبوع")
    
    # إعدادات شهرية
    day_of_month = models.IntegerField(null=True, blank=True,
                                     validators=[MinValueValidator(1), MaxValueValidator(31)],
                                     verbose_name="يوم من الشهر")
    
    # معاملات ثابتة
    default_parameters = models.JSONField(default=dict, verbose_name="المعاملات الافتراضية")
    output_format = models.CharField(max_length=10, choices=ReportTemplate.OUTPUT_FORMATS,
                                   default='PDF', verbose_name="تنسيق الإخراج")
    
    # المستلمون
    recipients = models.ManyToManyField(User, related_name='scheduled_reports',
                                      verbose_name="المستلمون")
    email_subject = models.CharField(max_length=200, blank=True, verbose_name="موضوع البريد")
    email_body = models.TextField(blank=True, verbose_name="نص البريد")
    
    # إعدادات التنفيذ
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    max_retries = models.IntegerField(default=3, verbose_name="أقصى محاولات")
    retry_interval = models.IntegerField(default=60, verbose_name="فترة إعادة المحاولة (دقيقة)")
    
    # معلومات آخر تنفيذ
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="آخر تنفيذ")
    next_run = models.DateTimeField(verbose_name="التنفيذ التالي")
    run_count = models.IntegerField(default=0, verbose_name="عدد مرات التنفيذ")
    success_count = models.IntegerField(default=0, verbose_name="مرات النجاح")
    failure_count = models.IntegerField(default=0, verbose_name="مرات الفشل")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='created_schedules', verbose_name="أنشئ بواسطة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "جدولة تقرير"
        verbose_name_plural = "جدولة التقارير"
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"

class ReportAnalytics(models.Model):
    """تحليلات استخدام التقارير"""
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE,
                               related_name='analytics', verbose_name="قالب التقرير")
    
    # إحصائيات الاستخدام
    total_requests = models.IntegerField(default=0, verbose_name="إجمالي الطلبات")
    successful_requests = models.IntegerField(default=0, verbose_name="الطلبات الناجحة")
    failed_requests = models.IntegerField(default=0, verbose_name="الطلبات الفاشلة")
    
    # معدلات الأداء
    average_processing_time = models.DurationField(null=True, blank=True,
                                                 verbose_name="متوسط وقت المعالجة")
    total_processing_time = models.DurationField(null=True, blank=True,
                                               verbose_name="إجمالي وقت المعالجة")
    
    # إحصائيات التحميل
    total_downloads = models.IntegerField(default=0, verbose_name="إجمالي التحميلات")
    total_file_size = models.BigIntegerField(default=0, verbose_name="إجمالي حجم الملفات")
    
    # توزيع الاستخدام
    usage_by_role = models.JSONField(default=dict, verbose_name="الاستخدام حسب الدور")
    usage_by_format = models.JSONField(default=dict, verbose_name="الاستخدام حسب التنسيق")
    usage_by_month = models.JSONField(default=dict, verbose_name="الاستخدام حسب الشهر")
    
    # فترة التحليل
    period_start = models.DateTimeField(verbose_name="بداية الفترة")
    period_end = models.DateTimeField(verbose_name="نهاية الفترة")
    
    # التحديث التلقائي
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "تحليلات تقرير"
        verbose_name_plural = "تحليلات التقارير"
        unique_together = ['template', 'period_start', 'period_end']
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.template.name} - {self.period_start.date()} to {self.period_end.date()}"

class DashboardWidget(models.Model):
    """عناصر لوحة المعلومات"""
    
    WIDGET_TYPES = [
        ('CHART', 'رسم بياني'),
        ('METRIC', 'مقياس'),
        ('TABLE', 'جدول'),
        ('GAUGE', 'مقياس دائري'),
        ('PROGRESS', 'شريط تقدم'),
        ('MAP', 'خريطة'),
        ('TEXT', 'نص'),
        ('IFRAME', 'إطار مضمن'),
    ]
    
    CHART_TYPES = [
        ('LINE', 'خطي'),
        ('BAR', 'أعمدة'),
        ('PIE', 'دائري'),
        ('DOUGHNUT', 'حلقي'),
        ('AREA', 'منطقة'),
        ('SCATTER', 'نثر'),
        ('RADAR', 'رادار'),
    ]
    
    DATA_SOURCES = [
        ('DATABASE', 'قاعدة البيانات'),
        ('API', 'واجهة برمجية'),
        ('STATIC', 'ثابت'),
        ('CALCULATED', 'محسوب'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم العنصر")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(blank=True, verbose_name="الوصف")
    
    # نوع العنصر
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name="نوع العنصر")
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True,
                                verbose_name="نوع الرسم البياني")
    
    # مصدر البيانات
    data_source = models.CharField(max_length=20, choices=DATA_SOURCES, verbose_name="مصدر البيانات")
    query = models.TextField(blank=True, verbose_name="الاستعلام")
    api_endpoint = models.URLField(blank=True, verbose_name="نقطة نهاية API")
    static_data = models.JSONField(default=dict, blank=True, verbose_name="البيانات الثابتة")
    
    # إعدادات العرض
    width = models.IntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(12)],
                              verbose_name="العرض (1-12)")
    height = models.IntegerField(default=300, verbose_name="الارتفاع (بكسل)")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    
    # إعدادات التنسيق
    color_scheme = models.JSONField(default=list, verbose_name="مخطط الألوان")
    custom_css = models.TextField(blank=True, verbose_name="CSS مخصص")
    
    # إعدادات التحديث
    auto_refresh = models.BooleanField(default=False, verbose_name="تحديث تلقائي")
    refresh_interval = models.IntegerField(default=300, verbose_name="فترة التحديث (ثانية)")
    
    # صلاحيات الوصول
    is_public = models.BooleanField(default=False, verbose_name="عام")
    allowed_roles = models.JSONField(default=list, verbose_name="الأدوار المسموحة")
    
    # معلومات الإنشاء
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='created_widgets', verbose_name="أنشئ بواسطة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "عنصر لوحة معلومات"
        verbose_name_plural = "عناصر لوحة المعلومات"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"

class Dashboard(models.Model):
    """لوحات المعلومات المخصصة"""
    
    DASHBOARD_TYPES = [
        ('EXECUTIVE', 'تنفيذي'),
        ('ACADEMIC', 'أكاديمي'),
        ('FINANCIAL', 'مالي'),
        ('OPERATIONAL', 'تشغيلي'),
        ('STUDENT', 'طلابي'),
        ('TEACHER', 'أعضاء هيئة التدريس'),
        ('DEPARTMENT', 'القسم'),
        ('CUSTOM', 'مخصص'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم لوحة المعلومات")
    description = models.TextField(blank=True, verbose_name="الوصف")
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_TYPES,
                                    verbose_name="نوع لوحة المعلومات")
    
    # العناصر المتضمنة
    widgets = models.ManyToManyField(DashboardWidget, through='DashboardWidgetOrder',
                                   verbose_name="العناصر")
    
    # إعدادات العرض
    layout = models.CharField(max_length=20, choices=[
        ('GRID', 'شبكة'),
        ('MASONRY', 'بناء'),
        ('TABS', 'تبويبات'),
        ('ACCORDION', 'أكورديون'),
    ], default='GRID', verbose_name="تخطيط العرض")
    
    theme = models.CharField(max_length=20, choices=[
        ('LIGHT', 'فاتح'),
        ('DARK', 'مظلم'),
        ('AUTO', 'تلقائي'),
    ], default='AUTO', verbose_name="السمة")
    
    # صلاحيات الوصول
    is_public = models.BooleanField(default=False, verbose_name="عام")
    allowed_users = models.ManyToManyField(User, blank=True, related_name='accessible_dashboards',
                                         verbose_name="المستخدمون المسموحون")
    allowed_roles = models.JSONField(default=list, verbose_name="الأدوار المسموحة")
    
    # إعدادات أخرى
    is_default = models.BooleanField(default=False, verbose_name="افتراضي")
    auto_refresh = models.BooleanField(default=True, verbose_name="تحديث تلقائي")
    refresh_interval = models.IntegerField(default=300, verbose_name="فترة التحديث (ثانية)")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='created_dashboards', verbose_name="أنشئ بواسطة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "لوحة معلومات"
        verbose_name_plural = "لوحات المعلومات"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"

class DashboardWidgetOrder(models.Model):
    """ترتيب عناصر لوحة المعلومات"""
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    
    # إعدادات الموضع
    row = models.IntegerField(default=0, verbose_name="الصف")
    column = models.IntegerField(default=0, verbose_name="العمود")
    width = models.IntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(12)],
                              verbose_name="العرض")
    height = models.IntegerField(null=True, blank=True, verbose_name="الارتفاع المخصص")
    
    # إعدادات إضافية
    is_visible = models.BooleanField(default=True, verbose_name="مرئي")
    custom_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان مخصص")
    
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    
    class Meta:
        verbose_name = "ترتيب عنصر لوحة المعلومات"
        verbose_name_plural = "ترتيب عناصر لوحة المعلومات"
        ordering = ['order']
        unique_together = ['dashboard', 'widget']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.widget.name}"

class ReportExportLog(models.Model):
    """سجل تصدير التقارير"""
    
    request = models.ForeignKey(ReportRequest, on_delete=models.CASCADE,
                              related_name='export_logs', verbose_name="طلب التقرير")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='report_exports', verbose_name="المستخدم")
    
    # معلومات التصدير
    export_format = models.CharField(max_length=10, verbose_name="تنسيق التصدير")
    file_name = models.CharField(max_length=255, verbose_name="اسم الملف")
    file_size = models.BigIntegerField(verbose_name="حجم الملف")
    
    # معلومات الوصول
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="معرف المتصفح")
    
    # معلومات التحميل
    download_method = models.CharField(max_length=20, choices=[
        ('DIRECT', 'مباشر'),
        ('EMAIL', 'بريد إلكتروني'),
        ('LINK', 'رابط'),
    ], verbose_name="طريقة التحميل")
    
    # التوقيت
    exported_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت التصدير")
    
    class Meta:
        verbose_name = "سجل تصدير"
        verbose_name_plural = "سجلات التصدير"
        ordering = ['-exported_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.file_name}"