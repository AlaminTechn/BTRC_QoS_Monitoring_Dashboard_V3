# R1 Charts - Schema-Compliant SQL Queries

**Date:** 2026-02-10
**Status:** ✅ **SCHEMA COMPLIANT**
**Schema Source:** `poc_data_v2.8/02_DB_Schema_Creation_v2.8.md`

---

## Important Schema Differences

### Tables That DON'T Exist in Schema

The spec references tables that are NOT in the actual schema:

| Spec References | Actual Schema | Solution |
|----------------|---------------|----------|
| ❌ `alerts` table | ✅ `sla_violations` table | Use sla_violations |
| ❌ `incidents` table | ✅ `sla_violations` table | Use sla_violations with pop_id |
| ❌ `ts_qos_measurements.package_id` | ✅ Only has `isp_id` | Join via isp_id |

---

## Tables That DO Exist

From `poc_data_v2.8/02_DB_Schema_Creation_v2.8.md`:

```
✅ geo_divisions
✅ geo_districts
✅ geo_upazilas
✅ geo_unions
✅ isp_license_categories
✅ isps
✅ pop_categories
✅ pops
✅ software_agents
✅ qos_test_targets
✅ upstream_types
✅ package_types
✅ connection_types
✅ qos_parameters
✅ sla_thresholds
✅ packages
✅ agent_pop_assignments
✅ isp_subscriber_snapshots
✅ ts_interface_metrics
✅ ts_subscriber_counts
✅ ts_qos_measurements
✅ sla_violations
```

---

## R1.4: Package Compliance Matrix (Card 97)

### Spec Requirement
```
Table comparing target vs actual speed by package tier
Data Source: ts_qos_measurements JOIN packages
Method: AVG(measured_speed) GROUP BY package_tier vs packages.download_speed_mbps
```

### Schema Challenge
- ❌ `ts_qos_measurements` does NOT have `package_id` column
- ✅ `ts_qos_measurements` has: `isp_id`, `download_speed_mbps`, `upload_speed_mbps`
- ✅ `packages` has: `id`, `isp_id`, `download_speed_mbps`, `upload_speed_mbps`

### Solution
Join via `isp_id` and group packages by tier

### Final SQL

```sql
-- R1.4: Package Compliance Matrix
-- Compares target vs actual speed by package tier
-- Note: ts_qos_measurements doesn't have package_id, so we aggregate by ISP and package tier

WITH package_tiers AS (
    SELECT
        p.isp_id,
        CASE
            WHEN p.download_speed_mbps < 10 THEN '0-10 Mbps'
            WHEN p.download_speed_mbps >= 10 AND p.download_speed_mbps < 25 THEN '10-25 Mbps'
            WHEN p.download_speed_mbps >= 25 AND p.download_speed_mbps < 50 THEN '25-50 Mbps'
            WHEN p.download_speed_mbps >= 50 AND p.download_speed_mbps < 100 THEN '50-100 Mbps'
            WHEN p.download_speed_mbps >= 100 AND p.download_speed_mbps < 200 THEN '100-200 Mbps'
            ELSE '200+ Mbps'
        END as package_tier,
        AVG(p.download_speed_mbps) as avg_target_download,
        AVG(p.upload_speed_mbps) as avg_target_upload,
        COUNT(*) as package_count
    FROM packages p
    WHERE p.is_active = true
    GROUP BY p.isp_id, package_tier
),
measured_by_isp AS (
    SELECT
        m.isp_id,
        AVG(m.download_speed_mbps) as avg_measured_download,
        AVG(m.upload_speed_mbps) as avg_measured_upload,
        COUNT(*) as measurement_count
    FROM ts_qos_measurements m
    WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
        AND m.test_status = 'SUCCESS'
    GROUP BY m.isp_id
)
SELECT
    pt.package_tier as "Package Tier",
    ROUND(AVG(pt.avg_target_download)::numeric, 2) as "Target Download (Mbps)",
    ROUND(AVG(COALESCE(mp.avg_measured_download, 0))::numeric, 2) as "Actual Download (Mbps)",
    ROUND((AVG(COALESCE(mp.avg_measured_download, 0)) / NULLIF(AVG(pt.avg_target_download), 0) * 100)::numeric, 2) as "Download Achievement %",
    ROUND(AVG(pt.avg_target_upload)::numeric, 2) as "Target Upload (Mbps)",
    ROUND(AVG(COALESCE(mp.avg_measured_upload, 0))::numeric, 2) as "Actual Upload (Mbps)",
    ROUND((AVG(COALESCE(mp.avg_measured_upload, 0)) / NULLIF(AVG(pt.avg_target_upload), 0) * 100)::numeric, 2) as "Upload Achievement %",
    SUM(pt.package_count) as "Packages in Tier",
    SUM(COALESCE(mp.measurement_count, 0)) as "Total Measurements"
FROM package_tiers pt
LEFT JOIN measured_by_isp mp ON pt.isp_id = mp.isp_id
GROUP BY pt.package_tier
ORDER BY
    CASE pt.package_tier
        WHEN '0-10 Mbps' THEN 1
        WHEN '10-25 Mbps' THEN 2
        WHEN '25-50 Mbps' THEN 3
        WHEN '50-100 Mbps' THEN 4
        WHEN '100-200 Mbps' THEN 5
        WHEN '200+ Mbps' THEN 6
    END;
```

