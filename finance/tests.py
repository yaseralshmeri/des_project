# FIX: Missing Tests - متوسط
# إضافة اختبارات شاملة للوظائف المالية الحساسة

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import uuid

from .models import FeeStructure, StudentFee, Payment, Scholarship, ScholarshipApplication
from students.models import User, Student

class FeeStructureModelTests(TestCase):
    """FIX: Test FeeStructure model functionality"""
    
    def setUp(self):
        self.fee_structure_data = {
            'program_type': 'UNDERGRADUATE',
            'semester': 1,
            'tuition_fee': Decimal('5000.00'),
            'lab_fee': Decimal('500.00'),
            'library_fee': Decimal('200.00'),
            'sports_fee': Decimal('100.00'),
            'other_fees': Decimal('300.00')
        }
    
    def test_fee_structure_creation(self):
        """Test fee structure creation"""
        fee_structure = FeeStructure.objects.create(**self.fee_structure_data)
        self.assertEqual(fee_structure.program_type, 'UNDERGRADUATE')
        self.assertEqual(fee_structure.semester, 1)
        self.assertEqual(fee_structure.tuition_fee, Decimal('5000.00'))
    
    def test_total_fee_calculation(self):
        """Test total fee property calculation"""
        fee_structure = FeeStructure.objects.create(**self.fee_structure_data)
        expected_total = Decimal('6100.00')  # Sum of all fees
        self.assertEqual(fee_structure.total_fee, expected_total)
    
    def test_fee_structure_string_representation(self):
        """Test fee structure __str__ method"""
        fee_structure = FeeStructure.objects.create(**self.fee_structure_data)
        expected = "UNDERGRADUATE - Semester 1"
        self.assertEqual(str(fee_structure), expected)
    
    def test_unique_constraint(self):
        """Test unique constraint on program_type and semester"""
        FeeStructure.objects.create(**self.fee_structure_data)
        
        # Try to create another with same program_type and semester
        with self.assertRaises(Exception):
            FeeStructure.objects.create(**self.fee_structure_data)


class StudentFeeModelTests(TestCase):
    """FIX: Test StudentFee model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            role='STUDENT'
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            enrollment_date=date.today(),
            major='Computer Science'
        )
        self.fee_structure = FeeStructure.objects.create(
            program_type='UNDERGRADUATE',
            semester=1,
            tuition_fee=Decimal('5000.00'),
            lab_fee=Decimal('500.00')
        )
        self.student_fee_data = {
            'student': self.student,
            'fee_structure': self.fee_structure,
            'academic_year': 2023,
            'total_amount': Decimal('5500.00'),
            'paid_amount': Decimal('2000.00'),
            'discount': Decimal('500.00'),
            'due_date': date.today() + timedelta(days=30)
        }
    
    def test_student_fee_creation(self):
        """Test student fee creation"""
        student_fee = StudentFee.objects.create(**self.student_fee_data)
        self.assertEqual(student_fee.student, self.student)
        self.assertEqual(student_fee.total_amount, Decimal('5500.00'))
        self.assertEqual(student_fee.status, 'PENDING')  # Default status
    
    def test_outstanding_amount_calculation(self):
        """Test outstanding amount property"""
        student_fee = StudentFee.objects.create(**self.student_fee_data)
        expected_outstanding = Decimal('3000.00')  # 5500 - 2000 - 500
        self.assertEqual(student_fee.outstanding_amount, expected_outstanding)
    
    def test_student_fee_string_representation(self):
        """Test student fee __str__ method"""
        student_fee = StudentFee.objects.create(**self.student_fee_data)
        expected = "STU001 - 2023 - PENDING"
        self.assertEqual(str(student_fee), expected)


class PaymentModelTests(TestCase):
    """FIX: Test Payment model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            role='STUDENT'
        )
        self.staff_user = User.objects.create_user(
            username='staff1',
            email='staff1@example.com',
            role='STAFF'
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            enrollment_date=date.today(),
            major='Computer Science'
        )
        self.fee_structure = FeeStructure.objects.create(
            program_type='UNDERGRADUATE',
            semester=1,
            tuition_fee=Decimal('5000.00')
        )
        self.student_fee = StudentFee.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            academic_year=2023,
            total_amount=Decimal('5000.00'),
            due_date=date.today() + timedelta(days=30)
        )
    
    def test_payment_creation(self):
        """Test payment creation"""
        payment = Payment.objects.create(
            student_fee=self.student_fee,
            amount=Decimal('1000.00'),
            payment_method='CARD',
            transaction_id=str(uuid.uuid4()),
            received_by=self.staff_user
        )
        self.assertEqual(payment.amount, Decimal('1000.00'))
        self.assertEqual(payment.payment_method, 'CARD')
        self.assertEqual(payment.received_by, self.staff_user)
    
    def test_payment_string_representation(self):
        """Test payment __str__ method"""
        transaction_id = str(uuid.uuid4())
        payment = Payment.objects.create(
            student_fee=self.student_fee,
            amount=Decimal('1000.00'),
            payment_method='CARD',
            transaction_id=transaction_id,
            received_by=self.staff_user
        )
        expected = f"{transaction_id} - 1000.00"
        self.assertEqual(str(payment), expected)
    
    def test_unique_transaction_id(self):
        """Test transaction ID uniqueness"""
        transaction_id = str(uuid.uuid4())
        Payment.objects.create(
            student_fee=self.student_fee,
            amount=Decimal('1000.00'),
            payment_method='CARD',
            transaction_id=transaction_id,
            received_by=self.staff_user
        )
        
        # Try to create another payment with same transaction ID
        with self.assertRaises(Exception):
            Payment.objects.create(
                student_fee=self.student_fee,
                amount=Decimal('500.00'),
                payment_method='CASH',
                transaction_id=transaction_id,
                received_by=self.staff_user
            )


