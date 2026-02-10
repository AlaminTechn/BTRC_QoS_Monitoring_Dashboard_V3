#!/usr/bin/env python3
"""
Update R1.1, R1.2, R1.3 cards to match demo UI design
- Add percentages
- Better formatting
- Color indicators
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

def update_card_with_percentage(card_id, card_name, sql_query, viz_settings):
    headers = login()

    update_data = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_query.strip(),
                "template-tags": {}
            },
            "database": 2
        },
        "display": "scalar",
        "visualization_settings": viz_settings
    }

    print(f"Updating {card_name}...")
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
    print("Update R1 Card Design to Match Demo UI")
    print("=" * 70)
    print()

    # Total ISPs query (for calculating percentages)
    total_isps_query = "(SELECT COUNT(*) FROM isps WHERE license_status = 'ACTIVE')"

    # R1.1: Compliant ISPs with percentage
    r11_sql = f"""
-- R1.1: Compliant ISPs Count with Percentage
WITH isp_stats AS (
    SELECT
        i.id as isp_id,
        i.name_en,
        AVG(m.download_speed_mbps) as avg_download,
        AVG(m.upload_speed_mbps) as avg_upload,
        AVG(CASE WHEN m.test_status = 'SUCCESS' THEN 100 ELSE 0 END) as availability_pct
    FROM isps i
    LEFT JOIN ts_qos_measurements m ON i.id = m.isp_id
    WHERE i.license_status = 'ACTIVE'
        AND m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '7 days'
    GROUP BY i.id, i.name_en
),
compliance_check AS (
    SELECT
        COUNT(*) as compliant_count,
        ROUND((COUNT(*) * 100.0 / {total_isps_query})::numeric, 0) as percentage
    FROM isp_stats
    WHERE avg_download >= 40  -- Minimum threshold
        AND availability_pct >= 95
)
SELECT
    compliant_count || E'\\n' || percentage || '% of total ISPs' as result
FROM compliance_check;
"""

    r11_viz = {
        "scalar.field": "result",
        "card.title": "COMPLIANT",
        "scalar.style": "decimal",
        "graph.colors": ["#10b981"],  # Green
        "card.description": "ISPs meeting all SLA requirements"
    }

    # R1.2: At Risk ISPs with percentage
    r12_sql = f"""
-- R1.2: At Risk ISPs Count with Percentage
WITH isp_stats AS (
    SELECT
        i.id as isp_id,
        i.name_en,
        AVG(m.download_speed_mbps) as avg_download,
        AVG(m.upload_speed_mbps) as avg_upload,
        AVG(CASE WHEN m.test_status = 'SUCCESS' THEN 100 ELSE 0 END) as availability_pct
    FROM isps i
    LEFT JOIN ts_qos_measurements m ON i.id = m.isp_id
    WHERE i.license_status = 'ACTIVE'
        AND m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '7 days'
    GROUP BY i.id, i.name_en
),
at_risk_check AS (
    SELECT
        COUNT(*) as at_risk_count,
        ROUND((COUNT(*) * 100.0 / {total_isps_query})::numeric, 0) as percentage
    FROM isp_stats
    WHERE (avg_download >= 35 AND avg_download < 40)  -- Within 5% of threshold
        OR (availability_pct >= 90 AND availability_pct < 95)
)
SELECT
    at_risk_count || E'\\n' || percentage || '% of total ISPs' as result
FROM at_risk_check;
"""

    r12_viz = {
        "scalar.field": "result",
        "card.title": "AT RISK",
        "scalar.style": "decimal",
        "graph.colors": ["#f59e0b"],  # Orange/Yellow
        "card.description": "ISPs approaching SLA thresholds"
    }

    # R1.3: Violation ISPs with percentage
    r13_sql = f"""
-- R1.3: Violation ISPs Count with Percentage
WITH isp_stats AS (
    SELECT
        i.id as isp_id,
        i.name_en,
        AVG(m.download_speed_mbps) as avg_download,
        AVG(m.upload_speed_mbps) as avg_upload,
        AVG(CASE WHEN m.test_status = 'SUCCESS' THEN 100 ELSE 0 END) as availability_pct
    FROM isps i
    LEFT JOIN ts_qos_measurements m ON i.id = m.isp_id
    WHERE i.license_status = 'ACTIVE'
        AND m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '7 days'
    GROUP BY i.id, i.name_en
),
violation_check AS (
    SELECT
        COUNT(*) as violation_count,
        ROUND((COUNT(*) * 100.0 / {total_isps_query})::numeric, 0) as percentage
    FROM isp_stats
    WHERE avg_download < 35  -- Below threshold
        OR availability_pct < 90
)
SELECT
    violation_count || E'\\n' || percentage || '% of total ISPs' as result
FROM violation_check;
"""

    r13_viz = {
        "scalar.field": "result",
        "card.title": "VIOLATION",
        "scalar.style": "decimal",
        "graph.colors": ["#ef4444"],  # Red
        "card.description": "ISPs currently in SLA violation"
    }

    # Update all three cards
    results = []
    results.append(update_card_with_percentage(76, "R1.1 Compliant ISPs", r11_sql, r11_viz))
    print()
    results.append(update_card_with_percentage(77, "R1.2 At Risk ISPs", r12_sql, r12_viz))
    print()
    results.append(update_card_with_percentage(78, "R1.3 Violation ISPs", r13_sql, r13_viz))

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    success_count = sum(results)
    print(f"✅ {success_count}/3 cards updated successfully")

    print("\nChanges Applied:")
    print("  📊 R1.1: Shows count + percentage (green)")
    print("  ⚠️  R1.2: Shows count + percentage (orange)")
    print("  ❌ R1.3: Shows count + percentage (red)")
    print("\nFormat: '847\\n87% of total ISPs'")

    print(f"\n🔗 View dashboard: {METABASE_URL}/dashboard/6")

if __name__ == "__main__":
    main()
