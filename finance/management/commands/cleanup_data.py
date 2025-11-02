from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'تنظيف البيانات القديمة في تطبيق finance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='عدد الأيام للاحتفاظ بالبيانات (افتراضي: 30)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حذف فعلي'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'تنظيف بيانات finance الأقدم من {cutoff_date.date()}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('تشغيل تجريبي - لن يتم حذف أي بيانات')
            )
        
        # TODO: إضافة منطق التنظيف حسب نماذج التطبيق
        
        self.stdout.write(
            self.style.SUCCESS('تم إكمال عملية التنظيف بنجاح')
        )
