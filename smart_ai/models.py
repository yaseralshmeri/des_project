# نظام الذكاء الاصطناعي المتقدم لإدارة الجامعة
# Advanced AI System for University Management

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import json

User = get_user_model()


class AIAnalyticsModel(models.Model):
    """نموذج تحليلات الذكاء الاصطناعي"""
    
    ANALYTICS_TYPES = [
        ('STUDENT_PERFORMANCE', 'أداء الطلاب'),
        ('COURSE_ANALYTICS', 'تحليلات المقررات'),
        ('FINANCIAL_FORECAST', 'تنبؤات مالية'),
        ('ENROLLMENT_PREDICTION', 'تنبؤات التسجيل'),
        ('RESOURCE_OPTIMIZATION', 'تحسين الموارد'),
        ('RISK_ASSESSMENT', 'تقييم المخاطر'),
        ('BEHAVIORAL_ANALYSIS', 'تحليل السلوك'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('TRAINING', 'تحت التدريب'),
        ('MAINTENANCE', 'صيانة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات النموذج
    name_ar = models.CharField(max_length=200, verbose_name="اسم النموذج - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم النموذج - إنجليزي")
    code = models.CharField(max_length=50, unique=True, verbose_name="رمز النموذج")
    analytics_type = models.CharField(max_length=25, choices=ANALYTICS_TYPES,
                                    verbose_name="نوع التحليل")
    
    # وصف والإعدادات
    description = models.TextField(verbose_name="وصف النموذج")
    configuration = models.JSONField(default=dict, verbose_name="إعدادات النموذج")
    parameters = models.JSONField(default=dict, verbose_name="معاملات النموذج")
    
    # حالة النموذج
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='INACTIVE',
                            verbose_name="حالة النموذج")
    
    # مقاييس الأداء
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(1)],
                                       verbose_name="درجة الدقة")
    last_training_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ آخر تدريب")
    total_predictions = models.IntegerField(default=0, verbose_name="إجمالي التنبؤات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_ai_analytics_models',
                                 verbose_name="أُنشئ بواسطة")
    
    class Meta:
        verbose_name = "نموذج تحليلات ذكية"
        verbose_name_plural = "نماذج التحليلات الذكية"
        ordering = ['analytics_type', 'name_ar']
    
    def __str__(self):
        return f"{self.name_ar} ({self.get_analytics_type_display()})"
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE'
    
    @property
    def performance_summary(self):
        return {
            'accuracy': float(self.accuracy_score) if self.accuracy_score else None,
            'total_predictions': self.total_predictions,
            'last_training': self.last_training_date.isoformat() if self.last_training_date else None,
            'status': self.status
        }

class AIModel(models.Model):
    """نماذج الذكاء الاصطناعي المستخدمة في النظام"""
    
    MODEL_TYPES = [
        ('PREDICTION', 'تنبؤي'),
        ('CLASSIFICATION', 'تصنيف'),
        ('RECOMMENDATION', 'توصية'),
        ('NLP', 'معالجة اللغة الطبيعية'),
        ('COMPUTER_VISION', 'رؤية حاسوبية'),
        ('CLUSTERING', 'تجميع'),
        ('ANOMALY_DETECTION', 'كشف الشذوذ'),
        ('OPTIMIZATION', 'تحسين'),
    ]
    
    MODEL_STATUS = [
        ('TRAINING', 'تحت التدريب'),
        ('TRAINED', 'مُدرب'),
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('DEPRECATED', 'مُهمل'),
        ('FAILED', 'فاشل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات النموذج الأساسية
    name_ar = models.CharField(max_length=200, verbose_name="اسم النموذج - عربي")
    name_en = models.CharField(max_length=200, verbose_name="اسم النموذج - إنجليزي")
    code = models.CharField(max_length=50, unique=True, verbose_name="رمز النموذج")
    description = models.TextField(verbose_name="وصف النموذج")
    
    # نوع وخصائص النموذج
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES,
                                verbose_name="نوع النموذج")
    algorithm = models.CharField(max_length=100, verbose_name="الخوارزمية المستخدمة")
    version = models.CharField(max_length=20, default='1.0', verbose_name="الإصدار")
    
    # إعدادات النموذج
    parameters = models.JSONField(default=dict, verbose_name="معاملات النموذج")
    hyperparameters = models.JSONField(default=dict, verbose_name="معاملات التحكم")
    feature_columns = models.JSONField(default=list, verbose_name="أعمدة الميزات")
    target_column = models.CharField(max_length=100, blank=True, verbose_name="العمود المستهدف")
    
    # معلومات الأداء
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(1)],
                                 verbose_name="دقة النموذج")
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                  validators=[MinValueValidator(0), MaxValueValidator(1)],
                                  verbose_name="الدقة")
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                               validators=[MinValueValidator(0), MaxValueValidator(1)],
                               verbose_name="الاستدعاء")
    f1_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(1)],
                                 verbose_name="نتيجة F1")
    
    # بيانات التدريب
    training_data_size = models.IntegerField(default=0, verbose_name="حجم بيانات التدريب")
    training_start_date = models.DateTimeField(null=True, blank=True, verbose_name="بداية التدريب")
    training_end_date = models.DateTimeField(null=True, blank=True, verbose_name="نهاية التدريب")
    last_retrained = models.DateTimeField(null=True, blank=True, verbose_name="آخر إعادة تدريب")
    
    # الحالة والإعدادات
    status = models.CharField(max_length=15, choices=MODEL_STATUS, default='TRAINING',
                            verbose_name="حالة النموذج")
    is_active = models.BooleanField(default=False, verbose_name="نشط")
    auto_retrain = models.BooleanField(default=False, verbose_name="إعادة تدريب تلقائي")
    retrain_threshold = models.DecimalField(max_digits=5, decimal_places=4, default=0.1,
                                          verbose_name="حد إعادة التدريب")
    
    # مسار النموذج والملفات
    model_file_path = models.CharField(max_length=500, blank=True, verbose_name="مسار ملف النموذج")
    config_file_path = models.CharField(max_length=500, blank=True, verbose_name="مسار ملف الإعدادات")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_ai_models', verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "نموذج ذكاء اصطناعي"
        verbose_name_plural = "نماذج الذكاء الاصطناعي"
        ordering = ['model_type', 'name_ar']
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} ({self.get_model_type_display()})"
    
    @property
    def performance_metrics(self):
        """مقاييس الأداء مجمعة"""
        return {
            'accuracy': float(self.accuracy or 0),
            'precision': float(self.precision or 0),
            'recall': float(self.recall or 0),
            'f1_score': float(self.f1_score or 0),
        }
    
    @property
    def needs_retraining(self):
        """هل يحتاج النموذج لإعادة تدريب"""
        if not self.auto_retrain:
            return False
        if self.accuracy and self.accuracy < self.retrain_threshold:
            return True
        return False


