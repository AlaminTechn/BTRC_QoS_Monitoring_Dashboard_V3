#!/usr/bin/env python3
"""
Fix all R1 cards SQL queries to use correct column names from schema
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
    print("Fix All R1 Cards SQL Queries")
    print("=" * 70)
    print()

    # R1.5: Real-Time Threshold Alerts
    r15_sql = """
-- R1.5: Real-Time Threshold Alerts
-- Live alert list from SLA violations
WITH recent_violations AS (
    SELECT
        v.violation_id,
        i.name_en as "ISP",
        v.metric_type as "Metric",
        ROUND(v.threshold_value::numeric, 2) as "Threshold",
        ROUND(v.measured_value::numeric, 2) as "Actual",
        EXTRACT(EPOCH FROM (NOW() - v.detection_time)) / 60 as duration_minutes,
        CASE
            WHEN v.severity = 'CRITICAL' THEN '🔴 Critical'
            WHEN v.severity = 'HIGH' THEN '🟠 High'
            WHEN v.severity = 'MEDIUM' THEN '🟡 Medium'
            ELSE '🟢 Low'
        END as "Severity",
        v.detection_time as "Detected At"
    FROM sla_violations v
    JOIN isps i ON v.isp_id = i.id
    WHERE v.status IN ('OPEN', 'ACKNOWLEDGED')
        AND v.detection_time >= NOW() - INTERVAL '24 hours'
)
SELECT
    "ISP",
    "Metric",
    "Threshold",
    "Actual",
    CASE
        WHEN duration_minutes < 60 THEN ROUND(duration_minutes::numeric, 0) || ' min'
        WHEN duration_minutes < 1440 THEN ROUND((duration_minutes / 60)::numeric, 1) || ' hrs'
        ELSE ROUND((duration_minutes / 1440)::numeric, 1) || ' days'
    END as "Duration",
    "Severity",
    TO_CHAR("Detected At", 'YYYY-MM-DD HH24:MI') as "Detected At"
FROM recent_violations
ORDER BY
    CASE
        WHEN "Severity" LIKE '%Critical%' THEN 1
        WHEN "Severity" LIKE '%High%' THEN 2
        WHEN "Severity" LIKE '%Medium%' THEN 3
        ELSE 4
    END,
    "Detected At" DESC
LIMIT 50;
"""

    # R1.6: PoP-Level Incident Table
    r16_sql = """
-- R1.6: PoP-Level Incident Table
-- Sortable incident tracking table
WITH pop_incidents AS (
    SELECT
        i.incident_id as "Incident ID",
        isp.name_en as "ISP",
        p.name_en as "PoP Location",
        d.name_en as "District",
        dv.name_en as "Division",
        i.metric_type as "Metric Type",
        CASE
            WHEN i.status = 'OPEN' THEN '🔴 Open'
            WHEN i.status = 'ACKNOWLEDGED' THEN '🟡 Acknowledged'
            WHEN i.status = 'RESOLVED' THEN '🟢 Resolved'
            ELSE i.status
        END as "Status",
        i.severity as "Severity",
        TO_CHAR(i.created_at, 'YYYY-MM-DD HH24:MI') as "Created",
        CASE
            WHEN i.resolved_at IS NOT NULL THEN TO_CHAR(i.resolved_at, 'YYYY-MM-DD HH24:MI')
            ELSE '-'
        END as "Resolved",
        CASE
            WHEN i.resolved_at IS NOT NULL THEN
                ROUND(EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)) / 3600::numeric, 2) || ' hrs'
            ELSE
                ROUND(EXTRACT(EPOCH FROM (NOW() - i.created_at)) / 3600::numeric, 2) || ' hrs'
        END as "Duration"
    FROM incidents i
    JOIN pops p ON i.pop_id = p.id
    JOIN isps isp ON p.isp_id = isp.id
    LEFT JOIN geo_districts d ON p.district_id = d.id
    LEFT JOIN geo_divisions dv ON d.division_id = dv.id
    WHERE i.status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED')
        AND i.created_at >= NOW() - INTERVAL '7 days'
)
SELECT
    "Incident ID",
    "ISP",
    "PoP Location",
    "District",
    "Division",
    "Metric Type",
    "Status",
    "Severity",
    "Created",
    "Resolved",
    "Duration"
FROM pop_incidents
ORDER BY
    CASE
        WHEN "Status" LIKE '%Open%' THEN 1
        WHEN "Status" LIKE '%Acknowledged%' THEN 2
        ELSE 3
    END,
    "Created" DESC
LIMIT 100;
"""

    # Update all cards
    results = []
    results.append(update_card(98, r15_sql, "R1.5 Real-Time Threshold Alerts"))
    print()
    results.append(update_card(99, r16_sql, "R1.6 PoP-Level Incident Table"))

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    success_count = sum(results)
    print(f"✅ {success_count}/2 cards updated successfully")

    print("\nColumn name fixes:")
    print("  - isp_name → name_en (isps table)")
    print("  - pop_name → name_en (pops table)")
    print("  - district_name → name_en (geo_districts table)")
    print("  - division_name → name_en (geo_divisions table)")

    print(f"\n🔗 View dashboard: {METABASE_URL}/dashboard/6")

if __name__ == "__main__":
    main()
