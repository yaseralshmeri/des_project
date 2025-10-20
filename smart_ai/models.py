# نماذج الذكاء الاصطناعي المتقدم
# Advanced AI Models for University Management System

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from students.models import Student
from courses.models import Course
import json

class AIAnalyticsModel(models.Model):
    """نموذج أساسي لتحليلات الذكاء الاصطناعي"""
    
    name = models.CharField(max_length=200, verbose_name="اسم النموذج")
    description = models.TextField(verbose_name="وصف النموذج")
    model_type = models.CharField(max_length=50, choices=[
        ('student_performance', 'تحليل أداء الطلاب'),
        ('financial_prediction', 'التنبؤ المالي'),
        ('academic_recommendation', 'التوصيات الأكاديمية'),
        ('anomaly_detection', 'كشف الشذوذ'),
        ('predictive_analytics', 'التحليل التنبؤي'),
    ], verbose_name="نوع النموذج")
    
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    accuracy_score = models.FloatField(default=0.0, verbose_name="دقة النموذج")
    last_trained = models.DateTimeField(null=True, blank=True, verbose_name="آخر تدريب")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "نموذج ذكاء اصطناعي"
        verbose_name_plural = "نماذج الذكاء الاصطناعي"

class StudentPerformancePrediction(models.Model):
    """نموذج التنبؤ بأداء الطلاب"""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="المقرر")
    
    # عوامل التنبؤ
    current_gpa = models.FloatField(verbose_name="المعدل التراكمي الحالي")
    attendance_rate = models.FloatField(verbose_name="معدل الحضور")
    assignment_completion = models.FloatField(verbose_name="معدل إنجاز المهام")
    participation_score = models.FloatField(verbose_name="درجة المشاركة")
    
    # التنبؤات
    predicted_grade = models.CharField(max_length=5, verbose_name="الدرجة المتوقعة")
    success_probability = models.FloatField(verbose_name="احتمالية النجاح")
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي'),
        ('critical', 'حرج'),
    ], verbose_name="مستوى المخاطر")
    
    # توصيات
    recommendations = models.JSONField(default=dict, verbose_name="التوصيات")
    intervention_needed = models.BooleanField(default=False, verbose_name="يحتاج تدخل")
    
    prediction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "تنبؤ أداء الطالب"
        verbose_name_plural = "تنبؤات أداء الطلاب"
        unique_together = ['student', 'course']

class AIChatBot(models.Model):
    """المساعد الذكي للطلاب والموظفين"""
    
    CHAT_TYPES = [
        ('student_support', 'دعم الطلاب'),
        ('academic_advisor', 'مستشار أكاديمي'),
        ('financial_assistant', 'مساعد مالي'),
        ('administrative_help', 'مساعدة إدارية'),
        ('technical_support', 'الدعم التقني'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="المستخدم")
    chat_type = models.CharField(max_length=50, choices=CHAT_TYPES, verbose_name="نوع المحادثة")
    session_id = models.CharField(max_length=100, unique=True, verbose_name="معرف الجلسة")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مساعد ذكي"
        verbose_name_plural = "المساعدات الذكية"

class ChatMessage(models.Model):
    """رسائل المحادثة مع المساعد الذكي"""
    
    chatbot = models.ForeignKey(AIChatBot, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(verbose_name="الرسالة")
    response = models.TextField(verbose_name="الرد")
    
    # معلومات السياق
    user_intent = models.CharField(max_length=100, blank=True, verbose_name="قصد المستخدم")
    confidence_score = models.FloatField(default=0.0, verbose_name="درجة الثقة")
    
    # حالة الرسالة
    is_resolved = models.BooleanField(default=False, verbose_name="محلولة")
    feedback_rating = models.IntegerField(null=True, blank=True, 
                                        choices=[(i, i) for i in range(1, 6)], 
                                        verbose_name="تقييم الرد")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "رسالة محادثة"
        verbose_name_plural = "رسائل المحادثات"
        ordering = ['-timestamp']

class SmartRecommendation(models.Model):
    """نظام التوصيات الذكية"""
    
    RECOMMENDATION_TYPES = [
        ('course_selection', 'اختيار المقررات'),
        ('study_plan', 'خطة الدراسة'),
        ('career_guidance', 'التوجيه المهني'),
        ('scholarship', 'المنح الدراسية'),
        ('extracurricular', 'الأنشطة اللاصفية'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES, 
                                         verbose_name="نوع التوصية")
    
    title = models.CharField(max_length=200, verbose_name="عنوان التوصية")
    description = models.TextField(verbose_name="الوصف")
    priority_score = models.FloatField(verbose_name="أولوية التوصية")
    
    # بيانات التوصية
    recommended_items = models.JSONField(default=list, verbose_name="العناصر الموصى بها")
    reasoning = models.TextField(verbose_name="السبب والمنطق")
    
    # حالة التوصية
    is_viewed = models.BooleanField(default=False, verbose_name="تم العرض")
    is_accepted = models.BooleanField(default=False, verbose_name="تم القبول")
    feedback = models.TextField(blank=True, verbose_name="تعليقات الطالب")
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="تاريخ انتهاء الصلاحية")
    
    class Meta:
        verbose_name = "توصية ذكية"
        verbose_name_plural = "التوصيات الذكية"
        ordering = ['-priority_score', '-created_at']

class PredictiveAnalytics(models.Model):
    """تحليلات تنبؤية متقدمة"""
    
    ANALYSIS_TYPES = [
        ('enrollment_forecast', 'توقع التسجيل'),
        ('dropout_risk', 'مخاطر التسرب'),
        ('resource_planning', 'تخطيط الموارد'),
        ('financial_projection', 'الإسقاط المالي'),
        ('performance_trends', 'اتجاهات الأداء'),
    ]
    
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES, 
                                   verbose_name="نوع التحليل")
    title = models.CharField(max_length=200, verbose_name="عنوان التحليل")
    
    # بيانات الإدخال
    input_data = models.JSONField(verbose_name="بيانات الإدخال")
    parameters = models.JSONField(default=dict, verbose_name="المعاملات")
    
    # النتائج
    predictions = models.JSONField(verbose_name="التنبؤات")
    confidence_interval = models.JSONField(verbose_name="فترة الثقة")
    accuracy_metrics = models.JSONField(default=dict, verbose_name="مقاييس الدقة")
    
    # البيانات المرجعية
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="تم الإنشاء بواسطة")
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    # حالة التحليل
    is_approved = models.BooleanField(default=False, verbose_name="معتمد")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    
    class Meta:
        verbose_name = "تحليل تنبؤي"
        verbose_name_plural = "التحليلات التنبؤية"
        ordering = ['-analysis_date']