class StudentAIProfile(models.Model):
    """الملف الذكي للطالب"""
    
    LEARNING_STYLES = [
        ('VISUAL', 'بصري'),
        ('AUDITORY', 'سمعي'),
        ('KINESTHETIC', 'حركي'),
        ('READING_WRITING', 'قراءة وكتابة'),
        ('MIXED', 'مختلط'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=False,
                               related_name='ai_profile', verbose_name="الطالب")
    
    # تحليل الأداء الأكاديمي
    predicted_gpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                      verbose_name="المعدل المتوقع")
    graduation_probability = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                               validators=[MinValueValidator(0), MaxValueValidator(1)],
                                               verbose_name="احتمالية التخرج")
    dropout_risk = models.CharField(max_length=10, choices=RISK_LEVELS, default='LOW',
                                  verbose_name="خطر التسرب")
    academic_standing_prediction = models.CharField(max_length=50, blank=True,
                                                  verbose_name="التوقع الأكاديمي")
    
    # أسلوب التعلم المفضل
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='MIXED',
                                    verbose_name="أسلوب التعلم")
    learning_pace = models.CharField(max_length=20, 
                                   choices=[('SLOW', 'بطيء'), ('NORMAL', 'عادي'), ('FAST', 'سريع')],
                                   default='NORMAL', verbose_name="وتيرة التعلم")
    
    # التحليل السلوكي
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="نقاط التفاعل")
    attendance_pattern = models.JSONField(default=dict, verbose_name="نمط الحضور")
    study_pattern = models.JSONField(default=dict, verbose_name="نمط الدراسة")
    
    # التوصيات الذكية
    recommended_courses = models.JSONField(default=list, verbose_name="المقررات المُوصى بها")
    recommended_study_plan = models.JSONField(default=dict, verbose_name="الخطة الدراسية المُوصى بها")
    improvement_suggestions = models.JSONField(default=list, verbose_name="اقتراحات التحسين")
    
    # التحليل العاطفي والنفسي
    stress_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='LOW',
                                  verbose_name="مستوى التوتر")
    motivation_level = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="مستوى الدافعية")
    satisfaction_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)],
                                           verbose_name="نقاط الرضا")
    
    # المهارات والكفاءات
    technical_skills = models.JSONField(default=dict, verbose_name="المهارات التقنية")
    soft_skills = models.JSONField(default=dict, verbose_name="المهارات الناعمة")
    career_interests = models.JSONField(default=list, verbose_name="الاهتمامات المهنية")
    
    # التدخلات المُوصى بها
    intervention_alerts = models.JSONField(default=list, verbose_name="تنبيهات التدخل")
    support_recommendations = models.JSONField(default=list, verbose_name="توصيات الدعم")
    
    # معلومات التحديث
    last_analysis_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ آخر تحليل")
    analysis_frequency = models.CharField(max_length=20, default='WEEKLY',
                                        choices=[
                                            ('DAILY', 'يومي'),
                                            ('WEEKLY', 'أسبوعي'),
                                            ('MONTHLY', 'شهري'),
                                        ], verbose_name="تكرار التحليل")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "الملف الذكي للطالب"
        verbose_name_plural = "الملفات الذكية للطلاب"
        ordering = ['user__first_name_ar']
        indexes = [
            models.Index(fields=['dropout_risk']),
            models.Index(fields=['learning_style']),
            models.Index(fields=['last_analysis_date']),
        ]
    
    def __str__(self):
        return f"الملف الذكي - {self.user.display_name}"
    
    @property
    def overall_risk_score(self):
        """نقاط المخاطر الإجمالية"""
        risk_scores = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4,
        }
        dropout_score = risk_scores.get(self.dropout_risk, 1)
        stress_score = risk_scores.get(self.stress_level, 1)
        return (dropout_score + stress_score) / 2
    
    @property
    def needs_attention(self):
        """يحتاج لانتباه"""
        return (self.dropout_risk in ['HIGH', 'CRITICAL'] or 
                self.stress_level in ['HIGH', 'CRITICAL'] or
                float(self.motivation_level) < 30)


class TeacherAIProfile(models.Model):
    """الملف الذكي للأستاذ"""
    
    TEACHING_EFFECTIVENESS = [
        ('EXCELLENT', 'ممتاز'),
        ('VERY_GOOD', 'جيد جداً'),
        ('GOOD', 'جيد'),
        ('SATISFACTORY', 'مرضي'),
        ('NEEDS_IMPROVEMENT', 'يحتاج تحسين'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=False,
                               related_name='teacher_ai_profile', verbose_name="الأستاذ")
    
    # تحليل فعالية التدريس
    teaching_effectiveness = models.CharField(max_length=20, choices=TEACHING_EFFECTIVENESS,
                                           default='SATISFACTORY', verbose_name="فعالية التدريس")
    student_satisfaction_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0.00,
                                                 validators=[MinValueValidator(0), MaxValueValidator(5)],
                                                 verbose_name="متوسط رضا الطلاب")
    course_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                                            verbose_name="معدل نجاح المقررات")
    
    # أسلوب التدريس
    teaching_style = models.JSONField(default=dict, verbose_name="أسلوب التدريس")
    preferred_methods = models.JSONField(default=list, verbose_name="الأساليب المفضلة")
    technology_adoption = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                                            verbose_name="تبني التكنولوجيا")
    
    # تحليل الأداء
    workload_balance = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="توازن العبء")
    research_activity = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)],
                                          verbose_name="النشاط البحثي")
    collaboration_index = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                                            verbose_name="مؤشر التعاون")
    
    # التوصيات المهنية
    development_areas = models.JSONField(default=list, verbose_name="مجالات التطوير")
    recommended_training = models.JSONField(default=list, verbose_name="التدريب المُوصى به")
    career_growth_path = models.JSONField(default=dict, verbose_name="مسار النمو المهني")
    
    # التحليل السلوكي
    engagement_with_students = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                                 validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                 verbose_name="التفاعل مع الطلاب")
    innovation_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="نقاط الابتكار")
    
    # معلومات التحديث
    last_evaluation_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ آخر تقييم")
    evaluation_frequency = models.CharField(max_length=20, default='SEMESTER',
                                          choices=[
                                              ('SEMESTER', 'فصلي'),
                                              ('ANNUAL', 'سنوي'),
                                              ('BI_ANNUAL', 'نصف سنوي'),
                                          ], verbose_name="تكرار التقييم")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "الملف الذكي للأستاذ"
        verbose_name_plural = "الملفات الذكية للأساتذة"
        ordering = ['user__first_name_ar']
        indexes = [
            models.Index(fields=['teaching_effectiveness']),
            models.Index(fields=['student_satisfaction_avg']),
            models.Index(fields=['last_evaluation_date']),
        ]
    
    def __str__(self):
        return f"الملف الذكي - {self.user.display_name}"
    
    @property
    def overall_performance_score(self):
        """نقاط الأداء الإجمالية"""
        scores = [
            float(self.student_satisfaction_avg) * 20,  # تحويل من 5 إلى 100
            float(self.course_success_rate),
            float(self.engagement_with_students),
            float(self.innovation_score),
        ]
        return sum(scores) / len(scores)


