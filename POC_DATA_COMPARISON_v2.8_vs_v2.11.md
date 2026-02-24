# POC Data Comparison: v2.8 → v2.11
**BTRC QoS Monitoring Dashboard V3**
Generated: 2026-02-24

---

## Quick Summary

| Metric | v2.8 (Current) | v2.11 (Updated) | Change |
|--------|---------------|-----------------|--------|
| Total tables | 36 | 29 | -7 |
| Total files | 22 | 29 | +7 |
| Total records | ~755,600 | ~1,448,914 | +92% |
| Timeseries tables | 3 (aggregated) | 7 (granular) | +4 |
| Timeseries records | 748,800 | 1,440,000 | +92% |
| Geographic levels | 4 (div/dist/upaz/**union**) | 3 (div/dist/upaz) | -1 |
| SLA violations | 150 | 200 | +50 |
| Packages | 170 | 158 | -12 |
| Subscriber snapshots | 480 | 5,655 | +10× |
| Hypertables | 0 (optional) | 7 (required) | +7 |
| Continuous aggregates | 0 | 3 | +3 |
| Archive size | ~100 MB | ~100 MB | ≈ same |

---

## 1. Schema Changes by Tier

### Tier 1 — Foundation Tables

| Table | v2.8 | v2.11 | Notes |
|-------|------|-------|-------|
| `geo_divisions` | ✅ | ✅ | Added: `bbs_code`, `iso_code`, `bbox`, `govt_url` columns |
| `geo_districts` | ✅ | ✅ | Added: `bbs_code`, `bbox`, `govt_url` columns |
| `geo_upazilas` | ✅ | ✅ | Added: `bbs_code`, `bbox`, `govt_url` columns |
| `geo_unions` | ✅ (4,859 rows) | ❌ **REMOVED** | Entire 4th geo level dropped |
| `isp_license_categories` | ✅ | ✅ | No changes |
| `pop_categories` | ✅ | ✅ | No changes |
| `upstream_types` | ✅ | ✅ | No changes |
| `package_types` | ✅ | ✅ | No changes |
| `connection_types` | ✅ | ✅ | No changes |
| `qos_parameters` | ✅ | ✅ | Moved to Foundation (was Compliance in v2.8) |
| `isps` | ✅ | ✅ | Moved to Master tier |

### Tier 2 — Master / Infrastructure Tables

| Table | v2.8 | v2.11 | Notes |
|-------|------|-------|-------|
| `isps` | ✅ | ✅ | Added: `api_enabled` column |
| `pops` | ✅ | ✅ | Added: `upazila_id` FK (was district-level only), `snmp_enabled` |
| `software_agents` | ✅ | ✅ | UUID now via `gen_random_uuid()` (was `uuid_generate_v4()`) |
| `qos_test_targets` | ✅ | ❌ renamed | → `test_targets` (restructured, see §3) |
| `test_targets` | ❌ | ✅ | Replaces `qos_test_targets` |
| `sla_thresholds` | ✅ | ✅ | Added: `package_type_id` FK, `measurement_period`, `min_samples_required` |
| `snmp_targets` | ❌ | ✅ **NEW** | 120 rows — explicit SNMP OID/interface config |
| `subscriber_count_sources` | ❌ | ✅ **NEW** | 40 rows — per-POP subscriber polling config |

### Tier 3 — Relationships / Product

| Table | v2.8 | v2.11 | Notes |
|-------|------|-------|-------|
| `packages` | ✅ (170 rows) | ✅ (158 rows) | -12 rows; added `connection_type_id` FK, `cir_mbps`, `fup_threshold_gb` |
| `agent_pop_assignments` | ✅ (160 rows) | ✅ (160 rows) | No changes |
| `isp_subscriber_snapshots` | ✅ (480 rows) | ❌ renamed | → `subscriber_snapshots` (structure changed, see §3) |
| `subscriber_snapshots` | ❌ | ✅ (5,655 rows) | Replaces `isp_subscriber_snapshots` |
| `bandwidth_snapshots` | ❌ | ✅ **NEW** (1,560 rows) | Monthly bandwidth per ISP/POP |

### Tier 4 — Timeseries Tables (Biggest Change)

| Table | v2.8 | v2.11 | Notes |
|-------|------|-------|-------|
| `ts_interface_metrics` | ✅ (518,400) | ✅ (518,400) | Schema changed — `id` PK removed; column renames |
| `ts_subscriber_counts` | ✅ (57,600) | ❌ renamed | → `ts_subscriber_session_counts` |
| `ts_subscriber_session_counts` | ❌ | ✅ (57,600) | Replaces `ts_subscriber_counts` |
| `ts_qos_measurements` | ✅ (172,800) | ❌ **SPLIT INTO 5** | Single table → 5 granular tables |
| `ts_qos_speed_tests` | ❌ | ✅ **NEW** (172,800) | download_mbps, upload_mbps, latency |
| `ts_qos_ping_tests` | ❌ | ✅ **NEW** (172,800) | rtt_min/max/avg, jitter, packet_loss |
| `ts_qos_dns_tests` | ❌ | ✅ **NEW** (172,800) | dns queries JSONB, avg_resolution_ms |
| `ts_qos_http_tests` | ❌ | ✅ **NEW** (172,800) | http targets JSONB, reachability_pct |
| `ts_qos_traceroute_tests` | ❌ | ✅ **NEW** (172,800) | hops JSONB, hop_count, path_complete |

### Tier 5 — Compliance Tables

| Table | v2.8 | v2.11 | Notes |
|-------|------|-------|-------|
| `sla_violations` | ✅ (150 rows) | ✅ (200 rows) | Added: `violation_uuid`, `detection_method`, `penalty_applicable`, `penalty_amount_bdt` |
| `compliance_scores` | ❌ | ✅ **NEW** (40 rows) | Per-ISP monthly score card |

---

## 2. Key Column-Level Differences

### `ts_interface_metrics`

| Column | v2.8 | v2.11 |
|--------|------|-------|
| `id` SERIAL PK | ✅ | ❌ removed — time-based partitioning only |
| `timestamp` | `timestamp` | `time` (renamed) |
| `interface_type_id` | ✅ | ❌ → `upstream_type_id` (renamed) |
| `in_octets`, `out_octets` | ✅ | ❌ removed (raw counters dropped) |
| `in_packets`, `out_packets` | ✅ | ❌ removed |
| `in_discards`, `out_discards` | ✅ | ❌ removed |
| `utilization_pct` | single column | split → `utilization_in_pct`, `utilization_out_pct` |
| `interface_status` | ✅ | ❌ removed |
| `collection_method` | ✅ | ❌ removed |
| `snmp_target_id` | ❌ | ✅ new FK to `snmp_targets` |

### `qos_test_targets` (v2.8) → `test_targets` (v2.11)

| Column | v2.8 `qos_test_targets` | v2.11 `test_targets` |
|--------|------------------------|---------------------|
| `host` | ✅ | → `target_host` (renamed) |
| `category` | `TEXT` | → `target_type` ENUM |
| `test_types` | `TEXT[]` (array) | ❌ removed |
| `target_port` | ❌ | ✅ new |
| `target_url` | ❌ | ✅ new |
| `timeout_ms` | ❌ | ✅ new |
| `is_bdix` | ❌ | ✅ new (BOOLEAN) |
| `is_international` | ❌ | ✅ new (BOOLEAN) |

### `isp_subscriber_snapshots` (v2.8) → `subscriber_snapshots` (v2.11)

| Column | v2.8 | v2.11 |
|--------|------|-------|
| `snapshot_month` | `VARCHAR(7)` e.g. "2025-12" | `DATE` e.g. 2025-12-01 |
| `period_start`, `period_end` | ✅ | ❌ removed |
| `residential_count` | ✅ | ❌ removed |
| `business_count` | ✅ | ❌ removed |
| `enterprise_count` | ✅ | ❌ removed |
| `fiber_count`, `dsl_count`, etc. | ✅ | ❌ removed |
| `avg_arpu_bdt`, `total_mrr_bdt` | ✅ | ❌ removed |
| `package_id` FK | ❌ | ✅ new |
| `district_id`, `upazila_id` FK | ❌ | ✅ new (geographic drill-down) |
| `new_subscribers` | ❌ | ✅ new |
| `churned_subscribers` | ❌ | ✅ new |
| `active_subscribers` | ❌ | ✅ new |
| `suspended_subscribers` | ❌ | ✅ new |

### `ts_qos_measurements` (v2.8) → SPLIT in v2.11

v2.8 single table columns now live in separate tables:

| v2.8 column | v2.11 table | v2.11 column |
|-------------|-------------|--------------|
| `download_speed_pct` | `ts_qos_speed_tests` | `download_mbps` (raw value, not %) |
| `upload_speed_pct` | `ts_qos_speed_tests` | `upload_mbps` |
| `latency_ms` | `ts_qos_speed_tests` | `latency_to_server_ms` |
| `packet_loss_pct` | `ts_qos_ping_tests` | `packet_loss_pct` |
| `jitter_ms` | `ts_qos_ping_tests` | `jitter_ms` |
| `dns_lookup_ms` | `ts_qos_dns_tests` | `avg_resolution_ms` |
| `tcp_connect_ms` | `ts_qos_http_tests` | `min_response_ms` |

> ⚠️ **Important:** `download_speed_pct` and `upload_speed_pct` in v2.8 were
> percentage-of-SLA values. v2.11 stores raw `download_mbps` / `upload_mbps`.
> **All Metabase card SQL queries computing speed compliance must be rewritten.**

---

## 3. GeoJSON Compatibility Analysis — CONFIRMED RESULTS ✅

> **Files inspected:** `F.01_geo_divisions.json`, `F.02_geo_districts.json`
> from the extracted `01-foundation.tar.gz` of v2.11.

### Current GeoJSON Setup (React Dashboard)

The React dashboard uses **two custom GeoJSON files** hosted externally:

| Map | GeoJSON File | Match Key |
|-----|-------------|-----------|
| Division choropleth (Card 94) | `bangladesh_divisions_8.geojson` | `NAME_1` property |
| District choropleth (Card 95) | `bgd_districts.geojson` | `shapeName` property |

These GeoJSON files are **independent of the POC database** — they do NOT change
between v2.8 and v2.11.

### Division Names — ✅ UNCHANGED, No React code change needed

All 8 division `name_en` values are **identical** to v2.8:

| id | DB `name_en` (v2.11 confirmed) | `iso_code` | GeoJSON `NAME_1` | Mapping needed? |
|----|-------------------------------|------------|-----------------|-----------------|
| 1 | Barisal | BD-A | Barisal | No |
| 2 | **Chattagram** | BD-B | **Chittagong** | **Yes** (unchanged) |
| 3 | Dhaka | BD-C | Dhaka | No |
| 4 | Khulna | BD-D | Khulna | No |
| 5 | Rajshahi | BD-E | Rajshahi* | No |
| 6 | Rangpur | BD-F | Rangpur | No |
| 7 | Sylhet | BD-G | Sylhet | No |
| 8 | Mymensingh | BD-H | Mymensingh | No |

`DIVISION_NAME_MAPPING` in `src/utils/dataTransform.js` is **still correct** for v2.11.

### District Names — ✅ UNCHANGED, No React code change needed

All 9 mapped district `name_en` values are **identical** to v2.8:

| id | DB `name_en` (v2.11 confirmed) | GeoJSON `shapeName` | Mapping needed? |
|----|-------------------------------|---------------------|-----------------|
| 41 | Bogura | Bogra | Yes (unchanged) |
| 8 | Brahmanbaria | Brahamanbaria | Yes (unchanged) |
| 42 | Chapainawabganj | Nawabganj | Yes (unchanged) |
| 10 | Chattogram | Chittagong | Yes (unchanged) |
| 12 | Coxsbazar | Cox's Bazar | Yes (unchanged) |
| 33 | Jashore | Jessore | Yes (unchanged) |
| 4 | Jhalakathi | Jhalokati | Yes (unchanged) |
| 58 | Moulvibazar | Maulvibazar | Yes (unchanged) |
| 63 | Netrokona | Netrakona | Yes (unchanged) |

`DISTRICT_NAME_MAPPING` in `src/utils/dataTransform.js` is **still correct** for v2.11.

### New: `iso_code` in `geo_divisions` ✅ Confirmed Present

v2.11 `geo_divisions` has a populated `iso_code` field (BD-A … BD-H).
The division choropleth Card 94 can optionally switch from `name_en`-matching to
`iso_code`-matching (`shapeISO` key in Metabase), which removes the Chattagram →
Chittagong mapping requirement entirely.

> **Note:** `geo_districts` has an `iso_code` column but all values are **NULL** in
> v2.11 — cannot be used for district matching. Continue using `shapeName`.

### PostGIS `boundary` Column

Both versions include a PostGIS `boundary` GEOMETRY column on geo tables.
The GeoJSON files used by Metabase are **external** — no action needed.

---

## 3b. 🚨 Critical: POC Date Window Changed

This is the **most impactful** change for the React dashboard.

| | v2.8 | v2.11 |
|--|------|-------|
| Timeseries window | Dec 1–15, 2025 | **Feb 1–15, 2026** |
| SLA violations | Dec 2025 (150 rows) | **Feb 1–15, 2026 (200 rows)** |
| Compliance scores | N/A | **Feb 2026 (40 rows)** |
| Subscriber snapshots | Jan–Dec 2025 | **Feb 2025 – Feb 2026** |
| Bandwidth snapshots | Jan–Dec 2025 | **Feb 2025 – Feb 2026** |

The React `RegulatoryDashboard.jsx` currently hard-codes the POC window as
**Nov 30 – Dec 15, 2025**. With v2.11 data, the date range filter will show
**zero violations** because all violation `detection_time` values are in Feb 2026.

### Files That Must Be Updated in React

**`src/pages/RegulatoryDashboard.jsx`** — update these 3 lines:

```js
// CURRENT (v2.8 window)
const POC_START = dayjs('2025-11-30');
const POC_END   = dayjs('2025-12-15');

// UPDATE TO (v2.11 window)
const POC_START = dayjs('2026-02-01');
const POC_END   = dayjs('2026-02-15');
```

And the date presets:

```js
// CURRENT
const DATE_PRESETS = [
  { label: 'Full Range (POC)', value: [POC_START, POC_END] },          // Nov 30 – Dec 15
  { label: 'First Week',       value: [POC_START, dayjs('2025-12-06')] },
  { label: 'Second Week',      value: [dayjs('2025-12-07'), POC_END] },
  { label: 'Dec 1–7',          value: [dayjs('2025-12-01'), dayjs('2025-12-07')] },
  { label: 'Dec 8–15',         value: [dayjs('2025-12-08'), POC_END] },
];

// UPDATE TO
const DATE_PRESETS = [
  { label: 'Full Range (POC)', value: [POC_START, POC_END] },          // Feb 1–15, 2026
  { label: 'First Week',       value: [POC_START, dayjs('2026-02-07')] },
  { label: 'Second Week',      value: [dayjs('2026-02-08'), POC_END] },
  { label: 'Feb 1–7',          value: [dayjs('2026-02-01'), dayjs('2026-02-07')] },
  { label: 'Feb 8–15',         value: [dayjs('2026-02-08'), POC_END] },
];
```

Also update the "no date selected" label:
```js
// CURRENT
'Showing all POC data (Nov 30 – Dec 15, 2025)'
// UPDATE TO
'Showing all POC data (Feb 1 – Feb 15, 2026)'
```

### sla_violations — New Columns in v2.11

v2.11 adds significant new columns to `sla_violations`. Cards 82-87 that currently
work with v2.8's 12-column structure may benefit from these additions:

| Column | v2.8 | v2.11 | Dashboard use |
|--------|------|-------|--------------|
| `violation_uuid` | ❌ | ✅ | Unique shareable ID |
| `sla_threshold_id` | ❌ | ✅ | FK to thresholds |
| `violation_start` / `violation_end` | ❌ | ✅ | Duration calculation |
| `measurement_period_start/end` | ❌ | ✅ | Exact measurement window |
| `sample_count` | ❌ | ✅ | Statistical confidence |
| `affected_subscribers_est` | ❌ | ✅ (was `affected_subscribers`) | Already shown in Card 85 |
| `evidence_summary` | ❌ | ✅ | Human-readable detail |
| `isp_notified_at` | ❌ | ✅ | SLA response tracking |
| `isp_response` / `isp_response_at` | ❌ | ✅ | ISP acknowledgement |
| `dispute_reason` | ❌ | ✅ | Dispute workflow |
| `resolved_at` / `resolved_by` | ❌ | ✅ | Resolution audit |
| `penalty_applicable` | ❌ | ✅ | Penalty workflow |
| `penalty_amount_bdt` | ❌ | ✅ | Financial data |
| `penalty_status` | ❌ | ✅ | PENDING / PAID / WAIVED |

### compliance_scores — New Table in v2.11

22-column table with per-ISP monthly compliance data. Not yet used in React.

Key columns: `isp_id`, `score_month`, `overall_score` (0-100), `speed_score`,
`latency_score`, `availability_score`, `reporting_score`, `total_violations`,
`critical_violations`, `compliance_rank`, `compliance_tier`, `trend_direction`,
`trend_change_pct`.

---

## 4. React Dashboard Impact — Card-by-Card Analysis

All Metabase cards currently query v2.8 table names. After loading v2.11 data
into a fresh DB, every card below needs SQL updates.

| Card | Current Query (v2.8) | v2.11 Change Required |
|------|---------------------|-----------------------|
| 76 SLA Compliant ISPs | `sla_violations` | ✅ Same table; verify new columns |
| 77 At-Risk ISPs | `sla_violations` | ✅ Same table; verify |
| 78 Violation ISPs | `sla_violations` | ✅ Same table; verify |
| 79 Division Performance Summary | `ts_qos_measurements` | ❌ → `ts_qos_speed_tests` + `ts_qos_ping_tests` |
| 80 District Ranking Table | `ts_qos_measurements` | ❌ → `ts_qos_speed_tests` + `ts_qos_ping_tests` |
| 81 ISP Performance by Area | `ts_qos_measurements` | ❌ → multiple tables |
| 82 Pending Violations | `sla_violations` | ✅ Same table |
| 83 Active/Disputed Violations | `sla_violations` | ✅ Same table |
| 84 Resolved Violations | `sla_violations` | ✅ Same table |
| 85 Violation Detail Table | `sla_violations` | ✅ Same table; new columns available |
| 86 Violation Trend by Severity | `sla_violations` | ✅ Same table |
| 87 Violations by Geography | `sla_violations` + geo | ✅ Same table |
| 94 Division Performance Map | `ts_qos_measurements` | ❌ → `ts_qos_speed_tests` |
| 95 District Performance Map | `ts_qos_measurements` | ❌ → `ts_qos_speed_tests` |
| 97-99 Additional SLA cards | `sla_thresholds` + `ts_qos_measurements` | ❌ Partial rewrite |

> ⚠️ Cards 79, 80, 81, 94, 95 are the most used in the React dashboard.
> All 5 require SQL rewrites due to `ts_qos_measurements` → split tables.

---

## 5. Missing / Unverified Fields in v2.11

These items need confirmation after extracting the v2.11 tar files:

| # | Item to Verify | Why It Matters |
|---|---------------|----------------|
| 1 | `name_en` values in `F.01_geo_divisions.json` | Division choropleth name mapping |
| 2 | `name_en` values in `F.02_geo_districts.json` | District choropleth name mapping |
| 3 | `iso_code` field present in `F.01_geo_divisions.json` | Can replace name mapping with ISO code matching |
| 4 | `sla_violations` column list in `C.01_sla_violations.json` | Cards 82-87 depend on these columns |
| 5 | `pops.district_id` still present (not replaced by upazila_id) | Cards 79, 80, 87 JOIN pops → geo_districts |
| 6 | `isps.name_en` values unchanged (40 ISPs, same names) | ISP filter dropdown, Card 81 |
| 7 | `compliance_scores` columns in `C.02_compliance_scores.json` | New — not yet used in React dashboard |
| 8 | Continuous aggregate view names | Can speed up Cards 94, 95 significantly |

---

## 6. What the React Dashboard Does NOT Need to Change

These items are unaffected by v2.8 → v2.11 migration:

- ✅ GeoJSON files (external, unchanged)
- ✅ Leaflet choropleth rendering logic
- ✅ `src/utils/dataTransform.js` → `transformToGeoJSON()`, `applyNameMapping()` (unless names changed)
- ✅ `src/api/metabase.js` — API client works with any Metabase card
- ✅ `src/config/permissions.js` — group IDs and rules unchanged
- ✅ `src/contexts/AuthContext.jsx` — login flow unchanged
- ✅ All UI components (charts, tables, filters)
- ✅ Date range filter (`start_date` / `end_date` template tags)
- ✅ Division / District / ISP filter dropdowns (UI logic unchanged)
- ✅ POC date window: Nov 30 – Dec 15, 2025 (same in both versions)

---

## 7. New Features Available in v2.11 (Not Yet Used by React)

| Feature | v2.11 Table | Potential Dashboard Use |
|---------|-------------|------------------------|
| `compliance_scores` | `compliance_scores` | New "Compliance Score" card per ISP per month |
| `bandwidth_snapshots` | `bandwidth_snapshots` | International vs. IX vs. cache bandwidth trend |
| Geographic subscriber data | `subscriber_snapshots` (district_id) | Subscribers per district choropleth |
| SNMP interface config | `snmp_targets` | ISP infrastructure explorer |
| Upazila-level POP location | `pops.upazila_id` | Finer-grained regional map drill-down |
| Hourly aggregates | `ts_qos_speed_tests_hourly` | Faster Card 94/95 queries (no full scan) |

---

## 8. Questions for the Frontend Engineer

Questions marked ✅ CONFIRMED have been answered by inspecting the extracted
v2.11 JSON files. Open questions remain for the frontend engineer.

---

### GeoJSON / Choropleth — CONFIRMED ✅

**Q1. ✅ CONFIRMED — No change needed.**
`F.01_geo_divisions.json` uses the **same** `name_en` values as v2.8.
Division 2 is still "Chattagram" (not "Chittagong").
`DIVISION_NAME_MAPPING` in `dataTransform.js` is still correct.

**Q2. ✅ CONFIRMED — `iso_code` is present.**
All 8 divisions have populated `iso_code` values (BD-A … BD-H).
Metabase Card 94 can be updated to use `iso_code` → `shapeISO` matching
to eliminate the name-mapping dependency. (Optional improvement.)

**Q3. ✅ CONFIRMED — No change needed.**
All 64 district `name_en` values are identical to v2.8.
All 9 mapped districts are unchanged. `DISTRICT_NAME_MAPPING` is still correct.

---

### New Open Questions

---

### Timeseries Query Rewrites

**Q4.** Cards 79, 80, 81, 94, 95 currently query `ts_qos_measurements` which
**does not exist in v2.11**. It is split into `ts_qos_speed_tests`,
`ts_qos_ping_tests`, `ts_qos_dns_tests`, `ts_qos_http_tests`, and
`ts_qos_traceroute_tests`.

Which metrics does each card currently show?
- Average download speed → comes from `ts_qos_measurements.download_speed_pct` (v2.8 %)
  → should now come from `ts_qos_speed_tests.download_mbps` (v2.11 raw Mbps)
- Do you want to continue showing percentage-of-SLA or switch to raw Mbps?
- If percentage: need to JOIN `sla_thresholds` to compute it

**Q5.** The `ts_interface_metrics` table lost the `id` SERIAL primary key in v2.11.
Some Metabase cards may use `ORDER BY id` or `GROUP BY id`. Confirm none of
the existing card SQL uses the `id` column from this table.

---

### Table / Column Renames

**Q6.** Cards that JOIN through `pops` to get district names:
- v2.8: `pops.district_id → geo_districts.name_en`
- v2.11: `pops` now also has `upazila_id`

Do any cards need upazila-level filtering, or is district-level still sufficient?

**Q7.** `ts_subscriber_counts` was renamed to `ts_subscriber_session_counts` in v2.11.
Are there any Metabase cards (outside Cards 76-99) that reference
`ts_subscriber_counts` by name?

---

### New Data Opportunities

**Q8.** v2.11 adds a `compliance_scores` table (per-ISP monthly score, rank, tier,
trend_direction). Should we add a new Metabase card and React component for this?
Suggested placement: a new card on the SLA Monitoring tab (R2.1).

**Q9.** `subscriber_snapshots` in v2.11 now has `district_id` and `upazila_id`,
enabling a **"Subscribers per District" choropleth**. Is this in scope for the
current dashboard?

**Q10.** v2.11 creates three **continuous aggregate views**:
- `ts_interface_metrics_hourly`
- `ts_qos_speed_tests_hourly`
- `ts_qos_ping_tests_hourly`

Cards 94 and 95 (choropleth maps) query large timeseries tables and are the
slowest cards. Should we update their SQL to query the hourly aggregate views
instead of the raw hypertables? This would give a significant performance boost.

---

### Data Loader / Docker

**Q11.** The v2.11 loader (`load_poc_data.py`) uses `OVERRIDING SYSTEM VALUE` for
SERIAL tables. The current Docker compose setup runs `init_metabase_users.py`
**after** Metabase is healthy. The DB data loading is separate.
Should `load_poc_data.py` be added as another one-shot Docker service
(similar to `metabase-init`) so it runs automatically on fresh deployments?

---

## 9. Recommended Migration Steps

### Step 1 — Database (already extractable)
- [x] Extract all `.tar.gz` files from `poc_data_v2.11/`
- [ ] Load schema: `psql -U btrc_admin btrc_qos_poc < poc_schema_v2.11.sql`
- [ ] Load data: `python3 load_poc_data.py /path/to/poc_data_v2.11/`
- [ ] Verify record counts match §1 table

### Step 2 — React Dashboard (date window, 2 lines)
- [ ] Update `RegulatoryDashboard.jsx`: `POC_START = dayjs('2026-02-01')`, `POC_END = dayjs('2026-02-15')`
- [ ] Update `DATE_PRESETS` labels: Dec → Feb
- [ ] Update "no date" tag text: "Feb 1 – Feb 15, 2026"

### Step 3 — Metabase SQL (table renames)
- [ ] Rewrite Cards 79, 80, 81: `ts_qos_measurements` → `ts_qos_speed_tests` + `ts_qos_ping_tests`
- [ ] Rewrite Cards 94, 95: `ts_qos_measurements` → `ts_qos_speed_tests`
- [ ] Rename `ts_subscriber_counts` → `ts_subscriber_session_counts` in any card that uses it
- [ ] Rename `isp_subscriber_snapshots` → `subscriber_snapshots` in any card that uses it
- [ ] Rename `qos_test_targets` → `test_targets`

### Step 4 — No changes needed
- [x] `DIVISION_NAME_MAPPING` — still correct (division names unchanged)
- [x] `DISTRICT_NAME_MAPPING` — still correct (district names unchanged)
- [x] All choropleth React components — no changes needed
- [x] All UI components — no changes needed
- [x] Auth / permissions — no changes needed

### Step 5 — Optional improvements (v2.11 bonuses)
- [ ] Card 94: Switch to `iso_code` → `shapeISO` matching (removes name mapping dependency)
- [ ] New card: `compliance_scores` on SLA tab (overall_score, rank, tier, trend)
- [ ] New card: `penalty_amount_bdt` from `sla_violations` (financial view)
- [ ] Use `ts_qos_speed_tests_hourly` aggregate view for faster Cards 94/95

---

*This document was generated by comparing schema files, data loading guides, and tar archive listings from both POC versions. Actual data file contents (JSON) should be inspected to confirm all name/value assumptions marked ⚠️.*
