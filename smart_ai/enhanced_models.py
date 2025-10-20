# نظام الذكاء الاصطناعي المتطور والشامل
# Enhanced Comprehensive AI System for University Management

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from students.enhanced_models import Student, AcademicProgram
from courses.enhanced_models import Course, CourseOffering, Enrollment
from finance.enhanced_models import StudentAccount, Payment
import json
import uuid
from decimal import Decimal

User = get_user_model()

class AIModel(models.Model):
    """نماذج الذكاء الاصطناعي المختلفة"""
    
    MODEL_TYPES = [
        ('STUDENT_PERFORMANCE', 'تحليل أداء الطلاب'),
        ('FINANCIAL_PREDICTION', 'التنبؤ المالي'),
        ('ACADEMIC_RECOMMENDATION', 'التوصيات الأكاديمية'),
        ('ANOMALY_DETECTION', 'كشف الشذوذ'),
        ('PREDICTIVE_ANALYTICS', 'التحليل التنبؤي'),
        ('CHATBOT', 'المساعد الذكي'),
        ('ENROLLMENT_PREDICTION', 'تنبؤ التسجيل'),
        ('RESOURCE_OPTIMIZATION', 'تحسين الموارد'),
        ('RISK_ASSESSMENT', 'تقييم المخاطر'),
        ('SENTIMENT_ANALYSIS', 'تحليل المشاعر'),
    ]
    
    STATUS_CHOICES = [
        ('TRAINING', 'قيد التدريب'),
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('UPDATING', 'قيد التحديث'),
        ('ERROR', 'خطأ'),
        ('ARCHIVED', 'مؤرشف'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم النموذج")
    description = models.TextField(verbose_name="وصف النموذج")
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES, verbose_name="نوع النموذج")
    version = models.CharField(max_length=20, default="1.0", verbose_name="إصدار النموذج")
    
    # معلمات النموذج
    algorithm = models.CharField(max_length=100, blank=True, verbose_name="الخوارزمية المستخدمة")
    parameters = models.JSONField(default=dict, verbose_name="معاملات النموذج")
    hyperparameters = models.JSONField(default=dict, verbose_name="المعاملات الفائقة")
    
    # إحصائيات الأداء
    accuracy_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                     verbose_name="دقة النموذج")
    precision_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                      verbose_name="الدقة")
    recall_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                   verbose_name="الاستدعاء")
    f1_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                               verbose_name="نتيجة F1")
    
    # معلومات التدريب
    training_data_size = models.IntegerField(default=0, verbose_name="حجم بيانات التدريب")
    training_duration = models.DurationField(null=True, blank=True, verbose_name="مدة التدريب")
    last_trained = models.DateTimeField(null=True, blank=True, verbose_name="آخر تدريب")
    
    # معلومات النشر
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRAINING',
                            verbose_name="حالة النموذج")
    deployment_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النشر")
    
    # إعدادات النموذج
    is_automated = models.BooleanField(default=False, verbose_name="تحديث تلقائي")
    update_frequency = models.CharField(max_length=20, choices=[
        ('DAILY', 'يومي'),
        ('WEEKLY', 'أسبوعي'),
        ('MONTHLY', 'شهري'),
        ('MANUAL', 'يدوي'),
    ], default='WEEKLY', verbose_name="تكرار التحديث")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_ai_models', verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "نموذج ذكاء اصطناعي"
        verbose_name_plural = "نماذج الذكاء الاصطناعي"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['status', 'is_automated']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"

