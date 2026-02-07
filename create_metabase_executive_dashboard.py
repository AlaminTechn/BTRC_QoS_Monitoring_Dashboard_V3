#!/usr/bin/env python3
"""
BTRC QoS Monitoring Dashboard — Executive Dashboard (Metabase)

Creates the Executive Dashboard in Metabase via REST API.
Replicates the V2 Superset Executive Dashboard with 3 tabs, 12 charts.

Dashboard URL: http://localhost:3000/dashboard/<id>

Tabs:
  E1: Performance Scorecard  (3 KPI cards + line chart + bar chart)
  E2: Geographic Intelligence (map/table + comparison table)
  E3: Compliance Overview    (compliance table + violations charts)

Usage:
    1. Set credentials in .env file (METABASE_EMAIL, METABASE_PASSWORD)
    2. python3 create_metabase_executive_dashboard.py
"""

import json
import os
import sys
import time
import uuid

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
#  Configuration
# =============================================================================
METABASE_URL = os.environ.get("METABASE_URL", "http://localhost:3000")
EMAIL = os.environ.get("METABASE_EMAIL", "")
PASSWORD = os.environ.get("METABASE_PASSWORD", "")

DASHBOARD_NAME = "Executive Dashboard - National Summary"
DASHBOARD_DESC = (
    "National-level summary dashboard for BTRC leadership. "
    "Shows broadband performance, geographic distribution, and compliance status."
)

# Metabase grid: 18 columns wide
GRID_WIDTH = 18

# =============================================================================
#  SQL Queries (same as V2 Executive Dashboard)
# =============================================================================

# ─── Tab E1: Performance Scorecard ───────────────────────────────────────────

E1_1_SQL = """
SELECT
    ROUND(AVG(download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)"
FROM ts_qos_measurements
WHERE timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
"""

E1_2_SQL = """
SELECT
    ROUND(AVG(upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)"
FROM ts_qos_measurements
WHERE timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
"""

E1_3_SQL = """
SELECT
    ROUND(
        (COUNT(*) FILTER (WHERE test_status = 'SUCCESS')::numeric /
         NULLIF(COUNT(*)::numeric, 0)) * 100,
        2
    ) as "Service Availability (%)"
FROM ts_qos_measurements
WHERE timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
"""

E1_5_SQL = """
SELECT
    DATE_TRUNC('month', timestamp) as "Month",
    ROUND(AVG(download_speed_mbps)::numeric, 2) as "Download Speed",
    ROUND(AVG(upload_speed_mbps)::numeric, 2) as "Upload Speed"
FROM ts_qos_measurements
WHERE timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', timestamp)
ORDER BY "Month"
"""

E1_6_SQL = """
SELECT
    d.name_en as "Division",
    ROUND(AVG(m.download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)",
    ROUND(AVG(m.upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)",
    COUNT(DISTINCT p.id) as "PoP Count"
FROM ts_qos_measurements m
JOIN software_agents sa ON sa.id = m.agent_id
JOIN agent_pop_assignments apa ON apa.agent_id = sa.id
JOIN pops p ON p.id = apa.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
GROUP BY d.id, d.name_en
ORDER BY "Avg Download (Mbps)" DESC
"""

# ─── Tab E2: Geographic Intelligence ─────────────────────────────────────────

E2_1_SQL = """
SELECT
    d.name_en as "Division",
    ROUND(AVG(m.download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)",
    ROUND(AVG(m.upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)",
    CASE
        WHEN AVG(m.download_speed_mbps) >= 50 THEN 'High'
        WHEN AVG(m.download_speed_mbps) >= 25 THEN 'Medium'
        ELSE 'Low'
    END as "Performance Tier"
FROM ts_qos_measurements m
JOIN software_agents sa ON sa.id = m.agent_id
JOIN agent_pop_assignments apa ON apa.agent_id = sa.id
JOIN pops p ON p.id = apa.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
GROUP BY d.id, d.name_en
ORDER BY "Avg Download (Mbps)" DESC
"""

E2_2_SQL = """
SELECT
    d.name_en as "Division",
    ROUND(AVG(m.download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)",
    ROUND(AVG(m.upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)",
    ROUND(
        (COUNT(*) FILTER (WHERE m.test_status = 'SUCCESS')::numeric /
         NULLIF(COUNT(*)::numeric, 0)) * 100,
        2
    ) as "Availability (%)",
    COUNT(DISTINCT i.id) as "ISP Count",
    COUNT(DISTINCT p.id) as "PoP Count"
FROM ts_qos_measurements m
JOIN software_agents sa ON sa.id = m.agent_id
JOIN agent_pop_assignments apa ON apa.agent_id = sa.id
JOIN pops p ON p.id = apa.pop_id
JOIN isps i ON i.id = p.isp_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
GROUP BY d.id, d.name_en
ORDER BY "Avg Download (Mbps)" DESC
"""

