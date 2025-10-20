# محرك الذكاء الاصطناعي المتقدم
# Advanced AI Engine for University Management System

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import json
import random
from django.db.models import Avg, Count, Q
from django.utils import timezone
from students.models import Student, Enrollment
from courses.models import Course
from .models import StudentPerformancePrediction, SmartRecommendation

class StudentPerformancePredictor:
    """محرك التنبؤ بأداء الطلاب"""
    
    def __init__(self):
        self.model_weights = {
            'gpa': 0.4,
            'attendance': 0.3,
            'assignments': 0.2,
            'participation': 0.1
        }
    
    def predict_student_performance(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """التنبؤ بأداء طالب في مقرر محدد"""
        try:
            student = Student.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
            
            # جمع البيانات التاريخية
            historical_data = self._get_historical_data(student, course)
            
            # حساب المقاييس الحالية
            current_metrics = self._calculate_current_metrics(student, course)
            
            # التنبؤ بالدرجة
            predicted_grade = self._predict_grade(current_metrics, historical_data)
            
            # حساب احتمالية النجاح
            success_probability = self._calculate_success_probability(current_metrics)
            
            # تحديد مستوى المخاطر
            risk_level = self._assess_risk_level(success_probability, current_metrics)
            
            # إنشاء التوصيات
            recommendations = self._generate_recommendations(current_metrics, risk_level)
            
            # حفظ التنبؤ في قاعدة البيانات
            prediction, created = StudentPerformancePrediction.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'current_gpa': current_metrics['gpa'],
                    'attendance_rate': current_metrics['attendance'],
                    'assignment_completion': current_metrics['assignments'],
                    'participation_score': current_metrics['participation'],
                    'predicted_grade': predicted_grade,
                    'success_probability': success_probability,
                    'risk_level': risk_level,
                    'recommendations': recommendations,
                    'intervention_needed': risk_level in ['high', 'critical']
                }
            )
            
            return {
                'student_id': student_id,
                'course_id': course_id,
                'predicted_grade': predicted_grade,
                'success_probability': success_probability,
                'risk_level': risk_level,
                'recommendations': recommendations,
                'current_metrics': current_metrics
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_historical_data(self, student: Student, course: Course) -> Dict[str, Any]:
        """جمع البيانات التاريخية للطالب"""
        # بيانات وهمية للتجربة - في التطبيق الحقيقي ستأتي من قاعدة البيانات
        return {
            'previous_courses_avg': 3.2,
            'similar_courses_performance': 3.5,
            'semester_trend': 0.1  # اتجاه تحسن
        }
    
    def _calculate_current_metrics(self, student: Student, course: Course) -> Dict[str, float]:
        """حساب المقاييس الحالية للطالب"""
        # بيانات وهمية للتجربة
        return {
            'gpa': random.uniform(2.0, 4.0),
            'attendance': random.uniform(0.6, 1.0),
            'assignments': random.uniform(0.5, 1.0),
            'participation': random.uniform(0.3, 1.0)
        }
    
    def _predict_grade(self, current_metrics: Dict[str, float], 
                      historical_data: Dict[str, Any]) -> str:
        """التنبؤ بالدرجة النهائية"""
        # حساب النقاط المرجحة
        weighted_score = (
            current_metrics['gpa'] * self.model_weights['gpa'] +
            current_metrics['attendance'] * self.model_weights['attendance'] * 4 +
            current_metrics['assignments'] * self.model_weights['assignments'] * 4 +
            current_metrics['participation'] * self.model_weights['participation'] * 4
        )
        
        # تحويل إلى درجة حرفية
        if weighted_score >= 3.7:
            return 'A'
        elif weighted_score >= 3.3:
            return 'B+'
        elif weighted_score >= 3.0:
            return 'B'
        elif weighted_score >= 2.7:
            return 'C+'
        elif weighted_score >= 2.3:
            return 'C'
        elif weighted_score >= 2.0:
            return 'D+'
        elif weighted_score >= 1.7:
            return 'D'
        else:
            return 'F'
    
    def _calculate_success_probability(self, metrics: Dict[str, float]) -> float:
        """حساب احتمالية النجاح"""
        success_score = (
            metrics['gpa'] * 0.4 +
            metrics['attendance'] * 0.3 +
            metrics['assignments'] * 0.2 +
            metrics['participation'] * 0.1
        ) / 4.0
        
        return min(success_score, 1.0)
    
    def _assess_risk_level(self, success_probability: float, 
                          metrics: Dict[str, float]) -> str:
        """تقييم مستوى المخاطر"""
        if success_probability < 0.5:
            return 'critical'
        elif success_probability < 0.65:
            return 'high'
        elif success_probability < 0.8:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, metrics: Dict[str, float], 
                                risk_level: str) -> List[str]:
        """إنشاء التوصيات"""
        recommendations = []
        
        if metrics['attendance'] < 0.8:
            recommendations.append("تحسين معدل الحضور - الحضور أقل من 80%")
        
        if metrics['assignments'] < 0.7:
            recommendations.append("إنجاز المهام المتأخرة - معدل الإنجاز منخفض")
        
        if metrics['participation'] < 0.5:
            recommendations.append("زيادة المشاركة في الصف")
        
        if risk_level in ['high', 'critical']:
            recommendations.extend([
                "طلب المساعدة من الأستاذ",
                "الانضمام لمجموعات الدراسة",
                "حجز جلسات إضافية مع المرشد الأكاديمي"
            ])
        
        return recommendations

