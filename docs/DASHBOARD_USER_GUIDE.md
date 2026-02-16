# BTRC QoS Dashboard - User Guide

**Version:** 3.0 POC
**Date:** 2026-02-09
**For:** BTRC Staff (Executive, Regulatory, Operational)

---

## 📊 Dashboard Overview

The BTRC QoS Monitoring System consists of **3 dashboards** with **native drill-down** capabilities:

| Dashboard | Audience | Purpose | Drill-Down Depth |
|-----------|----------|---------|------------------|
| **Executive** | Leadership (Chairman, Commissioners) | National overview & policy decisions | National → Division (8) |
| **Regulatory** | Operations Staff, Compliance Officers | SLA monitoring & enforcement | National → Division → District (64) → ISP |
| **Operational** | Market Analysts, Finance Division | ISP-submitted data & market analysis | National → Division → District (64) |

---

## 🔗 Access URLs

### Local Development
- **Executive Dashboard**: http://localhost:3000/dashboard/5
- **Regulatory Dashboard**: http://localhost:3000/dashboard/6
- **Custom Wrapper** (optional): http://localhost:8080/dashboard

### Production Server (after deployment)
- **Main URL**: http://your-server-ip:3000
- **With Domain**: https://btrc-qos.example.com

---

## 📊 Dashboard 1: Executive Dashboard

**Purpose**: National overview for BTRC leadership

### Tab E1: Performance Scorecard

**What You'll See:**
- 3 KPI cards: Download Speed, Upload Speed, Availability
- Speed Trend (12 Months): Line chart showing national performance over time
- Division Performance Ranking: Horizontal bar chart ranking all 8 divisions

**How to Drill Down:**
1. **Click any division bar** in the ranking chart
2. Dashboard filters to show **that division's data only**
3. All KPIs update to show division-specific metrics
4. **Click X** next to "Division" filter to return to National view

**Use Case:**
> "Commissioner wants to see how Dhaka is performing compared to national average"
> 1. Click "Dhaka" bar → See Dhaka-specific KPIs
> 2. Compare with national averages shown before filtering

### Tab E2: Geographic Intelligence

**What You'll See:**
- Division Performance Map: Choropleth map colored by performance
- Division Comparison Table: Sortable table with all 8 divisions

**How to Drill Down:**

**Method 1: Click Map Region**
1. **Click any colored region** on the Bangladesh map
2. Dashboard filters to that division
3. Map highlights the selected division

**Method 2: Click Table Row**
1. **Click division name** in the comparison table
2. Dashboard filters to that division

**Use Case:**
> "Chairman asks: Which division has the lowest performance?"
> 1. Look at map (red regions = low performance)
> 2. Click the red region
> 3. See detailed metrics for that division

### Tab E3: Compliance Overview

**What You'll See:**
- ISP Compliance Status: Traffic light grid (Green/Yellow/Red)
- Violations by Type: Bar chart (Speed, Availability, Latency, Packet Loss)
- Top 10 Violators: Ranked table
- Violation Trend: 6-month stacked bar chart
- Violations by Division: Table showing violations per division

**How to Drill Down:**
1. **Click division name** in "Violations by Division" table
2. All charts filter to show that division's data
3. Top 10 Violators shows ISPs in that division only
4. Violation Trend shows trend for that division

**Use Case:**
> "Need to review all violations in Chattagram division"
> 1. Go to Tab E3
> 2. Click "Chattagram" in Violations by Division table
> 3. See all Chattagram-specific violation data

### Executive Dashboard: Key Features

✅ **Audience**: BTRC Chairman, Commissioners, Senior Directors
✅ **Geo Depth**: National → Division (8 divisions only)
✅ **No District Drill-Down**: Executive level stays at division granularity
✅ **Single Parameter**: Division filter only
✅ **Data Refresh**: Daily aggregation

---

## 📊 Dashboard 2: Regulatory Dashboard

