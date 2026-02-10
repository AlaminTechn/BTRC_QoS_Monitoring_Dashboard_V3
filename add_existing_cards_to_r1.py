#!/usr/bin/env python3
"""
Add existing questions (97, 98, 99) to Regulatory Dashboard Tab R1
"""

import requests
import json
import sys

# Configuration
METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6
R1_TAB_ID = 13

# Questions already created
CARDS = [
    {'card_id': 97, 'name': 'R1.4 Package Compliance Matrix', 'row': 4, 'col': 0, 'size_x': 8, 'size_y': 4},
    {'card_id': 98, 'name': 'R1.5 Real-Time Threshold Alerts', 'row': 4, 'col': 8, 'size_x': 8, 'size_y': 4},
    {'card_id': 99, 'name': 'R1.6 PoP-Level Incident Table', 'row': 8, 'col': 0, 'size_x': 16, 'size_y': 4},
]

def login():
    """Login to Metabase and get session token"""
    print("Logging in to Metabase...")
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

    token = response.json()["id"]
    print(f"✅ Login successful\n")
    return {"X-Metabase-Session": token}

def add_cards_to_dashboard(headers):
    """Add cards to dashboard using PUT endpoint"""
    print(f"Fetching dashboard {REGULATORY_DASHBOARD_ID}...")

    # Get current dashboard structure
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers
    )

    if response.status_code != 200:
        print(f"❌ Failed to fetch dashboard: {response.text}")
        return False

    dashboard = response.json()
    current_dashcards = dashboard.get('dashcards', [])
    print(f"✅ Current dashboard has {len(current_dashcards)} cards\n")

    # Check if cards already exist
    existing_card_ids = [dc.get('card_id') for dc in current_dashcards]
    cards_to_add = []

    for card in CARDS:
        if card['card_id'] in existing_card_ids:
            print(f"⚠️  Card {card['card_id']} ({card['name']}) already exists, skipping")
        else:
            cards_to_add.append(card)

    if not cards_to_add:
        print("\n✅ All cards already exist on dashboard!")
        return True

    print(f"\nAdding {len(cards_to_add)} new cards to dashboard...")

    # Find the lowest ID to create negative IDs for new cards
    existing_ids = [dc.get('id', 0) for dc in current_dashcards]
    next_negative_id = min([id for id in existing_ids if id < 0], default=-1) - 1

    # Create new dashcards
    new_dashcards = []
    for card_info in cards_to_add:
        print(f"  - Adding {card_info['name']} (Card ID: {card_info['card_id']})")
        dashcard = {
            "id": next_negative_id,
            "card_id": card_info['card_id'],
            "dashboard_tab_id": R1_TAB_ID,
            "row": card_info['row'],
            "col": card_info['col'],
            "size_x": card_info['size_x'],
            "size_y": card_info['size_y'],
            "parameter_mappings": [],
            "visualization_settings": {}
        }
        new_dashcards.append(dashcard)
        next_negative_id -= 1

    # Combine existing and new dashcards
    all_dashcards = current_dashcards + new_dashcards

    # Update dashboard
    update_data = {
        "dashcards": all_dashcards
    }

    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers,
        json=update_data
    )

    if response.status_code not in [200, 202]:
        print(f"\n❌ Failed to update dashboard: {response.text}")
        return False

    print(f"\n✅ Successfully added {len(cards_to_add)} cards to dashboard!")
    return True

def main():
    print("=" * 70)
    print("Add Existing Questions to Regulatory Dashboard Tab R1")
    print("=" * 70)
    print()

    headers = login()
    success = add_cards_to_dashboard(headers)

    if success:
        print("\n" + "=" * 70)
        print("✅ Dashboard updated successfully!")
        print("=" * 70)
        print(f"\nView dashboard at: {METABASE_URL}/dashboard/{REGULATORY_DASHBOARD_ID}")
        print("\nCards added:")
        for card in CARDS:
            print(f"  - {card['name']} (Question ID: {card['card_id']})")
    else:
        print("\n❌ Failed to update dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