class SmartRecommendationEngine:
    """محرك التوصيات الذكية"""
    
    def generate_course_recommendations(self, student_id: int) -> List[Dict[str, Any]]:
        """إنشاء توصيات المقررات للطالب"""
        try:
            student = Student.objects.get(id=student_id)
            
            # تحليل المقررات المكتملة
            completed_courses = self._get_completed_courses(student)
            
            # العثور على المقررات المتاحة
            available_courses = self._get_available_courses(student)
            
            # تصنيف المقررات حسب الأولوية
            recommendations = []
            
            for course in available_courses:
                priority_score = self._calculate_course_priority(
                    student, course, completed_courses
                )
                
                recommendations.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'priority_score': priority_score,
                    'reasoning': self._get_recommendation_reasoning(
                        student, course, priority_score
                    )
                })
            
            # ترتيب حسب الأولوية
            recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # حفظ التوصيات في قاعدة البيانات
            self._save_recommendations(student, recommendations[:5])  # أفضل 5
            
            return recommendations[:10]  # إرجاع أفضل 10
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def _get_completed_courses(self, student: Student) -> List[Course]:
        """الحصول على المقررات المكتملة"""
        # منطق وهمي - في التطبيق الحقيقي سيأتي من قاعدة البيانات
        return []
    
    def _get_available_courses(self, student: Student) -> List[Course]:
        """الحصول على المقررات المتاحة"""
        return Course.objects.filter(is_active=True)[:20]  # أول 20 مقرر متاح
    
    def _calculate_course_priority(self, student: Student, course: Course, 
                                 completed_courses: List[Course]) -> float:
        """حساب أولوية المقرر"""
        priority_score = random.uniform(0.3, 1.0)  # نقاط وهمية للتجربة
        
        # عوامل التقييم الحقيقية:
        # - المتطلبات السابقة
        # - اهتمامات الطالب
        # - صعوبة المقرر
        # - توفر الوقت
        # - تقييمات الطلاب السابقين
        
        return priority_score
    
    def _get_recommendation_reasoning(self, student: Student, course: Course, 
                                    priority_score: float) -> str:
        """الحصول على مبرر التوصية"""
        if priority_score > 0.8:
            return "مقرر ممتاز يناسب مستواك الأكاديمي ويساعد في تطوير مهاراتك"
        elif priority_score > 0.6:
            return "مقرر جيد يكمل دراستك ويحقق متطلبات التخرج"
        else:
            return "مقرر مناسب كاختيار إضافي لتوسيع معرفتك"
    
    def _save_recommendations(self, student: Student, recommendations: List[Dict[str, Any]]):
        """حفظ التوصيات في قاعدة البيانات"""
        for rec in recommendations:
            SmartRecommendation.objects.create(
                student=student,
                recommendation_type='course_selection',
                title=f"يُنصح بدراسة: {rec['course_name']}",
                description=rec['reasoning'],
                priority_score=rec['priority_score'],
                recommended_items=[{
                    'course_id': rec['course_id'],
                    'course_name': rec['course_name']
                }],
                reasoning=rec['reasoning'],
                expires_at=timezone.now() + timedelta(days=30)
            )

