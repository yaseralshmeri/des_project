# نظام الإدارة المالية المتقدم للجامعة
# Advanced University Financial Management System

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

class AcademicYear(models.Model):
    """السنة الأكاديمية المالية"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.CharField(max_length=9, unique=True, verbose_name="السنة الأكاديمية")
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    is_current = models.BooleanField(default=False, verbose_name="السنة الحالية")
    
    # الميزانية العامة
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                     verbose_name="الميزانية الإجمالية")
    allocated_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                         verbose_name="الميزانية المخصصة")
    spent_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                     verbose_name="الميزانية المُنفقة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "سنة أكاديمية مالية"
        verbose_name_plural = "السنوات الأكاديمية المالية"
        ordering = ['-year']
    
    def __str__(self):
        return self.year
    
    @property
    def remaining_budget(self):
        """الميزانية المتبقية"""
        return self.total_budget - self.spent_budget
    
    @property
    def budget_utilization_percentage(self):
        """نسبة استخدام الميزانية"""
        if self.total_budget > 0:
            return (self.spent_budget / self.total_budget) * 100
        return 0


class FeeType(models.Model):
    """أنواع الرسوم"""
    
    FEE_CATEGORIES = [
        ('TUITION', 'رسوم دراسية'),
        ('APPLICATION', 'رسوم تقديم'),
        ('REGISTRATION', 'رسوم تسجيل'),
        ('LATE_REGISTRATION', 'رسوم تسجيل متأخر'),
        ('LABORATORY', 'رسوم معامل'),
        ('LIBRARY', 'رسوم مكتبة'),
        ('ACTIVITY', 'رسوم أنشطة'),
        ('GRADUATION', 'رسوم تخرج'),
        ('TRANSCRIPT', 'رسوم كشف درجات'),
        ('CERTIFICATE', 'رسوم شهادات'),
        ('PARKING', 'رسوم مواقف'),
        ('HOUSING', 'رسوم سكن'),
        ('MEALS', 'رسوم وجبات'),
        ('MEDICAL', 'رسوم طبية'),
        ('INSURANCE', 'رسوم تأمين'),
        ('OTHER', 'رسوم أخرى'),
    ]
    
    CALCULATION_METHODS = [
        ('FIXED', 'مبلغ ثابت'),
        ('PER_CREDIT', 'لكل ساعة معتمدة'),
        ('PERCENTAGE', 'نسبة مئوية'),
        ('VARIABLE', 'متغير'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات النوع الأساسية
    name_ar = models.CharField(max_length=200, verbose_name="اسم الرسوم - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم الرسوم - إنجليزي")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز الرسوم")
    category = models.CharField(max_length=20, choices=FEE_CATEGORIES,
                              verbose_name="فئة الرسوم")
    
    # طريقة الحساب
    calculation_method = models.CharField(max_length=15, choices=CALCULATION_METHODS,
                                        default='FIXED', verbose_name="طريقة الحساب")
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                    verbose_name="المبلغ الأساسي")
    
    # إعدادات السداد
    is_mandatory = models.BooleanField(default=True, verbose_name="إلزامي")
    is_refundable = models.BooleanField(default=False, verbose_name="قابل للاسترداد")
    payment_deadline_days = models.IntegerField(default=30, verbose_name="مهلة السداد (أيام)")
    
    # قواعد التطبيق
    applies_to_new_students = models.BooleanField(default=True, verbose_name="للطلاب الجدد")
    applies_to_continuing_students = models.BooleanField(default=True, verbose_name="للطلاب المستمرين")
    applies_to_graduate_students = models.BooleanField(default=True, verbose_name="لطلاب الدراسات العليا")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    effective_from = models.DateField(default=timezone.now, verbose_name="ساري من")
    effective_until = models.DateField(null=True, blank=True, verbose_name="ساري حتى")
    
    # وصف ومعلومات إضافية
    description = models.TextField(blank=True, verbose_name="وصف الرسوم")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_fee_types', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "نوع رسوم"
        verbose_name_plural = "أنواع الرسوم"
        ordering = ['category', 'name_ar']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name_ar}"
    
    @property
    def is_currently_effective(self):
        """هل الرسوم سارية حالياً"""
        today = timezone.now().date()
        if today < self.effective_from:
            return False
        if self.effective_until and today > self.effective_until:
            return False
        return self.is_active


class StudentAccount(models.Model):
    """الحساب المالي للطالب"""
    
    ACCOUNT_STATUS = [
        ('ACTIVE', 'نشط'),
        ('SUSPENDED', 'موقوف'),
        ('CLOSED', 'مُغلق'),
        ('HOLD', 'محجوز'),
    ]
    
    CREDIT_STATUS = [
        ('GOOD', 'جيد'),
        ('WARNING', 'تحذير'),
        ('POOR', 'ضعيف'),
        ('BLOCKED', 'محظور'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الطالب والسنة الأكاديمية
    student = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='financial_account', verbose_name="الطالب")
    current_academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT,
                                            verbose_name="السنة الأكاديمية الحالية")
    
    # معلومات الحساب
    account_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الحساب")
    account_status = models.CharField(max_length=15, choices=ACCOUNT_STATUS,
                                    default='ACTIVE', verbose_name="حالة الحساب")
    
    # الأرصدة المالية
    total_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                      verbose_name="إجمالي المستحقات")
    total_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                       verbose_name="إجمالي المدفوعات")
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                        verbose_name="الرصيد الحالي")
    
    # المنح والمساعدات
    total_scholarships = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                           verbose_name="إجمالي المنح")
    total_financial_aid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                            verbose_name="إجمالي المساعدات المالية")
    total_discounts = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                        verbose_name="إجمالي الخصومات")
    
    # الحد الائتماني
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                     verbose_name="الحد الائتماني")
    credit_status = models.CharField(max_length=15, choices=CREDIT_STATUS,
                                   default='GOOD', verbose_name="الحالة الائتمانية")
    
    # تواريخ مهمة
    last_payment_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ آخر دفعة")
    next_due_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الاستحقاق التالي")
    
    # إعدادات وتفضيلات
    auto_pay_enabled = models.BooleanField(default=False, verbose_name="الدفع التلقائي مُفعل")
    payment_reminders_enabled = models.BooleanField(default=True, verbose_name="تذكيرات الدفع مُفعلة")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "حساب مالي للطالب"
        verbose_name_plural = "الحسابات المالية للطلاب"
        ordering = ['student__first_name_ar']
        indexes = [
            models.Index(fields=['account_number']),
            models.Index(fields=['account_status']),
            models.Index(fields=['current_balance']),
        ]
    
    def __str__(self):
        return f"{self.account_number} - {self.student.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        """توليد رقم حساب فريد"""
        year = timezone.now().year
        count = StudentAccount.objects.filter(
            account_number__startswith=str(year)
        ).count()
        return f"{year}{count + 1:06d}"
    
    @property
    def outstanding_balance(self):
        """الرصيد المستحق"""
        return max(self.current_balance, Decimal('0.00'))
    
    @property
    def credit_balance(self):
        """الرصيد الدائن"""
        return max(-self.current_balance, Decimal('0.00'))
    
    @property
    def net_amount_due(self):
        """صافي المبلغ المستحق"""
        return self.total_charges - self.total_payments - self.total_scholarships - self.total_financial_aid - self.total_discounts
    
    @property
    def is_in_good_standing(self):
        """هل الحساب بحالة جيدة"""
        return self.current_balance <= 0 and self.account_status == 'ACTIVE'
    
    def calculate_balance(self):
        """حساب الرصيد الحالي"""
        self.current_balance = self.net_amount_due
        self.save(update_fields=['current_balance'])


class StudentCharge(models.Model):
    """مستحقات الطالب"""
    
    CHARGE_STATUS = [
        ('PENDING', 'في الانتظار'),
        ('POSTED', 'مُرحل'),
        ('PAID', 'مدفوع'),
        ('PARTIALLY_PAID', 'مدفوع جزئياً'),
        ('CANCELLED', 'ملغي'),
        ('REFUNDED', 'مُسترد'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المستحق الأساسية
    student_account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE,
                                      related_name='charges', verbose_name="حساب الطالب")
    fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT, verbose_name="نوع الرسوم")
    
    # المبالغ
    original_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                        verbose_name="المبلغ الأصلي")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        verbose_name="مبلغ الخصم")
    final_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                     verbose_name="المبلغ النهائي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                    verbose_name="المبلغ المدفوع")
    
    # التوقيت
    charge_date = models.DateField(default=timezone.now, verbose_name="تاريخ المستحق")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT,
                                    verbose_name="السنة الأكاديمية")
    semester = models.CharField(max_length=20, verbose_name="الفصل الدراسي")
    
    # الحالة والتتبع
    status = models.CharField(max_length=20, choices=CHARGE_STATUS, default='PENDING',
                            verbose_name="الحالة")
    reference_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المرجع")
    
    # معلومات إضافية
    description = models.TextField(blank=True, verbose_name="وصف المستحق")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # التفاصيل المرتبطة
    course_offering = models.ForeignKey('courses.CourseOffering', on_delete=models.SET_NULL,
                                      null=True, blank=True, verbose_name="عرض المقرر")
    
    # معلومات المعالجة
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='posted_charges', verbose_name="رُحل بواسطة")
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الترحيل")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "مستحق طالب"
        verbose_name_plural = "مستحقات الطلاب"
        ordering = ['-charge_date', '-created_at']
        indexes = [
            models.Index(fields=['student_account', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['academic_year', 'semester']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.student_account.student.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        
        # حساب المبلغ النهائي
        self.final_amount = self.original_amount - self.discount_amount
        
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        """توليد رقم مرجع فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"CHG-{timestamp}"
    
    @property
    def remaining_amount(self):
        """المبلغ المتبقي"""
        return self.final_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """هل المستحق متأخر"""
        return timezone.now().date() > self.due_date and self.status not in ['PAID', 'CANCELLED', 'REFUNDED']
    
    @property
    def days_overdue(self):
        """عدد أيام التأخير"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0


class Payment(models.Model):
    """المدفوعات"""
    
    PAYMENT_METHODS = [
        ('CASH', 'نقداً'),
        ('CREDIT_CARD', 'بطاقة ائتمان'),
        ('DEBIT_CARD', 'بطاقة خصم'),
        ('BANK_TRANSFER', 'تحويل بنكي'),
        ('ONLINE_PAYMENT', 'دفع إلكتروني'),
        ('CHECK', 'شيك'),
        ('SCHOLARSHIP', 'منحة دراسية'),
        ('FINANCIAL_AID', 'مساعدة مالية'),
        ('OTHER', 'أخرى'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'في الانتظار'),
        ('PROCESSING', 'قيد المعالجة'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'فاشل'),
        ('CANCELLED', 'ملغي'),
        ('REFUNDED', 'مُسترد'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الدفعة الأساسية
    student_account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE,
                                      related_name='payments', verbose_name="حساب الطالب")
    payment_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الدفعة")
    
    # المبلغ وطريقة الدفع
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS,
                                    verbose_name="طريقة الدفع")
    
    # التوقيت
    payment_date = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الدفع")
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المعالجة")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT,
                                    verbose_name="السنة الأكاديمية")
    
    # الحالة والمعالجة
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='PENDING',
                            verbose_name="الحالة")
    
    # تفاصيل الدفع
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="معرف المعاملة")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="رقم المرجع")
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="اسم البنك")
    check_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الشيك")
    
    # معلومات إضافية
    description = models.TextField(blank=True, verbose_name="وصف الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # المعالجة والموافقة
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='processed_payments',
                                   verbose_name="عولج بواسطة")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_payments',
                                  verbose_name="وافق عليه")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "المدفوعات"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student_account', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['payment_number']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)
    
    def generate_payment_number(self):
        """توليد رقم دفعة فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"PAY-{timestamp}"


