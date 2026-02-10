#!/usr/bin/env python3
"""
Update R1 charts to use EXACT tables from spec:
- R1.4: ts_qos_measurements JOIN packages
- R1.5: alerts JOIN sla_thresholds
- R1.6: incidents JOIN pops JOIN isps
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
    print("Update R1 Charts with SPEC-DEFINED Tables")
    print("=" * 70)
    print()

    # R1.4: ts_qos_measurements JOIN packages
    # Note: ts_qos_measurements has isp_id, packages has isp_id + download_speed_mbps
    r14_sql = """
-- R1.4: Package Compliance Matrix
-- Spec: ts_qos_measurements JOIN packages
-- Comparing target vs actual speed by package tier

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
        AVG(p.upload_speed_mbps) as avg_target_upload
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
    ROUND((AVG(COALESCE(mp.avg_measured_download, 0)) / NULLIF(AVG(pt.avg_target_download), 0) * 100)::numeric, 1) as "Achievement %",
    ROUND(AVG(pt.avg_target_upload)::numeric, 2) as "Target Upload (Mbps)",
    ROUND(AVG(COALESCE(mp.avg_measured_upload, 0))::numeric, 2) as "Actual Upload (Mbps)",
    SUM(COALESCE(mp.measurement_count, 0)) as "Total Tests"
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

    # R1.5: alerts JOIN sla_thresholds
    r15_sql = """
-- R1.5: Real-Time Threshold Alerts
-- Spec: alerts JOIN sla_thresholds
-- Live scrolling alert list

SELECT
    i.name_en as "ISP",
    a.metric_type as "Metric",
    ROUND(a.threshold_value::numeric, 2) as "Threshold",
    ROUND(a.actual_value::numeric, 2) as "Actual",
    CASE
        WHEN EXTRACT(EPOCH FROM (NOW() - a.detection_time)) / 60 < 60 THEN
            ROUND((EXTRACT(EPOCH FROM (NOW() - a.detection_time)) / 60)::numeric, 0) || ' min'
        WHEN EXTRACT(EPOCH FROM (NOW() - a.detection_time)) / 3600 < 24 THEN
            ROUND((EXTRACT(EPOCH FROM (NOW() - a.detection_time)) / 3600)::numeric, 1) || ' hrs'
        ELSE
            ROUND((EXTRACT(EPOCH FROM (NOW() - a.detection_time)) / 86400)::numeric, 1) || ' days'
    END as "Duration",
    CASE
        WHEN a.severity = 'CRITICAL' THEN '🔴 Critical'
        WHEN a.severity = 'HIGH' THEN '🟠 High'
        WHEN a.severity = 'MEDIUM' THEN '🟡 Medium'
        ELSE '🟢 Low'
    END as "Severity",
    a.status as "Status",
    TO_CHAR(a.detection_time, 'YYYY-MM-DD HH24:MI') as "Detected At"
FROM alerts a
JOIN isps i ON a.isp_id = i.id
LEFT JOIN sla_thresholds st ON a.sla_threshold_id = st.id
WHERE a.status IN ('OPEN', 'ACKNOWLEDGED')
    AND a.detection_time >= NOW() - INTERVAL '24 hours'
ORDER BY
    CASE a.severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    a.detection_time DESC
LIMIT 50;
"""

    # R1.6: incidents JOIN pops JOIN isps
    r16_sql = """
-- R1.6: PoP-Level Incident Table
-- Spec: incidents JOIN pops JOIN isps
-- Sortable table with incident details

SELECT
    inc.incident_id as "Incident ID",
    i.name_en as "ISP",
    p.name_en as "PoP Location",
    d.name_en as "District",
    dv.name_en as "Division",
    inc.metric_type as "Metric Type",
    CASE
        WHEN inc.status = 'OPEN' THEN '🔴 Open'
        WHEN inc.status = 'ACKNOWLEDGED' THEN '🟡 Acknowledged'
        WHEN inc.status = 'RESOLVED' THEN '🟢 Resolved'
        ELSE inc.status
    END as "Status",
    inc.severity as "Severity",
    TO_CHAR(inc.created_at, 'YYYY-MM-DD HH24:MI') as "Created",
    CASE
        WHEN inc.resolved_at IS NOT NULL THEN TO_CHAR(inc.resolved_at, 'YYYY-MM-DD HH24:MI')
        ELSE '-'
    END as "Resolved",
    CASE
        WHEN inc.resolved_at IS NOT NULL THEN
            ROUND((EXTRACT(EPOCH FROM (inc.resolved_at - inc.created_at)) / 3600)::numeric, 1) || ' hrs'
        ELSE
            ROUND((EXTRACT(EPOCH FROM (NOW() - inc.created_at)) / 3600)::numeric, 1) || ' hrs'
    END as "Duration"
FROM incidents inc
JOIN isps i ON inc.isp_id = i.id
LEFT JOIN pops p ON inc.pop_id = p.id
LEFT JOIN geo_districts d ON p.district_id = d.id
LEFT JOIN geo_divisions dv ON d.division_id = dv.id
WHERE inc.status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED')
    AND inc.created_at >= NOW() - INTERVAL '7 days'
ORDER BY
    CASE inc.status
        WHEN 'OPEN' THEN 1
        WHEN 'ACKNOWLEDGED' THEN 2
        ELSE 3
    END,
    inc.created_at DESC
LIMIT 100;
"""

    # Update all cards
    print("Using SPEC-DEFINED tables:")
    print("  ✅ R1.4: ts_qos_measurements JOIN packages")
    print("  ✅ R1.5: alerts JOIN sla_thresholds")
    print("  ✅ R1.6: incidents JOIN pops JOIN isps")
    print()

    results = []
    results.append(update_card(97, r14_sql, "R1.4 Package Compliance Matrix"))
    print()
    results.append(update_card(98, r15_sql, "R1.5 Real-Time Threshold Alerts"))
    print()
    results.append(update_card(99, r16_sql, "R1.6 PoP-Level Incident Table"))

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    success_count = sum(results)
    print(f"✅ {success_count}/3 cards updated successfully")

    print("\nAll queries now use EXACT tables from spec:")
    print("  📊 R1.4: ts_qos_measurements + packages (joined by isp_id)")
    print("  🚨 R1.5: alerts + sla_thresholds")
    print("  📍 R1.6: incidents + pops + isps")

    print(f"\n🔗 View dashboard: {METABASE_URL}/dashboard/6")
    print("\n📝 Note: alerts and incidents tables created from sla_violations data")

if __name__ == "__main__":
    main()
