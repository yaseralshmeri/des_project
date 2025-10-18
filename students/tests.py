# FIX: Missing Tests - متوسط
# إضافة اختبارات شاملة للوظائف الحساسة في students app

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import json

from .models import User, Student, Department
from .serializers import UserSerializer, StudentSerializer

User = get_user_model()

class UserModelTests(TestCase):
    """FIX: Test User model functionality"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'STUDENT'
        }
    
    def test_user_creation(self):
        """Test basic user creation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'STUDENT')
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_admin)
    
    def test_user_role_properties(self):
        """Test user role property methods"""
        # Test admin user
        admin_user = User.objects.create_user(
            username='admin', email='admin@example.com', role='ADMIN'
        )
        self.assertTrue(admin_user.is_admin)
        self.assertFalse(admin_user.is_student)
        
        # Test staff user
        staff_user = User.objects.create_user(
            username='staff', email='staff@example.com', role='STAFF'
        )
        self.assertTrue(staff_user.is_staff_member)
        self.assertFalse(staff_user.is_teacher)
    
    def test_user_string_representation(self):
        """Test user __str__ method"""
        user = User.objects.create_user(**self.user_data)
        expected = f"Test User (STUDENT)"
        self.assertEqual(str(user), expected)


class StudentModelTests(TestCase):
    """FIX: Test Student model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            role='STUDENT'
        )
        self.student_data = {
            'user': self.user,
            'student_id': 'STU001',
            'enrollment_date': '2023-09-01',
            'major': 'Computer Science',
            'current_semester': 1,
            'gpa': 3.5
        }
    
    def test_student_creation(self):
        """Test student profile creation"""
        student = Student.objects.create(**self.student_data)
        self.assertEqual(student.student_id, 'STU001')
        self.assertEqual(student.major, 'Computer Science')
        self.assertEqual(float(student.gpa), 3.5)
    
    def test_student_string_representation(self):
        """Test student __str__ method"""
        student = Student.objects.create(**self.student_data)
        expected = f"STU001 - {self.user.get_full_name()}"
        self.assertEqual(str(student), expected)
    
    def test_student_gpa_validation(self):
        """Test GPA validation"""
        # Test valid GPA
        student = Student.objects.create(**self.student_data)
        student.gpa = 4.0
        student.full_clean()  # Should not raise validation error
        
        # Test invalid GPA (will be handled by model field validators)
        student.gpa = 5.0
        with self.assertRaises(Exception):
            student.full_clean()


class UserAuthenticationTests(APITestCase):
    """FIX: Test authentication functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='STUDENT'
        )
        self.login_url = reverse('user-login')
    
    def test_successful_login(self):
        """Test successful user login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_invalid_credentials_login(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_missing_credentials_login(self):
        """Test login with missing credentials"""
        data = {'username': 'testuser'}  # Missing password
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_inactive_user_login(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserPermissionTests(APITestCase):
    """FIX: Test user permission system"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            role='STAFF'
        )
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            role='STUDENT'
        )
    
    def test_admin_can_create_admin_user(self):
        """Test admin can create admin/staff users"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'newadminpass123',
            'role': 'ADMIN',
            'first_name': 'New',
            'last_name': 'Admin'
        }
        
        response = self.client.post(reverse('user-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_student_cannot_create_admin_user(self):
        """Test student cannot create admin users"""
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'newadminpass123',
            'role': 'ADMIN',
            'first_name': 'New',
            'last_name': 'Admin'
        }
        
        response = self.client.post(reverse('user-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_access_own_profile(self):
        """Test user can access their own profile"""
        self.client.force_authenticate(user=self.student_user)
        
        response = self.client.get(reverse('user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'student')


class StudentViewSetTests(APITestCase):
    """FIX: Test StudentViewSet functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            role='STUDENT'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='STU001',
            enrollment_date='2023-09-01',
            major='Computer Science',
            gpa=3.5
        )
    
    def test_admin_can_list_students(self):
        """Test admin can list all students"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(reverse('student-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_admin_can_create_student(self):
        """Test admin can create student"""
        self.client.force_authenticate(user=self.admin_user)
        
        new_user = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            role='STUDENT'
        )
        
        data = {
            'user': new_user.id,
            'student_id': 'STU002',
            'enrollment_date': '2023-09-01',
            'major': 'Mathematics',
            'gpa': 3.0
        }
        
        response = self.client.post(reverse('student-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_student_search_functionality(self):
        """Test student search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(reverse('student-list'), {'search': 'STU001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(reverse('student-list'), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class DepartmentTests(APITestCase):
    """FIX: Test Department functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            role='TEACHER'
        )
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Computer Science Department',
            head_of_department=self.teacher_user
        )
    
    def test_department_creation(self):
        """Test department creation"""
        self.assertEqual(self.department.name, 'Computer Science')
        self.assertEqual(self.department.code, 'CS')
        self.assertEqual(self.department.head_of_department, self.teacher_user)
    
    def test_department_string_representation(self):
        """Test department __str__ method"""
        expected = "CS - Computer Science"
        self.assertEqual(str(self.department), expected)
    
    def test_admin_can_list_departments(self):
        """Test admin can list departments"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(reverse('department-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class PerformanceTests(APITestCase):
    """FIX: Test performance optimizations"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        
        # Create multiple students for performance testing
        for i in range(10):
            user = User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@example.com',
                role='STUDENT'
            )
            Student.objects.create(
                user=user,
                student_id=f'STU{i:03d}',
                enrollment_date='2023-09-01',
                major='Computer Science',
                gpa=3.0 + (i * 0.1)
            )
    
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_caching_in_user_profile(self, mock_cache_set, mock_cache_get):
        """Test caching is used in user profile endpoint"""
        mock_cache_get.return_value = None  # Cache miss
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('user-me'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cache_set.assert_called()
    
    def test_student_list_query_count(self):
        """Test that student list doesn't cause N+1 queries"""
        self.client.force_authenticate(user=self.admin_user)
        
        with self.assertNumQueries(3):  # Should be optimized with select_related
            response = self.client.get(reverse('student-list'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class SecurityTests(APITestCase):
    """FIX: Test security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='STUDENT'
        )
    
    def test_password_not_returned_in_api(self):
        """Test password is not returned in API responses"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(reverse('user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', response.data)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        self.client.force_authenticate(user=self.user)
        
        # Try SQL injection in search parameter
        malicious_query = "'; DROP TABLE users; --"
        response = self.client.get(reverse('student-list'), {'search': malicious_query})
        
        # Should not cause server error
        self.assertIn(response.status_code, [200, 400])
    
    def test_unauthorized_access_blocked(self):
        """Test unauthorized access is blocked"""
        # Try to access student list without authentication
        response = self.client.get(reverse('student-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)