class PaymentAllocation(models.Model):
    """توزيع الدفعات على المستحقات"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE,
                              related_name='allocations', verbose_name="الدفعة")
    charge = models.ForeignKey(StudentCharge, on_delete=models.CASCADE,
                             related_name='payment_allocations', verbose_name="المستحق")
    
    # المبلغ المخصص
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                         verbose_name="المبلغ المخصص")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "توزيع دفعة"
        verbose_name_plural = "توزيعات الدفعات"
        unique_together = ['payment', 'charge']
        indexes = [
            models.Index(fields=['payment']),
            models.Index(fields=['charge']),
        ]
    
    def __str__(self):
        return f"{self.payment.payment_number} -> {self.charge.reference_number}"


class Scholarship(models.Model):
    """المنح الدراسية"""
    
    SCHOLARSHIP_TYPES = [
        ('FULL_TUITION', 'منحة كاملة للرسوم الدراسية'),
        ('PARTIAL_TUITION', 'منحة جزئية للرسوم الدراسية'),
        ('NEED_BASED', 'منحة على أساس الحاجة'),
        ('MERIT_BASED', 'منحة على أساس الجدارة'),
        ('ATHLETIC', 'منحة رياضية'),
        ('ACADEMIC_EXCELLENCE', 'منحة التفوق الأكاديمي'),
        ('RESEARCH', 'منحة بحثية'),
        ('INTERNATIONAL', 'منحة دولية'),
        ('EMPLOYEE_DEPENDENT', 'منحة أبناء الموظفين'),
        ('OTHER', 'أخرى'),
    ]
    
    FUNDING_SOURCES = [
        ('UNIVERSITY', 'الجامعة'),
        ('GOVERNMENT', 'حكومية'),
        ('PRIVATE_DONOR', 'متبرع خاص'),
        ('FOUNDATION', 'مؤسسة'),
        ('CORPORATE', 'شركة'),
        ('INTERNATIONAL', 'دولية'),
        ('OTHER', 'أخرى'),
    ]
    
    SCHOLARSHIP_STATUS = [
        ('ACTIVE', 'نشطة'),
        ('SUSPENDED', 'موقوفة'),
        ('TERMINATED', 'منتهية'),
        ('COMPLETED', 'مكتملة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المنحة الأساسية
    name_ar = models.CharField(max_length=200, verbose_name="اسم المنحة - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم المنحة - إنجليزي")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز المنحة")
    
    # نوع ومصدر المنحة
    scholarship_type = models.CharField(max_length=30, choices=SCHOLARSHIP_TYPES,
                                      verbose_name="نوع المنحة")
    funding_source = models.CharField(max_length=20, choices=FUNDING_SOURCES,
                                    verbose_name="مصدر التمويل")
    
    # التمويل
    total_budget = models.DecimalField(max_digits=15, decimal_places=2,
                                     verbose_name="الميزانية الإجمالية")
    allocated_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                         verbose_name="الميزانية المخصصة")
    
    # معايير الأهلية
    min_gpa = models.DecimalField(max_digits=4, decimal_places=3, default=0.000,
                                validators=[MinValueValidator(0), MaxValueValidator(4)],
                                verbose_name="الحد الأدنى للمعدل")
    max_family_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                          verbose_name="الحد الأقصى لدخل الأسرة")
    
    # شروط أخرى
    requires_financial_need = models.BooleanField(default=False, verbose_name="يتطلب حاجة مالية")
    requires_community_service = models.BooleanField(default=False, verbose_name="يتطلب خدمة مجتمعية")
    renewable = models.BooleanField(default=True, verbose_name="قابلة للتجديد")
    
    # التوقيت
    application_start_date = models.DateField(verbose_name="تاريخ بداية التقديم")
    application_end_date = models.DateField(verbose_name="تاريخ نهاية التقديم")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT,
                                    verbose_name="السنة الأكاديمية")
    
    # الحالة
    status = models.CharField(max_length=15, choices=SCHOLARSHIP_STATUS, default='ACTIVE',
                            verbose_name="حالة المنحة")
    
    # وصف ومعلومات إضافية
    description = models.TextField(verbose_name="وصف المنحة")
    requirements = models.TextField(verbose_name="المتطلبات")
    benefits = models.TextField(verbose_name="المزايا")
    
    # معلومات الاتصال
    contact_person = models.CharField(max_length=200, blank=True, verbose_name="جهة الاتصال")
    contact_email = models.EmailField(blank=True, verbose_name="بريد جهة الاتصال")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_scholarships',
                                 verbose_name="أُنشأت بواسطة")
    
    class Meta:
        verbose_name = "منحة دراسية"
        verbose_name_plural = "المنح الدراسية"
        ordering = ['name_ar']
        indexes = [
            models.Index(fields=['scholarship_type', 'status']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name_ar}"
    
    @property
    def remaining_budget(self):
        """الميزانية المتبقية"""
        return self.total_budget - self.allocated_budget
    
    @property
    def is_application_open(self):
        """هل التقديم مفتوح"""
        today = timezone.now().date()
        return (self.application_start_date <= today <= self.application_end_date and 
                self.status == 'ACTIVE')


class ScholarshipApplication(models.Model):
    """طلبات المنح الدراسية"""
    
    APPLICATION_STATUS = [
        ('SUBMITTED', 'مقدم'),
        ('UNDER_REVIEW', 'قيد المراجعة'),
        ('APPROVED', 'موافق عليه'),
        ('REJECTED', 'مرفوض'),
        ('WAITLISTED', 'في قائمة الانتظار'),
        ('WITHDRAWN', 'منسحب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الطلب الأساسية
    application_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الطلب")
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='scholarship_applications', verbose_name="الطالب")
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE,
                                  related_name='applications', verbose_name="المنحة")
    
    # تواريخ مهمة
    submitted_date = models.DateTimeField(default=timezone.now, verbose_name="تاريخ التقديم")
    review_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    decision_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ القرار")
    
    # الحالة والقرار
    status = models.CharField(max_length=15, choices=APPLICATION_STATUS, default='SUBMITTED',
                            verbose_name="حالة الطلب")
    
    # معلومات الطالب المالية
    family_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                      verbose_name="دخل الأسرة")
    current_gpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                    verbose_name="المعدل الحالي")
    
    # المبلغ المطلوب والممنوح
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                         verbose_name="المبلغ المطلوب")
    awarded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                       verbose_name="المبلغ الممنوح")
    
    # المستندات المطلوبة
    documents_uploaded = models.JSONField(default=list, verbose_name="المستندات المرفوعة")
    
    # المراجعة والقرار
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='reviewed_scholarship_applications',
                                  verbose_name="راجعه")
    reviewer_comments = models.TextField(blank=True, verbose_name="تعليقات المراجع")
    decision_reason = models.TextField(blank=True, verbose_name="سبب القرار")
    
    # معلومات إضافية
    essay = models.TextField(blank=True, verbose_name="مقال الطالب")
    extracurricular_activities = models.TextField(blank=True, verbose_name="الأنشطة اللامنهجية")
    community_service_hours = models.IntegerField(default=0, verbose_name="ساعات الخدمة المجتمعية")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "طلب منحة دراسية"
        verbose_name_plural = "طلبات المنح الدراسية"
        ordering = ['-submitted_date']
        unique_together = ['student', 'scholarship']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['submitted_date']),
            models.Index(fields=['application_number']),
        ]
    
    def __str__(self):
        return f"{self.application_number} - {self.student.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = self.generate_application_number()
        super().save(*args, **kwargs)
    
    def generate_application_number(self):
        """توليد رقم طلب فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"SCHAPP-{timestamp}"


