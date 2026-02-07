# Drill-Down & Filter Capabilities - BI Tools Comparison

**Date:** 2026-02-07
**Focus:** Geographic drill-down (Division → District) and filter capabilities
**Customer Requirements:** Drill-down + Filters are MAIN priorities

---

## Executive Summary

| Tool | Map Drill-Down | Click-to-Filter | Cross-Filter | Custom GeoJSON | Free/OSS | **Score** |
|------|----------------|-----------------|--------------|----------------|----------|-----------|
| **Helical Insight** | Yes | Yes | Yes | Yes | Yes | **Best** |
| **Metabase** | Partial* | Yes | Yes | Yes | Yes | **Good** |
| **Apache Superset** | No | Yes | Yes | Manual | Yes | Medium |
| **Lightdash** | Yes | Yes | Yes | Limited | Yes | Medium |
| **Grafana** | No | Limited | Limited | Alpha | Yes | Low |
| **Redash** | No | No | No | No | Yes | Not Suitable |

*Metabase: Custom click destinations (workaround), not true map drill-down

---

## CRITICAL: What "Map Drill-Down" Means

**True Geographic Drill-Down:**
```
Click Bangladesh Map → Shows 8 Divisions
Click Dhaka Division → Shows 13 Districts of Dhaka
Click Dhaka District → Shows Upazilas of Dhaka
```

**Current Reality (Most Open Source Tools):**
- NO tool offers true click-to-zoom geographic drill-down for custom regions
- All require workarounds (linked dashboards, custom destinations, filters)
- Power BI and Tableau (commercial) have this feature built-in

---

## Tool 1: Helical Insight (Recommended for Drill-Down)

### Overview
- **License:** Open Source (Community) + Commercial
- **Website:** https://www.helicalinsight.com/
- **Self-Hosted:** Yes (Free)

### Drill-Down & Filter Capabilities

| Feature | Support | Details |
|---------|---------|---------|
| **Map Drill-Down** | Yes | Drill up/down through hierarchy levels |
| **Map Click Filter** | Yes | Click region to filter dashboard |
| **Cross-Filtering** | Yes | Charts filter each other |
| **Dashboard Filters** | Yes | Global filter panel |
| **Hierarchy Support** | Yes | Division → District → Upazila |
| **Custom GeoJSON** | Yes | Upload country/state/city boundaries |
| **Drill-Through** | Yes | Navigate to detail reports |

### Map Visualization Features
- GeoJSON data support for countries, states, cities
- Coordinate fields (Latitude/Longitude) support
- Choropleth maps with data binding
- **Hierarchy drill-down on map** (key differentiator)

### Strengths
- **Best drill-down support among open source tools**
- Self-service drag-drop interface
- Interactivity and drill-through built-in
- PostgreSQL/TimescaleDB support
- Free community edition

### Weaknesses
- Smaller community than Metabase/Superset
- Less documentation available
- UI less modern than competitors
- May require more setup effort

### Verdict: **BEST for Drill-Down Requirements**

---

## Tool 2: Metabase (Best Balance)

### Overview
- **License:** AGPL (Open Source)
- **Website:** https://www.metabase.com/
- **Self-Hosted:** Yes (Free)

### Drill-Down & Filter Capabilities

| Feature | Support | Details |
|---------|---------|---------|
| **Map Drill-Down** | Partial | Custom click destinations (workaround) |
| **Map Click Filter** | Partial | Via custom destinations, not native |
| **Cross-Filtering** | Yes | Dashboard cross-filter support |
| **Dashboard Filters** | Yes | Native filter widgets |
| **Hierarchy Support** | Yes | Via linked questions |
| **Custom GeoJSON** | Yes | Admin panel upload (<5MB) |
| **Drill-Through** | Yes | Click any chart to drill |

### Map Workaround for Drill-Down
```
Approach: Use smallest region map + dashboard filters

1. Create District-level map (64 districts)
2. Add Division filter dropdown
3. User selects Division → Map shows only that division's districts
4. Click district → Custom destination to detail dashboard
```

### Drill-Through Features (Non-Map)
- Click any chart value → Filter, Breakout, or View Source
- Custom click destinations to other dashboards
- Parameterized URLs based on clicked values
- "Zoom in" on time series data

### Strengths
- Best documentation and community
- Easiest custom GeoJSON setup
- Good drill-through for tables/charts
- Modern, user-friendly UI
- Very active development

