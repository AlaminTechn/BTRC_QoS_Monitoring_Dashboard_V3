# Docker Auto-Initialization Guide

**Automatic User & Permission Setup on Container Start**

---

## 🎯 Overview

The BTRC Dashboard now automatically initializes users and permissions when Docker containers start. No manual script execution required!

### **What Gets Created Automatically:**
- ✅ 5 User Groups (with proper permissions)
- ✅ 9 Sample Users (different roles)
- ✅ Data Permissions (database access control)
- ✅ Collection Permissions (dashboard access control)
- ✅ Proper admin access (can see Admin menu)
- ✅ Restricted external access (no SQL queries)

---

## 🐳 Docker Setup

### **Services**
```
1. timescaledb     - PostgreSQL 15 + TimescaleDB
2. metabase        - Metabase v0.58.5
3. nginx           - Nginx 1.25 (reverse proxy)
4. metabase-init   - Python 3.10 (user initialization)
```

### **Initialization Flow**
```
Docker Start
    ↓
TimescaleDB Ready (5-10 seconds)
    ↓
Metabase Starts (60-120 seconds)
    ↓
Metabase Healthy
    ↓
metabase-init Service Runs (10-20 seconds)
    ↓
Users & Permissions Created ✅
    ↓
System Ready!
```

---

## 🚀 Quick Start

### **First Time Setup**

```bash
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3"

# Build the init container
docker-compose build metabase-init

# Start all services
docker-compose up -d

# Watch initialization progress
docker-compose logs -f metabase-init
```

**Expected Output:**
```
metabase-init | ==================================
metabase-init | Metabase User Initialization
metabase-init | ==================================
metabase-init | Waiting for Metabase to be ready...
metabase-init | ✅ Metabase is ready
metabase-init | Running user setup script...
metabase-init | ✅ Created users:
metabase-init | ✅ User initialization complete!
```

### **Check Status**

```bash
# Check all containers
docker-compose ps

# Should show:
# btrc-v3-timescaledb   - Up (healthy)
# btrc-v3-metabase      - Up (healthy)
# btrc-v3-nginx         - Up
# btrc-v3-metabase-init - Exited (0)  ← This is normal!
```

**Note:** `metabase-init` exits after completing. This is expected!

---

## 👥 Users Created Automatically

### **🔴 Administrators (Full Access)**
```
admin@btrc.gov.bd         / Admin@123!
it.manager@btrc.gov.bd    / ITMgr@123!
```
**Permissions:**
- ✅ See "Admin" menu
- ✅ Manage users and settings
- ✅ Create/edit dashboards
- ✅ Write SQL queries
- ✅ Full database access

---

### **🟢 Management Team (View Only)**
```
ceo@btrc.gov.bd  / CEO@123!
cto@btrc.gov.bd  / CTO@123!
```
**Permissions:**
- ✅ View all dashboards
- ✅ Use filters
- ✅ Export data
- ✅ Query Builder (GUI only)
- ❌ No "Admin" menu
- ❌ Cannot write SQL
- ❌ Cannot create dashboards

---

### **🟡 Operations Team (Analysts)**
```
pm@btrc.gov.bd       / PM@123!
analyst@btrc.gov.bd  / Analyst@123!
```
**Permissions:**
- ✅ View dashboards
- ✅ Write SQL queries
- ✅ Create dashboards (in own collection)
- ✅ Full database read access
- ❌ No "Admin" menu
- ❌ Cannot manage users

---

### **🔵 Regional Officers (Query Builder Only)**
```
dhaka.officer@btrc.gov.bd      / Dhaka@123!
chittagong.officer@btrc.gov.bd / Chittagong@123!
```
**Permissions:**
- ✅ View dashboards
- ✅ Use filters
- ✅ Query Builder (GUI only)
- ❌ Cannot write SQL
- ❌ Cannot create dashboards

---

### **⚪ External Viewers (No Database Access)**
```
consultant@example.com  / Consult@123!
```
**Permissions:**
- ❌ Cannot access database
- ❌ Cannot write SQL
- ❌ Cannot create questions
- ⚠️ Can only view via public shared links

---

## 🧪 Testing Permissions

### **Test 1: Admin Access** ✅

```bash
# Login Details
URL: http://localhost:3000
Email: admin@btrc.gov.bd
Password: Admin@123!
```

**Expected:**
- ✅ See "Admin" gear icon (top right)
- ✅ Can access Admin Settings
- ✅ Click "+ New" → Question → Native Query (SQL editor appears)
- ✅ Can edit dashboards
- ✅ Can manage users (Admin Settings → People)

**If NOT working:**
```bash
# Re-run initialization
docker-compose restart metabase-init
docker-compose logs -f metabase-init
```

---

### **Test 2: Management View-Only** ✅

```bash
# Login Details
Email: ceo@btrc.gov.bd
Password: CEO@123!
```

**Expected:**
- ❌ No "Admin" gear icon
- ✅ Can see dashboards
- ✅ Click "+ New" → Question → Simple Question (GUI query builder)
- ❌ No "Native Query" option
- ❌ Cannot edit dashboards (no pencil icon)

---

### **Test 3: Operations SQL Access** ✅

```bash
# Login Details
Email: analyst@btrc.gov.bd
Password: Analyst@123!
```