# ─── Tab E3: Compliance Overview ─────────────────────────────────────────────

E3_1_SQL = """
WITH isp_violations AS (
    SELECT
        i.id as isp_id,
        i.name_en as "ISP Name",
        lc.name_en as "License Category",
        COUNT(v.id) as violation_count
    FROM isps i
    LEFT JOIN isp_license_categories lc ON lc.id = i.license_category_id
    LEFT JOIN sla_violations v ON v.isp_id = i.id
        AND v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
    WHERE i.license_status = 'ACTIVE'
    GROUP BY i.id, i.name_en, lc.name_en
)
SELECT
    "ISP Name",
    "License Category",
    CASE
        WHEN violation_count = 0 THEN 100
        WHEN violation_count <= 2 THEN 80
        WHEN violation_count <= 5 THEN 60
        ELSE 40
    END as "Compliance Score",
    CASE
        WHEN violation_count = 0 THEN 'Compliant'
        WHEN violation_count <= 2 THEN 'At Risk'
        ELSE 'Violation'
    END as "Status"
FROM isp_violations
ORDER BY "License Category", "Compliance Score" DESC
"""

E3_2_SQL = """
SELECT
    COALESCE(violation_type, 'Speed') as "Violation Type",
    COUNT(*) as "Count"
FROM sla_violations
WHERE detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
GROUP BY violation_type
ORDER BY "Count" DESC
"""

E3_3_SQL = """
SELECT
    i.name_en as "ISP Name",
    COUNT(*) as "Violations",
    MAX(v.severity) as "Max Severity",
    STRING_AGG(DISTINCT v.violation_type, ', ') as "Violation Types"
FROM sla_violations v
JOIN isps i ON i.id = v.isp_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
GROUP BY i.id, i.name_en
ORDER BY "Violations" DESC
LIMIT 10
"""

E3_4_SQL = """
SELECT
    DATE_TRUNC('month', detection_time) as "Month",
    COALESCE(violation_type, 'Speed') as "Violation Type",
    COUNT(*) as "Count"
FROM sla_violations
WHERE detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '6 months'
GROUP BY DATE_TRUNC('month', detection_time), violation_type
ORDER BY "Month", "Violation Type"
"""

E3_5_SQL = """
SELECT
    d.name_en as "Division",
    COUNT(*) as "Total",
    COUNT(*) FILTER (WHERE v.violation_type = 'Speed' OR v.violation_type IS NULL)
        as "Speed",
    COUNT(*) FILTER (WHERE v.violation_type = 'Availability')
        as "Availability",
    COUNT(*) FILTER (WHERE v.violation_type = 'Latency')
        as "Latency",
    COUNT(*) FILTER (WHERE v.violation_type = 'Packet Loss')
        as "Packet Loss"
FROM sla_violations v
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
GROUP BY d.id, d.name_en
ORDER BY "Total" DESC
"""


