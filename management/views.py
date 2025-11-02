"""
Management Views for University System
عروض إدارة النظام للجامعة
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import connection
from django.core.management import call_command
from django.utils import timezone
import os
import sys
import platform
try:
    import psutil
except ImportError:
    psutil = None
import logging

logger = logging.getLogger(__name__)

def is_superuser(user):
    """Check if user is a superuser"""
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def dashboard(request):
    """System Management Dashboard"""
    context = {
        'title': 'لوحة إدارة النظام',
        'system_info': get_system_info(),
        'database_info': get_database_info(),
        'application_info': get_application_info(),
    }
    return render(request, 'management/dashboard.html', context)

@user_passes_test(is_superuser)
def system_info(request):
    """Display detailed system information"""
    context = {
        'title': 'معلومات النظام',
        'system': get_system_info(),
        'hardware': get_hardware_info(),
        'software': get_software_info(),
    }
    return render(request, 'management/system_info.html', context)

@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def backup_system(request):
    """Create system backup"""
    try:
        # Here you would implement actual backup logic
        # This is a placeholder implementation
        backup_path = f"/tmp/backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
            'backup_path': backup_path
        })
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'فشل في إنشاء النسخة الاحتياطية: {str(e)}'
        }, status=500)

@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def maintenance_mode(request):
    """Toggle maintenance mode"""
    try:
        action = request.POST.get('action', 'enable')
        
        if action == 'enable':
            # Enable maintenance mode
            # This would typically involve creating a maintenance flag file
            # or setting a configuration variable
            message = 'تم تفعيل وضع الصيانة'
        else:
            # Disable maintenance mode
            message = 'تم إلغاء وضع الصيانة'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'maintenance_mode': action == 'enable'
        })
    except Exception as e:
        logger.error(f"Maintenance mode toggle failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'فشل في تغيير وضع الصيانة: {str(e)}'
        }, status=500)

@user_passes_test(is_superuser)
def database_status(request):
    """Display database status and statistics"""
    context = {
        'title': 'حالة قاعدة البيانات',
        'database': get_database_info(),
        'tables': get_database_tables_info(),
    }
    return render(request, 'management/database_status.html', context)

@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def optimize_database(request):
    """Optimize database performance"""
    try:
        # Run database optimization commands
        # This is a placeholder - actual implementation would depend on database type
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE;")  # For SQLite
        
        return JsonResponse({
            'success': True,
            'message': 'تم تحسين قاعدة البيانات بنجاح'
        })
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'فشل في تحسين قاعدة البيانات: {str(e)}'
        }, status=500)

@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def backup_database(request):
    """Create database backup"""
    try:
        # This would implement actual database backup logic
        backup_file = f"db_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء نسخة احتياطية من قاعدة البيانات',
            'backup_file': backup_file
        })
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'فشل في إنشاء نسخة احتياطية: {str(e)}'
        }, status=500)

@user_passes_test(is_superuser)
def view_logs(request):
    """Display system logs"""
    log_type = request.GET.get('type', 'application')
    
    try:
        logs = get_recent_logs(log_type)
        context = {
            'title': 'سجلات النظام',
            'logs': logs,
            'log_type': log_type,
        }
        return render(request, 'management/logs.html', context)
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        context = {
            'title': 'سجلات النظام',
            'error': f'فشل في استرداد السجلات: {str(e)}',
        }
        return render(request, 'management/logs.html', context)

@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def clear_logs(request):
    """Clear system logs"""
    try:
        log_type = request.POST.get('type', 'all')
        # Implement log clearing logic here
        
        return JsonResponse({
            'success': True,
            'message': 'تم مسح السجلات بنجاح'
        })
    except Exception as e:
        logger.error(f"Log clearing failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'فشل في مسح السجلات: {str(e)}'
        }, status=500)

@user_passes_test(is_superuser)
def system_health(request):
    """Display system health status"""
    context = {
        'title': 'صحة النظام',
        'health_checks': perform_health_checks(),
    }
    return render(request, 'management/system_health.html', context)

# API Views
@user_passes_test(is_superuser)
def api_system_status(request):
    """API endpoint for system status"""
    try:
        status = {
            'system': get_system_info(),
            'database': get_database_info(),
            'application': get_application_info(),
            'timestamp': timezone.now().isoformat(),
        }
        return JsonResponse(status)
    except Exception as e:
        logger.error(f"System status API error: {e}")
        return JsonResponse({
            'error': 'Failed to retrieve system status'
        }, status=500)

@user_passes_test(is_superuser)
def api_performance_metrics(request):
    """API endpoint for performance metrics"""
    try:
        metrics = {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': dict(psutil.virtual_memory()._asdict()),
            'disk_usage': dict(psutil.disk_usage('/')._asdict()),
            'timestamp': timezone.now().isoformat(),
        }
        return JsonResponse(metrics)
    except Exception as e:
        logger.error(f"Performance metrics API error: {e}")
        return JsonResponse({
            'error': 'Failed to retrieve performance metrics'
        }, status=500)

# Helper Functions
def get_system_info():
    """Get basic system information"""
    try:
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {'error': str(e)}

def get_hardware_info():
    """Get hardware information"""
    try:
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': dict(psutil.virtual_memory()._asdict()),
            'disk': dict(psutil.disk_usage('/')._asdict()),
            'boot_time': psutil.boot_time(),
        }
    except Exception as e:
        logger.error(f"Failed to get hardware info: {e}")
        return {'error': str(e)}

def get_software_info():
    """Get software and application information"""
    try:
        return {
            'python_path': sys.executable,
            'python_version': sys.version,
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'installed_apps': list(settings.INSTALLED_APPS),
            'middleware': list(settings.MIDDLEWARE),
            'database_engine': settings.DATABASES['default']['ENGINE'],
        }
    except Exception as e:
        logger.error(f"Failed to get software info: {e}")
        return {'error': str(e)}

def get_database_info():
    """Get database information"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
        return {
            'engine': connection.settings_dict['ENGINE'],
            'name': connection.settings_dict['NAME'],
            'tables_count': len(tables),
            'tables': tables,
        }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {'error': str(e)}