class AIRecommendation(models.Model):
    """التوصيات الذكية"""
    
    RECOMMENDATION_TYPES = [
        ('COURSE', 'مقرر'),
        ('MAJOR', 'تخصص'),
        ('CAREER', 'مهنة'),
        ('STUDY_PLAN', 'خطة دراسية'),
        ('INTERVENTION', 'تدخل'),
        ('IMPROVEMENT', 'تحسين'),
        ('RESOURCE', 'مورد'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'في الانتظار'),
        ('ACCEPTED', 'مقبول'),
        ('REJECTED', 'مرفوض'),
        ('IMPLEMENTED', 'مُنفذ'),
        ('EXPIRED', 'منتهي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستخدم المستهدف
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='ai_recommendations', verbose_name="المستخدم")
    
    # نوع التوصية
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES,
                                         verbose_name="نوع التوصية")
    title = models.CharField(max_length=200, verbose_name="عنوان التوصية")
    description = models.TextField(verbose_name="وصف التوصية")
    
    # تفاصيل التوصية
    recommendation_data = models.JSONField(default=dict, verbose_name="بيانات التوصية")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, 
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="نقاط الثقة")
    
    # الأولوية والحالة
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM',
                              verbose_name="الأولوية")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="الحالة")
    
    # النموذج المستخدم
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='recommendations', verbose_name="النموذج المستخدم")
    
    # التواريخ المهمة
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="صالح حتى")
    implemented_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التنفيذ")
    
    # ردود الأفعال
    user_feedback = models.TextField(blank=True, verbose_name="تعليق المستخدم")
    feedback_rating = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name="تقييم التوصية")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "توصية ذكية"
        verbose_name_plural = "التوصيات الذكية"
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['recommendation_type', 'priority']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.display_name}"
    
    @property
    def is_valid(self):
        """هل التوصية سارية"""
        if self.valid_until:
            return timezone.now() <= self.valid_until
        return True
    
    @property
    def is_high_confidence(self):
        """توصية عالية الثقة"""
        return float(self.confidence_score) >= 0.8


class PredictiveAnalytics(models.Model):
    """التحليلات التنبؤية"""
    
    PREDICTION_TYPES = [
        ('STUDENT_SUCCESS', 'نجاح الطالب'),
        ('DROPOUT_RISK', 'خطر التسرب'),
        ('ENROLLMENT_FORECAST', 'توقع التسجيل'),
        ('RESOURCE_DEMAND', 'طلب الموارد'),
        ('FINANCIAL_FORECAST', 'توقع مالي'),
        ('PERFORMANCE_TREND', 'اتجاه الأداء'),
        ('CAPACITY_PLANNING', 'تخطيط السعة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # نوع التنبؤ
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES,
                                     verbose_name="نوع التنبؤ")
    name = models.CharField(max_length=200, verbose_name="اسم التحليل")
    description = models.TextField(verbose_name="وصف التحليل")
    
    # المستخدم أو المجموعة المستهدفة
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='predictive_analytics', verbose_name="المستخدم المستهدف")
    target_group = models.CharField(max_length=100, blank=True, verbose_name="المجموعة المستهدفة")
    
    # النموذج والبيانات
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                               related_name='predictions', verbose_name="النموذج المستخدم")
    input_data = models.JSONField(default=dict, verbose_name="البيانات المدخلة")
    
    # نتائج التنبؤ
    prediction_result = models.JSONField(default=dict, verbose_name="نتيجة التنبؤ")
    confidence_level = models.DecimalField(max_digits=5, decimal_places=4,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="مستوى الثقة")
    
    # التوقيت والصلاحية
    prediction_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التنبؤ")
    forecast_horizon = models.CharField(max_length=50, verbose_name="أفق التنبؤ")  # "1 month", "1 semester"
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="صالح حتى")
    
    # التحقق من الدقة
    actual_result = models.JSONField(default=dict, blank=True, verbose_name="النتيجة الفعلية")
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(1)],
                                       verbose_name="نقاط الدقة")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_predictions',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "تحليل تنبؤي"
        verbose_name_plural = "التحليلات التنبؤية"
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['prediction_type', 'prediction_date']),
            models.Index(fields=['target_user']),
            models.Index(fields=['ai_model']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_prediction_type_display()}"


