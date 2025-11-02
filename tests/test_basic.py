"""
اختبارات أساسية للمشروع
Basic project tests
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class BasicSystemTests(TestCase):
    """اختبارات النظام الأساسية"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """اختبار إنشاء المستخدم"""
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_admin_access(self):
        """اختبار الوصول للوحة الإدارة"""
        response = self.client.get('/admin/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    @pytest.mark.django_db
    def test_database_connection(self):
        """اختبار الاتصال بقاعدة البيانات"""
        from django.db import connection
        self.assertTrue(connection.is_usable())
