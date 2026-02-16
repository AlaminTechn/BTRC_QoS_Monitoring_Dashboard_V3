# BTRC QoS Dashboard - Quick Start Guide

**🚀 Get your dashboard running in 5 minutes!**

---

## 📦 What You Need

- Ubuntu 20.04+ server
- 4GB RAM minimum (8GB recommended)
- 50GB storage
- SSH access with sudo privileges

---

## 🎯 Option 1: Automated Deployment (Recommended)

### Step 1: Transfer Files to Server

**On your local machine:**

```bash
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3"

# Create deployment package
tar -czf btrc-dashboard.tar.gz \
    --exclude='node_modules' \
    --exclude='.git' \
    .

# Transfer to server
scp btrc-dashboard.tar.gz your-user@your-server-ip:/home/your-user/
```

### Step 2: Extract on Server

**On your server:**

```bash
# Extract files
mkdir -p /opt/btrc-qos-dashboard
cd /opt/btrc-qos-dashboard
tar -xzf ~/btrc-dashboard.tar.gz
```

### Step 3: Run Deployment Script

```bash
# Make script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**That's it!** The script will:
- ✅ Check dependencies
- ✅ Install Docker (if needed)
- ✅ Create secure passwords
- ✅ Configure firewall
- ✅ Start all services
- ✅ Verify deployment

### Step 4: Access Dashboard

```
http://your-server-ip:3000
```

**Login:**
- Email: `alamin.technometrics22@gmail.com`
- Password: `Test@123` ⚠️ **Change immediately!**

---

## 🎯 Option 2: Manual Deployment

### Step 1: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Start Services

```bash
cd /opt/btrc-qos-dashboard

# Start services
docker compose up -d

# Check status
docker ps
```

### Step 3: Wait for Services (2-3 minutes)

```bash
# Check Metabase health
curl http://localhost:3000/api/health

# Should return: {"status":"ok"}
```

---

## 📊 Access Your Dashboards

### Executive Dashboard
```
http://your-server-ip:3000/dashboard/5
```

### Regulatory Dashboard
```
http://your-server-ip:3000/dashboard/6
```

### Custom Wrapper (with breadcrumb)
```
http://your-server-ip:8080/dashboard
```

---

## 🔐 Security Checklist

**Do these immediately:**

- [ ] Change Metabase password
- [ ] Update `.env` file passwords
- [ ] Configure firewall (ports: 22, 3000, 8080)
- [ ] Set up SSL/HTTPS (see DEPLOYMENT_GUIDE.md)
- [ ] Schedule backups
- [ ] Test backup/restore

---

## 🔧 Common Commands

### View Logs
```bash
docker compose logs -f
```

### Restart Services
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Backup Database
```bash
./backup.sh
```

### Check Service Status
```bash
docker ps
```

---

## 🆘 Troubleshooting

### Services Won't Start

```bash
# Check Docker
sudo systemctl status docker

# Check logs
docker compose logs

# Restart Docker
sudo systemctl restart docker
docker compose up -d
```

### Can't Access Dashboard

```bash
# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 3000/tcp
sudo ufw allow 8080/tcp

# Check if services are running
docker ps
```

### Database Connection Error

```bash
# Check PostgreSQL
docker exec btrc-v3-timescaledb pg_isready -U btrc_admin

# Restart database
docker restart btrc-v3-timescaledb
```

---

## 📚 Full Documentation

- **User Guide**: `DASHBOARD_USER_GUIDE.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Configuration**: `README.md`

---

## 🎯 Next Steps

1. **Change passwords** ⚠️
2. **Set up SSL** (see DEPLOYMENT_GUIDE.md)
3. **Configure backups** (automatic via cron)
4. **Test drill-down** (click divisions/districts)
5. **Import production data**

---

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Review DEPLOYMENT_GUIDE.md
3. Check Docker logs: `docker compose logs`

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Can access http://your-server-ip:3000
- [ ] Can login to Metabase
- [ ] Executive Dashboard (5) loads
- [ ] Regulatory Dashboard (6) loads
- [ ] Drill-down works (click divisions)
- [ ] Browser back button works
- [ ] Custom wrapper works (port 8080)
- [ ] Database is accessible
- [ ] Backups are configured

---

**🎉 Congratulations! Your BTRC QoS Dashboard is ready!**

Access: `http://your-server-ip:3000`
