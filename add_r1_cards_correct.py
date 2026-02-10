#!/usr/bin/env python3
"""
Add R1 removed charts with correct tab ID and positioning
"""

import requests
import json
import sys

# Configuration
METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6
R1_TAB_ID = 13  # R2.1: SLA Monitoring

# Questions already created
CARDS = [
    {'card_id': 97, 'name': 'R1.4 Package Compliance Matrix'},
    {'card_id': 98, 'name': 'R1.5 Real-Time Threshold Alerts'},
    {'card_id': 99, 'name': 'R1.6 PoP-Level Incident Table'},
]

def login():
    """Login to Metabase"""
    print("Logging in to Metabase...")
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    print("✅ Login successful\n")
    return {"X-Metabase-Session": response.json()["id"]}

def get_dashboard(headers):
    """Get dashboard structure"""
    print(f"Fetching dashboard {REGULATORY_DASHBOARD_ID}...")
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers
    )
    dashboard = response.json()

    # Check tab 13 cards
    tab13_cards = [dc for dc in dashboard.get('dashcards', []) if dc.get('dashboard_tab_id') == R1_TAB_ID]
    print(f"✅ Tab 13 (R1) currently has {len(tab13_cards)} cards")

    # Find max row
    max_row = 0
    for dc in tab13_cards:
        row_end = dc.get('row', 0) + dc.get('size_y', 0)
        if row_end > max_row:
            max_row = row_end

    print(f"   Max row used: {max_row}")
    print(f"   Will start new cards at row: {max_row}\n")

    return dashboard, max_row

def add_cards(headers, dashboard, start_row):
    """Add new cards to dashboard"""
    current_dashcards = dashboard.get('dashcards', [])

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

    print(f"Adding {len(cards_to_add)} new cards...")

    # Find lowest negative ID
    existing_ids = [dc.get('id', 0) for dc in current_dashcards]
    next_negative_id = min([id for id in existing_ids if id < 0], default=-1) - 1

    # Layout on Tab 13:
    # R1.1, R1.2, R1.3 are in row 0 (3 cards, 6 cols each)
    # New cards:
    # R1.4: row=4, col=0, size_x=8, size_y=4  (left side, 50% width)
    # R1.5: row=4, col=8, size_x=8, size_y=4  (right side, 50% width)
    # R1.6: row=8, col=0, size_x=16, size_y=4 (full width)

    new_dashcards = []

    # R1.4 - Package Compliance Matrix (left, row 4)
    if 97 not in existing_card_ids:
        new_dashcards.append({
            "id": next_negative_id,
            "card_id": 97,
            "dashboard_tab_id": R1_TAB_ID,
            "row": 4,
            "col": 0,
            "size_x": 8,
            "size_y": 4,
            "parameter_mappings": [],
            "visualization_settings": {}
        })
        print(f"  - R1.4 Package Compliance Matrix at row 4, col 0 (8x4)")
        next_negative_id -= 1

    # R1.5 - Real-Time Threshold Alerts (right, row 4)
    if 98 not in existing_card_ids:
        new_dashcards.append({
            "id": next_negative_id,
            "card_id": 98,
            "dashboard_tab_id": R1_TAB_ID,
            "row": 4,
            "col": 8,
            "size_x": 8,
            "size_y": 4,
            "parameter_mappings": [],
            "visualization_settings": {}
        })
        print(f"  - R1.5 Real-Time Threshold Alerts at row 4, col 8 (8x4)")
        next_negative_id -= 1

    # R1.6 - PoP-Level Incident Table (full width, row 8)
    if 99 not in existing_card_ids:
        new_dashcards.append({
            "id": next_negative_id,
            "card_id": 99,
            "dashboard_tab_id": R1_TAB_ID,
            "row": 8,
            "col": 0,
            "size_x": 16,
            "size_y": 4,
            "parameter_mappings": [],
            "visualization_settings": {}
        })
        print(f"  - R1.6 PoP-Level Incident Table at row 8, col 0 (16x4)")

    # Combine all dashcards
    all_dashcards = current_dashcards + new_dashcards

    # Update dashboard
    print(f"\nUpdating dashboard...")
    update_data = {
        "dashcards": all_dashcards
    }

    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers,
        json=update_data
    )

    if response.status_code not in [200, 202]:
        print(f"❌ Failed to update dashboard")
        print(f"Response: {response.text[:500]}")
        return False

    print(f"✅ Successfully added {len(new_dashcards)} cards!")
    return True

def main():
    print("=" * 70)
    print("Add R1 Removed Charts to Regulatory Dashboard")
    print("=" * 70)
    print()

    headers = login()
    dashboard, start_row = get_dashboard(headers)
    success = add_cards(headers, dashboard, start_row)

    if success:
        print("\n" + "=" * 70)
        print("✅ Dashboard updated successfully!")
        print("=" * 70)
        print(f"\nView dashboard at: {METABASE_URL}/dashboard/{REGULATORY_DASHBOARD_ID}")
        print("\nCards added to Tab R1 (SLA Monitoring):")
        print("  - R1.4: Package Compliance Matrix")
        print("  - R1.5: Real-Time Threshold Alerts")
        print("  - R1.6: PoP-Level Incident Table")
    else:
        print("\n❌ Failed to update dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
