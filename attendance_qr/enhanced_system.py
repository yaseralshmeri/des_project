# نظام QR Code المتطور للحضور والغياب
# Advanced QR Code Attendance System with Security

import qrcode
import base64
import json
import hashlib
import datetime
from io import BytesIO
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import uuid
from typing import Dict, List, Optional, Tuple
import secrets

logger = logging.getLogger(__name__)

User = get_user_model()

class SecureQRGenerator:
    """مولد رموز QR آمنة للحضور"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """الحصول على مفتاح التشفير أو إنشاؤه"""
        key_cache = cache.get('qr_encryption_key')
        if key_cache:
            return key_cache.encode()
        
        # إنشاء مفتاح جديد
        password = settings.SECRET_KEY.encode()
        salt = b'attendance_qr_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        # حفظ المفتاح في الكاش
        cache.set('qr_encryption_key', key.decode(), timeout=None)
        return key
    
    def generate_session_qr(self, session_data: Dict) -> Dict:
        """إنشاء رمز QR لجلسة دراسية"""
        try:
            # إنشاء رمز فريد للجلسة
            session_token = self._generate_session_token()
            
            # بيانات الجلسة المشفرة
            qr_data = {
                'session_id': session_data['session_id'],
                'course_id': session_data['course_id'],
                'teacher_id': session_data['teacher_id'],
                'session_date': session_data['session_date'],
                'session_time': session_data['session_time'],
                'location': session_data.get('location', ''),
                'token': session_token,
                'expires_at': (timezone.now() + datetime.timedelta(hours=2)).isoformat(),
                'checksum': self._calculate_checksum(session_data)
            }
            
            # تشفير البيانات
            encrypted_data = self.cipher_suite.encrypt(json.dumps(qr_data).encode())
            encoded_data = base64.urlsafe_b64encode(encrypted_data).decode()
            
            # إنشاء رمز QR
            qr_image = self._create_qr_image(encoded_data)
            
            # حفظ بيانات الجلسة في الكاش للتحقق
            cache_key = f"qr_session_{session_token}"
            cache.set(cache_key, qr_data, timeout=7200)  # ساعتان
            
            return {
                'qr_code': qr_image,
                'session_token': session_token,
                'expires_at': qr_data['expires_at'],
                'encrypted_data': encoded_data
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رمز QR: {str(e)}")
            raise
    
    def _generate_session_token(self) -> str:
        """توليد رمز جلسة فريد وآمن"""
        return secrets.token_urlsafe(32)
    
    def _calculate_checksum(self, data: Dict) -> str:
        """حساب المجموع التحقق للبيانات"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _create_qr_image(self, data: str) -> str:
        """إنشاء صورة رمز QR"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # إنشاء الصورة
        img = qr.make_image(fill_color="black", back_color="white")
        
        # تحويل إلى base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"

class AttendanceVerifier:
    """مُحقق الحضور من رموز QR"""
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """الحصول على مفتاح التشفير"""
        key_cache = cache.get('qr_encryption_key')
        if not key_cache:
            raise ValueError("مفتاح التشفير غير موجود")
        return key_cache.encode()
    
    def verify_and_record_attendance(self, qr_data: str, student_id: str, 
                                   location_data: Dict = None) -> Dict:
        """التحقق من رمز QR وتسجيل الحضور"""
        try:
            # فك تشفير البيانات
            session_data = self._decrypt_qr_data(qr_data)
            
            # التحقق من صحة الجلسة
            verification_result = self._verify_session(session_data, student_id, location_data)
            
            if verification_result['valid']:
                # تسجيل الحضور
                attendance_record = self._record_attendance(session_data, student_id)
                verification_result['attendance_record'] = attendance_record
            
            return verification_result
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الحضور: {str(e)}")
            return {
                'valid': False,
                'error': 'فشل في التحقق من رمز QR',
                'details': str(e)
            }
    
    def _decrypt_qr_data(self, encrypted_data: str) -> Dict:
        """فك تشفير بيانات رمز QR"""
        try:
            # فك الترميز
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # فك التشفير
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            
            # تحويل إلى JSON
            session_data = json.loads(decrypted_data.decode())
            
            return session_data
            
        except Exception as e:
            raise ValueError(f"فشل في فك تشفير البيانات: {str(e)}")
    
    def _verify_session(self, session_data: Dict, student_id: str, 
                       location_data: Dict = None) -> Dict:
        """التحقق من صحة جلسة الحضور"""
        try:
            # التحقق من انتهاء الصلاحية
            expires_at = datetime.datetime.fromisoformat(session_data['expires_at'].replace('Z', '+00:00'))
            if timezone.now() > expires_at:
                return {
                    'valid': False,
                    'error': 'انتهت صلاحية رمز QR',
                    'error_code': 'EXPIRED'
                }
            
            # التحقق من وجود الجلسة في الكاش
            cache_key = f"qr_session_{session_data['token']}"
            cached_session = cache.get(cache_key)
            if not cached_session:
                return {
                    'valid': False,
                    'error': 'جلسة غير صالحة أو منتهية',
                    'error_code': 'INVALID_SESSION'
                }
            
            # التحقق من عدم استخدام الرمز مسبقاً من نفس الطالب
            attendance_key = f"attendance_{session_data['session_id']}_{student_id}"
            if cache.get(attendance_key):
                return {
                    'valid': False,
                    'error': 'تم تسجيل الحضور مسبقاً',
                    'error_code': 'ALREADY_RECORDED'
                }
            
            # التحقق من تسجيل الطالب في المقرر
            enrollment_check = self._verify_student_enrollment(
                student_id, session_data['course_id']
            )
            if not enrollment_check['enrolled']:
                return {
                    'valid': False,
                    'error': 'الطالب غير مسجل في هذا المقرر',
                    'error_code': 'NOT_ENROLLED'
                }
            
            # التحقق من الموقع (إذا كان متوفراً)
            location_check = self._verify_location(session_data, location_data)
            if not location_check['valid']:
                return location_check
            
            return {
                'valid': True,
                'session_data': session_data,
                'student_enrollment': enrollment_check
            }
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الجلسة: {str(e)}")
            return {
                'valid': False,
                'error': 'خطأ في التحقق من الجلسة',
                'error_code': 'VERIFICATION_ERROR'
            }
    
    def _verify_student_enrollment(self, student_id: str, course_id: str) -> Dict:
        """التحقق من تسجيل الطالب في المقرر"""
        try:
            # استيراد النماذج داخل الدالة لتجنب التبعيات الدائرية
            from courses.models import CourseEnrollment
            from students.models import User
            
            student = User.objects.get(student_id=student_id, role='STUDENT')
            enrollment = CourseEnrollment.objects.filter(
                student=student,
                course_id=course_id,
                status='ENROLLED'
            ).first()
            
            return {
                'enrolled': bool(enrollment),
                'student': student,
                'enrollment': enrollment
            }
            
        except User.DoesNotExist:
            return {'enrolled': False, 'error': 'الطالب غير موجود'}
        except Exception as e:
            logger.error(f"خطأ في التحقق من التسجيل: {str(e)}")
            return {'enrolled': False, 'error': 'خطأ في التحقق'}
    
    def _verify_location(self, session_data: Dict, location_data: Dict = None) -> Dict:
        """التحقق من الموقع الجغرافي"""
        if not location_data or not session_data.get('location'):
            return {'valid': True}  # لا يوجد قيود موقع
        
        try:
            # تحليل بيانات الموقع المطلوبة
            required_location = json.loads(session_data['location'])
            if not required_location:
                return {'valid': True}
            
            # التحقق من المسافة
            student_lat = float(location_data.get('latitude', 0))
            student_lng = float(location_data.get('longitude', 0))
            session_lat = float(required_location.get('latitude', 0))
            session_lng = float(required_location.get('longitude', 0))
            
            distance = self._calculate_distance(
                student_lat, student_lng, session_lat, session_lng
            )
            
            max_distance = required_location.get('max_distance', 100)  # 100 متر افتراضي
            
            if distance > max_distance:
                return {
                    'valid': False,
                    'error': f'أنت خارج نطاق الحضور المسموح ({distance:.0f}م من الموقع المطلوب)',
                    'error_code': 'LOCATION_OUT_OF_RANGE',
                    'distance': distance,
                    'max_distance': max_distance
                }
            
            return {
                'valid': True,
                'distance': distance,
                'within_range': True
            }
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الموقع: {str(e)}")
            return {
                'valid': False,
                'error': 'خطأ في التحقق من الموقع',
                'error_code': 'LOCATION_ERROR'
            }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """حساب المسافة بين نقطتين جغرافيتين (بالأمتار)"""
        import math
        
        # تحويل إلى راديان
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # حساب الفروق
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        # صيغة Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # نصف قطر الأرض بالأمتار
        r = 6371000
        
        return c * r
    
    def _record_attendance(self, session_data: Dict, student_id: str) -> Dict:
        """تسجيل الحضور في قاعدة البيانات"""
        try:
            # استيراد النماذج
            from academic.models import AttendanceRecord
            from students.models import User
            
            student = User.objects.get(student_id=student_id, role='STUDENT')
            
            # إنشاء سجل الحضور
            attendance = AttendanceRecord.objects.create(
                student=student,
                session_id=session_data['session_id'],
                course_id=session_data['course_id'],
                attendance_date=session_data['session_date'],
                attendance_time=timezone.now().time(),
                status='PRESENT',
                verification_method='QR_CODE',
                qr_token=session_data['token'],
                metadata={
                    'qr_verification': True,
                    'verification_timestamp': timezone.now().isoformat()
                }
            )
            
            # وضع علامة في الكاش لمنع التسجيل المتكرر
            cache_key = f"attendance_{session_data['session_id']}_{student_id}"
            cache.set(cache_key, True, timeout=86400)  # 24 ساعة
            
            logger.info(f"تم تسجيل حضور الطالب {student_id} للجلسة {session_data['session_id']}")
            
            return {
                'recorded': True,
                'attendance_id': str(attendance.id),
                'timestamp': timezone.now().isoformat(),
                'student_name': student.display_name
            }
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الحضور: {str(e)}")
            raise

class AttendanceAnalytics:
    """تحليلات الحضور والغياب"""
    
    @staticmethod
    def get_course_attendance_stats(course_id: str, date_range: Tuple[str, str] = None) -> Dict:
        """إحصائيات حضور مقرر"""
        try:
            from academic.models import AttendanceRecord, CourseSession
            from django.db.models import Count, Q
            
            # تحديد نطاق التاريخ
            filters = {'course_id': course_id}
            if date_range:
                filters['attendance_date__range'] = date_range
            
            # إجمالي الجلسات
            total_sessions = CourseSession.objects.filter(course_id=course_id).count()
            
            # إحصائيات الحضور
            attendance_stats = AttendanceRecord.objects.filter(**filters).aggregate(
                total_records=Count('id'),
                present_count=Count('id', filter=Q(status='PRESENT')),
                absent_count=Count('id', filter=Q(status='ABSENT')),
                late_count=Count('id', filter=Q(status='LATE')),
                excused_count=Count('id', filter=Q(status='EXCUSED'))
            )
            
            # حساب النسب
            total = attendance_stats['total_records'] or 1
            attendance_rate = (attendance_stats['present_count'] / total) * 100
            
            return {
                'course_id': course_id,
                'total_sessions': total_sessions,
                'attendance_stats': attendance_stats,
                'attendance_rate': round(attendance_rate, 2),
                'analysis_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل حضور المقرر: {str(e)}")
            return {}
    
    @staticmethod
    def get_student_attendance_report(student_id: str, course_id: str = None) -> Dict:
        """تقرير حضور طالب"""
        try:
            from academic.models import AttendanceRecord
            from students.models import User
            from django.db.models import Count, Q
            
            student = User.objects.get(student_id=student_id, role='STUDENT')
            
            # تحديد المرشحات
            filters = {'student': student}
            if course_id:
                filters['course_id'] = course_id
            
            # إحصائيات الحضور
            attendance_data = AttendanceRecord.objects.filter(**filters).aggregate(
                total_sessions=Count('id'),
                present_sessions=Count('id', filter=Q(status='PRESENT')),
                absent_sessions=Count('id', filter=Q(status='ABSENT')),
                late_sessions=Count('id', filter=Q(status='LATE')),
                excused_sessions=Count('id', filter=Q(status='EXCUSED'))
            )
            
            # حساب النسب
            total = attendance_data['total_sessions'] or 1
            attendance_rate = (attendance_data['present_sessions'] / total) * 100
            
            # الحضور حسب الشهر
            monthly_attendance = self._get_monthly_attendance(student, course_id)
            
            return {
                'student_id': student_id,
                'student_name': student.display_name,
                'course_id': course_id,
                'attendance_stats': attendance_data,
                'attendance_rate': round(attendance_rate, 2),
                'monthly_breakdown': monthly_attendance,
                'report_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير حضور الطالب: {str(e)}")
            return {}
    
    @staticmethod
    def _get_monthly_attendance(student, course_id=None):
        """الحصول على حضور شهري"""
        try:
            from academic.models import AttendanceRecord
            from django.db.models import Count, Q
            from django.utils import timezone
            
            # آخر 6 أشهر
            six_months_ago = timezone.now().date() - datetime.timedelta(days=180)
            
            filters = {
                'student': student,
                'attendance_date__gte': six_months_ago
            }
            if course_id:
                filters['course_id'] = course_id
            
            monthly_data = AttendanceRecord.objects.filter(**filters).extra(
                select={'month': 'EXTRACT(month from attendance_date)'}
            ).values('month').annotate(
                total=Count('id'),
                present=Count('id', filter=Q(status='PRESENT'))
            ).order_by('month')
            
            return list(monthly_data)
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على البيانات الشهرية: {str(e)}")
            return []

# دوال مساعدة للاستخدام الخارجي

def generate_qr_for_session(session_id: str, course_id: str, teacher_id: str,
                           session_date: str, session_time: str, location: str = None) -> Dict:
    """إنشاء رمز QR لجلسة دراسية"""
    generator = SecureQRGenerator()
    
    session_data = {
        'session_id': session_id,
        'course_id': course_id,
        'teacher_id': teacher_id,
        'session_date': session_date,
        'session_time': session_time,
        'location': location or ''
    }
    
    return generator.generate_session_qr(session_data)

def verify_attendance_qr(qr_data: str, student_id: str, location_data: Dict = None) -> Dict:
    """التحقق من رمز QR وتسجيل الحضور"""
    verifier = AttendanceVerifier()
    return verifier.verify_and_record_attendance(qr_data, student_id, location_data)

def get_attendance_analytics(course_id: str = None, student_id: str = None) -> Dict:
    """الحصول على تحليلات الحضور"""
    analytics = AttendanceAnalytics()
    
    if course_id:
        return analytics.get_course_attendance_stats(course_id)
    elif student_id:
        return analytics.get_student_attendance_report(student_id)
    else:
        return {'error': 'يجب تحديد معرف المقرر أو الطالب'}

# نماذج إضافية للنظام

class QRAttendanceSession:
    """جلسة حضور QR"""
    
    def __init__(self, session_id: str, course_id: str, teacher_id: str):
        self.session_id = session_id
        self.course_id = course_id
        self.teacher_id = teacher_id
        self.created_at = timezone.now()
        self.qr_data = None
        self.attendance_count = 0
    
    def generate_qr(self, location: str = None) -> Dict:
        """إنشاء رمز QR للجلسة"""
        self.qr_data = generate_qr_for_session(
            self.session_id,
            self.course_id,
            self.teacher_id,
            self.created_at.date().isoformat(),
            self.created_at.time().isoformat(),
            location
        )
        return self.qr_data
    
    def record_attendance(self, student_id: str, location_data: Dict = None) -> Dict:
        """تسجيل حضور طالب"""
        if not self.qr_data:
            raise ValueError("لم يتم إنشاء رمز QR للجلسة")
        
        result = verify_attendance_qr(
            self.qr_data['encrypted_data'],
            student_id,
            location_data
        )
        
        if result.get('valid') and result.get('attendance_record'):
            self.attendance_count += 1
        
        return result
    
    def get_session_stats(self) -> Dict:
        """إحصائيات الجلسة"""
        return {
            'session_id': self.session_id,
            'course_id': self.course_id,
            'created_at': self.created_at.isoformat(),
            'attendance_count': self.attendance_count,
            'qr_generated': bool(self.qr_data),
            'expires_at': self.qr_data.get('expires_at') if self.qr_data else None
        }