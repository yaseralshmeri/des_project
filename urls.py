"""
URLs الرئيسية للمشروع الجامعي - موحدة ومدمجة
University Management System - Unified URLs

تم الدمج في: 2025-11-02
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# URLs الأساسية
urlpatterns = [
    # الإدارة
    path('admin/', admin.site.urls),
    
    # التطبيقات الأساسية
    path('api/students/', include('students.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/academic/', include('academic.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/hr/', include('hr.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # الواجهة الرئيسية
    path('', include('web.urls')),
    
    # APIs الإضافية (معطلة مؤقتاً)
    # path('api/ai/', include('ai.urls')),
    # path('api/cyber-security/', include('cyber_security.urls')),
    # path('api/attendance/', include('attendance_qr.urls')),
]

# الملفات الثابتة والوسائط للتطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
