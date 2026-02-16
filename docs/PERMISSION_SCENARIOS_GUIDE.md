# BTRC Dashboard - Permission Scenarios Guide

**For:** Metabase Free Tier (Built-in Authentication)
**Created:** 2026-02-16

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [User Groups](#user-groups)
3. [Permission Matrix](#permission-matrix)
4. [Implementation](#implementation)
5. [Test Scenarios](#test-scenarios)
6. [Best Practices](#best-practices)

---

## 🎯 Overview

### **Permission Layers in Metabase**

Metabase has 3 permission layers:

1. **Data Permissions** (Database Access)
   - Controls access to databases and tables
   - Levels: Unrestricted, Query Builder Only, No Access

2. **Collection Permissions** (Dashboard Access)
   - Controls access to dashboards, questions, models
   - Levels: Curate (Edit), View, No Access

3. **Application Permissions** (Administrative)
   - Controls admin functions
   - Levels: Admin, Regular User

---

## 👥 User Groups

### **1. BTRC Administrators** 🔴

**Who:** IT Team, System Administrators

**Permissions:**
- ✅ **Data Access:** Unrestricted (full database access)
- ✅ **Collection Access:** Curate (can create/edit/delete)
- ✅ **Admin Access:** Yes (can manage users, settings)
- ✅ **Can create native SQL queries:** Yes
- ✅ **Can see all dashboards:** Yes

**Use Cases:**
- System configuration and maintenance
- User management
- Database administration
- Troubleshooting and debugging

**Sample Users:**
```
Email: admin@btrc.gov.bd
Password: Admin@123!
```

---

### **2. Management Team** 🟢

**Who:** CEO, CTO, Directors, Senior Management

**Permissions:**
- ✅ **Data Access:** Query Builder Only (no SQL)
- ✅ **Collection Access:** View (read-only)
- ❌ **Admin Access:** No
- ❌ **Can create native SQL queries:** No
- ✅ **Can see dashboards:** Executive + Regulatory

**Use Cases:**
- View executive dashboard for KPIs
- Monitor overall performance
- Export reports
- Filter data by division/district

**Sample Users:**
```
Email: ceo@btrc.gov.bd
Password: CEO@123!

Email: cto@btrc.gov.bd
Password: CTO@123!
```

---

### **3. Operations Team** 🟡

**Who:** Project Managers, Analysts, Operations Staff

**Permissions:**
- ✅ **Data Access:** Query Builder + SQL
- ✅ **Collection Access:** Curate (can create own dashboards)
- ❌ **Admin Access:** No
- ✅ **Can create native SQL queries:** Yes
- ✅ **Can create dashboards:** Yes (in their collection)

**Use Cases:**
- Create custom queries and reports
- Build new dashboards
- Analyze data trends
- Create alerts and visualizations

**Sample Users:**
```
Email: pm@btrc.gov.bd
Password: PM@123!

Email: analyst@btrc.gov.bd
Password: Analyst@123!
```

---

### **4. Regional Officers** 🔵

**Who:** Division Officers, District Officers

**Permissions:**
- ✅ **Data Access:** Query Builder Only (filtered by region)
- ✅ **Collection Access:** View (specific dashboards)
- ❌ **Admin Access:** No
- ❌ **Can create native SQL queries:** No
- ⚠️ **Row-level security:** Yes (see only their region)

**Use Cases:**
- View regional performance
- Monitor ISPs in their division/district
- Generate regional reports
- Track violations in their area

**Sample Users:**
```
Email: dhaka.officer@btrc.gov.bd
Password: Dhaka@123!
(Can only see Dhaka division data)

Email: chittagong.officer@btrc.gov.bd
Password: Chittagong@123!
(Can only see Chittagong division data)
```

**Note:** Row-level security requires Metabase Enterprise or custom SQL filters

---

### **5. External Viewers** ⚪

**Who:** External Consultants, Auditors, Partners

**Permissions:**
- ❌ **Data Access:** No direct database access
- ✅ **Collection Access:** View (public dashboards only)
- ❌ **Admin Access:** No
- ❌ **Can create queries:** No
- ⚠️ **Limited access:** Public shared dashboards only

**Use Cases:**
- View public dashboards
- Export specific reports
- Read-only access for audits

**Sample Users:**
```
Email: consultant@example.com
Password: Consult@123!
```

---

## 📊 Permission Matrix

### **Data Permissions**

| Group | Database Access | Native SQL | Query Builder | Tables Accessible |
|-------|----------------|------------|---------------|-------------------|
| **BTRC Administrators** | Unrestricted | ✅ Yes | ✅ Yes | All tables |
| **Management Team** | Query Builder Only | ❌ No | ✅ Yes | All tables |
| **Operations Team** | Unrestricted | ✅ Yes | ✅ Yes | All tables |
| **Regional Officers** | Query Builder Only | ❌ No | ✅ Yes | All tables* |
| **External Viewers** | No Access | ❌ No | ❌ No | None |

*With row-level filters applied

---

### **Collection Permissions**

| Group | Executive Dashboard | Regulatory Dashboard | Personal Dashboards |
|-------|---------------------|----------------------|---------------------|
| **BTRC Administrators** | Curate (Edit) | Curate (Edit) | Curate (Edit) |
| **Management Team** | View (Read) | View (Read) | No Access |
| **Operations Team** | View (Read) | Curate (Edit) | Curate (Edit) |
| **Regional Officers** | View (Read) | View (Read) | No Access |
| **External Viewers** | No Access | No Access | No Access |

---

### **Application Permissions**

| Feature | Admins | Management | Operations | Regional | External |
|---------|--------|------------|------------|----------|----------|
| **Manage Users** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Manage Settings** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Create Dashboards** | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Create Questions** | ✅ | ⚠️ Query Builder | ✅ | ⚠️ Query Builder | ❌ |
| **Export Data** | ✅ | ✅ | ✅ | ✅ | ⚠️ Limited |
| **View Audit Logs** | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 🚀 Implementation

### **Step 1: Run Setup Script**

```bash
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3"
python3 setup_dashboard_users_and_permissions.py
```

**What it does:**
1. Creates 5 user groups
2. Creates sample users (11 users total)
3. Assigns users to groups
4. Sets data permissions for each group
5. Sets collection permissions for dashboards

**Time:** ~2 minutes

---

### **Step 2: Verify Groups**

1. Login to Metabase as admin: http://localhost:3000
2. Go to **Admin Settings** → **People**
3. Click **Groups** tab
4. Verify 5 groups are created:
   - BTRC Administrators
   - Management Team
   - Operations Team
   - Regional Officers
   - External Viewers

---

### **Step 3: Verify Users**

1. In Admin Settings → **People**
2. Verify 11 users created
3. Check each user's group membership

---

### **Step 4: Set Data Permissions**

1. Admin Settings → **Permissions** → **Data**
2. Find "btrc_qos_poc" database
3. For each group, verify permissions:

**BTRC Administrators:**
```
Database: Unrestricted
Native Queries: Yes
```

**Management Team:**
```
Database: Query Builder Only
Native Queries: No
```

**Operations Team:**
```
Database: Unrestricted
Native Queries: Yes
```

**Regional Officers:**
```
Database: Query Builder Only
Native Queries: No
(Add row-level security separately)
```

**External Viewers:**
```
Database: No Access
Native Queries: No
```

---

### **Step 5: Set Collection Permissions**

1. Admin Settings → **Permissions** → **Collections**
2. Find "Executive Dashboard" collection
3. Set permissions:

| Group | Permission |
|-------|------------|
| BTRC Administrators | Curate |
| Management Team | View |
| Operations Team | View |
| Regional Officers | View |
| External Viewers | No Access |

4. Repeat for "Regulatory Dashboard" collection

---

## 🧪 Test Scenarios

### **Test 1: Admin Access**

1. Logout from Metabase
2. Login as: `admin@btrc.gov.bd` / `Admin@123!`
3. Verify:
   - ✅ Can see Admin Settings menu
   - ✅ Can access all dashboards
   - ✅ Can create new questions with SQL
   - ✅ Can manage users
   - ✅ Can edit dashboards

---

### **Test 2: Management View-Only**

1. Logout
2. Login as: `ceo@btrc.gov.bd` / `CEO@123!`
3. Verify:
   - ✅ Can see Executive Dashboard
   - ✅ Can see Regulatory Dashboard
   - ✅ Can use filters (Division, District, ISP)
   - ✅ Can export data
   - ❌ Cannot see Admin Settings
   - ❌ Cannot create new questions
   - ❌ Cannot edit dashboards

---

### **Test 3: Operations Create & Edit**

1. Logout
2. Login as: `analyst@btrc.gov.bd` / `Analyst@123!`
3. Verify:
   - ✅ Can see both dashboards
   - ✅ Can create new questions (SQL + GUI)
   - ✅ Can create new dashboards
   - ✅ Can save to personal collection
   - ❌ Cannot manage users
   - ❌ Cannot edit main dashboards

---

### **Test 4: Regional Filtered View**

1. Logout
2. Login as: `dhaka.officer@btrc.gov.bd` / `Dhaka@123!`
3. Verify:
   - ✅ Can see dashboards
   - ⚠️ Should only see Dhaka division data (if row-level security configured)
   - ✅ Can use filters
   - ❌ Cannot create queries
   - ❌ Cannot see other divisions

**Note:** Row-level security requires additional configuration

---

### **Test 5: External Limited Access**

1. Logout
2. Login as: `consultant@example.com` / `Consult@123!`
3. Verify:
   - ❌ Cannot access private dashboards
   - ✅ Can access public shared links (if provided)
   - ❌ Cannot see database
   - ❌ Cannot create anything

---

## 🔒 Best Practices

### **1. Password Policy**

**Require strong passwords:**
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 number, 1 special char
- Example: `User@123!`

**Set in User Creation:**
```python
{
    "email": "user@btrc.gov.bd",
    "password": "StrongPass@123!",
    "first_name": "User",
    "last_name": "Name"
}
```

---

### **2. Regular Access Reviews**

**Monthly:**
- Review active users
- Remove inactive accounts
- Audit group memberships

**Quarterly:**
- Review permissions
- Update access levels
- Check for over-privileged users

---

### **3. Principle of Least Privilege**

- Give users minimum access needed
- Start with view-only, upgrade if needed
- Regularly review and downgrade unused permissions

---

### **4. Group-Based Management**

**Do:**
- ✅ Use groups for permission management
- ✅ Assign users to appropriate groups
- ✅ Set permissions at group level

**Don't:**
- ❌ Set individual user permissions
- ❌ Give everyone admin access
- ❌ Create too many groups

---

### **5. Audit Logging**

**Monitor:**
- User logins
- Dashboard access
- Query execution
- Permission changes

**Check logs in:**
- Admin Settings → Troubleshooting → Logs
- Or use Metabase Enterprise for advanced auditing

---

### **6. Collection Organization**

```
Root
├── Executive Dashboards (Management View)
│   └── Executive Dashboard
├── Regulatory Dashboards (Operations Curate)
│   └── Regulatory Dashboard
├── Regional Dashboards (Regional View)
│   ├── Dhaka Dashboard
│   └── Chittagong Dashboard
└── Personal Collections (User-owned)
    ├── PM's Analysis
    └── Analyst Reports
```

---

## 🎯 Advanced: Row-Level Security

### **Concept**

Restrict data based on user attributes (e.g., division, role)

### **Implementation (Free Tier Workaround)**

Since Metabase free tier doesn't have native row-level security, use:

**Option 1: Separate Dashboards**
- Create division-specific dashboards
- Set collection permissions per division
- Dhaka officers see only Dhaka dashboard

**Option 2: SQL Filters in Questions**
- Add WHERE clause to all queries
- Use session variables (not available in free tier)
- Manually create filtered copies

**Option 3: Database Views**
- Create database views per division
- Grant access to specific views per group
- More secure but requires database admin access

---

## 📞 Support

### **Common Issues**

**Problem: User can't see dashboard**
→ Check collection permissions
→ Verify group membership

**Problem: User can't create queries**
→ Check data permissions
→ Ensure "Unrestricted" or "Query Builder" access

**Problem: Filters not working**
→ Check dashboard parameter mappings
→ Verify template tags in questions

---

## 📝 Summary

### **Quick Reference**

| Group | Database | Collections | Admin | SQL |
|-------|----------|-------------|-------|-----|
| **Administrators** | Full | Edit | Yes | Yes |
| **Management** | View | View | No | No |
| **Operations** | Full | Edit Own | No | Yes |
| **Regional** | View | View | No | No |
| **External** | None | None | No | No |

### **Setup Checklist**

- [ ] Run `setup_dashboard_users_and_permissions.py`
- [ ] Verify 5 groups created
- [ ] Verify 11 users created
- [ ] Test admin login
- [ ] Test management login
- [ ] Test operations login
- [ ] Set data permissions
- [ ] Set collection permissions
- [ ] Document custom changes
- [ ] Train users on access levels

---

**Document Version:** 1.0
**Last Updated:** 2026-02-16
**Maintained By:** BTRC Technical Team