class FinancialReport(models.Model):
    """التقارير المالية"""
    
    REPORT_TYPES = [
        ('DAILY', 'تقرير يومي'),
        ('WEEKLY', 'تقرير أسبوعي'),
        ('MONTHLY', 'تقرير شهري'),
        ('QUARTERLY', 'تقرير ربع سنوي'),
        ('ANNUAL', 'تقرير سنوي'),
        ('CUSTOM', 'تقرير مخصص'),
    ]
    
    REPORT_STATUS = [
        ('GENERATING', 'قيد الإنتاج'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'فاشل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات التقرير
    report_name = models.CharField(max_length=200, verbose_name="اسم التقرير")
    report_type = models.CharField(max_length=15, choices=REPORT_TYPES,
                                 verbose_name="نوع التقرير")
    
    # فترة التقرير
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                    verbose_name="السنة الأكاديمية")
    
    # البيانات المالية
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                      verbose_name="إجمالي الإيرادات")
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                       verbose_name="إجمالي المصروفات")
    net_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                   verbose_name="صافي الدخل")
    
    # تفاصيل إضافية
    report_data = models.JSONField(default=dict, verbose_name="بيانات التقرير")
    
    # الحالة والملف
    status = models.CharField(max_length=15, choices=REPORT_STATUS, default='GENERATING',
                            verbose_name="حالة التقرير")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الملف")
    
    # معلومات الإنتاج
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='generated_financial_reports',
                                   verbose_name="أُنتج بواسطة")
    generated_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإنتاج")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تقرير مالي"
        verbose_name_plural = "التقارير المالية"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'academic_year']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.report_name} - {self.academic_year.year}"
    
    @property
    def profit_margin(self):
        """هامش الربح"""
        if self.total_revenue > 0:
            return (self.net_income / self.total_revenue) * 100
        return 0# إضافة النماذج المفقودة لتطبيق Finance

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

