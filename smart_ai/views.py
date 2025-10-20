from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    AIAnalyticsModel, StudentPerformancePrediction, AIChatBot,
    ChatMessage, SmartRecommendation, PredictiveAnalytics,
    AISecurityAlert, SmartScheduling
)
from .serializers import (
    AIAnalyticsModelSerializer, StudentPerformancePredictionSerializer,
    AIChatBotSerializer, ChatMessageSerializer, SmartRecommendationSerializer,
    PredictiveAnalyticsSerializer, AISecurityAlertSerializer,
    SmartSchedulingSerializer
)
from .ai_engine import (
    StudentPerformancePredictor, SmartRecommendationEngine,
    SecurityAIEngine, SchedulingAI
)
from students.models import Student
from courses.models import Course

# =============================================================================
# Student Performance Prediction API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_student_performance(request):
    """API للتنبؤ بأداء الطالب"""
    try:
        student_id = request.data.get('student_id')
        course_id = request.data.get('course_id')
        
        if not student_id or not course_id:
            return Response({
                'error': 'student_id و course_id مطلوبان'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        predictor = StudentPerformancePredictor()
        result = predictor.predict_student_performance(student_id, course_id)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_predictions(request, student_id):
    """الحصول على جميع تنبؤات الطالب"""
    try:
        predictions = StudentPerformancePrediction.objects.filter(
            student_id=student_id
        ).order_by('-prediction_date')
        
        serializer = StudentPerformancePredictionSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# Smart Recommendations API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_course_recommendations(request):
    """إنشاء توصيات المقررات للطالب"""
    try:
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response({
                'error': 'student_id مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        recommendation_engine = SmartRecommendationEngine()
        recommendations = recommendation_engine.generate_course_recommendations(student_id)
        
        return Response({
            'student_id': student_id,
            'recommendations': recommendations
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_recommendations(request, student_id):
    """الحصول على توصيات الطالب"""
    try:
        recommendations = SmartRecommendation.objects.filter(
            student_id=student_id,
            expires_at__gt=timezone.now()
        ).order_by('-priority_score', '-created_at')
        
        serializer = SmartRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# AI Chatbot API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    """محادثة مع المساعد الذكي"""
    try:
        user = request.user
        message = request.data.get('message', '')
        chat_type = request.data.get('chat_type', 'student_support')
        session_id = request.data.get('session_id')
        
        if not message:
            return Response({
                'error': 'الرسالة مطلوبة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # العثور على جلسة المحادثة أو إنشاء جديدة
        if session_id:
            chatbot = get_object_or_404(AIChatBot, session_id=session_id, user=user)
        else:
            import uuid
            chatbot = AIChatBot.objects.create(
                user=user,
                chat_type=chat_type,
                session_id=str(uuid.uuid4())
            )
        
        # معالجة الرسالة وإنشاء الرد
        ai_response = process_ai_message(message, chat_type, user)
        
        # حفظ المحادثة
        chat_message = ChatMessage.objects.create(
            chatbot=chatbot,
            message=message,
            response=ai_response['response'],
            user_intent=ai_response.get('intent', ''),
            confidence_score=ai_response.get('confidence', 0.8)
        )
        
        return Response({
            'session_id': chatbot.session_id,
            'response': ai_response['response'],
            'intent': ai_response.get('intent', ''),
            'confidence': ai_response.get('confidence', 0.8),
            'suggestions': ai_response.get('suggestions', [])
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def process_ai_message(message: str, chat_type: str, user) -> dict:
    """معالجة رسالة المستخدم وإنشاء رد ذكي"""
    message_lower = message.lower()
    
    # تحليل قصد المستخدم
    intent = detect_user_intent(message_lower, chat_type)
    
    # إنشاء الرد حسب النوع والقصد
    if chat_type == 'student_support':
        response = generate_student_support_response(message_lower, intent, user)
    elif chat_type == 'academic_advisor':
        response = generate_academic_advisor_response(message_lower, intent, user)
    elif chat_type == 'financial_assistant':
        response = generate_financial_response(message_lower, intent, user)
    else:
        response = generate_general_response(message_lower, intent)
    
    return {
        'response': response,
        'intent': intent,
        'confidence': 0.85,
        'suggestions': get_follow_up_suggestions(intent, chat_type)
    }

def detect_user_intent(message: str, chat_type: str) -> str:
    """كشف قصد المستخدم من الرسالة"""
    # كلمات مفتاحية للأقسام المختلفة
    intents = {
        'grades_inquiry': ['درجات', 'علامات', 'نتائج', 'امتحان'],
        'schedule_inquiry': ['جدول', 'محاضرات', 'مواعيد', 'وقت'],
        'registration': ['تسجيل', 'تسجيل مقررات', 'حذف مقرر'],
        'financial_inquiry': ['رسوم', 'دفع', 'مالية', 'فاتورة'],
        'general_help': ['مساعدة', 'كيف', 'ماذا', 'متى'],
        'complaint': ['شكوى', 'مشكلة', 'خطأ', 'لا يعمل']
    }
    
    for intent, keywords in intents.items():
        if any(keyword in message for keyword in keywords):
            return intent
    
    return 'general_help'

def generate_student_support_response(message: str, intent: str, user) -> str:
    """إنشاء رد دعم الطلاب"""
    responses = {
        'grades_inquiry': f"مرحباً {user.get_full_name()}! يمكنك مراجعة درجاتك من خلال لوحة التحكم الخاصة بك. هل تريد مساعدة في فهم كيفية حساب المعدل التراكمي؟",
        
        'schedule_inquiry': "يمكنك الاطلاع على جدولك الدراسي من قسم 'الجداول' في حسابك. أو يمكنني مساعدتك في العثور على مواعيد محاضرة معينة.",
        
        'registration': "لتسجيل المقررات، اذهب إلى قسم 'التسجيل' واختر المقررات المتاحة. تأكد من استيفاء المتطلبات السابقة.",
        
        'financial_inquiry': "للاستعلام عن الرسوم الدراسية، يرجى زيارة قسم 'الشؤون المالية' في حسابك أو التواصل مع قسم المحاسبة.",
        
        'general_help': "مرحباً بك! أنا المساعد الذكي للطلاب. يمكنني مساعدتك في الاستفسار عن الدرجات، الجداول، التسجيل، والرسوم الدراسية. كيف يمكنني مساعدتك اليوم؟",
        
        'complaint': "أتفهم مشكلتك. سأقوم بتوجيه شكواك إلى القسم المختص. في هذه الأثناء، يمكنك التواصل مباشرة مع خدمة الطلاب."
    }
    
    return responses.get(intent, responses['general_help'])

def generate_academic_advisor_response(message: str, intent: str, user) -> str:
    """رد المستشار الأكاديمي"""
    return "كمستشار أكاديمي، أنصحك بمراجعة خطتك الدراسية والتأكد من استيفاء المتطلبات. هل تحتاج مساعدة في اختيار المقررات للفصل القادم؟"

def generate_financial_response(message: str, intent: str, user) -> str:
    """رد المساعد المالي"""
    return "بخصوص الشؤون المالية، يمكنك مراجعة حسابك المالي وطرق الدفع المتاحة. هل تحتاج مساعدة في سداد الرسوم أو الاستعلام عن المنح؟"

def generate_general_response(message: str, intent: str) -> str:
    """رد عام"""
    return "شكراً لتواصلك معنا. كيف يمكنني مساعدتك اليوم؟ يمكنني الإجابة على استفساراتك الأكاديمية والإدارية."

def get_follow_up_suggestions(intent: str, chat_type: str) -> list:
    """اقتراحات للمتابعة"""
    suggestions = {
        'grades_inquiry': [
            "كيف يتم حساب المعدل التراكمي؟",
            "متى تظهر درجات الامتحانات؟",
            "كيف أطعن في درجة؟"
        ],
        'schedule_inquiry': [
            "أريد تغيير وقت محاضرة",
            "كيف أتجنب تعارض الجداول؟",
            "أين تقام المحاضرة؟"
        ],
        'registration': [
            "ما هي المقررات المتاحة؟",
            "كيف أحذف مقرر؟",
            "متى ينتهي وقت التسجيل؟"
        ]
    }
    
    return suggestions.get(intent, [
        "هل يمكنك المساعدة في أمر آخر؟",
        "أريد التحدث مع مختص",
        "شكراً لك"
    ])

# =============================================================================
# Security AI API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_security_event(request):
    """تحليل حدث أمني"""
    try:
        user_id = request.data.get('user_id')
        ip_address = request.data.get('ip_address')
        user_agent = request.data.get('user_agent', '')
        event_type = request.data.get('event_type', 'login')
        
        security_ai = SecurityAIEngine()
        analysis = security_ai.analyze_login_attempt(
            user_id, ip_address, user_agent, True
        )
        
        # إنشاء تنبيه أمني إذا لزم الأمر
        if analysis['threat_level'] in ['high', 'critical']:
            AISecurityAlert.objects.create(
                alert_type='suspicious_activity',
                severity=analysis['threat_level'],
                title=f"نشاط مشبوه من المستخدم {user_id}",
                description=f"تم كشف تهديدات: {', '.join(analysis['threats_detected'])}",
                affected_user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return Response(analysis, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# Smart Scheduling API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_smart_schedule(request):
    """إنشاء جدول ذكي"""
    try:
        semester = request.data.get('semester')
        academic_year = request.data.get('academic_year')
        
        if not semester or not academic_year:
            return Response({
                'error': 'semester و academic_year مطلوبان'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على المقررات المطلوب جدولتها
        courses = Course.objects.filter(is_active=True)
        
        # إنشاء بيانات وهمية للقاعات والمدرسين
        rooms = [{'id': i, 'name': f'قاعة {i}', 'capacity': 50} for i in range(1, 11)]
        instructors = [{'id': i, 'name': f'أستاذ {i}'} for i in range(1, 6)]
        
        scheduling_ai = SchedulingAI()
        schedule_result = scheduling_ai.generate_optimal_schedule(
            list(courses), rooms, instructors
        )
        
        # حفظ الجدول الذكي
        smart_schedule = SmartScheduling.objects.create(
            name=f"جدول {semester} {academic_year}",
            semester=semester,
            academic_year=academic_year,
            algorithm_used='genetic_algorithm',
            schedule_data=schedule_result['schedule'],
            fitness_score=schedule_result['fitness_score'],
            conflicts_resolved=schedule_result['conflicts'],
            is_optimal=schedule_result['is_optimal'],
            generated_by=request.user
        )
        
        serializer = SmartSchedulingSerializer(smart_schedule)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# Analytics Dashboard API
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_dashboard_data(request):
    """الحصول على بيانات لوحة تحكم الذكاء الاصطناعي"""
    try:
        dashboard_data = {
            'predictions_count': StudentPerformancePrediction.objects.count(),
            'at_risk_students': StudentPerformancePrediction.objects.filter(
                risk_level__in=['high', 'critical']
            ).count(),
            'active_chatbots': AIChatBot.objects.filter(is_active=True).count(),
            'security_alerts': AISecurityAlert.objects.filter(
                is_resolved=False
            ).count(),
            'recommendations_given': SmartRecommendation.objects.count(),
            'recommendations_accepted': SmartRecommendation.objects.filter(
                is_accepted=True
            ).count(),
        }
        
        # إحصائيات إضافية
        dashboard_data['success_rate'] = (
            dashboard_data['recommendations_accepted'] / 
            max(dashboard_data['recommendations_given'], 1) * 100
        )
        
        return Response(dashboard_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# Generic AI Model Views
# =============================================================================

class AIAnalyticsModelListView(generics.ListCreateAPIView):
    queryset = AIAnalyticsModel.objects.all()
    serializer_class = AIAnalyticsModelSerializer
    permission_classes = [IsAuthenticated]

class StudentPerformancePredictionListView(generics.ListCreateAPIView):
    queryset = StudentPerformancePrediction.objects.all().order_by('-prediction_date')
    serializer_class = StudentPerformancePredictionSerializer
    permission_classes = [IsAuthenticated]

class SmartRecommendationListView(generics.ListCreateAPIView):
    queryset = SmartRecommendation.objects.all().order_by('-created_at')
    serializer_class = SmartRecommendationSerializer
    permission_classes = [IsAuthenticated]

class AISecurityAlertListView(generics.ListCreateAPIView):
    queryset = AISecurityAlert.objects.all().order_by('-detected_at')
    serializer_class = AISecurityAlertSerializer
    permission_classes = [IsAuthenticated]