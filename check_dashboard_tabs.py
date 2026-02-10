#!/usr/bin/env python3
"""
Check Regulatory Dashboard tabs
"""

import requests
import json

# Configuration
METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6

def login():
    """Login to Metabase"""
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    return {"X-Metabase-Session": response.json()["id"]}

def main():
    headers = login()

    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers
    )

    dashboard = response.json()

    print(f"Dashboard: {dashboard['name']}")
    print(f"\nTabs:")
    for tab in dashboard.get('tabs', []):
        print(f"  ID: {tab['id']}, Name: {tab['name']}")

    print(f"\nDashcards:")
    for card in dashboard.get('dashcards', [])[:5]:  # Show first 5
        print(f"  Card ID: {card.get('card_id')}, Tab ID: {card.get('dashboard_tab_id')}, Row: {card.get('row')}, Col: {card.get('col')}")

if __name__ == "__main__":
    main()