### Schema Used
```sql
-- ts_qos_measurements
id, agent_id, isp_id, test_target_id, timestamp,
download_speed_mbps, upload_speed_mbps, test_status

-- packages
id, isp_id, package_type_id, connection_type_id,
download_speed_mbps, upload_speed_mbps, is_active
```

---

## R1.5: Real-Time Threshold Alerts (Card 98)

### Spec Requirement
```
Live scrolling alert list
Data Source: alerts JOIN sla_thresholds
Method: SELECT * FROM alerts WHERE status = 'OPEN'
```

### Schema Challenge
- ❌ `alerts` table does NOT exist in schema!
- ✅ `sla_violations` table DOES exist with similar data

### Solution
Use `sla_violations` table instead of non-existent `alerts` table

### Final SQL

```sql
-- R1.5: Real-Time Threshold Alerts
-- Using sla_violations table (alerts table doesn't exist in schema)
-- Schema: sla_violations has id, isp_id, qos_parameter_id, violation_type, severity,
--         detection_time, expected_value, actual_value, status

SELECT
    i.name_en as "ISP",
    v.violation_type as "Metric",
    qp.name_en as "Parameter",
    ROUND(v.expected_value::numeric, 2) as "Threshold",
    ROUND(v.actual_value::numeric, 2) as "Actual Value",
    ROUND(v.deviation_pct::numeric, 2) as "Deviation %",
    CASE
        WHEN EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 60 < 60 THEN
            ROUND((EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 60)::numeric, 0) || ' min'
        WHEN EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 3600 < 24 THEN
            ROUND((EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 3600)::numeric, 1) || ' hrs'
        ELSE
            ROUND((EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 86400)::numeric, 1) || ' days'
    END as "Duration",
    CASE
        WHEN v.severity = 'CRITICAL' THEN '🔴 Critical'
        WHEN v.severity = 'HIGH' THEN '🟠 High'
        WHEN v.severity = 'MEDIUM' THEN '🟡 Medium'
        ELSE '🟢 Low'
    END as "Severity",
    v.status as "Status",
    TO_CHAR(v.detection_time, 'YYYY-MM-DD HH24:MI') as "Detected At"
FROM sla_violations v
JOIN isps i ON v.isp_id = i.id
JOIN qos_parameters qp ON v.qos_parameter_id = qp.id
WHERE v.status IN ('DETECTED', 'ACKNOWLEDGED', 'UNDER_REVIEW')
    AND v.detection_time >= NOW() - INTERVAL '24 hours'
ORDER BY
    CASE v.severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    v.detection_time DESC
LIMIT 50;
```

### Schema Used
```sql
-- sla_violations
id, violation_uuid, isp_id, pop_id, qos_parameter_id, sla_threshold_id,
violation_type, severity, detection_method, detection_time,
expected_value, actual_value, deviation_pct, status

-- isps
id, name_en, name_bn, btrc_license_no

-- qos_parameters
id, code, name_en, name_bn, metric_type
```

---

## R1.6: PoP-Level Violations Table (Card 99)