### Weaknesses
- **No native map drill-down** (custom maps don't support drill-through)
- Workaround required for geographic hierarchy
- Region map click doesn't auto-filter

### Verdict: **GOOD - Best UI/UX, needs workaround for map drill-down**

---

## Tool 3: Apache Superset (Current)

### Overview
- **License:** Apache 2.0
- **Website:** https://superset.apache.org/
- **Self-Hosted:** Yes (Free)

### Drill-Down & Filter Capabilities

| Feature | Support | Details |
|---------|---------|---------|
| **Map Drill-Down** | No | Single level only |
| **Map Click Filter** | Yes | emit_filter on country_map |
| **Cross-Filtering** | Yes | Dashboard cross-filter |
| **Dashboard Filters** | Yes | Native filter panel |
| **Hierarchy Support** | No | Via linked tables only |
| **Custom GeoJSON** | Manual | Replace files in Docker |
| **Drill-Through** | Limited | Via cross-filter only |

### Current BTRC Implementation
```
Workaround: Two-linked-tables approach

1. Division Map (country_map) with emit_filter: true
2. Division Ranking Table
3. District Detail Table (filters by division)
4. Native filters for Division/District/ISP
```

### Strengths
- Already deployed and configured
- 50+ visualization types
- SQL Lab for advanced queries
- Good cross-filter support

### Weaknesses
- **No geographic drill-down**
- deck.gl broken in Chrome
- Complex custom GeoJSON setup
- Native filter API bugs

### Verdict: **MEDIUM - Keep for POC, consider alternatives for production**

---

## Tool 4: Lightdash

### Overview
- **License:** MIT (Open Source)
- **Website:** https://www.lightdash.com/
- **Self-Hosted:** Yes (Free)

### Drill-Down & Filter Capabilities

| Feature | Support | Details |
|---------|---------|---------|
| **Map Drill-Down** | Yes | Via dbt metrics hierarchy |
| **Map Click Filter** | Yes | Interactive dashboards |
| **Cross-Filtering** | Yes | Dashboard interactivity |
| **Dashboard Filters** | Yes | Filter widgets |
| **Hierarchy Support** | Yes | dbt model based |
| **Custom GeoJSON** | Limited | Less mature than others |
| **Drill-Through** | Yes | Pivots and drill-downs |

### Key Difference: dbt Integration
- Requires dbt (data build tool) for data modeling
- Metrics defined once in dbt, reused everywhere
- Hierarchy defined in dbt models
- More developer-focused

### Strengths
- Modern architecture
- Good drill-down for dbt users
- Interactive exploration
- Active development

### Weaknesses
- **Requires dbt** (additional tool to learn)
- Less mature map support
- Smaller community
- More developer-focused than analyst-focused

### Verdict: **MEDIUM - Good if already using dbt, otherwise extra complexity**

---

## Tool 5: Grafana

### Overview
- **License:** AGPL
- **Website:** https://grafana.com/
- **Self-Hosted:** Yes (Free)

### Drill-Down & Filter Capabilities

| Feature | Support | Details |
|---------|---------|---------|
| **Map Drill-Down** | No | Not supported |
| **Map Click Filter** | Limited | Data links only |
| **Cross-Filtering** | Limited | Template variables |
| **Dashboard Filters** | Yes | Variable dropdowns |
| **Hierarchy Support** | No | Manual setup |
| **Custom GeoJSON** | Alpha | Dynamic GeoJSON layer |
| **Drill-Through** | Limited | Data links to other dashboards |

### Strengths
- Best for real-time monitoring
- Excellent alerting
- Good time-series support

### Weaknesses
- **Not designed for BI drill-down**
- Map features are alpha/experimental
- Complex for business users

### Verdict: **LOW - Not suitable for drill-down requirements**

---

## Tool 6: Redash

### Drill-Down & Filter Capabilities

| Feature | Support |
|---------|---------|
| Map Drill-Down | No |
| Map Click Filter | No |
| Cross-Filtering | No |
| Dashboard Filters | Yes (basic) |
| Custom GeoJSON | No |

### Verdict: **NOT SUITABLE - Lacks all key requirements**

---

## Detailed Comparison: Drill-Down Features

### Geographic Drill-Down (Division → District → Upazila)

| Capability | Helical | Metabase | Superset | Lightdash |
|------------|---------|----------|----------|-----------|
| Click Division → Show Districts | Yes | Workaround | Workaround | Yes* |
| Click District → Show Upazilas | Yes | Workaround | No | Yes* |
| Automatic Map Zoom | No | No | No | No |
| Breadcrumb Navigation | Yes | Manual | Manual | Yes |
| Back/Up Navigation | Yes | Manual | Manual | Yes |

*Requires dbt model setup

### Filter Capabilities

| Capability | Helical | Metabase | Superset | Lightdash |
|------------|---------|----------|----------|-----------|
| Global Dashboard Filters | Yes | Yes | Yes | Yes |
| Filter Cascading | Yes | Yes | Yes | Yes |
| Cross-Chart Filtering | Yes | Yes | Yes | Yes |
| Map Click → Filter | Yes | Partial | Yes | Yes |
| Time Range Filter | Yes | Yes | Yes | Yes |
| Multi-Select Filters | Yes | Yes | Yes | Yes |
| Filter Presets/Bookmarks | Yes | Yes | Limited | Yes |

### Drill-Through (Click to Detail)

| Capability | Helical | Metabase | Superset | Lightdash |
|------------|---------|----------|----------|-----------|
| Click Table Row → Detail | Yes | Yes | Limited | Yes |
| Click Chart Point → Detail | Yes | Yes | Limited | Yes |
| Click Map Region → Detail | Yes | Partial | No | Yes |
| Parameterized Destinations | Yes | Yes | No | Yes |
| Custom URL Actions | Yes | Yes | No | Limited |

---

## Recommendation Matrix

### For BTRC Requirements (Drill-Down + Filters Priority)

| Scenario | Recommended Tool | Reason |
|----------|------------------|--------|
| **Best Drill-Down** | Helical Insight | Native hierarchy drill-down on maps |
| **Best Overall Balance** | Metabase | Good UX + workarounds available |
| **Already Deployed** | Superset | Keep for POC, evaluate others |
| **Modern Data Stack (dbt)** | Lightdash | If using dbt already |
| **Real-Time Monitoring** | Grafana | Add as complement, not primary |

### Migration Effort Comparison

| Tool | Setup Effort | Learning Curve | Bangladesh GeoJSON |
|------|--------------|----------------|-------------------|
| Helical Insight | Medium | Medium | Upload via UI |
| Metabase | Low | Low | Upload via Admin |
| Superset (current) | Done | Done | Manual Docker |
| Lightdash | High | High | dbt model needed |

---

## Final Recommendation for BTRC

### Option 1: Pilot Helical Insight (Best for Drill-Down)
**Effort:** 2-3 weeks
**Why:**
- Only open-source tool with true map hierarchy drill-down
- Self-service interface with drag-drop
- Free community edition
- PostgreSQL support

**Steps:**
1. Deploy Helical Insight (Docker)
2. Connect to TimescaleDB
3. Upload Bangladesh GeoJSON (Division → District → Upazila)
4. Create hierarchy in data model
5. Build drill-down dashboards
6. Compare with current Superset

### Option 2: Metabase with Workarounds (Best UX)
**Effort:** 2 weeks
**Why:**
- Best user experience
- Large community and documentation
- Easy custom GeoJSON
- Good filter capabilities

**Workaround for Drill-Down:**
1. Use District-level map as base
2. Add Division filter dropdown
3. Use custom click destinations
4. Create linked detail dashboards

### Option 3: Keep Superset + Two-Linked-Tables (Current)
**Effort:** None
**Why:**
- Already working
- POC timeline constraint
- Document limitations for Phase 2

---

## Quick Decision Guide

```
Do you need TRUE map drill-down (click region → zoom to sub-regions)?
├── YES → Helical Insight (only open-source option)
└── NO (filter-based drill-down OK)
    ├── Priority: Ease of Use → Metabase
    ├── Priority: Already Deployed → Keep Superset
    └── Priority: Modern/dbt → Lightdash
```

---

## Sources

- [Helical Insight Map Visualization](https://www.helicalinsight.com/map-visualization-in-helical-insight-version-5-1-0/)
- [Helical Insight Open Source BI](https://www.helicalinsight.com/open-source-bi/)
- [Metabase Drill-Throughs](https://www.metabase.com/features/drill-through)
- [Metabase Custom Click Destinations](https://www.metabase.com/learn/metabase-basics/querying-and-dashboards/dashboards/custom-destinations)
- [Metabase Maps Documentation](https://www.metabase.com/docs/latest/questions/visualizations/map)
- [Lightdash GitHub](https://github.com/lightdash/lightdash)
- [Best Open Source BI Tools 2025](https://posthog.com/blog/best-open-source-business-intelligence-tools)
- [14 Free Open Source BI Tools 2026](https://www.holistics.io/blog/best-open-source-bi-tools/)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
