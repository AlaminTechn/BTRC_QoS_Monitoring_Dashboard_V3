#!/usr/bin/env python3
"""
Load GeoJSON boundary polygons into geo_divisions and geo_districts tables.

Downloads simplified GeoJSON from geoBoundaries project, matches features
to existing DB records, and updates the PostGIS boundary/centroid columns.

Usage:
    python3 load_geojson_boundaries.py
"""

import json
import os
import sys

import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- GeoJSON files ---
GEODATA_DIR = os.path.join(os.path.dirname(__file__), 'geodata')
DIVISIONS_FILE = os.path.join(GEODATA_DIR, 'bgd_divisions.geojson')
DISTRICTS_FILE = os.path.join(GEODATA_DIR, 'bgd_districts.geojson')

# --- Division matching: GeoJSON ISO code → DB iso_code ---
# Both use BD-A through BD-H, so this is a direct match.

# --- District name mapping: GeoJSON shapeName → DB name_en ---
DISTRICT_NAME_MAP = {
    'Bogra': 'Bogura',
    'Brahamanbaria': 'Brahmanbaria',
    'Chittagong': 'Chattogram',
    "Cox's Bazar": 'Coxsbazar',
    'Jessore': 'Jashore',
    'Jhalokati': 'Jhalakathi',
    'Maulvibazar': 'Moulvibazar',
    'Nawabganj': 'Chapainawabganj',
    'Netrakona': 'Netrokona',
}


def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5433'),
        dbname=os.getenv('DB_NAME', 'btrc_qos_poc'),
        user=os.getenv('DB_USER', 'btrc_admin'),
        password=os.getenv('DB_PASSWORD', 'btrc_poc_2026'),
    )


def load_divisions(conn):
    """Match division GeoJSON features by ISO code and update boundary."""
    with open(DIVISIONS_FILE) as f:
        geojson = json.load(f)

    print(f"\n--- Loading Division Boundaries ({len(geojson['features'])} features) ---")

    cur = conn.cursor()
    # Build DB lookup: iso_code → id
    cur.execute("SELECT id, iso_code, name_en FROM geo_divisions")
    db_divisions = {row[1]: (row[0], row[2]) for row in cur.fetchall()}

    matched = 0
    for feat in geojson['features']:
        iso = feat['properties'].get('shapeISO', '')
        geojson_name = feat['properties'].get('shapeName', '?')
        geom_json = json.dumps(feat['geometry'])

        if iso not in db_divisions:
            print(f"  WARNING: No DB match for ISO={iso} ({geojson_name})")
            continue

        db_id, db_name = db_divisions[iso]
        cur.execute("""
            UPDATE geo_divisions
            SET boundary = ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)),
                centroid = ST_Centroid(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            WHERE id = %s
        """, (geom_json, geom_json, db_id))
        matched += 1
        print(f"  {geojson_name} (ISO {iso}) → {db_name} (id={db_id})")

    conn.commit()
    print(f"  Matched: {matched}/{len(geojson['features'])}")
    return matched


def load_districts(conn):
    """Match district GeoJSON features by name and update boundary."""
    with open(DISTRICTS_FILE) as f:
        geojson = json.load(f)

    print(f"\n--- Loading District Boundaries ({len(geojson['features'])} features) ---")

    cur = conn.cursor()
    # Build DB lookup: lower(name_en) → (id, name_en)
    cur.execute("SELECT id, name_en FROM geo_districts")
    db_districts = {row[1].lower(): (row[0], row[1]) for row in cur.fetchall()}

    matched = 0
    unmatched = []
    for feat in geojson['features']:
        geojson_name = feat['properties'].get('shapeName', '?')
        geom_json = json.dumps(feat['geometry'])

        # Apply name mapping, then match case-insensitively
        mapped_name = DISTRICT_NAME_MAP.get(geojson_name, geojson_name)
        lookup_key = mapped_name.lower()

        if lookup_key not in db_districts:
            unmatched.append(geojson_name)
            continue

        db_id, db_name = db_districts[lookup_key]
        cur.execute("""
            UPDATE geo_districts
            SET boundary = ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)),
                centroid = ST_Centroid(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            WHERE id = %s
        """, (geom_json, geom_json, db_id))
        matched += 1

        rename_note = f" (mapped from '{geojson_name}')" if geojson_name != db_name else ""
        print(f"  {db_name}{rename_note} (id={db_id})")

    conn.commit()
    print(f"  Matched: {matched}/{len(geojson['features'])}")
    if unmatched:
        print(f"  UNMATCHED: {', '.join(unmatched)}")
    return matched


def verify(conn):
    """Print summary of boundary coverage."""
    cur = conn.cursor()
    print("\n--- Verification ---")

    cur.execute("""
        SELECT 'divisions' as tbl, COUNT(*) as total,
               COUNT(boundary) as has_boundary, COUNT(centroid) as has_centroid
        FROM geo_divisions
        UNION ALL
        SELECT 'districts', COUNT(*), COUNT(boundary), COUNT(centroid)
        FROM geo_districts
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} total, {row[2]} boundaries, {row[3]} centroids")

    # Sample boundary check
    cur.execute("""
        SELECT name_en, ST_Area(boundary::geography)/1e6 as area_km2,
               ST_Y(centroid) as lat, ST_X(centroid) as lon
        FROM geo_divisions WHERE boundary IS NOT NULL
        ORDER BY name_en LIMIT 4
    """)
    print("\n  Sample divisions (area in km²):")
    for row in cur.fetchall():
        print(f"    {row[0]}: {row[1]:.0f} km², centroid ({row[2]:.4f}, {row[3]:.4f})")


def main():
    # Check files exist
    for path, label in [(DIVISIONS_FILE, 'Divisions'), (DISTRICTS_FILE, 'Districts')]:
        if not os.path.exists(path):
            print(f"ERROR: {label} GeoJSON not found: {path}")
            sys.exit(1)

    conn = get_connection()
    try:
        div_count = load_divisions(conn)
        dist_count = load_districts(conn)
        verify(conn)
        print(f"\nDone: {div_count} divisions + {dist_count} districts updated.")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