class StudentPerformanceAnalysis(models.Model):
    """تحليل أداء الطلاب الذكي"""
    
    RISK_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    RECOMMENDATION_TYPES = [
        ('STUDY_PLAN', 'خطة دراسية'),
        ('TUTORING', 'دروس تقوية'),
        ('COUNSELING', 'إرشاد أكاديمي'),
        ('RESOURCE_ACCESS', 'الوصول للموارد'),
        ('TIME_MANAGEMENT', 'إدارة الوقت'),
        ('EXAM_PREPARATION', 'التحضير للامتحانات'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                              related_name='performance_analyses', verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='student_analyses', verbose_name="المقرر")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                               related_name='performance_analyses', verbose_name="نموذج الذكاء الاصطناعي")
    
    # بيانات الإدخال
    current_gpa = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
                                  verbose_name="المعدل التراكمي الحالي")
    attendance_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                      verbose_name="معدل الحضور %")
    assignment_completion_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                                 verbose_name="معدل إنجاز المهام %")
    participation_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                          verbose_name="درجة المشاركة")
    study_hours_per_week = models.FloatField(default=0.0, verbose_name="ساعات الدراسة الأسبوعية")
    
    # نتائج التحليل
    predicted_final_grade = models.FloatField(null=True, blank=True,
                                            validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                            verbose_name="الدرجة النهائية المتوقعة")
    success_probability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                          verbose_name="احتمالية النجاح")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, verbose_name="مستوى المخاطر")
    
    # التوصيات الذكية
    recommendations = models.JSONField(default=list, verbose_name="التوصيات")
    intervention_needed = models.BooleanField(default=False, verbose_name="يحتاج تدخل")
    priority_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)],
                                       verbose_name="مستوى الأولوية")
    
    # عوامل مؤثرة
    influencing_factors = models.JSONField(default=dict, verbose_name="العوامل المؤثرة")
    improvement_areas = models.JSONField(default=list, verbose_name="مجالات التحسين")
    
    # معلومات التحليل
    analysis_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التحليل")
    confidence_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                       verbose_name="درجة الثقة")
    
    # متابعة التوصيات
    recommendations_implemented = models.BooleanField(default=False, verbose_name="تم تنفيذ التوصيات")
    implementation_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التنفيذ")
    
    class Meta:
        verbose_name = "تحليل أداء طالب"
        verbose_name_plural = "تحليلات أداء الطلاب"
        ordering = ['-analysis_date']
        indexes = [
            models.Index(fields=['student', 'risk_level']),
            models.Index(fields=['course', 'analysis_date']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.risk_level} - {self.analysis_date.date()}"

class AIChatBot(models.Model):
    """المساعد الذكي للطلاب والموظفين"""
    
    CHAT_TYPES = [
        ('STUDENT_SUPPORT', 'دعم الطلاب'),
        ('ACADEMIC_ADVISOR', 'مستشار أكاديمي'),
        ('FINANCIAL_ASSISTANT', 'مساعد مالي'),
        ('ADMINISTRATIVE_HELP', 'مساعدة إدارية'),
        ('TECHNICAL_SUPPORT', 'الدعم التقني'),
        ('CAREER_GUIDANCE', 'التوجيه المهني'),
        ('MENTAL_HEALTH', 'الصحة النفسية'),
        ('GENERAL_INQUIRY', 'استفسار عام'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('BUSY', 'مشغول'),
        ('OFFLINE', 'غير متصل'),
        ('MAINTENANCE', 'صيانة'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم المساعد")
    chat_type = models.CharField(max_length=50, choices=CHAT_TYPES, verbose_name="نوع المحادثة")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                               related_name='chatbots', verbose_name="نموذج الذكاء الاصطناعي")
    
    # إعدادات المساعد
    welcome_message = models.TextField(verbose_name="رسالة الترحيب")
    personality_traits = models.JSONField(default=dict, verbose_name="سمات الشخصية")
    knowledge_base = models.JSONField(default=dict, verbose_name="قاعدة المعرفة")
    
    # إعدادات التفاعل
    max_conversation_length = models.IntegerField(default=50, verbose_name="أقصى طول للمحادثة")
    response_delay = models.FloatField(default=1.0, verbose_name="تأخير الرد (ثانية)")
    confidence_threshold = models.FloatField(default=0.7, verbose_name="حد الثقة")
    
    # إحصائيات الاستخدام
    total_conversations = models.IntegerField(default=0, verbose_name="إجمالي المحادثات")
    successful_resolutions = models.IntegerField(default=0, verbose_name="الحلول الناجحة")
    average_satisfaction = models.FloatField(default=0.0, verbose_name="متوسط الرضا")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE',
                            verbose_name="حالة المساعد")
    
    is_multilingual = models.BooleanField(default=True, verbose_name="متعدد اللغات")
    supported_languages = models.JSONField(default=list, verbose_name="اللغات المدعومة")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "مساعد ذكي"
        verbose_name_plural = "المساعدات الذكية"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_chat_type_display()})"