**Purpose**: Deep dive into SLA monitoring and compliance enforcement

### Tab R2.1: SLA Monitoring

**What You'll See:**
- 3 Status Cards: Compliant ISPs, At Risk ISPs, Violation ISPs
- Real-time SLA status for all monitored ISPs

**Features:**
- Real-time data (5-minute refresh)
- Color-coded status (Green/Yellow/Red)
- Quick overview of compliance landscape

### Tab R2.2: Regional Analysis (MAIN DRILL-DOWN TAB)

**What You'll See:**
- Division Performance Map: Choropleth showing all 8 divisions
- Division Performance Summary: Table with division metrics
- District Performance Map: Shows districts within selected division
- District Ranking Table: Shows districts with performance scores
- ISP Performance by Area: Shows ISPs in selected district

**How to Drill Down (3 Levels):**

#### Level 1: National → Division

**Starting Point**: No filters applied, see all 8 divisions

**Method 1: Click Division in Table**
1. Look at "Division Performance Summary" table
2. **Click "Dhaka"** (division name is blue and clickable)
3. Dashboard filters to Dhaka division

**Method 2: Click Division on Map**
1. Look at "Division Performance Map" (choropleth)
2. **Click on Dhaka region** (map area)
3. Dashboard filters to Dhaka division

**Result:**
- URL changes to: `?division=Dhaka`
- District map shows only Dhaka's 13 districts
- District Ranking table shows Dhaka districts only
- Breadcrumb shows: "National → Dhaka"

#### Level 2: Division → District

**Starting Point**: Dhaka division filter applied

**Method 1: Click District in Table**
1. Look at "District Ranking" table
2. **Click "Gazipur"** (district name is blue and clickable)
3. Dashboard filters to Gazipur district

**Method 2: Click District on Map**
1. Look at "District Performance Map"
2. **Click on Gazipur region** (map area)
3. Dashboard filters to Gazipur district

**Result:**
- URL changes to: `?division=Dhaka&district=Gazipur`
- ISP Performance table shows only Gazipur ISPs
- All metrics show Gazipur-specific data
- Breadcrumb shows: "National → Dhaka → Gazipur"

#### Level 3: District → ISP

**Starting Point**: Gazipur district filter applied

1. Look at "ISP Performance by Area" table
2. **Click "Link3 Technologies"** (ISP name)
3. Dashboard filters to that ISP

**Result:**
- URL changes to: `?division=Dhaka&district=Gazipur&isp=Link3+Technologies`
- All metrics show ISP-specific data
- Breadcrumb shows: "National → Dhaka → Gazipur → Link3 Technologies"

### Navigation Controls

**Breadcrumb Navigation:**
```
🏠 National → 📍 Dhaka → 🏘️ Gazipur → 🏢 Link3 Technologies
```
- Click any level to jump back
- Click "🏠 National" to reset to national view

**Filter Dropdowns (Top of Dashboard):**
- Division: Select from 8 divisions
- District: Select from 64 districts (filtered by division)
- ISP: Select from 40 ISPs (filtered by district)

**Clear Filters:**
- Click **X** next to each filter to remove it
- Or click **"Reset View"** button to clear all

**Browser Back Button:**
- ✅ Works! Press BACK to return to previous level
- Press FORWARD to go forward again

### Tab R2.3: Violation Analysis

**What You'll See:**
- 3 Status Cards: Pending, Active, Resolved violations
- Violation Detail Table: Full list of all violations
- Violation Trend: Time-series chart
- Violations by District Heatmap: Choropleth showing violation density

**Features:**
- Sortable table (click column headers)
- Exportable data (click download button)
- Filter by violation type, status, severity

### Regulatory Dashboard: Key Features

✅ **Audience**: BTRC Operations Staff, Compliance Officers
✅ **Geo Depth**: National → Division → District → ISP (4 levels)
✅ **Three Parameters**: Division, District, ISP
✅ **Real-Time Data**: 5-minute refresh for SLA monitoring
✅ **Time Range Filter**: 1h, 24h, 7d, 30d, Custom

