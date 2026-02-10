#!/bin/bash

# ============================================================================
# BTRC QoS Dashboard - Automated Deployment Script
# Version: 3.0
# Date: 2026-02-09
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="BTRC QoS Dashboard"
PROJECT_DIR="/opt/btrc-qos-dashboard"
BACKUP_DIR="/opt/btrc-qos-dashboard/backups"
LOG_DIR="/opt/btrc-qos-dashboard/logs"
COMPOSE_FILE="docker-compose.prod.yml"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should NOT be run as root"
        log_info "Run as regular user with sudo privileges"
        exit 1
    fi
}

check_docker() {
    log_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        log_info "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        log_info "Please install Docker Compose"
        exit 1
    fi

    log_success "Docker is installed"
}

create_directories() {
    log_info "Creating required directories..."
    mkdir -p "$PROJECT_DIR"
    mkdir -p "$BACKUP_DIR/db"
    mkdir -p "$BACKUP_DIR/metabase"
    mkdir -p "$BACKUP_DIR/config"
    mkdir -p "$LOG_DIR"
    log_success "Directories created"
}

create_env_file() {
    log_info "Creating production environment file..."

    if [ -f "$PROJECT_DIR/.env" ]; then
        log_warning ".env file already exists"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing .env file"
            return
        fi
    fi

    # Generate secure passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    MB_DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

    cat > "$PROJECT_DIR/.env" <<EOF
# BTRC QoS Dashboard - Production Environment
# Generated: $(date)

# PostgreSQL / TimescaleDB Configuration
POSTGRES_USER=btrc_admin
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=btrc_qos_poc

# Metabase Configuration
MB_DB_TYPE=postgres
MB_DB_DBNAME=metabase_meta
MB_DB_USER=btrc_admin
MB_DB_PASS=$MB_DB_PASS
MB_JETTY_PORT=3000
JAVA_TIMEZONE=Asia/Dhaka

# Nginx Configuration
NGINX_PORT=8080

# Application
APP_ENV=production
APP_DEBUG=false

# Backup Configuration
BACKUP_DIR=$BACKUP_DIR
BACKUP_RETENTION_DAYS=30
EOF

    chmod 600 "$PROJECT_DIR/.env"

    log_success "Environment file created"
    log_warning "IMPORTANT: Save these credentials securely!"
    echo ""
    echo "PostgreSQL Password: $POSTGRES_PASSWORD"
    echo "Metabase DB Password: $MB_DB_PASS"
    echo ""
    read -p "Press Enter to continue..."
}

configure_firewall() {
    log_info "Configuring firewall..."

    if command -v ufw &> /dev/null; then
        if ! sudo ufw status | grep -q "Status: active"; then
            log_info "Enabling UFW firewall..."
            sudo ufw --force enable
        fi

        log_info "Allowing required ports..."
        sudo ufw allow 22/tcp comment "SSH"
        sudo ufw allow 3000/tcp comment "Metabase"
        sudo ufw allow 8080/tcp comment "Nginx Wrapper"

        log_success "Firewall configured"
        sudo ufw status
    else
        log_warning "UFW not found. Please configure firewall manually"
    fi
}

pull_images() {
    log_info "Pulling Docker images..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" pull
    log_success "Docker images pulled"
}

start_services() {
    log_info "Starting services..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" up -d
    log_success "Services started"
}

wait_for_services() {
    log_info "Waiting for services to be ready..."

    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker exec btrc-v3-timescaledb pg_isready -U btrc_admin &> /dev/null; then
            log_success "PostgreSQL is ready"
            break
        fi
        echo -n "."
        sleep 2
    done

    # Wait for Metabase
    log_info "Waiting for Metabase (this may take 2-3 minutes)..."
    for i in {1..60}; do
        if curl -sf http://localhost:3000/api/health &> /dev/null; then
            log_success "Metabase is ready"
            break
        fi
        echo -n "."
        sleep 3
    done

    # Wait for Nginx
    log_info "Waiting for Nginx..."
    for i in {1..10}; do
        if curl -sf http://localhost:8080/health &> /dev/null; then
            log_success "Nginx is ready"
            break
        fi
        echo -n "."
        sleep 1
    done
}

verify_deployment() {
    log_info "Verifying deployment..."

    # Check containers
    log_info "Checking containers..."
    docker ps --filter "name=btrc-v3" --format "table {{.Names}}\t{{.Status}}"

    # Test endpoints
    log_info "Testing endpoints..."

    if curl -sf http://localhost:3000/api/health > /dev/null; then
        log_success "✓ Metabase API: http://localhost:3000"
    else
        log_error "✗ Metabase API not responding"
    fi

    if curl -sf http://localhost:8080/health > /dev/null; then
        log_success "✓ Custom Wrapper: http://localhost:8080/dashboard"
    else
        log_error "✗ Custom Wrapper not responding"
    fi

    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    log_success "Server IP: $SERVER_IP"
}

setup_cron_backup() {
    log_info "Setting up automated backups..."

    # Check if backup script exists
    if [ ! -f "$PROJECT_DIR/backup.sh" ]; then
        log_warning "backup.sh not found, skipping cron setup"
        return
    fi

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$PROJECT_DIR/backup.sh"; then
        log_info "Backup cron job already exists"
        return
    fi

    # Add cron job
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh >> $LOG_DIR/backup.log 2>&1") | crontab -

    log_success "Daily backup scheduled (2 AM)"
}

show_summary() {
    echo ""
    echo "============================================================"
    echo "  $PROJECT_NAME - Deployment Complete!"
    echo "============================================================"
    echo ""
    echo "✅ Services Status:"
    docker ps --filter "name=btrc-v3" --format "  {{.Names}}: {{.Status}}"
    echo ""
    echo "📊 Access URLs:"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "  Metabase:       http://$SERVER_IP:3000"
    echo "  Custom Wrapper: http://$SERVER_IP:8080/dashboard"
    echo ""
    echo "🔐 Default Credentials:"
    echo "  Email:    alamin.technometrics22@gmail.com"
    echo "  Password: Test@123"
    echo "  ⚠️  CHANGE PASSWORD IMMEDIATELY!"
    echo ""
    echo "📝 Important Files:"
    echo "  Project Dir:  $PROJECT_DIR"
    echo "  Environment:  $PROJECT_DIR/.env"
    echo "  Backups:      $BACKUP_DIR"
    echo "  Logs:         $LOG_DIR"
    echo ""
    echo "📚 Documentation:"
    echo "  User Guide:       DASHBOARD_USER_GUIDE.md"
    echo "  Deployment Guide: DEPLOYMENT_GUIDE.md"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  View logs:     docker compose -f $COMPOSE_FILE logs -f"
    echo "  Stop services: docker compose -f $COMPOSE_FILE down"
    echo "  Start services: docker compose -f $COMPOSE_FILE up -d"
    echo "  Restart:       docker compose -f $COMPOSE_FILE restart"
    echo ""
    echo "============================================================"
    echo ""
}

main() {
    echo ""
    echo "============================================================"
    echo "  $PROJECT_NAME - Deployment Script"
    echo "============================================================"
    echo ""

    check_root
    check_docker

    log_info "Starting deployment to: $PROJECT_DIR"
    echo ""

    # Deployment steps
    create_directories
    create_env_file
    configure_firewall
    pull_images
    start_services
    wait_for_services
    verify_deployment
    setup_cron_backup

    show_summary

    log_success "Deployment completed successfully!"
    log_info "Access your dashboard at: http://$(hostname -I | awk '{print $1}'):3000"
}

# Run main function
main "$@"
