#!/bin/bash
# Automated backup script for University Management System
# This script creates backups of database, media files, and configurations

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Database configuration
DB_HOST=${POSTGRES_HOST:-db}
DB_NAME=${POSTGRES_DB:-university_db}
DB_USER=${POSTGRES_USER:-university_user}
DB_PASSWORD=${POSTGRES_PASSWORD}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create backup directory
create_backup_dir() {
    local backup_path="$BACKUP_DIR/$DATE"
    mkdir -p "$backup_path"
    echo "$backup_path"
}

# Database backup
backup_database() {
    local backup_path=$1
    local db_backup_file="$backup_path/database_backup_$DATE.sql"
    
    log "Starting database backup..."
    
    if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$db_backup_file"; then
        success "Database backup completed: $db_backup_file"
        
        # Compress the SQL file
        gzip "$db_backup_file"
        success "Database backup compressed: ${db_backup_file}.gz"
        
        # Verify backup integrity
        if [ -f "${db_backup_file}.gz" ] && [ -s "${db_backup_file}.gz" ]; then
            success "Database backup verified successfully"
            return 0
        else
            error "Database backup verification failed"
            return 1
        fi
    else
        error "Database backup failed"
        return 1
    fi
}

# Media files backup
backup_media() {
    local backup_path=$1
    local media_backup_file="$backup_path/media_backup_$DATE.tar.gz"
    
    log "Starting media files backup..."
    
    if [ -d "/app/media" ] && [ "$(ls -A /app/media)" ]; then
        if tar -czf "$media_backup_file" -C /app media/; then
            success "Media files backup completed: $media_backup_file"
            return 0
        else
            error "Media files backup failed"
            return 1
        fi
    else
        warning "No media files found to backup"
        touch "$backup_path/no_media_files_$DATE.txt"
        return 0
    fi
}

# Static files backup (optional)
backup_static() {
    local backup_path=$1
    local static_backup_file="$backup_path/static_backup_$DATE.tar.gz"
    
    log "Starting static files backup..."
    
    if [ -d "/app/staticfiles" ] && [ "$(ls -A /app/staticfiles)" ]; then
        if tar -czf "$static_backup_file" -C /app staticfiles/; then
            success "Static files backup completed: $static_backup_file"
            return 0
        else
            warning "Static files backup failed (non-critical)"
            return 0
        fi
    else
        warning "No static files found to backup"
        return 0
    fi
}

# Configuration backup
backup_config() {
    local backup_path=$1
    local config_backup_file="$backup_path/config_backup_$DATE.tar.gz"
    
    log "Starting configuration backup..."
    
    # Create temporary directory for config files
    local temp_config_dir=$(mktemp -d)
    
    # Copy important configuration files
    cp /app/.env* "$temp_config_dir/" 2>/dev/null || true
    cp /app/docker-compose*.yml "$temp_config_dir/" 2>/dev/null || true
    cp -r /app/nginx "$temp_config_dir/" 2>/dev/null || true
    cp -r /app/docker "$temp_config_dir/" 2>/dev/null || true
    
    if tar -czf "$config_backup_file" -C "$temp_config_dir" .; then
        success "Configuration backup completed: $config_backup_file"
        rm -rf "$temp_config_dir"
        return 0
    else
        error "Configuration backup failed"
        rm -rf "$temp_config_dir"
        return 1
    fi
}

# Create backup manifest
create_manifest() {
    local backup_path=$1
    local manifest_file="$backup_path/backup_manifest_$DATE.txt"
    
    log "Creating backup manifest..."
    
    cat > "$manifest_file" << EOF
University Management System Backup Manifest
============================================
Backup Date: $(date)
Backup Path: $backup_path
Database: $DB_NAME
User: $DB_USER
Host: $DB_HOST

Files in this backup:
EOF
    
    # List all files in backup directory with sizes
    ls -lah "$backup_path" >> "$manifest_file"
    
    # Add system information
    cat >> "$manifest_file" << EOF

System Information:
==================
Hostname: $(hostname)
Disk Usage: $(df -h "$backup_path" | tail -1)
Memory Usage: $(free -h | head -2)
Load Average: $(uptime)
EOF
    
    success "Backup manifest created: $manifest_file"
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    if find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null; then
        success "Old backups cleaned up successfully"
    else
        warning "Failed to clean up some old backups"
    fi
    
    # Show remaining backups
    local remaining_backups=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" | wc -l)
    log "Remaining backups: $remaining_backups"
}

# Verify backup integrity
verify_backup() {
    local backup_path=$1
    
    log "Verifying backup integrity..."
    
    local errors=0
    
    # Check database backup
    if [ -f "$backup_path/database_backup_$DATE.sql.gz" ]; then
        if gzip -t "$backup_path/database_backup_$DATE.sql.gz"; then
            success "Database backup integrity verified"
        else
            error "Database backup is corrupted"
            ((errors++))
        fi
    else
        error "Database backup file not found"
        ((errors++))
    fi
    
    # Check media backup
    if [ -f "$backup_path/media_backup_$DATE.tar.gz" ]; then
        if tar -tzf "$backup_path/media_backup_$DATE.tar.gz" >/dev/null 2>&1; then
            success "Media backup integrity verified"
        else
            error "Media backup is corrupted"
            ((errors++))
        fi
    fi
    
    # Check config backup
    if [ -f "$backup_path/config_backup_$DATE.tar.gz" ]; then
        if tar -tzf "$backup_path/config_backup_$DATE.tar.gz" >/dev/null 2>&1; then
            success "Configuration backup integrity verified"
        else
            error "Configuration backup is corrupted"
            ((errors++))
        fi
    fi
    
    return $errors
}

# Send notification (optional)
send_notification() {
    local status=$1
    local backup_path=$2
    
    if command -v curl >/dev/null 2>&1 && [ -n "$WEBHOOK_URL" ]; then
        local message
        if [ "$status" = "success" ]; then
            message="✅ University System backup completed successfully at $backup_path"
        else
            message="❌ University System backup failed. Check logs for details."
        fi
        
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$message\"}" \
            >/dev/null 2>&1 || true
    fi
}

# Main backup function
main() {
    log "Starting University Management System backup process..."
    
    # Check if database is accessible
    if ! pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
        error "Database is not accessible. Aborting backup."
        send_notification "failed" ""
        exit 1
    fi
    
    # Create backup directory
    local backup_path
    backup_path=$(create_backup_dir)
    
    local backup_errors=0
    
    # Perform backups
    backup_database "$backup_path" || ((backup_errors++))
    backup_media "$backup_path" || ((backup_errors++))
    backup_static "$backup_path"
    backup_config "$backup_path" || ((backup_errors++))
    
    # Create manifest
    create_manifest "$backup_path"
    
    # Verify backup integrity
    verify_backup "$backup_path" || ((backup_errors++))
    
    # Clean old backups
    cleanup_old_backups
    
    # Report results
    if [ $backup_errors -eq 0 ]; then
        success "🎉 Backup process completed successfully!"
        success "Backup location: $backup_path"
        success "Total backup size: $(du -sh "$backup_path" | cut -f1)"
        send_notification "success" "$backup_path"
        exit 0
    else
        error "❌ Backup process completed with $backup_errors errors"
        send_notification "failed" "$backup_path"
        exit 1
    fi
}

# Handle signals
trap 'error "Backup interrupted by signal"; exit 1' INT TERM

# Run main function
main "$@"