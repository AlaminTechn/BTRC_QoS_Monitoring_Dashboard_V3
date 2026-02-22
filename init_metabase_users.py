#!/usr/bin/env python3
"""
BTRC QoS Dashboard — Metabase User & Permission Initializer
============================================================
Run this script after a fresh Metabase instance starts to create:
  - 5 custom groups  (BTRC Administrators, Management Team, Operations Team,
                      Regional Officers, External Viewers)
  - 7 test users     (passwords: Test@12345)
  - Data permissions per group

Usage:
  python3 init_metabase_users.py

  # Override defaults via environment variables:
  METABASE_URL=http://localhost:3000 \
  METABASE_ADMIN_EMAIL=admin@example.com \
  METABASE_ADMIN_PASSWORD=your-admin-password \
  python3 init_metabase_users.py

After running, check the printed group ID table and compare with
btrc-react-regional/src/config/permissions.js.  If any IDs differ,
follow the instructions in PERMISSIONS_GUIDE.md to update the React config.
"""

import requests
import json
import time
import sys
import os

# =============================================================================
# Configuration
# =============================================================================
METABASE_URL    = os.getenv("METABASE_URL",             "http://localhost:3000")
ADMIN_EMAIL     = os.getenv("METABASE_ADMIN_EMAIL",     "alamin.technometrics22@gmail.com")
ADMIN_PASSWORD  = os.getenv("METABASE_ADMIN_PASSWORD",  "Test@123")

# Shared password for ALL test / POC accounts
TEST_PASSWORD = "Test@12345"

MAX_RETRIES = 30   # x RETRY_DELAY seconds = 5 min max wait
RETRY_DELAY = 10

# Built-in Metabase group IDs (always present, never change)
ALL_USERS_GROUP_ID     = 1
ADMINISTRATORS_GROUP_ID = 2