### Spec Requirement
```
Sortable table with incident details
Data Source: incidents JOIN pops JOIN isps
Method: SELECT * FROM incidents WHERE status IN ('OPEN','ACKNOWLEDGED')
```

### Schema Challenge
- ❌ `incidents` table does NOT exist in schema!
- ✅ `sla_violations` table has `pop_id` column

### Solution
Use `sla_violations` filtered by `pop_id IS NOT NULL` to show PoP-level violations

### Final SQL

```sql
-- R1.6: PoP-Level Violations Table
-- Using sla_violations table (incidents table doesn't exist in schema)
-- Showing violations that have a pop_id associated

SELECT
    v.id as "Violation ID",
    i.name_en as "ISP",
    p.name_en as "PoP Location",
    d.name_en as "District",
    dv.name_en as "Division",
    v.violation_type as "Violation Type",
    qp.name_en as "QoS Parameter",
    CASE
        WHEN v.status = 'DETECTED' THEN '🔴 Detected'
        WHEN v.status = 'ACKNOWLEDGED' THEN '🟡 Acknowledged'
        WHEN v.status = 'UNDER_REVIEW' THEN '🟠 Under Review'
        WHEN v.status = 'RESOLVED' THEN '🟢 Resolved'
        WHEN v.status = 'DISPUTED' THEN '🔵 Disputed'
        ELSE v.status
    END as "Status",
    v.severity as "Severity",
    ROUND(v.expected_value::numeric, 2) as "Expected",
    ROUND(v.actual_value::numeric, 2) as "Actual",
    TO_CHAR(v.detection_time, 'YYYY-MM-DD HH24:MI') as "Detected",
    CASE
        WHEN v.resolved_at IS NOT NULL THEN TO_CHAR(v.resolved_at, 'YYYY-MM-DD HH24:MI')
        ELSE '-'
    END as "Resolved",
    CASE
        WHEN v.resolved_at IS NOT NULL THEN
            ROUND((EXTRACT(EPOCH FROM (v.resolved_at - v.detection_time)) / 3600)::numeric, 2) || ' hrs'
        ELSE
            ROUND((EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 3600)::numeric, 2) || ' hrs'
    END as "Duration"
FROM sla_violations v
JOIN isps i ON v.isp_id = i.id
LEFT JOIN pops p ON v.pop_id = p.id
LEFT JOIN geo_districts d ON p.district_id = d.id
LEFT JOIN geo_divisions dv ON d.division_id = dv.id
JOIN qos_parameters qp ON v.qos_parameter_id = qp.id
WHERE v.pop_id IS NOT NULL  -- Only show violations associated with a PoP
    AND v.detection_time >= NOW() - INTERVAL '7 days'
ORDER BY
    CASE v.status
        WHEN 'DETECTED' THEN 1
        WHEN 'ACKNOWLEDGED' THEN 2
        WHEN 'UNDER_REVIEW' THEN 3
        ELSE 4
    END,
    v.detection_time DESC
LIMIT 100;
```

### Schema Used
```sql
-- sla_violations
id, isp_id, pop_id, qos_parameter_id, violation_type, severity,
detection_time, expected_value, actual_value, status, resolved_at

-- pops
id, isp_id, name_en, name_bn, district_id, status

-- geo_districts
id, division_id, name_en, name_bn

-- geo_divisions
id, name_en, name_bn
```

---

## Complete Schema Reference

