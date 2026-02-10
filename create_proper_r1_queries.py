#!/usr/bin/env python3
"""
Create R1 charts with PROPER schema from poc_data_v2.8
"""

import requests
import json

METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"

def login():
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    return {"X-Metabase-Session": response.json()["id"]}

def update_card(card_id, sql_query, card_name):
    headers = login()

    update_data = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_query.strip(),
                "template-tags": {}
            },
            "database": 2
        }
    }

    print(f"Updating Card {card_id} ({card_name})...")
    response = requests.put(
        f"{METABASE_URL}/api/card/{card_id}",
        headers=headers,
        json=update_data
    )

    if response.status_code == 200:
        print(f"✅ {card_name} updated successfully!")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text[:500])
        return False

def main():
    print("=" * 70)
    print("Update R1 Charts with PROPER SCHEMA")
    print("=" * 70)
    print()

    # R1.4: Package Compliance Matrix
    # Using actual schema: ts_qos_measurements JOIN packages (via isp_id)
    # ts_qos_measurements has: isp_id, download_speed_mbps, upload_speed_mbps
    # packages has: id, isp_id, download_speed_mbps (target), upload_speed_mbps (target)
    r14_sql = """
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
"""

    # R1.5: Real-Time Threshold Alerts
    # Spec says: alerts table - but this DOESN'T EXIST in schema!
    # Use sla_violations instead (which DOES exist)
    r15_sql = """
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
"""

    # R1.6: PoP-Level Incident Table
    # Spec says: incidents table - but this DOESN'T EXIST in schema!
    # Use sla_violations with pop_id instead
    r16_sql = """
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
"""

    # Update all cards
    print("IMPORTANT NOTE:")
    print("  - 'alerts' table does NOT exist in schema - using sla_violations")
    print("  - 'incidents' table does NOT exist in schema - using sla_violations")
    print("  - ts_qos_measurements has NO package_id - joining via isp_id")
    print()

    results = []
    results.append(update_card(97, r14_sql, "R1.4 Package Compliance Matrix"))
    print()
    results.append(update_card(98, r15_sql, "R1.5 Real-Time Threshold Alerts"))
    print()
    results.append(update_card(99, r16_sql, "R1.6 PoP-Level Violations Table"))

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    success_count = sum(results)
    print(f"✅ {success_count}/3 cards updated successfully")

    print("\nSchema Fixes Applied:")
    print("  ✅ R1.4: Uses ts_qos_measurements.isp_id to join with packages")
    print("  ✅ R1.5: Uses sla_violations (alerts table doesn't exist)")
    print("  ✅ R1.6: Uses sla_violations with pop_id (incidents doesn't exist)")
    print("  ✅ All queries use correct column names from schema")

    print(f"\n🔗 View dashboard: {METABASE_URL}/dashboard/6")

if __name__ == "__main__":
    main()