# ─────────────────────────────────────────────────────────────────────────────
# Group definitions — order matters: they are created in this order, which
# usually produces sequential IDs (4, 5, 6, 7, 8) on a fresh instance.
# The React app's permissions.js expects:
#   ID 5 → BTRC Administrators
#   ID 6 → Management Team
#   ID 7 → Operations Team
#   ID 8 → Regional Officers
#   ID 9 → External Viewers
# ─────────────────────────────────────────────────────────────────────────────
GROUP_DEFINITIONS = [
    # key            display name            data_level
    ("btrc_admin",   "BTRC Administrators",  "unrestricted"),
    ("management",   "Management Team",      "no-self-service"),
    ("operations",   "Operations Team",      "unrestricted"),
    ("regional",     "Regional Officers",    "no-self-service"),
    ("external",     "External Viewers",     "no-access"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Test users  — all passwords are TEST_PASSWORD
# ─────────────────────────────────────────────────────────────────────────────
USERS = [
    # ── BTRC Administrators ──────────────────────────────────────────────────
    {
        "first_name": "System", "last_name": "Admin",
        "email": "admin@btrc.gov.bd",
        "group_key": "btrc_admin",
        "add_to_metabase_admin": True,   # also put in built-in Administrators
    },
    # ── Management Team ──────────────────────────────────────────────────────
    {
        "first_name": "Chief", "last_name": "Executive",
        "email": "ceo@btrc.gov.bd",
        "group_key": "management",
    },
    # ── Operations Team ──────────────────────────────────────────────────────
    {
        "first_name": "QoS", "last_name": "Analyst",
        "email": "analyst@btrc.gov.bd",
        "group_key": "operations",
    },
    # ── Regional Officers ────────────────────────────────────────────────────
    {
        "first_name": "Dhaka", "last_name": "Officer",
        "email": "dhaka.officer@btrc.gov.bd",
        "group_key": "regional",
    },
    {
        "first_name": "Chittagong", "last_name": "Officer",
        "email": "chittagong.officer@btrc.gov.bd",
        "group_key": "regional",
    },
    # ── External Viewers ─────────────────────────────────────────────────────
    {
        "first_name": "External", "last_name": "Consultant",
        "email": "consultant@example.com",
        "group_key": "external",
    },
]

# =============================================================================
# API Helpers
# =============================================================================

def wait_for_metabase(base_url, max_retries=30, delay=10):
    print(f"\nWaiting for Metabase at {base_url} ...")
    for i in range(max_retries):
        try:
            r = requests.get(f"{base_url}/api/health", timeout=5)
            if r.status_code == 200 and r.json().get("status") == "ok":
                print("✅ Metabase is ready")
                return True
        except Exception:
            pass
        print(f"   [{i+1}/{max_retries}] not ready yet, retrying in {delay}s...")
        time.sleep(delay)
    print("❌ Metabase did not become ready in time")
    return False


def login(base_url, email, password):
    r = requests.post(
        f"{base_url}/api/session",
        json={"username": email, "password": password},
        timeout=10,
    )
    if r.status_code == 200:
        return {"X-Metabase-Session": r.json()["id"]}
    print(f"   ❌ Login failed ({r.status_code}): {r.text[:200]}")
    return None


def get_existing_groups(base_url, headers):
    """Return {name: group_dict} for all existing custom groups."""
    r = requests.get(f"{base_url}/api/permissions/group", headers=headers)
    if r.status_code == 200:
        return {g["name"]: g for g in r.json()}
    return {}


def create_group(base_url, headers, name):
    """Create a group if it does not already exist. Returns group dict."""
    existing = get_existing_groups(base_url, headers)
    if name in existing:
        return existing[name]
    r = requests.post(
        f"{base_url}/api/permissions/group",
        json={"name": name},
        headers=headers,
        timeout=10,
    )
    if r.status_code in (200, 201):
        return r.json()
    print(f"   ❌ Could not create group '{name}': {r.text[:200]}")
    return None


def get_all_users(base_url, headers):
    """Return {email: user_dict} for all users."""
    r = requests.get(f"{base_url}/api/user", headers=headers)
    if r.status_code == 200:
        return {u["email"]: u for u in r.json().get("data", [])}
    return {}


def create_user(base_url, headers, first_name, last_name, email):
    """Create user if not existing. Returns user dict."""
    existing = get_all_users(base_url, headers)
    if email in existing:
        return existing[email]
    r = requests.post(
        f"{base_url}/api/user",
        json={
            "first_name": first_name,
            "last_name":  last_name,
            "email":      email,
            "password":   TEST_PASSWORD,
        },
        headers=headers,
        timeout=10,
    )
    if r.status_code in (200, 201):
        return r.json()
    print(f"   ❌ Could not create user '{email}': {r.text[:200]}")
    return None


def set_password(base_url, headers, user_id, password):
    """Reset a user's password via the correct API endpoint."""
    r = requests.put(
        f"{base_url}/api/user/{user_id}/password",
        json={"password": password},
        headers=headers,
        timeout=10,
    )
    return r.status_code in (200, 204)


def add_to_group(base_url, headers, user_id, group_id):
    """Add user to a permission group (idempotent)."""
    r = requests.post(
        f"{base_url}/api/permissions/membership",
        json={"user_id": user_id, "group_id": group_id},
        headers=headers,
        timeout=10,
    )
    return r.status_code in (200, 201)


def get_database_id(base_url, headers):
    """Find the BTRC QoS database."""
    r = requests.get(f"{base_url}/api/database", headers=headers)
    if r.status_code != 200:
        return None
    for db in r.json().get("data", []):
        if "btrc" in db.get("name", "").lower() or \
           db.get("details", {}).get("dbname") == "btrc_qos_poc":
            return db["id"]
    return None


def set_data_permissions(base_url, headers, group_id, database_id, level):
    """
    level: "unrestricted" | "no-self-service" | "no-access"
    Returns True on success.
    """
    r = requests.get(f"{base_url}/api/permissions/graph", headers=headers)
    if r.status_code != 200:
        return False
    graph = r.json()
    gstr  = str(group_id)
    dbstr = str(database_id)
    if "groups" not in graph:
        graph["groups"] = {}
    if gstr not in graph["groups"]:
        graph["groups"][gstr] = {}

    pmap = {
        "unrestricted":    {"native": "write", "schemas": "all"},
        "no-self-service": {"native": "none",  "schemas": "all"},
        "no-access":       {"native": "none",  "schemas": "none"},
    }
    graph["groups"][gstr][dbstr] = pmap[level]

    r = requests.put(
        f"{base_url}/api/permissions/graph",
        json=graph,
        headers=headers,
        timeout=10,
    )
    return r.status_code == 200


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 70)
    print("  BTRC Dashboard — Metabase User & Permission Setup")
    print("=" * 70)

    # ── 1. Wait for Metabase ─────────────────────────────────────────────────
    if not wait_for_metabase(METABASE_URL, MAX_RETRIES, RETRY_DELAY):
        sys.exit(1)

    # ── 2. Login ─────────────────────────────────────────────────────────────
    print("\n[1/5] Authenticating as admin ...")
    headers = login(METABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD)
    if not headers:
        print("❌ Cannot continue without a valid session.")
        sys.exit(1)
    print("✅ Logged in")

    # ── 3. Find DB ───────────────────────────────────────────────────────────
    print("\n[2/5] Locating BTRC database ...")
    db_id = get_database_id(METABASE_URL, headers)
    if db_id:
        print(f"✅ Found database (ID: {db_id})")
    else:
        print("⚠️  Database not found — data-permission step will be skipped.")

    # ── 4. Create groups ─────────────────────────────────────────────────────
    print("\n[3/5] Creating custom groups ...")
    group_map = {}   # key → group dict

    for key, display_name, _ in GROUP_DEFINITIONS:
        g = create_group(METABASE_URL, headers, display_name)
        if g:
            group_map[key] = g
            print(f"  ✅ '{display_name}' (ID: {g['id']})")
        else:
            print(f"  ❌ Failed to create '{display_name}'")

    # ── 5. Create users, set passwords, assign groups ────────────────────────
    print("\n[4/5] Creating users ...")

    for u in USERS:
        email = u["email"]
        user  = create_user(METABASE_URL, headers, u["first_name"], u["last_name"], email)
        if not user:
            continue

        uid = user["id"]
        print(f"  ✅ {email} (ID: {uid})")

        # Always reset password to TEST_PASSWORD (covers pre-existing users)
        if set_password(METABASE_URL, headers, uid, TEST_PASSWORD):
            print(f"     🔑 Password set to Test@12345")
        else:
            print(f"     ⚠️  Password reset may have failed — verify manually")

        # Add to appropriate custom group
        gkey = u.get("group_key")
        if gkey and gkey in group_map:
            gid = group_map[gkey]["id"]
            if add_to_group(METABASE_URL, headers, uid, gid):
                print(f"     👥 Added to '{group_map[gkey]['name']}'")

        # Also add admins to built-in Administrators group
        if u.get("add_to_metabase_admin"):
            if add_to_group(METABASE_URL, headers, uid, ADMINISTRATORS_GROUP_ID):
                print(f"     🛡️  Added to built-in Administrators group")

        time.sleep(0.2)

    # ── 6. Set data permissions ───────────────────────────────────────────────
    if db_id:
        print("\n[5/5] Setting data permissions ...")

        # Restrict the "All Users" default
        if set_data_permissions(METABASE_URL, headers, ALL_USERS_GROUP_ID, db_id, "no-self-service"):
            print("  ✅ All Users → Query Builder only")

        for key, display_name, level in GROUP_DEFINITIONS:
            if key not in group_map:
                continue
            gid = group_map[key]["id"]
            if set_data_permissions(METABASE_URL, headers, gid, db_id, level):
                label = {"unrestricted": "Full SQL", "no-self-service": "Query Builder", "no-access": "No access"}[level]
                print(f"  ✅ {display_name} → {label}")
            else:
                print(f"  ⚠️  Could not set permissions for {display_name}")
    else:
        print("\n[5/5] Skipping data permissions (no database found)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  SETUP COMPLETE")
    print("=" * 70)

    print("\n📋 Group IDs assigned on this instance:")
    print(f"   {'Group Name':<30} {'ID':>4}   {'React permissions.js expects'}")
    print(f"   {'-'*30} {'-'*4}   {'-'*30}")
    EXPECTED = {
        "BTRC Administrators": 5,
        "Management Team":     6,
        "Operations Team":     7,
        "Regional Officers":   8,
        "External Viewers":    9,
    }
    all_match = True
    for key, display_name, _ in GROUP_DEFINITIONS:
        if key not in group_map:
            print(f"   {'  ' + display_name:<30} {'?':>4}   ⚠️  not created")
            all_match = False
            continue
        actual   = group_map[key]["id"]
        expected = EXPECTED.get(display_name, "?")
        match    = "✅" if actual == expected else "❌ MISMATCH"
        print(f"   {display_name:<30} {actual:>4}   expected {expected}  {match}")
        if actual != expected:
            all_match = False

    print("\n📧 Test accounts (password: Test@12345):")
    print(f"   {'Email':<40} {'Group'}")
    print(f"   {'-'*40} {'-'*25}")
    for u in USERS:
        gkey  = u.get("group_key", "")
        gname = group_map[gkey]["name"] if gkey in group_map else "—"
        print(f"   {u['email']:<40} {gname}")

    if not all_match:
        print("\n" + "⚠️  " * 20)
        print("  ONE OR MORE GROUP IDs DO NOT MATCH WHAT permissions.js EXPECTS.")
        print("  Open btrc-react-regional/src/config/permissions.js and update")
        print("  GROUP_PERMISSIONS so the keys match the actual IDs shown above.")
        print("  See PERMISSIONS_GUIDE.md for step-by-step instructions.")
        print("⚠️  " * 20)
    else:
        print("\n✅ All group IDs match permissions.js — no React config changes needed.")

    print(f"\n🌐 Metabase URL:  {METABASE_URL}")
    print(f"🔑 Admin login:   {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