# سأحتاج لاستيراد النماذج من التطبيقات الأخرى
# from courses.models import Major, Semester, Course
# from students.models import StudentProfile

class FeeStructure(models.Model):
    """هيكل الرسوم الجامعية"""
    
    PROGRAM_TYPES = [
        ('UNDERGRADUATE', 'بكالوريوس'),
        ('GRADUATE', 'دراسات عليا'),
        ('DIPLOMA', 'دبلوم'),
        ('CERTIFICATE', 'شهادة'),
    ]
    
    STUDENT_TYPES = [
        ('REGULAR', 'نظامي'),
        ('PART_TIME', 'جزئي'),
        ('DISTANCE', 'تعليم عن بُعد'),
        ('INTERNATIONAL', 'دولي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الهيكل
    name_ar = models.CharField(max_length=200, verbose_name="اسم هيكل الرسوم - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم هيكل الرسوم - إنجليزي")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز الهيكل")
    
    # التصنيف
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES,
                                  verbose_name="نوع البرنامج")
    student_type = models.CharField(max_length=15, choices=STUDENT_TYPES,
                                  default='REGULAR', verbose_name="نوع الطالب")
    
    # الرسوم الأساسية
    tuition_fee_per_credit = models.DecimalField(max_digits=8, decimal_places=2,
                                               verbose_name="رسوم الساعة المعتمدة")
    registration_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                         verbose_name="رسوم التسجيل")
    activity_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                     verbose_name="رسوم الأنشطة")
    lab_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                verbose_name="رسوم المختبرات")
    
    # رسوم إضافية
    library_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                    verbose_name="رسوم المكتبة")
    medical_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                    verbose_name="رسوم طبية")
    insurance_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                      verbose_name="رسوم تأمين")
    
    # فترة السريان
    effective_from = models.DateField(verbose_name="سارية من")
    effective_to = models.DateField(null=True, blank=True, verbose_name="سارية حتى")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_fee_structures',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "هيكل رسوم"
        verbose_name_plural = "هياكل الرسوم"
        ordering = ['program_type', 'student_type', '-effective_from']
        indexes = [
            models.Index(fields=['program_type', 'student_type', 'is_active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} - {self.get_program_type_display()}"
    
    @property
    def is_current(self):
        """فحص إذا كان الهيكل ساري حالياً"""
        today = timezone.now().date()
        if self.effective_to:
            return self.effective_from <= today <= self.effective_to
        return self.effective_from <= today


class StudentFee(models.Model):
    """رسوم الطلاب"""
    
    STATUS_CHOICES = [
        ('PENDING', 'معلق'),
        ('PARTIAL', 'دُفع جزئياً'),
        ('PAID', 'مدفوع'),
        ('OVERDUE', 'متأخر'),
        ('WAIVED', 'معفى'),
        ('CANCELLED', 'ملغي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ربط بالطالب والفصل
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='student_fees', verbose_name="الطالب")
    # semester = models.ForeignKey('courses.Semester', on_delete=models.CASCADE,
    #                            related_name='student_fees', verbose_name="الفصل الدراسي")
    academic_year = models.CharField(max_length=9, verbose_name="السنة الأكاديمية")
    semester = models.CharField(max_length=20, verbose_name="الفصل الدراسي")
    
    # هيكل الرسوم المطبق
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT,
                                    related_name='student_fees', verbose_name="هيكل الرسوم")
    
    # تفاصيل الرسوم
    total_credit_hours = models.IntegerField(default=0, verbose_name="إجمالي الساعات المعتمدة")
    tuition_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                       verbose_name="مبلغ الرسوم الدراسية")
    additional_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        verbose_name="الرسوم الإضافية")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                     verbose_name="إجمالي المبلغ")
    
    # المدفوعات
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                    verbose_name="المبلغ المدفوع")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        verbose_name="مبلغ الخصم")
    
    # المواعيد
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    payment_deadline = models.DateField(null=True, blank=True,
                                      verbose_name="آخر موعد للدفع")
    
    # الحالة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="حالة الدفع")
    is_installment_allowed = models.BooleanField(default=True, verbose_name="السماح بالتقسيط")
    
    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_student_fees',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "رسوم طالب"
        verbose_name_plural = "رسوم الطلاب"
        ordering = ['-academic_year', 'semester', 'student__first_name']
        unique_together = ['student', 'academic_year', 'semester']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['academic_year', 'semester']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.academic_year} {self.semester}"
    
    @property
    def remaining_amount(self):
        """المبلغ المتبقي"""
        return self.total_amount - self.paid_amount - self.discount_amount
    
    @property
    def is_overdue(self):
        """فحص التأخير في السداد"""
        return self.due_date < timezone.now().date() and self.status != 'PAID'
    
    @property
    def payment_percentage(self):
        """نسبة الدفع"""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0


