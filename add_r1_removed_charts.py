#!/usr/bin/env python3
"""
Add Removed Charts to Regulatory Dashboard Tab R1

This script creates 3 charts that were marked "(Remove)" in the spec:
- R1.4: Package Compliance Matrix
- R1.5: Real-Time Threshold Alerts
- R1.6: PoP-Level Incident Table
"""

import requests
import json
import sys

# Configuration
METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6
DATABASE_ID = 2  # TimescaleDB

def login():
    """Login to Metabase and get session token"""
    print("Logging in to Metabase...")
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

    token = response.json()["id"]
    print(f"✅ Login successful")
    return {"X-Metabase-Session": token}

def get_dashboard(headers):
    """Get current dashboard structure"""
    print(f"\nFetching Regulatory Dashboard (ID={REGULATORY_DASHBOARD_ID})...")
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers
    )
    if response.status_code != 200:
        print(f"❌ Failed to fetch dashboard: {response.text}")
        sys.exit(1)

    dashboard = response.json()
    print(f"✅ Dashboard fetched: {dashboard['name']}")
    print(f"   Current tabs: {len(dashboard.get('tabs', []))}")
    print(f"   Current cards: {len(dashboard.get('dashcards', []))}")

    # Find R1 tab
    r1_tab = None
    for tab in dashboard.get('tabs', []):
        if 'R1' in tab.get('name', '') or 'SLA Monitoring' in tab.get('name', ''):
            r1_tab = tab
            break

    if not r1_tab:
        print("❌ R1 (SLA Monitoring) tab not found!")
        sys.exit(1)

    print(f"   R1 Tab ID: {r1_tab['id']} - {r1_tab['name']}")
    return dashboard, r1_tab['id']

def create_question(headers, name, description, sql_query, viz_settings=None):
    """Create a Metabase question (card)"""
    print(f"\nCreating question: {name}...")

    question_data = {
        "name": name,
        "description": description,
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_query,
                "template-tags": {}
            },
            "database": DATABASE_ID
        },
        "display": "table",
        "visualization_settings": viz_settings or {}
    }

    response = requests.post(
        f"{METABASE_URL}/api/card",
        headers=headers,
        json=question_data
    )

    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create question: {response.text}")
        return None

    question = response.json()
    print(f"✅ Question created: ID={question['id']}")
    return question

def add_cards_to_dashboard(headers, dashboard_id, cards_to_add):
    """Add multiple cards to the dashboard using PUT endpoint"""
    print(f"\nAdding {len(cards_to_add)} cards to dashboard...")

    # Get current dashboard structure
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}",
        headers=headers
    )

    if response.status_code != 200:
        print(f"❌ Failed to fetch dashboard: {response.text}")
        return False

    dashboard = response.json()
    current_dashcards = dashboard.get('dashcards', [])

    # Find the highest ID to create negative IDs for new cards
    existing_ids = [dc.get('id', 0) for dc in current_dashcards]
    next_negative_id = min(existing_ids) - 1 if existing_ids else -1

    # Add new dashcards
    new_dashcards = []
    for card_info in cards_to_add:
        dashcard = {
            "id": next_negative_id,
            "card_id": card_info['card_id'],
            "dashboard_tab_id": card_info['tab_id'],
            "row": card_info['row'],
            "col": card_info['col'],
            "size_x": card_info['size_x'],
            "size_y": card_info['size_y'],
            "parameter_mappings": [],
            "visualization_settings": {}
        }
        new_dashcards.append(dashcard)
        next_negative_id -= 1

    # Combine existing and new dashcards
    all_dashcards = current_dashcards + new_dashcards

    # Update dashboard
    update_data = {
        "dashcards": all_dashcards
    }

    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}",
        headers=headers,
        json=update_data
    )

    if response.status_code not in [200, 202]:
        print(f"❌ Failed to update dashboard: {response.text}")
        return False

    print(f"✅ {len(cards_to_add)} cards added to dashboard")
    return True

