# نظام الحضور بـ QR - المسلسلات
# QR Attendance System - Serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    QRCode, AttendanceSession, AttendanceRecord, 
    AttendanceReport, QRScanLog
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """مسلسل المستخدم الأساسي"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class QRCodeSerializer(serializers.ModelSerializer):
    """مسلسل رموز QR"""
    
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    qr_image_url = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    time_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = QRCode
        fields = '__all__'
        read_only_fields = ['id', 'code_id', 'qr_image', 'scan_count', 'last_scanned_at', 'created_at', 'updated_at']
    
    def get_qr_image_url(self, obj):
        """الحصول على رابط صورة QR"""
        if obj.qr_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_image.url)
            return obj.qr_image.url
        return None


class AttendanceSessionSerializer(serializers.ModelSerializer):
    """مسلسل جلسات الحضور"""
    
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.user.get_full_name', read_only=True)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    qr_codes = QRCodeSerializer(many=True, read_only=True)
    total_attendees = serializers.ReadOnlyField()
    attendance_percentage = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    
    class Meta:
        model = AttendanceSession
        fields = '__all__'
        read_only_fields = ['id', 'session_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """التحقق من صحة البيانات"""
        if data.get('start_time') and data.get('end_time'):
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("وقت الانتهاء يجب أن يكون بعد وقت البداية")
        return data


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """مسلسل سجلات الحضور"""
    
    student = UserBasicSerializer(source='student.user', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    course_name = serializers.CharField(source='session.course.course_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    verification_method_display = serializers.CharField(source='get_verification_method_display', read_only=True)
    qr_code_id = serializers.CharField(source='qr_code_used.code_id', read_only=True)
    is_late = serializers.ReadOnlyField()
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceRecordCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء سجل حضور (مبسط)"""
    
    qr_code_data = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'session', 'status', 'qr_code_data', 'notes']
    
    def create(self, validated_data):
        qr_code_data = validated_data.pop('qr_code_data', None)
        
        # إذا تم توفير بيانات QR، البحث عن الرمز المناسب
        if qr_code_data:
            try:
                qr_code = QRCode.objects.get(qr_data=qr_code_data, is_active=True)
                if not qr_code.is_expired:
                    validated_data['qr_code_used'] = qr_code
                    validated_data['verification_method'] = 'QR_CODE'
                    # تحديث عداد المسح
                    qr_code.scan_count += 1
                    qr_code.last_scanned_at = timezone.now()
                    qr_code.save()
                else:
                    raise serializers.ValidationError("رمز QR منتهي الصلاحية")
            except QRCode.DoesNotExist:
                raise serializers.ValidationError("رمز QR غير صحيح")
        
        # تعيين وقت الحضور
        validated_data['check_in_time'] = timezone.now()
        
        return super().create(validated_data)


class AttendanceReportSerializer(serializers.ModelSerializer):
    """مسلسل تقارير الحضور"""
    
    generated_by = UserBasicSerializer(read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = AttendanceReport
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['generated_by'] = request.user
        return super().create(validated_data)


class QRScanLogSerializer(serializers.ModelSerializer):
    """مسلسل سجلات مسح QR"""
    
    qr_code_id = serializers.CharField(source='qr_code.code_id', read_only=True)
    scanned_by = UserBasicSerializer(read_only=True)
    scan_result_display = serializers.CharField(source='get_scan_result_display', read_only=True)
    
    class Meta:
        model = QRScanLog
        fields = '__all__'
        read_only_fields = ['id', 'scanned_at']


# مسلسلات للإحصائيات والتقارير المتقدمة
class AttendanceStatisticsSerializer(serializers.Serializer):
    """مسلسل إحصائيات الحضور"""
    
    total_sessions = serializers.IntegerField()
    total_students = serializers.IntegerField()
    average_attendance = serializers.FloatField()
    attendance_by_course = serializers.DictField()
    attendance_by_date = serializers.DictField()
    late_arrivals = serializers.IntegerField()
    absent_students = serializers.IntegerField()


class StudentAttendanceReportSerializer(serializers.Serializer):
    """مسلسل تقرير حضور الطالب"""
    
    student = UserBasicSerializer()
    total_sessions = serializers.IntegerField()
    attended_sessions = serializers.IntegerField()
    absent_sessions = serializers.IntegerField()
    late_sessions = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
    last_attendance = serializers.DateTimeField()


class CourseAttendanceReportSerializer(serializers.Serializer):
    """مسلسل تقرير حضور المقرر"""
    
    course_name = serializers.CharField()
    total_sessions = serializers.IntegerField()
    total_students = serializers.IntegerField()
    average_attendance = serializers.FloatField()
    best_attended_session = serializers.CharField()
    worst_attended_session = serializers.CharField()
    attendance_trend = serializers.ListField()


class QRCodeCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء رمز QR (مبسط)"""
    
    class Meta:
        model = QRCode
        fields = ['session', 'expires_at', 'scan_limit']
    
    def create(self, validated_data):
        # سيتم توليد code_id و qr_data تلقائياً في النموذج
        return super().create(validated_data)


class AttendanceSessionCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء جلسة حضور (مبسط)"""
    
    generate_qr = serializers.BooleanField(write_only=True, default=False)
    qr_expires_minutes = serializers.IntegerField(write_only=True, default=60)
    
    class Meta:
        model = AttendanceSession
        fields = [
            'session_name', 'description', 'course', 'instructor',
            'session_type', 'start_time', 'end_time', 'location',
            'room_number', 'building', 'allow_late_entry',
            'late_entry_minutes', 'generate_qr', 'qr_expires_minutes'
        ]
    
    def create(self, validated_data):
        generate_qr = validated_data.pop('generate_qr', False)
        qr_expires_minutes = validated_data.pop('qr_expires_minutes', 60)
        
        session = super().create(validated_data)
        
        # إنشاء رمز QR تلقائياً إذا طُلب ذلك
        if generate_qr:
            from datetime import timedelta
            expires_at = timezone.now() + timedelta(minutes=qr_expires_minutes)
            QRCode.objects.create(
                session=session,
                expires_at=expires_at,
                is_active=True
            )
        
        return session


# مسلسلات للبحث والتصفية
class AttendanceFilterSerializer(serializers.Serializer):
    """مسلسل تصفية سجلات الحضور"""
    
    course = serializers.CharField(required=False)
    instructor = serializers.CharField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=AttendanceRecord.STATUS_CHOICES, required=False)
    verification_method = serializers.ChoiceField(choices=AttendanceRecord.VERIFICATION_METHODS, required=False)


class QRScanSerializer(serializers.Serializer):
    """مسلسل مسح رمز QR"""
    
    qr_data = serializers.CharField()
    location_data = serializers.JSONField(required=False)
    
    def validate_qr_data(self, value):
        """التحقق من صحة بيانات QR"""
        try:
            qr_code = QRCode.objects.get(qr_data=value, is_active=True)
            if qr_code.is_expired:
                raise serializers.ValidationError("رمز QR منتهي الصلاحية")
            if qr_code.scan_limit and qr_code.scan_count >= qr_code.scan_limit:
                raise serializers.ValidationError("تم الوصول للحد الأقصى لعدد المسحات")
        except QRCode.DoesNotExist:
            raise serializers.ValidationError("رمز QR غير صحيح أو غير نشط")
        
        return value