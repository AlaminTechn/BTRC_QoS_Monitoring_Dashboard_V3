# Complete Deployment Guide

Production deployment guide for BTRC QoS Monitoring Dashboard V3.

## Table of Contents
1. [Deployment Architecture](#deployment-architecture)
2. [Prerequisites](#prerequisites)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Server Configuration](#server-configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Backup & Restore](#backup--restore)
9. [Monitoring & Logging](#monitoring--logging)
10. [Security Hardening](#security-hardening)

---

## Deployment Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                       Production Server                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Nginx     │  │    React     │  │   Metabase   │          │
│  │  (Port 80)   │  │  (Port 5173) │  │  (Port 3000) │          │
│  │              │  │              │  │              │          │
│  │  - Reverse   │  │  - Dashboard │  │  - BI Engine │          │
│  │    Proxy     │  │  - Charts    │  │  - Queries   │          │
│  │  - SSL/TLS   │  │  - Filters   │  │  - Caching   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │  TimescaleDB    │                           │
│                   │  (Port 5433)    │                           │
│                   │                 │                           │
│                   │  - QoS Data     │                           │
│                   │  - Time-series  │                           │
│                   └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### Network Ports

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| Nginx | 80, 443 | 80, 443 | Reverse proxy, SSL termination |
| React | 5173 | 5180 | Frontend dashboard |
| Metabase | 3000 | 3000 | BI tool |
| TimescaleDB | 5432 | 5433 | Database |
| Custom Dashboard | 9000 | 9000 | HTML wrapper |

---

## Prerequisites

### Server Requirements

**Minimum Specifications**:
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 22.04 LTS or later

**Recommended Specifications**:
- **CPU**: 8 cores
- **RAM**: 16 GB
- **Storage**: 100 GB SSD
- **OS**: Ubuntu 22.04 LTS

### Software Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Install Node.js 22 (for local builds)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx (for reverse proxy)
sudo apt install nginx

# Install certbot (for SSL)
sudo apt install certbot python3-certbot-nginx

# Verify installations
docker --version
docker compose version
node --version
nginx -v
certbot --version
```

---

## Development Deployment

### Step 1: Clone Repository

```bash
# Clone project
cd /home/alamin/Desktop/Python\ Projects
git clone <repository-url> BTRC-QoS-Monitoring-Dashboard-V3
cd BTRC-QoS-Monitoring-Dashboard-V3
```

### Step 2: Environment Configuration

Create `.env` in project root:

```bash
# Database
POSTGRES_USER=btrc_admin
POSTGRES_PASSWORD=btrc_poc_2026
POSTGRES_DB=btrc_qos_poc

# Metabase
METABASE_ADMIN_EMAIL=alamin.technometrics22@gmail.com
METABASE_ADMIN_PASSWORD=Test@123

# React
VITE_METABASE_URL=http://localhost:3000
```

### Step 3: Start Services

```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f

# Verify services are running
docker compose ps

# Expected output:
# NAME                    STATUS
# btrc-v3-timescaledb    Up (healthy)
# btrc-v3-metabase       Up (healthy)
# btrc-v3-react-regional Up (healthy)
# btrc-v3-nginx          Up (healthy)
```

### Step 4: Access Dashboards

- **React Dashboard**: http://localhost:5180
- **Metabase**: http://localhost:3000
- **Custom Wrapper**: http://localhost:9000
- **Database**: localhost:5433 (use pgAdmin or DBeaver)

---

## Production Deployment

### Step 1: Build Production Images

```bash
# Build React production bundle
cd btrc-react-regional
yarn install
yarn build

# Output: dist/ directory with optimized assets

# Build Docker images for production
docker compose -f docker-compose.prod.yml build
```

### Step 2: Production docker-compose.yml

Create `docker-compose.prod.yml`:

```yaml
services:
  timescaledb:
    image: timescale/timescaledb-ha:pg15-latest
    container_name: btrc-v3-timescaledb-prod
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5433:5432"
    volumes:
      - timescale_data_prod:/home/postgres/pgdata/data
    networks:
      - btrc-v3-prod

  metabase:
    image: metabase/metabase:latest
    container_name: btrc-v3-metabase-prod
    restart: always
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: metabase_meta
      MB_DB_PORT: 5432
      MB_DB_USER: ${POSTGRES_USER}
      MB_DB_PASS: ${POSTGRES_PASSWORD}
      MB_DB_HOST: timescaledb
      MB_JETTY_PORT: 3000
      JAVA_TIMEZONE: Asia/Dhaka
      # Production settings
      MB_ENABLE_PUBLIC_SHARING: false
      MB_ANON_TRACKING_ENABLED: false
    ports:
      - "3000:3000"
    volumes:
      - metabase_data_prod:/metabase-data
    depends_on:
      - timescaledb
    networks:
      - btrc-v3-prod

  react-regional:
    build:
      context: ./btrc-react-regional
      dockerfile: Dockerfile
      target: production  # Use production stage
    container_name: btrc-v3-react-prod
    restart: always
    ports:
      - "80:80"
    networks:
      - btrc-v3-prod

  nginx:
    image: nginx:1.25-alpine
    container_name: btrc-v3-nginx-prod
    restart: always
    ports:
      - "9000:9000"
    volumes:
      - ./public:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro  # SSL certificates
    networks:
      - btrc-v3-prod

volumes:
  timescale_data_prod:
  metabase_data_prod:

networks:
  btrc-v3-prod:
    driver: bridge
```

### Step 3: Production Environment Variables

Create `.env.prod`:

```bash
# Database (use strong passwords in production!)
POSTGRES_USER=btrc_admin
POSTGRES_PASSWORD=<STRONG_PASSWORD_HERE>
POSTGRES_DB=btrc_qos_poc

# Metabase
METABASE_ADMIN_EMAIL=admin@btrc.gov.bd
METABASE_ADMIN_PASSWORD=<STRONG_PASSWORD_HERE>

# Domain
DOMAIN=dashboard.btrc.gov.bd
```

### Step 4: Deploy to Production

```bash
# Stop development services
docker compose down

# Start production services
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## Docker Deployment

### Understanding Docker Compose

The project uses multi-stage Docker builds:

**Development Stage**:
- Hot Module Reload (HMR) enabled
- Source code mounted as volume
- Fast rebuilds

**Production Stage**:
- Optimized bundle (minified, tree-shaken)
- Static files served via Nginx
- No source code in image

### Docker Commands Reference

```bash
# Build all services
docker compose build

# Build specific service
docker compose build react-regional

# Start services in background
docker compose up -d

# Start services with logs
docker compose up

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# View logs
docker compose logs -f react-regional

# Execute command in container
docker compose exec react-regional sh
docker compose exec timescaledb psql -U btrc_admin -d btrc_qos_poc

# Rebuild without cache
docker compose build --no-cache

# Scale service (e.g., 3 instances of React)
docker compose up -d --scale react-regional=3

# List running containers
docker ps

# View container stats (CPU, RAM)
docker stats
```

### Health Checks

All services have health checks defined:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 10
  start_period: 120s
```

View health status:
```bash
docker inspect btrc-v3-metabase | grep -A 10 Health
```

---

## Server Configuration

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/btrc-dashboard`:

```nginx
# HTTP server (redirect to HTTPS)
server {
    listen 80;
    server_name dashboard.btrc.gov.bd;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name dashboard.btrc.gov.bd;

    # SSL certificates
    ssl_certificate /etc/nginx/ssl/btrc-dashboard.crt;
    ssl_certificate_key /etc/nginx/ssl/btrc-dashboard.key;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # React Dashboard (main entry)
    location / {
        proxy_pass http://localhost:5180;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Metabase (BI Tool)
    location /metabase/ {
        proxy_pass http://localhost:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Custom Dashboard Wrapper
    location /wrapper/ {
        proxy_pass http://localhost:9000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Logs
    access_log /var/log/nginx/btrc-dashboard-access.log;
    error_log /var/log/nginx/btrc-dashboard-error.log;
}
```

Enable site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/btrc-dashboard /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Firewall Configuration

```bash
# Allow HTTP, HTTPS, SSH
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Block direct access to internal ports (optional)
sudo ufw deny 3000/tcp  # Metabase (only via Nginx)
sudo ufw deny 5173/tcp  # React (only via Nginx)
sudo ufw deny 5433/tcp  # Database (only from localhost)

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt (Free, Auto-Renewal)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d dashboard.btrc.gov.bd

# Certbot will:
# 1. Verify domain ownership
# 2. Generate SSL certificate
# 3. Update Nginx config
# 4. Set up auto-renewal

# Test auto-renewal
sudo certbot renew --dry-run

# Certificates location:
# /etc/letsencrypt/live/dashboard.btrc.gov.bd/fullchain.pem
# /etc/letsencrypt/live/dashboard.btrc.gov.bd/privkey.pem
```

### Option 2: Custom SSL Certificate

```bash
# Generate self-signed certificate (for testing)
sudo mkdir /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/btrc-dashboard.key \
  -out /etc/nginx/ssl/btrc-dashboard.crt

# For production, use certificate from CA (e.g., Sectigo, DigiCert)

# Update Nginx config with certificate paths
ssl_certificate /etc/nginx/ssl/btrc-dashboard.crt;
ssl_certificate_key /etc/nginx/ssl/btrc-dashboard.key;
```

### SSL Best Practices

```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;

# HSTS (force HTTPS)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/chain.pem;
```

---

## Backup & Restore

### Database Backup

```bash
# Manual backup
docker compose exec timescaledb pg_dump \
  -U btrc_admin \
  -d btrc_qos_poc \
  -F c \
  -f /tmp/backup_$(date +%Y%m%d_%H%M%S).dump

# Copy backup out of container
docker cp btrc-v3-timescaledb:/tmp/backup_20260216_120000.dump ./backups/

# Automated daily backup (cron job)
# Edit crontab: crontab -e
# Add line:
0 2 * * * /home/alamin/scripts/backup_database.sh
```

Create `~/scripts/backup_database.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/alamin/backups/btrc-dashboard"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="btrc_qos_backup_${DATE}.dump"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T timescaledb pg_dump \
  -U btrc_admin \
  -d btrc_qos_poc \
  -F c \
  > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.dump.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

Make executable:
```bash
chmod +x ~/scripts/backup_database.sh
```

### Database Restore

```bash
# Copy backup into container
docker cp ./backups/btrc_qos_backup_20260216.dump btrc-v3-timescaledb:/tmp/

# Restore database
docker compose exec timescaledb pg_restore \
  -U btrc_admin \
  -d btrc_qos_poc \
  -c \
  -F c \
  /tmp/btrc_qos_backup_20260216.dump
```

### Metabase Backup

```bash
# Backup Metabase metadata
docker compose exec metabase-db pg_dump \
  -U btrc_admin \
  -d metabase_meta \
  -F c \
  -f /tmp/metabase_meta_backup_$(date +%Y%m%d).dump

# Copy out of container
docker cp btrc-v3-timescaledb:/tmp/metabase_meta_backup_20260216.dump ./backups/
```

### Volume Backup

```bash
# Backup Docker volumes
docker run --rm \
  -v btrc-v3_timescale_data:/source:ro \
  -v $(pwd)/backups:/backup \
  ubuntu tar czf /backup/timescale_data_$(date +%Y%m%d).tar.gz -C /source .

# Restore Docker volume
docker run --rm \
  -v btrc-v3_timescale_data:/target \
  -v $(pwd)/backups:/backup \
  ubuntu tar xzf /backup/timescale_data_20260216.tar.gz -C /target
```

---

## Monitoring & Logging

### Docker Logs

```bash
# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f react-regional

# Last 100 lines
docker compose logs --tail=100 metabase

# Since timestamp
docker compose logs --since 2026-02-16T10:00:00 timescaledb
```

### Application Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/btrc-dashboard-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/btrc-dashboard-error.log

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u docker -f
```

### Monitoring Tools

Install monitoring stack:

```bash
# Prometheus + Grafana (optional)
docker run -d --name prometheus -p 9090:9090 prom/prometheus
docker run -d --name grafana -p 3001:3000 grafana/grafana
```

### Health Check Script

Create `~/scripts/health_check.sh`:

```bash
#!/bin/bash

# Check if all services are healthy
SERVICES=("btrc-v3-timescaledb" "btrc-v3-metabase" "btrc-v3-react-regional")

for service in "${SERVICES[@]}"; do
  status=$(docker inspect --format='{{.State.Health.Status}}' $service 2>/dev/null)

  if [ "$status" != "healthy" ]; then
    echo "⚠️  $service is not healthy: $status"
    # Send alert (email, Slack, etc.)
  else
    echo "✅ $service is healthy"
  fi
done
```

Run every 5 minutes:
```bash
# crontab -e
*/5 * * * * /home/alamin/scripts/health_check.sh >> /var/log/btrc-health-check.log 2>&1
```

---

## Security Hardening

### 1. Change Default Passwords

```bash
# Generate strong passwords
openssl rand -base64 32

# Update .env.prod with strong passwords
POSTGRES_PASSWORD=<GENERATED_PASSWORD>
METABASE_ADMIN_PASSWORD=<GENERATED_PASSWORD>
```

### 2. Database Security

```sql
-- Connect to database
psql -U btrc_admin -d btrc_qos_poc

-- Create read-only user for Metabase
CREATE USER metabase_readonly WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE btrc_qos_poc TO metabase_readonly;
GRANT USAGE ON SCHEMA public TO metabase_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metabase_readonly;

-- Revoke unnecessary privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

### 3. Metabase Security

```bash
# In docker-compose.prod.yml
environment:
  # Disable public sharing
  MB_ENABLE_PUBLIC_SHARING: false

  # Disable anonymous tracking
  MB_ANON_TRACKING_ENABLED: false

  # Enable HTTPS-only cookies
  MB_SESSION_COOKIES: "SameSite=Strict; Secure"
```

### 4. Docker Security

```bash
# Run containers as non-root user
# In Dockerfile:
USER node

# Limit container resources
# In docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### 5. Network Security

```bash
# Use internal Docker networks
networks:
  btrc-v3-prod:
    driver: bridge
    internal: true  # No external access

# Expose only Nginx to internet
```

### 6. Regular Updates

```bash
# Update Docker images
docker compose pull
docker compose up -d

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Node.js dependencies
cd btrc-react-regional
yarn upgrade
```

---

## Performance Tuning

### Nginx Optimization

```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

# Enable caching
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### React Build Optimization

```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'charts': ['echarts', 'echarts-for-react'],
          'ui': ['antd'],
        },
      },
    },
  },
})
```

### Database Optimization

```sql
-- Create indexes on frequently queried columns
CREATE INDEX idx_measurements_timestamp ON ts_qos_measurements(timestamp);
CREATE INDEX idx_measurements_division ON ts_qos_measurements(division);
CREATE INDEX idx_measurements_district ON ts_qos_measurements(district);

-- Vacuum and analyze
VACUUM ANALYZE ts_qos_measurements;
```

---

## Troubleshooting Deployment

See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) for detailed solutions.

---

## Next Steps

1. **Read**: [Development Workflow Guide](./DEVELOPMENT_WORKFLOW.md)
2. **Read**: [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)
3. **Monitor**: Set up monitoring and alerting
4. **Test**: Perform load testing and security audits

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Metabase Deployment Guide](https://www.metabase.com/docs/latest/operations-guide/start)