class SmartAssistant(models.Model):
    """المساعد الذكي"""
    
    ASSISTANT_TYPES = [
        ('STUDENT', 'مساعد طلابي'),
        ('TEACHER', 'مساعد أكاديمي'),
        ('ADMIN', 'مساعد إداري'),
        ('FINANCIAL', 'مساعد مالي'),
        ('GENERAL', 'مساعد عام'),
    ]
    
    CAPABILITY_LEVELS = [
        ('BASIC', 'أساسي'),
        ('INTERMEDIATE', 'متوسط'),
        ('ADVANCED', 'متقدم'),
        ('EXPERT', 'خبير'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المساعد
    name_ar = models.CharField(max_length=100, verbose_name="اسم المساعد - عربي")
    name_en = models.CharField(max_length=100, verbose_name="اسم المساعد - إنجليزي")
    assistant_type = models.CharField(max_length=15, choices=ASSISTANT_TYPES,
                                    verbose_name="نوع المساعد")
    
    # القدرات والمهارات
    capabilities = models.JSONField(default=list, verbose_name="القدرات")
    capability_level = models.CharField(max_length=15, choices=CAPABILITY_LEVELS,
                                      default='INTERMEDIATE', verbose_name="مستوى القدرة")
    supported_languages = models.JSONField(default=list, verbose_name="اللغات المدعومة")
    
    # النماذج المستخدمة
    nlp_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='nlp_assistants', verbose_name="نموذج معالجة اللغة")
    knowledge_base = models.JSONField(default=dict, verbose_name="قاعدة المعرفة")
    
    # إعدادات السلوك
    personality_traits = models.JSONField(default=dict, verbose_name="سمات الشخصية")
    response_style = models.CharField(max_length=50, default='FRIENDLY',
                                    verbose_name="أسلوب الرد")
    
    # إحصائيات الاستخدام
    total_interactions = models.IntegerField(default=0, verbose_name="إجمالي التفاعلات")
    successful_responses = models.IntegerField(default=0, verbose_name="الردود الناجحة")
    user_satisfaction_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0.00,
                                              validators=[MinValueValidator(0), MaxValueValidator(5)],
                                              verbose_name="متوسط رضا المستخدمين")
    
    # الحالة والإعدادات
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_learning_enabled = models.BooleanField(default=True, verbose_name="التعلم مُفعل")
    max_conversation_length = models.IntegerField(default=50, verbose_name="الحد الأقصى للمحادثة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_assistants',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "مساعد ذكي"
        verbose_name_plural = "المساعدون الأذكياء"
        ordering = ['assistant_type', 'name_ar']
        indexes = [
            models.Index(fields=['assistant_type', 'is_active']),
            models.Index(fields=['capability_level']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} ({self.get_assistant_type_display()})"
    
    @property
    def success_rate(self):
        """معدل النجاح"""
        if self.total_interactions > 0:
            return (self.successful_responses / self.total_interactions) * 100
        return 0


class ConversationLog(models.Model):
    """سجل المحادثات مع المساعد الذكي"""
    
    MESSAGE_TYPES = [
        ('USER', 'مستخدم'),
        ('ASSISTANT', 'مساعد'),
        ('SYSTEM', 'نظام'),
    ]
    
    SENTIMENT_TYPES = [
        ('POSITIVE', 'إيجابي'),
        ('NEGATIVE', 'سلبي'),
        ('NEUTRAL', 'محايد'),
        ('MIXED', 'مختلط'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المحادثة
    conversation_id = models.CharField(max_length=100, verbose_name="معرف المحادثة")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='conversation_logs', verbose_name="المستخدم")
    assistant = models.ForeignKey(SmartAssistant, on_delete=models.CASCADE,
                                related_name='conversation_logs', verbose_name="المساعد")
    
    # محتوى الرسالة
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES,
                                  verbose_name="نوع الرسالة")
    message_content = models.TextField(verbose_name="محتوى الرسالة")
    message_language = models.CharField(max_length=5, default='ar', verbose_name="لغة الرسالة")
    
    # تحليل المشاعر
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_TYPES, null=True, blank=True,
                               verbose_name="المشاعر")
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                        validators=[MinValueValidator(-1), MaxValueValidator(1)],
                                        verbose_name="نقاط المشاعر")
    
    # معلومات التفاعل
    response_time_ms = models.IntegerField(default=0, verbose_name="وقت الرد (ميلي ثانية)")
    was_helpful = models.BooleanField(null=True, blank=True, verbose_name="كان مفيداً")
    user_rating = models.IntegerField(null=True, blank=True,
                                    validators=[MinValueValidator(1), MaxValueValidator(5)],
                                    verbose_name="تقييم المستخدم")
    
    # معلومات إضافية
    context_data = models.JSONField(default=dict, verbose_name="بيانات السياق")
    intent_detected = models.CharField(max_length=100, blank=True, verbose_name="النية المكتشفة")
    entities_extracted = models.JSONField(default=list, verbose_name="الكيانات المستخرجة")
    
    # معلومات تقنية
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    
    class Meta:
        verbose_name = "سجل محادثة"
        verbose_name_plural = "سجلات المحادثات"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['conversation_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['assistant', 'timestamp']),
            models.Index(fields=['sentiment']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.assistant.name_ar} - {self.timestamp}"


# إضافة النموذج المطلوب للتوافق
class StudentPerformancePrediction(models.Model):
    """تنبؤات أداء الطلاب - نموذج التوافق"""
    
    RISK_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='smart_ai_performance_predictions', verbose_name="الطالب")
    
    # تنبؤات الأداء
    predicted_gpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                      verbose_name="المعدل المتوقع")
    success_probability = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                            validators=[MinValueValidator(0), MaxValueValidator(1)],
                                            verbose_name="احتمالية النجاح")
    dropout_risk = models.CharField(max_length=10, choices=RISK_LEVELS, default='LOW',
                                  verbose_name="خطر التسرب")
    
    # بيانات التنبؤ
    prediction_data = models.JSONField(default=dict, verbose_name="بيانات التنبؤ")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="مستوى الثقة")
    
    # التواريخ
    prediction_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التنبؤ")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="صالح حتى")
    
    class Meta:
        verbose_name = "تنبؤ أداء طالب"
        verbose_name_plural = "تنبؤات أداء الطلاب"
        ordering = ['-prediction_date']
    
    def __str__(self):
        return f"تنبؤ أداء - {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.username}"


class LearningAnalytics(models.Model):
    """تحليلات التعلم"""
    
    ANALYTICS_TYPES = [
        ('ENGAGEMENT', 'التفاعل'),
        ('PROGRESS', 'التقدم'),
        ('PERFORMANCE', 'الأداء'),
        ('BEHAVIOR', 'السلوك'),
        ('COMPETENCY', 'الكفاءة'),
        ('PREDICTIVE', 'تنبؤي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستخدم والمقرر
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='learning_analytics', verbose_name="المستخدم")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='learning_analytics', verbose_name="المقرر")
    
    # نوع التحليل
    analytics_type = models.CharField(max_length=15, choices=ANALYTICS_TYPES,
                                    verbose_name="نوع التحليل")
    
    # البيانات المحللة
    raw_data = models.JSONField(default=dict, verbose_name="البيانات الخام")
    processed_data = models.JSONField(default=dict, verbose_name="البيانات المعالجة")
    insights = models.JSONField(default=dict, verbose_name="الرؤى")
    
    # المقاييس الرئيسية
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="نقاط التفاعل")
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                                            verbose_name="نسبة التقدم")
    mastery_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                      validators=[MinValueValidator(0), MaxValueValidator(100)],
                                      verbose_name="مستوى الإتقان")
    
    # التوصيات
    recommendations = models.JSONField(default=list, verbose_name="التوصيات")
    action_items = models.JSONField(default=list, verbose_name="عناصر العمل")
    
    # فترة التحليل
    analysis_period_start = models.DateTimeField(verbose_name="بداية فترة التحليل")
    analysis_period_end = models.DateTimeField(verbose_name="نهاية فترة التحليل")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تحليل تعلم"
        verbose_name_plural = "تحليلات التعلم"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'analytics_type']),
            models.Index(fields=['course', 'analytics_type']),
            models.Index(fields=['analysis_period_start', 'analysis_period_end']),
        ]
    
    def __str__(self):
        course_name = f" - {self.course.name_ar}" if self.course else ""
        return f"{self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.username} - {self.get_analytics_type_display()}{course_name}"