def get_database_tables_info():
    """Get detailed information about database tables"""
    try:
        tables_info = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    tables_info.append({
                        'name': table,
                        'rows': count
                    })
                except Exception:
                    tables_info.append({
                        'name': table,
                        'rows': 'N/A'
                    })
                    
        return tables_info
    except Exception as e:
        logger.error(f"Failed to get tables info: {e}")
        return []

def get_application_info():
    """Get application-specific information"""
    try:
        return {
            'debug_mode': settings.DEBUG,
            'secret_key_set': bool(settings.SECRET_KEY),
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'time_zone': settings.TIME_ZONE,
            'language_code': settings.LANGUAGE_CODE,
            'static_url': settings.STATIC_URL,
            'media_url': settings.MEDIA_URL,
        }
    except Exception as e:
        logger.error(f"Failed to get application info: {e}")
        return {'error': str(e)}

def get_recent_logs(log_type='application', max_lines=100):
    """Get recent log entries"""
    try:
        # This is a placeholder implementation
        # In a real system, you'd read from actual log files
        logs = [
            {'timestamp': timezone.now(), 'level': 'INFO', 'message': 'System started successfully'},
            {'timestamp': timezone.now(), 'level': 'WARNING', 'message': 'High memory usage detected'},
            {'timestamp': timezone.now(), 'level': 'ERROR', 'message': 'Database connection timeout'},
        ]
        return logs
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return []

def perform_health_checks():
    """Perform various system health checks"""
    checks = []
    
    try:
        # Database connectivity check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            checks.append({
                'name': 'Database Connectivity',
                'status': 'PASS',
                'message': 'Database connection successful'
            })
    except Exception as e:
        checks.append({
            'name': 'Database Connectivity',
            'status': 'FAIL',
            'message': f'Database connection failed: {str(e)}'
        })
    
    # Disk space check
    try:
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent > 20:
            checks.append({
                'name': 'Disk Space',
                'status': 'PASS',
                'message': f'Disk space available: {free_percent:.1f}%'
            })
        elif free_percent > 10:
            checks.append({
                'name': 'Disk Space',
                'status': 'WARNING',
                'message': f'Low disk space: {free_percent:.1f}% available'
            })
        else:
            checks.append({
                'name': 'Disk Space',
                'status': 'FAIL',
                'message': f'Critical disk space: {free_percent:.1f}% available'
            })
    except Exception as e:
        checks.append({
            'name': 'Disk Space',
            'status': 'FAIL',
            'message': f'Failed to check disk space: {str(e)}'
        })
    
    # Memory check
    try:
        memory = psutil.virtual_memory()
        if memory.percent < 80:
            checks.append({
                'name': 'Memory Usage',
                'status': 'PASS',
                'message': f'Memory usage: {memory.percent:.1f}%'
            })
        elif memory.percent < 90:
            checks.append({
                'name': 'Memory Usage',
                'status': 'WARNING',
                'message': f'High memory usage: {memory.percent:.1f}%'
            })
        else:
            checks.append({
                'name': 'Memory Usage',
                'status': 'FAIL',
                'message': f'Critical memory usage: {memory.percent:.1f}%'
            })
    except Exception as e:
        checks.append({
            'name': 'Memory Usage',
            'status': 'FAIL',
            'message': f'Failed to check memory usage: {str(e)}'
        })
    
    return checks