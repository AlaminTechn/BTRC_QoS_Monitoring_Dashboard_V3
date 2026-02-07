# Regulatory Dashboard (Dashboard 2) - Status Report

**Date:** 2026-02-07
**Dashboard URL:** http://localhost:8088/superset/dashboard/regulatory/
**Slug:** `regulatory`
**Dashboard ID:** 1

---

## Completed Features ✅

### Tab R1: SLA Monitoring
| ID | Element | Status | Notes |
|----|---------|--------|-------|
| R1.1 | Compliant ISPs Count | ✅ Done | big_number_total, green card |
| R1.2 | At Risk ISPs Count | ✅ Done | big_number_total, yellow card |
| R1.3 | Violation ISPs Count | ✅ Done | big_number_total, red card |
| R1.4 | Package Compliance Matrix | ⏭️ Removed | Per spec - removed from POC scope |
| R1.5 | Real-Time Threshold Alerts | ⏭️ Removed | Per spec - removed from POC scope |
| R1.6 | PoP-Level Incident Table | ⏭️ Removed | Per spec - removed from POC scope |

### Tab R2: Regional Drill-Down
| ID | Element | Status | Notes |
|----|---------|--------|-------|
| R2.1 | Division Performance Map | ✅ Done | country_map (D3/SVG), emit_filter enabled |
| R2.2 | Division/District Ranking | ✅ Done | table with all metrics |
| R2.3 | ISP Performance by Area | ✅ Done | table filtered by division/district |
| R2.4 | District Detail | ✅ Done | NEW - drill-down table for districts |
| R2.4 | Time Range Filter | ✅ Done | Native filter in sidebar |
| R2.5 | Geo Breadcrumb | ⚠️ Partial | Using native filter cascade instead |

### Tab R3: Violation Analysis
| ID | Element | Status | Notes |
|----|---------|--------|-------|
| R3.1 | Pending Violations Count | ✅ Done | DETECTED + INVESTIGATING status |
| R3.2 | Active Violations Count | ✅ Done | DISPUTED status |
| R3.3 | Resolved Violations Count | ✅ Done | RESOLVED + WAIVED status |
| R3.4 | Violation Detail Table | ✅ Done | Full sortable/filterable table |
| R3.5 | Violation Trend | ✅ Done | echarts_timeseries_bar by date |
| R3.6 | Violations by Division | ✅ Done | echarts_timeseries_bar stacked by severity |

### Native Filters (Sidebar)
| Filter | Status | Notes |
|--------|--------|-------|
| Division | ✅ Done | Created via UI |
| District | ✅ Done | Cascades from Division |
| ISP | ✅ Done | Filters ISP-related charts |

### Cross-Filtering
| Feature | Status | Notes |
|---------|--------|-------|
| Map → Tables | ✅ Done | emit_filter: true on R2.1 |
| Division → District cascade | ✅ Done | Native filter parent-child |

---

## Limitations & Known Issues ⚠️

### 1. Map Visualization Limitations
| Issue | Details | Workaround |
|-------|---------|------------|
| deck.gl broken in Chrome | WebGL luma.gl error: "Cannot read properties of null (reading 'luma')" | Works in Firefox; using country_map (D3/SVG) instead |
| No true map drill-down | country_map doesn't support click-to-zoom to districts | Using two-linked-tables approach with native filters |
| cartodiagram plugin not working | Plugin in bundle but frontend registration broken | Would require building Superset from source |
| echarts_map not available | Registered but "visualization type not supported" | Same issue as cartodiagram |

### 2. Native Filter Limitations
| Issue | Details | Workaround |
|-------|---------|------------|
| API-created filters broken | "Apply Filters" button stays disabled | Must create filters via Superset UI |
| Time Range filter complex | filter_time type has empty target issues | Omitted for now; can add via UI |

### 3. Chart Limitations
| Issue | Details | Workaround |
|-------|---------|------------|
| Table ordering | order_by_cols causes "invalid orderby" error | Using query_mode: raw with ORDER BY in SQL |
| Markdown components | MARKDOWN layout type doesn't render properly | Using handlebars chart type with HTML |

### 4. Data Scope Limitations
| Issue | Details |
|-------|---------|
| No real-time data | POC uses static synthetic data |
| Limited time range | Data covers fixed period from poc_data_v2.8 |

---

## Not Implemented (Phase 2) ⏳

### Tab R4: Investigation Center
- Investigation query builder
- Evidence attachment and review
- ISP response tracking
- Dispute resolution workflow

### Tab R5: License Compliance
- License condition tracking
- Compliance score dashboard
- Renewal and expiry alerts
- Regulatory reporting templates

### Additional Features Deferred
| Feature | Reason |
|---------|--------|
| District-level choropleth map | deck.gl broken, country_map only supports country subdivisions |
| Real-time threshold alerts | Requires live data integration |
| Investigation workflow | Complex multi-step process |
| Export to PDF/Excel | Requires additional configuration |

---

## Technical Details

### Charts Created
| Chart ID | Name | Viz Type | Dataset ID |
|----------|------|----------|------------|
| 1 | R1.1 Compliant ISPs | big_number_total | 1 |
| 2 | R1.2 At Risk ISPs | big_number_total | 2 |
| 3 | R1.3 Violation ISPs | big_number_total | 3 |
| 13 | R2.1 Division Performance Map | country_map | 13 |
| 5 | R2.2 Division/District Ranking | table | 5 |
| 32 | R2.4 District Detail | table | 18 |
| 6 | R2.3 ISP Performance by Area | table | 6 |
| 7 | R3.1 Pending Violations | big_number_total | 7 |
| 8 | R3.2 Active Violations | big_number_total | 8 |
| 9 | R3.3 Resolved Violations | big_number_total | 9 |
| 10 | R3.4 Violation Detail Table | table | 10 |
| 11 | R3.5 Violation Trend | echarts_timeseries_bar | 11 |
| 14 | R3.6 Violations by Division | echarts_timeseries_bar | 14 |

### Datasets Created
| Dataset ID | Name | Purpose |
|------------|------|---------|
| 1 | r1_compliant_isps | Compliant ISP count |
| 2 | r1_at_risk_isps | At-risk ISP count |
| 3 | r1_violation_isps | Violating ISP count |
| 5 | r2_division_district_ranking | Division/district ranking |
| 6 | r2_isp_performance_by_area | ISP performance by geo |
| 13 | r2_division_map | Division map data |
| 18 | r2_district_detail | District drill-down data |
| 7 | r3_pending_violations | Pending violation count |
| 8 | r3_active_violations | Active violation count |
| 9 | r3_resolved_violations | Resolved violation count |
| 10 | r3_violation_detail | Full violation details |
| 11 | r3_violation_trend | Violation trend by date |
| 14 | r3_division_violations | Violations by division |

### Files Modified/Created
| File | Purpose |
|------|---------|
| `create_regulatory_dashboard.py` | Dashboard creation script |
| `geodata/bangladesh_divisions_8.geojson` | Fixed 8-division GeoJSON |
| `docker/superset/Dockerfile` | Includes GeoJSON fix |
| `superset_config.py` | Map tiles, CORS, feature flags |

---

## How to Recreate Dashboard

```bash
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V2"
source superset_env/bin/activate
python3 create_regulatory_dashboard.py
```

**Note:** Native filters must be created via Superset UI after running the script.

---

## Backup Location

`backups/2026-02-05_pre_holiday/`
- `btrc_qos_poc.dump` - Data database
- `superset_meta.dump` - Superset metadata
- `regulatory_dashboard_export.zip` - Dashboard export
- `project_source.tar.gz` - Source files

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