**Expected:**
- ✅ Click "+ New" → Question → Native Query (SQL editor appears)
- ✅ Can write: `SELECT * FROM isps LIMIT 10`
- ✅ Can create and save questions
- ✅ Can create dashboards in personal collection
- ❌ No "Admin" menu

---

### **Test 4: External No Access** ✅

```bash
# Login Details
Email: consultant@example.com
Password: Consult@123!
```

**Expected:**
- ❌ Cannot see databases
- ❌ "+ New" button disabled or very limited
- ❌ Cannot access data browser
- ⚠️ Can only view public shared dashboard links

---

## 🔧 Troubleshooting

### **Problem: Init container failed**

```bash
# Check logs
docker-compose logs metabase-init

# Common issues:
# 1. Metabase not ready yet
# 2. Wrong admin credentials
# 3. Network connectivity
```

**Solution:**
```bash
# Restart init container
docker-compose restart metabase-init

# Or rebuild and restart
docker-compose build metabase-init
docker-compose up -d metabase-init
```

---

### **Problem: Admin user can't see Admin menu**

**Likely Cause:** User not in Administrators group (ID: 2)

**Solution:**
```bash
# Re-run initialization
docker-compose restart metabase-init

# Or manually via Metabase UI:
# 1. Login as alamin.technometrics22@gmail.com
# 2. Admin Settings → People
# 3. Find admin@btrc.gov.bd
# 4. Click user → Groups
# 5. Add to "Administrators" group
```

---

### **Problem: External user can write SQL**

**Likely Cause:** Permissions not set correctly

**Solution:**
```bash
# Re-run initialization
docker-compose restart metabase-init

# Verify in UI:
# 1. Login as admin
# 2. Admin Settings → Permissions → Data
# 3. Find "External Viewers" group
# 4. Ensure database is set to "No access"
```

---

### **Problem: Initialization hangs**

```bash
# Check if Metabase is healthy
docker-compose ps

# If metabase shows "starting" for > 2 minutes:
docker-compose restart metabase

# Then restart init
docker-compose restart metabase-init
```

---

## 🔄 Re-running Initialization

### **When to Re-run:**
- After resetting Metabase data
- After permission changes need to be reapplied
- After adding new user groups

### **How to Re-run:**

```bash
# Method 1: Restart init container
docker-compose restart metabase-init

# Method 2: Run manually
docker-compose run --rm metabase-init

# Method 3: Run script directly
python3 init_users_permissions.py
```

---

## 📝 Customizing Users

### **Add More Users**

Edit `init_users_permissions.py`:

```python
USERS = {
    "admins": [
        # Add more admins here
        {
            "first_name": "New",
            "last_name": "Admin",
            "email": "newadmin@btrc.gov.bd",
            "password": "NewPass@123!",
            "is_superuser": True,
        },
    ],
    # ... other groups
}
```

Then rebuild:
```bash
docker-compose build metabase-init
docker-compose up -d metabase-init
```

---

## 🐍 Container Version Compatibility

| Component | Version | Why |
|-----------|---------|-----|
| **Python** | 3.10-slim | Matches host system |
| **Requests** | 2.31.0 | Stable, well-tested |
| **Metabase** | v0.58.5 | Current running version |
| **TimescaleDB** | PG15 | Latest stable |

**See:** `CONTAINER_VERSIONS.md` for full details

---

## 📊 Permission Summary

| Feature | Admin | Management | Operations | Regional | External |
|---------|-------|------------|------------|----------|----------|
| **Admin Menu** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Write SQL** | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Query Builder** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Create Dashboards** | ✅ | ❌ | ✅ Own | ❌ | ❌ |
| **View Dashboards** | ✅ | ✅ | ✅ | ✅ | ⚠️ Public |
| **Export Data** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Manage Users** | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 📁 Files Created

```
BTRC-QoS-Monitoring-Dashboard-V3/
├── init_users_permissions.py          ← Main initialization script
├── docker/
│   ├── Dockerfile.init               ← Python 3.10 container
│   └── init-users.sh                 ← Shell wrapper script
├── docker-compose.yml                ← Updated with init service
├── DOCKER_AUTO_INIT_GUIDE.md         ← This guide
├── CONTAINER_VERSIONS.md             ← Version compatibility
└── PERMISSION_SCENARIOS_GUIDE.md     ← Detailed permissions
```

---

## ✅ Checklist

**Initial Setup:**
- [ ] Build init container: `docker-compose build metabase-init`
- [ ] Start services: `docker-compose up -d`
- [ ] Wait 2-3 minutes for initialization
- [ ] Check init logs: `docker-compose logs metabase-init`

**Testing:**
- [ ] Login as admin@btrc.gov.bd - See Admin menu
- [ ] Login as ceo@btrc.gov.bd - No Admin menu, view only
- [ ] Login as analyst@btrc.gov.bd - Can write SQL
- [ ] Login as consultant@example.com - No database access

**Verification:**
- [ ] Admin Settings → People → 9 users created
- [ ] Admin Settings → Permissions → Data permissions set
- [ ] All dashboards accessible by appropriate users

---

## 🔗 Quick Links

- **Metabase:** http://localhost:3000
- **Admin Email:** alamin.technometrics22@gmail.com
- **Admin Password:** Test@123
- **Documentation:** PERMISSION_SCENARIOS_GUIDE.md

---

**Document Version:** 1.0
**Last Updated:** 2026-02-16
**Maintained By:** BTRC Technical Team
