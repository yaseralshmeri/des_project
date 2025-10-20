"""
Setup system with initial data and configurations
إعداد النظام مع البيانات والتكوينات الأولية
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from admin_control.models import SystemConfiguration, AdminDashboardWidget
from roles_permissions.models import Department, Role, Permission, RolePermission
from finance.models import FiscalYear
from django.utils import timezone
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup system with initial data and configurations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before setup',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 بدء إعداد النظام...')
        
        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_data()
                
                self.create_system_configurations()
                self.create_departments()
                self.create_roles_and_permissions()
                self.create_fiscal_year()
                self.create_dashboard_widgets()
                self.create_admin_user()
                
            self.stdout.write(
                self.style.SUCCESS('✅ تم إعداد النظام بنجاح!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إعداد النظام: {str(e)}')
            )
            raise
    
    def reset_data(self):
        """Reset existing data"""
        self.stdout.write('🔄 إعادة تعيين البيانات الموجودة...')
        
        # Delete non-critical data
        SystemConfiguration.objects.filter(is_system_permission=False).delete()
        AdminDashboardWidget.objects.all().delete()
        
        self.stdout.write('✅ تم إعادة تعيين البيانات')
    
    def create_system_configurations(self):
        """Create default system configurations"""
        self.stdout.write('⚙️ إنشاء تكوينات النظام...')
        
        configs = [
            {
                'key': 'system_name',
                'value': 'نظام إدارة الجامعة الشامل',
                'description': 'اسم النظام',
                'category': 'general'
            },
            {
                'key': 'academic_year',
                'value': '2024-2025',
                'description': 'السنة الأكاديمية الحالية',
                'category': 'academic'
            },
            {
                'key': 'max_login_attempts',
                'value': '5',
                'description': 'عدد محاولات تسجيل الدخول القصوى',
                'category': 'security'
            },
            {
                'key': 'session_timeout',
                'value': '30',
                'description': 'مهلة انتهاء الجلسة بالدقائق',
                'category': 'security'
            },
            {
                'key': 'default_language',
                'value': 'ar',
                'description': 'اللغة الافتراضية للنظام',
                'category': 'localization'
            },
            {
                'key': 'email_notifications',
                'value': 'true',
                'description': 'تفعيل إشعارات البريد الإلكتروني',
                'category': 'notifications'
            },
            {
                'key': 'sms_notifications',
                'value': 'false',
                'description': 'تفعيل إشعارات الرسائل النصية',
                'category': 'notifications'
            },
            {
                'key': 'auto_backup',
                'value': 'true',
                'description': 'تفعيل النسخ الاحتياطي التلقائي',
                'category': 'system'
            },
            {
                'key': 'backup_frequency',
                'value': 'daily',
                'description': 'تكرار النسخ الاحتياطي',
                'category': 'system'
            },
            {
                'key': 'ai_predictions',
                'value': 'true',
                'description': 'تفعيل توقعات الذكاء الاصطناعي',
                'category': 'ai'
            }
        ]
        
        for config_data in configs:
            config, created = SystemConfiguration.objects.get_or_create(
                key=config_data['key'],
                defaults=config_data
            )
            if created:
                self.stdout.write(f'  ✅ تم إنشاء التكوين: {config.key}')
    
    def create_departments(self):
        """Create default departments"""
        self.stdout.write('🏢 إنشاء الأقسام الأكاديمية...')
        
        departments = [
            {
                'name': 'كلية الهندسة',
                'code': 'ENG',
                'description': 'كلية الهندسة وعلوم الحاسوب'
            },
            {
                'name': 'كلية الطب',
                'code': 'MED',
                'description': 'كلية الطب والعلوم الصحية'
            },
            {
                'name': 'كلية الأعمال',
                'code': 'BUS',
                'description': 'كلية إدارة الأعمال والاقتصاد'
            },
            {
                'name': 'كلية الآداب',
                'code': 'ART',
                'description': 'كلية الآداب والعلوم الإنسانية'
            },
            {
                'name': 'كلية العلوم',
                'code': 'SCI',
                'description': 'كلية العلوم الطبيعية والرياضيات'
            },
            {
                'name': 'الشؤون الإدارية',
                'code': 'ADM',
                'description': 'قسم الشؤون الإدارية والمالية'
            },
            {
                'name': 'تقنية المعلومات',
                'code': 'IT',
                'description': 'قسم تقنية المعلومات والنظم'
            }
        ]
        
        for dept_data in departments:
            department, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(f'  ✅ تم إنشاء القسم: {department.name}')
    
    def create_roles_and_permissions(self):
        """Create default roles and permissions"""
        self.stdout.write('🔐 إنشاء الأدوار والصلاحيات...')
        
        # Create permissions
        permissions_data = [
            # Student permissions
            ('view_students', 'عرض الطلاب', 'READ', 'students'),
            ('add_students', 'إضافة طلاب', 'CREATE', 'students'),
            ('change_students', 'تعديل الطلاب', 'UPDATE', 'students'),
            ('delete_students', 'حذف الطلاب', 'DELETE', 'students'),
            
            # Course permissions
            ('view_courses', 'عرض المقررات', 'READ', 'courses'),
            ('add_courses', 'إضافة مقررات', 'CREATE', 'courses'),
            ('change_courses', 'تعديل المقررات', 'UPDATE', 'courses'),
            ('delete_courses', 'حذف المقررات', 'DELETE', 'courses'),
            
            # Financial permissions
            ('view_finance', 'عرض المالية', 'READ', 'finance'),
            ('manage_payments', 'إدارة المدفوعات', 'MANAGE', 'finance'),
            ('generate_invoices', 'إنشاء الفواتير', 'CREATE', 'finance'),
            ('approve_refunds', 'الموافقة على المبالغ المسترد', 'APPROVE', 'finance'),
            
            # Report permissions
            ('view_reports', 'عرض التقارير', 'READ', 'reports'),
            ('generate_reports', 'إنشاء التقارير', 'CREATE', 'reports'),
            ('export_reports', 'تصدير التقارير', 'EXPORT', 'reports'),
            
            # System permissions
            ('manage_users', 'إدارة المستخدمين', 'MANAGE', 'users'),
            ('system_configuration', 'تكوين النظام', 'MANAGE', 'system'),
            ('view_analytics', 'عرض التحليلات', 'READ', 'analytics'),
            ('manage_notifications', 'إدارة الإشعارات', 'MANAGE', 'notifications'),
        ]
        
        for perm_name, display_name, perm_type, resource in permissions_data:
            permission, created = Permission.objects.get_or_create(
                name=perm_name,
                defaults={
                    'display_name': display_name,
                    'permission_type': perm_type,
                    'resource_name': resource,
                    'description': f'صلاحية {display_name}'
                }
            )
            if created:
                self.stdout.write(f'  ✅ تم إنشاء الصلاحية: {permission.display_name}')
        
        # Create roles
        roles_data = [
            {
                'name': 'super_admin',
                'display_name': 'مدير النظام الرئيسي',
                'description': 'صلاحيات كاملة لإدارة النظام',
                'role_type': 'SYSTEM',
                'priority': 10
            },
            {
                'name': 'admin',
                'display_name': 'مدير النظام',
                'description': 'صلاحيات إدارية عامة',
                'role_type': 'SYSTEM',
                'priority': 9
            },
            {
                'name': 'academic_admin',
                'display_name': 'مدير أكاديمي',
                'description': 'إدارة الشؤون الأكاديمية',
                'role_type': 'DEPARTMENT',
                'priority': 8
            },
            {
                'name': 'financial_admin',
                'display_name': 'مدير مالي',
                'description': 'إدارة الشؤون المالية',
                'role_type': 'DEPARTMENT',
                'priority': 7
            },
            {
                'name': 'teacher',
                'display_name': 'عضو هيئة تدريس',
                'description': 'أعضاء هيئة التدريس',
                'role_type': 'DEPARTMENT',
                'priority': 6
            },
            {
                'name': 'staff',
                'display_name': 'موظف',
                'description': 'موظفو الجامعة',
                'role_type': 'DEPARTMENT',
                'priority': 5
            },
            {
                'name': 'student',
                'display_name': 'طالب',
                'description': 'طلاب الجامعة',
                'role_type': 'CUSTOM',
                'priority': 1
            }
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'  ✅ تم إنشاء الدور: {role.display_name}')
        
        # Assign permissions to roles
        self.assign_role_permissions()
    
    def assign_role_permissions(self):
        """Assign permissions to roles"""
        self.stdout.write('🔗 ربط الصلاحيات بالأدوار...')
        
        # Super Admin gets all permissions
        super_admin_role = Role.objects.get(name='super_admin')
        all_permissions = Permission.objects.all()
        
        for permission in all_permissions:
            role_perm, created = RolePermission.objects.get_or_create(
                role=super_admin_role,
                permission=permission
            )
        
        # Define specific role permissions
        role_permissions = {
            'admin': ['view_students', 'add_students', 'change_students', 'view_courses', 
                     'add_courses', 'change_courses', 'view_reports', 'generate_reports'],
            'academic_admin': ['view_students', 'add_students', 'change_students', 
                              'view_courses', 'add_courses', 'change_courses', 'view_reports'],
            'financial_admin': ['view_finance', 'manage_payments', 'generate_invoices', 
                               'view_reports', 'generate_reports'],
            'teacher': ['view_students', 'view_courses', 'change_courses'],
            'staff': ['view_students', 'view_courses'],
            'student': ['view_courses']
        }
        
        for role_name, permission_names in role_permissions.items():
            try:
                role = Role.objects.get(name=role_name)
                for perm_name in permission_names:
                    try:
                        permission = Permission.objects.get(name=perm_name)
                        RolePermission.objects.get_or_create(
                            role=role,
                            permission=permission
                        )
                    except Permission.DoesNotExist:
                        continue
            except Role.DoesNotExist:
                continue
    
    def create_fiscal_year(self):
        """Create current fiscal year"""
        self.stdout.write('📅 إنشاء السنة المالية...')
        
        current_year = timezone.now().year
        fiscal_year, created = FiscalYear.objects.get_or_create(
            name=f'{current_year}-{current_year + 1}',
            defaults={
                'start_date': date(current_year, 9, 1),
                'end_date': date(current_year + 1, 8, 31),
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✅ تم إنشاء السنة المالية: {fiscal_year.name}')
    
    def create_dashboard_widgets(self):
        """Create default dashboard widgets"""
        self.stdout.write('📊 إنشاء ويدجت لوحة التحكم...')
        
        widgets = [
            {
                'name': 'student_stats',
                'widget_type': 'STAT',
                'title': 'إحصائيات الطلاب',
                'description': 'عدد الطلاب المسجلين والنشطين',
                'position_x': 0,
                'position_y': 0,
                'width': 3,
                'height': 2
            },
            {
                'name': 'financial_overview',
                'widget_type': 'CHART',
                'title': 'نظرة مالية عامة',
                'description': 'الإيرادات والمدفوعات',
                'position_x': 3,
                'position_y': 0,
                'width': 6,
                'height': 4
            },
            {
                'name': 'recent_activities',
                'widget_type': 'ACTIVITY',
                'title': 'الأنشطة الحديثة',
                'description': 'آخر الأنشطة في النظام',
                'position_x': 9,
                'position_y': 0,
                'width': 3,
                'height': 4
            },
            {
                'name': 'alerts',
                'widget_type': 'ALERT',
                'title': 'التنبيهات',
                'description': 'تنبيهات النظام والأمان',
                'position_x': 0,
                'position_y': 2,
                'width': 3,
                'height': 2
            }
        ]
        
        for widget_data in widgets:
            widget, created = AdminDashboardWidget.objects.get_or_create(
                name=widget_data['name'],
                defaults=widget_data
            )
            if created:
                self.stdout.write(f'  ✅ تم إنشاء الويدجت: {widget.title}')
    
    def create_admin_user(self):
        """Create default admin user if doesn't exist"""
        self.stdout.write('👤 إنشاء مستخدم الإدارة...')
        
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                first_name='مدير',
                last_name='النظام'
            )
            
            # Assign super admin role
            try:
                super_admin_role = Role.objects.get(name='super_admin')
                from roles_permissions.models import UserRole
                UserRole.objects.create(
                    user=admin_user,
                    role=super_admin_role,
                    assigned_by=admin_user,
                    reason='إعداد أولي للنظام'
                )
            except Role.DoesNotExist:
                pass
            
            self.stdout.write('  ✅ تم إنشاء مستخدم الإدارة')
            self.stdout.write('  📝 اسم المستخدم: admin')
            self.stdout.write('  🔑 كلمة المرور: admin123')
            self.stdout.write('  ⚠️  يرجى تغيير كلمة المرور بعد تسجيل الدخول')
        else:
            self.stdout.write('  ℹ️  مستخدم الإدارة موجود بالفعل')