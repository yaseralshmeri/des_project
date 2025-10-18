from rest_framework import serializers
from .models import Employee, Teacher, EmployeeAttendance, Leave, Salary
from students.models import User
from students.serializers import UserSerializer

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Employee model.
    """
    user_details = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_details', 'employee_id', 'department', 'position', 
                 'employment_type', 'hire_date', 'salary', 'status', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Teacher model.
    """
    employee_details = EmployeeSerializer(source='employee', read_only=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    
    class Meta:
        model = Teacher
        fields = ['id', 'employee', 'employee_details', 'academic_rank', 'specialization', 'qualifications', 
                 'research_interests', 'publications', 'office_hours', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the EmployeeAttendance model.
    """
    class Meta:
        model = EmployeeAttendance
        fields = ['id', 'employee', 'date', 'status', 'check_in_time', 
                 'check_out_time', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']



class LeaveSerializer(serializers.ModelSerializer):
    """
    Serializer for the Leave model.
    """
    approved_by_details = UserSerializer(source='approved_by', read_only=True)
    approved_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Leave
        fields = ['id', 'employee', 'leave_type', 'start_date', 'end_date', 
                 'reason', 'status', 'approved_by', 'approved_by_details', 'approval_notes', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalarySerializer(serializers.ModelSerializer):
    """
    Serializer for the Salary model.
    """
    net_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Salary
        fields = ['id', 'employee', 'month', 'year', 'basic_salary', 'allowances', 
                 'deductions', 'bonus', 'payment_date', 'net_salary', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