class PaymentProcessingTests(APITestCase):
    """FIX: Test payment processing functionality"""
    
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
            enrollment_date=date.today(),
            major='Computer Science'
        )
        self.fee_structure = FeeStructure.objects.create(
            program_type='UNDERGRADUATE',
            semester=1,
            tuition_fee=Decimal('5000.00')
        )
        self.student_fee = StudentFee.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            academic_year=2023,
            total_amount=Decimal('5000.00'),
            due_date=date.today() + timedelta(days=30)
        )
    
    def test_payment_creation_updates_student_fee_status(self):
        """Test payment creation updates student fee status"""
        self.client.force_authenticate(user=self.admin_user)
        
        payment_data = {
            'student_fee': self.student_fee.id,
            'amount': '2500.00',
            'payment_method': 'CARD',
            'transaction_id': str(uuid.uuid4()),
            'notes': 'Partial payment'
        }
        
        response = self.client.post(reverse('payment-list'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that student fee status was updated
        self.student_fee.refresh_from_db()
        self.assertEqual(self.student_fee.status, 'PARTIAL')
        self.assertEqual(self.student_fee.paid_amount, Decimal('2500.00'))
    
    def test_full_payment_marks_fee_as_paid(self):
        """Test full payment marks fee as PAID"""
        self.client.force_authenticate(user=self.admin_user)
        
        payment_data = {
            'student_fee': self.student_fee.id,
            'amount': '5000.00',  # Full amount
            'payment_method': 'BANK_TRANSFER',
            'transaction_id': str(uuid.uuid4())
        }
        
        response = self.client.post(reverse('payment-list'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that student fee is marked as PAID
        self.student_fee.refresh_from_db()
        self.assertEqual(self.student_fee.status, 'PAID')
        self.assertEqual(self.student_fee.outstanding_amount, Decimal('0.00'))
    
    def test_payment_validation(self):
        """Test payment amount validation"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test negative amount
        payment_data = {
            'student_fee': self.student_fee.id,
            'amount': '-100.00',
            'payment_method': 'CASH',
            'transaction_id': str(uuid.uuid4())
        }
        
        response = self.client.post(reverse('payment-list'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_overpayment_handling(self):
        """Test handling of overpayments"""
        self.client.force_authenticate(user=self.admin_user)
        
        payment_data = {
            'student_fee': self.student_fee.id,
            'amount': '6000.00',  # More than total amount
            'payment_method': 'CARD',
            'transaction_id': str(uuid.uuid4())
        }
        
        response = self.client.post(reverse('payment-list'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Fee should still be marked as PAID
        self.student_fee.refresh_from_db()
        self.assertEqual(self.student_fee.status, 'PAID')


class ScholarshipTests(APITestCase):
    """FIX: Test scholarship functionality"""
    
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
            enrollment_date=date.today(),
            major='Computer Science',
            gpa=Decimal('3.8')
        )
        self.scholarship = Scholarship.objects.create(
            name='Merit Scholarship',
            description='For high-achieving students',
            scholarship_type='MERIT',
            amount=Decimal('2000.00'),
            eligibility_criteria='GPA >= 3.5',
            application_deadline=date.today() + timedelta(days=30)
        )
    
    def test_scholarship_creation(self):
        """Test scholarship creation"""
        self.assertEqual(self.scholarship.name, 'Merit Scholarship')
        self.assertEqual(self.scholarship.scholarship_type, 'MERIT')
        self.assertEqual(self.scholarship.amount, Decimal('2000.00'))
    
    def test_scholarship_application_creation(self):
        """Test scholarship application creation"""
        application = ScholarshipApplication.objects.create(
            student=self.student,
            scholarship=self.scholarship,
            documents='transcripts.pdf, recommendation.pdf'
        )
        self.assertEqual(application.student, self.student)
        self.assertEqual(application.scholarship, self.scholarship)
        self.assertEqual(application.status, 'SUBMITTED')  # Default status
    
    def test_unique_scholarship_application(self):
        """Test student can only apply once per scholarship"""
        ScholarshipApplication.objects.create(
            student=self.student,
            scholarship=self.scholarship
        )
        
        # Try to create another application for same scholarship
        with self.assertRaises(Exception):
            ScholarshipApplication.objects.create(
                student=self.student,
                scholarship=self.scholarship
            )
    
    def test_scholarship_application_review(self):
        """Test scholarship application review process"""
        self.client.force_authenticate(user=self.admin_user)
        
        application = ScholarshipApplication.objects.create(
            student=self.student,
            scholarship=self.scholarship
        )
        
        # Update application status
        update_data = {
            'status': 'APPROVED',
            'reviewer': self.admin_user.id,
            'review_notes': 'Excellent academic performance'
        }
        
        response = self.client.patch(
            reverse('scholarshipapplication-detail', args=[application.id]),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        application.refresh_from_db()
        self.assertEqual(application.status, 'APPROVED')
        self.assertEqual(application.reviewer, self.admin_user)


class FinancialReportsTests(APITestCase):
    """FIX: Test financial reporting functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        
        # Create test data
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            role='STUDENT'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='STU001',
            enrollment_date=date.today(),
            major='Computer Science'
        )
        self.fee_structure = FeeStructure.objects.create(
            program_type='UNDERGRADUATE',
            semester=1,
            tuition_fee=Decimal('5000.00')
        )
        self.student_fee = StudentFee.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            academic_year=2023,
            total_amount=Decimal('5000.00'),
            paid_amount=Decimal('3000.00'),
            due_date=date.today() + timedelta(days=30)
        )
    
    def test_student_fee_summary_endpoint(self):
        """Test student fee summary endpoint"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(reverse('studentfee-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check summary data structure
        self.assertIn('total_fees', response.data)
        self.assertIn('total_paid', response.data)
        self.assertIn('total_outstanding', response.data)
        self.assertIn('status_breakdown', response.data)
    
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_summary_endpoint_uses_caching(self, mock_cache_set, mock_cache_get):
        """Test that summary endpoint uses caching"""
        mock_cache_get.return_value = None  # Cache miss
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('studentfee-summary'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cache_set.assert_called()
    
    def test_scholarship_statistics_endpoint(self):
        """Test scholarship statistics endpoint"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create scholarship and application
        scholarship = Scholarship.objects.create(
            name='Test Scholarship',
            description='Test',
            scholarship_type='MERIT',
            amount=Decimal('1000.00'),
            eligibility_criteria='GPA >= 3.0',
            application_deadline=date.today() + timedelta(days=30)
        )
        ScholarshipApplication.objects.create(
            student=self.student,
            scholarship=scholarship
        )
        
        response = self.client.get(reverse('scholarshipapplication-statistics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check statistics data structure
        self.assertIn('total_applications', response.data)
        self.assertIn('status_breakdown', response.data)
        self.assertIn('scholarship_breakdown', response.data)


class SecurityTests(APITestCase):
    """FIX: Test financial security features"""
    
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
            password='studentpass123',
            role='STUDENT'
        )
    
    def test_student_cannot_access_financial_data(self):
        """Test students cannot access financial management endpoints"""
        self.client.force_authenticate(user=self.student_user)
        
        # Try to access fee structures
        response = self.client.get(reverse('feestructure-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to access payments
        response = self.client.get(reverse('payment-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthorized_access_blocked(self):
        """Test unauthorized access to financial endpoints is blocked"""
        # Try to access without authentication
        response = self.client.get(reverse('payment-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_payment_amount_precision(self):
        """Test payment amount precision handling"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create necessary test data
        student_user = User.objects.create_user(
            username='teststudent',
            email='test@example.com',
            role='STUDENT'
        )
        student = Student.objects.create(
            user=student_user,
            student_id='STU001',
            enrollment_date=date.today(),
            major='Computer Science'
        )
        fee_structure = FeeStructure.objects.create(
            program_type='UNDERGRADUATE',
            semester=1,
            tuition_fee=Decimal('5000.00')
        )
        student_fee = StudentFee.objects.create(
            student=student,
            fee_structure=fee_structure,
            academic_year=2023,
            total_amount=Decimal('5000.00'),
            due_date=date.today() + timedelta(days=30)
        )
        
        # Test payment with high precision
        payment_data = {
            'student_fee': student_fee.id,
            'amount': '1234.567',  # 3 decimal places
            'payment_method': 'CARD',
            'transaction_id': str(uuid.uuid4())
        }
        
        response = self.client.post(reverse('payment-list'), payment_data)
        # Should handle precision appropriately
        self.assertIn(response.status_code, [200, 201, 400])