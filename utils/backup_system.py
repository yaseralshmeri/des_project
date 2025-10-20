"""
Advanced Backup System for University Management System
نظام النسخ الاحتياطي المتقدم لنظام إدارة الجامعة
"""

import os
import json
import gzip
import shutil
import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Advanced backup manager with multiple backup types and restoration
    مدير النسخ الاحتياطي المتقدم مع أنواع متعددة من النسخ والاستعادة
    """
    
    def __init__(self):
        self.backup_dir = Path(settings.BASE_DIR) / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different backup types
        (self.backup_dir / 'full').mkdir(exist_ok=True)
        (self.backup_dir / 'incremental').mkdir(exist_ok=True)
        (self.backup_dir / 'media').mkdir(exist_ok=True)
        (self.backup_dir / 'database').mkdir(exist_ok=True)
    
    def create_full_backup(self, compress=True):
        """
        Create a full system backup including database and media files
        إنشاء نسخة احتياطية كاملة تشمل قاعدة البيانات والملفات
        """
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'full_backup_{timestamp}'
            backup_path = self.backup_dir / 'full' / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup database
            db_backup_path = backup_path / 'database'
            self._backup_database(db_backup_path)
            
            # Backup media files
            media_backup_path = backup_path / 'media'
            self._backup_media_files(media_backup_path)
            
            # Backup configuration files
            config_backup_path = backup_path / 'config'
            self._backup_config_files(config_backup_path)
            
            # Create backup manifest
            manifest = {
                'type': 'full',
                'timestamp': timestamp,
                'created_at': datetime.datetime.now().isoformat(),
                'database_included': True,
                'media_included': True,
                'config_included': True,
                'compressed': compress
            }
            
            manifest_path = backup_path / 'manifest.json'
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Compress if requested
            if compress:
                compressed_path = self._compress_backup(backup_path)
                shutil.rmtree(backup_path)
                backup_path = compressed_path
            
            # Log success
            logger.info(f"Full backup created successfully: {backup_path}")
            
            # Send notification email
            self._send_backup_notification('full', backup_path, True)
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Full backup failed: {str(e)}")
            self._send_backup_notification('full', None, False, str(e))
            raise
    
    def create_incremental_backup(self, since_date=None):
        """
        Create an incremental backup of changes since last backup
        إنشاء نسخة احتياطية تدريجية للتغييرات منذ آخر نسخة
        """
        try:
            if since_date is None:
                # Get date of last backup
                since_date = self._get_last_backup_date()
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'incremental_backup_{timestamp}'
            backup_path = self.backup_dir / 'incremental' / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup only changed database records
            db_backup_path = backup_path / 'database'
            self._backup_database_incremental(db_backup_path, since_date)
            
            # Backup only changed media files
            media_backup_path = backup_path / 'media'
            self._backup_media_files_incremental(media_backup_path, since_date)
            
            # Create manifest
            manifest = {
                'type': 'incremental',
                'timestamp': timestamp,
                'created_at': datetime.datetime.now().isoformat(),
                'since_date': since_date.isoformat() if since_date else None,
                'database_included': True,
                'media_included': True
            }
            
            manifest_path = backup_path / 'manifest.json'
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Incremental backup created successfully: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Incremental backup failed: {str(e)}")
            raise
    
    def restore_backup(self, backup_path, restore_type='full'):
        """
        Restore system from backup
        استعادة النظام من النسخة الاحتياطية
        """
        try:
            backup_path = Path(backup_path)
            
            # Decompress if needed
            if backup_path.suffix == '.gz':
                backup_path = self._decompress_backup(backup_path)
            
            # Read manifest
            manifest_path = backup_path / 'manifest.json'
            if not manifest_path.exists():
                raise ValueError("Invalid backup: manifest.json not found")
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Restore database
            if manifest.get('database_included', False):
                db_backup_path = backup_path / 'database'
                self._restore_database(db_backup_path)
            
            # Restore media files
            if manifest.get('media_included', False):
                media_backup_path = backup_path / 'media'
                self._restore_media_files(media_backup_path)
            
            # Restore configuration files
            if manifest.get('config_included', False):
                config_backup_path = backup_path / 'config'
                self._restore_config_files(config_backup_path)
            
            logger.info(f"Backup restored successfully from: {backup_path}")
            
            # Send notification email
            self._send_restore_notification(backup_path, True)
            
            return True
            
        except Exception as e:
            logger.error(f"Backup restoration failed: {str(e)}")
            self._send_restore_notification(backup_path, False, str(e))
            raise
    
    def list_backups(self):
        """
        List all available backups with details
        عرض جميع النسخ الاحتياطية المتاحة مع التفاصيل
        """
        backups = []
        
        # List full backups
        full_backup_dir = self.backup_dir / 'full'
        if full_backup_dir.exists():
            for backup_path in full_backup_dir.iterdir():
                backup_info = self._get_backup_info(backup_path)
                if backup_info:
                    backups.append(backup_info)
        
        # List incremental backups
        incremental_backup_dir = self.backup_dir / 'incremental'
        if incremental_backup_dir.exists():
            for backup_path in incremental_backup_dir.iterdir():
                backup_info = self._get_backup_info(backup_path)
                if backup_info:
                    backups.append(backup_info)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def delete_old_backups(self, keep_days=30):
        """
        Delete backups older than specified days
        حذف النسخ الاحتياطية الأقدم من عدد الأيام المحدد
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        deleted_count = 0
        
        for backup_type in ['full', 'incremental']:
            backup_dir = self.backup_dir / backup_type
            if backup_dir.exists():
                for backup_path in backup_dir.iterdir():
                    try:
                        # Get backup creation time
                        backup_info = self._get_backup_info(backup_path)
                        if backup_info and backup_info['created_at'] < cutoff_date:
                            if backup_path.is_dir():
                                shutil.rmtree(backup_path)
                            else:
                                backup_path.unlink()
                            deleted_count += 1
                            logger.info(f"Deleted old backup: {backup_path}")
                    except Exception as e:
                        logger.error(f"Error deleting backup {backup_path}: {str(e)}")
        
        return deleted_count
    
    def _backup_database(self, backup_path):
        """Backup all database models"""
        backup_path.mkdir(exist_ok=True)
        
        # Get all models
        models = apps.get_models()
        
        for model in models:
            try:
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                
                # Create app directory
                app_dir = backup_path / app_label
                app_dir.mkdir(exist_ok=True)
                
                # Serialize model data
                data = serialize('json', model.objects.all(), indent=2)
                
                # Save to file
                model_file = app_dir / f'{model_name}.json'
                with open(model_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                
            except Exception as e:
                logger.error(f"Error backing up model {model}: {str(e)}")
    
    def _backup_database_incremental(self, backup_path, since_date):
        """Backup database changes since date"""
        backup_path.mkdir(exist_ok=True)
        
        models = apps.get_models()
        
        for model in models:
            try:
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                
                # Check if model has created_at or updated_at field
                queryset = model.objects.all()
                
                # Try to filter by date
                date_fields = ['created_at', 'updated_at', 'modified_at', 'date_created', 'date_modified']
                filtered = False
                
                for field_name in date_fields:
                    if hasattr(model, field_name):
                        filter_kwargs = {f'{field_name}__gte': since_date}
                        queryset = model.objects.filter(**filter_kwargs)
                        filtered = True
                        break
                
                # Only backup if there are changes or if we couldn't filter by date
                if not filtered or queryset.exists():
                    app_dir = backup_path / app_label
                    app_dir.mkdir(exist_ok=True)
                    
                    data = serialize('json', queryset, indent=2)
                    
                    model_file = app_dir / f'{model_name}.json'
                    with open(model_file, 'w', encoding='utf-8') as f:
                        f.write(data)
                
            except Exception as e:
                logger.error(f"Error backing up model {model} incrementally: {str(e)}")
    
    def _backup_media_files(self, backup_path):
        """Backup all media files"""
        if hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
            shutil.copytree(settings.MEDIA_ROOT, backup_path, dirs_exist_ok=True)
    
    def _backup_media_files_incremental(self, backup_path, since_date):
        """Backup media files changed since date"""
        if not hasattr(settings, 'MEDIA_ROOT') or not os.path.exists(settings.MEDIA_ROOT):
            return
        
        backup_path.mkdir(exist_ok=True)
        media_root = Path(settings.MEDIA_ROOT)
        
        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                # Check file modification time
                mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime >= since_date:
                    # Copy file to backup
                    relative_path = file_path.relative_to(media_root)
                    backup_file_path = backup_path / relative_path
                    backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_file_path)
    
    def _backup_config_files(self, backup_path):
        """Backup configuration files"""
        backup_path.mkdir(exist_ok=True)
        
        config_files = [
            'settings.py',
            'urls.py',
            'requirements.txt',
            '.env'
        ]
        
        for config_file in config_files:
            file_path = Path(settings.BASE_DIR) / config_file
            if file_path.exists():
                shutil.copy2(file_path, backup_path / config_file)
    
    def _restore_database(self, backup_path):
        """Restore database from backup"""
        # This is a simplified version - in production, you'd want more sophisticated restoration
        # including dependency handling and data validation
        pass
    
    def _restore_media_files(self, backup_path):
        """Restore media files from backup"""
        if backup_path.exists() and hasattr(settings, 'MEDIA_ROOT'):
            shutil.copytree(backup_path, settings.MEDIA_ROOT, dirs_exist_ok=True)
    
    def _restore_config_files(self, backup_path):
        """Restore configuration files from backup"""
        if backup_path.exists():
            for config_file in backup_path.iterdir():
                if config_file.is_file():
                    shutil.copy2(config_file, settings.BASE_DIR / config_file.name)
    
    def _compress_backup(self, backup_path):
        """Compress backup directory"""
        compressed_path = backup_path.with_suffix('.tar.gz')
        shutil.make_archive(str(backup_path), 'gztar', backup_path)
        return compressed_path
    
    def _decompress_backup(self, compressed_path):
        """Decompress backup archive"""
        extract_path = compressed_path.with_suffix('')
        shutil.unpack_archive(compressed_path, extract_path)
        return extract_path
    
    def _get_backup_info(self, backup_path):
        """Get backup information from manifest"""
        try:
            manifest_path = backup_path / 'manifest.json'
            if not manifest_path.exists():
                return None
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Get file size
            size = self._get_directory_size(backup_path)
            
            manifest.update({
                'path': str(backup_path),
                'size': size,
                'size_formatted': self._format_file_size(size)
            })
            
            return manifest
            
        except Exception as e:
            logger.error(f"Error getting backup info for {backup_path}: {str(e)}")
            return None
    
    def _get_directory_size(self, path):
        """Get total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def _format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _get_last_backup_date(self):
        """Get the date of the last backup"""
        backups = self.list_backups()
        if backups:
            return datetime.datetime.fromisoformat(backups[0]['created_at'])
        return datetime.datetime.now() - datetime.timedelta(days=1)
    
    def _send_backup_notification(self, backup_type, backup_path, success, error_message=None):
        """Send email notification about backup status"""
        try:
            if success:
                subject = f'نجح إنشاء النسخة الاحتياطية - {backup_type}'
                message = f'تم إنشاء النسخة الاحتياطية بنجاح في المسار: {backup_path}'
            else:
                subject = f'فشل في إنشاء النسخة الاحتياطية - {backup_type}'
                message = f'حدث خطأ أثناء إنشاء النسخة الاحتياطية: {error_message}'
            
            # Send email to administrators
            # This requires EMAIL_BACKEND to be configured in settings
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['admin@university.edu'])
            
        except Exception as e:
            logger.error(f"Error sending backup notification: {str(e)}")
    
    def _send_restore_notification(self, backup_path, success, error_message=None):
        """Send email notification about restore status"""
        try:
            if success:
                subject = 'نجحت عملية استعادة النسخة الاحتياطية'
                message = f'تم استعادة النظام بنجاح من النسخة الاحتياطية: {backup_path}'
            else:
                subject = 'فشلت عملية استعادة النسخة الاحتياطية'
                message = f'حدث خطأ أثناء استعادة النسخة الاحتياطية: {error_message}'
            
            # Send email to administrators
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['admin@university.edu'])
            
        except Exception as e:
            logger.error(f"Error sending restore notification: {str(e)}")


# Convenience functions for easy use
def create_full_backup(compress=True):
    """Create a full backup"""
    manager = BackupManager()
    return manager.create_full_backup(compress=compress)

def create_incremental_backup(since_date=None):
    """Create an incremental backup"""
    manager = BackupManager()
    return manager.create_incremental_backup(since_date=since_date)

def restore_backup(backup_path):
    """Restore from backup"""
    manager = BackupManager()
    return manager.restore_backup(backup_path)

def list_backups():
    """List all backups"""
    manager = BackupManager()
    return manager.list_backups()

def cleanup_old_backups(keep_days=30):
    """Clean up old backups"""
    manager = BackupManager()
    return manager.delete_old_backups(keep_days=keep_days)