def main():
    print("=" * 70)
    print("Add Removed Charts to Regulatory Dashboard Tab R1")
    print("=" * 70)

    # Login
    headers = login()

    # Get dashboard structure
    dashboard, r1_tab_id = get_dashboard(headers)

    # Chart 1: R1.4 - Package Compliance Matrix
    print("\n" + "=" * 70)
    print("Creating R1.4: Package Compliance Matrix")
    print("=" * 70)

    r14_sql = """
-- R1.4: Package Compliance Matrix
-- Compares target vs actual speed by package tier
WITH package_tiers AS (
    SELECT
        CASE
            WHEN declared_download_speed_mbps < 10 THEN '0-10 Mbps'
            WHEN declared_download_speed_mbps >= 10 AND declared_download_speed_mbps < 25 THEN '10-25 Mbps'
            WHEN declared_download_speed_mbps >= 25 AND declared_download_speed_mbps < 50 THEN '25-50 Mbps'
            WHEN declared_download_speed_mbps >= 50 AND declared_download_speed_mbps < 100 THEN '50-100 Mbps'
            WHEN declared_download_speed_mbps >= 100 AND declared_download_speed_mbps < 200 THEN '100-200 Mbps'
            ELSE '200+ Mbps'
        END as package_tier,
        declared_download_speed_mbps,
        declared_upload_speed_mbps
    FROM packages
    WHERE status = 'ACTIVE'
),
measured_performance AS (
    SELECT
        CASE
            WHEN p.declared_download_speed_mbps < 10 THEN '0-10 Mbps'
            WHEN p.declared_download_speed_mbps >= 10 AND p.declared_download_speed_mbps < 25 THEN '10-25 Mbps'
            WHEN p.declared_download_speed_mbps >= 25 AND p.declared_download_speed_mbps < 50 THEN '25-50 Mbps'
            WHEN p.declared_download_speed_mbps >= 50 AND p.declared_download_speed_mbps < 100 THEN '50-100 Mbps'
            WHEN p.declared_download_speed_mbps >= 100 AND p.declared_download_speed_mbps < 200 THEN '100-200 Mbps'
            ELSE '200+ Mbps'
        END as package_tier,
        AVG(m.download_speed_mbps) as avg_measured_download,
        AVG(m.upload_speed_mbps) as avg_measured_upload,
        COUNT(*) as measurement_count
    FROM ts_qos_measurements m
    JOIN packages p ON m.package_id = p.package_id
    WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
    GROUP BY 1
)
SELECT
    pt.package_tier as "Package Tier",
    ROUND(AVG(pt.declared_download_speed_mbps)::numeric, 2) as "Target Download (Mbps)",
    ROUND(COALESCE(mp.avg_measured_download, 0)::numeric, 2) as "Actual Download (Mbps)",
    ROUND((COALESCE(mp.avg_measured_download, 0) / NULLIF(AVG(pt.declared_download_speed_mbps), 0) * 100)::numeric, 2) as "Download Achievement %",
    ROUND(AVG(pt.declared_upload_speed_mbps)::numeric, 2) as "Target Upload (Mbps)",
    ROUND(COALESCE(mp.avg_measured_upload, 0)::numeric, 2) as "Actual Upload (Mbps)",
    ROUND((COALESCE(mp.avg_measured_upload, 0) / NULLIF(AVG(pt.declared_upload_speed_mbps), 0) * 100)::numeric, 2) as "Upload Achievement %",
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

    r14_question = create_question(
        headers,
        "R1.4 Package Compliance Matrix",
        "Compares target vs actual speed by package tier with achievement %",
        r14_sql,
        viz_settings={
            "table.pivot_column": "Package Tier",
            "table.cell_column": "Download Achievement %"
        }
    )

    cards_to_add = []
    if r14_question:
        cards_to_add.append({
            'card_id': r14_question['id'],
            'tab_id': r1_tab_id,
            'row': 4,
            'col': 0,
            'size_x': 8,
            'size_y': 4
        })

    # Chart 2: R1.5 - Real-Time Threshold Alerts
    print("\n" + "=" * 70)
    print("Creating R1.5: Real-Time Threshold Alerts")
    print("=" * 70)

    r15_sql = """