# =============================================================================
#  Metabase API Client
# =============================================================================
class MetabaseClient:
    """Simple Metabase REST API client."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session_token = None
        self.database_id = None

    def login(self, email, password):
        """Authenticate and store session token."""
        resp = self.session.post(
            f"{self.base_url}/api/session",
            json={"username": email, "password": password}
        )
        if resp.status_code != 200:
            print(f"  Login failed ({resp.status_code}): {resp.text[:300]}")
            return False
        self.session_token = resp.json()["id"]
        self.session.headers["X-Metabase-Session"] = self.session_token
        return True

    def get(self, path, **kwargs):
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

    def find_database(self, db_name="btrc_qos_poc"):
        """Find database ID by name."""
        resp = self.get("/api/database")
        if resp.status_code != 200:
            print(f"  Failed to list databases: {resp.text[:200]}")
            return None
        databases = resp.json().get("data", resp.json() if isinstance(resp.json(), list) else [])
        for db in databases:
            if db.get("name", "").lower() == db_name.lower() or \
               db.get("details", {}).get("db", "") == db_name:
                self.database_id = db["id"]
                return db["id"]
        # Try by details.dbname
        for db in databases:
            details = db.get("details", {})
            if details.get("dbname") == db_name or details.get("db") == db_name:
                self.database_id = db["id"]
                return db["id"]
        return None

    def create_card(self, name, sql, display="table", description="",
                    visualization_settings=None, collection_id=None):
        """Create a native SQL question (card). Returns card dict or None."""
        payload = {
            "name": name,
            "description": description,
            "dataset_query": {
                "database": self.database_id,
                "native": {"query": sql},
                "type": "native"
            },
            "display": display,
            "visualization_settings": visualization_settings or {},
        }
        if collection_id:
            payload["collection_id"] = collection_id

        resp = self.post("/api/card", json=payload)
        if resp.status_code in (200, 201, 202):
            card = resp.json()
            print(f"  Card '{name}' created (id={card['id']}, display={display})")
            return card
        else:
            print(f"  Card '{name}' FAILED ({resp.status_code}): {resp.text[:300]}")
            return None

    def create_collection(self, name, description=""):
        """Create a collection (folder) for organizing cards."""
        resp = self.post("/api/collection", json={
            "name": name,
            "description": description
        })
        if resp.status_code in (200, 201):
            coll = resp.json()
            print(f"  Collection '{name}' created (id={coll['id']})")
            return coll
        else:
            print(f"  Collection '{name}' error ({resp.status_code}): {resp.text[:200]}")
            return None

    def create_dashboard(self, name, description="", collection_id=None):
        """Create a new dashboard. Returns dashboard dict."""
        payload = {"name": name, "description": description}
        if collection_id:
            payload["collection_id"] = collection_id
        resp = self.post("/api/dashboard", json=payload)
        if resp.status_code in (200, 201):
            dash = resp.json()
            print(f"  Dashboard '{name}' created (id={dash['id']})")
            return dash
        else:
            print(f"  Dashboard '{name}' FAILED ({resp.status_code}): {resp.text[:300]}")
            return None

    def setup_dashboard_tabs_and_cards(self, dashboard_id, ordered_tabs, cards):
        """Atomically create tabs and place cards on a dashboard.

        Uses PUT /api/dashboard/{id} which accepts both 'tabs' and 'dashcards'
        in a single request. Metabase v0.50+ requires this approach.

        Steps:
          1. First PUT with tabs only to create tabs and get real IDs
          2. Map negative temp tab IDs to real IDs
          3. Second PUT with real tab IDs in dashcards
        """
        # Step 1: Create tabs first (send with empty dashcards)
        tab_payload = {
            "tabs": ordered_tabs,
            "dashcards": [],
        }
        resp = self.put(f"/api/dashboard/{dashboard_id}", json=tab_payload)
        if resp.status_code != 200:
            print(f"  Tab creation FAILED ({resp.status_code}): {resp.text[:300]}")
            return None

        # Step 2: Map negative temp IDs to real IDs
        result = resp.json()
        created_tabs = result.get("tabs", [])
        if not created_tabs:
            print("  WARNING: No tabs returned. Placing cards without tabs.")
            # Place cards without tab assignment
            for card in cards:
                card.pop("dashboard_tab_id", None)
        else:
            # Build mapping: negative temp ID -> real positive ID
            temp_to_real = {}
            for orig_tab, created_tab in zip(ordered_tabs, created_tabs):
                temp_to_real[orig_tab["id"]] = created_tab["id"]
            print(f"  Tabs created: {len(created_tabs)} "
                  f"(IDs: {[t['id'] for t in created_tabs]})")

            # Update cards with real tab IDs
            for card in cards:
                old_tab_id = card.get("dashboard_tab_id")
                if old_tab_id in temp_to_real:
                    card["dashboard_tab_id"] = temp_to_real[old_tab_id]

            # Preserve created tab objects for final PUT
            ordered_tabs = [{"id": t["id"], "name": t["name"]}
                            for t in created_tabs]

        # Step 3: Place cards on dashboard with real tab IDs
        card_payload = {
            "tabs": ordered_tabs if created_tabs else [],
            "dashcards": cards,
        }
        resp = self.put(f"/api/dashboard/{dashboard_id}", json=card_payload)
        if resp.status_code == 200:
            result = resp.json()
            placed = len(result.get("dashcards", []))
            print(f"  Dashboard layout set: {len(ordered_tabs)} tabs, {placed} cards")
            return result
        else:
            print(f"  Layout FAILED ({resp.status_code}): {resp.text[:300]}")
            return None

    def find_existing_dashboard(self, name):
        """Find dashboard by name. Returns dashboard dict or None."""
        resp = self.get("/api/dashboard")
        if resp.status_code != 200:
            return None
        dashboards = resp.json()
        if isinstance(dashboards, list):
            for d in dashboards:
                if d.get("name") == name:
                    return d
        return None

    def delete_dashboard(self, dashboard_id):
        """Delete a dashboard by ID."""
        resp = self.delete(f"/api/dashboard/{dashboard_id}")
        return resp.status_code == 204


# =============================================================================
#  Chart Definitions
# =============================================================================
CHARTS = {
    # ─── Tab E1: Performance Scorecard ───────────────────────────────────────
    "e1_1": {
        "name": "E1.1 National Avg Download Speed",
        "sql": E1_1_SQL,
        "display": "scalar",
        "description": "30-day average download speed across all ISPs nationally",
        "viz_settings": {
            "scalar.field": "Avg Download (Mbps)",
            "scalar.suffix": " Mbps",
            "column_settings": {
                '["name","Avg Download (Mbps)"]': {"suffix": " Mbps"}
            }
        },
        "tab": "e1",
        "col": 0, "row": 0, "size_x": 6, "size_y": 4
    },
    "e1_2": {
        "name": "E1.2 National Avg Upload Speed",
        "sql": E1_2_SQL,
        "display": "scalar",
        "description": "30-day average upload speed across all ISPs nationally",
        "viz_settings": {
            "scalar.field": "Avg Upload (Mbps)",
            "scalar.suffix": " Mbps",
            "column_settings": {
                '["name","Avg Upload (Mbps)"]': {"suffix": " Mbps"}
            }
        },
        "tab": "e1",
        "col": 6, "row": 0, "size_x": 6, "size_y": 4
    },
    "e1_3": {
        "name": "E1.3 National Service Availability",
        "sql": E1_3_SQL,
        "display": "scalar",
        "description": "30-day service availability percentage (SUCCESS test ratio)",
        "viz_settings": {
            "scalar.field": "Service Availability (%)",
            "scalar.suffix": "%",
            "column_settings": {
                '["name","Service Availability (%)"]': {"suffix": "%"}
            }
        },
        "tab": "e1",
        "col": 12, "row": 0, "size_x": 6, "size_y": 4
    },
    "e1_5": {
        "name": "E1.5 Speed Trend (12 Months)",
        "sql": E1_5_SQL,
        "display": "line",
        "description": "Monthly average download and upload speed over 12 months",
        "viz_settings": {
            "graph.dimensions": ["Month"],
            "graph.metrics": ["Download Speed", "Upload Speed"],
            "graph.x_axis.title_text": "Month",
            "graph.y_axis.title_text": "Speed (Mbps)",
            "graph.show_values": True,
            "graph.label_value_formatting": "auto",
        },
        "tab": "e1",
        "col": 0, "row": 4, "size_x": 9, "size_y": 8
    },
    "e1_6": {
        "name": "E1.6 Division Performance Ranking",
        "sql": E1_6_SQL,
        "display": "row",
        "description": "8 divisions ranked by avg download speed (horizontal bar)",
        "viz_settings": {
            "graph.dimensions": ["Division"],
            "graph.metrics": ["Avg Download (Mbps)"],
            "graph.x_axis.title_text": "Avg Download Speed (Mbps)",
            "graph.y_axis.title_text": "Division",
            "graph.show_values": True,
        },
        "tab": "e1",
        "col": 9, "row": 4, "size_x": 9, "size_y": 8
    },

    # ─── Tab E2: Geographic Intelligence ─────────────────────────────────────
    "e2_1": {
        "name": "E2.1 Division Performance Overview",
        "sql": E2_1_SQL,
        "display": "table",
        "description": "Division performance with speed tiers (High/Medium/Low). "
                        "Can be converted to map after GeoJSON setup.",
        "viz_settings": {
            "table.pivot": False,
            "table.cell_column": "Performance Tier",
            "column_settings": {
                '["name","Avg Download (Mbps)"]': {
                    "show_mini_bar": True,
                    "number_style": "decimal",
                    "decimals": 2
                },
                '["name","Avg Upload (Mbps)"]': {
                    "show_mini_bar": True,
                    "number_style": "decimal",
                    "decimals": 2
                },
                '["name","Performance Tier"]': {
                    "column_title": "Tier"
                }
            }
        },
        "tab": "e2",
        "col": 0, "row": 0, "size_x": 9, "size_y": 10
    },
    "e2_2": {
        "name": "E2.2 Division Comparison Table",
        "sql": E2_2_SQL,
        "display": "table",
        "description": "Sortable comparison of all 8 divisions with ISP/PoP counts",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Avg Download (Mbps)"]': {
                    "show_mini_bar": True,
                    "decimals": 2
                },
                '["name","Avg Upload (Mbps)"]': {
                    "show_mini_bar": True,
                    "decimals": 2
                },
                '["name","Availability (%)"]': {
                    "show_mini_bar": True,
                    "decimals": 2,
                    "suffix": "%"
                }
            }
        },
        "tab": "e2",
        "col": 9, "row": 0, "size_x": 9, "size_y": 10
    },

    # ─── Tab E3: Compliance Overview ─────────────────────────────────────────
    "e3_1": {
        "name": "E3.1 ISP Compliance Status",
        "sql": E3_1_SQL,
        "display": "table",
        "description": "All active ISPs with compliance score and status (Compliant/At Risk/Violation)",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Compliance Score"]': {
                    "show_mini_bar": True,
                    "number_style": "decimal",
                    "decimals": 0
                },
                '["name","Status"]': {
                    "column_title": "Compliance Status"
                }
            }
        },
        "tab": "e3",
        "col": 0, "row": 0, "size_x": 18, "size_y": 8
    },
    "e3_2": {
        "name": "E3.2 Violations by Type",
        "sql": E3_2_SQL,
        "display": "row",
        "description": "Violation count by type (Speed, Availability, Latency, Packet Loss)",
        "viz_settings": {
            "graph.dimensions": ["Violation Type"],
            "graph.metrics": ["Count"],
            "graph.x_axis.title_text": "Count",
            "graph.y_axis.title_text": "Violation Type",
            "graph.show_values": True,
        },
        "tab": "e3",
        "col": 0, "row": 8, "size_x": 9, "size_y": 7
    },
    "e3_3": {
        "name": "E3.3 Top 10 Violators",
        "sql": E3_3_SQL,
        "display": "table",
        "description": "Top 10 ISPs by violation count with severity and violation types",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Violations"]': {
                    "show_mini_bar": True
                }
            }
        },
        "tab": "e3",
        "col": 9, "row": 8, "size_x": 9, "size_y": 7
    },
    "e3_4": {
        "name": "E3.4 Violation Trend (6 Months)",
        "sql": E3_4_SQL,
        "display": "bar",
        "description": "Monthly violation counts by type over 6 months (stacked bar)",
        "viz_settings": {
            "graph.dimensions": ["Month"],
            "graph.metrics": ["Count"],
            "graph.series_order_dimension": "Violation Type",
            "stackable.stack_type": "stacked",
            "graph.x_axis.title_text": "Month",
            "graph.y_axis.title_text": "Violations",
            "graph.show_values": False,
        },
        "tab": "e3",
        "col": 0, "row": 15, "size_x": 9, "size_y": 8
    },
    "e3_5": {
        "name": "E3.5 Violations by Division",
        "sql": E3_5_SQL,
        "display": "table",
        "description": "Violation breakdown by division and type",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Total"]': {"show_mini_bar": True},
                '["name","Speed"]': {"show_mini_bar": True},
                '["name","Availability"]': {"show_mini_bar": True},
                '["name","Latency"]': {"show_mini_bar": True},
                '["name","Packet Loss"]': {"show_mini_bar": True},
            }
        },
        "tab": "e3",
        "col": 9, "row": 15, "size_x": 9, "size_y": 8
    },
}


# =============================================================================
#  Main Script
# =============================================================================
def main():
    print("=" * 65)
    print("  BTRC Executive Dashboard Creator (Metabase)")
    print("=" * 65)

    # ── Credentials ──────────────────────────────────────────────────────
    email = EMAIL
    password = PASSWORD

    if not email:
        email = input("  Metabase email: ").strip()
    if not password:
        import getpass
        password = getpass.getpass("  Metabase password: ").strip()

    if not email or not password:
        print("  ERROR: Email and password are required.")
        print("  Set METABASE_EMAIL and METABASE_PASSWORD env vars, or enter them above.")
        sys.exit(1)

    # ── Initialize client ────────────────────────────────────────────────
    mb = MetabaseClient(METABASE_URL)

    # Step 1: Login
    print(f"\n[1/6] Authenticating as {email}...")
    if not mb.login(email, password):
        print("  FATAL: Authentication failed. Check credentials.")
        sys.exit(1)
    print("  Logged in successfully.")

    # Step 2: Find database
    print("\n[2/6] Finding database...")
    db_id = mb.find_database("btrc_qos_poc")
    if not db_id:
        # Try finding by display name
        db_id = mb.find_database("BTRC QoS")
    if not db_id:
        print("  ERROR: Could not find btrc_qos_poc database in Metabase.")
        print("  Make sure the database is connected in Metabase admin.")
        sys.exit(1)
    print(f"  Database found (id={db_id})")

    # Step 3: Create collection for organization
    print("\n[3/6] Creating collection...")
    collection = mb.create_collection(
        "Executive Dashboard",
        "Charts for the Executive Dashboard - National Summary"
    )
    collection_id = collection["id"] if collection else None

    # Step 4: Create all cards (questions)
    print("\n[4/6] Creating cards (questions)...")
    card_ids = {}
    for key, chart_def in CHARTS.items():
        card = mb.create_card(
            name=chart_def["name"],
            sql=chart_def["sql"],
            display=chart_def["display"],
            description=chart_def["description"],
            visualization_settings=chart_def["viz_settings"],
            collection_id=collection_id,
        )
        if card:
            card_ids[key] = card["id"]
        else:
            print(f"  WARNING: Card '{chart_def['name']}' creation failed, skipping.")
        time.sleep(0.3)  # Rate limiting

    if not card_ids:
        print("  FATAL: No cards created. Check database connection and SQL queries.")
        sys.exit(1)
    print(f"  Created {len(card_ids)}/{len(CHARTS)} cards.")

    # Step 5: Create dashboard
    print("\n[5/6] Creating dashboard...")

    # Check for existing dashboard
    existing = mb.find_existing_dashboard(DASHBOARD_NAME)
    if existing:
        print(f"  Found existing dashboard (id={existing['id']}). Deleting...")
        mb.delete_dashboard(existing["id"])
        time.sleep(0.5)

    dashboard = mb.create_dashboard(
        DASHBOARD_NAME,
        DASHBOARD_DESC,
        collection_id=collection_id
    )
    if not dashboard:
        print("  FATAL: Dashboard creation failed.")
        sys.exit(1)
    dashboard_id = dashboard["id"]

    # Step 6: Set up tabs and cards atomically
    print("\n[6/6] Setting up tabs and cards with layout...")

    # Define tabs with negative temporary IDs
    tab_defs = [
        {"id": -1, "name": "E1: Performance Scorecard"},
        {"id": -2, "name": "E2: Geographic Intelligence"},
        {"id": -3, "name": "E3: Compliance Overview"},
    ]
    tab_key_to_temp_id = {"e1": -1, "e2": -2, "e3": -3}

    # Build cards array with negative temporary IDs
    cards = []
    card_temp_id = -1
    for key, chart_def in CHARTS.items():
        if key not in card_ids:
            continue
        tab_key = chart_def["tab"]
        cards.append({
            "id": card_temp_id,
            "card_id": card_ids[key],
            "dashboard_tab_id": tab_key_to_temp_id[tab_key],
            "row": chart_def["row"],
            "col": chart_def["col"],
            "size_x": chart_def["size_x"],
            "size_y": chart_def["size_y"],
            "series": [],
            "visualization_settings": {},
            "parameter_mappings": [],
        })
        card_temp_id -= 1

    result = mb.setup_dashboard_tabs_and_cards(dashboard_id, tab_defs, cards)
    if not result:
        print("  WARNING: Dashboard layout may not have been applied correctly.")

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Executive Dashboard created successfully!")
    print(f"  URL: {METABASE_URL}/dashboard/{dashboard_id}")
    print(f"  Dashboard ID: {dashboard_id}")
    print(f"  Cards created: {len(card_ids)}")
    print(f"  Tabs: {len(tab_defs)}")
    print("-" * 65)
    print("  Tab E1: Performance Scorecard")
    for k in ["e1_1", "e1_2", "e1_3", "e1_5", "e1_6"]:
        if k in card_ids:
            print(f"    {CHARTS[k]['name']} (id={card_ids[k]})")
    print("  Tab E2: Geographic Intelligence")
    for k in ["e2_1", "e2_2"]:
        if k in card_ids:
            print(f"    {CHARTS[k]['name']} (id={card_ids[k]})")
    print("  Tab E3: Compliance Overview")
    for k in ["e3_1", "e3_2", "e3_3", "e3_4", "e3_5"]:
        if k in card_ids:
            print(f"    {CHARTS[k]['name']} (id={card_ids[k]})")
    print("=" * 65)


if __name__ == "__main__":
    main()
