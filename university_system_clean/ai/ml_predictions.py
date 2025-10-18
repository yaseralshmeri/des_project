"""
Machine Learning Predictions for Student Performance
Advanced AI features for academic performance prediction and course recommendations
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import warnings
warnings.filterwarnings('ignore')

from django.db.models import Avg, Count, Sum, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from students.models import Student, User
from courses.models import Course
from academic.models import Enrollment, Grade, Attendance, Semester
from .models import PerformancePrediction, CourseRecommendation, StudyPattern


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_student_performance(request):
    """
    Predict student performance for next semester based on historical data
    """
    if not request.user.role in ['ADMIN', 'STAFF', 'TEACHER'] and not request.user.is_student:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student_id = request.data.get('student_id')
        if not student_id and request.user.is_student:
            student_id = request.user.student_profile.id
        
        if not student_id:
            return Response(
                {'error': 'Student ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student = Student.objects.get(id=student_id)
        
        # Collect student data for prediction
        student_data = collect_student_features(student)
        
        if not student_data:
            return Response(
                {'error': 'Insufficient data for prediction'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load or train model
        model = get_or_train_performance_model()
        
        # Make prediction
        features = np.array([list(student_data.values())]).reshape(1, -1)
        predicted_gpa = model.predict(features)[0]
        
        # Calculate confidence based on historical accuracy
        confidence = calculate_prediction_confidence(student, predicted_gpa)
        
        # Generate recommendations
        recommendations = generate_performance_recommendations(student, predicted_gpa)
        
        # Save prediction to database
        prediction = PerformancePrediction.objects.create(
            student=student,
            predicted_gpa=predicted_gpa,
            confidence_score=confidence,
            features_used=student_data,
            semester=Semester.objects.filter(is_current=True).first()
        )
        
        return Response({
            'student_id': student.id,
            'student_name': student.user.get_full_name(),
            'current_gpa': float(student.gpa),
            'predicted_gpa': round(predicted_gpa, 2),
            'confidence_score': round(confidence, 2),
            'prediction_trend': 'improving' if predicted_gpa > student.gpa else 'declining' if predicted_gpa < student.gpa else 'stable',
            'recommendations': recommendations,
            'features_analyzed': list(student_data.keys())
        }, status=status.HTTP_200_OK)
        
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Prediction failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_courses(request):
    """
    Recommend courses for student based on performance patterns and preferences
    """
    if not request.user.is_student and not request.user.role in ['ADMIN', 'STAFF']:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student_id = request.data.get('student_id')
        if not student_id and request.user.is_student:
            student_id = request.user.student_profile.id
        
        student = Student.objects.get(id=student_id)
        current_semester = Semester.objects.filter(is_current=True).first()
        
        # Get student's course history and performance
        completed_enrollments = Enrollment.objects.filter(
            student=student,
            status='COMPLETED'
        ).select_related('course')
        
        # Analyze performance patterns
        performance_by_department = {}
        for enrollment in completed_enrollments:
            dept = enrollment.course.department.name
            if dept not in performance_by_department:
                performance_by_department[dept] = []
            performance_by_department[dept].append(enrollment.final_grade or 0)
        
        # Calculate average performance per department
        dept_averages = {
            dept: np.mean(grades) 
            for dept, grades in performance_by_department.items()
        }
        
        # Get available courses
        enrolled_courses = Enrollment.objects.filter(
            student=student,
            semester=current_semester,
            status__in=['ENROLLED', 'COMPLETED']
        ).values_list('course_id', flat=True)
        
        available_courses = Course.objects.filter(
            is_active=True,
            semester_offered=student.current_semester
        ).exclude(id__in=enrolled_courses)
        
        # Score courses based on multiple factors
        course_recommendations = []
        for course in available_courses:
            score = calculate_course_score(student, course, dept_averages)
            
            if score > 0.5:  # Threshold for recommendation
                course_recommendations.append({
                    'course_id': course.id,
                    'course_code': course.code,
                    'course_name': course.name,
                    'department': course.department.name,
                    'credits': course.credits,
                    'recommendation_score': round(score, 2),
                    'predicted_performance': predict_course_performance(student, course),
                    'reasons': get_recommendation_reasons(student, course, dept_averages)
                })
        
        # Sort by recommendation score
        course_recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        # Save recommendations to database
        for rec in course_recommendations[:10]:  # Top 10 recommendations
            CourseRecommendation.objects.create(
                student=student,
                course_id=rec['course_id'],
                recommendation_score=rec['recommendation_score'],
                predicted_grade=rec['predicted_performance'],
                reasons=rec['reasons']
            )
        
        return Response({
            'student_id': student.id,
            'student_name': student.user.get_full_name(),
            'current_semester': student.current_semester,
            'total_recommendations': len(course_recommendations),
            'recommendations': course_recommendations[:10]  # Top 10
        }, status=status.HTTP_200_OK)
        
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Course recommendation failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_study_patterns(request):
    """
    Analyze student study patterns and provide insights
    """
    if not request.user.is_student and not request.user.role in ['ADMIN', 'STAFF']:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student_id = request.GET.get('student_id')
        if not student_id and request.user.is_student:
            student_id = request.user.student_profile.id
        
        student = Student.objects.get(id=student_id)
        
        # Analyze attendance patterns
        attendance_pattern = analyze_attendance_patterns(student)
        
        # Analyze grade patterns
        grade_pattern = analyze_grade_patterns(student)
        
        # Analyze course load patterns
        course_load_pattern = analyze_course_load_patterns(student)
        
        # Generate insights and recommendations
        insights = generate_study_insights(attendance_pattern, grade_pattern, course_load_pattern)
        
        # Save study pattern analysis
        study_pattern = StudyPattern.objects.create(
            student=student,
            attendance_pattern=attendance_pattern,
            grade_pattern=grade_pattern,
            course_load_pattern=course_load_pattern,
            insights=insights
        )
        
        return Response({
            'student_id': student.id,
            'student_name': student.user.get_full_name(),
            'analysis_date': study_pattern.created_at,
            'attendance_analysis': attendance_pattern,
            'grade_analysis': grade_pattern,
            'course_load_analysis': course_load_pattern,
            'insights_and_recommendations': insights
        }, status=status.HTTP_200_OK)
        
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Study pattern analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def collect_student_features(student):
    """
    Collect relevant features for machine learning model
    """
    features = {}
    
    # Basic student info
    features['current_gpa'] = float(student.gpa)
    features['current_semester'] = student.current_semester
    
    # Historical performance
    completed_enrollments = Enrollment.objects.filter(
        student=student,
        status='COMPLETED',
        final_grade__isnull=False
    )
    
    if completed_enrollments.count() < 3:  # Need minimum data
        return None
    
    grades = [e.final_grade for e in completed_enrollments]
    features['avg_grade'] = np.mean(grades)
    features['grade_std'] = np.std(grades)
    features['grade_trend'] = calculate_grade_trend(grades)
    
    # Course load analysis
    features['avg_courses_per_semester'] = calculate_avg_course_load(student)
    features['avg_credits_per_semester'] = calculate_avg_credits(student)
    
    # Attendance patterns
    attendance_rate = calculate_attendance_rate(student)
    features['attendance_rate'] = attendance_rate
    
    # Department performance
    dept_performance = calculate_department_performance(student)
    features['best_dept_performance'] = max(dept_performance.values()) if dept_performance else 0
    features['worst_dept_performance'] = min(dept_performance.values()) if dept_performance else 0
    
    return features


def get_or_train_performance_model():
    """
    Get existing model or train new one if needed
    """
    try:
        # Try to load existing model
        model = joblib.load('/tmp/performance_model.pkl')
        return model
    except:
        # Train new model
        return train_performance_model()


def train_performance_model():
    """
    Train machine learning model for performance prediction
    """
    # Collect training data from all students
    students = Student.objects.filter(status='ACTIVE')
    training_data = []
    
    for student in students:
        features = collect_student_features(student)
        if features:
            # Add target variable (next semester GPA)
            next_semester_gpa = get_next_semester_gpa(student)
            if next_semester_gpa:
                features['target_gpa'] = next_semester_gpa
                training_data.append(features)
    
    if len(training_data) < 10:  # Need minimum samples
        # Return simple model if insufficient data
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        # Create dummy data for training
        X = np.random.random((10, 8))
        y = np.random.random(10) * 4  # GPA range 0-4
        model.fit(X, y)
        return model
    
    # Convert to DataFrame
    df = pd.DataFrame(training_data)
    
    # Separate features and target
    X = df.drop('target_gpa', axis=1)
    y = df['target_gpa']
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save model
    joblib.dump(model, '/tmp/performance_model.pkl')
    
    return model


def calculate_prediction_confidence(student, predicted_gpa):
    """
    Calculate confidence score for prediction
    """
    # Simple confidence calculation based on data availability
    completed_courses = Enrollment.objects.filter(
        student=student,
        status='COMPLETED'
    ).count()
    
    # More courses = higher confidence
    base_confidence = min(completed_courses / 10.0, 1.0) * 80
    
    # Adjust based on GPA stability
    grades = [e.final_grade for e in Enrollment.objects.filter(
        student=student,
        status='COMPLETED',
        final_grade__isnull=False
    )[:5]]  # Last 5 courses
    
    if len(grades) > 1:
        stability = 1 / (1 + np.std(grades))  # Lower std = higher stability
        base_confidence += stability * 20
    
    return min(base_confidence, 100)


def generate_performance_recommendations(student, predicted_gpa):
    """
    Generate actionable recommendations based on prediction
    """
    recommendations = []
    current_gpa = float(student.gpa)
    
    if predicted_gpa < current_gpa:
        recommendations.extend([
            "Consider reducing course load next semester",
            "Schedule regular study sessions and stick to them",
            "Seek tutoring for challenging subjects",
            "Meet with academic advisor to discuss strategies"
        ])
    elif predicted_gpa > current_gpa:
        recommendations.extend([
            "Great progress! Continue current study habits",
            "Consider taking on leadership roles or internships",
            "Explore advanced courses in your area of strength"
        ])
    else:
        recommendations.extend([
            "Maintain current study schedule",
            "Look for opportunities to improve in weaker subjects",
            "Consider exploring new academic interests"
        ])
    
    # Add attendance-based recommendations
    attendance_rate = calculate_attendance_rate(student)
    if attendance_rate < 85:
        recommendations.append("Improve class attendance - it strongly correlates with performance")
    
    return recommendations


def calculate_course_score(student, course, dept_averages):
    """
    Calculate recommendation score for a course
    """
    score = 0.5  # Base score
    
    # Department performance factor
    dept_name = course.department.name
    if dept_name in dept_averages:
        dept_performance = dept_averages[dept_name] / 100.0  # Normalize to 0-1
        score += dept_performance * 0.3
    
    # Course difficulty (based on average grades of all students)
    avg_course_grade = Enrollment.objects.filter(
        course=course,
        status='COMPLETED',
        final_grade__isnull=False
    ).aggregate(avg=Avg('final_grade'))['avg']
    
    if avg_course_grade:
        # Higher average grade = easier course = higher score
        difficulty_factor = avg_course_grade / 100.0
        score += difficulty_factor * 0.2
    
    # Prerequisites met factor
    from academic.enrollment_views import check_prerequisites
    prereq_met, _ = check_prerequisites(student, course)
    if prereq_met:
        score += 0.2
    else:
        score -= 0.3
    
    return max(0, min(1, score))


def predict_course_performance(student, course):
    """
    Predict student's likely grade in a specific course
    """
    # Simple prediction based on department performance
    student_enrollments = Enrollment.objects.filter(
        student=student,
        course__department=course.department,
        status='COMPLETED',
        final_grade__isnull=False
    )
    
    if student_enrollments.exists():
        avg_grade = student_enrollments.aggregate(avg=Avg('final_grade'))['avg']
        # Add some variation based on course difficulty
        course_difficulty = get_course_difficulty(course)
        adjusted_grade = avg_grade * (1 - course_difficulty * 0.1)
        return round(max(0, min(100, adjusted_grade)), 1)
    else:
        # Default prediction based on overall GPA
        return round(float(student.gpa) * 25, 1)  # Convert 4.0 scale to 100 scale


def get_recommendation_reasons(student, course, dept_averages):
    """
    Generate reasons for course recommendation
    """
    reasons = []
    
    dept_name = course.department.name
    if dept_name in dept_averages and dept_averages[dept_name] > 80:
        reasons.append(f"Strong performance in {dept_name} courses")
    
    # Check prerequisite completion
    from academic.enrollment_views import check_prerequisites
    prereq_met, _ = check_prerequisites(student, course)
    if prereq_met:
        reasons.append("All prerequisites completed")
    
    # Course popularity/success rate
    success_rate = calculate_course_success_rate(course)
    if success_rate > 85:
        reasons.append(f"High success rate ({success_rate}%) among students")
    
    return reasons


# Helper functions for analysis
def calculate_grade_trend(grades):
    """Calculate if grades are improving, declining, or stable"""
    if len(grades) < 2:
        return 0
    
    # Simple linear trend
    x = np.arange(len(grades))
    z = np.polyfit(x, grades, 1)
    return z[0]  # Slope indicates trend


def calculate_avg_course_load(student):
    """Calculate average number of courses per semester"""
    semesters = Enrollment.objects.filter(student=student).values(
        'semester'
    ).distinct().count()
    
    total_courses = Enrollment.objects.filter(student=student).count()
    
    return total_courses / semesters if semesters > 0 else 0


def calculate_avg_credits(student):
    """Calculate average credits per semester"""
    enrollments = Enrollment.objects.filter(student=student)
    semesters = enrollments.values('semester').distinct().count()
    total_credits = sum([e.course.credits for e in enrollments])
    
    return total_credits / semesters if semesters > 0 else 0


def calculate_attendance_rate(student):
    """Calculate overall attendance rate for student"""
    total_records = Attendance.objects.filter(
        enrollment__student=student
    ).count()
    
    present_records = Attendance.objects.filter(
        enrollment__student=student,
        status='PRESENT'
    ).count()
    
    return (present_records / total_records * 100) if total_records > 0 else 100


def calculate_department_performance(student):
    """Calculate average performance per department"""
    enrollments = Enrollment.objects.filter(
        student=student,
        status='COMPLETED',
        final_grade__isnull=False
    )
    
    dept_performance = {}
    for enrollment in enrollments:
        dept = enrollment.course.department.name
        if dept not in dept_performance:
            dept_performance[dept] = []
        dept_performance[dept].append(enrollment.final_grade)
    
    return {dept: np.mean(grades) for dept, grades in dept_performance.items()}


def get_next_semester_gpa(student):
    """Get GPA from next semester for training data"""
    # This would require historical data - simplified for now
    return None


def get_course_difficulty(course):
    """Calculate course difficulty based on average grades"""
    avg_grade = Enrollment.objects.filter(
        course=course,
        status='COMPLETED',
        final_grade__isnull=False
    ).aggregate(avg=Avg('final_grade'))['avg']
    
    if avg_grade:
        # Lower average grade = higher difficulty
        return (100 - avg_grade) / 100.0
    return 0.5  # Default medium difficulty


def calculate_course_success_rate(course):
    """Calculate percentage of students who passed the course"""
    total_students = Enrollment.objects.filter(
        course=course,
        status='COMPLETED'
    ).count()
    
    passed_students = Enrollment.objects.filter(
        course=course,
        status='COMPLETED',
        final_grade__gte=60  # Assuming 60 is passing grade
    ).count()
    
    return (passed_students / total_students * 100) if total_students > 0 else 0


def analyze_attendance_patterns(student):
    """Analyze student's attendance patterns"""
    # Simplified analysis
    attendance_rate = calculate_attendance_rate(student)
    return {
        'overall_rate': round(attendance_rate, 2),
        'pattern': 'consistent' if attendance_rate > 90 else 'irregular' if attendance_rate < 70 else 'moderate'
    }