# إضافة النموذج المطلوب للتوافق
class AIChatBot(models.Model):
    """روبوت الدردشة الذكي - نموذج التوافق"""
    
    BOT_TYPES = [
        ('STUDENT_SUPPORT', 'دعم طلابي'),
        ('ACADEMIC_ADVISOR', 'مستشار أكاديمي'),
        ('TECHNICAL_SUPPORT', 'دعم تقني'),
        ('GENERAL_INFO', 'معلومات عامة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الروبوت
    name = models.CharField(max_length=100, verbose_name="اسم الروبوت")
    bot_type = models.CharField(max_length=20, choices=BOT_TYPES, verbose_name="نوع الروبوت")
    description = models.TextField(verbose_name="وصف الروبوت")
    
    # إعدادات الروبوت
    personality_traits = models.JSONField(default=dict, verbose_name="سمات الشخصية")
    knowledge_base = models.JSONField(default=dict, verbose_name="قاعدة المعرفة")
    response_templates = models.JSONField(default=list, verbose_name="قوالب الرد")
    
    # الفريق والصيانة
    developers = models.ManyToManyField(User, related_name='developed_chatbots', blank=True,
                                      verbose_name="المطورون")
    maintainers = models.ManyToManyField(User, related_name='maintained_chatbots', blank=True,
                                       verbose_name="فريق الصيانة")
    
    # إحصائيات
    total_conversations = models.IntegerField(default=0, verbose_name="إجمالي المحادثات")
    satisfaction_score = models.DecimalField(max_digits=4, decimal_places=2, default=0.00,
                                           validators=[MinValueValidator(0), MaxValueValidator(5)],
                                           verbose_name="نقاط الرضا")
    
    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "روبوت دردشة ذكي"
        verbose_name_plural = "روبوتات الدردشة الذكية"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_bot_type_display()}"


# إضافة نموذج رسائل الدردشة
class ChatMessage(models.Model):
    """رسائل الدردشة - نموذج التوافق"""
    
    SENDER_TYPES = [
        ('USER', 'مستخدم'),
        ('BOT', 'روبوت'),
        ('SYSTEM', 'نظام'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات الرسالة
    chatbot = models.ForeignKey(AIChatBot, on_delete=models.CASCADE,
                              related_name='messages', verbose_name="روبوت الدردشة")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='chat_messages', verbose_name="المستخدم")
    
    # محتوى الرسالة
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES, verbose_name="نوع المرسل")
    message = models.TextField(verbose_name="نص الرسالة")
    
    # بيانات إضافية
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    conversation_id = models.CharField(max_length=100, verbose_name="معرف المحادثة")
    
    # التوقيت
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    
    class Meta:
        verbose_name = "رسالة دردشة"
        verbose_name_plural = "رسائل الدردشة"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.username} - {self.chatbot.name}"

class StudentPerformancePrediction(models.Model):
    """توقع أداء الطلاب"""
    
    RISK_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    PERFORMANCE_LEVELS = [
        ('EXCELLENT', 'ممتاز'),
        ('VERY_GOOD', 'جيد جداً'),
        ('GOOD', 'جيد'),
        ('SATISFACTORY', 'مرضي'),
        ('POOR', 'ضعيف'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # الطالب والمقرr
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='smart_ai_performance_predictions', verbose_name="الطالب")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='smart_ai_performance_predictions', verbose_name="المقرر")
    
    # التنبؤات
    predicted_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)],
                                        verbose_name="الدرجة المتوقعة")
    predicted_gpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                      validators=[MinValueValidator(0), MaxValueValidator(4)],
                                      verbose_name="المعدل المتوقع")
    performance_level = models.CharField(max_length=15, choices=PERFORMANCE_LEVELS,
                                       verbose_name="مستوى الأداء المتوقع")
    dropout_risk = models.CharField(max_length=10, choices=RISK_LEVELS, default='LOW',
                                  verbose_name="خطر التسرب")
    
    # مقاييس الثقة
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="نقاط الثقة")
    model_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(1)],
                                       verbose_name="دقة النموذج")
    
    # العوامل المؤثرة
    influencing_factors = models.JSONField(default=dict, verbose_name="العوامل المؤثرة")
    feature_importance = models.JSONField(default=dict, verbose_name="أهمية الميزات")
    
    # التوصيات
    recommendations = models.JSONField(default=list, verbose_name="التوصيات")
    intervention_suggestions = models.JSONField(default=list, verbose_name="اقتراحات التدخل")
    
    # فترة التنبؤ
    prediction_horizon = models.CharField(max_length=50, verbose_name="أفق التنبؤ")
    valid_from = models.DateTimeField(verbose_name="صالح من")
    valid_until = models.DateTimeField(verbose_name="صالح حتى")
    
    # النموذج المستخدم
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='student_predictions', verbose_name="النموذج المستخدم")
    
    # التحقق من الدقة
    actual_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)],
                                     verbose_name="الدرجة الفعلية")
    actual_gpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True,
                                   validators=[MinValueValidator(0), MaxValueValidator(4)],
                                   verbose_name="المعدل الفعلي")
    prediction_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                            validators=[MinValueValidator(0), MaxValueValidator(1)],
                                            verbose_name="دقة التنبؤ")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_student_predictions',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "توقع أداء طالب"
        verbose_name_plural = "توقعات أداء الطلاب"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'course']),
            models.Index(fields=['dropout_risk']),
            models.Index(fields=['performance_level']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]
    
    def __str__(self):
        course_name = f" - {self.course.name_ar}" if self.course else ""
        return f"{self.student.display_name} - {self.get_performance_level_display()}{course_name}"
    
    @property
    def is_valid(self):
        """هل التنبؤ ساري"""
        now = timezone.now()
        return self.valid_from <= now <= self.valid_until
    
    @property
    def needs_intervention(self):
        """يحتاج لتدخل"""
        return (self.dropout_risk in ['HIGH', 'CRITICAL'] or 
                self.performance_level in ['POOR', 'SATISFACTORY'])