class Payment(models.Model):
    """المدفوعات"""
    
    PAYMENT_METHODS = [
        ('CASH', 'نقدي'),
        ('BANK_TRANSFER', 'تحويل بنكي'),
        ('CREDIT_CARD', 'بطاقة ائتمان'),
        ('DEBIT_CARD', 'بطاقة خصم'),
        ('CHEQUE', 'شيك'),
        ('ONLINE', 'دفع إلكتروني'),
        ('MOBILE_PAYMENT', 'دفع جوال'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'معلق'),
        ('PROCESSING', 'قيد المعالجة'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'فاشل'),
        ('CANCELLED', 'ملغي'),
        ('REFUNDED', 'مُسترد'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ربط بالطالب والرسوم
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='payments', verbose_name="الطالب")
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE,
                                  related_name='payments', verbose_name="رسوم الطالب")
    
    # تفاصيل الدفع
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               verbose_name="مبلغ الدفع")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS,
                                    verbose_name="طريقة الدفع")
    
    # معلومات المعاملة
    transaction_id = models.CharField(max_length=100, unique=True,
                                    verbose_name="رقم المعاملة")
    reference_number = models.CharField(max_length=100, blank=True,
                                      verbose_name="الرقم المرجعي")
    
    # التوقيتات
    payment_date = models.DateTimeField(verbose_name="تاريخ الدفع")
    processed_date = models.DateTimeField(null=True, blank=True,
                                        verbose_name="تاريخ المعالجة")
    
    # الحالة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="حالة الدفع")
    
    # معلومات إضافية
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    receipt_number = models.CharField(max_length=50, blank=True,
                                    verbose_name="رقم الإيصال")
    
    # معلومات البنك (في حالة التحويل البنكي)
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="اسم البنك")
    bank_reference = models.CharField(max_length=100, blank=True,
                                    verbose_name="مرجع البنك")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='processed_payments',
                                   verbose_name="معالج بواسطة")
    
    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "المدفوعات"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['student_fee', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.amount} - {self.payment_date.strftime('%Y-%m-%d')}"


