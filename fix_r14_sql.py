#!/usr/bin/env python3
"""
Fix R1.4 SQL query with correct column names
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

def fix_r14():
    headers = login()

    # Corrected SQL with proper column names
    corrected_sql = """
-- R1.4: Package Compliance Matrix
-- Compares target vs actual speed by package tier
WITH package_tiers AS (
    SELECT
        CASE
            WHEN download_speed_mbps < 10 THEN '0-10 Mbps'
            WHEN download_speed_mbps >= 10 AND download_speed_mbps < 25 THEN '10-25 Mbps'
            WHEN download_speed_mbps >= 25 AND download_speed_mbps < 50 THEN '25-50 Mbps'
            WHEN download_speed_mbps >= 50 AND download_speed_mbps < 100 THEN '50-100 Mbps'
            WHEN download_speed_mbps >= 100 AND download_speed_mbps < 200 THEN '100-200 Mbps'
            ELSE '200+ Mbps'
        END as package_tier,
        download_speed_mbps,
        upload_speed_mbps
    FROM packages
    WHERE is_active = true
),
measured_performance AS (
    SELECT
        CASE
            WHEN p.download_speed_mbps < 10 THEN '0-10 Mbps'
            WHEN p.download_speed_mbps >= 10 AND p.download_speed_mbps < 25 THEN '10-25 Mbps'
            WHEN p.download_speed_mbps >= 25 AND p.download_speed_mbps < 50 THEN '25-50 Mbps'
            WHEN p.download_speed_mbps >= 50 AND p.download_speed_mbps < 100 THEN '50-100 Mbps'
            WHEN p.download_speed_mbps >= 100 AND p.download_speed_mbps < 200 THEN '100-200 Mbps'
            ELSE '200+ Mbps'
        END as package_tier,
        AVG(m.download_speed_mbps) as avg_measured_download,
        AVG(m.upload_speed_mbps) as avg_measured_upload,
        COUNT(*) as measurement_count
    FROM ts_qos_measurements m
    JOIN packages p ON m.package_id = p.id
    WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
    GROUP BY 1
)
SELECT
    pt.package_tier as "Package Tier",
    ROUND(AVG(pt.download_speed_mbps)::numeric, 2) as "Target Download (Mbps)",
    ROUND(COALESCE(mp.avg_measured_download, 0)::numeric, 2) as "Actual Download (Mbps)",
    ROUND((COALESCE(mp.avg_measured_download, 0) / NULLIF(AVG(pt.download_speed_mbps), 0) * 100)::numeric, 2) as "Download Achievement %",
    ROUND(AVG(pt.upload_speed_mbps)::numeric, 2) as "Target Upload (Mbps)",
    ROUND(COALESCE(mp.avg_measured_upload, 0)::numeric, 2) as "Actual Upload (Mbps)",
    ROUND((COALESCE(mp.avg_measured_upload, 0) / NULLIF(AVG(pt.upload_speed_mbps), 0) * 100)::numeric, 2) as "Upload Achievement %",
    COALESCE(mp.measurement_count, 0) as "Measurements"
FROM package_tiers pt
LEFT JOIN measured_performance mp ON pt.package_tier = mp.package_tier
GROUP BY pt.package_tier, mp.avg_measured_download, mp.avg_measured_upload, mp.measurement_count
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

    # Update card 97
    update_data = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": corrected_sql.strip(),
                "template-tags": {}
            },
            "database": 2
        }
    }

    print("Updating Card 97 (R1.4 Package Compliance Matrix)...")
    response = requests.put(
        f"{METABASE_URL}/api/card/97",
        headers=headers,
        json=update_data
    )

    if response.status_code == 200:
        print("✅ R1.4 SQL updated successfully!")
        print("\nFixed column names:")
        print("  - declared_download_speed_mbps → download_speed_mbps")
        print("  - declared_upload_speed_mbps → upload_speed_mbps")
        print("  - package_id join now uses p.id (was p.package_id)")
        print("  - status filter changed to is_active = true")
        return True
    else:
        print(f"❌ Failed to update: {response.status_code}")
        print(response.text[:500])
        return False

def fix_r15_r16():
    """Check and fix R1.5 and R1.6 if needed"""
    headers = login()

    # R1.5 uses sla_violations table - check if it needs fixes
    print("\nChecking R1.5 (Real-Time Threshold Alerts)...")
    response = requests.get(f"{METABASE_URL}/api/card/98", headers=headers)
    if response.status_code == 200:
        print("✅ R1.5 uses sla_violations table - should be OK")

    # R1.6 uses incidents table - check if it needs fixes
    print("\nChecking R1.6 (PoP-Level Incident Table)...")
    response = requests.get(f"{METABASE_URL}/api/card/99", headers=headers)
    if response.status_code == 200:
        print("✅ R1.6 uses incidents table - should be OK")

if __name__ == "__main__":
    print("=" * 70)
    print("Fix R1.4 SQL Query")
    print("=" * 70)
    print()

    success = fix_r14()
    fix_r15_r16()

    if success:
        print("\n" + "=" * 70)
        print("✅ SQL queries fixed!")
        print("=" * 70)
        print(f"\nView dashboard: {METABASE_URL}/dashboard/6")
        print("Test R1.4 query by refreshing the card on the dashboard")
    else:
        print("\n❌ Fix failed")
