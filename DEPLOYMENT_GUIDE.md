# BTRC QoS Dashboard - Server Deployment Guide

**Version:** 3.0 POC
**Date:** 2026-02-09
**Target:** Production Server Deployment

---

## 📋 Table of Contents

1. [Server Requirements](#server-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Step 1: Server Preparation](#step-1-server-preparation)
4. [Step 2: Install Dependencies](#step-2-install-dependencies)
5. [Step 3: Transfer Project Files](#step-3-transfer-project-files)
6. [Step 4: Configure Environment](#step-4-configure-environment)
7. [Step 5: Deploy Services](#step-5-deploy-services)
8. [Step 6: Configure Firewall](#step-6-configure-firewall)
9. [Step 7: Set Up Domain & SSL (Optional)](#step-7-set-up-domain--ssl-optional)
10. [Step 8: Verify Deployment](#step-8-verify-deployment)
11. [Step 9: Backup Configuration](#step-9-backup-configuration)
12. [Maintenance & Updates](#maintenance--updates)
13. [Troubleshooting](#troubleshooting)

---

## 🖥️ Server Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4 cores |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 50 GB | 100 GB SSD |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| **Network** | 10 Mbps | 100 Mbps |
| **Ports** | 3000, 5433, 8080 | Open as needed |

### Software Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (for version control)
- Nginx (optional, for reverse proxy)
- Certbot (optional, for SSL)

### Network Requirements

- **Static IP** or reserved DHCP lease
- **Domain name** (optional but recommended)
- **Firewall access** to open required ports
- **Internet access** for Docker image pulls

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Server access (SSH with sudo privileges)
- [ ] Server meets minimum requirements
- [ ] Backup of current local database
- [ ] Backup of Metabase configurations
- [ ] Domain name configured (optional)
- [ ] SSL certificate or plan to use Let's Encrypt
- [ ] Firewall rules documented
- [ ] Production credentials ready
- [ ] Monitoring tools identified
- [ ] Maintenance schedule planned

---

## Step 1: Server Preparation

### 1.1. Connect to Server

```bash
# SSH into your server
ssh your-username@your-server-ip

# Example:
ssh ubuntu@192.168.1.100
```

### 1.2. Update System

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git vim htop net-tools
```

### 1.3. Create Application User (Recommended)

```bash
# Create dedicated user for BTRC app
sudo useradd -m -s /bin/bash btrc
sudo usermod -aG sudo btrc

# Set password
sudo passwd btrc

# Switch to btrc user
su - btrc
```

### 1.4. Create Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/btrc-qos-dashboard
sudo chown btrc:btrc /opt/btrc-qos-dashboard
cd /opt/btrc-qos-dashboard
```

---

## Step 2: Install Dependencies

### 2.1. Install Docker

```bash
# Remove old Docker versions (if any)
sudo apt remove docker docker-engine docker.io containerd runc

# Install Docker dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2.2. Configure Docker Permissions

```bash
# Add user to docker group
sudo usermod -aG docker btrc

# Apply group changes (logout and login again, or run):
newgrp docker

# Verify Docker works without sudo
docker ps
```

### 2.3. Configure Docker for Production

```bash
# Create Docker daemon config
sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

# Restart Docker
sudo systemctl restart docker
sudo systemctl enable docker
```

---

## Step 3: Transfer Project Files

### Method A: Direct Transfer from Local Machine

```bash
# On your LOCAL machine, from project directory:
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3"

# Create deployment archive (exclude unnecessary files)
tar -czf btrc-qos-dashboard.tar.gz \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='.env.local' \
    .

# Transfer to server
scp btrc-qos-dashboard.tar.gz btrc@your-server-ip:/opt/btrc-qos-dashboard/

# On SERVER:
cd /opt/btrc-qos-dashboard
tar -xzf btrc-qos-dashboard.tar.gz
rm btrc-qos-dashboard.tar.gz
```

### Method B: Git Clone (if using Git repository)

```bash
# On SERVER:
cd /opt/btrc-qos-dashboard

# Clone repository
git clone https://github.com/your-org/btrc-qos-dashboard.git .

# Or if using private repo:
git clone https://username:token@github.com/your-org/btrc-qos-dashboard.git .
```

### 3.1. Verify Files

```bash
# List directory structure
ls -la

# Should see:
# - docker-compose.yml
# - nginx.conf
# - public/
# - docker/
# - *.py (configuration scripts)
# - *.md (documentation)
```

---

## Step 4: Configure Environment

### 4.1. Create Production Environment File

```bash
# Create .env file for production
cat > .env <<EOF
# PostgreSQL / TimescaleDB Configuration
POSTGRES_USER=btrc_admin
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=btrc_qos_poc

# Metabase Configuration
MB_DB_TYPE=postgres
MB_DB_DBNAME=metabase_meta
MB_DB_USER=btrc_admin
MB_DB_PASS=$(openssl rand -base64 32)
MB_JETTY_PORT=3000
JAVA_TIMEZONE=Asia/Dhaka

# Nginx Configuration
NGINX_PORT=8080

# Application
APP_ENV=production
APP_DEBUG=false

# Monitoring (optional)
ENABLE_MONITORING=true

# Backup Configuration
BACKUP_DIR=/opt/btrc-qos-dashboard/backups
BACKUP_RETENTION_DAYS=30
EOF

# Secure the .env file
chmod 600 .env
```

**IMPORTANT**: Save the generated passwords securely!

### 4.2. Update docker-compose.yml for Production

```bash
# Backup original
cp docker-compose.yml docker-compose.yml.backup

# Update for production (adjust ports if needed)
# This assumes you'll use nginx reverse proxy
```

Create production docker-compose.yml:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb-ha:pg15-latest
    container_name: btrc-v3-timescaledb
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5433:5432"
    volumes:
      - timescale_data:/home/postgres/pgdata/data
      - ./docker/timescaledb/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - btrc-v3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  metabase:
    image: metabase/metabase:latest
    container_name: btrc-v3-metabase
    restart: always
    environment:
      MB_DB_TYPE: ${MB_DB_TYPE}
      MB_DB_DBNAME: ${MB_DB_DBNAME}
      MB_DB_PORT: 5432
      MB_DB_USER: ${MB_DB_USER}
      MB_DB_PASS: ${MB_DB_PASS}
      MB_DB_HOST: timescaledb
      MB_JETTY_PORT: ${MB_JETTY_PORT}
      JAVA_TIMEZONE: ${JAVA_TIMEZONE}
      MB_EMBEDDING_APP_ORIGIN: "http://your-server-ip:8080"
    ports:
      - "3000:3000"
    volumes:
      - metabase_data:/metabase-data
    depends_on:
      timescaledb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 120s
    networks:
      - btrc-v3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: btrc-v3-nginx
    restart: always
    ports:
      - "8080:80"
    volumes:
      - ./public:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - metabase
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - btrc-v3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  timescale_data:
  metabase_data:

networks:
  btrc-v3:
    driver: bridge
```

---

## Step 5: Deploy Services

### 5.1. Create Required Directories

```bash
# Create backup directory
mkdir -p /opt/btrc-qos-dashboard/backups

# Create log directory
mkdir -p /opt/btrc-qos-dashboard/logs

# Set permissions
chmod 755 /opt/btrc-qos-dashboard/backups
chmod 755 /opt/btrc-qos-dashboard/logs
```

### 5.2. Pull Docker Images

```bash
cd /opt/btrc-qos-dashboard

# Pull images before starting (faster startup)
docker compose -f docker-compose.prod.yml pull
```

### 5.3. Start Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Wait for services to be healthy (2-3 minutes)
```

### 5.4. Verify Services

```bash
# Check running containers
docker ps

# Should see 3 containers:
# - btrc-v3-timescaledb (healthy)
# - btrc-v3-metabase (healthy)
# - btrc-v3-nginx (healthy)

# Check service health
docker compose -f docker-compose.prod.yml ps
```

---

## Step 6: Configure Firewall

### 6.1. UFW Firewall (Ubuntu)

```bash
# Install UFW if not present
sudo apt install -y ufw

# Allow SSH (IMPORTANT: Do this first!)
sudo ufw allow 22/tcp

# Allow Metabase
sudo ufw allow 3000/tcp

# Allow Custom Wrapper
sudo ufw allow 8080/tcp

# Allow PostgreSQL (if external access needed)
# sudo ufw allow 5433/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### 6.2. Cloud Provider Firewall

If using AWS, Azure, GCP, DigitalOcean, etc.:

**AWS Security Group:**
- Inbound: TCP 22 (SSH) from your IP
- Inbound: TCP 3000 (Metabase) from 0.0.0.0/0
- Inbound: TCP 8080 (Nginx) from 0.0.0.0/0
- Outbound: All traffic

**Azure Network Security Group:**
- Similar rules as AWS

**GCP Firewall Rules:**
- Similar rules as AWS

---

## Step 7: Set Up Domain & SSL (Optional)

### 7.1. Configure Domain DNS

Point your domain to server IP:

```
A Record:  btrc-qos.example.com → your-server-ip
A Record:  www.btrc-qos.example.com → your-server-ip
```

### 7.2. Install Nginx Reverse Proxy

```bash
# Install Nginx (separate from Docker nginx)
sudo apt install -y nginx

# Create configuration
sudo tee /etc/nginx/sites-available/btrc-qos <<EOF
server {
    listen 80;
    server_name btrc-qos.example.com www.btrc-qos.example.com;

    # Redirect to HTTPS (after SSL is set up)
    # return 301 https://\$host\$request_uri;

    # For now, proxy to Docker nginx
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Metabase direct access
    location /metabase/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/btrc-qos /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 7.3. Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d btrc-qos.example.com -d www.btrc-qos.example.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose to redirect HTTP to HTTPS

# Verify auto-renewal
sudo certbot renew --dry-run

# Certificate will auto-renew every 90 days
```

### 7.4. Update Docker Configuration for HTTPS

Update docker-compose.prod.yml:

```yaml
metabase:
  environment:
    MB_EMBEDDING_APP_ORIGIN: "https://btrc-qos.example.com"
```

Restart services:

```bash
docker compose -f docker-compose.prod.yml restart metabase
```

---

## Step 8: Verify Deployment

### 8.1. Access Dashboard

```bash
# Test locally first
curl http://localhost:3000/api/health

# Should return: {"status":"ok"}

# Test nginx wrapper
curl http://localhost:8080/health

# Should return: OK
```

### 8.2. Access from Browser

**Metabase Direct:**
- http://your-server-ip:3000

**Custom Wrapper:**
- http://your-server-ip:8080/dashboard

**With Domain:**
- https://btrc-qos.example.com

### 8.3. Login to Metabase

1. Navigate to Metabase URL
2. Login with credentials:
   - Email: alamin.technometrics22@gmail.com
   - Password: Test@123 (change this!)

3. Verify dashboards:
   - Dashboard 5: Executive
   - Dashboard 6: Regulatory

### 8.4. Test Drill-Down

1. Go to Regulatory Dashboard (Dashboard 6)
2. Tab R2.2: Regional Analysis
3. Click "Dhaka" in Division table
4. Verify URL changes and data filters
5. Test browser back button

---

## Step 9: Backup Configuration

### 9.1. Create Backup Script

```bash
# Create backup script
cat > /opt/btrc-qos-dashboard/backup.sh <<'EOF'
#!/bin/bash

# BTRC QoS Dashboard - Backup Script
# Run daily via cron

BACKUP_DIR="/opt/btrc-qos-dashboard/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "=== BTRC QoS Dashboard Backup - $TIMESTAMP ==="

# Create backup directory
mkdir -p "$BACKUP_DIR/db"
mkdir -p "$BACKUP_DIR/metabase"

# Backup PostgreSQL databases
echo "Backing up PostgreSQL..."
docker exec btrc-v3-timescaledb pg_dump -U btrc_admin btrc_qos_poc | \
    gzip > "$BACKUP_DIR/db/btrc_qos_poc_$TIMESTAMP.sql.gz"

docker exec btrc-v3-timescaledb pg_dump -U btrc_admin metabase_meta | \
    gzip > "$BACKUP_DIR/db/metabase_meta_$TIMESTAMP.sql.gz"

# Backup Metabase configuration
echo "Backing up Metabase data..."
docker cp btrc-v3-metabase:/metabase-data "$BACKUP_DIR/metabase/metabase-data_$TIMESTAMP"
tar -czf "$BACKUP_DIR/metabase/metabase-data_$TIMESTAMP.tar.gz" \
    -C "$BACKUP_DIR/metabase" "metabase-data_$TIMESTAMP"
rm -rf "$BACKUP_DIR/metabase/metabase-data_$TIMESTAMP"

# Backup docker-compose and configs
echo "Backing up configuration files..."
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" \
    /opt/btrc-qos-dashboard/docker-compose.prod.yml \
    /opt/btrc-qos-dashboard/nginx.conf \
    /opt/btrc-qos-dashboard/.env

# Remove old backups
echo "Cleaning old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $TIMESTAMP"
echo "Backup location: $BACKUP_DIR"

# List backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR/db" | tail -5
EOF

# Make executable
chmod +x /opt/btrc-qos-dashboard/backup.sh
```

### 9.2. Schedule Daily Backups

```bash
# Add to crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /opt/btrc-qos-dashboard/backup.sh >> /opt/btrc-qos-dashboard/logs/backup.log 2>&1
```

### 9.3. Test Backup

```bash
# Run backup manually
/opt/btrc-qos-dashboard/backup.sh

# Verify backups created
ls -lh /opt/btrc-qos-dashboard/backups/db/
ls -lh /opt/btrc-qos-dashboard/backups/metabase/
```

---

## Maintenance & Updates

### Update Docker Images

```bash
cd /opt/btrc-qos-dashboard

# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Restart with new images
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

### Update Application Code

```bash
# If using Git:
cd /opt/btrc-qos-dashboard
git pull origin main

# Restart services
docker compose -f docker-compose.prod.yml restart

# If transferred manually:
# 1. Create new tar.gz on local machine
# 2. Transfer to server
# 3. Extract and restart
```

### Monitor Disk Usage

```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up unused Docker resources
docker system prune -a --volumes
```

### Monitor Logs

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service
docker compose -f docker-compose.prod.yml logs -f metabase

# View last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

---

## Troubleshooting

### Issue: Services Won't Start

```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker compose -f docker-compose.prod.yml logs

# Check ports in use
sudo netstat -tulpn | grep -E ':(3000|5433|8080)'

# Restart Docker
sudo systemctl restart docker

# Restart services
docker compose -f docker-compose.prod.yml restart
```

### Issue: Can't Access Dashboard

```bash
# Check firewall
sudo ufw status

# Check if services are running
docker ps

# Check nginx logs
docker logs btrc-v3-nginx

# Test locally
curl http://localhost:3000/api/health
curl http://localhost:8080/health
```

### Issue: Database Connection Error

```bash
# Check PostgreSQL logs
docker logs btrc-v3-timescaledb

# Check if database is ready
docker exec btrc-v3-timescaledb pg_isready -U btrc_admin

# Connect to database
docker exec -it btrc-v3-timescaledb psql -U btrc_admin -d btrc_qos_poc
```

### Issue: Metabase Slow or Unresponsive

```bash
# Check memory usage
docker stats

# Check Metabase logs
docker logs btrc-v3-metabase --tail=100

# Increase memory (edit docker-compose.prod.yml)
# Add under metabase service:
#   deploy:
#     resources:
#       limits:
#         memory: 2G

# Restart Metabase
docker compose -f docker-compose.prod.yml restart metabase
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Configure firewall properly
- [ ] Restrict database access
- [ ] Enable Docker security features
- [ ] Regular backups scheduled
- [ ] Monitor system logs
- [ ] Keep Docker images updated
- [ ] Implement access controls
- [ ] Use strong passwords (20+ characters)
- [ ] Enable two-factor authentication (if available)
- [ ] Regular security audits

---

## Performance Tuning

### PostgreSQL/TimescaleDB

```sql
-- Connect to database
docker exec -it btrc-v3-timescaledb psql -U btrc_admin -d btrc_qos_poc

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Metabase

- Increase Java heap size if needed
- Schedule question caching
- Archive old queries
- Optimize slow queries

---

## Monitoring Setup (Optional)

### Install Prometheus + Grafana

```bash
# Add monitoring stack to docker-compose
# See separate monitoring guide for details
```

### Basic Monitoring with cron

```bash
# Create monitoring script
cat > /opt/btrc-qos-dashboard/monitor.sh <<'EOF'
#!/bin/bash
# Check if services are running
docker ps --filter "name=btrc-v3" --format "{{.Names}}: {{.Status}}" | mail -s "BTRC Dashboard Status" admin@example.com
EOF

chmod +x /opt/btrc-qos-dashboard/monitor.sh

# Run every hour
crontab -e
# Add: 0 * * * * /opt/btrc-qos-dashboard/monitor.sh
```

---

## Quick Reference Commands

```bash
# Start services
docker compose -f docker-compose.prod.yml up -d

# Stop services
docker compose -f docker-compose.prod.yml down

# Restart services
docker compose -f docker-compose.prod.yml restart

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Check status
docker compose -f docker-compose.prod.yml ps

# Backup database
docker exec btrc-v3-timescaledb pg_dump -U btrc_admin btrc_qos_poc > backup.sql

# Restore database
docker exec -i btrc-v3-timescaledb psql -U btrc_admin -d btrc_qos_poc < backup.sql

# Access Metabase shell
docker exec -it btrc-v3-metabase /bin/bash

# Access PostgreSQL
docker exec -it btrc-v3-timescaledb psql -U btrc_admin -d btrc_qos_poc
```

---

## Support & Contacts

### For Deployment Issues:
- System Administrator: [Contact]
- DevOps Team: [Contact]

### For Application Issues:
- Technical Lead: [Contact]
- Database Admin: [Contact]

---

**Deployment Guide Complete**

Your BTRC QoS Dashboard should now be running on your production server!

Access URLs:
- **Metabase**: http://your-server-ip:3000
- **Custom Wrapper**: http://your-server-ip:8080/dashboard
- **With Domain**: https://btrc-qos.example.com

For usage instructions, see `DASHBOARD_USER_GUIDE.md`.
