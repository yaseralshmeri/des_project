# النظام المالي المتكامل والذكي
# Enhanced Comprehensive Financial Management System

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from students.enhanced_models import Student, AcademicProgram, User
from courses.enhanced_models import Semester, CourseOffering
import uuid

class FeeCategory(models.Model):
    """فئات الرسوم الجامعية"""
    
    CATEGORY_TYPES = [
        ('TUITION', 'رسوم دراسية'),
        ('LABORATORY', 'رسوم مختبر'),
        ('LIBRARY', 'رسوم مكتبة'),
        ('REGISTRATION', 'رسوم تسجيل'),
        ('GRADUATION', 'رسوم تخرج'),
        ('DORMITORY', 'رسوم سكن'),
        ('TRANSPORTATION', 'رسوم نقل'),
        ('MEDICAL', 'رسوم طبية'),
        ('SPORTS', 'رسوم رياضية'),
        ('TECHNOLOGY', 'رسوم تقنية'),
        ('STUDENT_ACTIVITY', 'رسوم أنشطة طلابية'),
        ('LATE_PAYMENT', 'رسوم تأخير'),
        ('PENALTY', 'رسوم جزائية'),
        ('OTHER', 'رسوم أخرى'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم فئة الرسوم")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز الفئة")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, 
                                   verbose_name="نوع الفئة")
    
    description = models.TextField(blank=True, verbose_name="وصف الفئة")
    
    # إعدادات الفئة
    is_mandatory = models.BooleanField(default=True, verbose_name="إجباري")
    is_refundable = models.BooleanField(default=False, verbose_name="قابل للاسترداد")
    allow_partial_payment = models.BooleanField(default=True, verbose_name="يسمح بالدفع الجزئي")
    
    # الحد الأدنى والأقصى
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                   verbose_name="الحد الأدنى للمبلغ")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   verbose_name="الحد الأقصى للمبلغ")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "فئة رسوم"
        verbose_name_plural = "فئات الرسوم"
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class FeeStructure(models.Model):
    """هيكل الرسوم للبرامج الأكاديمية"""
    
    program = models.ForeignKey(AcademicProgram, on_delete=models.CASCADE,
                              related_name='fee_structures', verbose_name="البرنامج الأكاديمي")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                               related_name='fee_structures', verbose_name="الفصل الدراسي")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE,
                                   related_name='fee_structures', verbose_name="فئة الرسوم")
    
    # مبلغ الرسوم
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.00'))],
                               verbose_name="المبلغ")
    
    # تواريخ الاستحقاق
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        verbose_name="رسوم التأخير")
    late_fee_days = models.IntegerField(default=30, verbose_name="أيام السماح")
    
    # إعدادات إضافية
    is_per_credit_hour = models.BooleanField(default=False, verbose_name="حسب الساعة المعتمدة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "هيكل رسوم"
        verbose_name_plural = "هياكل الرسوم"
        unique_together = ['program', 'semester', 'fee_category']
        ordering = ['program', 'semester', 'fee_category']
    
    def __str__(self):
        return f"{self.program.code} - {self.semester} - {self.fee_category.name}"

class StudentAccount(models.Model):
    """حساب الطالب المالي"""
    
    ACCOUNT_STATUS = [
        ('ACTIVE', 'نشط'),
        ('SUSPENDED', 'موقوف'),
        ('CLOSED', 'مغلق'),
        ('UNDER_REVIEW', 'قيد المراجعة'),
    ]
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE,
                                 related_name='financial_account', verbose_name="الطالب")
    account_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الحساب")
    
    # أرصدة الحساب
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                        verbose_name="الرصيد الحالي")
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                        verbose_name="الرصيد المعلق")
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                          verbose_name="الرصيد المتاح")
    
    # إجمالي المبالغ
    total_fees_charged = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                           verbose_name="إجمالي الرسوم المحملة")
    total_payments_made = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                            verbose_name="إجمالي المدفوعات")
    total_refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                      verbose_name="إجمالي المبالغ المستردة")
    
    # إعدادات الحساب
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                     verbose_name="الحد الائتماني")
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='ACTIVE',
                            verbose_name="حالة الحساب")
    
    # تواريخ مهمة
    last_payment_date = models.DateTimeField(null=True, blank=True, verbose_name="آخر دفعة")
    last_statement_date = models.DateTimeField(null=True, blank=True, verbose_name="آخر كشف حساب")
    
    # إعدادات التنبيهات
    send_balance_alerts = models.BooleanField(default=True, verbose_name="إرسال تنبيهات الرصيد")
    send_payment_reminders = models.BooleanField(default=True, verbose_name="إرسال تذكيرات الدفع")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "حساب طالب"
        verbose_name_plural = "حسابات الطلاب"
        ordering = ['account_number']
    
    def __str__(self):
        return f"{self.account_number} - {self.student.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لتوليد رقم الحساب"""
        if not self.account_number:
            # توليد رقم حساب فريد
            year = timezone.now().year
            self.account_number = f"ACC{year}{self.student.student_id}"
        
        # حساب الرصيد المتاح
        self.available_balance = self.current_balance - self.pending_balance
        
        super().save(*args, **kwargs)
    
    @property
    def outstanding_balance(self):
        """الرصيد المستحق"""
        return abs(min(self.current_balance, 0))
    
    @property
    def is_in_good_standing(self):
        """فحص حالة الحساب الجيدة"""
        return self.current_balance >= 0 and self.status == 'ACTIVE'

