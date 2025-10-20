# محرك الذكاء الاصطناعي المتقدم للجامعة
# Advanced AI Engine for University Management System

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class UniversityAIEngine:
    """
    محرك الذكاء الاصطناعي الشامل للجامعة
    يوفر التنبؤات الأكاديمية، التوصيات الذكية، وكشف الأنماط
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.is_trained = False
        
        # إعداد النماذج
        self._initialize_models()
        
    def _initialize_models(self):
        """تهيئة نماذج التعلم الآلي"""
        
        # نموذج التنبؤ بالدرجات
        self.models['grade_predictor'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # نموذج تصنيف مستوى الطلاب
        self.models['student_classifier'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        
        # نموذج كشف المخاطر الأكاديمية
        self.models['risk_detector'] = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            max_iter=500,
            random_state=42
        )
        
        # نموذج التوصيات
        self.models['recommendation_engine'] = MLPRegressor(
            hidden_layer_sizes=(150, 100, 50),
            max_iter=500,
            random_state=42
        )
        
        # نموذج تجميع الطلاب
        self.models['student_clustering'] = KMeans(
            n_clusters=5,
            random_state=42
        )
        
        # معالجات البيانات
        self.scalers['standard'] = StandardScaler()
        self.encoders['label'] = LabelEncoder()

class StudentPerformancePredictor:
    """نظام التنبؤ بأداء الطلاب"""
    
    def __init__(self, ai_engine: UniversityAIEngine):
        self.ai_engine = ai_engine
        
    def predict_student_grade(self, student_data: Dict) -> Dict:
        """
        التنبؤ بدرجة الطالب في مقرر معين
        
        Args:
            student_data: بيانات الطالب والمقرر
            
        Returns:
            Dict: التنبؤات والتوصيات
        """
        try:
            # استخراج الميزات
            features = self._extract_features(student_data)
            
            # التنبؤ بالدرجة
            predicted_grade = self.ai_engine.models['grade_predictor'].predict([features])[0]
            
            # حساب احتمالية النجاح
            success_probability = self._calculate_success_probability(features, predicted_grade)
            
            # تحديد مستوى المخاطر
            risk_level = self._assess_risk_level(predicted_grade, success_probability)
            
            # إنتاج التوصيات
            recommendations = self._generate_recommendations(student_data, risk_level)
            
            return {
                'predicted_grade': round(predicted_grade, 2),
                'letter_grade': self._convert_to_letter_grade(predicted_grade),
                'success_probability': round(success_probability * 100, 1),
                'risk_level': risk_level,
                'recommendations': recommendations,
                'confidence_score': self._calculate_confidence_score(features),
                'prediction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'خطأ في التنبؤ: {str(e)}',
                'predicted_grade': 0,
                'success_probability': 0,
                'risk_level': 'unknown'
            }
    
    def _extract_features(self, student_data: Dict) -> List[float]:
        """استخراج الميزات من بيانات الطالب"""
        
        features = [
            student_data.get('current_gpa', 0.0),
            student_data.get('attendance_rate', 0.0),
            student_data.get('assignment_completion', 0.0),
            student_data.get('participation_score', 0.0),
            student_data.get('previous_grades_avg', 0.0),
            student_data.get('study_hours_per_week', 0.0),
            student_data.get('course_difficulty', 3.0),
            student_data.get('semester_load', 15.0),
            student_data.get('extracurricular_activities', 0.0),
            student_data.get('financial_aid_status', 0.0)  # 1 if receiving aid, 0 otherwise
        ]
        
        return features
    
    def _calculate_success_probability(self, features: List[float], predicted_grade: float) -> float:
        """حساب احتمالية النجاح"""
        
        # العتبة الأساسية للنجاح (60%)
        base_threshold = 60.0
        
        # حساب الاحتمالية بناءً على الدرجة المتوقعة والعوامل الأخرى
        if predicted_grade >= base_threshold:
            probability = min(0.95, predicted_grade / 100.0 + 0.1)
        else:
            probability = max(0.05, predicted_grade / 100.0 - 0.1)
        
        # تعديل الاحتمالية بناءً على العوامل الإضافية
        attendance_factor = features[1] / 100.0  # معدل الحضور
        assignment_factor = features[2] / 100.0  # معدل إنجاز المهام
        
        probability = probability * (0.7 + 0.3 * (attendance_factor + assignment_factor) / 2)
        
        return max(0.0, min(1.0, probability))
    
    def _assess_risk_level(self, predicted_grade: float, success_probability: float) -> str:
        """تقييم مستوى المخاطر الأكاديمية"""
        
        if predicted_grade >= 85 and success_probability >= 0.9:
            return 'low'  # مخاطر منخفضة
        elif predicted_grade >= 70 and success_probability >= 0.7:
            return 'medium'  # مخاطر متوسطة
        elif predicted_grade >= 60 and success_probability >= 0.5:
            return 'high'  # مخاطر عالية
        else:
            return 'critical'  # مخاطر حرجة
    
    def _generate_recommendations(self, student_data: Dict, risk_level: str) -> List[Dict]:
        """إنتاج التوصيات الأكاديمية"""
        
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                {
                    'type': 'urgent',
                    'title': 'تدخل أكاديمي عاجل',
                    'description': 'يحتاج الطالب لدعم أكاديمي فوري ومراجعة خطة الدراسة',
                    'priority': 'high',
                    'actions': [
                        'تحديد موعد مع المرشد الأكاديمي',
                        'انضمام لبرنامج الدعم الأكاديمي',
                        'تقليل العبء الدراسي إن أمكن'
                    ]
                },
                {
                    'type': 'study_plan',
                    'title': 'خطة دراسة مكثفة',
                    'description': 'برنامج دراسي مكثف لتحسين الأداء',
                    'priority': 'high',
                    'actions': [
                        'جدولة ساعات دراسة إضافية يومياً',
                        'تشكيل مجموعة دراسية',
                        'استخدام موارد تعليمية إضافية'
                    ]
                }
            ])
        
        elif risk_level == 'high':
            recommendations.extend([
                {
                    'type': 'academic_support',
                    'title': 'دعم أكاديمي',
                    'description': 'الحصول على دعم أكاديمي إضافي',
                    'priority': 'medium',
                    'actions': [
                        'حضور ساعات مكتبية للأستاذ',
                        'الانضمام لمجموعات الدراسة',
                        'استخدام مركز التعلم'
                    ]
                }
            ])
        
        elif risk_level == 'medium':
            recommendations.append({
                'type': 'improvement',
                'title': 'تحسين الأداء',
                'description': 'فرص لتحسين الأداء الأكاديمي',
                'priority': 'low',
                'actions': [
                    'مراجعة عادات الدراسة',
                    'تحسين إدارة الوقت',
                    'زيادة المشاركة في الصف'
                ]
            })
        
        # توصيات خاصة بناءً على البيانات
        if student_data.get('attendance_rate', 100) < 80:
            recommendations.append({
                'type': 'attendance',
                'title': 'تحسين الحضور',
                'description': 'الحضور المنتظم ضروري للنجاح الأكاديمي',
                'priority': 'high',
                'actions': [
                    'وضع جدول زمني منتظم للحضور',
                    'تحديد أسباب الغياب ومعالجتها',
                    'استخدام تذكيرات الحضور'
                ]
            })
        
        if student_data.get('assignment_completion', 100) < 70:
            recommendations.append({
                'type': 'assignments',
                'title': 'إنجاز المهام',
                'description': 'تحسين معدل إنجاز المهام والواجبات',
                'priority': 'medium',
                'actions': [
                    'إنشاء تقويم للمهام والواجبات',
                    'تقسيم المهام الكبيرة لمهام صغيرة',
                    'طلب المساعدة عند الحاجة'
                ]
            })
        
        return recommendations
    
    def _convert_to_letter_grade(self, numeric_grade: float) -> str:
        """تحويل الدرجة الرقمية لدرجة حرفية"""
        
        if numeric_grade >= 90:
            return 'A+'
        elif numeric_grade >= 85:
            return 'A'
        elif numeric_grade >= 80:
            return 'B+'
        elif numeric_grade >= 75:
            return 'B'
        elif numeric_grade >= 70:
            return 'C+'
        elif numeric_grade >= 65:
            return 'C'
        elif numeric_grade >= 60:
            return 'D'
        else:
            return 'F'
    
    def _calculate_confidence_score(self, features: List[float]) -> float:
        """حساب درجة الثقة في التنبؤ"""
        
        # حساب درجة الثقة بناءً على جودة البيانات المتاحة
        feature_completeness = sum(1 for f in features if f > 0) / len(features)
        
        # درجة الثقة الأساسية
        base_confidence = 0.7
        
        # تعديل بناءً على اكتمال البيانات
        confidence = base_confidence + (feature_completeness * 0.3)
        
        return round(confidence, 2)

class SmartRecommendationEngine:
    """محرك التوصيات الذكية"""
    
    def __init__(self, ai_engine: UniversityAIEngine):
        self.ai_engine = ai_engine
        
    def generate_course_recommendations(self, student_data: Dict) -> List[Dict]:
        """إنتاج توصيات المقررات الدراسية"""
        
        recommendations = []
        
        try:
            # تحليل الأداء الحالي
            current_performance = self._analyze_student_performance(student_data)
            
            # توصيات المقررات بناءً على التخصص
            major_courses = self._recommend_major_courses(student_data)
            recommendations.extend(major_courses)
            
            # توصيات المقررات الاختيارية
            elective_courses = self._recommend_elective_courses(student_data, current_performance)
            recommendations.extend(elective_courses)
            
            # ترتيب التوصيات حسب الأولوية
            recommendations.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
            
        except Exception as e:
            recommendations = [{
                'error': f'خطأ في إنتاج التوصيات: {str(e)}',
                'type': 'error'
            }]
        
        return recommendations
    
    def _analyze_student_performance(self, student_data: Dict) -> Dict:
        """تحليل أداء الطالب الحالي"""
        
        performance = {
            'overall_gpa': student_data.get('current_gpa', 0.0),
            'strong_subjects': [],
            'weak_subjects': [],
            'learning_style': self._determine_learning_style(student_data),
            'academic_strengths': [],
            'areas_for_improvement': []
        }
        
        # تحليل المواد القوية والضعيفة
        courses_grades = student_data.get('courses_grades', {})
        for course, grade in courses_grades.items():
            if grade >= 85:
                performance['strong_subjects'].append(course)
            elif grade < 70:
                performance['weak_subjects'].append(course)
        
        return performance
    
    def _determine_learning_style(self, student_data: Dict) -> str:
        """تحديد أسلوب التعلم المفضل للطالب"""
        
        # تحليل بسيط لأسلوب التعلم بناءً على الأداء
        practical_courses = student_data.get('practical_performance', 0)
        theoretical_courses = student_data.get('theoretical_performance', 0)
        
        if practical_courses > theoretical_courses:
            return 'practical'  # تطبيقي
        elif theoretical_courses > practical_courses:
            return 'theoretical'  # نظري
        else:
            return 'balanced'  # متوازن
    
    def _recommend_major_courses(self, student_data: Dict) -> List[Dict]:
        """توصيات مقررات التخصص"""
        
        major = student_data.get('major', '')
        current_semester = student_data.get('current_semester', 1)
        completed_courses = student_data.get('completed_courses', [])
        
        recommendations = []
        
        # مقررات أساسية حسب التخصص (مثال)
        major_courses_map = {
            'Computer Science': [
                {'name': 'Data Structures', 'semester': 3, 'difficulty': 4},
                {'name': 'Algorithms', 'semester': 4, 'difficulty': 5},
                {'name': 'Database Systems', 'semester': 5, 'difficulty': 4},
                {'name': 'Software Engineering', 'semester': 6, 'difficulty': 4}
            ],
            'Business Administration': [
                {'name': 'Financial Management', 'semester': 3, 'difficulty': 3},
                {'name': 'Marketing Management', 'semester': 4, 'difficulty': 3},
                {'name': 'Operations Management', 'semester': 5, 'difficulty': 4},
                {'name': 'Strategic Management', 'semester': 6, 'difficulty': 5}
            ]
        }
        
        if major in major_courses_map:
            for course in major_courses_map[major]:
                if (course['semester'] <= current_semester + 1 and 
                    course['name'] not in completed_courses):
                    
                    recommendations.append({
                        'course_name': course['name'],
                        'type': 'major_requirement',
                        'priority_score': 90 - course['difficulty'],
                        'difficulty_level': course['difficulty'],
                        'recommended_semester': course['semester'],
                        'reasoning': f'مقرر أساسي في تخصص {major}'
                    })
        
        return recommendations
    
    def _recommend_elective_courses(self, student_data: Dict, performance: Dict) -> List[Dict]:
        """توصيات المقررات الاختيارية"""
        
        recommendations = []
        
        # توصيات بناءً على نقاط القوة
        for strong_subject in performance['strong_subjects']:
            if 'Math' in strong_subject:
                recommendations.append({
                    'course_name': 'Advanced Statistics',
                    'type': 'elective',
                    'priority_score': 75,
                    'difficulty_level': 4,
                    'reasoning': 'مناسب لقوتك في الرياضيات'
                })
            elif 'Programming' in strong_subject:
                recommendations.append({
                    'course_name': 'Mobile App Development',
                    'type': 'elective',
                    'priority_score': 80,
                    'difficulty_level': 4,
                    'reasoning': 'مناسب لمهاراتك في البرمجة'
                })
        
        # توصيات لتحسين نقاط الضعف
        for weak_subject in performance['weak_subjects']:
            if 'Communication' in weak_subject:
                recommendations.append({
                    'course_name': 'Public Speaking',
                    'type': 'skill_improvement',
                    'priority_score': 85,
                    'difficulty_level': 2,
                    'reasoning': 'لتحسين مهارات التواصل'
                })
        
        return recommendations

class PredictiveAnalytics:
    """نظام التحليلات التنبؤية المتقدم"""
    
    def __init__(self, ai_engine: UniversityAIEngine):
        self.ai_engine = ai_engine
        
    def predict_enrollment_trends(self, historical_data: List[Dict]) -> Dict:
        """التنبؤ بأعداد التسجيل في الفصول القادمة"""
        
        try:
            # تحضير البيانات التاريخية
            df = pd.DataFrame(historical_data)
            
            # استخراج الميزات الزمنية
            df['year'] = pd.to_datetime(df['date']).dt.year
            df['month'] = pd.to_datetime(df['date']).dt.month
            df['semester'] = df['month'].apply(lambda x: 1 if x <= 6 else 2)
            
            # بناء نموذج التنبؤ
            features = ['year', 'semester', 'total_capacity', 'marketing_budget']
            X = df[features].fillna(0)
            y = df['enrollment_count']
            
            # تدريب النموذج
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # التنبؤ للفصول القادمة
            future_periods = []
            current_year = datetime.now().year
            
            for year in range(current_year, current_year + 3):
                for semester in [1, 2]:
                    prediction_data = [year, semester, 1000, 50000]  # قيم افتراضية
                    predicted_enrollment = model.predict([prediction_data])[0]
                    
                    future_periods.append({
                        'year': year,
                        'semester': semester,
                        'predicted_enrollment': int(predicted_enrollment),
                        'confidence_interval': [
                            int(predicted_enrollment * 0.9),
                            int(predicted_enrollment * 1.1)
                        ]
                    })
            
            return {
                'predictions': future_periods,
                'model_accuracy': model.score(X, y),
                'feature_importance': dict(zip(features, model.feature_importances_)),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'خطأ في التنبؤ بالتسجيل: {str(e)}',
                'predictions': []
            }
    
    def detect_dropout_risk(self, student_data: List[Dict]) -> List[Dict]:
        """كشف الطلاب المعرضين لخطر التسرب"""
        
        at_risk_students = []
        
        try:
            for student in student_data:
                risk_score = self._calculate_dropout_risk_score(student)
                
                if risk_score > 0.7:  # عتبة عالية للخطر
                    at_risk_students.append({
                        'student_id': student.get('student_id'),
                        'student_name': student.get('name'),
                        'risk_score': round(risk_score, 2),
                        'risk_level': 'high',
                        'risk_factors': self._identify_risk_factors(student),
                        'intervention_recommendations': self._suggest_interventions(student, risk_score)
                    })
                elif risk_score > 0.5:  # عتبة متوسطة للخطر
                    at_risk_students.append({
                        'student_id': student.get('student_id'),
                        'student_name': student.get('name'),
                        'risk_score': round(risk_score, 2),
                        'risk_level': 'medium',
                        'risk_factors': self._identify_risk_factors(student),
                        'intervention_recommendations': self._suggest_interventions(student, risk_score)
                    })
        
        except Exception as e:
            return [{
                'error': f'خطأ في كشف مخاطر التسرب: {str(e)}'
            }]
        
        # ترتيب حسب درجة المخاطر
        at_risk_students.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        
        return at_risk_students
    
    def _calculate_dropout_risk_score(self, student: Dict) -> float:
        """حساب درجة مخاطر التسرب للطالب"""
        
        risk_factors = []
        
        # عوامل أكاديمية
        gpa = student.get('current_gpa', 4.0)
        if gpa < 2.0:
            risk_factors.append(0.3)  # GPA منخفض جداً
        elif gpa < 2.5:
            risk_factors.append(0.2)  # GPA منخفض
        
        # عوامل الحضور
        attendance = student.get('attendance_rate', 100)
        if attendance < 60:
            risk_factors.append(0.25)  # حضور ضعيف جداً
        elif attendance < 80:
            risk_factors.append(0.15)  # حضور ضعيف
        
        # عوامل مالية
        if student.get('financial_difficulties', False):
            risk_factors.append(0.2)
        
        # عوامل اجتماعية
        if student.get('social_isolation', False):
            risk_factors.append(0.15)
        
        # عدد الفصول المتعثر فيها
        failed_semesters = student.get('failed_semesters', 0)
        if failed_semesters > 2:
            risk_factors.append(0.25)
        elif failed_semesters > 0:
            risk_factors.append(0.1)
        
        # حساب الدرجة الإجمالية
        total_risk = min(1.0, sum(risk_factors))
        
        return total_risk
    
    def _identify_risk_factors(self, student: Dict) -> List[str]:
        """تحديد عوامل المخاطر المحددة للطالب"""
        
        factors = []
        
        if student.get('current_gpa', 4.0) < 2.5:
            factors.append('معدل تراكمي منخفض')
        
        if student.get('attendance_rate', 100) < 80:
            factors.append('ضعف في الحضور')
        
        if student.get('financial_difficulties', False):
            factors.append('صعوبات مالية')
        
        if student.get('social_isolation', False):
            factors.append('عزلة اجتماعية')
        
        if student.get('failed_semesters', 0) > 0:
            factors.append('فصول دراسية متعثرة')
        
        if not factors:
            factors.append('عوامل عامة')
        
        return factors
    
    def _suggest_interventions(self, student: Dict, risk_score: float) -> List[Dict]:
        """اقتراح تدخلات للحد من مخاطر التسرب"""
        
        interventions = []
        
        if risk_score > 0.7:
            interventions.extend([
                {
                    'type': 'urgent',
                    'action': 'اجتماع عاجل مع المرشد الأكاديمي',
                    'priority': 'high',
                    'timeline': 'خلال أسبوع'
                },
                {
                    'type': 'academic',
                    'action': 'وضع خطة أكاديمية مكثفة',
                    'priority': 'high',
                    'timeline': 'فوري'
                },
                {
                    'type': 'support',
                    'action': 'تقديم دعم نفسي واجتماعي',
                    'priority': 'medium',
                    'timeline': 'خلال أسبوعين'
                }
            ])
        elif risk_score > 0.5:
            interventions.extend([
                {
                    'type': 'monitoring',
                    'action': 'مراقبة أكاديمية دورية',
                    'priority': 'medium',
                    'timeline': 'شهرياً'
                },
                {
                    'type': 'mentoring',
                    'action': 'برنامج إرشاد أكاديمي',
                    'priority': 'medium',
                    'timeline': 'خلال شهر'
                }
            ])
        
        # تدخلات خاصة بالعوامل المحددة
        if student.get('financial_difficulties', False):
            interventions.append({
                'type': 'financial',
                'action': 'تقييم للمساعدات المالية',
                'priority': 'high',
                'timeline': 'خلال أسبوعين'
            })
        
        return interventions

# مثيل عام للمحرك
university_ai = UniversityAIEngine()
performance_predictor = StudentPerformancePredictor(university_ai)
recommendation_engine = SmartRecommendationEngine(university_ai)
predictive_analytics = PredictiveAnalytics(university_ai)