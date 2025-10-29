from rest_framework import serializers
from .models import FeeStructure, StudentFee, Payment, Scholarship, ScholarshipApplication
from students.models import User, Student
from students.serializers import UserSerializer, StudentSerializer

class FeeStructureSerializer(serializers.ModelSerializer):
    """
    Serializer for the FeeStructure model.
    """
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'program_type', 'semester', 'tuition_fee', 'lab_fee', 
                 'library_fee', 'sports_fee', 'other_fees', 'total_fee', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentFeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the StudentFee model.
    """
    student_details = StudentSerializer(source='student', read_only=True)
    fee_structure_details = FeeStructureSerializer(source='fee_structure', read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    fee_structure = serializers.PrimaryKeyRelatedField(queryset=FeeStructure.objects.all())
    
    class Meta:
        model = StudentFee
        fields = ['id', 'student', 'student_details', 'fee_structure', 'fee_structure_details', 
                 'academic_year', 'total_amount', 'paid_amount', 'discount', 'status', 'due_date', 
                 'outstanding_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model.
    """
    received_by_details = UserSerializer(source='received_by', read_only=True)
    received_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'student_fee', 'amount', 'payment_method', 'transaction_id', 
                 'payment_date', 'received_by', 'received_by_details', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'payment_date', 'created_at', 'updated_at']


class ScholarshipSerializer(serializers.ModelSerializer):
    """
    Serializer for the Scholarship model.
    """
    class Meta:
        model = Scholarship
        fields = ['id', 'name', 'description', 'scholarship_type', 'amount', 
                 'eligibility_criteria', 'application_deadline', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the ScholarshipApplication model.
    """
    student_details = StudentSerializer(source='student', read_only=True)
    scholarship_details = ScholarshipSerializer(source='scholarship', read_only=True)
    reviewer_details = UserSerializer(source='reviewer', read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    scholarship = serializers.PrimaryKeyRelatedField(queryset=Scholarship.objects.all())
    reviewer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = ScholarshipApplication
        fields = ['id', 'student', 'student_details', 'scholarship', 'scholarship_details', 
                 'submitted_date', 'status', 'documents', 'reviewer', 'reviewer_details', 
                 'review_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'submitted_date', 'created_at', 'updated_at']