### ts_qos_measurements
```sql
CREATE TABLE ts_qos_measurements (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES software_agents(id),
    isp_id INTEGER NOT NULL REFERENCES isps(id),
    test_target_id INTEGER REFERENCES qos_test_targets(id),
    timestamp TIMESTAMPTZ NOT NULL,
    test_uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    download_speed_mbps DECIMAL(10,2),
    upload_speed_mbps DECIMAL(10,2),
    download_speed_pct DECIMAL(5,2),
    upload_speed_pct DECIMAL(5,2),
    latency_ms DECIMAL(10,2),
    packet_loss_pct DECIMAL(5,3),
    jitter_ms DECIMAL(10,2),
    dns_lookup_ms DECIMAL(10,2),
    tcp_connect_ms DECIMAL(10,2),
    test_duration_sec DECIMAL(8,2),
    test_status VARCHAR(20) DEFAULT 'SUCCESS',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### packages
```sql
CREATE TABLE packages (
    id SERIAL PRIMARY KEY,
    isp_id INTEGER NOT NULL REFERENCES isps(id),
    package_type_id INTEGER REFERENCES package_types(id),
    connection_type_id INTEGER REFERENCES connection_types(id),
    code VARCHAR(50) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    name_bn VARCHAR(200),
    description TEXT,
    download_speed_mbps DECIMAL(10,2) NOT NULL,
    upload_speed_mbps DECIMAL(10,2) NOT NULL,
    mir_mbps DECIMAL(10,2),
    cir_mbps DECIMAL(10,2),
    data_cap_gb INTEGER,
    contention_ratio VARCHAR(20),
    monthly_price_bdt DECIMAL(10,2),
    setup_fee_bdt DECIMAL(10,2),
    is_fup_applicable BOOLEAN DEFAULT false,
    fup_threshold_gb INTEGER,
    fup_reduced_speed_mbps DECIMAL(10,2),
    min_contract_months INTEGER,
    launch_date DATE,
    discontinue_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    UNIQUE(isp_id, code)
);
```

### sla_violations
```sql
CREATE TABLE sla_violations (
    id SERIAL PRIMARY KEY,
    violation_uuid UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    isp_id INTEGER NOT NULL REFERENCES isps(id),
    pop_id INTEGER REFERENCES pops(id),
    qos_parameter_id INTEGER NOT NULL REFERENCES qos_parameters(id),
    sla_threshold_id INTEGER REFERENCES sla_thresholds(id),
    violation_type VARCHAR(20) NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    detection_method VARCHAR(30) NOT NULL,
    detection_time TIMESTAMPTZ NOT NULL,
    violation_start TIMESTAMPTZ,
    violation_end TIMESTAMPTZ,
    measurement_period_start TIMESTAMPTZ,
    measurement_period_end TIMESTAMPTZ,
    expected_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    deviation_pct DECIMAL(6,2),
    sample_count INTEGER,
    affected_subscribers_est INTEGER,
    evidence_summary TEXT,
    evidence_data JSONB,
    status VARCHAR(20) DEFAULT 'DETECTED',
    isp_notified_at TIMESTAMPTZ,
    isp_response TEXT,
    isp_response_at TIMESTAMPTZ,
    dispute_reason TEXT,
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(50),
    penalty_applicable BOOLEAN DEFAULT false,
    penalty_amount_bdt DECIMAL(15,2),
    penalty_status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
```

---

## Testing Queries

### Check if data exists

```sql
-- Check packages by tier
SELECT
    CASE
        WHEN download_speed_mbps < 10 THEN '0-10 Mbps'
        WHEN download_speed_mbps >= 10 AND download_speed_mbps < 25 THEN '10-25 Mbps'
        WHEN download_speed_mbps >= 25 AND download_speed_mbps < 50 THEN '25-50 Mbps'
        WHEN download_speed_mbps >= 50 AND download_speed_mbps < 100 THEN '50-100 Mbps'
        WHEN download_speed_mbps >= 100 AND download_speed_mbps < 200 THEN '100-200 Mbps'
        ELSE '200+ Mbps'
    END as tier,
    COUNT(*) as count
FROM packages
WHERE is_active = true
GROUP BY tier
ORDER BY tier;

-- Check measurements
SELECT COUNT(*) as total_measurements FROM ts_qos_measurements;

-- Check violations
SELECT COUNT(*) as total_violations FROM sla_violations;

-- Check violations with pop_id
SELECT COUNT(*) as pop_violations
FROM sla_violations
WHERE pop_id IS NOT NULL;
```

---

## Summary

✅ **All 3 cards now use correct schema**
✅ **No non-existent tables referenced**
✅ **All column names match actual database**
✅ **Queries tested and working**

### Key Changes:
1. **R1.4**: Join packages to measurements via `isp_id` (not package_id)
2. **R1.5**: Use `sla_violations` instead of `alerts` table
3. **R1.6**: Use `sla_violations` with `pop_id` instead of `incidents` table

**Dashboard:** http://localhost:3000/dashboard/6
**Tab:** R2.1: SLA Monitoring

---

**Status:** ✅ SCHEMA COMPLIANT
**Date:** 2026-02-10

---

**End of Document**
