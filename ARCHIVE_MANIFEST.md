# BTRC QoS Monitoring Dashboard V3 - Archive Manifest

**Archive:** `btrc-dashboard-v3-updated-20260210-165321.tar.gz`
**Created:** 2026-02-10 16:53:21
**Size:** 78 MB (compressed)
**Format:** tar.gz (gzip compressed)

---

## 📦 What's Included

### **Core Application Files**

#### Docker Configuration
- `docker-compose.yml` - Docker services (TimescaleDB, Metabase, Nginx)
- `nginx.conf` - Nginx reverse proxy configuration

#### Database Schema & Data
- `poc_data_v2.8/` - Complete POC data (v2.8)
  - Schema creation scripts
  - Test data (172,800 measurements)
  - ISPs, PoPs, violations data
  - GeoJSON files for maps

#### Custom Dashboard Files
- `public/` - Custom HTML/JS dashboard wrapper
  - `dashboard.html` - Main dashboard page
  - `dashboard.js` - Navigation logic
  - `README.md` - Usage guide

---

### **Python Scripts**

#### Dashboard Management
- `configure_executive_dashboard.py` - Executive dashboard setup
- `configure_drillthrough.py` - Drill-down configuration
- `add_r1_cards_correct.py` - Add R1 tab cards
- `update_r1_cards_design.py` - Update card designs
- `fix_scalar_card_display.py` - Fix scalar card fonts
- `remove_custom_css.py` - Clean custom CSS
- `clear_admin_css.py` - Clear admin-level CSS

#### Public Sharing
- `enable_public_sharing.py` - Generate public links

#### Dark Mode (Not Applied)
- `apply_dark_mode.py` - Dark mode script (optional)

#### Data Population
- `populate_alerts_incidents_test_data.sql` - Test data for alerts/incidents

---

### **Documentation**

#### User Guides
- `DASHBOARD_USER_GUIDE.md` - Complete user guide
- `QUICK_START.md` - Quick start instructions
- `TRANSFER_GUIDE.md` - Transfer to production guide
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `DEPLOYMENT_SUMMARY.md` - Deployment summary

#### Sharing & Access
- `SHARING_MESSAGE.md` - Email template for sharing
- `QUICK_ACCESS_CARD.md` - Printable access card
- `INTERNET_ACCESS_SETUP.md` - Remote access setup (VPN, domain)

#### Styling (Optional - Not Applied)
- `DASHBOARD_STYLING_GUIDE.md` - CSS styling guide
- `enable_metabase_dark_mode.md` - Dark mode instructions
- `metabase_dark_mode.css` - Dark mode CSS (not active)
- `scalar_cards_complete_fix.css` - Card font fix CSS (not active)
- `FIX_FONT_SIZE_INSTRUCTIONS.md` - Font fix guide

#### Technical Documentation
- `DRILL_DOWN_SOLUTION_OPTIONS.md` - Drill-down solution options
- `OPTION_1_DETAILED_EXPLANATION.md` - Custom wrapper details
- `R1_CORRECTED_SQL.md` - SQL fixes documentation
- `SQL_FIXES_COMPLETE.md` - SQL fixes summary
- `SCHEMA_COMPLIANT_R1_QUERIES.md` - Schema-compliant queries
- `TEST_DATA_SUMMARY.md` - Test data documentation
- `ARCHIVE_MANIFEST.md` - This file

#### Comparison & Analysis
- `superset_vs_metabase_comparison.html` - BI tool comparison

---

### **SQL Scripts**

- `create_missing_tables.sql` - Create alerts/incidents tables
- `populate_alerts_incidents_test_data.sql` - Populate test data
- Various fix scripts for SQL queries

---

### **Development Scripts**

- `check_dashboard_tabs.py` - Tab verification
- `inspect_dashcards.py` - Card inspection
- `test_dashboard.sh` - Dashboard testing
- `deploy.sh` - Deployment script

---

## 📊 Dashboard Status

### **Dashboards Created**

1. **Executive Dashboard (ID: 5)**
   - 3 tabs: E1, E2, E3
   - 12 charts
   - Public link available
   - URL: http://localhost:3000/dashboard/5

2. **Regulatory Dashboard (ID: 6)**
   - 3 tabs: R2.1, R2.2, R2.3
   - 29 charts (including R1.4, R1.5, R1.6)
   - Public link available
   - URL: http://localhost:3000/dashboard/6

### **Data Populated**

- ✅ **172,800** QoS measurements (Nov 30 - Dec 15, 2025)
- ✅ **40** ISPs
- ✅ **120** PoPs (Points of Presence)
- ✅ **150** SLA violations
- ✅ **39** alerts (test data)
- ✅ **40** incidents (test data)

### **Features Implemented**

- ✅ Public sharing links (no login required)
- ✅ Dashboard filters (Division, District, ISP)
- ✅ Choropleth maps (Division & District)
- ✅ Real-time alerts & incidents
- ✅ Drill-down navigation (via custom wrapper)
- ✅ Responsive design (mobile-friendly)

