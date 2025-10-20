# توجيهات الأمان السيبراني
# Cyber Security URL Configuration

from django.urls import path, include
from . import views

app_name = 'cyber_security'

urlpatterns = [
    # لوحة تحكم الأمان
    path('dashboard/', views.SecurityDashboardView.as_view(), name='security_dashboard'),
    
    # إدارة الأحداث الأمنية
    path('events/', views.SecurityEventsView.as_view(), name='security_events'),
    path('events/<int:event_id>/update/', views.SecurityEventsView.as_view(), name='update_security_event'),
    
    # تحليل التهديدات
    path('threat-analysis/', views.ThreatAnalysisView.as_view(), name='threat_analysis'),
    
    # تحليل سلوك المستخدمين
    path('behavior-analysis/', views.BehaviorAnalysisView.as_view(), name='behavior_analysis'),
    path('behavior-analysis/<int:user_id>/', views.BehaviorAnalysisView.as_view(), name='analyze_user_behavior'),
    
    # إدارة الحوادث الأمنية
    path('incidents/', views.SecurityIncidentsView.as_view(), name='security_incidents'),
    
    # سجلات المراجعة الأمنية
    path('audit-logs/', views.security_audit_logs, name='audit_logs'),
    
    # تقارير الأمان
    path('reports/', views.security_reports, name='security_reports'),
    
    # إجراءات أمنية
    path('block-ip/', views.block_ip_address, name='block_ip'),
]