#!/usr/bin/env python3
"""
Enable Public Sharing for BTRC Dashboards
Generates public links that anyone can access without login
"""

import requests
import json

METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"

def login():
    print("Logging in to Metabase...")
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    if response.status_code == 200:
        print("✅ Login successful\n")
        return {"X-Metabase-Session": response.json()["id"]}
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def enable_public_sharing(headers, dashboard_id, dashboard_name):
    print(f"Enabling public sharing for {dashboard_name}...")

    # Enable public sharing
    response = requests.post(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}/public_link",
        headers=headers
    )

    if response.status_code == 200:
        public_data = response.json()
        public_uuid = public_data.get("uuid")
        public_url = f"{METABASE_URL}/public/dashboard/{public_uuid}"

        print(f"✅ Public sharing enabled!")
        print(f"   UUID: {public_uuid}")
        print(f"   URL:  {public_url}\n")
        return public_url
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.text}\n")
        return None

def main():
    print("=" * 70)
    print("Enable Public Sharing for BTRC Dashboards")
    print("=" * 70)
    print()

    headers = login()
    if not headers:
        print("❌ Failed to login. Please check credentials.")
        return

    # Dashboard IDs
    dashboards = [
        (5, "Executive Dashboard"),
        (6, "Regulatory Dashboard")
    ]

    public_links = {}

    for dashboard_id, dashboard_name in dashboards:
        url = enable_public_sharing(headers, dashboard_id, dashboard_name)
        if url:
            public_links[dashboard_name] = url

    print("=" * 70)
    print("Public Links Summary")
    print("=" * 70)
    print()

    if public_links:
        print("✅ Share these links with your team:\n")
        for name, url in public_links.items():
            print(f"📊 {name}")
            print(f"   {url}\n")

        print("=" * 70)
        print("Important Notes:")
        print("=" * 70)
        print()
        print("✅ No login required - Anyone with link can view")
        print("✅ Read-only access - Users cannot edit")
        print("✅ Auto-updates - Data refreshes automatically")
        print("✅ Filters work - Users can filter by Division/District/ISP")
        print()
        print("⚠️  Security Notes:")
        print("   - Links are public - Anyone with URL can access")
        print("   - To revoke access, disable public sharing in Metabase")
        print("   - For external sharing, use reverse proxy with HTTPS")
        print()
        print("🔒 To make these accessible from outside:")
        print("   1. Set up reverse proxy (nginx/caddy)")
        print("   2. Use domain name (e.g., dashboard.btrc.gov.bd)")
        print("   3. Enable HTTPS with SSL certificate")
        print("   4. Configure firewall rules")
        print()
    else:
        print("❌ No public links were created. Check errors above.")

if __name__ == "__main__":
    main()