---

## 📊 Dashboard 3: Operational Dashboard

**Purpose**: ISP-submitted data and market analysis

### Tab O1: Market Overview

**What You'll See:**
- 4 KPI cards: Total Subscribers, ISPs Reporting, PoPs Declared, Bandwidth Capacity
- Subscriber Distribution by Division: Bar chart
- Market Share by ISP: Donut chart

**Drill-Down:**
- Similar to Executive Dashboard
- Click division in charts to filter

### Tab O2: Package & Subscriber Analysis

**What You'll See:**
- Package Tier Distribution: Stacked bar chart (speed tiers)
- Subscriber Distribution by Tier: Donut chart
- Package Detail Table: Full package listing with prices
- Average Package Price by Tier: Grouped bar chart

**Use Case:**
> "Analyze what packages ISPs are offering in Dhaka"
> 1. Use Division filter → Select "Dhaka"
> 2. Package Detail Table filters to Dhaka ISPs
> 3. See all packages available in Dhaka

### Tab O3: Geographic Coverage

**What You'll See:**
- ISP Coverage Map: PoP locations plotted on Bangladesh map
- Coverage Summary Cards: Competitive/Limited/Unserved districts
- ISP Coverage Overlap Table: Districts by ISP count
- Division-Level PoP Summary: Aggregated by division

**Use Case:**
> "Find districts with no ISP coverage"
> 1. Look at Coverage Summary Cards
> 2. Click "0 ISPs (Unserved)" card
> 3. See list of unserved districts

---

## 🎯 Common Use Cases

### Use Case 1: Monthly Executive Report

**Scenario**: Chairman needs monthly performance summary

**Steps:**
1. Open Executive Dashboard
2. Tab E1: Screenshot KPI cards (Download, Upload, Availability)
3. Tab E1: Screenshot Speed Trend (12 months)
4. Tab E2: Screenshot Division Performance Map
5. Tab E3: Screenshot Top 10 Violators

**Export Data:**
- Click download button on each card
- Select CSV or Excel format
- Attach to monthly report

### Use Case 2: ISP Compliance Investigation

**Scenario**: Investigate specific ISP for SLA violations

**Steps:**
1. Open Regulatory Dashboard
2. Tab R2.2: Use ISP filter → Select target ISP
3. Tab R2.3: Review violation details
4. Export Violation Detail Table
5. Generate compliance report

### Use Case 3: Regional Performance Analysis

**Scenario**: Compare division performance for resource allocation

**Steps:**
1. Open Executive Dashboard
2. Tab E2: Review Division Performance Map
3. Identify low-performing divisions (red regions)
4. Click each division to see detailed metrics
5. Tab E1: Screenshot Division Performance Ranking
6. Present to leadership for budget decisions

### Use Case 4: District-Level Investigation

**Scenario**: High violation count in specific district

**Steps:**
1. Open Regulatory Dashboard
2. Tab R2.2: Click target division (e.g., "Dhaka")
3. Review District Ranking table
4. Click problem district (e.g., "Gazipur")
5. Tab R2.3: Review violations in Gazipur
6. Identify problematic ISPs
7. Document findings

---

## 🔑 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Alt + Home** | Reset to national view (custom wrapper only) |
| **Alt + Backspace** | Go back one level (custom wrapper only) |
| **ESC** | Close drill-down menu (custom wrapper only) |
| **Ctrl + F** | Search within page |
| **F5** | Refresh dashboard |
| **Ctrl + Shift + R** | Hard refresh (clear cache) |

---

## 💡 Tips & Best Practices

### Tip 1: Share Filtered Views

**Problem**: Need to share specific drill-down state with colleague