class ChatSession(models.Model):
    """جلسة محادثة مع المساعد الذكي"""
    
    SESSION_STATUS = [
        ('ACTIVE', 'نشط'),
        ('COMPLETED', 'مكتمل'),
        ('ABANDONED', 'متروك'),
        ('ESCALATED', 'تم تصعيده'),
        ('ERROR', 'خطأ'),
    ]
    
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="معرف الجلسة")
    chatbot = models.ForeignKey(AIChatBot, on_delete=models.CASCADE,
                              related_name='chat_sessions', verbose_name="المساعد الذكي")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='chat_sessions', verbose_name="المستخدم")
    
    # معلومات الجلسة
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="وقت البداية")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت النهاية")
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='ACTIVE',
                            verbose_name="حالة الجلسة")
    
    # إحصائيات الجلسة
    message_count = models.IntegerField(default=0, verbose_name="عدد الرسائل")
    user_satisfaction = models.IntegerField(null=True, blank=True,
                                          validators=[MinValueValidator(1), MaxValueValidator(5)],
                                          verbose_name="رضا المستخدم")
    issue_resolved = models.BooleanField(null=True, blank=True, verbose_name="تم حل المشكلة")
    
    # معلومات إضافية
    session_summary = models.TextField(blank=True, verbose_name="ملخص الجلسة")
    tags = models.JSONField(default=list, verbose_name="العلامات")
    escalated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='escalated_chats', verbose_name="تم تصعيدها إلى")
    
    class Meta:
        verbose_name = "جلسة محادثة"
        verbose_name_plural = "جلسات المحادثة"
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.session_id} - {self.user.username} - {self.chatbot.name}"
    
    @property
    def duration(self):
        """مدة الجلسة"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time

class ChatMessage(models.Model):
    """رسائل المحادثة"""
    
    MESSAGE_TYPES = [
        ('USER', 'رسالة المستخدم'),
        ('BOT', 'رسالة المساعد'),
        ('SYSTEM', 'رسالة النظام'),
        ('ESCALATION', 'تصعيد'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE,
                              related_name='messages', verbose_name="الجلسة")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name="نوع الرسالة")
    
    # محتوى الرسالة
    content = models.TextField(verbose_name="محتوى الرسالة")
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # معلومات الذكاء الاصطناعي
    user_intent = models.CharField(max_length=100, blank=True, verbose_name="قصد المستخدم")
    confidence_score = models.FloatField(default=0.0, verbose_name="درجة الثقة")
    entities_extracted = models.JSONField(default=list, verbose_name="الكيانات المستخرجة")
    
    # معلومات الرد
    response_time = models.FloatField(null=True, blank=True, verbose_name="وقت الرد (ثانية)")
    was_helpful = models.BooleanField(null=True, blank=True, verbose_name="كان مفيداً")
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإرسال")
    
    class Meta:
        verbose_name = "رسالة محادثة"
        verbose_name_plural = "رسائل المحادثة"
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.session.session_id} - {self.get_message_type_display()} - {self.timestamp}"

class FinancialPrediction(models.Model):
    """التنبؤات المالية الذكية"""
    
    PREDICTION_TYPES = [
        ('PAYMENT_BEHAVIOR', 'سلوك الدفع'),
        ('DEFAULT_RISK', 'مخاطر التخلف عن السداد'),
        ('REVENUE_FORECAST', 'توقع الإيرادات'),
        ('EXPENSE_PREDICTION', 'توقع المصروفات'),
        ('CASH_FLOW', 'التدفق النقدي'),
        ('SCHOLARSHIP_ALLOCATION', 'توزيع المنح'),
    ]
    
    student_account = models.ForeignKey('finance.StudentAccount', on_delete=models.CASCADE,
                                      related_name='ai_predictions', verbose_name="حساب الطالب")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                               related_name='financial_predictions', verbose_name="نموذج الذكاء الاصطناعي")
    
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPES,
                                     verbose_name="نوع التنبؤ")
    
    # بيانات الإدخال
    historical_data = models.JSONField(default=dict, verbose_name="البيانات التاريخية")
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الرصيد الحالي")
    payment_history = models.JSONField(default=list, verbose_name="تاريخ المدفوعات")
    
    # نتائج التنبؤ
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name="المبلغ المتوقع")
    probability_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                        verbose_name="درجة الاحتمالية")
    risk_category = models.CharField(max_length=20, choices=[
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
    ], verbose_name="فئة المخاطر")
    
    # التوصيات المالية
    recommendations = models.JSONField(default=list, verbose_name="التوصيات المالية")
    suggested_actions = models.JSONField(default=list, verbose_name="الإجراءات المقترحة")
    
    # فترة التنبؤ
    prediction_period = models.CharField(max_length=20, choices=[
        ('1_MONTH', 'شهر واحد'),
        ('3_MONTHS', 'ثلاثة أشهر'),
        ('6_MONTHS', 'ستة أشهر'),
        ('1_YEAR', 'سنة واحدة'),
    ], verbose_name="فترة التنبؤ")
    
    prediction_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التنبؤ")
    confidence_interval = models.JSONField(default=dict, verbose_name="فترة الثقة")
    
    # التحقق من صحة التنبؤ
    actual_outcome = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       verbose_name="النتيجة الفعلية")
    prediction_accuracy = models.FloatField(null=True, blank=True, verbose_name="دقة التنبؤ")
    
    class Meta:
        verbose_name = "تنبؤ مالي"
        verbose_name_plural = "التنبؤات المالية"
        ordering = ['-prediction_date']
    
    def __str__(self):
        return f"{self.student_account.student.student_id} - {self.get_prediction_type_display()}"

class AcademicRecommendation(models.Model):
    """التوصيات الأكاديمية الذكية"""
    
    RECOMMENDATION_TYPES = [
        ('COURSE_SELECTION', 'اختيار المقررات'),
        ('STUDY_PLAN', 'خطة الدراسة'),
        ('CAREER_PATH', 'المسار المهني'),
        ('SKILL_DEVELOPMENT', 'تطوير المهارات'),
        ('RESEARCH_TOPIC', 'موضوع البحث'),
        ('INTERNSHIP', 'التدريب العملي'),
        ('GRADUATION_TIMELINE', 'جدول التخرج'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                              related_name='ai_recommendations', verbose_name="الطالب")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                               related_name='academic_recommendations', verbose_name="نموذج الذكاء الاصطناعي")
    
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES,
                                         verbose_name="نوع التوصية")
    title = models.CharField(max_length=200, verbose_name="عنوان التوصية")
    description = models.TextField(verbose_name="وصف التوصية")
    
    # تفاصيل التوصية
    recommended_courses = models.ManyToManyField(Course, blank=True,
                                               related_name='ai_recommendations',
                                               verbose_name="المقررات المقترحة")
    rationale = models.TextField(verbose_name="المبرر")
    expected_benefits = models.JSONField(default=list, verbose_name="الفوائد المتوقعة")
    
    # الأولوية والتوقيت
    priority_level = models.CharField(max_length=20, choices=PRIORITY_LEVELS,
                                    default='MEDIUM', verbose_name="مستوى الأولوية")
    recommended_timeline = models.CharField(max_length=100, verbose_name="الجدول الزمني المقترح")
    
    # معايير التوصية
    based_on_factors = models.JSONField(default=list, verbose_name="العوامل المؤثرة")
    confidence_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                       verbose_name="درجة الثقة")
    
    # متابعة التوصية
    is_accepted = models.BooleanField(null=True, blank=True, verbose_name="تم قبولها")
    acceptance_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ القبول")
    rejection_reason = models.TextField(blank=True, verbose_name="سبب الرفض")
    
    # تقييم التوصية
    effectiveness_rating = models.IntegerField(null=True, blank=True,
                                             validators=[MinValueValidator(1), MaxValueValidator(5)],
                                             verbose_name="تقييم الفعالية")
    feedback = models.TextField(blank=True, verbose_name="ملاحظات")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ انتهاء الصلاحية")
    
    class Meta:
        verbose_name = "توصية أكاديمية"
        verbose_name_plural = "التوصيات الأكاديمية"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'recommendation_type']),
            models.Index(fields=['priority_level', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.title}"

class SystemAnalytics(models.Model):
    """تحليلات النظام الشاملة"""
    
    ANALYTICS_TYPES = [
        ('USER_BEHAVIOR', 'سلوك المستخدمين'),
        ('SYSTEM_PERFORMANCE', 'أداء النظام'),
        ('ACADEMIC_TRENDS', 'الاتجاهات الأكاديمية'),
        ('FINANCIAL_ANALYSIS', 'التحليل المالي'),
        ('RESOURCE_UTILIZATION', 'استخدام الموارد'),
        ('PREDICTIVE_INSIGHTS', 'الرؤى التنبؤية'),
    ]
    
    analytics_type = models.CharField(max_length=50, choices=ANALYTICS_TYPES,
                                    verbose_name="نوع التحليل")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                               related_name='system_analytics', verbose_name="نموذج الذكاء الاصطناعي")
    
    # بيانات التحليل
    analysis_period = models.CharField(max_length=20, choices=[
        ('DAILY', 'يومي'),
        ('WEEKLY', 'أسبوعي'),
        ('MONTHLY', 'شهري'),
        ('QUARTERLY', 'ربع سنوي'),
        ('YEARLY', 'سنوي'),
    ], verbose_name="فترة التحليل")
    
    start_date = models.DateTimeField(verbose_name="تاريخ البداية")
    end_date = models.DateTimeField(verbose_name="تاريخ النهاية")
    
    # نتائج التحليل
    metrics = models.JSONField(default=dict, verbose_name="المقاييس")
    insights = models.JSONField(default=list, verbose_name="الرؤى")
    recommendations = models.JSONField(default=list, verbose_name="التوصيات")
    
    # الاتجاهات والأنماط
    trends_identified = models.JSONField(default=list, verbose_name="الاتجاهات المحددة")
    anomalies_detected = models.JSONField(default=list, verbose_name="الشذوذات المكتشفة")
    patterns = models.JSONField(default=dict, verbose_name="الأنماط")
    
    # التقييم والثقة
    confidence_level = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                       verbose_name="مستوى الثقة")
    data_quality_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                         verbose_name="درجة جودة البيانات")
    
    analysis_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التحليل")
    
    class Meta:
        verbose_name = "تحليلات النظام"
        verbose_name_plural = "تحليلات النظام"
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f"{self.get_analytics_type_display()} - {self.analysis_date.date()}"