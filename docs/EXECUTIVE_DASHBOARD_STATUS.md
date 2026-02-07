# Executive Dashboard (Dashboard 1) - Status Report

**Date:** 2026-02-07
**Dashboard URL:** http://localhost:8088/superset/dashboard/executive/
**Slug:** `executive`
**Dashboard ID:** 2

---

## Completed Features

### Tab E1: Performance Scorecard
| ID | Element | Status | Notes |
|----|---------|--------|-------|
| E1.1 | National Avg Download Speed | Done | big_number_total, 30-day avg |
| E1.2 | National Avg Upload Speed | Done | big_number_total, 30-day avg |
| E1.3 | National Service Availability | Done | big_number_total, % (30-day) |
| E1.4 | Active ISP Count | Removed | Per spec - removed from POC scope |
| E1.5 | Speed Trend (12 Months) | Done | echarts_timeseries_line, DL+UL |
| E1.6 | Division Performance Ranking | Done | echarts_bar, horizontal |
| E1.7 | Performance by ISP Category | Removed | Per spec - removed from POC scope |

### Tab E2: Geographic Intelligence
| ID | Element | Status | Notes |
|----|---------|--------|-------|
| E2.1 | Division Performance Map | Done | country_map (D3/SVG), Bangladesh |
| E2.2 | Division Comparison Table | Done | table with all metrics |
| E2.3 | Urban vs Rural Gap | Removed | Per spec - removed from POC scope |
| E2.4 | PoP Coverage Summary | Removed | Per spec - removed from POC scope |

### Tab E3: Compliance Overview
| ID | Element | Status | Notes |
|----|---------|--------|-------|
| E3.1 | ISP Compliance Status | Done | table with calculated scores from violations |
| E3.2 | Violations by Type | Done | echarts_bar, horizontal |
| E3.3 | Top 10 Violators | Done | table with violation counts |
| E3.4 | Violation Trend (6 Months) | Done | echarts_timeseries_bar, stacked by type |
| E3.5 | Violations by Division | Done | table with breakdown by type |

---

## Technical Details

### Charts Created
| Chart ID | Name | Viz Type | Dataset ID |
|----------|------|----------|------------|
| 33 | E1.1 National Avg Download Speed | big_number_total | 44 |
| 34 | E1.2 National Avg Upload Speed | big_number_total | 45 |
| 35 | E1.3 National Service Availability | big_number_total | 46 |
| 36 | E1.5 Speed Trend (12 Months) | echarts_timeseries_line | 47 |
| 37 | E1.6 Division Performance Ranking | echarts_bar | 48 |
| 38 | E2.1 Division Performance Map | country_map | 49 |
| 39 | E2.2 Division Comparison Table | table | 50 |
| 40 | E3.1 ISP Compliance Status | table | 54 |
| 41 | E3.2 Violations by Type | echarts_bar | 40 |
| 42 | E3.3 Top 10 Violators | table | 52 |
| 43 | E3.4 Violation Trend (6 Months) | echarts_timeseries_bar | 42 |
| 44 | E3.5 Violations by Division | table | 43 |

### Datasets Created
| Dataset ID | Name | Purpose |
|------------|------|---------|
| 44 | e1_national_dl_speed | National download speed avg |
| 45 | e1_national_ul_speed | National upload speed avg |
| 46 | e1_national_availability | National availability % |
| 47 | e1_speed_trend | 12-month speed trend |
| 48 | e1_division_ranking | Division ranking by speed |
| 49 | e2_division_map | Division map data |
| 50 | e2_division_comparison | Division comparison table |
| 54 | e3_compliance_traffic_light | ISP compliance status |
| 40 | e3_violations_by_type | Violations by type |
| 52 | e3_top_violators | Top 10 violators |
| 42 | e3_violation_trend | Violation trend by month |
| 43 | e3_violations_by_division | Violations by division |

### Schema Adaptations
Since `compliance_scores` table doesn't exist in the current schema, E3.1 calculates compliance dynamically from `sla_violations`:
- 0 violations = Compliant (score 100)
- 1-2 violations = At Risk (score 80)
- 3-5 violations = At Risk (score 60)
- 6+ violations = Violation (score 40)

### Column Mappings (vs spec)
| Spec Column | Actual Column | Table |
|-------------|---------------|-------|
| measurement_time | timestamp | ts_qos_measurements |
| detected_at | detection_time | sla_violations |
| company_name | name_en | isps |
| category_name | name_en | isp_license_categories |

---

## Limitations & Known Issues

### 1. No Compliance Scores Table
- The `compliance_scores` table from the spec doesn't exist
- E3.1 calculates compliance dynamically from violation counts
- This is a POC simplification; production would have proper scoring

### 2. Map Visualization
- Uses country_map (D3/SVG) instead of deck.gl
- deck.gl broken in Chrome due to luma.gl WebGL error
- Map shows division-level data only (no district drill-down)

### 3. Data Time Range
- Queries use `NOW() - INTERVAL '30 days'` for consistency
- 12-month trend shows data from the POC dataset

---

## Not Implemented (Phase 2)

### Removed Elements (per spec)
- E1.4: Active ISP Count
- E1.7: Performance by ISP Category
- E2.3: Urban vs Rural Gap
- E2.4: PoP Coverage Summary

### Additional Features Deferred
| Feature | Reason |
|---------|--------|
| Consumer Experience Tab | Dashboard 1 simplified for POC |
| PoP Availability Tab | Dashboard 1 simplified for POC |
| NPS calculation | Requires BTRC approval |
| ISP Grade (A/B/C) system | Requires BTRC approval |

---

## Files Modified/Created

| File | Purpose |
|------|---------|
| `create_executive_dashboard.py` | Dashboard creation script |
| `docs/EXECUTIVE_DASHBOARD_STATUS.md` | This status document |

---

## How to Recreate Dashboard

```bash
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V2"
source superset_env/bin/activate
python3 create_executive_dashboard.py
```

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
