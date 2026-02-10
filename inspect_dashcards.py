#!/usr/bin/env python3
import requests
import json

METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6

def login():
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    return {"X-Metabase-Session": response.json()["id"]}

headers = login()
response = requests.get(
    f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
    headers=headers
)
dashboard = response.json()

print("Dashcards with None card_id:")
for dc in dashboard.get('dashcards', []):
    if dc.get('card_id') is None:
        print(f"\nDashcard ID: {dc.get('id')}")
        print(f"  Tab ID: {dc.get('dashboard_tab_id')}")
        print(f"  Row: {dc.get('row')}, Col: {dc.get('col')}")
        print(f"  Size: {dc.get('size_x')}x{dc.get('size_y')}")
        print(f"  Keys: {list(dc.keys())}")
        # Check if it's a heading or text
        if 'visualization_settings' in dc:
            vs = dc['visualization_settings']
            if 'virtual_card' in vs:
                print(f"  Type: Virtual Card (Heading/Text)")
                print(f"  Content: {vs['virtual_card']}")