def analyze_grade_patterns(student):
    """Analyze student's grade patterns"""
    grades = [e.final_grade for e in Enrollment.objects.filter(
        student=student,
        status='COMPLETED',
        final_grade__isnull=False
    ).order_by('enrollment_date')]
    
    if len(grades) < 2:
        return {'trend': 'insufficient_data'}
    
    trend = calculate_grade_trend(grades)
    return {
        'trend': 'improving' if trend > 1 else 'declining' if trend < -1 else 'stable',
        'consistency': 'high' if np.std(grades) < 10 else 'low'
    }


def analyze_course_load_patterns(student):
    """Analyze student's course load patterns"""
    avg_load = calculate_avg_course_load(student)
    return {
        'average_courses': round(avg_load, 1),
        'load_level': 'heavy' if avg_load > 6 else 'light' if avg_load < 4 else 'moderate'
    }


def generate_study_insights(attendance_pattern, grade_pattern, course_load_pattern):
    """Generate insights based on patterns"""
    insights = []
    
    if attendance_pattern['overall_rate'] < 80:
        insights.append("Low attendance is likely affecting your grades - try to attend classes more regularly")
    
    if grade_pattern.get('trend') == 'declining':
        insights.append("Your grades show a declining trend - consider meeting with an academic advisor")
    
    if course_load_pattern['load_level'] == 'heavy' and grade_pattern.get('consistency') == 'low':
        insights.append("Heavy course load might be affecting grade consistency - consider reducing courses")
    
    return insights