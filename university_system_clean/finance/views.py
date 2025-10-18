# FIX: Performance Issues - عالي
# إصلاح مشاكل N+1 queries وإضافة select_related/prefetch_related وcaching

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Sum, Q, Prefetch
import logging

from .models import FeeStructure, StudentFee, Payment, Scholarship, ScholarshipApplication
from .serializers import (FeeStructureSerializer, StudentFeeSerializer, PaymentSerializer,
                          ScholarshipSerializer, ScholarshipApplicationSerializer)
from students.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)

class FeeStructureViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization with caching and query optimization
    """
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAdminOrStaff]
    queryset = FeeStructure.objects.order_by('program_type', 'semester')
    
    def get_queryset(self):
        """FIX: Add ordering for consistent results"""
        return self.queryset
    
    @method_decorator(cache_page(3600))  # Cache for 1 hour
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view"""
        return super().list(request, *args, **kwargs)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            fee_structure = serializer.save()
            logger.info(f"Fee structure created: {fee_structure.program_type} - Semester {fee_structure.semester}")
            # Clear cache
            cache.delete('fee_structures_list')
        except Exception as e:
            logger.error(f"Failed to create fee structure: {str(e)}")
            raise

class StudentFeeViewSet(viewsets.ModelViewSet):
    """
    FIX: Major performance improvements with optimized queries
    """
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['status', 'academic_year', 'student']
    queryset = StudentFee.objects.select_related(
        'student',  # Join with Student
        'student__user',  # Join with User through Student
        'fee_structure'  # Join with FeeStructure
    ).prefetch_related(
        Prefetch(
            'payments',
            queryset=Payment.objects.select_related('received_by').order_by('-payment_date')
        )
    ).order_by('-academic_year', '-due_date')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related and prefetch_related to avoid N+1 queries"""
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        FIX: Add optimized summary endpoint with proper aggregation
        """
        cache_key = f"student_fee_summary_{request.GET.get('academic_year', 'all')}"
        summary = cache.get(cache_key)
        
        if not summary:
            queryset = self.get_queryset()
            
            # Filter by academic year if provided
            academic_year = request.GET.get('academic_year')
            if academic_year:
                queryset = queryset.filter(academic_year=academic_year)
            
            # FIX: Use aggregation instead of Python loops for better performance
            summary = queryset.aggregate(
                total_fees=Sum('total_amount'),
                total_paid=Sum('paid_amount'),
                total_discount=Sum('discount')
            )
            
            # Calculate outstanding
            summary['total_outstanding'] = (
                (summary['total_fees'] or 0) - 
                (summary['total_paid'] or 0) - 
                (summary['total_discount'] or 0)
            )
            
            # Status breakdown
            status_breakdown = {}
            for status_choice in StudentFee.STATUS_CHOICES:
                status_code = status_choice[0]
                count = queryset.filter(status=status_code).count()
                status_breakdown[status_code] = count
            
            summary['status_breakdown'] = status_breakdown
            
            cache.set(cache_key, summary, 1800)  # Cache for 30 minutes
        
        return Response(summary)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            student_fee = serializer.save()
            logger.info(f"Student fee created: {student_fee.student.student_id} - {student_fee.academic_year}")
        except Exception as e:
            logger.error(f"Failed to create student fee: {str(e)}")
            raise

class PaymentViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for payment operations
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['payment_method', 'student_fee', 'payment_date']
    queryset = Payment.objects.select_related(
        'student_fee',  # Join with StudentFee
        'student_fee__student',  # Join with Student
        'student_fee__student__user',  # Join with User
        'received_by'  # Join with User who received payment
    ).order_by('-payment_date')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related to avoid N+1 queries"""
        return self.queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        """
        FIX: Enhanced payment creation with automatic fee status update
        """
        try:
            payment = serializer.save(received_by=self.request.user)
            student_fee = payment.student_fee
            
            # Update student fee status based on payment
            self._update_student_fee_status(student_fee)
            
            logger.info(f"Payment created: {payment.transaction_id} for {student_fee.student.student_id}")
        except Exception as e:
            logger.error(f"Failed to create payment: {str(e)}")
            raise
    
    def _update_student_fee_status(self, student_fee):
        """
        FIX: Helper method to update student fee status after payment
        """
        outstanding = student_fee.outstanding_amount
        
        if outstanding <= 0:
            student_fee.status = 'PAID'
        elif student_fee.paid_amount > 0:
            student_fee.status = 'PARTIAL'
        else:
            student_fee.status = 'PENDING'
        
        student_fee.save()

class ScholarshipViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization with caching
    """
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['scholarship_type']
    queryset = Scholarship.objects.prefetch_related(
        'applications',
        'applications__student',
        'applications__student__user'
    ).order_by('name')
    
    def get_queryset(self):
        """FIX: Add prefetch for applications"""
        return self.queryset
    
    @method_decorator(cache_page(1800))  # Cache for 30 minutes
    def list(self, request, *args, **kwargs):
        """FIX: Add caching to list view"""
        return super().list(request, *args, **kwargs)

class ScholarshipApplicationViewSet(viewsets.ModelViewSet):
    """
    FIX: Performance optimization for scholarship applications
    """
    serializer_class = ScholarshipApplicationSerializer
    permission_classes = [IsAdminOrStaff]
    filterset_fields = ['status', 'scholarship', 'student']
    queryset = ScholarshipApplication.objects.select_related(
        'student',  # Join with Student
        'student__user',  # Join with User
        'scholarship',  # Join with Scholarship
        'reviewer'  # Join with reviewer User
    ).order_by('-application_date')
    
    def get_queryset(self):
        """FIX: Performance - Add select_related to avoid N+1 queries"""
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        FIX: Add optimized statistics endpoint
        """
        cache_key = "scholarship_statistics"
        stats = cache.get(cache_key)
        
        if not stats:
            queryset = self.get_queryset()
            
            # FIX: Use aggregation for better performance
            stats = {
                'total_applications': queryset.count(),
                'status_breakdown': {},
                'scholarship_breakdown': {}
            }
            
            # Status breakdown
            for status_choice in ScholarshipApplication.STATUS_CHOICES:
                status_code = status_choice[0]
                count = queryset.filter(status=status_code).count()
                stats['status_breakdown'][status_code] = count
            
            # Scholarship breakdown (top 10)
            scholarship_stats = queryset.values(
                'scholarship__name'
            ).annotate(
                application_count=models.Count('id')
            ).order_by('-application_count')[:10]
            
            stats['scholarship_breakdown'] = list(scholarship_stats)
            
            cache.set(cache_key, stats, 1800)  # Cache for 30 minutes
        
        return Response(stats)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """FIX: Add transaction for data consistency"""
        try:
            application = serializer.save()
            logger.info(f"Scholarship application created: {application.student.student_id} - {application.scholarship.name}")
        except Exception as e:
            logger.error(f"Failed to create scholarship application: {str(e)}")
            raise
    
    @transaction.atomic
    def perform_update(self, serializer):
        """FIX: Add transaction and logging for status changes"""
        try:
            application = serializer.save()
            if 'status' in serializer.validated_data:
                logger.info(f"Scholarship application status updated: {application.student.student_id} - {application.status}")
        except Exception as e:
            logger.error(f"Failed to update scholarship application: {str(e)}")
            raise