class AIChatBot(models.Model):
    """روبوت المحادثة الذكي"""
    
    BOT_TYPES = [
        ('GENERAL', 'عام'),
        ('ACADEMIC', 'أكاديمي'),
        ('ADMINISTRATIVE', 'إداري'),
        ('TECHNICAL_SUPPORT', 'دعم تقني'),
        ('FINANCIAL', 'مالي'),
        ('STUDENT_SERVICES', 'خدمات طلابية'),
        ('ADMISSIONS', 'قبول'),
        ('LIBRARY', 'مكتبة'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('TRAINING', 'تحت التدريب'),
        ('MAINTENANCE', 'صيانة'),
        ('TESTING', 'اختبار'),
    ]
    
    LANGUAGE_CODES = [
        ('ar', 'العربية'),
        ('en', 'English'),
        ('ar-en', 'العربية والإنجليزية'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات البوت الأساسية
    name_ar = models.CharField(max_length=100, verbose_name="اسم البوت - عربي")
    name_en = models.CharField(max_length=100, verbose_name="اسم البوت - إنجليزي")
    bot_type = models.CharField(max_length=20, choices=BOT_TYPES, default='GENERAL',
                              verbose_name="نوع البوت")
    description_ar = models.TextField(verbose_name="وصف البوت - عربي")
    description_en = models.TextField(verbose_name="وصف البوت - إنجليزي")
    
    # إعدادات البوت
    avatar = models.ImageField(upload_to='chatbots/avatars/', blank=True, null=True,
                             verbose_name="صورة البوت")
    welcome_message_ar = models.TextField(verbose_name="رسالة الترحيب - عربي")
    welcome_message_en = models.TextField(verbose_name="رسالة الترحيب - إنجليزي")
    
    # إعدادات اللغة والسلوك
    supported_languages = models.CharField(max_length=10, choices=LANGUAGE_CODES,
                                         default='ar-en', verbose_name="اللغات المدعومة")
    personality_traits = models.JSONField(default=dict, verbose_name="سمات الشخصية")
    response_style = models.CharField(max_length=50, default='FRIENDLY',
                                    verbose_name="أسلوب الرد")
    
    # النماذج المستخدمة
    nlp_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='chatbots', verbose_name="نموذج معالجة اللغة")
    knowledge_base = models.JSONField(default=dict, verbose_name="قاعدة المعرفة")
    training_data = models.JSONField(default=list, verbose_name="بيانات التدريب")
    
    # القدرات والمهارات
    capabilities = models.JSONField(default=list, verbose_name="القدرات")
    integrations = models.JSONField(default=list, verbose_name="التكاملات")
    api_endpoints = models.JSONField(default=list, verbose_name="نقاط API")
    
    # إعدادات الحوار
    max_conversation_length = models.IntegerField(default=50, verbose_name="الحد الأقصى للمحادثة")
    context_memory_size = models.IntegerField(default=10, verbose_name="حجم ذاكرة السياق")
    response_timeout = models.IntegerField(default=30, verbose_name="مهلة الرد (ثانية)")
    
    # الحالة والإعدادات
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='INACTIVE',
                            verbose_name="الحالة")
    is_public = models.BooleanField(default=True, verbose_name="عام")
    is_learning_enabled = models.BooleanField(default=True, verbose_name="التعلم مُفعل")
    is_multilingual = models.BooleanField(default=True, verbose_name="متعدد اللغات")
    
    # إحصائيات الاستخدام
    total_conversations = models.IntegerField(default=0, verbose_name="إجمالي المحادثات")
    total_messages = models.IntegerField(default=0, verbose_name="إجمالي الرسائل")
    successful_responses = models.IntegerField(default=0, verbose_name="الردود الناجحة")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                                       validators=[MinValueValidator(0), MaxValueValidator(5)],
                                       verbose_name="متوسط التقييم")
    
    # إعدادات المطورين
    
    # معلومات الأمان
    access_permissions = models.JSONField(default=dict, verbose_name="صلاحيات الوصول")
    security_settings = models.JSONField(default=dict, verbose_name="إعدادات الأمان")
    rate_limiting = models.JSONField(default=dict, verbose_name="تحديد المعدل")
    
    # التسجيل والمراقبة
    logging_enabled = models.BooleanField(default=True, verbose_name="التسجيل مُفعل")
    analytics_enabled = models.BooleanField(default=True, verbose_name="التحليلات مُفعلة")
    monitoring_settings = models.JSONField(default=dict, verbose_name="إعدادات المراقبة")
    
    # معلومات الإصدار
    version = models.CharField(max_length=20, default='1.0.0', verbose_name="الإصدار")
    last_trained = models.DateTimeField(null=True, blank=True, verbose_name="آخر تدريب")
    next_maintenance = models.DateTimeField(null=True, blank=True, verbose_name="الصيانة القادمة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_chatbots',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "روبوت محادثة ذكي"
        verbose_name_plural = "روبوتات المحادثة الذكية"
        ordering = ['bot_type', 'name_ar']
        indexes = [
            models.Index(fields=['bot_type', 'status']),
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['supported_languages']),
        ]
    
    def __str__(self):
        return f"{self.name_ar} ({self.get_bot_type_display()})"
    
    @property
    def is_active(self):
        """هل البوت نشط"""
        return self.status == 'ACTIVE'
    
    @property
    def success_rate(self):
        """معدل النجاح"""
        if self.total_messages > 0:
            return (self.successful_responses / self.total_messages) * 100
        return 0
    
    @property
    def needs_training(self):
        """يحتاج لتدريب"""
        if not self.last_trained:
            return True
        # إذا لم يتم التدريب لأكثر من شهر
        one_month_ago = timezone.now() - timezone.timedelta(days=30)
        return self.last_trained < one_month_ago
    
    def get_welcome_message(self, language='ar'):
        """الحصول على رسالة الترحيب باللغة المحددة"""
        if language == 'en':
            return self.welcome_message_en
        return self.welcome_message_ar
    
    def get_name(self, language='ar'):
        """الحصول على اسم البوت باللغة المحددة"""
        if language == 'en':
            return self.name_en
        return self.name_ar
    
    def get_description(self, language='ar'):
        """الحصول على وصف البوت باللغة المحددة"""
        if language == 'en':
            return self.description_en
        return self.description_ar


class ChatMessage(models.Model):
    """رسائل المحادثة مع البوت"""
    
    MESSAGE_TYPES = [
        ('USER', 'مستخدم'),
        ('BOT', 'بوت'),
        ('SYSTEM', 'نظام'),
    ]
    
    SENTIMENT_TYPES = [
        ('POSITIVE', 'إيجابي'),
        ('NEGATIVE', 'سلبي'),
        ('NEUTRAL', 'محايد'),
        ('MIXED', 'مختلط'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات المحادثة
    conversation_id = models.CharField(max_length=100, verbose_name="معرف المحادثة")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الجلسة")
    
    # المشاركون
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='chat_messages', verbose_name="المستخدم")
    chatbot = models.ForeignKey(AIChatBot, on_delete=models.CASCADE,
                              related_name='messages', verbose_name="البوت")
    
    # محتوى الرسالة
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES,
                                  verbose_name="نوع الرسالة")
    content = models.TextField(verbose_name="محتوى الرسالة")
    language = models.CharField(max_length=5, default='ar', verbose_name="اللغة")
    
    # تحليل المحتوى
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_TYPES, null=True, blank=True,
                               verbose_name="المشاعر")
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                        validators=[MinValueValidator(-1), MaxValueValidator(1)],
                                        verbose_name="نقاط المشاعر")
    intent = models.CharField(max_length=100, blank=True, verbose_name="النية")
    entities = models.JSONField(default=list, verbose_name="الكيانات المستخرجة")
    
    # معلومات الاستجابة (للرسائل من البوت)
    response_time_ms = models.IntegerField(null=True, blank=True,
                                         verbose_name="وقت الرد (ميلي ثانية)")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="نقاط الثقة")
    is_fallback = models.BooleanField(default=False, verbose_name="رد احتياطي")
    
    # تقييم المستخدم
    user_feedback = models.CharField(max_length=20, blank=True,
                                   choices=[
                                       ('HELPFUL', 'مفيد'),
                                       ('NOT_HELPFUL', 'غير مفيد'),
                                       ('IRRELEVANT', 'غير ذي صلة'),
                                       ('INCORRECT', 'غير صحيح'),
                                   ], verbose_name="تقييم المستخدم")
    rating = models.IntegerField(null=True, blank=True,
                               validators=[MinValueValidator(1), MaxValueValidator(5)],
                               verbose_name="التقييم")
    
    # السياق والبيانات الإضافية
    context_data = models.JSONField(default=dict, verbose_name="بيانات السياق")
    metadata = models.JSONField(default=dict, verbose_name="بيانات إضافية")
    
    # المرفقات
    attachments = models.JSONField(default=list, verbose_name="المرفقات")
    
    # معلومات تقنية
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    is_flagged = models.BooleanField(default=False, verbose_name="مُعلم")
    is_deleted = models.BooleanField(default=False, verbose_name="محذوف")
    
    class Meta:
        verbose_name = "رسالة محادثة"
        verbose_name_plural = "رسائل المحادثة"
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['chatbot', 'timestamp']),
            models.Index(fields=['message_type']),
            models.Index(fields=['sentiment']),
        ]
    
    def __str__(self):
        return f"{self.conversation_id} - {self.get_message_type_display()} - {self.timestamp}"
    
    @property
    def is_from_user(self):
        """هل الرسالة من المستخدم"""
        return self.message_type == 'USER'
    
    @property
    def is_from_bot(self):
        """هل الرسالة من البوت"""
        return self.message_type == 'BOT'
    
    @property
    def content_preview(self):
        """معاينة المحتوى"""
        if len(self.content) > 100:
            return self.content[:97] + "..."
        return self.content


