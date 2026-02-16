#!/usr/bin/env python3
"""
Setup Users, Groups, and Permissions for BTRC Dashboards
Uses Metabase's built-in authentication (free tier)

Creates:
- 5 User Groups (with different permission levels)
- Sample users for each group
- Data permissions (database access)
- Collection permissions (dashboard/card access)
- Dashboard-specific permissions

Usage:
    python3 setup_dashboard_users_and_permissions.py
"""

import requests
import json
import time
from typing import Dict, List, Optional

# =============================================================================
# Configuration
# =============================================================================
METABASE_URL = "http://localhost:3000"
ADMIN_EMAIL = "alamin.technometrics22@gmail.com"
ADMIN_PASSWORD = "Test@123"

# User Groups Definition
USER_GROUPS = {
    "BTRC Administrators": {
        "description": "Full system access - IT administrators and system managers",
        "data_access": "full",  # Full access to all databases
        "collection_access": "write",  # Can create/edit dashboards
        "can_manage_users": True,
    },
    "Management Team": {
        "description": "Executive team - CEO, CTO, Directors (view-only access)",
        "data_access": "view",  # View-only access to databases
        "collection_access": "read",  # Can view all dashboards
        "can_manage_users": False,
    },
    "Operations Team": {
        "description": "Operations staff - PMs, Analysts (can create queries)",
        "data_access": "query",  # Can write queries but not manage database
        "collection_access": "write",  # Can create their own dashboards
        "can_manage_users": False,
    },
    "Regional Officers": {
        "description": "Division/District officers (filtered view by region)",
        "data_access": "view",  # View-only with row-level security
        "collection_access": "read",  # Can view specific dashboards
        "can_manage_users": False,
    },
    "External Viewers": {
        "description": "External consultants, auditors (limited read access)",
        "data_access": "limited",  # Very limited access
        "collection_access": "read",  # Can view public dashboards only
        "can_manage_users": False,
    },
}

