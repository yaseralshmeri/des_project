#!/bin/bash
# Deployment script for University Management System
# This script handles production deployment with zero downtime

set -e

# Configuration
PROJECT_NAME="university_system"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
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

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backup-first     Create backup before deployment"
    echo "  --skip-tests       Skip running tests"
    echo "  --force           Force deployment without confirmations"
    echo "  --rollback        Rollback to previous version"
    echo "  --status          Show deployment status"
    echo "  --logs            Show application logs"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Normal deployment"
    echo "  $0 --backup-first         # Backup then deploy"
    echo "  $0 --force                # Deploy without confirmations"
    echo "  $0 --rollback             # Rollback deployment"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker >/dev/null 2>&1; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file $ENV_FILE not found"
        info "Please copy .env.production.example to $ENV_FILE and configure it"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Check environment configuration
check_environment() {
    log "Checking environment configuration..."
    
    # Source the environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required variables
    local required_vars=(
        "SECRET_KEY"
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "EMAIL_HOST_PASSWORD"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            error "  - $var"
        done
        exit 1
    fi
    
    success "Environment configuration check passed"
}

# Create backup
create_backup() {
    if [ "$BACKUP_FIRST" = true ]; then
        log "Creating backup before deployment..."
        
        # Check if backup script exists
        if [ -f "scripts/backup.sh" ]; then
            ./scripts/backup.sh
            success "Backup completed"
        else
            warning "Backup script not found, skipping backup"
        fi
    fi
}

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" != true ]; then
        log "Running tests..."
        
        # Run tests in a temporary container
        if docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm web python manage.py test; then
            success "All tests passed"
        else
            error "Tests failed"
            exit 1
        fi
    else
        warning "Skipping tests"
    fi
}

# Build images
build_images() {
    log "Building Docker images..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache; then
        success "Images built successfully"
    else
        error "Failed to build images"
        exit 1
    fi
}

# Deploy application
deploy_application() {
    log "Deploying application..."
    
    # Create necessary directories
    mkdir -p logs/nginx
    mkdir -p backups
    
    # Pull latest images (if using external registry)
    # docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    # Start services
    if docker-compose -f "$DOCKER_COMPOSE_FILE" up -d; then
        success "Application deployed successfully"
    else
        error "Failed to deploy application"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    log "Waiting for services to be ready..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py check --database default >/dev/null 2>&1; then
            success "Services are ready"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 5
        ((attempt++))
    done
    
    error "Services failed to start within expected time"
    exit 1
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py migrate; then
        success "Migrations completed successfully"
    else
        error "Migration failed"
        exit 1
    fi
}

# Collect static files
collect_static() {
    log "Collecting static files..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput; then
        success "Static files collected successfully"
    else
        warning "Static files collection failed (non-critical)"
    fi
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check if web service is healthy
    local web_status=$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps web | grep -c "Up")
    if [ "$web_status" -eq 0 ]; then
        error "Web service is not running"
        exit 1
    fi
    
    # Check database connection
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py check --database default >/dev/null 2>&1; then
        success "Database connection verified"
    else
        error "Database connection failed"
        exit 1
    fi
    
    # Check Redis connection
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
        success "Redis connection verified"
    else
        error "Redis connection failed"
        exit 1
    fi
    
    # Check application health endpoint
    if curl -f http://localhost/health/ >/dev/null 2>&1; then
        success "Application health check passed"
    else
        error "Application health check failed"
        exit 1
    fi
    
    success "🎉 Deployment verification completed successfully!"
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo ""
    
    # Show container status
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
    
    # Show resource usage
    info "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
    
    # Show logs summary
    info "Recent logs (last 10 lines):"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=10
}

# Show logs
show_logs() {
    local service=${1:-web}
    log "Showing logs for service: $service"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f "$service"
}

# Rollback deployment
rollback_deployment() {
    warning "Starting rollback process..."
    
    if [ "$FORCE" != true ]; then
        read -p "Are you sure you want to rollback? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Rollback cancelled"
            exit 0
        fi
    fi
    
    # Stop current services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # TODO: Implement proper rollback logic
    # This would typically involve:
    # 1. Restoring previous Docker images
    # 2. Restoring database from backup
    # 3. Restoring configuration files
    
    warning "Rollback feature is not fully implemented yet"
    warning "Please restore manually from backup if needed"
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old Docker images and containers..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    success "Cleanup completed"
}

# Main deployment function
main_deploy() {
    log "🚀 Starting University Management System deployment..."
    
    check_prerequisites
    check_environment
    create_backup
    
    if [ "$FORCE" != true ]; then
        read -p "Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Deployment cancelled"
            exit 0
        fi
    fi
    
    run_tests
    build_images
    deploy_application
    wait_for_services
    run_migrations
    collect_static
    verify_deployment
    cleanup
    
    success "🎉 Deployment completed successfully!"
    info "Application is available at: https://$(grep UNIVERSITY_DOMAIN $ENV_FILE | cut -d'=' -f2)"
}

# Parse command line arguments
BACKUP_FIRST=false
SKIP_TESTS=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backup-first)
            BACKUP_FIRST=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --rollback)
            rollback_deployment
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --logs)
            show_logs "$2"
            exit 0
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run main deployment
main_deploy