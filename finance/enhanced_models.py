"""
Enhanced Financial Management System
نظام إدارة مالي ومحاسبي متطور
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from students.models import Student

User = get_user_model()


class FiscalYear(models.Model):
    """
    Fiscal year management
    إدارة السنة المالية
    """
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fiscal_years'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Only one fiscal year can be active
            FiscalYear.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class ChartOfAccounts(models.Model):
    """
    Chart of accounts for advanced financial management
    دليل الحسابات للإدارة المالية المتقدمة
    """
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
    ]
    
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_accounts')
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_system_account = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chart_of_accounts'
        ordering = ['account_code']
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    def get_balance(self, as_of_date=None):
        """Calculate account balance as of a specific date"""
        if not as_of_date:
            as_of_date = timezone.now().date()
        
        entries = JournalEntry.objects.filter(
            journal_lines__account=self,
            date__lte=as_of_date,
            is_posted=True
        )
        
        total_debit = sum(line.debit_amount for entry in entries for line in entry.journal_lines.filter(account=self))
        total_credit = sum(line.credit_amount for entry in entries for line in entry.journal_lines.filter(account=self))
        
        if self.account_type in ['ASSET', 'EXPENSE']:
            return total_debit - total_credit
        else:
            return total_credit - total_debit


class EnhancedFeeStructure(models.Model):
    """
    Enhanced fee structure with more flexibility
    هيكل رسوم محسن بمرونة أكثر
    """
    PROGRAM_LEVELS = [
        ('FOUNDATION', 'Foundation'),
        ('DIPLOMA', 'Diploma'),
        ('BACHELOR', 'Bachelor'),
        ('MASTER', 'Master'),
        ('PHD', 'PhD'),
        ('CERTIFICATE', 'Certificate'),
    ]
    
    name = models.CharField(max_length=200)
    program_level = models.CharField(max_length=20, choices=PROGRAM_LEVELS)
    department = models.ForeignKey('roles_permissions.Department', on_delete=models.CASCADE, null=True)
    
    # Fee components
    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2)
    registration_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    library_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sports_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    technology_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activity_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Semester-specific settings
    semester_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    academic_year = models.IntegerField()
    
    # Currency and taxation
    currency = models.CharField(max_length=3, default='USD')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Validity
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enhanced_fee_structures'
        unique_together = [['program_level', 'department', 'semester_number', 'academic_year']]
        ordering = ['-academic_year', 'semester_number']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year} S{self.semester_number}"
    
    @property
    def total_fee_before_tax(self):
        return (
            self.tuition_fee + self.registration_fee + self.lab_fee +
            self.library_fee + self.sports_fee + self.technology_fee +
            self.activity_fee + self.insurance_fee
        )
    
    @property
    def tax_amount(self):
        return self.total_fee_before_tax * (self.tax_rate / 100)
    
    @property
    def total_fee_after_tax(self):
        return self.total_fee_before_tax + self.tax_amount


class Invoice(models.Model):
    """
    Comprehensive invoice system
    نظام فواتير شامل
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('VIEWED', 'Viewed'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    INVOICE_TYPES = [
        ('TUITION', 'Tuition Fee'),
        ('REGISTRATION', 'Registration Fee'),
        ('LIBRARY', 'Library Fine'),
        ('DORMITORY', 'Dormitory Fee'),
        ('EXAM', 'Exam Fee'),
        ('CERTIFICATE', 'Certificate Fee'),
        ('OTHER', 'Other'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    fee_structure = models.ForeignKey(EnhancedFeeStructure, on_delete=models.PROTECT, null=True, blank=True)
    
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPES, default='TUITION')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Invoice details
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Additional information
    description = models.TextField()
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    sent_at = models.DateTimeField(null=True, blank=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['invoice_type', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.student.student_id}"
    
    @property
    def outstanding_amount(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.outstanding_amount > 0
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        prefix = f"INV{timezone.now().year}"
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:06d}"


class InvoiceLineItem(models.Model):
    """
    Individual line items for invoices
    بنود فردية للفواتير
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Accounting link
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoice_line_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"
    
    @property
    def line_total_before_discount(self):
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        return self.line_total_before_discount * (self.discount_percentage / 100)
    
    @property
    def line_total_after_discount(self):
        return self.line_total_before_discount - self.discount_amount
    
    @property
    def tax_amount(self):
        return self.line_total_after_discount * (self.tax_rate / 100)
    
    @property
    def line_total(self):
        return self.line_total_after_discount + self.tax_amount


class EnhancedPayment(models.Model):
    """
    Enhanced payment system with full tracking
    نظام دفع محسن مع تتبع كامل
    """
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('ONLINE', 'Online Payment'),
        ('CHEQUE', 'Cheque'),
        ('MOBILE_PAYMENT', 'Mobile Payment'),
        ('CRYPTOCURRENCY', 'Cryptocurrency'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    payment_id = models.CharField(max_length=100, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    
    # Payment gateway information
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Banking information (for bank transfers, cheques)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    routing_number = models.CharField(max_length=50, blank=True)
    cheque_number = models.CharField(max_length=50, blank=True)
    
    # Timing
    payment_date = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Staff handling
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_payments')
    
    # Additional information
    notes = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enhanced_payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student', '-payment_date']),
            models.Index(fields=['payment_method', 'status']),
            models.Index(fields=['invoice', 'status']),
        ]
    
    def __str__(self):
        return f"{self.payment_id} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        super().save(*args, **kwargs)
    
    def generate_payment_id(self):
        """Generate unique payment ID"""
        prefix = f"PAY{timezone.now().year}"
        last_payment = EnhancedPayment.objects.filter(
            payment_id__startswith=prefix
        ).order_by('-payment_id').first()
        
        if last_payment:
            last_number = int(last_payment.payment_id.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:08d}"


class JournalEntry(models.Model):
    """
    Double-entry bookkeeping journal entries
    قيود يومية للمحاسبة المزدوجة
    """
    ENTRY_TYPES = [
        ('MANUAL', 'Manual Entry'),
        ('PAYMENT', 'Payment Entry'),
        ('INVOICE', 'Invoice Entry'),
        ('ADJUSTMENT', 'Adjustment Entry'),
        ('CLOSING', 'Closing Entry'),
    ]
    
    entry_number = models.CharField(max_length=50, unique=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='MANUAL')
    date = models.DateField()
    description = models.TextField()
    
    # Reference to source document
    reference_number = models.CharField(max_length=100, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(EnhancedPayment, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Entry control
    is_posted = models.BooleanField(default=False)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_entries')
    posted_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'journal_entries'
        ordering = ['-date', '-entry_number']
    
    def __str__(self):
        return f"{self.entry_number} - {self.description}"
    
    @property
    def total_debits(self):
        return sum(line.debit_amount for line in self.journal_lines.all())
    
    @property
    def total_credits(self):
        return sum(line.credit_amount for line in self.journal_lines.all())
    
    @property
    def is_balanced(self):
        return self.total_debits == self.total_credits
    
    def post_entry(self, user):
        """Post the journal entry"""
        if self.is_balanced and not self.is_posted:
            self.is_posted = True
            self.posted_by = user
            self.posted_at = timezone.now()
            self.save()
            return True
        return False


class JournalEntryLine(models.Model):
    """
    Individual lines of journal entries
    سطور فردية لقيود اليومية
    """
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='journal_lines')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT)
    description = models.CharField(max_length=200, blank=True)
    
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'journal_entry_lines'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.account_code}"
    
    def clean(self):
        # Ensure only debit OR credit is entered, not both
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("A line can have either debit or credit, not both")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("A line must have either debit or credit amount")


class BudgetCategory(models.Model):
    """
    Budget categories for financial planning
    فئات الميزانية للتخطيط المالي
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budget_categories'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Budget(models.Model):
    """
    Annual budget planning
    تخطيط الميزانية السنوية
    """
    BUDGET_TYPES = [
        ('OPERATIONAL', 'Operational Budget'),
        ('CAPITAL', 'Capital Budget'),
        ('PROJECT', 'Project Budget'),
    ]
    
    name = models.CharField(max_length=200)
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='budgets')
    department = models.ForeignKey('roles_permissions.Department', on_delete=models.CASCADE, null=True, blank=True)
    
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budgets'
        unique_together = [['name', 'fiscal_year']]
        ordering = ['-fiscal_year', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.fiscal_year.name}"


class BudgetLineItem(models.Model):
    """
    Individual budget line items
    بنود الميزانية الفردية
    """
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='line_items')
    category = models.ForeignKey(BudgetCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=200)
    
    budgeted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    committed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budget_line_items'
        unique_together = [['budget', 'category']]
        ordering = ['category__code']
    
    def __str__(self):
        return f"{self.budget.name} - {self.category.name}"
    
    @property
    def available_amount(self):
        return self.budgeted_amount - self.spent_amount - self.committed_amount
    
    @property
    def utilization_percentage(self):
        if self.budgeted_amount > 0:
            return ((self.spent_amount + self.committed_amount) / self.budgeted_amount) * 100
        return 0