**Solution**: Copy URL after drilling down
```
Before: http://localhost:3000/dashboard/6
After:  http://localhost:3000/dashboard/6?division=Dhaka&district=Gazipur
```
Send the filtered URL → Colleague sees exact same view

### Tip 2: Bookmark Common Views

Create browser bookmarks for frequently used filters:
- **Dhaka Performance**: `?division=Dhaka`
- **Sylhet Violations**: `?division=Sylhet&tab=15` (Tab R2.3)
- **High Violation Districts**: Custom URL with filters

### Tip 3: Export Data Regularly

- All tables have download buttons
- Export formats: CSV, Excel, JSON
- Schedule weekly exports for record-keeping

### Tip 4: Use Time Range Filters

On Regulatory Dashboard:
- **1h**: Real-time monitoring
- **24h**: Daily operations review
- **7d**: Weekly performance check
- **30d**: Monthly reporting

### Tip 5: Combine Filters

Use multiple filters together:
- Division: Dhaka
- District: Gazipur
- Time Range: Last 7 days
- **Result**: See Gazipur performance for the past week

---

## 🐛 Troubleshooting

### Issue: Drill-Down Not Working

**Symptom**: Clicking division/district name doesn't filter dashboard

**Solutions:**
1. **Hard refresh browser**: `Ctrl + Shift + R`
2. **Clear browser cache**: Settings → Clear browsing data
3. **Check browser console**: `F12` → Look for errors
4. **Try different browser**: Chrome, Firefox, Edge

### Issue: Data Not Loading

**Symptom**: Cards show "Loading..." indefinitely

**Solutions:**
1. **Check database connection**: Verify TimescaleDB is running
2. **Restart Metabase**: `docker restart btrc-v3-metabase`
3. **Check query timeout**: Contact system admin

### Issue: Map Not Showing

**Symptom**: Choropleth map is blank or shows error

**Solutions:**
1. **GeoJSON not loaded**: Verify GeoJSON files exist
2. **Check custom GeoJSON IDs**: divisions=49e4c04b, districts=1d814613
3. **Reload dashboard**: Press F5

### Issue: Filters Not Appearing

**Symptom**: No Division/District/ISP dropdowns at top

**Solutions:**
1. **Parameters not configured**: Contact system admin
2. **Wrong dashboard**: Verify you're on Dashboard 5 (Executive) or 6 (Regulatory)

### Issue: Can't Go Back to National View

**Symptom**: Stuck in filtered view, can't see all divisions

**Solutions:**
1. **Click X** next to Division filter at top of dashboard
2. **Click "National"** in breadcrumb (custom wrapper)
3. **Manual URL**: Navigate to `http://localhost:3000/dashboard/5` or `/6`

---

## 📞 Support & Contact

### For Technical Issues:
- **System Admin**: [Admin contact]
- **Database Issues**: Check with IT department
- **Dashboard Configuration**: Refer to technical documentation

### For Data Issues:
- **Missing Data**: Verify data collection is running
- **Incorrect Values**: Review data source configurations
- **POC Data Range**: Nov 30 - Dec 15, 2025 (static POC data)

### For Feature Requests:
- Document requirements clearly
- Specify dashboard and tab
- Provide use case examples

---

## 📚 Additional Resources

- **Technical Documentation**: See `README.md`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **API Documentation**: See `API_GUIDE.md`
- **Database Schema**: See `DEV/03-data/` directory
- **Spec Document**: `BTRC-FXBB-QOS-POC_Dev-Spec(POC-DASHBOARD-MIN-SCOPE)_DRAFT_v0.1.md`

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | 2026-02-09 | Added native Metabase drill-through, configured Executive & Regulatory dashboards |
| 2.0 | 2026-02-07 | Added custom wrapper with drill-down menu |
| 1.0 | 2026-02-02 | Initial POC deployment with 3 dashboards |

---

**End of User Guide**

For deployment and server setup instructions, see `DEPLOYMENT_GUIDE.md`.
