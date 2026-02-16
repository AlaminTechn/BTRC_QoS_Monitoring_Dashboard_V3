# Quick Extract & Run Guide

## 📦 Extract Archive

```bash
# Extract the archive
tar -xzf btrc-dashboard-v3-updated-20260210-165321.tar.gz

# Navigate to directory
cd BTRC-QoS-Monitoring-Dashboard-V3
```

---

## 🚀 Start Dashboard

### **Option 1: Quick Start (Recommended)**

```bash
# Start all services
docker-compose up -d

# Wait 2 minutes for services to start
# Then open browser to:
# http://localhost:3000
```

### **Option 2: With Logs (For debugging)**

```bash
# Start with logs visible
docker-compose up

# Press Ctrl+C to stop
```

---

## 🌐 Access URLs

### **Metabase Dashboard**
```
http://localhost:3000
```
**Login:** alamin.technometrics22@gmail.com / Test@123

### **Public Links (No Login Required)**

**Executive Dashboard:**
```
http://localhost:3000/public/dashboard/54733c64-24e2-4977-9d2f-2ed086219635
```

**Regulatory Dashboard:**
```
http://localhost:3000/public/dashboard/bac7ee8a-62d3-422f-a1e9-123673b52c5f
```

### **Custom Wrapper (Drill-down Navigation)**
```
http://localhost:8080/dashboard
```

---

## 📊 Verify Data

### **Check Database**

```bash
# Connect to database
docker exec -it btrc-v3-timescaledb psql -U btrc_admin -d btrc_qos_poc

# Run test queries
\dt  -- List tables

SELECT COUNT(*) FROM ts_qos_measurements;
-- Should return: 172800

SELECT COUNT(*) FROM isps;
-- Should return: 40

SELECT COUNT(*) FROM pops;
-- Should return: 120

\q  -- Exit
```

---

## 🛑 Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 🔧 Troubleshooting

### **Port Already in Use**

If port 3000 or 5433 is already in use:

Edit `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change 3000 to 3001
```

### **Services Not Starting**

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs metabase
docker-compose logs timescaledb

# Restart specific service
docker-compose restart metabase
```

### **Database Connection Error**

Wait 2-3 minutes for TimescaleDB to fully initialize before Metabase connects.

---

## 📱 Share with Team (LAN)

**Find your IP address:**
```bash
hostname -I | awk '{print $1}'
```

**Share links with your IP:**
```
http://YOUR_IP:3000/public/dashboard/54733c64-24e2-4977-9d2f-2ed086219635
http://YOUR_IP:3000/public/dashboard/bac7ee8a-62d3-422f-a1e9-123673b52c5f
```

Replace `YOUR_IP` with the IP from command above.

---

## 📚 Documentation

- **User Guide:** `DASHBOARD_USER_GUIDE.md`
- **Deployment:** `DEPLOYMENT_GUIDE.md`
- **Sharing:** `SHARING_MESSAGE.md`
- **Remote Access:** `INTERNET_ACCESS_SETUP.md`

---

## ✅ Success Checklist

After extraction and startup:

- [ ] Docker services running (3 containers)
- [ ] Metabase accessible at localhost:3000
- [ ] Database has 172,800 measurements
- [ ] Public links work without login
- [ ] Filters work (Division, District, ISP)
- [ ] Maps display correctly

---

**Total Time:** ~5 minutes from extraction to running dashboard

**Next:** Open `DASHBOARD_USER_GUIDE.md` for full feature guide
