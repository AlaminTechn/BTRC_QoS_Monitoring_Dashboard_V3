#!/usr/bin/env python3
"""
BTRC QoS POC Data Loader v2.8
Loads JSON data files into PostgreSQL in FK-aware sequence.
Uses execute_values for fast bulk loading of large timeseries files.
"""

import json
import psycopg2
from psycopg2.extras import execute_values, Json
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5433')),
    'dbname': os.getenv('DB_NAME', 'btrc_qos_poc'),
    'user': os.getenv('DB_USER', 'btrc_admin'),
    'password': os.getenv('DB_PASSWORD', 'btrc_poc_2026'),
}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'poc_data_v2.8')

LOAD_SEQUENCE = [
    ('01-foundation/F.01_geo_divisions.json', 'geo_divisions'),
    ('01-foundation/F.02_geo_districts.json', 'geo_districts'),
    ('01-foundation/F.03_geo_upazilas.json', 'geo_upazilas'),
    ('01-foundation/F.04_geo_unions.json', 'geo_unions'),
    ('01-foundation/F.05_isp_license_categories.json', 'isp_license_categories'),
    ('01-foundation/F.06_pop_categories.json', 'pop_categories'),
    ('01-foundation/F.07_upstream_types.json', 'upstream_types'),
    ('01-foundation/F.08_package_types.json', 'package_types'),
    ('01-foundation/F.09_connection_types.json', 'connection_types'),
    ('01-foundation/F.10_qos_parameters.json', 'qos_parameters'),
    ('02-master/M.01_isps.json', 'isps'),
    ('02-master/M.02_pops.json', 'pops'),
    ('02-master/M.03_agents.json', 'software_agents'),
    ('02-master/M.04_packages.json', 'packages'),
    ('02-master/M.05_qos_test_targets.json', 'qos_test_targets'),
    ('02-master/M.06_sla_thresholds.json', 'sla_thresholds'),
    ('03-relationships/R.01_agent_pop_assignments.json', 'agent_pop_assignments'),
    ('03-relationships/R.02_subscriber_snapshots.json', 'isp_subscriber_snapshots'),
    ('04-timeseries/T.01_ts_interface_metrics.json', 'ts_interface_metrics'),
    ('04-timeseries/T.02_ts_subscriber_counts.json', 'ts_subscriber_counts'),
    ('04-timeseries/T.03_ts_qos_measurements.json', 'ts_qos_measurements'),
    ('05-compliance/C.01_violations.json', 'sla_violations'),
]

# JSON column -> DB column renames (per table)
COLUMN_MAPPINGS = {
    'pop_categories': {'tier': 'tier_level'},
    'upstream_types': {'priority': 'display_order'},
}

# Cache for DB column lookups
_db_columns_cache = {}


def get_db_columns(conn, table_name):
    if table_name in _db_columns_cache:
        return _db_columns_cache[table_name]
    cursor = conn.cursor()
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = %s",
        (table_name,)
    )
    cols = {row[0] for row in cursor.fetchall()}
    _db_columns_cache[table_name] = cols
    return cols


def filter_and_map_data(data, table_name, db_columns):
    mappings = COLUMN_MAPPINGS.get(table_name, {})
    filtered = []
    for record in data:
        new_record = {}
        for key, value in record.items():
            col_name = mappings.get(key, key)  # rename if mapped
            if col_name in db_columns:          # keep only DB columns
                new_record[col_name] = value
        filtered.append(new_record)
    return filtered, mappings


def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _adapt_value(val):
    """Wrap dicts as psycopg2 Json for jsonb columns. Lists pass through
    natively for PostgreSQL array columns."""
    if isinstance(val, dict):
        return Json(val)
    return val


def insert_data(conn, table_name, data, batch_size=5000):
    if not data:
        return 0

    columns = list(data[0].keys())
    cols_str = ', '.join(columns)
    template = '(' + ', '.join(['%s'] * len(columns)) + ')'

    cursor = conn.cursor()
    inserted = 0

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        values = [tuple(_adapt_value(record.get(col)) for col in columns) for record in batch]

        try:
            execute_values(
                cursor,
                f"INSERT INTO {table_name} ({cols_str}) VALUES %s ON CONFLICT DO NOTHING",
                values,
                template=template,
                page_size=batch_size
            )
            inserted += len(batch)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"  Error at batch {i//batch_size}: {e}")
            raise

        if len(data) > 10000 and (i + batch_size) % 50000 == 0:
            pct = min(100, (i + batch_size) * 100 // len(data))
            print(f"  ... {pct}% ({i + batch_size:,}/{len(data):,})")

    return inserted


def main():
    print("=" * 60)
    print("BTRC QoS POC Data Loader v2.8")
    print("=" * 60)

    print(f"\nConnecting to {DB_CONFIG['dbname']} on port {DB_CONFIG['port']}...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    print("Connected.\n")

    total_records = 0
    total_start = time.time()

    for filepath_rel, table_name in LOAD_SEQUENCE:
        filepath = os.path.join(DATA_DIR, filepath_rel)
        if not os.path.exists(filepath):
            print(f"SKIP: {filepath_rel} (not found)")
            continue

        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"Loading {filepath_rel} ({file_size_mb:.1f} MB) -> {table_name}...")

        start = time.time()
        data = load_json_file(filepath)
        load_time = time.time() - start
        print(f"  Parsed {len(data):,} records in {load_time:.1f}s")

        # Capture original keys before filtering
        original_keys = set(data[0].keys()) if data else set()

        # Filter & map columns to match DB schema
        db_columns = get_db_columns(conn, table_name)
        data, mappings = filter_and_map_data(data, table_name, db_columns)

        # Log renamed/skipped columns
        mapped_cols = [f"{k}->{v}" for k, v in mappings.items()]
        skipped_cols = [k for k in original_keys
                       if mappings.get(k, k) not in db_columns]
        if mapped_cols or skipped_cols:
            parts = []
            if mapped_cols:
                parts.append(f"Mapped: {', '.join(mapped_cols)}")
            if skipped_cols:
                parts.append(f"Skipped: {', '.join(sorted(skipped_cols))}")
            print(f"  {' | '.join(parts)}")

        start = time.time()
        try:
            inserted = insert_data(conn, table_name, data)
            elapsed = time.time() - start
            print(f"  Inserted: {inserted:,} records in {elapsed:.1f}s")
            total_records += inserted
        except Exception as e:
            print(f"  FAILED: {e}")
            break

    conn.close()
    total_elapsed = time.time() - total_start

    print("\n" + "=" * 60)
    print(f"TOTAL RECORDS LOADED: {total_records:,}")
    print(f"TOTAL TIME: {total_elapsed:.1f}s")
    print("=" * 60)


if __name__ == '__main__':
    main()
