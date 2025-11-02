"""
Views لنظام المراقبة
Monitoring System Views

تم تطويره في: 2025-11-02
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from .performance_monitor import monitor
from .error_handler import error_tracker


class SystemHealthView(APIView):
    """API لفحص صحة النظام"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """الحصول على حالة النظام"""
        try:
            health_status = monitor.get_health_status()
            return Response(health_status, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'فشل في الحصول على حالة النظام',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerformanceMetricsView(APIView):
    """API لمقاييس الأداء"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """الحصول على مقاييس الأداء"""
        hours = int(request.GET.get('hours', 1))
        
        try:
            metrics = monitor.get_metrics_summary(hours)
            db_stats = monitor.get_database_stats()
            
            return Response({
                'performance_metrics': metrics,
                'database_stats': db_stats,
                'period_hours': hours
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'فشل في الحصول على مقاييس الأداء',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ErrorStatisticsView(APIView):
    """API لإحصائيات الأخطاء"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """الحصول على إحصائيات الأخطاء"""
        hours = int(request.GET.get('hours', 24))
        
        try:
            error_stats = error_tracker.get_error_statistics(hours)
            return Response(error_stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'فشل في الحصول على إحصائيات الأخطاء', 
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerformanceReportView(APIView):
    """API لتقارير الأداء"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """إنشاء تقرير أداء شامل"""
        hours = int(request.GET.get('hours', 24))
        
        try:
            report = monitor.generate_report(hours)
            return Response(report, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'فشل في إنشاء تقرير الأداء',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(staff_member_required, name='dispatch')
class MonitoringDashboardView(TemplateView):
    """لوحة تحكم المراقبة"""
    
    template_name = 'monitoring/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # بيانات النظام
            context['health_status'] = monitor.get_health_status()
            context['metrics_summary'] = monitor.get_metrics_summary()
            context['error_stats'] = error_tracker.get_error_statistics()
            context['db_stats'] = monitor.get_database_stats()
            
        except Exception as e:
            context['error'] = f"فشل في تحميل بيانات المراقبة: {e}"
        
        return context


@require_http_methods(["GET"])
@cache_page(60)  # كاش لمدة دقيقة
def quick_health_check(request):
    """فحص سريع لحالة النظام (للمراقبة الخارجية)"""
    try:
        # فحص قاعدة البيانات
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # فحص الكاش
        from django.core.cache import cache
        cache.set('health_check', 'ok', timeout=10)
        cache_test = cache.get('health_check')
        
        health_data = {
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_test == 'ok' else 'error',
            'timestamp': monitor.get_health_status()['last_check'].isoformat()
        }
        
        return JsonResponse(health_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': monitor.get_health_status()['last_check'].isoformat()
        }, status=500)


@staff_member_required
def system_metrics_json(request):
    """إرجاع مقاييس النظام بصيغة JSON (لـ AJAX)"""
    try:
        hours = int(request.GET.get('hours', 1))
        
        data = {
            'metrics': monitor.get_metrics_summary(hours),
            'health': monitor.get_health_status(),
            'errors': error_tracker.get_error_statistics(hours),
            'database': monitor.get_database_stats()
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'error': 'فشل في الحصول على البيانات',
            'detail': str(e)
        }, status=500)


@staff_member_required  
def clear_error_logs(request):
    """مسح سجلات الأخطاء"""
    if request.method == 'POST':
        try:
            # مسح الأخطاء من الذاكرة
            error_tracker.error_details.clear()
            error_tracker.error_counts.clear()
            
            return JsonResponse({
                'success': True,
                'message': 'تم مسح سجلات الأخطاء بنجاح'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'فشل في مسح السجلات: {e}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'طريقة الطلب غير مدعومة'
    }, status=405)