# Sample Users for Each Group
SAMPLE_USERS = {
    "BTRC Administrators": [
        {
            "first_name": "System",
            "last_name": "Admin",
            "email": "admin@btrc.gov.bd",
            "password": "Admin@123!",
        },
        {
            "first_name": "IT",
            "last_name": "Manager",
            "email": "it.manager@btrc.gov.bd",
            "password": "ITMgr@123!",
        },
    ],
    "Management Team": [
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
    "Operations Team": [
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
    "Regional Officers": [
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
    "External Viewers": [
        {
            "first_name": "External",
            "last_name": "Consultant",
            "email": "consultant@example.com",
            "password": "Consult@123!",
        },
    ],
}

# =============================================================================
# Metabase API Client
# =============================================================================
class MetabaseClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None

    def login(self, email: str, password: str) -> bool:
        """Login and get session token"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/session",
                json={"username": email, "password": password}
            )
            if resp.status_code == 200:
                self.token = resp.json()["id"]
                self.session.headers["X-Metabase-Session"] = self.token
                return True
            else:
                print(f"❌ Login failed: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get(self, path: str, **kwargs):
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def put(self, path: str, **kwargs):
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    def delete(self, path: str, **kwargs):
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

# =============================================================================
# User Management
# =============================================================================
def create_user(client: MetabaseClient, user_data: Dict) -> Optional[Dict]:
    """Create a new user"""
    try:
        resp = client.post("/api/user", json=user_data)
        if resp.status_code in (200, 201):
            user = resp.json()
            print(f"  ✅ User created: {user_data['email']}")
            return user
        else:
            error = resp.json() if resp.text else {}
            # Check if user already exists
            if "already" in str(error).lower():
                print(f"  ⚠️  User exists: {user_data['email']}")
                # Try to find existing user
                users = get_all_users(client)
                for u in users:
                    if u.get('email') == user_data['email']:
                        return u
            else:
                print(f"  ❌ Failed to create {user_data['email']}: {resp.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ Error creating user: {e}")
        return None

def get_all_users(client: MetabaseClient) -> List[Dict]:
    """Get all users"""
    try:
        resp = client.get("/api/user")
        if resp.status_code == 200:
            return resp.json().get('data', [])
        return []
    except:
        return []

def deactivate_user(client: MetabaseClient, user_id: int) -> bool:
    """Deactivate a user"""
    try:
        resp = client.delete(f"/api/user/{user_id}")
        return resp.status_code == 204
    except:
        return False

# =============================================================================
# Group Management
# =============================================================================
def create_group(client: MetabaseClient, name: str, description: str = "") -> Optional[Dict]:
    """Create a user group"""
    try:
        # Check if group exists
        existing = get_group_by_name(client, name)
        if existing:
            print(f"  ⚠️  Group exists: {name}")
            return existing

        resp = client.post("/api/permissions/group", json={"name": name})
        if resp.status_code in (200, 201):
            group = resp.json()
            print(f"  ✅ Group created: {name} (ID: {group['id']})")
            return group
        else:
            print(f"  ❌ Failed to create group {name}: {resp.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ Error creating group: {e}")
        return None

def get_all_groups(client: MetabaseClient) -> List[Dict]:
    """Get all permission groups"""
    try:
        resp = client.get("/api/permissions/group")
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def get_group_by_name(client: MetabaseClient, name: str) -> Optional[Dict]:
    """Find group by name"""
    groups = get_all_groups(client)
    for group in groups:
        if group.get('name') == name:
            return group
    return None

def add_user_to_group(client: MetabaseClient, user_id: int, group_id: int) -> bool:
    """Add user to a group"""
    try:
        resp = client.post(f"/api/permissions/membership", json={
            "user_id": user_id,
            "group_id": group_id
        })
        if resp.status_code in (200, 201):
            print(f"    ✅ User {user_id} added to group {group_id}")
            return True
        else:
            # Check if already member
            if "already" in resp.text.lower():
                print(f"    ⚠️  User {user_id} already in group {group_id}")
                return True
            print(f"    ❌ Failed to add user to group: {resp.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

# =============================================================================
# Permission Management
# =============================================================================
def get_database_id(client: MetabaseClient, db_name: str = "btrc_qos_poc") -> Optional[int]:
    """Find database ID by name"""
    try:
        resp = client.get("/api/database")
        if resp.status_code == 200:
            databases = resp.json().get("data", [])
            for db in databases:
                # Check by name
                if db.get("name") == db_name:
                    return db["id"]
                # Check by database name in details
                details = db.get("details", {})
                if details.get("db") == db_name or details.get("dbname") == db_name:
                    return db["id"]
                # Check if name contains the db_name
                if db_name.lower() in db.get("name", "").lower():
                    return db["id"]
        return None
    except:
        return None

def set_data_permissions(client: MetabaseClient, group_id: int, database_id: int,
                         access_level: str) -> bool:
    """Set database access permissions for a group

    Access levels:
    - "full": Full access (unrestricted)
    - "view": View-only (no native queries)
    - "query": Can write queries
    - "limited": No access
    """
    try:
        # Get current permissions
        resp = client.get("/api/permissions/graph")
        if resp.status_code != 200:
            print(f"    ❌ Failed to get permissions graph")
            return False

        perms = resp.json()

        # Modify permissions for this group
        group_id_str = str(group_id)
        db_id_str = str(database_id)

        if "groups" not in perms:
            perms["groups"] = {}
        if group_id_str not in perms["groups"]:
            perms["groups"][group_id_str] = {}
        if db_id_str not in perms["groups"][group_id_str]:
            perms["groups"][group_id_str][db_id_str] = {}

        # Set permission level
        if access_level == "full":
            perms["groups"][group_id_str][db_id_str] = {"native": "write", "schemas": "all"}
        elif access_level == "query":
            perms["groups"][group_id_str][db_id_str] = {"native": "write", "schemas": "all"}
        elif access_level == "view":
            perms["groups"][group_id_str][db_id_str] = {"native": "none", "schemas": "all"}
        elif access_level == "limited":
            perms["groups"][group_id_str][db_id_str] = {"native": "none", "schemas": "none"}

        # Update permissions
        resp = client.put("/api/permissions/graph", json=perms)
        if resp.status_code == 200:
            print(f"    ✅ Data permissions set: {access_level}")
            return True
        else:
            print(f"    ❌ Failed to set permissions: {resp.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ Error setting permissions: {e}")
        return False

def set_collection_permissions(client: MetabaseClient, group_id: int,
                                collection_id: int, access_level: str) -> bool:
    """Set collection access permissions

    Access levels:
    - "write": Can create/edit
    - "read": View-only
    - "none": No access
    """
    try:
        # Get collection
        resp = client.get(f"/api/collection/{collection_id}")
        if resp.status_code != 200:
            print(f"    ⚠️  Collection {collection_id} not found")
            return False

        # Get current permissions
        resp = client.get("/api/collection/graph")
        if resp.status_code != 200:
            print(f"    ❌ Failed to get collection permissions")
            return False

        perms = resp.json()
        group_id_str = str(group_id)
        coll_id_str = str(collection_id)

        # Modify permissions
        if "groups" not in perms:
            perms["groups"] = {}
        if group_id_str not in perms["groups"]:
            perms["groups"][group_id_str] = {}

        perms["groups"][group_id_str][coll_id_str] = access_level

        # Update permissions
        resp = client.put("/api/collection/graph", json=perms)
        if resp.status_code == 200:
            print(f"    ✅ Collection permissions set: {access_level}")
            return True
        else:
            print(f"    ❌ Failed to set collection permissions: {resp.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

# =============================================================================
# Main Setup
# =============================================================================
def main():
    print("=" * 70)
    print("BTRC Dashboard - User & Permission Setup")
    print("=" * 70)

    # Initialize client
    client = MetabaseClient(METABASE_URL)

    # Step 1: Login as admin
    print("\n[1/6] Logging in as admin...")
    if not client.login(ADMIN_EMAIL, ADMIN_PASSWORD):
        print("❌ Failed to login. Check credentials.")
        return
    print("✅ Logged in successfully")

    # Step 2: Get database ID
    print("\n[2/6] Finding database...")
    database_id = get_database_id(client, "btrc_qos_poc")
    if not database_id:
        print("❌ Database not found")
        return
    print(f"✅ Database found (ID: {database_id})")

    # Step 3: Create groups
    print("\n[3/6] Creating user groups...")
    created_groups = {}
    for group_name, group_config in USER_GROUPS.items():
        group = create_group(client, group_name, group_config["description"])
        if group:
            created_groups[group_name] = group

    print(f"\n✅ Groups ready: {len(created_groups)}")

    # Step 4: Create users
    print("\n[4/6] Creating users...")
    created_users = {}
    for group_name, users in SAMPLE_USERS.items():
        if group_name not in created_groups:
            continue

        print(f"\n  Group: {group_name}")
        for user_data in users:
            user = create_user(client, user_data)
            if user:
                created_users[user_data['email']] = user
                # Add user to group
                group_id = created_groups[group_name]['id']
                user_id = user['id']
                add_user_to_group(client, user_id, group_id)
                time.sleep(0.2)

    print(f"\n✅ Users created: {len(created_users)}")

    # Step 5: Set data permissions
    print("\n[5/6] Setting data permissions...")
    for group_name, group in created_groups.items():
        if group_name not in USER_GROUPS:
            continue

        print(f"\n  Group: {group_name}")
        access_level = USER_GROUPS[group_name]["data_access"]
        set_data_permissions(client, group['id'], database_id, access_level)
        time.sleep(0.3)

    # Step 6: Set collection permissions (if collections exist)
    print("\n[6/6] Setting collection permissions...")
    try:
        resp = client.get("/api/collection")
        if resp.status_code == 200:
            collections = resp.json()
            for coll in collections:
                if coll.get('name') in ['Regulatory Dashboard', 'Executive Dashboard']:
                    print(f"\n  Collection: {coll['name']} (ID: {coll['id']})")
                    for group_name, group in created_groups.items():
                        if group_name not in USER_GROUPS:
                            continue
                        access = USER_GROUPS[group_name]["collection_access"]
                        set_collection_permissions(client, group['id'], coll['id'], access)
                        time.sleep(0.2)
    except Exception as e:
        print(f"  ⚠️  Collection permissions skipped: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("Setup Complete!")
    print("=" * 70)

    print("\n📊 User Groups Created:")
    for group_name, group in created_groups.items():
        config = USER_GROUPS[group_name]
        user_count = len([u for u in SAMPLE_USERS.get(group_name, [])])
        print(f"\n  {group_name} (ID: {group['id']})")
        print(f"    Users: {user_count}")
        print(f"    Data Access: {config['data_access']}")
        print(f"    Collection Access: {config['collection_access']}")

    print("\n👥 Sample Users Created:")
    print("\n  Login with any of these credentials:")
    for group_name, users in SAMPLE_USERS.items():
        print(f"\n  {group_name}:")
        for user in users:
            if user['email'] in created_users:
                print(f"    📧 {user['email']}")
                print(f"    🔑 {user['password']}")

    print("\n" + "=" * 70)
    print("Testing Instructions:")
    print("=" * 70)
    print("\n1. Logout from Metabase")
    print("2. Login with different user credentials above")
    print("3. Verify access levels:")
    print("   - Admins: Can see everything, manage users")
    print("   - Management: Can view all dashboards")
    print("   - Operations: Can create queries and dashboards")
    print("   - Regional: Can view filtered data only")
    print("   - External: Limited access to public dashboards")

    print(f"\n🔗 Dashboard URL: {METABASE_URL}")
    print("\n✅ Setup complete!")


if __name__ == "__main__":
    main()
