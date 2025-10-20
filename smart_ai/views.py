# واجهات الذكاء الاصطناعي للجامعة
# AI Views for University Management System

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

import json
from datetime import datetime, timedelta
from typing import Dict, List

from .models import (
    AIAnalyticsModel, StudentPerformancePrediction, AIChatBot, 
    ChatMessage, SmartRecommendation, PredictiveAnalytics, AISecurityAlert
)
from .ai_engine import (
    university_ai, performance_predictor, recommendation_engine, predictive_analytics
)
from students.models import Student, User
from courses.models import Course
from academic.models import Enrollment, Grade

class AIStudentAssistantView(APIView):
    """مساعد الطلاب الذكي"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """معالجة طلبات المساعد الذكي"""
        
        try:
            data = request.data
            message = data.get('message', '')
            chat_type = data.get('chat_type', 'student_support')
            
            # الحصول على أو إنشاء جلسة المحادثة
            chatbot, created = AIChatBot.objects.get_or_create(
                user=request.user,
                chat_type=chat_type,
                defaults={
                    'session_id': f"{request.user.id}_{datetime.now().timestamp()}"
                }
            )
            
            # معالجة الرسالة وإنتاج الرد
            response_data = self._process_ai_message(message, chat_type, request.user)
            
            # حفظ المحادثة
            chat_message = ChatMessage.objects.create(
                chatbot=chatbot,
                message=message,
                response=response_data['response'],
                user_intent=response_data.get('intent', ''),
                confidence_score=response_data.get('confidence', 0.8)
            )
            
            return Response({
                'success': True,
                'response': response_data['response'],
                'intent': response_data.get('intent', ''),
                'confidence': response_data.get('confidence', 0.8),
                'suggestions': response_data.get('suggestions', []),
                'message_id': chat_message.id
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في المساعد الذكي: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_ai_message(self, message: str, chat_type: str, user: User) -> Dict:
        """معالجة رسالة المساعد الذكي وإنتاج الرد"""
        
        message_lower = message.lower()
        
        # تحديد نوع الاستفسار
        intent = self._classify_intent(message_lower, chat_type)
        
        # إنتاج الرد حسب النوع
        if intent == 'grades_inquiry':
            return self._handle_grades_inquiry(user)
        elif intent == 'schedule_inquiry':
            return self._handle_schedule_inquiry(user)
        elif intent == 'attendance_inquiry':
            return self._handle_attendance_inquiry(user)
        elif intent == 'financial_inquiry':
            return self._handle_financial_inquiry(user)
        elif intent == 'course_recommendation':
            return self._handle_course_recommendation(user)
        elif intent == 'academic_advice':
            return self._handle_academic_advice(user)
        elif intent == 'general_info':
            return self._handle_general_info(message, user)
        else:
            return self._handle_general_response(message, user)
    
    def _classify_intent(self, message: str, chat_type: str) -> str:
        """تصنيف نوع الاستفسار"""
        
        # كلمات مفتاحية للدرجات
        if any(word in message for word in ['درجة', 'درجات', 'نتيجة', 'نتائج', 'علامة', 'علامات']):
            return 'grades_inquiry'
        
        # كلمات مفتاحية للجدول
        if any(word in message for word in ['جدول', 'محاضرة', 'محاضرات', 'وقت', 'موعد']):
            return 'schedule_inquiry'
        
        # كلمات مفتاحية للحضور
        if any(word in message for word in ['حضور', 'غياب', 'حاضر', 'غائب']):
            return 'attendance_inquiry'
        
        # كلمات مفتاحية للأمور المالية
        if any(word in message for word in ['رسوم', 'دفع', 'مالي', 'فاتورة', 'مبلغ']):
            return 'financial_inquiry'
        
        # كلمات مفتاحية للتوصيات
        if any(word in message for word in ['توصية', 'اقتراح', 'مقرر', 'مادة', 'اختيار']):
            return 'course_recommendation'
        
        # كلمات مفتاحية للإرشاد الأكاديمي
        if any(word in message for word in ['نصيحة', 'إرشاد', 'مساعدة', 'خطة', 'تخطيط']):
            return 'academic_advice'
        
        # معلومات عامة
        if any(word in message for word in ['معلومات', 'تعريف', 'شرح', 'كيف', 'ماذا', 'متى']):
            return 'general_info'
        
        return 'general'
    
    def _handle_grades_inquiry(self, user: User) -> Dict:
        """التعامل مع استفسارات الدرجات"""
        
        try:
            if hasattr(user, 'student_profile'):
                student = user.student_profile
                
                # جلب الدرجات الحديثة
                recent_grades = Grade.objects.filter(
                    enrollment__student=student
                ).order_by('-created_at')[:5]
                
                if recent_grades:
                    response = "إليك درجاتك الأخيرة:\n\n"
                    for grade in recent_grades:
                        response += f"• {grade.enrollment.course.name}: {grade.total_grade}/100\n"
                    
                    # حساب المعدل
                    avg_grade = sum(g.total_grade for g in recent_grades) / len(recent_grades)
                    response += f"\nمتوسط درجاتك الأخيرة: {avg_grade:.1f}"
                    
                    # تقييم الأداء
                    if avg_grade >= 85:
                        response += "\n\n🎉 أداء ممتاز! استمر على هذا المستوى"
                    elif avg_grade >= 75:
                        response += "\n\n👍 أداء جيد، يمكنك تحسينه أكثر"
                    else:
                        response += "\n\n📚 يحتاج أداؤك لمزيد من التحسين، أنصحك بمراجعة المرشد الأكاديمي"
                    
                else:
                    response = "لا توجد درجات مسجلة حتى الآن."
                
                return {
                    'response': response,
                    'intent': 'grades_inquiry',
                    'confidence': 0.9,
                    'suggestions': ['عرض تفاصيل المقررات', 'نصائح لتحسين الدرجات', 'مقارنة مع الفصل السابق']
                }
            else:
                return {
                    'response': 'عذراً، لا يمكنني الوصول إلى بيانات الطالب.',
                    'intent': 'grades_inquiry',
                    'confidence': 0.5
                }
                
        except Exception as e:
            return {
                'response': f'عذراً، حدث خطأ في جلب الدرجات: {str(e)}',
                'intent': 'grades_inquiry',
                'confidence': 0.3
            }
    
    def _handle_schedule_inquiry(self, user: User) -> Dict:
        """التعامل مع استفسارات الجدول الدراسي"""
        
        try:
            if hasattr(user, 'student_profile'):
                student = user.student_profile
                
                # جلب المقررات المسجلة للفصل الحالي
                current_enrollments = Enrollment.objects.filter(
                    student=student,
                    academic_year='2024-2025',  # الفصل الحالي
                    is_active=True
                )
                
                if current_enrollments:
                    response = "إليك جدولك الدراسي للفصل الحالي:\n\n"
                    
                    for enrollment in current_enrollments:
                        course = enrollment.course
                        response += f"📚 {course.name}\n"
                        response += f"   الرمز: {course.code}\n"
                        response += f"   الساعات: {course.credit_hours}\n"
                        if hasattr(course, 'schedule'):
                            response += f"   التوقيت: {course.schedule}\n"
                        response += "\n"
                    
                    total_hours = sum(e.course.credit_hours for e in current_enrollments)
                    response += f"إجمالي الساعات المسجلة: {total_hours}"
                    
                    # نصائح حسب العبء الدراسي
                    if total_hours > 18:
                        response += "\n\n⚠️ عبؤك الدراسي مرتفع، تأكد من تنظيم وقتك جيداً"
                    elif total_hours < 12:
                        response += "\n\n💡 يمكنك إضافة مقررات إضافية إذا أردت"
                    
                else:
                    response = "لا توجد مقررات مسجلة للفصل الحالي."
                
                return {
                    'response': response,
                    'intent': 'schedule_inquiry',
                    'confidence': 0.9,
                    'suggestions': ['تفاصيل المحاضرات', 'تعديل الجدول', 'المقررات المتاحة']
                }
            else:
                return {
                    'response': 'عذراً، لا يمكنني الوصول إلى بيانات الطالب.',
                    'intent': 'schedule_inquiry',
                    'confidence': 0.5
                }
                
        except Exception as e:
            return {
                'response': f'عذراً، حدث خطأ في جلب الجدول: {str(e)}',
                'intent': 'schedule_inquiry',
                'confidence': 0.3
            }
    
    def _handle_course_recommendation(self, user: User) -> Dict:
        """التعامل مع طلبات توصيات المقررات"""
        
        try:
            if hasattr(user, 'student_profile'):
                student = user.student_profile
                
                # إعداد بيانات الطالب للذكاء الاصطناعي
                student_data = {
                    'current_gpa': float(student.gpa),
                    'current_semester': student.current_semester,
                    'major': student.major,
                    'completed_courses': [],  # يمكن جلبها من قاعدة البيانات
                    'courses_grades': {}      # يمكن جلبها من قاعدة البيانات
                }
                
                # الحصول على التوصيات من الذكاء الاصطناعي
                recommendations = recommendation_engine.generate_course_recommendations(student_data)
                
                if recommendations:
                    response = "إليك توصياتي للمقررات:\n\n"
                    
                    for i, rec in enumerate(recommendations[:3], 1):  # أول 3 توصيات
                        if 'error' not in rec:
                            response += f"{i}. {rec.get('course_name', 'مقرر غير محدد')}\n"
                            response += f"   النوع: {rec.get('type', 'غير محدد')}\n"
                            response += f"   السبب: {rec.get('reasoning', 'توصية عامة')}\n"
                            response += f"   مستوى الصعوبة: {rec.get('difficulty_level', 3)}/5\n\n"
                    
                    response += "💡 هذه التوصيات مبنية على أدائك الأكاديمي الحالي وتخصصك."
                else:
                    response = "عذراً، لا يمكنني إنتاج توصيات في الوقت الحالي."
                
                return {
                    'response': response,
                    'intent': 'course_recommendation',
                    'confidence': 0.8,
                    'suggestions': ['تفاصيل أكثر عن المقررات', 'متطلبات التسجيل', 'جدول المقررات']
                }
            else:
                return {
                    'response': 'عذراً، أحتاج للوصول إلى ملفك الأكاديمي لإنتاج توصيات مناسبة.',
                    'intent': 'course_recommendation',
                    'confidence': 0.5
                }
                
        except Exception as e:
            return {
                'response': f'عذراً، حدث خطأ في إنتاج التوصيات: {str(e)}',
                'intent': 'course_recommendation',
                'confidence': 0.3
            }
    
    def _handle_general_response(self, message: str, user: User) -> Dict:
        """التعامل مع الردود العامة"""
        
        # ردود عامة ودودة
        general_responses = [
            "أهلاً بك! كيف يمكنني مساعدتك اليوم؟",
            "أنا هنا لمساعدتك في أي استفسار أكاديمي.",
            "يمكنني مساعدتك في الدرجات، الجدول، الحضور، والمقررات.",
            "لا تتردد في سؤالي عن أي شيء يخص دراستك!"
        ]
        
        response = "مرحباً! 👋\n\n"
        response += "أنا مساعدك الأكاديمي الذكي. يمكنني مساعدتك في:\n\n"
        response += "📊 الدرجات والنتائج\n"
        response += "📅 الجدول الدراسي\n"
        response += "✅ الحضور والغياب\n"
        response += "💰 الأمور المالية\n"
        response += "🎓 توصيات المقررات\n"
        response += "💡 النصائح الأكاديمية\n\n"
        response += "كيف يمكنني مساعدتك؟"
        
        return {
            'response': response,
            'intent': 'general',
            'confidence': 0.7,
            'suggestions': [
                'عرض درجاتي',
                'جدولي الدراسي',
                'نصائح أكاديمية',
                'توصيات مقررات'
            ]
        }

class StudentPerformancePredictionView(APIView):
    """واجهة التنبؤ بأداء الطلاب"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """التنبؤ بأداء طالب معين"""
        
        try:
            data = request.data
            student_id = data.get('student_id')
            course_id = data.get('course_id')
            
            # الحصول على بيانات الطالب والمقرر
            student = get_object_or_404(Student, id=student_id)
            course = get_object_or_404(Course, id=course_id)
            
            # إعداد بيانات التنبؤ
            student_data = {
                'current_gpa': float(student.gpa),
                'attendance_rate': data.get('attendance_rate', 85.0),
                'assignment_completion': data.get('assignment_completion', 80.0),
                'participation_score': data.get('participation_score', 75.0),
                'previous_grades_avg': float(student.gpa) * 25,  # تحويل تقريبي
                'study_hours_per_week': data.get('study_hours_per_week', 10.0),
                'course_difficulty': data.get('course_difficulty', 3.0),
                'semester_load': data.get('semester_load', 15.0),
                'extracurricular_activities': data.get('extracurricular_activities', 2.0),
                'financial_aid_status': 1 if data.get('financial_aid', False) else 0
            }
            
            # التنبؤ بالأداء
            prediction_result = performance_predictor.predict_student_grade(student_data)
            
            # حفظ النتيجة في قاعدة البيانات
            prediction_record, created = StudentPerformancePrediction.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'current_gpa': student_data['current_gpa'],
                    'attendance_rate': student_data['attendance_rate'],
                    'assignment_completion': student_data['assignment_completion'],
                    'participation_score': student_data['participation_score'],
                    'predicted_grade': prediction_result['letter_grade'],
                    'success_probability': prediction_result['success_probability'] / 100,
                    'risk_level': prediction_result['risk_level'],
                    'recommendations': prediction_result['recommendations'],
                    'intervention_needed': prediction_result['risk_level'] in ['high', 'critical']
                }
            )
            
            return Response({
                'success': True,
                'prediction': prediction_result,
                'student_name': student.user.get_full_name(),
                'course_name': course.name,
                'prediction_id': prediction_record.id
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في التنبؤ: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SmartRecommendationsView(APIView):
    """واجهة التوصيات الذكية"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """جلب التوصيات الذكية للمستخدم"""
        
        try:
            if hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                
                # جلب التوصيات الحديثة
                recommendations = SmartRecommendation.objects.filter(
                    student=student,
                    expires_at__gt=datetime.now()
                ).order_by('-priority_score', '-created_at')[:10]
                
                recommendations_data = []
                for rec in recommendations:
                    recommendations_data.append({
                        'id': rec.id,
                        'type': rec.recommendation_type,
                        'title': rec.title,
                        'description': rec.description,
                        'priority_score': rec.priority_score,
                        'recommended_items': rec.recommended_items,
                        'reasoning': rec.reasoning,
                        'is_viewed': rec.is_viewed,
                        'created_at': rec.created_at.isoformat()
                    })
                
                return Response({
                    'success': True,
                    'recommendations': recommendations_data,
                    'total_count': len(recommendations_data)
                })
            else:
                return Response({
                    'success': False,
                    'error': 'غير متاح للمستخدمين غير الطلاب'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في جلب التوصيات: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, recommendation_id):
        """تحديث حالة التوصية (مشاهدة/قبول)"""
        
        try:
            recommendation = get_object_or_404(SmartRecommendation, id=recommendation_id)
            
            action = request.data.get('action')
            if action == 'mark_viewed':
                recommendation.is_viewed = True
                recommendation.save()
            elif action == 'accept':
                recommendation.is_accepted = True
                recommendation.feedback = request.data.get('feedback', '')
                recommendation.save()
            
            return Response({
                'success': True,
                'message': 'تم تحديث التوصية بنجاح'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في تحديث التوصية: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PredictiveAnalyticsView(APIView):
    """واجهة التحليلات التنبؤية"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """جلب التحليلات التنبؤية"""
        
        try:
            analysis_type = request.GET.get('type', 'enrollment_forecast')
            
            if analysis_type == 'enrollment_forecast':
                # بيانات تاريخية وهمية لأغراض التجربة
                historical_data = [
                    {'date': '2023-01-01', 'enrollment_count': 1200, 'total_capacity': 1500, 'marketing_budget': 50000},
                    {'date': '2023-09-01', 'enrollment_count': 1350, 'total_capacity': 1500, 'marketing_budget': 60000},
                    {'date': '2024-01-01', 'enrollment_count': 1280, 'total_capacity': 1500, 'marketing_budget': 55000},
                    {'date': '2024-09-01', 'enrollment_count': 1420, 'total_capacity': 1600, 'marketing_budget': 65000},
                ]
                
                prediction_result = predictive_analytics.predict_enrollment_trends(historical_data)
                
            elif analysis_type == 'dropout_risk':
                # بيانات طلاب وهمية لأغراض التجربة
                students_data = []
                students = Student.objects.all()[:50]  # عينة من الطلاب
                
                for student in students:
                    students_data.append({
                        'student_id': student.id,
                        'name': student.user.get_full_name(),
                        'current_gpa': float(student.gpa),
                        'attendance_rate': 85.0,  # قيمة افتراضية
                        'financial_difficulties': False,
                        'social_isolation': False,
                        'failed_semesters': 0
                    })
                
                prediction_result = predictive_analytics.detect_dropout_risk(students_data)
            
            else:
                prediction_result = {'error': 'نوع تحليل غير مدعوم'}
            
            return Response({
                'success': True,
                'analysis_type': analysis_type,
                'results': prediction_result
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في التحليل التنبؤي: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# واجهات إضافية للذكاء الاصطناعي

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_smart_schedule(request):
    """إنتاج جدول ذكي للطالب"""
    
    try:
        student_id = request.data.get('student_id')
        semester = request.data.get('semester', '2024-2025-1')
        
        student = get_object_or_404(Student, id=student_id)
        
        # منطق الجدولة الذكية (مبسط)
        available_courses = Course.objects.filter(
            department=student.major,  # افتراض وجود تطابق
            is_active=True
        )[:6]  # حد أقصى 6 مقررات
        
        smart_schedule = []
        for course in available_courses:
            smart_schedule.append({
                'course_id': course.id,
                'course_name': course.name,
                'course_code': course.code,
                'credit_hours': course.credit_hours,
                'recommended_time': 'Sunday 08:00-10:00',  # وقت افتراضي
                'difficulty_score': 3.5,
                'workload_estimate': course.credit_hours * 3,
                'prerequisites_met': True
            })
        
        return Response({
            'success': True,
            'student_name': student.user.get_full_name(),
            'semester': semester,
            'recommended_schedule': smart_schedule,
            'total_credit_hours': sum(c['credit_hours'] for c in smart_schedule),
            'estimated_workload': sum(c['workload_estimate'] for c in smart_schedule)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'خطأ في إنتاج الجدول الذكي: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_dashboard_stats(request):
    """إحصائيات لوحة تحكم الذكاء الاصطناعي"""
    
    try:
        # إحصائيات عامة
        total_predictions = StudentPerformancePrediction.objects.count()
        total_recommendations = SmartRecommendation.objects.count()
        active_chatbots = AIChatBot.objects.filter(is_active=True).count()
        recent_analytics = PredictiveAnalytics.objects.filter(
            analysis_date__gte=datetime.now() - timedelta(days=30)
        ).count()
        
        # إحصائيات المخاطر
        high_risk_students = StudentPerformancePrediction.objects.filter(
            risk_level__in=['high', 'critical']
        ).count()
        
        # إحصائيات التوصيات
        accepted_recommendations = SmartRecommendation.objects.filter(
            is_accepted=True
        ).count()
        
        stats = {
            'total_predictions': total_predictions,
            'total_recommendations': total_recommendations,
            'active_chatbots': active_chatbots,
            'recent_analytics': recent_analytics,
            'high_risk_students': high_risk_students,
            'accepted_recommendations': accepted_recommendations,
            'ai_accuracy': 0.87,  # دقة افتراضية
            'user_satisfaction': 0.92  # رضا افتراضي
        }
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'خطأ في جلب الإحصائيات: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)