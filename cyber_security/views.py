# واجهات الأمان السيبراني
# Cyber Security Views

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone

import json
from datetime import datetime, timedelta
from typing import Dict, List

from .models import (
    SecurityEvent, ThreatIntelligence, SecurityRule, SecurityIncident,
    UserBehaviorProfile, SecurityAuditLog, VulnerabilityAssessment, SecurityConfiguration
)
from .security_engine import threat_detector, behavior_analyzer

def is_security_admin(user):
    """فحص ما إذا كان المستخدم مدير أمان"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Security Admins').exists())

class SecurityDashboardView(APIView):
    """لوحة تحكم الأمان السيبراني"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """جلب إحصائيات لوحة تحكم الأمان"""
        
        try:
            # فحص صلاحيات الأمان
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول للوصول لبيانات الأمان'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # الإحصائيات العامة
            total_events = SecurityEvent.objects.count()
            recent_events = SecurityEvent.objects.filter(
                detected_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            critical_events = SecurityEvent.objects.filter(
                threat_level='critical',
                detected_at__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            unresolved_incidents = SecurityIncident.objects.filter(
                status__in=['open', 'investigating']
            ).count()
            
            # إحصائيات التهديدات حسب النوع
            threat_stats = SecurityEvent.objects.filter(
                detected_at__gte=timezone.now() - timedelta(days=30)
            ).values('event_type').annotate(count=Count('id')).order_by('-count')[:10]
            
            # إحصائيات المستويات
            severity_stats = SecurityEvent.objects.filter(
                detected_at__gte=timezone.now() - timedelta(days=30)
            ).values('threat_level').annotate(count=Count('id'))
            
            # أحدث الأحداث الحرجة
            recent_critical = SecurityEvent.objects.filter(
                threat_level__in=['critical', 'high'],
                detected_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-detected_at')[:5]
            
            recent_critical_data = []
            for event in recent_critical:
                recent_critical_data.append({
                    'id': event.id,
                    'title': event.title,
                    'threat_level': event.threat_level,
                    'event_type': event.event_type,
                    'ip_address': event.ip_address,
                    'detected_at': event.detected_at.isoformat(),
                    'is_resolved': event.is_resolved
                })
            
            # Top IPs مشبوهة
            suspicious_ips = SecurityEvent.objects.filter(
                detected_at__gte=timezone.now() - timedelta(days=7)
            ).values('ip_address').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            return Response({
                'success': True,
                'dashboard_stats': {
                    'total_events': total_events,
                    'recent_events': recent_events,
                    'critical_events': critical_events,
                    'unresolved_incidents': unresolved_incidents,
                    'threat_stats': list(threat_stats),
                    'severity_stats': list(severity_stats),
                    'recent_critical_events': recent_critical_data,
                    'suspicious_ips': list(suspicious_ips)
                },
                'last_updated': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في جلب بيانات لوحة التحكم: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SecurityEventsView(APIView):
    """واجهة إدارة الأحداث الأمنية"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """جلب قائمة الأحداث الأمنية"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول للوصول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # معاملات التصفية
            threat_level = request.GET.get('threat_level')
            event_type = request.GET.get('event_type')
            ip_address = request.GET.get('ip_address')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            resolved = request.GET.get('resolved')
            
            # بناء الاستعلام
            queryset = SecurityEvent.objects.all()
            
            if threat_level:
                queryset = queryset.filter(threat_level=threat_level)
            
            if event_type:
                queryset = queryset.filter(event_type=event_type)
            
            if ip_address:
                queryset = queryset.filter(ip_address__icontains=ip_address)
            
            if date_from:
                queryset = queryset.filter(detected_at__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(detected_at__lte=date_to)
            
            if resolved is not None:
                is_resolved = resolved.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(is_resolved=is_resolved)
            
            # ترتيب النتائج
            queryset = queryset.order_by('-detected_at')
            
            # تقسيم الصفحات
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 20))
            
            paginator = Paginator(queryset, per_page)
            events_page = paginator.get_page(page)
            
            # تحضير البيانات
            events_data = []
            for event in events_page:
                events_data.append({
                    'id': event.id,
                    'event_type': event.event_type,
                    'threat_level': event.threat_level,
                    'title': event.title,
                    'description': event.description,
                    'ip_address': event.ip_address,
                    'user_agent': event.user_agent,
                    'request_path': event.request_path,
                    'affected_user': event.affected_user.username if event.affected_user else None,
                    'is_investigated': event.is_investigated,
                    'is_resolved': event.is_resolved,
                    'detected_at': event.detected_at.isoformat(),
                    'resolved_at': event.resolved_at.isoformat() if event.resolved_at else None
                })
            
            return Response({
                'success': True,
                'events': events_data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': events_page.has_next(),
                    'has_previous': events_page.has_previous()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في جلب الأحداث: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, event_id):
        """تحديث حالة حدث أمني"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            event = get_object_or_404(SecurityEvent, id=event_id)
            
            # تحديث الحقول المسموحة
            if 'is_investigated' in request.data:
                event.is_investigated = request.data['is_investigated']
                if event.is_investigated and not event.investigated_at:
                    event.investigated_at = timezone.now()
            
            if 'is_resolved' in request.data:
                event.is_resolved = request.data['is_resolved']
                if event.is_resolved and not event.resolved_at:
                    event.resolved_at = timezone.now()
            
            if 'is_false_positive' in request.data:
                event.is_false_positive = request.data['is_false_positive']
            
            event.save()
            
            return Response({
                'success': True,
                'message': 'تم تحديث الحدث بنجاح'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في تحديث الحدث: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ThreatAnalysisView(APIView):
    """واجهة تحليل التهديدات المباشر"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """تحليل تهديد مخصص"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # بيانات التحليل
            analysis_data = {
                'ip_address': request.data.get('ip_address', ''),
                'path': request.data.get('path', ''),
                'method': request.data.get('method', 'GET'),
                'user_agent': request.data.get('user_agent', ''),
                'post_data': request.data.get('post_data', ''),
                'timestamp': timezone.now().isoformat()
            }
            
            # تحليل التهديدات
            threat_analysis = threat_detector.analyze_request(analysis_data)
            
            return Response({
                'success': True,
                'analysis_result': threat_analysis,
                'analyzed_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في التحليل: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BehaviorAnalysisView(APIView):
    """واجهة تحليل سلوك المستخدمين"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """جلب تحليل سلوك المستخدمين"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # جلب المستخدمين مع سلوك مشبوه
            suspicious_users = UserBehaviorProfile.objects.filter(
                risk_score__gte=0.5
            ).order_by('-risk_score')[:20]
            
            users_data = []
            for profile in suspicious_users:
                users_data.append({
                    'user_id': profile.user.id,
                    'username': profile.user.username,
                    'full_name': profile.user.get_full_name(),
                    'risk_score': profile.risk_score,
                    'anomaly_score': profile.anomaly_score,
                    'total_logins': profile.total_logins,
                    'failed_logins': profile.failed_logins,
                    'last_login_analyzed': profile.last_login_analyzed.isoformat() if profile.last_login_analyzed else None,
                    'typical_hours': profile.typical_login_hours,
                    'typical_locations': profile.typical_locations[:5]  # أول 5 مواقع
                })
            
            return Response({
                'success': True,
                'suspicious_users': users_data,
                'total_count': len(users_data)
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في جلب تحليل السلوك: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, user_id):
        """تحليل سلوك مستخدم محدد"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # بيانات الجلسة للتحليل
            session_data = {
                'ip_address': request.data.get('ip_address', ''),
                'user_agent': request.data.get('user_agent', ''),
                'timestamp': timezone.now().isoformat()
            }
            
            # تحليل السلوك
            behavior_analysis = behavior_analyzer.analyze_user_behavior(user_id, session_data)
            
            return Response({
                'success': True,
                'behavior_analysis': behavior_analysis
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في تحليل السلوك: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SecurityIncidentsView(APIView):
    """واجهة إدارة الحوادث الأمنية"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """جلب قائمة الحوادث الأمنية"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # معاملات التصفية
            status_filter = request.GET.get('status')
            severity = request.GET.get('severity')
            assigned_to = request.GET.get('assigned_to')
            
            queryset = SecurityIncident.objects.all()
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if severity:
                queryset = queryset.filter(severity=severity)
            
            if assigned_to:
                queryset = queryset.filter(assigned_to_id=assigned_to)
            
            queryset = queryset.order_by('-created_at')
            
            # تقسيم الصفحات
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 10))
            
            paginator = Paginator(queryset, per_page)
            incidents_page = paginator.get_page(page)
            
            incidents_data = []
            for incident in incidents_page:
                incidents_data.append({
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'incident_type': incident.incident_type,
                    'severity': incident.severity,
                    'status': incident.status,
                    'assigned_to': incident.assigned_to.get_full_name() if incident.assigned_to else None,
                    'reporter': incident.reporter.get_full_name(),
                    'affected_systems': incident.affected_systems,
                    'created_at': incident.created_at.isoformat(),
                    'resolved_at': incident.resolved_at.isoformat() if incident.resolved_at else None,
                    'related_events_count': incident.related_events.count()
                })
            
            return Response({
                'success': True,
                'incidents': incidents_data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في جلب الحوادث: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """إنشاء حادث أمني جديد"""
        
        try:
            if not is_security_admin(request.user):
                return Response({
                    'error': 'غير مخول'
                }, status=status.HTTP_403_FORBIDDEN)
            
            incident = SecurityIncident.objects.create(
                title=request.data.get('title'),
                description=request.data.get('description'),
                incident_type=request.data.get('incident_type'),
                severity=request.data.get('severity', 'medium'),
                reporter=request.user,
                affected_systems=request.data.get('affected_systems', []),
                impact_assessment=request.data.get('impact_assessment', '')
            )
            
            return Response({
                'success': True,
                'incident_id': incident.id,
                'message': 'تم إنشاء الحادث بنجاح'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'خطأ في إنشاء الحادث: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_audit_logs(request):
    """جلب سجلات المراجعة الأمنية"""
    
    try:
        if not is_security_admin(request.user):
            return Response({
                'error': 'غير مخول'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # معاملات التصفية
        user_id = request.GET.get('user_id')
        action_type = request.GET.get('action_type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        success_only = request.GET.get('success_only')
        
        queryset = SecurityAuditLog.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        if success_only:
            is_success = success_only.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(success=is_success)
        
        queryset = queryset.order_by('-timestamp')
        
        # تقسيم الصفحات
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
        paginator = Paginator(queryset, per_page)
        logs_page = paginator.get_page(page)
        
        logs_data = []
        for log in logs_page:
            logs_data.append({
                'id': log.id,
                'user': log.user.get_full_name(),
                'username': log.user.username,
                'action_type': log.action_type,
                'description': log.description,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent[:100] + '...' if len(log.user_agent) > 100 else log.user_agent,
                'success': log.success,
                'timestamp': log.timestamp.isoformat()
            })
        
        return Response({
            'success': True,
            'audit_logs': logs_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'خطأ في جلب سجلات المراجعة: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_reports(request):
    """تقارير الأمان المختصرة"""
    
    try:
        if not is_security_admin(request.user):
            return Response({
                'error': 'غير مخول'
            }, status=status.HTTP_403_FORBIDDEN)
        
        report_type = request.GET.get('type', 'summary')
        days = int(request.GET.get('days', 7))
        
        date_from = timezone.now() - timedelta(days=days)
        
        if report_type == 'summary':
            # تقرير ملخص
            report_data = {
                'period': f'آخر {days} أيام',
                'total_events': SecurityEvent.objects.filter(detected_at__gte=date_from).count(),
                'critical_events': SecurityEvent.objects.filter(
                    detected_at__gte=date_from, threat_level='critical'
                ).count(),
                'resolved_events': SecurityEvent.objects.filter(
                    detected_at__gte=date_from, is_resolved=True
                ).count(),
                'top_threats': list(
                    SecurityEvent.objects.filter(detected_at__gte=date_from)
                    .values('event_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                ),
                'top_ips': list(
                    SecurityEvent.objects.filter(detected_at__gte=date_from)
                    .values('ip_address')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                )
            }
        
        elif report_type == 'trends':
            # تقرير اتجاهات
            daily_stats = []
            for i in range(days):
                date = timezone.now().date() - timedelta(days=i)
                daily_count = SecurityEvent.objects.filter(
                    detected_at__date=date
                ).count()
                daily_stats.append({
                    'date': date.isoformat(),
                    'events_count': daily_count
                })
            
            report_data = {
                'period': f'آخر {days} أيام',
                'daily_stats': list(reversed(daily_stats))
            }
        
        else:
            report_data = {'error': 'نوع تقرير غير مدعوم'}
        
        return Response({
            'success': True,
            'report_type': report_type,
            'report_data': report_data,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'خطأ في إنتاج التقرير: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_ip_address(request):
    """حظر عنوان IP"""
    
    try:
        if not is_security_admin(request.user):
            return Response({
                'error': 'غير مخول'
            }, status=status.HTTP_403_FORBIDDEN)
        
        ip_address = request.data.get('ip_address')
        duration_hours = int(request.data.get('duration_hours', 24))
        reason = request.data.get('reason', 'Manual block by admin')
        
        if not ip_address:
            return Response({
                'error': 'عنوان IP مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # إضافة للقائمة السوداء في الـ cache
        from django.core.cache import cache
        cache_key = f'blocked_ip_{ip_address}'
        cache.set(cache_key, {
            'blocked_by': request.user.id,
            'reason': reason,
            'blocked_at': timezone.now().isoformat()
        }, duration_hours * 3600)
        
        # تسجيل الحدث
        SecurityEvent.objects.create(
            event_type='ip_blocked',
            threat_level='medium',
            title=f'IP Address Blocked: {ip_address}',
            description=f'IP address {ip_address} was manually blocked by {request.user.get_full_name()}. Reason: {reason}',
            ip_address=ip_address,
            metadata={
                'blocked_by': request.user.id,
                'duration_hours': duration_hours,
                'reason': reason
            }
        )
        
        return Response({
            'success': True,
            'message': f'تم حظر عنوان IP {ip_address} لمدة {duration_hours} ساعة'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'خطأ في حظر IP: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)