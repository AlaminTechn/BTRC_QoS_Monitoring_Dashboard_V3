#!/usr/bin/env python3
"""
Add R1 cards using direct dashcard creation
"""

import requests
import json
import sys
import time

METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6
R1_TAB_ID = 13

CARDS = [
    {'card_id': 97, 'name': 'R1.4 Package Compliance Matrix', 'row': 4, 'col': 0, 'size_x': 8, 'size_y': 4},
    {'card_id': 98, 'name': 'R1.5 Real-Time Threshold Alerts', 'row': 4, 'col': 8, 'size_x': 8, 'size_y': 4},
    {'card_id': 99, 'name': 'R1.6 PoP-Level Incident Table', 'row': 8, 'col': 0, 'size_x': 16, 'size_y': 4},
]

def login():
    print("Logging in...")
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    print("✅ Login successful\n")
    return {"X-Metabase-Session": response.json()["id"]}

def check_if_exists(headers):
    """Check if cards already exist"""
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers
    )
    dashboard = response.json()
    existing_card_ids = [dc.get('card_id') for dc in dashboard.get('dashcards', [])]

    cards_to_add = []
    for card in CARDS:
        if card['card_id'] in existing_card_ids:
            print(f"⚠️  Card {card['card_id']} ({card['name']}) already exists")
        else:
            cards_to_add.append(card)

    return cards_to_add

def add_single_card(headers, card_info):
    """Add a single card using POST endpoint"""
    print(f"Adding {card_info['name']}...")

    # Try the dashcard endpoint
    payload = {
        "cardId": card_info['card_id'],
        "dashboard_tab_id": R1_TAB_ID,
        "row": card_info['row'],
        "col": card_info['col'],
        "size_x": card_info['size_x'],
        "size_y": card_info['size_y'],
        "parameter_mappings": [],
        "visualization_settings": {}
    }

    response = requests.post(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}/dashcard",
        headers=headers,
        json=payload
    )

    if response.status_code in [200, 201]:
        print(f"  ✅ Added successfully")
        return True
    else:
        print(f"  ❌ Failed: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return False

def main():
    print("=" * 70)
    print("Add R1 Removed Charts")
    print("=" * 70)
    print()

    headers = login()
    cards_to_add = check_if_exists(headers)

    if not cards_to_add:
        print("\n✅ All cards already exist!")
        return

    print(f"\nAdding {len(cards_to_add)} cards...\n")

    success_count = 0
    for card in cards_to_add:
        if add_single_card(headers, card):
            success_count += 1
        time.sleep(0.5)  # Small delay between requests

    print("\n" + "=" * 70)
    print(f"✅ Added {success_count}/{len(cards_to_add)} cards successfully!")
    print("=" * 70)
    print(f"\nView dashboard at: {METABASE_URL}/dashboard/{REGULATORY_DASHBOARD_ID}")

if __name__ == "__main__":
    main()