class Scholarship(models.Model):
    """المنح الدراسية"""
    
    SCHOLARSHIP_TYPES = [
        ('FULL', 'منحة كاملة'),
        ('PARTIAL', 'منحة جزئية'),
        ('MERIT', 'منحة تفوق'),
        ('NEED_BASED', 'منحة حاجة'),
        ('SPORTS', 'منحة رياضية'),
        ('RESEARCH', 'منحة بحثية'),
        ('EMPLOYEE', 'منحة موظفين'),
        ('DISABLED', 'منحة ذوي الاحتياجات'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشطة'),
        ('SUSPENDED', 'معلقة'),
        ('CANCELLED', 'ملغية'),
        ('COMPLETED', 'مكتملة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المنحة
    name_ar = models.CharField(max_length=200, verbose_name="اسم المنحة - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم المنحة - إنجليزي")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز المنحة")
    
    # نوع المنحة
    scholarship_type = models.CharField(max_length=15, choices=SCHOLARSHIP_TYPES,
                                      verbose_name="نوع المنحة")
    
    # قيمة المنحة
    coverage_percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                                            verbose_name="نسبة التغطية %")
    max_amount_per_semester = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                                verbose_name="الحد الأقصى للمبلغ لكل فصل")
    max_total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name="الحد الأقصى للمبلغ الإجمالي")
    
    # شروط الاستحقاق
    min_gpa_requirement = models.DecimalField(max_digits=4, decimal_places=3, default=0.000,
                                            verbose_name="الحد الأدنى للمعدل المطلوب")
    max_family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name="الحد الأقصى لدخل الأسرة")
    
    # فترة المنحة
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    max_duration_semesters = models.IntegerField(default=8, verbose_name="الحد الأقصى للفصول")
    
    # العدد والحصص
    total_slots = models.IntegerField(default=10, verbose_name="إجمالي المقاعد")
    available_slots = models.IntegerField(default=10, verbose_name="المقاعد المتاحة")
    
    # الوصف والشروط
    description = models.TextField(verbose_name="وصف المنحة")
    eligibility_criteria = models.TextField(verbose_name="معايير الاستحقاق")
    required_documents = models.TextField(blank=True, verbose_name="المستندات المطلوبة")
    
    # الحالة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="حالة المنحة")
    is_renewable = models.BooleanField(default=True, verbose_name="قابلة للتجديد")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_scholarships',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "منحة دراسية"
        verbose_name_plural = "المنح الدراسية"
        ordering = ['name_ar']
        indexes = [
            models.Index(fields=['scholarship_type', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} ({self.coverage_percentage}%)"
    
    @property
    def is_active(self):
        """فحص إذا كانت المنحة نشطة"""
        today = timezone.now().date()
        return (self.status == 'ACTIVE' and 
                self.start_date <= today <= self.end_date and 
                self.available_slots > 0)


class ScholarshipApplication(models.Model):
    """طلبات المنح الدراسية"""
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'مُقدم'),
        ('UNDER_REVIEW', 'قيد المراجعة'),
        ('APPROVED', 'موافق عليه'),
        ('REJECTED', 'مرفوض'),
        ('WAITLISTED', 'قائمة انتظار'),
        ('WITHDRAWN', 'منسحب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ربط بالطالب والمنحة
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='scholarship_applications',
                              verbose_name="الطالب")
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE,
                                  related_name='applications',
                                  verbose_name="المنحة")
    
    # معلومات الطلب
    application_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقديم")
    academic_year = models.CharField(max_length=9, verbose_name="السنة الأكاديمية")
    
    # المعلومات الأكاديمية
    current_gpa = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="المعدل الحالي")
    total_credit_hours = models.IntegerField(verbose_name="إجمالي الساعات المُنجزة")
    
    # المعلومات المالية
    family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                      verbose_name="دخل الأسرة")
    financial_need_statement = models.TextField(blank=True, verbose_name="بيان الحاجة المالية")
    
    # المستندات
    supporting_documents = models.JSONField(default=list, verbose_name="المستندات المؤيدة")
    
    # حالة الطلب
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUBMITTED',
                            verbose_name="حالة الطلب")
    review_comments = models.TextField(blank=True, verbose_name="تعليقات المراجعة")
    
    # قرار اللجنة
    decision_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ القرار")
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                        verbose_name="المبلغ المعتمد")
    approved_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            verbose_name="النسبة المعتمدة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='reviewed_applications',
                                  verbose_name="راجعه")
    
    class Meta:
        verbose_name = "طلب منحة دراسية"
        verbose_name_plural = "طلبات المنح الدراسية"
        ordering = ['-application_date']
        unique_together = ['student', 'scholarship', 'academic_year']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['scholarship', 'status']),
            models.Index(fields=['application_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.scholarship.name_ar}"