class SmartRecommendation(models.Model):
    """التوصيات الذكية للمستخدمين"""
    
    RECOMMENDATION_TYPES = [
        ('COURSE', 'مقرر دراسي'),
        ('STUDY_PATH', 'مسار دراسي'),
        ('CAREER', 'مسار مهني'),
        ('SKILL', 'مهارة'),
        ('ACTIVITY', 'نشاط'),
        ('RESOURCE', 'مورد تعليمي'),
        ('MENTOR', 'مرشد'),
        ('GROUP', 'مجموعة دراسية'),
        ('EVENT', 'فعالية'),
        ('IMPROVEMENT', 'تحسين'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'في الانتظار'),
        ('VIEWED', 'تم عرضه'),
        ('ACCEPTED', 'مقبول'),
        ('REJECTED', 'مرفوض'),
        ('IMPLEMENTED', 'مُنفذ'),
        ('EXPIRED', 'منتهي الصلاحية'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المستخدم المستهدف
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='smart_recommendations', verbose_name="المستخدم")
    
    # نوع التوصية
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES,
                                         verbose_name="نوع التوصية")
    title = models.CharField(max_length=200, verbose_name="عنوان التوصية")
    description = models.TextField(verbose_name="وصف التوصية")
    
    # تفاصيل التوصية
    recommendation_data = models.JSONField(default=dict, verbose_name="بيانات التوصية")
    reasoning = models.TextField(verbose_name="المبرر")
    expected_benefits = models.JSONField(default=list, verbose_name="الفوائد المتوقعة")
    
    # مقاييس الثقة والأولوية
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="نقاط الثقة")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM',
                              verbose_name="الأولوية")
    relevance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)],
                                        verbose_name="نقاط الصلة")
    
    # الحالة والحياة
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING',
                            verbose_name="الحالة")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="صالح حتى")
    
    # النموذج المستخدم
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='smart_recommendations', verbose_name="النموذج المستخدم")
    
    # البيانات المستخدمة في التوصية
    input_features = models.JSONField(default=dict, verbose_name="الميزات المدخلة")
    feature_importance = models.JSONField(default=dict, verbose_name="أهمية الميزات")
    
    # تقييم المستخدم
    user_rating = models.IntegerField(null=True, blank=True,
                                    validators=[MinValueValidator(1), MaxValueValidator(5)],
                                    verbose_name="تقييم المستخدم")
    user_feedback = models.TextField(blank=True, verbose_name="تعليق المستخدم")
    was_helpful = models.BooleanField(null=True, blank=True, verbose_name="كانت مفيدة")
    
    # تتبع التفاعل
    viewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ العرض")
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الرد")
    implemented_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التنفيذ")
    
    # معلومات إضافية
    tags = models.JSONField(default=list, verbose_name="العلامات")
    related_recommendations = models.JSONField(default=list, verbose_name="التوصيات المرتبطة")
    success_metrics = models.JSONField(default=dict, verbose_name="مقاييس النجاح")
    
    # الإعدادات
    auto_implement = models.BooleanField(default=False, verbose_name="تنفيذ تلقائي")
    notification_sent = models.BooleanField(default=False, verbose_name="تم إرسال الإشعار")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "توصية ذكية"
        verbose_name_plural = "التوصيات الذكية"
        ordering = ['-priority', '-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['recommendation_type', 'priority']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def is_valid(self):
        """هل التوصية سارية"""
        if self.valid_until:
            return timezone.now() <= self.valid_until
        return True
    
    @property
    def is_high_confidence(self):
        """توصية عالية الثقة"""
        return float(self.confidence_score) >= 0.8
    
    @property
    def is_urgent(self):
        """توصية عاجلة"""
        return self.priority == 'URGENT'
    
    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء الصلاحية"""
        if self.valid_until:
            delta = self.valid_until - timezone.now()
            return max(0, delta.days)
        return None
    
    def mark_as_viewed(self):
        """تمييز كمُشاهدة"""
        if self.status == 'PENDING':
            self.status = 'VIEWED'
            self.viewed_at = timezone.now()
            self.save(update_fields=['status', 'viewed_at'])
    
    def accept(self):
        """قبول التوصية"""
        self.status = 'ACCEPTED'
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])
    
    def reject(self):
        """رفض التوصية"""
        self.status = 'REJECTED'
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])
    
    def implement(self):
        """تنفيذ التوصية"""
        self.status = 'IMPLEMENTED'
        self.implemented_at = timezone.now()
        self.save(update_fields=['status', 'implemented_at'])


class AISecurityAlert(models.Model):
    """تنبيهات أمنية ذكية"""
    
    ALERT_TYPES = [
        ('THREAT_DETECTED', 'تهديد مكتشف'),
        ('ANOMALY_DETECTED', 'شذوذ مكتشف'),
        ('BREACH_ATTEMPT', 'محاولة اختراق'),
        ('SUSPICIOUS_ACTIVITY', 'نشاط مشبوه'),
        ('POLICY_VIOLATION', 'انتهاك سياسة'),
        ('MALWARE_DETECTED', 'برمجية خبيثة مكتشفة'),
        ('UNAUTHORIZED_ACCESS', 'وصول غير مصرح'),
        ('DATA_LEAK', 'تسريب بيانات'),
        ('SYSTEM_COMPROMISE', 'اختراق نظام'),
        ('BEHAVIORAL_ANOMALY', 'شذوذ سلوكي'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
        ('EMERGENCY', 'طوارئ'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'جديد'),
        ('ACKNOWLEDGED', 'مُؤكد'),
        ('INVESTIGATING', 'قيد التحقيق'),
        ('RESOLVED', 'محلول'),
        ('FALSE_POSITIVE', 'إيجابي كاذب'),
        ('ESCALATED', 'مُصعد'),
        ('CLOSED', 'مُغلق'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # معلومات التنبيه الأساسية
    alert_id = models.CharField(max_length=50, unique=True, verbose_name="معرف التنبيه")
    alert_type = models.CharField(max_length=25, choices=ALERT_TYPES, verbose_name="نوع التنبيه")
    title = models.CharField(max_length=200, verbose_name="عنوان التنبيه")
    description = models.TextField(verbose_name="وصف التنبيه")
    
    # الخطورة والحالة
    severity = models.CharField(max_length=15, choices=SEVERITY_LEVELS, verbose_name="مستوى الخطورة")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='NEW',
                            verbose_name="حالة التنبيه")
    
    # النموذج الذكي المكتشف
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='security_alerts', verbose_name="النموذج المكتشف")
    
    # بيانات الكشف
    detection_data = models.JSONField(default=dict, verbose_name="بيانات الكشف")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4,
                                         validators=[MinValueValidator(0), MaxValueValidator(1)],
                                         verbose_name="نقاط الثقة")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   verbose_name="نقاط المخاطر")
    
    # المصدر والهدف
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP المصدر")
    source_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='security_alerts_as_source',
                                  verbose_name="المستخدم المصدر")
    affected_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='security_alerts_affected',
                                    verbose_name="المستخدم المتأثر")
    affected_systems = models.JSONField(default=list, verbose_name="الأنظمة المتأثرة")
    
    # تفاصيل التحليل
    analysis_results = models.JSONField(default=dict, verbose_name="نتائج التحليل")
    indicators_of_compromise = models.JSONField(default=list, verbose_name="مؤشرات الاختراق")
    attack_vector = models.CharField(max_length=100, blank=True, verbose_name="متجه الهجوم")
    mitigation_suggestions = models.JSONField(default=list, verbose_name="اقتراحات التخفيف")
    
    # الاستجابة التلقائية
    auto_response_taken = models.BooleanField(default=False, verbose_name="تم اتخاذ استجابة تلقائية")
    response_actions = models.JSONField(default=list, verbose_name="إجراءات الاستجابة")
    containment_status = models.CharField(max_length=20, default='NONE',
                                        choices=[
                                            ('NONE', 'لا يوجد'),
                                            ('PARTIAL', 'جزئي'),
                                            ('COMPLETE', 'كامل'),
                                        ], verbose_name="حالة الاحتواء")
    
    # التصعيد والتعيين
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_security_alerts',
                                  verbose_name="مُعيّن إلى")
    escalated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='escalated_security_alerts',
                                   verbose_name="مُصعد إلى")
    escalation_reason = models.TextField(blank=True, verbose_name="سبب التصعيد")
    
    # التوقيت
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الكشف")
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التأكيد")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    # المتابعة والتحقيق
    investigation_notes = models.TextField(blank=True, verbose_name="ملاحظات التحقيق")
    resolution_notes = models.TextField(blank=True, verbose_name="ملاحظات الحل")
    lessons_learned = models.TextField(blank=True, verbose_name="الدروس المستفادة")
    
    # التنبيهات والإشعارات
    notifications_sent = models.JSONField(default=list, verbose_name="الإشعارات المرسلة")
    notification_channels = models.JSONField(default=list, verbose_name="قنوات الإشعارات")
    
    # معلومات إضافية
    tags = models.JSONField(default=list, verbose_name="العلامات")
    related_alerts = models.JSONField(default=list, verbose_name="التنبيهات المرتبطة")
    evidence_collected = models.JSONField(default=list, verbose_name="الأدلة المجمعة")
    
    # التقييم والتحسين
    false_positive_feedback = models.TextField(blank=True, verbose_name="تعليق الإيجابي الكاذب")
    accuracy_rating = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name="تقييم الدقة")
    
    # معلومات تقنية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_ai_security_alerts',
                                 verbose_name="أُنشأ بواسطة")
    
    class Meta:
        verbose_name = "تنبيه أمني ذكي"
        verbose_name_plural = "التنبيهات الأمنية الذكية"
        ordering = ['-severity', '-detected_at']
        indexes = [
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['status']),
            models.Index(fields=['detected_at']),
            models.Index(fields=['source_ip']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.alert_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.alert_id:
            self.alert_id = self.generate_alert_id()
        super().save(*args, **kwargs)
    
    def generate_alert_id(self):
        """توليد معرف تنبيه فريد"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        alert_code = self.alert_type[:3].upper()
        return f"SA-{alert_code}-{timestamp}"
    
    @property
    def is_critical(self):
        """هل التنبيه حرج"""
        return self.severity in ['CRITICAL', 'EMERGENCY']
    
    @property
    def is_active(self):
        """هل التنبيه نشط"""
        return self.status not in ['RESOLVED', 'FALSE_POSITIVE', 'CLOSED']
    
    @property
    def response_time(self):
        """وقت الاستجابة"""
        if self.acknowledged_at:
            return self.acknowledged_at - self.detected_at
        return None
    
    @property
    def resolution_time(self):
        """وقت الحل"""
        if self.resolved_at:
            return self.resolved_at - self.detected_at
        return None
    
    @property
    def is_high_confidence(self):
        """تنبيه عالي الثقة"""
        return float(self.confidence_score) >= 0.8
    
    def acknowledge(self, user, notes=""):
        """تأكيد التنبيه"""
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_at = timezone.now()
        self.assigned_to = user
        if notes:
            self.investigation_notes = notes
        self.save(update_fields=['status', 'acknowledged_at', 'assigned_to', 'investigation_notes'])
    
    def resolve(self, user, notes=""):
        """حل التنبيه"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes'])
    
    def mark_false_positive(self, user, feedback=""):
        """تمييز كإيجابي كاذب"""
        self.status = 'FALSE_POSITIVE'
        self.resolved_at = timezone.now()
        self.false_positive_feedback = feedback
        self.save(update_fields=['status', 'resolved_at', 'false_positive_feedback'])
    
    def escalate(self, user, reason=""):
        """تصعيد التنبيه"""
        self.status = 'ESCALATED'
        self.escalated_to = user
        self.escalation_reason = reason
        self.save(update_fields=['status', 'escalated_to', 'escalation_reason'])
