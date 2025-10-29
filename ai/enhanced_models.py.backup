"""
Advanced AI Analytics and Recommendation System
نظام ذكاء اصطناعي متطور للتحليلات والتوصيات
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Student
import json

User = get_user_model()


class AIModel(models.Model):
    """
    AI/ML Model registry and management
    سجل وإدارة نماذج الذكاء الاصطناعي
    """
    MODEL_TYPES = [
        ('CLASSIFICATION', 'Classification'),
        ('REGRESSION', 'Regression'),
        ('CLUSTERING', 'Clustering'),
        ('ANOMALY_DETECTION', 'Anomaly Detection'),
        ('RECOMMENDATION', 'Recommendation'),
        ('PREDICTION', 'Prediction'),
        ('NLP', 'Natural Language Processing'),
        ('COMPUTER_VISION', 'Computer Vision'),
    ]
    
    STATUS_CHOICES = [
        ('TRAINING', 'Training'),
        ('TRAINED', 'Trained'),
        ('DEPLOYED', 'Deployed'),
        ('RETIRED', 'Retired'),
        ('FAILED', 'Failed'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=50, default='1.0.0')
    
    # Model configuration
    algorithm = models.CharField(max_length=100)
    hyperparameters = models.JSONField(default=dict)
    features = models.JSONField(default=list, help_text="List of features used by the model")
    target_variable = models.CharField(max_length=100, blank=True)
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    precision = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    recall = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    f1_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    rmse = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)
    
    # Model artifacts
    model_path = models.CharField(max_length=500, blank=True)
    model_size = models.BigIntegerField(null=True, blank=True, help_text="Model size in bytes")
    training_data_size = models.IntegerField(null=True, blank=True)
    
    # Status and lifecycle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRAINING')
    is_active = models.BooleanField(default=True)
    last_retrained = models.DateTimeField(null=True, blank=True)
    next_retrain_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'
        ordering = ['-created_at']
        unique_together = [['name', 'version']]
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class StudentPerformancePrediction(models.Model):
    """
    AI-based student performance predictions
    توقعات أداء الطلاب بالذكاء الاصطناعي
    """
    PREDICTION_TYPES = [
        ('GPA_PREDICTION', 'GPA Prediction'),
        ('GRADUATION_LIKELIHOOD', 'Graduation Likelihood'),
        ('DROPOUT_RISK', 'Dropout Risk'),
        ('COURSE_PERFORMANCE', 'Course Performance'),
        ('SEMESTER_PERFORMANCE', 'Semester Performance'),
        ('CAREER_RECOMMENDATION', 'Career Recommendation'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performance_predictions')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    
    # Prediction results
    predicted_value = models.FloatField()
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, null=True, blank=True)
    
    # Supporting data
    input_features = models.JSONField(default=dict)
    feature_importance = models.JSONField(default=dict)
    explanation = models.TextField(blank=True)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    action_items = models.JSONField(default=list)
    
    # Validation
    actual_value = models.FloatField(null=True, blank=True)
    prediction_error = models.FloatField(null=True, blank=True)
    is_accurate = models.BooleanField(null=True, blank=True)
    
    # Timing
    prediction_date = models.DateTimeField(auto_now_add=True)
    target_date = models.DateField(help_text="Date for which prediction is made")
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    is_viewed = models.BooleanField(default=False)
    viewed_by = models.ManyToManyField(User, blank=True, related_name='viewed_predictions')
    actions_taken = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_performance_predictions'
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['student', 'prediction_type']),
            models.Index(fields=['risk_level', '-prediction_date']),
            models.Index(fields=['target_date', 'prediction_type']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.prediction_type} - {self.predicted_value}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class AcademicAnalytics(models.Model):
    """
    Academic analytics and insights
    تحليلات وإحصائيات أكاديمية
    """
    ANALYTICS_TYPES = [
        ('COURSE_DIFFICULTY', 'Course Difficulty Analysis'),
        ('INSTRUCTOR_EFFECTIVENESS', 'Instructor Effectiveness'),
        ('CURRICULUM_GAP', 'Curriculum Gap Analysis'),
        ('STUDENT_ENGAGEMENT', 'Student Engagement'),
        ('GRADE_DISTRIBUTION', 'Grade Distribution'),
        ('ATTENDANCE_PATTERN', 'Attendance Patterns'),
        ('RESOURCE_UTILIZATION', 'Resource Utilization'),
        ('TREND_ANALYSIS', 'Trend Analysis'),
    ]
    
    analytics_type = models.CharField(max_length=30, choices=ANALYTICS_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Scope
    department = models.ForeignKey('roles_permissions.Department', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics_about')
    
    # Data and results
    raw_data = models.JSONField(default=dict)
    processed_data = models.JSONField(default=dict)
    insights = models.JSONField(default=list)
    visualizations = models.JSONField(default=dict, help_text="Chart configurations and data")
    
    # Analysis parameters
    date_from = models.DateField()
    date_to = models.DateField()
    sample_size = models.IntegerField(null=True, blank=True)
    
    # Results
    key_findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    action_items = models.JSONField(default=list)
    
    # Confidence and quality
    confidence_level = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.95)
    data_quality_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], null=True, blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    generated_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_analytics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['analytics_type', '-created_at']),
            models.Index(fields=['department', 'is_published']),
            models.Index(fields=['date_from', 'date_to']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.analytics_type}"


class EarlyWarningSystem(models.Model):
    """
    Early warning system for at-risk students
    نظام إنذار مبكر للطلاب المعرضين للخطر
    """
    WARNING_TYPES = [
        ('ACADEMIC_PERFORMANCE', 'Academic Performance'),
        ('ATTENDANCE', 'Attendance Issue'),
        ('FINANCIAL', 'Financial Difficulty'),
        ('BEHAVIORAL', 'Behavioral Concern'),
        ('HEALTH', 'Health/Wellness'),
        ('ENGAGEMENT', 'Low Engagement'),
        ('GRADUATION_RISK', 'Graduation Risk'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='warnings')
    warning_type = models.CharField(max_length=30, choices=WARNING_TYPES)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Warning details
    title = models.CharField(max_length=200)
    description = models.TextField()
    indicators = models.JSONField(default=list, help_text="List of indicators that triggered this warning")
    risk_factors = models.JSONField(default=list)
    
    # AI-generated information
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    predicted_outcome = models.TextField(blank=True)
    recommended_actions = models.JSONField(default=list)
    
    # Intervention tracking
    interventions_applied = models.JSONField(default=list)
    progress_notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    
    # Assignment and follow-up
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_warnings')
    due_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Tracking
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_warnings')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_warnings')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'early_warning_system'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['warning_type', 'severity_level']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.warning_type} - {self.severity_level}"


class RecommendationEngine(models.Model):
    """
    AI-powered recommendation engine
    محرك التوصيات المدعوم بالذكاء الاصطناعي
    """
    RECOMMENDATION_TYPES = [
        ('COURSE_SELECTION', 'Course Selection'),
        ('STUDY_PLAN', 'Study Plan'),
        ('CAREER_PATH', 'Career Path'),
        ('TUTORING', 'Tutoring'),
        ('EXTRACURRICULAR', 'Extracurricular Activities'),
        ('SCHOLARSHIP', 'Scholarship Opportunities'),
        ('INTERNSHIP', 'Internship Opportunities'),
        ('RESOURCE_UTILIZATION', 'Resource Utilization'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='recommendations')
    
    # Recommendation details
    title = models.CharField(max_length=200)
    description = models.TextField()
    recommendations = models.JSONField(default=list)
    reasoning = models.TextField()
    
    # Scoring and ranking
    relevance_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    priority_rank = models.IntegerField(default=1)
    
    # Context and personalization
    context_data = models.JSONField(default=dict)
    personalization_factors = models.JSONField(default=dict)
    
    # Interaction tracking
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    is_accepted = models.BooleanField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    feedback_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_comment = models.TextField(blank=True)
    
    # Expiry and refresh
    expires_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendation_engine'
        ordering = ['-relevance_score', '-confidence_score']
        indexes = [
            models.Index(fields=['student', 'recommendation_type']),
            models.Index(fields=['relevance_score', 'confidence_score']),
            models.Index(fields=['is_viewed', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.title}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class LearningPath(models.Model):
    """
    AI-generated personalized learning paths
    مسارات تعلم شخصية مُنتَجة بالذكاء الاصطناعي
    """
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('EXPERT', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('PAUSED', 'Paused'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_paths')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Path configuration
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    estimated_duration = models.DurationField(help_text="Estimated time to complete")
    learning_objectives = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    
    # Path structure
    milestones = models.JSONField(default=list)
    resources = models.JSONField(default=list)
    assessments = models.JSONField(default=list)
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    progress_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    current_milestone = models.IntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI generation
    generated_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    generation_parameters = models.JSONField(default=dict)
    personalization_data = models.JSONField(default=dict)
    
    # Feedback and improvement
    effectiveness_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    student_satisfaction = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    completion_rate = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['difficulty_level', 'status']),
            models.Index(fields=['target_completion_date']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.title}"
    
    def update_progress(self):
        """Update progress based on completed milestones"""
        if self.milestones:
            completed_milestones = sum(1 for milestone in self.milestones if milestone.get('completed', False))
            self.progress_percentage = (completed_milestones / len(self.milestones)) * 100
            self.current_milestone = completed_milestones
            
            if self.progress_percentage == 100 and self.status == 'ACTIVE':
                self.status = 'COMPLETED'
                self.completed_at = timezone.now()
            
            self.save()


class AIInsight(models.Model):
    """
    AI-generated insights and patterns
    رؤى وأنماط مُنتَجة بالذكاء الاصطناعي
    """
    INSIGHT_CATEGORIES = [
        ('ACADEMIC_TREND', 'Academic Trend'),
        ('BEHAVIORAL_PATTERN', 'Behavioral Pattern'),
        ('RESOURCE_OPTIMIZATION', 'Resource Optimization'),
        ('PERFORMANCE_DRIVER', 'Performance Driver'),
        ('RISK_INDICATOR', 'Risk Indicator'),
        ('OPPORTUNITY', 'Opportunity'),
        ('ANOMALY', 'Anomaly Detection'),
        ('CORRELATION', 'Correlation Analysis'),
    ]
    
    SCOPE_LEVELS = [
        ('INDIVIDUAL', 'Individual Student'),
        ('COURSE', 'Course Level'),
        ('DEPARTMENT', 'Department Level'),
        ('INSTITUTION', 'Institution Level'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=INSIGHT_CATEGORIES)
    scope_level = models.CharField(max_length=20, choices=SCOPE_LEVELS)
    
    # Insight content
    description = models.TextField()
    key_findings = models.JSONField(default=list)
    supporting_data = models.JSONField(default=dict)
    statistical_significance = models.FloatField(null=True, blank=True)
    
    # Context
    students_affected = models.ManyToManyField(Student, blank=True, related_name='ai_insights')
    departments_affected = models.ManyToManyField('roles_permissions.Department', blank=True, related_name='ai_insights')
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    
    # AI model and generation
    generated_by = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='generated_insights')
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Impact and priority
    impact_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')])
    priority_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Actions and recommendations
    recommended_actions = models.JSONField(default=list)
    potential_impact = models.TextField(blank=True)
    
    # Tracking
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_insights')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    actions_taken = models.JSONField(default=list)
    
    # Validation
    is_validated = models.BooleanField(null=True, blank=True)
    validation_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_insights'
        ordering = ['-priority_score', '-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['category', 'scope_level']),
            models.Index(fields=['impact_level', 'priority_score']),
            models.Index(fields=['is_reviewed', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.category}"


class ModelPerformanceMetrics(models.Model):
    """
    Track performance metrics of AI models over time
    تتبع مقاييس أداء نماذج الذكاء الاصطناعي عبر الزمن
    """
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    auc_roc = models.FloatField(null=True, blank=True)
    mean_absolute_error = models.FloatField(null=True, blank=True)
    root_mean_square_error = models.FloatField(null=True, blank=True)
    
    # Custom metrics
    custom_metrics = models.JSONField(default=dict)
    
    # Evaluation context
    evaluation_dataset_size = models.IntegerField()
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    
    # Comparison with previous version
    performance_change = models.FloatField(null=True, blank=True, help_text="Performance change compared to previous evaluation")
    is_improvement = models.BooleanField(null=True, blank=True)
    
    # Metadata
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    evaluation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'model_performance_metrics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model', '-created_at']),
            models.Index(fields=['evaluation_period_start', 'evaluation_period_end']),
        ]
    
    def __str__(self):
        return f"{self.model.name} - Performance - {self.created_at.date()}"