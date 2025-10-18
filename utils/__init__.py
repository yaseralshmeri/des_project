# University Management System - Utilities Package
"""
حزمة الأدوات المساعدة لنظام إدارة الجامعة
"""

from .error_handlers import (
    ErrorMessages,
    custom_exception_handler,
    ErrorHandlerMixin,
    log_error,
    create_error_response
)

from .performance import (
    PerformanceOptimizer,
    performance_cache,
    measure_performance,
    CacheManager,
    QueryOptimizer,
    performance_monitor
)

from .notifications import (
    NotificationManager,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
    PrebuiltNotifications,
    NotificationScheduler,
    notification_manager,
    prebuilt_notifications
)

__all__ = [
    # Error Handling
    'ErrorMessages',
    'custom_exception_handler',
    'ErrorHandlerMixin',
    'log_error',
    'create_error_response',
    
    # Performance
    'PerformanceOptimizer',
    'performance_cache',
    'measure_performance',
    'CacheManager',
    'QueryOptimizer',
    'performance_monitor',
    
    # Notifications
    'NotificationManager',
    'NotificationType',
    'NotificationPriority',
    'NotificationChannel',
    'PrebuiltNotifications',
    'NotificationScheduler',
    'notification_manager',
    'prebuilt_notifications',
]