#!/usr/bin/env python3
"""
Initialize Users and Permissions for BTRC Dashboards
Designed to run automatically in Docker on Metabase startup

Fixes:
- Properly adds admins to built-in Administrators group (ID 2)
- Correctly restricts external users (no SQL, no create)
- Sets proper data permissions using permission graphs
- Handles existing users gracefully
"""

import requests
import json
import time
import sys
import os

# =============================================================================
# Configuration
# =============================================================================
METABASE_URL = os.getenv("METABASE_URL", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("METABASE_ADMIN_EMAIL", "alamin.technometrics22@gmail.com")
ADMIN_PASSWORD = os.getenv("METABASE_ADMIN_PASSWORD", "Test@123")

# Wait for Metabase to be ready
MAX_RETRIES = 30
RETRY_DELAY = 10

# Built-in Metabase Groups
ALL_USERS_GROUP_ID = 1
ADMINISTRATORS_GROUP_ID = 2  # Built-in admin group

# User Definitions
USERS = {
    "admins": [
        {
            "first_name": "System",
            "last_name": "Admin",
            "email": "admin@btrc.gov.bd",
            "password": "Admin@123!",
            "is_superuser": True,
        },
        {
            "first_name": "IT",
            "last_name": "Manager",
            "email": "it.manager@btrc.gov.bd",
            "password": "ITMgr@123!",
            "is_superuser": True,
        },
    ],
    "management": [
        {
            "first_name": "Chief",
            "last_name": "Executive",
            "email": "ceo@btrc.gov.bd",
            "password": "CEO@123!",
        },
        {
            "first_name": "Chief",
            "last_name": "Technology",
            "email": "cto@btrc.gov.bd",
            "password": "CTO@123!",
        },
    ],
    "operations": [
        {
            "first_name": "Project",
            "last_name": "Manager",
            "email": "pm@btrc.gov.bd",
            "password": "PM@123!",
        },
        {
            "first_name": "QoS",
            "last_name": "Analyst",
            "email": "analyst@btrc.gov.bd",
            "password": "Analyst@123!",
        },
    ],
    "regional": [
        {
            "first_name": "Dhaka",
            "last_name": "Officer",
            "email": "dhaka.officer@btrc.gov.bd",
            "password": "Dhaka@123!",
        },
        {
            "first_name": "Chittagong",
            "last_name": "Officer",
            "email": "chittagong.officer@btrc.gov.bd",
            "password": "Chittagong@123!",
        },
    ],
    "external": [
        {
            "first_name": "External",
            "last_name": "Consultant",
            "email": "consultant@example.com",
            "password": "Consult@123!",
        },
    ],
}

# =============================================================================
# Helper Functions
# =============================================================================
def wait_for_metabase(base_url, max_retries=30, delay=10):
    """Wait for Metabase to be ready"""
    print(f"Waiting for Metabase at {base_url}...")
    for i in range(max_retries):
        try:
            resp = requests.get(f"{base_url}/api/health", timeout=5)
            if resp.status_code == 200:
                print("✅ Metabase is ready")
                return True
        except:
            pass

        print(f"  Waiting... ({i+1}/{max_retries})")
        time.sleep(delay)

    print("❌ Metabase did not become ready")
    return False

def login(base_url, email, password):
    """Login and get session token"""
    try:
        resp = requests.post(
            f"{base_url}/api/session",
            json={"username": email, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            token = resp.json()["id"]
            return {"X-Metabase-Session": token}
        return None
    except:
        return None

def create_user(base_url, headers, user_data):
    """Create a user"""
    try:
        resp = requests.post(
            f"{base_url}/api/user",
            json=user_data,
            headers=headers,
            timeout=10
        )
        if resp.status_code in (200, 201):
            return resp.json()

        # Check if user exists
        if "already" in resp.text.lower() or resp.status_code == 400:
            # Find existing user
            resp = requests.get(f"{base_url}/api/user", headers=headers)
            if resp.status_code == 200:
                users = resp.json().get('data', [])
                for u in users:
                    if u.get('email') == user_data['email']:
                        return u
        return None
    except Exception as e:
        print(f"    Error creating user: {e}")
        return None

def add_to_admin_group(base_url, headers, user_id):
    """Add user to built-in Administrators group"""
    try:
        resp = requests.post(
            f"{base_url}/api/permissions/membership",
            json={"user_id": user_id, "group_id": ADMINISTRATORS_GROUP_ID},
            headers=headers,
            timeout=10
        )
        return resp.status_code in (200, 201)
    except:
        return False

def create_group(base_url, headers, name):
    """Create a custom group"""
    try:
        # Check if exists
        resp = requests.get(f"{base_url}/api/permissions/group", headers=headers)
        if resp.status_code == 200:
            groups = resp.json()
            for g in groups:
                if g.get('name') == name:
                    return g

        # Create new
        resp = requests.post(
            f"{base_url}/api/permissions/group",
            json={"name": name},
            headers=headers,
            timeout=10
        )
        if resp.status_code in (200, 201):
            return resp.json()
        return None
    except:
        return None

def add_to_group(base_url, headers, user_id, group_id):
    """Add user to group"""
    try:
        resp = requests.post(
            f"{base_url}/api/permissions/membership",
            json={"user_id": user_id, "group_id": group_id},
            headers=headers,
            timeout=10
        )
        return resp.status_code in (200, 201)
    except:
        return False

def get_database_id(base_url, headers):
    """Get BTRC database ID"""
    try:
        resp = requests.get(f"{base_url}/api/database", headers=headers)
        if resp.status_code == 200:
            databases = resp.json().get("data", [])
            for db in databases:
                details = db.get("details", {})
                if "btrc" in db.get("name", "").lower() or \
                   details.get("dbname") == "btrc_qos_poc":
                    return db["id"]
        return None
    except:
        return None

def set_group_permissions(base_url, headers, group_id, database_id, level):
    """
    Set data permissions for a group

    Levels:
    - "unrestricted": Full access (can write SQL)
    - "no-self-service": Can only use Query Builder
    - "no-access": No database access
    """
    try:
        # Get current permission graph
        resp = requests.get(f"{base_url}/api/permissions/graph", headers=headers)
        if resp.status_code != 200:
            return False

        graph = resp.json()
        group_id_str = str(group_id)
        db_id_str = str(database_id)

        # Initialize structure
        if "groups" not in graph:
            graph["groups"] = {}
        if group_id_str not in graph["groups"]:
            graph["groups"][group_id_str] = {}

        # Set permissions based on level
        if level == "unrestricted":
            # Full access: can write SQL and access all tables
            graph["groups"][group_id_str][db_id_str] = {
                "native": "write",
                "schemas": "all"
            }
        elif level == "no-self-service":
            # Query Builder only: no SQL, but can use GUI
            graph["groups"][group_id_str][db_id_str] = {
                "native": "none",
                "schemas": "all"
            }
        elif level == "no-access":
            # No access at all
            graph["groups"][group_id_str][db_id_str] = {
                "native": "none",
                "schemas": "none"
            }

        # Update permissions
        resp = requests.put(
            f"{base_url}/api/permissions/graph",
            json=graph,
            headers=headers,
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"    Error setting permissions: {e}")
        return False

# =============================================================================
# Main Setup
# =============================================================================
def main():
    print("=" * 70)
    print("BTRC Dashboard - Automated User & Permission Setup")
    print("=" * 70)

    # Wait for Metabase
    if not wait_for_metabase(METABASE_URL, MAX_RETRIES, RETRY_DELAY):
        print("❌ Exiting: Metabase not ready")
        sys.exit(1)

    # Login
    print("\n[1/6] Logging in as admin...")
    headers = login(METABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD)
    if not headers:
        print("❌ Login failed")
        sys.exit(1)
    print("✅ Logged in")

    # Get database ID
    print("\n[2/6] Finding database...")
    db_id = get_database_id(METABASE_URL, headers)
    if not db_id:
        print("⚠️  Database not found, will skip data permissions")
    else:
        print(f"✅ Database found (ID: {db_id})")

    # Create custom groups
    print("\n[3/6] Creating custom groups...")
    groups = {}
    group_names = {
        "management": "Management Team",
        "operations": "Operations Team",
        "regional": "Regional Officers",
        "external": "External Viewers"
    }

    for key, name in group_names.items():
        group = create_group(METABASE_URL, headers, name)
        if group:
            groups[key] = group
            print(f"  ✅ {name} (ID: {group['id']})")

    # Create users
    print("\n[4/6] Creating users and assigning groups...")
    created_users = {}

    for category, user_list in USERS.items():
        print(f"\n  {category.upper()}:")
        for user_data in user_list:
            user = create_user(METABASE_URL, headers, user_data)
            if user:
                email = user_data['email']
                user_id = user['id']
                created_users[email] = user
                print(f"    ✅ {email} (ID: {user_id})")

                # Add admins to Administrators group (ID 2)
                if category == "admins":
                    if add_to_admin_group(METABASE_URL, headers, user_id):
                        print(f"      ✅ Added to Administrators group")
                    else:
                        print(f"      ⚠️  Could not add to Administrators group")

                # Add to custom groups
                elif category in groups:
                    group_id = groups[category]['id']
                    if add_to_group(METABASE_URL, headers, user_id, group_id):
                        print(f"      ✅ Added to {group_names[category]}")

                time.sleep(0.2)

    # Set data permissions
    if db_id:
        print("\n[5/6] Setting data permissions...")

        # All Users group (ID 1) - restrict default access
        print("\n  All Users (default):")
        if set_group_permissions(METABASE_URL, headers, ALL_USERS_GROUP_ID, db_id, "no-self-service"):
            print("    ✅ Set to Query Builder only (no SQL)")

        # Management Team - Query Builder only
        if "management" in groups:
            print("\n  Management Team:")
            if set_group_permissions(METABASE_URL, headers, groups["management"]["id"], db_id, "no-self-service"):
                print("    ✅ Query Builder only (no SQL)")

        # Operations Team - Unrestricted (can write SQL)
        if "operations" in groups:
            print("\n  Operations Team:")
            if set_group_permissions(METABASE_URL, headers, groups["operations"]["id"], db_id, "unrestricted"):
                print("    ✅ Unrestricted access (can write SQL)")

        # Regional Officers - Query Builder only
        if "regional" in groups:
            print("\n  Regional Officers:")
            if set_group_permissions(METABASE_URL, headers, groups["regional"]["id"], db_id, "no-self-service"):
                print("    ✅ Query Builder only (no SQL)")

        # External Viewers - No access
        if "external" in groups:
            print("\n  External Viewers:")
            if set_group_permissions(METABASE_URL, headers, groups["external"]["id"], db_id, "no-access"):
                print("    ✅ No database access")

    # Summary
    print("\n[6/6] Setup complete!")
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    print("\n✅ Created users:")
    print("\n  ADMINISTRATORS (Full Access):")
    for user_data in USERS["admins"]:
        print(f"    📧 {user_data['email']} / 🔑 {user_data['password']}")

    print("\n  MANAGEMENT (View Only):")
    for user_data in USERS["management"]:
        print(f"    📧 {user_data['email']} / 🔑 {user_data['password']}")

    print("\n  OPERATIONS (Can Create SQL):")
    for user_data in USERS["operations"]:
        print(f"    📧 {user_data['email']} / 🔑 {user_data['password']}")

    print("\n  REGIONAL (Query Builder Only):")
    for user_data in USERS["regional"]:
        print(f"    📧 {user_data['email']} / 🔑 {user_data['password']}")

    print("\n  EXTERNAL (No Database Access):")
    for user_data in USERS["external"]:
        print(f"    📧 {user_data['email']} / 🔑 {user_data['password']}")

    print("\n" + "=" * 70)
    print("Testing:")
    print("=" * 70)
    print(f"\n1. Go to: {METABASE_URL}")
    print("2. Login with different users above")
    print("3. Verify:")
    print("   - Admins: See 'Admin' menu, can write SQL")
    print("   - Management: No 'Admin' menu, Query Builder only")
    print("   - Operations: Can write SQL, create dashboards")
    print("   - Regional: Query Builder only")
    print("   - External: Cannot access database")
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
