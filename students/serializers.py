from rest_framework import serializers
from .models import User, Student, Department

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                 'phone', 'address', 'date_of_birth', 'profile_picture', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users with password.
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 
                 'phone', 'address', 'date_of_birth']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'STUDENT'),
            phone=validated_data.get('phone'),
            address=validated_data.get('address'),
            date_of_birth=validated_data.get('date_of_birth')
        )
        return user


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Student model.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True
    )
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'user_id', 'student_id', 'enrollment_date', 'major', 
                 'current_semester', 'gpa', 'status', 'guardian_name', 'guardian_phone', 
                 'emergency_contact', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model.
    """
    head_of_department = UserSerializer(read_only=True)
    head_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='head_of_department', 
        write_only=True, 
        required=False, 
        allow_null=True
    )
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'head_of_department', 'head_id', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