-- R1.5: Real-Time Threshold Alerts
-- Live scrolling alert list from SLA violations
WITH recent_violations AS (
    SELECT
        v.violation_id,
        i.isp_name as "ISP",
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
    JOIN isps i ON v.isp_id = i.isp_id
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

    r15_question = create_question(
        headers,
        "R1.5 Real-Time Threshold Alerts",
        "Live alert list showing active SLA violations with severity and duration",
        r15_sql,
        viz_settings={
            "table.columns": [
                {"name": "ISP", "enabled": True},
                {"name": "Metric", "enabled": True},
                {"name": "Threshold", "enabled": True},
                {"name": "Actual", "enabled": True},
                {"name": "Duration", "enabled": True},
                {"name": "Severity", "enabled": True},
                {"name": "Detected At", "enabled": True}
            ]
        }
    )

    if r15_question:
        cards_to_add.append({
            'card_id': r15_question['id'],
            'tab_id': r1_tab_id,
            'row': 4,
            'col': 8,
            'size_x': 8,
            'size_y': 4
        })

    # Chart 3: R1.6 - PoP-Level Incident Table
    print("\n" + "=" * 70)
    print("Creating R1.6: PoP-Level Incident Table")
    print("=" * 70)

    r16_sql = """
-- R1.6: PoP-Level Incident Table
-- Sortable table with incident details by PoP
WITH pop_incidents AS (
    SELECT
        i.incident_id as "Incident ID",
        isp.isp_name as "ISP",
        p.pop_name as "PoP Location",
        d.district_name as "District",
        dv.division_name as "Division",
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
    JOIN pops p ON i.pop_id = p.pop_id
    JOIN isps isp ON p.isp_id = isp.isp_id
    LEFT JOIN geo_districts d ON p.district_id = d.district_id
    LEFT JOIN geo_divisions dv ON d.division_id = dv.division_id
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

    r16_question = create_question(
        headers,
        "R1.6 PoP-Level Incident Table",
        "Sortable incident tracking table with status, severity, and resolution time",
        r16_sql,
        viz_settings={
            "table.columns": [
                {"name": "Incident ID", "enabled": True},
                {"name": "ISP", "enabled": True},
                {"name": "PoP Location", "enabled": True},
                {"name": "District", "enabled": True},
                {"name": "Division", "enabled": True},
                {"name": "Metric Type", "enabled": True},
                {"name": "Status", "enabled": True},
                {"name": "Severity", "enabled": True},
                {"name": "Created", "enabled": True},
                {"name": "Resolved", "enabled": True},
                {"name": "Duration", "enabled": True}
            ]
        }
    )

    if r16_question:
        cards_to_add.append({
            'card_id': r16_question['id'],
            'tab_id': r1_tab_id,
            'row': 8,
            'col': 0,
            'size_x': 16,
            'size_y': 4
        })

    # Add all cards to dashboard in one batch
    if cards_to_add:
        add_cards_to_dashboard(headers, REGULATORY_DASHBOARD_ID, cards_to_add)

    # Final status
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ R1.4: Package Compliance Matrix - {'Created' if r14_question else 'Failed'}")
    print(f"✅ R1.5: Real-Time Threshold Alerts - {'Created' if r15_question else 'Failed'}")
    print(f"✅ R1.6: PoP-Level Incident Table - {'Created' if r16_question else 'Failed'}")
    print("\n🎉 All removed charts added to Regulatory Dashboard Tab R1!")
    print(f"\nView dashboard at: {METABASE_URL}/dashboard/{REGULATORY_DASHBOARD_ID}")

if __name__ == "__main__":
    main()
