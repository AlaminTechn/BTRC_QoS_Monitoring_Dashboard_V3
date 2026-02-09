#!/usr/bin/env python3
"""
BTRC QoS Monitoring Dashboard — Regulatory Operations Dashboard (Metabase)

Creates the Regulatory Operations Dashboard in Metabase via REST API.
Implements Dashboard 2 from the POC spec with 3 tabs, 12 charts, and
dashboard filter parameters for Division/District/ISP drill-down.

Dashboard URL: http://localhost:3000/dashboard/<id>

Tabs:
  R1: SLA Monitoring       (3 KPI status cards)
  R2: Regional Drill-Down  (3 data tables with filter support)
  R3: Violation Analysis   (3 KPI cards + detail table + trend + breakdown)

Filters:
  - Division  (cascading to District)
  - District
  - ISP

Usage:
    1. Set credentials in .env file (METABASE_EMAIL, METABASE_PASSWORD)
    2. python3 create_metabase_regulatory_dashboard.py
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

DASHBOARD_NAME = "Regulatory Operations Dashboard"
DASHBOARD_DESC = (
    "Drill-down dashboard for BTRC compliance officers. "
    "SLA monitoring, regional analysis down to district level, "
    "and violation tracking with time filters."
)

GRID_WIDTH = 18

# =============================================================================
#  SQL Queries — Regulatory Dashboard
# =============================================================================

# ─── Tab R1: SLA Monitoring ─────────────────────────────────────────────────

R1_1_SQL = """
SELECT COUNT(*) as "Compliant ISPs"
FROM (
    SELECT i.id
    FROM isps i
    WHERE i.license_status = 'ACTIVE'
      AND i.id NOT IN (
          SELECT DISTINCT v.isp_id
          FROM sla_violations v
          WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
      )
) sub
"""

R1_2_SQL = """
SELECT COUNT(*) as "At Risk ISPs"
FROM (
    SELECT i.id
    FROM isps i
    JOIN sla_violations v ON v.isp_id = i.id
    WHERE i.license_status = 'ACTIVE'
      AND v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
    GROUP BY i.id
    HAVING COUNT(v.id) BETWEEN 1 AND 2
) sub
"""

R1_3_SQL = """
SELECT COUNT(*) as "Violation ISPs"
FROM (
    SELECT i.id
    FROM isps i
    JOIN sla_violations v ON v.isp_id = i.id
    WHERE i.license_status = 'ACTIVE'
      AND v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
    GROUP BY i.id
    HAVING COUNT(v.id) >= 3
) sub
"""

# ─── Tab R2: Regional Drill-Down ────────────────────────────────────────────

R2_1_SQL = """
SELECT
    d.name_en as "Division",
    ROUND(AVG(m.download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)",
    ROUND(AVG(m.upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)",
    ROUND(AVG(m.latency_ms)::numeric, 1) as "Avg Latency (ms)",
    ROUND(
        (COUNT(*) FILTER (WHERE m.test_status = 'SUCCESS')::numeric /
         NULLIF(COUNT(*)::numeric, 0)) * 100, 2
    ) as "Availability (%)",
    COUNT(DISTINCT p.isp_id) as "ISP Count",
    COUNT(DISTINCT p.id) as "PoP Count",
    COALESCE(viol.violation_count, 0) as "Violations",
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
LEFT JOIN (
    SELECT dv.id as division_id, COUNT(v.id) as violation_count
    FROM sla_violations v
    JOIN pops vp ON vp.id = v.pop_id
    JOIN geo_districts vgd ON vgd.id = vp.district_id
    JOIN geo_divisions dv ON dv.id = vgd.division_id
    WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
    GROUP BY dv.id
) viol ON viol.division_id = d.id
WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
[[ AND d.name_en = {{division}} ]]
GROUP BY d.id, d.name_en, viol.violation_count
ORDER BY "Avg Download (Mbps)" DESC
"""

R2_2_SQL = """
SELECT
    d.name_en as "Division",
    gd.name_en as "District",
    ROUND(AVG(m.download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)",
    ROUND(AVG(m.upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)",
    ROUND(AVG(m.latency_ms)::numeric, 1) as "Avg Latency (ms)",
    ROUND(
        (COUNT(*) FILTER (WHERE m.test_status = 'SUCCESS')::numeric /
         NULLIF(COUNT(*)::numeric, 0)) * 100, 2
    ) as "Availability (%)",
    COUNT(DISTINCT p.isp_id) as "ISP Count",
    COUNT(DISTINCT p.id) as "PoP Count"
FROM ts_qos_measurements m
JOIN software_agents sa ON sa.id = m.agent_id
JOIN agent_pop_assignments apa ON apa.agent_id = sa.id
JOIN pops p ON p.id = apa.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
GROUP BY d.id, d.name_en, gd.id, gd.name_en
ORDER BY d.name_en, "Avg Download (Mbps)" DESC
"""

R2_3_SQL = """
SELECT
    d.name_en as "Division",
    gd.name_en as "District",
    i.name_en as "ISP",
    lc.name_en as "License Category",
    COUNT(DISTINCT p.id) as "PoP Count",
    ROUND(AVG(m.download_speed_mbps)::numeric, 2) as "Avg Download (Mbps)",
    ROUND(AVG(m.upload_speed_mbps)::numeric, 2) as "Avg Upload (Mbps)",
    ROUND(AVG(m.latency_ms)::numeric, 1) as "Avg Latency (ms)",
    ROUND(
        (COUNT(*) FILTER (WHERE m.test_status = 'SUCCESS')::numeric /
         NULLIF(COUNT(*)::numeric, 0)) * 100, 2
    ) as "Availability (%)",
    COALESCE(viol.violation_count, 0) as "Violations"
FROM ts_qos_measurements m
JOIN software_agents sa ON sa.id = m.agent_id
JOIN agent_pop_assignments apa ON apa.agent_id = sa.id
JOIN pops p ON p.id = apa.pop_id
JOIN isps i ON i.id = p.isp_id
LEFT JOIN isp_license_categories lc ON lc.id = i.license_category_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
LEFT JOIN (
    SELECT v.isp_id, COUNT(v.id) as violation_count
    FROM sla_violations v
    WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
    GROUP BY v.isp_id
) viol ON viol.isp_id = i.id
WHERE m.timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '30 days'
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
[[ AND i.name_en = {{isp}} ]]
GROUP BY d.name_en, gd.name_en, i.id, i.name_en, lc.name_en, viol.violation_count
ORDER BY d.name_en, gd.name_en, "Avg Download (Mbps)" DESC
"""

# ─── Tab R3: Violation Analysis ─────────────────────────────────────────────

R3_1_SQL = """
SELECT COUNT(*) as "Pending Violations"
FROM sla_violations v
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
  AND v.status IN ('DETECTED', 'INVESTIGATING')
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
"""

R3_2_SQL = """
SELECT COUNT(*) as "Active (Disputed)"
FROM sla_violations v
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
  AND v.status = 'DISPUTED'
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
"""

R3_3_SQL = """
SELECT COUNT(*) as "Resolved Violations"
FROM sla_violations v
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
  AND v.status IN ('RESOLVED', 'WAIVED')
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
"""

R3_4_SQL = """
SELECT
    v.id as "ID",
    i.name_en as "ISP",
    v.violation_type as "Type",
    v.severity as "Severity",
    d.name_en as "Division",
    gd.name_en as "District",
    v.status as "Status",
    v.detection_time as "Detected At",
    ROUND(v.expected_value::numeric, 2) as "Expected",
    ROUND(v.actual_value::numeric, 2) as "Actual",
    ROUND(v.deviation_pct::numeric, 1) as "Deviation %",
    v.affected_subscribers_est as "Affected Subscribers"
FROM sla_violations v
JOIN isps i ON i.id = v.isp_id
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
[[ AND i.name_en = {{isp}} ]]
ORDER BY
    CASE v.severity
        WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3 WHEN 'LOW' THEN 4 ELSE 5
    END,
    v.detection_time DESC
"""

R3_5_SQL = """
SELECT
    DATE_TRUNC('day', v.detection_time) as "Date",
    v.severity as "Severity",
    COUNT(*) as "Count"
FROM sla_violations v
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
GROUP BY DATE_TRUNC('day', v.detection_time), v.severity
ORDER BY "Date", v.severity
"""

R3_6_SQL = """
SELECT
    d.name_en as "Division",
    gd.name_en as "District",
    COUNT(*) as "Total",
    COUNT(*) FILTER (WHERE v.severity = 'CRITICAL') as "Critical",
    COUNT(*) FILTER (WHERE v.severity = 'HIGH') as "High",
    COUNT(*) FILTER (WHERE v.severity = 'MEDIUM') as "Medium",
    COUNT(*) FILTER (WHERE v.severity = 'LOW') as "Low"
FROM sla_violations v
JOIN pops p ON p.id = v.pop_id
JOIN geo_districts gd ON gd.id = p.district_id
JOIN geo_divisions d ON d.id = gd.division_id
WHERE v.detection_time >= (SELECT MAX(detection_time) FROM sla_violations) - INTERVAL '30 days'
[[ AND d.name_en = {{division}} ]]
[[ AND gd.name_en = {{district}} ]]
GROUP BY d.id, d.name_en, gd.id, gd.name_en
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

    def re_login(self, email, password):
        """Re-authenticate to refresh session token."""
        return self.login(email, password)

    def get(self, path, **kwargs):
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

    def find_database(self, db_name="btrc_qos_poc"):
        resp = self.get("/api/database")
        if resp.status_code != 200:
            return None
        databases = resp.json().get("data", resp.json() if isinstance(resp.json(), list) else [])
        for db in databases:
            if db.get("name", "").lower() == db_name.lower() or \
               db.get("details", {}).get("db", "") == db_name:
                self.database_id = db["id"]
                return db["id"]
        for db in databases:
            details = db.get("details", {})
            if details.get("dbname") == db_name or details.get("db") == db_name:
                self.database_id = db["id"]
                return db["id"]
        return None

    def create_card(self, name, sql, display="table", description="",
                    visualization_settings=None, collection_id=None,
                    template_tags=None):
        """Create a native SQL question (card). Returns card dict or None."""
        native = {"query": sql}
        if template_tags:
            native["template-tags"] = template_tags
        payload = {
            "name": name,
            "description": description,
            "dataset_query": {
                "database": self.database_id,
                "native": native,
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
        resp = self.post("/api/collection", json={
            "name": name, "description": description
        })
        if resp.status_code in (200, 201):
            coll = resp.json()
            print(f"  Collection '{name}' created (id={coll['id']})")
            return coll
        else:
            print(f"  Collection '{name}' error ({resp.status_code}): {resp.text[:200]}")
            return None

    def create_dashboard(self, name, description="", collection_id=None,
                         parameters=None):
        payload = {"name": name, "description": description}
        if collection_id:
            payload["collection_id"] = collection_id
        if parameters:
            payload["parameters"] = parameters
        resp = self.post("/api/dashboard", json=payload)
        if resp.status_code in (200, 201):
            dash = resp.json()
            print(f"  Dashboard '{name}' created (id={dash['id']})")
            return dash
        else:
            print(f"  Dashboard '{name}' FAILED ({resp.status_code}): {resp.text[:300]}")
            return None

    def setup_dashboard_tabs_and_cards(self, dashboard_id, ordered_tabs, cards):
        """Create tabs and place cards using PUT /api/dashboard/{id}.

        Steps:
          1. PUT with tabs only to create tabs and get real IDs
          2. Map negative temp tab IDs to real IDs
          3. PUT with real tab IDs in dashcards
        """
        tab_payload = {"tabs": ordered_tabs, "dashcards": []}
        resp = self.put(f"/api/dashboard/{dashboard_id}", json=tab_payload)
        if resp.status_code != 200:
            print(f"  Tab creation FAILED ({resp.status_code}): {resp.text[:300]}")
            return None

        result = resp.json()
        created_tabs = result.get("tabs", [])
        if not created_tabs:
            print("  WARNING: No tabs returned.")
        else:
            temp_to_real = {}
            for orig_tab, created_tab in zip(ordered_tabs, created_tabs):
                temp_to_real[orig_tab["id"]] = created_tab["id"]
            print(f"  Tabs created: {len(created_tabs)} "
                  f"(IDs: {[t['id'] for t in created_tabs]})")
            for card in cards:
                old_tab_id = card.get("dashboard_tab_id")
                if old_tab_id in temp_to_real:
                    card["dashboard_tab_id"] = temp_to_real[old_tab_id]
            ordered_tabs = [{"id": t["id"], "name": t["name"]}
                            for t in created_tabs]

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
        resp = self.delete(f"/api/dashboard/{dashboard_id}")
        return resp.status_code == 204


# =============================================================================
#  Template Tags for Filter Parameters
# =============================================================================
def make_text_tag(name, display_name):
    """Create a Metabase native query template tag definition."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "display-name": display_name,
        "type": "text",
    }


# Template tag definitions (reused across queries)
TAG_DIVISION = make_text_tag("division", "Division")
TAG_DISTRICT = make_text_tag("district", "District")
TAG_ISP = make_text_tag("isp", "ISP")


def tags_for(*names):
    """Return template-tags dict for given variable names."""
    tag_map = {
        "division": TAG_DIVISION,
        "district": TAG_DISTRICT,
        "isp": TAG_ISP,
    }
    return {n: tag_map[n] for n in names if n in tag_map}


# =============================================================================
#  Dashboard Parameters (filter widgets)
# =============================================================================
PARAM_DIVISION_ID = str(uuid.uuid4())
PARAM_DISTRICT_ID = str(uuid.uuid4())
PARAM_ISP_ID = str(uuid.uuid4())

DASHBOARD_PARAMETERS = [
    {
        "id": PARAM_DIVISION_ID,
        "name": "Division",
        "slug": "division",
        "type": "string/=",
        "sectionId": "string",
    },
    {
        "id": PARAM_DISTRICT_ID,
        "name": "District",
        "slug": "district",
        "type": "string/=",
        "sectionId": "string",
    },
    {
        "id": PARAM_ISP_ID,
        "name": "ISP",
        "slug": "isp",
        "type": "string/=",
        "sectionId": "string",
    },
]


def param_mapping(param_id, card_id, tag_name):
    """Create a parameter_mapping entry linking a dashboard param to a card template tag."""
    return {
        "parameter_id": param_id,
        "card_id": card_id,
        "target": ["variable", ["template-tag", tag_name]],
    }


# =============================================================================
#  Chart Definitions
# =============================================================================
CHARTS = {
    # ─── Tab R1: SLA Monitoring ─────────────────────────────────────────────
    "r1_1": {
        "name": "R1.1 Compliant ISPs",
        "sql": R1_1_SQL,
        "display": "scalar",
        "description": "Count of ISPs with zero SLA violations in the last 30 days",
        "viz_settings": {
            "scalar.field": "Compliant ISPs",
        },
        "template_tags": {},
        "param_tags": [],
        "tab": "r1",
        "col": 0, "row": 0, "size_x": 6, "size_y": 4,
    },
    "r1_2": {
        "name": "R1.2 At Risk ISPs",
        "sql": R1_2_SQL,
        "display": "scalar",
        "description": "Count of ISPs with 1-2 SLA violations (approaching threshold)",
        "viz_settings": {
            "scalar.field": "At Risk ISPs",
        },
        "template_tags": {},
        "param_tags": [],
        "tab": "r1",
        "col": 6, "row": 0, "size_x": 6, "size_y": 4,
    },
    "r1_3": {
        "name": "R1.3 Violation ISPs",
        "sql": R1_3_SQL,
        "display": "scalar",
        "description": "Count of ISPs currently in SLA violation (3+ violations)",
        "viz_settings": {
            "scalar.field": "Violation ISPs",
        },
        "template_tags": {},
        "param_tags": [],
        "tab": "r1",
        "col": 12, "row": 0, "size_x": 6, "size_y": 4,
    },

    # ─── Tab R2: Regional Drill-Down ────────────────────────────────────────
    "r2_1": {
        "name": "R2.1 Division Performance Summary",
        "sql": R2_1_SQL,
        "display": "table",
        "description": "Division-level performance with speed, availability, violations, "
                       "and performance tier. Filterable by Division.",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Avg Download (Mbps)"]': {"show_mini_bar": True, "decimals": 2},
                '["name","Avg Upload (Mbps)"]': {"show_mini_bar": True, "decimals": 2},
                '["name","Availability (%)"]': {"show_mini_bar": True, "decimals": 2, "suffix": "%"},
                '["name","Violations"]': {"show_mini_bar": True},
            },
        },
        "template_tags": tags_for("division"),
        "param_tags": ["division"],
        "tab": "r2",
        "col": 0, "row": 0, "size_x": 18, "size_y": 8,
    },
    "r2_2": {
        "name": "R2.2 District Ranking Table",
        "sql": R2_2_SQL,
        "display": "table",
        "description": "District-level ranking with speed, availability, and PoP metrics. "
                       "Drill-down: filter by Division to see its districts.",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Avg Download (Mbps)"]': {"show_mini_bar": True, "decimals": 2},
                '["name","Avg Upload (Mbps)"]': {"show_mini_bar": True, "decimals": 2},
                '["name","Availability (%)"]': {"show_mini_bar": True, "decimals": 2, "suffix": "%"},
            },
        },
        "template_tags": tags_for("division", "district"),
        "param_tags": ["division", "district"],
        "tab": "r2",
        "col": 0, "row": 8, "size_x": 18, "size_y": 10,
    },
    "r2_3": {
        "name": "R2.3 ISP Performance by Area",
        "sql": R2_3_SQL,
        "display": "table",
        "description": "ISP-level performance within selected Division/District. "
                       "Shows PoP count, speed, availability, and violations per ISP.",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Avg Download (Mbps)"]': {"show_mini_bar": True, "decimals": 2},
                '["name","Avg Upload (Mbps)"]': {"show_mini_bar": True, "decimals": 2},
                '["name","Availability (%)"]': {"show_mini_bar": True, "decimals": 2, "suffix": "%"},
                '["name","Violations"]': {"show_mini_bar": True},
            },
        },
        "template_tags": tags_for("division", "district", "isp"),
        "param_tags": ["division", "district", "isp"],
        "tab": "r2",
        "col": 0, "row": 18, "size_x": 18, "size_y": 10,
    },

    # ─── Tab R3: Violation Analysis ─────────────────────────────────────────
    "r3_1": {
        "name": "R3.1 Pending Violations",
        "sql": R3_1_SQL,
        "display": "scalar",
        "description": "Violations with DETECTED or INVESTIGATING status",
        "viz_settings": {
            "scalar.field": "Pending Violations",
        },
        "template_tags": tags_for("division", "district"),
        "param_tags": ["division", "district"],
        "tab": "r3",
        "col": 0, "row": 0, "size_x": 6, "size_y": 4,
    },
    "r3_2": {
        "name": "R3.2 Active (Disputed) Violations",
        "sql": R3_2_SQL,
        "display": "scalar",
        "description": "Violations currently under dispute by ISPs",
        "viz_settings": {
            "scalar.field": "Active (Disputed)",
        },
        "template_tags": tags_for("division", "district"),
        "param_tags": ["division", "district"],
        "tab": "r3",
        "col": 6, "row": 0, "size_x": 6, "size_y": 4,
    },
    "r3_3": {
        "name": "R3.3 Resolved Violations",
        "sql": R3_3_SQL,
        "display": "scalar",
        "description": "Violations resolved or waived in the selected period",
        "viz_settings": {
            "scalar.field": "Resolved Violations",
        },
        "template_tags": tags_for("division", "district"),
        "param_tags": ["division", "district"],
        "tab": "r3",
        "col": 12, "row": 0, "size_x": 6, "size_y": 4,
    },
    "r3_4": {
        "name": "R3.4 Violation Detail Table",
        "sql": R3_4_SQL,
        "display": "table",
        "description": "Full violation list: ISP, Type, Severity, Division, District, "
                       "Status, Expected vs Actual values. Sortable and filterable.",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Deviation %"]': {"show_mini_bar": True},
                '["name","Affected Subscribers"]': {"show_mini_bar": True},
            },
        },
        "template_tags": tags_for("division", "district", "isp"),
        "param_tags": ["division", "district", "isp"],
        "tab": "r3",
        "col": 0, "row": 4, "size_x": 18, "size_y": 10,
    },
    "r3_5": {
        "name": "R3.5 Violation Trend",
        "sql": R3_5_SQL,
        "display": "bar",
        "description": "Daily violation count by severity over the selected period (stacked bar)",
        "viz_settings": {
            "graph.dimensions": ["Date"],
            "graph.metrics": ["Count"],
            "graph.series_order_dimension": "Severity",
            "stackable.stack_type": "stacked",
            "graph.x_axis.title_text": "Date",
            "graph.y_axis.title_text": "Violations",
            "graph.show_values": False,
        },
        "template_tags": tags_for("division", "district"),
        "param_tags": ["division", "district"],
        "tab": "r3",
        "col": 0, "row": 14, "size_x": 9, "size_y": 8,
    },
    "r3_6": {
        "name": "R3.6 Violations by District",
        "sql": R3_6_SQL,
        "display": "table",
        "description": "Violation breakdown by Division/District and severity level",
        "viz_settings": {
            "table.pivot": False,
            "column_settings": {
                '["name","Total"]': {"show_mini_bar": True},
                '["name","Critical"]': {"show_mini_bar": True},
                '["name","High"]': {"show_mini_bar": True},
                '["name","Medium"]': {"show_mini_bar": True},
                '["name","Low"]': {"show_mini_bar": True},
            },
        },
        "template_tags": tags_for("division", "district"),
        "param_tags": ["division", "district"],
        "tab": "r3",
        "col": 9, "row": 14, "size_x": 9, "size_y": 8,
    },
}


# =============================================================================
#  Main Script
# =============================================================================
def main():
    print("=" * 65)
    print("  BTRC Regulatory Operations Dashboard Creator (Metabase)")
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
        sys.exit(1)

    # ── Initialize client ────────────────────────────────────────────────
    mb = MetabaseClient(METABASE_URL)

    # Step 1: Login
    print(f"\n[1/7] Authenticating as {email}...")
    if not mb.login(email, password):
        print("  FATAL: Authentication failed.")
        sys.exit(1)
    print("  Logged in successfully.")

    # Step 2: Find database
    print("\n[2/7] Finding database...")
    db_id = mb.find_database("btrc_qos_poc")
    if not db_id:
        db_id = mb.find_database("BTRC QoS")
    if not db_id:
        print("  ERROR: Could not find btrc_qos_poc database.")
        sys.exit(1)
    print(f"  Database found (id={db_id})")

    # Step 3: Create collection
    print("\n[3/7] Creating collection...")
    collection = mb.create_collection(
        "Regulatory Dashboard",
        "Charts for the Regulatory Operations Dashboard"
    )
    collection_id = collection["id"] if collection else None

    # Step 4: Create all cards
    print("\n[4/7] Creating cards (questions)...")
    card_ids = {}
    for key, chart_def in CHARTS.items():
        card = mb.create_card(
            name=chart_def["name"],
            sql=chart_def["sql"],
            display=chart_def["display"],
            description=chart_def["description"],
            visualization_settings=chart_def["viz_settings"],
            collection_id=collection_id,
            template_tags=chart_def.get("template_tags") or None,
        )
        if card:
            card_ids[key] = card["id"]
        else:
            print(f"  WARNING: Card '{chart_def['name']}' creation failed.")
        time.sleep(0.3)

    if not card_ids:
        print("  FATAL: No cards created.")
        sys.exit(1)
    print(f"  Created {len(card_ids)}/{len(CHARTS)} cards.")

    # Re-login to avoid session expiry
    mb.re_login(email, password)

    # Step 5: Create dashboard with parameters
    print("\n[5/7] Creating dashboard...")
    existing = mb.find_existing_dashboard(DASHBOARD_NAME)
    if existing:
        print(f"  Found existing dashboard (id={existing['id']}). Deleting...")
        mb.delete_dashboard(existing["id"])
        time.sleep(0.5)

    dashboard = mb.create_dashboard(
        DASHBOARD_NAME,
        DASHBOARD_DESC,
        collection_id=collection_id,
        parameters=DASHBOARD_PARAMETERS,
    )
    if not dashboard:
        print("  FATAL: Dashboard creation failed.")
        sys.exit(1)
    dashboard_id = dashboard["id"]

    # Step 6: Set up tabs and cards
    print("\n[6/7] Setting up tabs and cards with layout...")

    tab_defs = [
        {"id": -1, "name": "R1: SLA Monitoring"},
        {"id": -2, "name": "R2: Regional Drill-Down"},
        {"id": -3, "name": "R3: Violation Analysis"},
    ]
    tab_key_to_temp_id = {"r1": -1, "r2": -2, "r3": -3}

    # Build dashcards array
    cards = []
    card_temp_id = -1
    for key, chart_def in CHARTS.items():
        if key not in card_ids:
            continue
        tab_key = chart_def["tab"]

        # Build parameter_mappings for this card
        mappings = []
        param_id_map = {
            "division": PARAM_DIVISION_ID,
            "district": PARAM_DISTRICT_ID,
            "isp": PARAM_ISP_ID,
        }
        for tag_name in chart_def.get("param_tags", []):
            if tag_name in param_id_map:
                mappings.append(param_mapping(
                    param_id_map[tag_name],
                    card_ids[key],
                    tag_name,
                ))

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
            "parameter_mappings": mappings,
        })
        card_temp_id -= 1

    # Re-login before final API call
    mb.re_login(email, password)

    result = mb.setup_dashboard_tabs_and_cards(dashboard_id, tab_defs, cards)
    if not result:
        print("  WARNING: Dashboard layout may not have been applied correctly.")

    # Step 7: Update dashboard to ensure parameters are set
    print("\n[7/7] Finalizing dashboard parameters...")
    mb.re_login(email, password)
    resp = mb.put(f"/api/dashboard/{dashboard_id}", json={
        "parameters": DASHBOARD_PARAMETERS,
    })
    if resp.status_code == 200:
        print("  Dashboard parameters configured.")
    else:
        print(f"  Parameter update: {resp.status_code}")

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Regulatory Operations Dashboard created successfully!")
    print(f"  URL: {METABASE_URL}/dashboard/{dashboard_id}")
    print(f"  Dashboard ID: {dashboard_id}")
    print(f"  Cards created: {len(card_ids)}")
    print(f"  Tabs: {len(tab_defs)}")
    print(f"  Filter Parameters: Division, District, ISP")
    print("-" * 65)
    print("  Tab R1: SLA Monitoring")
    for k in ["r1_1", "r1_2", "r1_3"]:
        if k in card_ids:
            print(f"    {CHARTS[k]['name']} (id={card_ids[k]})")
    print("  Tab R2: Regional Drill-Down")
    for k in ["r2_1", "r2_2", "r2_3"]:
        if k in card_ids:
            print(f"    {CHARTS[k]['name']} (id={card_ids[k]})")
    print("  Tab R3: Violation Analysis")
    for k in ["r3_1", "r3_2", "r3_3", "r3_4", "r3_5", "r3_6"]:
        if k in card_ids:
            print(f"    {CHARTS[k]['name']} (id={card_ids[k]})")
    print("=" * 65)
    print("\n  Drill-Down Usage:")
    print("    1. Select a Division → All tables filter to that division")
    print("    2. Select a District → Tables drill down to district level")
    print("    3. Select an ISP → ISP-specific tables filter accordingly")
    print("    4. Clear filters → Return to national view")


if __name__ == "__main__":
    main()