class AISecurityAlert(models.Model):
    """تنبيهات الأمان الذكية"""
    
    ALERT_TYPES = [
        ('login_anomaly', 'شذوذ في تسجيل الدخول'),
        ('data_breach_attempt', 'محاولة اختراق البيانات'),
        ('suspicious_activity', 'نشاط مشبوه'),
        ('system_intrusion', 'تسلل للنظام'),
        ('privilege_escalation', 'تصعيد الصلاحيات'),
        ('malware_detection', 'كشف برامج ضارة'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي'),
        ('critical', 'حرج'),
    ]
    
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES, verbose_name="نوع التنبيه")
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name="مستوى الخطورة")
    
    # تفاصيل التنبيه
    title = models.CharField(max_length=200, verbose_name="عنوان التنبيه")
    description = models.TextField(verbose_name="الوصف")
    affected_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="المستخدم المتأثر")
    
    # بيانات تقنية
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="معرف المتصفح")
    request_path = models.CharField(max_length=500, blank=True, verbose_name="مسار الطلب")
    
    # الاستجابة للتنبيه
    is_investigated = models.BooleanField(default=False, verbose_name="تم التحقيق")
    is_resolved = models.BooleanField(default=False, verbose_name="تم الحل")
    resolution_notes = models.TextField(blank=True, verbose_name="ملاحظات الحل")
    
    # التوقيتات
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الكشف")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحل")
    
    class Meta:
        verbose_name = "تنبيه أمني ذكي"
        verbose_name_plural = "تنبيهات الأمان الذكية"
        ordering = ['-detected_at', '-severity']

class SmartScheduling(models.Model):
    """نظام الجدولة الذكية"""
    
    name = models.CharField(max_length=200, verbose_name="اسم الجدولة")
    semester = models.CharField(max_length=50, verbose_name="الفصل الدراسي")
    academic_year = models.CharField(max_length=10, verbose_name="العام الدراسي")
    
    # خوارزميات الجدولة
    algorithm_used = models.CharField(max_length=50, choices=[
        ('genetic_algorithm', 'الخوارزمية الجينية'),
        ('simulated_annealing', 'التبريد المحاكي'),
        ('constraint_satisfaction', 'إشباع القيود'),
        ('hybrid_approach', 'النهج المختلط'),
    ], verbose_name="الخوارزمية المستخدمة")
    
    # معاملات التحسين
    optimization_criteria = models.JSONField(default=dict, verbose_name="معايير التحسين")
    constraints = models.JSONField(default=list, verbose_name="القيود")
    
    # النتائج
    schedule_data = models.JSONField(verbose_name="بيانات الجدول")
    fitness_score = models.FloatField(verbose_name="درجة الجودة")
    conflicts_resolved = models.IntegerField(default=0, verbose_name="التعارضات المحلولة")
    
    # حالة الجدولة
    is_optimal = models.BooleanField(default=False, verbose_name="أمثل")
    is_approved = models.BooleanField(default=False, verbose_name="معتمد")
    
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="منشئ الجدول")
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "جدولة ذكية"
        verbose_name_plural = "الجدولة الذكية"
        ordering = ['-generated_at']