---

## 🚀 How to Deploy

### **Extract Archive**

```bash
tar -xzf btrc-dashboard-v3-updated-20260210-165321.tar.gz
cd BTRC-QoS-Monitoring-Dashboard-V3
```

### **Start Services**

```bash
docker-compose up -d
```

### **Access Dashboards**

- **Metabase:** http://localhost:3000
- **Custom Wrapper:** http://localhost:8080
- **TimescaleDB:** localhost:5433

### **Login Credentials**

**Metabase:**
- Email: alamin.technometrics22@gmail.com
- Password: Test@123

**Database:**
- User: btrc_admin
- Password: btrc_poc_2026
- Database: btrc_qos_poc

---

## 📁 Directory Structure

```
BTRC-QoS-Monitoring-Dashboard-V3/
├── docker-compose.yml
├── nginx.conf
├── public/
│   ├── dashboard.html
│   ├── dashboard.js
│   └── README.md
├── poc_data_v2.8/
│   ├── 01_DB_Extensions.sql
│   ├── 02_DB_Schema_Creation_v2.8.md
│   ├── 03_poc_isps.json
│   ├── 04_poc_pops.json
│   ├── ...
│   └── geojson/
├── *.py (Python scripts)
├── *.sql (SQL scripts)
├── *.md (Documentation)
└── *.css (Styling - optional)
```

---

## 🔗 Public Sharing Links

### **Executive Dashboard**
```
http://192.168.200.52:3000/public/dashboard/54733c64-24e2-4977-9d2f-2ed086219635
```

### **Regulatory Dashboard**
```
http://192.168.200.52:3000/public/dashboard/bac7ee8a-62d3-422f-a1e9-123673b52c5f
```

**Note:** Replace `192.168.200.52` with your server IP address.

---

## 🛠️ Configuration

### **Ports**
- TimescaleDB: 5433
- Metabase: 3000
- Nginx: 8080

### **Environment**
- Timezone: Asia/Dhaka
- Database: PostgreSQL 15 + TimescaleDB
- Metabase Version: v0.58.5.2

---

## 📝 Recent Changes (2026-02-10)

### **Added**
- ✅ R1.4: Package Compliance Matrix
- ✅ R1.5: Real-Time Threshold Alerts
- ✅ R1.6: PoP-Level Incident Table
- ✅ Public sharing links (no login required)
- ✅ Test data for alerts and incidents (79 records)
- ✅ Custom dashboard wrapper with drill-down

### **Fixed**
- ✅ SQL column names (declared_* → actual columns)
- ✅ Schema compliance (alerts & incidents tables)
- ✅ POC data date ranges (NOW() → MAX(timestamp))
- ✅ GeoJSON name mappings (9 districts)

### **Removed**
- ✅ Custom CSS from all cards (29 cards)
- ✅ Admin-level custom styling
- ✅ Font size customizations

---

## 🔒 Security Notes

### **Current Setup (Safe for LAN)**
- Read-only public links
- Office network only (192.168.200.52)
- No sensitive data exposed

### **For Internet Access**
- Use VPN (WireGuard recommended)
- Or use Cloudflare Tunnel for HTTPS
- Enable firewall rules
- Set up SSL certificates
- See: `INTERNET_ACCESS_SETUP.md`

---

## 📞 Support

**Technical Contact:**
- Email: alamin.technometrics22@gmail.com
- Project: BTRC QoS Monitoring Dashboard V3

**Documentation:**
- Main Guide: `DASHBOARD_USER_GUIDE.md`
- Quick Start: `QUICK_START.md`
- Deployment: `DEPLOYMENT_GUIDE.md`

---

## 📦 Archive Details

### **Excluded from Archive**
- `.git/` - Git repository (large)
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python
- `node_modules/` - Node dependencies (if any)
- `.venv/`, `venv/` - Virtual environments
- `*.log` - Log files

### **File Count**
- Total files: ~200+
- Python scripts: ~20
- Markdown docs: ~15
- SQL scripts: ~10
- JSON data files: ~15

### **Compression**
- Original size: ~250 MB
- Compressed: 78 MB
- Compression ratio: 68.8%

---

## ✅ Ready for Production

This archive contains everything needed to deploy the BTRC QoS Monitoring Dashboard:

1. ✅ Complete codebase
2. ✅ POC data (172,800 measurements)
3. ✅ Docker configuration
4. ✅ Documentation
5. ✅ Public sharing enabled
6. ✅ Test data populated
7. ✅ All bugs fixed

**Next Steps:**
1. Extract archive on production server
2. Update IP addresses in configs
3. Run `docker-compose up -d`
4. Share public links with team

---

**Archive Version:** 3.0 Final
**Last Updated:** 2026-02-10 16:53:21
**Status:** ✅ Production Ready

---

**End of Manifest**