class StudentBill(models.Model):
    """فاتورة الطالب"""
    
    BILL_STATUS = [
        ('DRAFT', 'مسودة'),
        ('SENT', 'مرسلة'),
        ('PAID', 'مدفوعة'),
        ('PARTIAL', 'مدفوعة جزئياً'),
        ('OVERDUE', 'متأخرة'),
        ('CANCELLED', 'ملغية'),
        ('REFUNDED', 'مستردة'),
    ]
    
    student_account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE,
                                      related_name='bills', verbose_name="حساب الطالب")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                               related_name='student_bills', verbose_name="الفصل الدراسي")
    
    # معلومات الفاتورة
    bill_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الفاتورة")
    bill_date = models.DateField(default=timezone.now, verbose_name="تاريخ الفاتورة")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    
    # المبالغ
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                 verbose_name="المجموع الفرعي")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        verbose_name="مبلغ الخصم")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                   verbose_name="مبلغ الضريبة")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                     verbose_name="المبلغ الإجمالي")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                    verbose_name="المبلغ المدفوع")
    
    # حالة ومعلومات إضافية
    status = models.CharField(max_length=20, choices=BILL_STATUS, default='DRAFT',
                            verbose_name="حالة الفاتورة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات الإنشاء
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_bills', verbose_name="أنشئت بواسطة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "فاتورة طالب"
        verbose_name_plural = "فواتير الطلاب"
        ordering = ['-bill_date', '-bill_number']
        indexes = [
            models.Index(fields=['student_account', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {self.student_account.student.student_id}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لتوليد رقم الفاتورة وحساب المجاميع"""
        if not self.bill_number:
            year = timezone.now().year
            month = timezone.now().month
            count = StudentBill.objects.filter(
                bill_date__year=year,
                bill_date__month=month
            ).count() + 1
            self.bill_number = f"BILL{year}{month:02d}{count:04d}"
        
        # حساب المجموع الإجمالي
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        
        super().save(*args, **kwargs)
    
    @property
    def balance_due(self):
        """الرصيد المستحق"""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """فحص التأخير في الدفع"""
        return timezone.now().date() > self.due_date and self.balance_due > 0
    
    @property
    def payment_percentage(self):
        """نسبة الدفع"""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0

class BillItem(models.Model):
    """عناصر الفاتورة"""
    
    bill = models.ForeignKey(StudentBill, on_delete=models.CASCADE,
                           related_name='items', verbose_name="الفاتورة")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE,
                                   verbose_name="فئة الرسوم")
    
    # تفاصيل العنصر
    description = models.CharField(max_length=200, verbose_name="الوصف")
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)],
                                 verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                   validators=[MinValueValidator(Decimal('0.00'))],
                                   verbose_name="سعر الوحدة")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                    verbose_name="السعر الإجمالي")
    
    # خصومات على مستوى العنصر
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)],
                                           verbose_name="نسبة الخصم")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        verbose_name="مبلغ الخصم")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "عنصر فاتورة"
        verbose_name_plural = "عناصر الفواتير"
        ordering = ['bill', 'fee_category']
    
    def __str__(self):
        return f"{self.bill.bill_number} - {self.description}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لحساب المجاميع"""
        # حساب السعر الإجمالي قبل الخصم
        gross_total = self.quantity * self.unit_price
        
        # حساب مبلغ الخصم
        if self.discount_percentage > 0:
            self.discount_amount = gross_total * (self.discount_percentage / 100)
        
        # حساب السعر الإجمالي بعد الخصم
        self.total_price = gross_total - self.discount_amount
        
        super().save(*args, **kwargs)

class PaymentMethod(models.Model):
    """طرق الدفع المتاحة"""
    
    METHOD_TYPES = [
        ('CASH', 'نقداً'),
        ('BANK_TRANSFER', 'حوالة بنكية'),
        ('CREDIT_CARD', 'بطاقة ائتمان'),
        ('DEBIT_CARD', 'بطاقة خصم'),
        ('CHECK', 'شيك'),
        ('ONLINE_PAYMENT', 'دفع إلكتروني'),
        ('MOBILE_PAYMENT', 'دفع محمول'),
        ('SCHOLARSHIP', 'منحة دراسية'),
        ('INSTALLMENT', 'قسط'),
        ('OTHER', 'أخرى'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم طريقة الدفع")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="الاسم بالإنجليزية")
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES, verbose_name="نوع الطريقة")
    
    # إعدادات الطريقة
    is_online = models.BooleanField(default=False, verbose_name="طريقة إلكترونية")
    requires_approval = models.BooleanField(default=False, verbose_name="تتطلب موافقة")
    processing_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00,
                                       verbose_name="رسوم المعالجة")
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                                  verbose_name="نسبة رسوم المعالجة")
    
    # حدود المبالغ
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   verbose_name="الحد الأدنى للمبلغ")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   verbose_name="الحد الأقصى للمبلغ")
    
    # معلومات إضافية
    description = models.TextField(blank=True, verbose_name="الوصف")
    instructions = models.TextField(blank=True, verbose_name="تعليمات الدفع")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    sort_order = models.IntegerField(default=0, verbose_name="ترتيب العرض")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "طريقة دفع"
        verbose_name_plural = "طرق الدفع"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name

class Payment(models.Model):
    """مدفوعات الطلاب"""
    
    PAYMENT_STATUS = [
        ('PENDING', 'معلق'),
        ('PROCESSING', 'قيد المعالجة'),
        ('COMPLETED', 'مكتمل'),
        ('FAILED', 'فاشل'),
        ('CANCELLED', 'ملغي'),
        ('REFUNDED', 'مسترد'),
    ]
    
    # معلومات أساسية
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف الدفعة")
    student_account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE,
                                      related_name='payments', verbose_name="حساب الطالب")
    bill = models.ForeignKey(StudentBill, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='payments', verbose_name="الفاتورة")
    
    # تفاصيل الدفعة
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE,
                                     verbose_name="طريقة الدفع")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="رقم المرجع")
    
    # المبالغ
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.01'))],
                               verbose_name="المبلغ")
    processing_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00,
                                       verbose_name="رسوم المعالجة")
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                   verbose_name="المبلغ الصافي")
    
    # التواريخ
    payment_date = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الدفع")
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المعالجة")
    
    # الحالة والمعلومات
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING',
                            verbose_name="حالة الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات المعالجة
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='processed_payments', verbose_name="عولج بواسطة")
    
    # معلومات خارجية (للدفع الإلكتروني)
    external_transaction_id = models.CharField(max_length=100, blank=True,
                                             verbose_name="معرف المعاملة الخارجية")
    gateway_response = models.JSONField(default=dict, blank=True,
                                      verbose_name="استجابة البوابة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student_account', 'status']),
            models.Index(fields=['payment_date', 'status']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.payment_id} - {self.amount} - {self.student_account.student.student_id}"
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لحساب المبلغ الصافي"""
        # حساب رسوم المعالجة
        if self.payment_method.processing_fee_percentage > 0:
            self.processing_fee = self.amount * (self.payment_method.processing_fee_percentage / 100)
        elif self.payment_method.processing_fee > 0:
            self.processing_fee = self.payment_method.processing_fee
        
        # حساب المبلغ الصافي
        self.net_amount = self.amount - self.processing_fee
        
        super().save(*args, **kwargs)

class Scholarship(models.Model):
    """المنح الدراسية"""
    
    SCHOLARSHIP_TYPES = [
        ('ACADEMIC', 'منحة أكاديمية'),
        ('NEED_BASED', 'منحة حاجة'),
        ('ATHLETIC', 'منحة رياضية'),
        ('MERIT', 'منحة تفوق'),
        ('GOVERNMENT', 'منحة حكومية'),
        ('PRIVATE', 'منحة خاصة'),
        ('INTERNATIONAL', 'منحة دولية'),
        ('EMPLOYEE', 'منحة موظفين'),
        ('OTHER', 'أخرى'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('SUSPENDED', 'موقوف'),
        ('EXPIRED', 'منتهي'),
        ('CANCELLED', 'ملغي'),
    ]
    
    # معلومات أساسية
    name = models.CharField(max_length=200, verbose_name="اسم المنحة")
    name_en = models.CharField(max_length=200, blank=True, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=20, unique=True, verbose_name="رمز المنحة")
    scholarship_type = models.CharField(max_length=20, choices=SCHOLARSHIP_TYPES,
                                      verbose_name="نوع المنحة")
    
    description = models.TextField(verbose_name="وصف المنحة")
    
    # مبلغ المنحة
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.00'))],
                               verbose_name="مبلغ المنحة")
    is_percentage = models.BooleanField(default=False, verbose_name="نسبة مئوية")
    percentage_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="القيمة النسبية")
    
    # فترة المنحة
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    renewable = models.BooleanField(default=False, verbose_name="قابلة للتجديد")
    
    # شروط المنحة
    min_gpa = models.FloatField(null=True, blank=True,
                              validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
                              verbose_name="أقل معدل مطلوب")
    max_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   verbose_name="أقصى دخل مسموح")
    
    # قيود أخرى
    max_recipients = models.IntegerField(null=True, blank=True,
                                       validators=[MinValueValidator(1)],
                                       verbose_name="أقصى عدد مستفيدين")
    current_recipients = models.IntegerField(default=0, verbose_name="المستفيدين الحاليين")
    
    # معلومات الجهة المانحة
    sponsor_name = models.CharField(max_length=200, blank=True, verbose_name="اسم الجهة المانحة")
    sponsor_contact = models.CharField(max_length=200, blank=True, verbose_name="معلومات التواصل")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="حالة المنحة")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_scholarships', verbose_name="أنشئت بواسطة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "منحة دراسية"
        verbose_name_plural = "المنح الدراسية"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def is_available(self):
        """فحص توفر المنحة"""
        if not self.is_active or timezone.now().date() > self.end_date:
            return False
        
        if self.max_recipients and self.current_recipients >= self.max_recipients:
            return False
        
        return True
    
    @property
    def is_active(self):
        """فحص نشاط المنحة"""
        return (self.status == 'ACTIVE' and 
                self.start_date <= timezone.now().date() <= self.end_date)

class StudentScholarship(models.Model):
    """منح الطلاب"""
    
    STATUS_CHOICES = [
        ('APPLIED', 'مُقدم'),
        ('UNDER_REVIEW', 'قيد المراجعة'),
        ('APPROVED', 'موافق'),
        ('REJECTED', 'مرفوض'),
        ('ACTIVE', 'نشط'),
        ('SUSPENDED', 'موقوف'),
        ('EXPIRED', 'منتهي'),
        ('CANCELLED', 'ملغي'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                              related_name='scholarships', verbose_name="الطالب")
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE,
                                  related_name='recipients', verbose_name="المنحة")
    
    # تواريخ مهمة
    application_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقديم")
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الموافقة")
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    
    # مبلغ المنحة المحدد للطالب
    awarded_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       validators=[MinValueValidator(Decimal('0.00'))],
                                       verbose_name="مبلغ المنحة الممنوحة")
    
    # الحالة والمعلومات
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED',
                            verbose_name="حالة المنحة")
    
    # معلومات الموافقة
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_scholarships', verbose_name="تمت الموافقة بواسطة")
    
    # شروط خاصة
    conditions = models.TextField(blank=True, verbose_name="الشروط الخاصة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "منحة طالب"
        verbose_name_plural = "منح الطلاب"
        unique_together = ['student', 'scholarship']
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.scholarship.name}"
    
    @property
    def is_active(self):
        """فحص نشاط المنحة"""
        return (self.status == 'ACTIVE' and 
                self.start_date <= timezone.now().date() <= self.end_date)

class FinancialTransaction(models.Model):
    """المعاملات المالية العامة"""
    
    TRANSACTION_TYPES = [
        ('CHARGE', 'رسوم'),
        ('PAYMENT', 'دفعة'),
        ('REFUND', 'استرداد'),
        ('SCHOLARSHIP', 'منحة'),
        ('ADJUSTMENT', 'تعديل'),
        ('TRANSFER', 'تحويل'),
        ('PENALTY', 'جزاء'),
        ('DISCOUNT', 'خصم'),
    ]
    
    # معلومات أساسية
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True,
                                    verbose_name="معرف المعاملة")
    student_account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE,
                                      related_name='transactions', verbose_name="حساب الطالب")
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES,
                                      verbose_name="نوع المعاملة")
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               verbose_name="المبلغ")
    
    # المراجع
    reference_type = models.CharField(max_length=50, blank=True, verbose_name="نوع المرجع")
    reference_id = models.CharField(max_length=50, blank=True, verbose_name="معرف المرجع")
    
    # تفاصيل إضافية
    description = models.CharField(max_length=200, verbose_name="الوصف")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    # معلومات المعالجة
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='processed_transactions', verbose_name="عولج بواسطة")
    
    # أرصدة قبل وبعد المعاملة
    balance_before = models.DecimalField(max_digits=12, decimal_places=2,
                                       verbose_name="الرصيد قبل المعاملة")
    balance_after = models.DecimalField(max_digits=12, decimal_places=2,
                                      verbose_name="الرصيد بعد المعاملة")
    
    transaction_date = models.DateTimeField(default=timezone.now, verbose_name="تاريخ المعاملة")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "معاملة مالية"
        verbose_name_plural = "المعاملات المالية"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['student_account', 'transaction_type']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} - {self.amount}"