class SecurityAIEngine:
    """محرك الأمان الذكي"""
    
    def __init__(self):
        self.threat_patterns = {
            'brute_force': {'attempts_threshold': 5, 'time_window': 300},
            'suspicious_ip': {'known_threats': [], 'geo_anomaly': True},
            'privilege_escalation': {'role_changes': True, 'admin_access': True}
        }
    
    def analyze_login_attempt(self, user_id: int, ip_address: str, 
                            user_agent: str, success: bool) -> Dict[str, Any]:
        """تحليل محاولة تسجيل الدخول"""
        threat_level = 'low'
        threats_detected = []
        
        # فحص محاولات القوة الغاشمة
        if self._check_brute_force(user_id, ip_address):
            threat_level = 'high'
            threats_detected.append('brute_force')
        
        # فحص IP مشبوه
        if self._check_suspicious_ip(ip_address):
            threat_level = 'medium'
            threats_detected.append('suspicious_ip')
        
        # فحص نمط الاستخدام غير العادي
        if self._check_usage_anomaly(user_id, user_agent):
            threat_level = 'medium'
            threats_detected.append('usage_anomaly')
        
        return {
            'threat_level': threat_level,
            'threats_detected': threats_detected,
            'recommendation': self._get_security_recommendation(threats_detected),
            'timestamp': timezone.now()
        }
    
    def _check_brute_force(self, user_id: int, ip_address: str) -> bool:
        """فحص محاولات القوة الغاشمة"""
        # منطق وهمي - في التطبيق الحقيقي سيفحص السجلات
        return random.choice([True, False]) if random.random() < 0.1 else False
    
    def _check_suspicious_ip(self, ip_address: str) -> bool:
        """فحص IP مشبوه"""
        # فحص قوائم IP المشبوهة
        suspicious_ips = ['192.168.1.100', '10.0.0.50']  # أمثلة
        return ip_address in suspicious_ips
    
    def _check_usage_anomaly(self, user_id: int, user_agent: str) -> bool:
        """فحص شذوذ في نمط الاستخدام"""
        # تحليل نمط الاستخدام المعتاد للمستخدم
        return random.choice([True, False]) if random.random() < 0.05 else False
    
    def _get_security_recommendation(self, threats: List[str]) -> str:
        """الحصول على توصية أمنية"""
        if 'brute_force' in threats:
            return "حظر IP مؤقتاً وإرسال تنبيه للمستخدم"
        elif 'suspicious_ip' in threats:
            return "مراقبة إضافية وطلب تأكيد الهوية"
        elif 'usage_anomaly' in threats:
            return "إرسال تنبيه للمستخدم وطلب تغيير كلمة المرور"
        else:
            return "متابعة المراقبة العادية"

class SchedulingAI:
    """الذكاء الاصطناعي للجدولة"""
    
    def __init__(self):
        self.constraints = {
            'no_conflicts': True,
            'balanced_load': True,
            'room_capacity': True,
            'instructor_availability': True
        }
    
    def generate_optimal_schedule(self, courses: List[Course], 
                                rooms: List[Dict], instructors: List[Dict]) -> Dict[str, Any]:
        """إنشاء جدول أمثل للمقررات"""
        
        # خوارزمية الجدولة الذكية (مبسطة)
        schedule = {}
        conflicts = 0
        
        time_slots = self._generate_time_slots()
        
        for course in courses:
            best_slot = self._find_best_slot(course, time_slots, schedule)
            if best_slot:
                schedule[course.id] = best_slot
            else:
                conflicts += 1
        
        fitness_score = self._calculate_fitness_score(schedule, conflicts)
        
        return {
            'schedule': schedule,
            'fitness_score': fitness_score,
            'conflicts': conflicts,
            'is_optimal': conflicts == 0 and fitness_score > 0.8
        }
    
    def _generate_time_slots(self) -> List[Dict[str, Any]]:
        """إنشاء فترات زمنية متاحة"""
        days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
        times = ['08:00', '09:30', '11:00', '12:30', '14:00', '15:30']
        
        slots = []
        for day in days:
            for time in times:
                slots.append({
                    'day': day,
                    'time': time,
                    'available': True
                })
        
        return slots
    
    def _find_best_slot(self, course: Course, time_slots: List[Dict], 
                       current_schedule: Dict) -> Dict[str, Any]:
        """العثور على أفضل فترة زمنية للمقرر"""
        available_slots = [slot for slot in time_slots if slot['available']]
        
        if available_slots:
            # اختيار عشوائي للتجربة - في التطبيق الحقيقي سيكون هناك خوارزمية تحسين
            best_slot = random.choice(available_slots)
            best_slot['available'] = False
            best_slot['course_id'] = course.id
            return best_slot
        
        return None
    
    def _calculate_fitness_score(self, schedule: Dict, conflicts: int) -> float:
        """حساب درجة جودة الجدول"""
        if not schedule:
            return 0.0
        
        # حساب معايير الجودة
        total_courses = len(schedule)
        conflict_penalty = conflicts * 0.1
        
        # توزيع الأحمال
        balance_score = self._calculate_balance_score(schedule)
        
        fitness = max(0.0, 1.0 - conflict_penalty + balance_score * 0.2)
        return min(fitness, 1.0)
    
    def _calculate_balance_score(self, schedule: Dict) -> float:
        """حساب توازن الأحمال في الجدول"""
        # تحليل توزيع المقررات عبر الأيام والأوقات
        daily_loads = {}
        
        for course_id, slot in schedule.items():
            day = slot['day']
            daily_loads[day] = daily_loads.get(day, 0) + 1
        
        if daily_loads:
            max_load = max(daily_loads.values())
            min_load = min(daily_loads.values())
            balance = 1.0 - (max_load - min_load) / max_load if max_load > 0 else 1.0
            return balance
        
        return 0.0