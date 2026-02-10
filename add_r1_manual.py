#!/usr/bin/env python3
"""
Manually add R1 cards by reconstructing complete dashcards array
"""

import requests
import json
import sys

METABASE_URL = "http://localhost:3000"
METABASE_EMAIL = "alamin.technometrics22@gmail.com"
METABASE_PASSWORD = "Test@123"
REGULATORY_DASHBOARD_ID = 6

def login():
    print("Logging in...")
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD}
    )
    print("✅ Login successful\n")
    return {"X-Metabase-Session": response.json()["id"]}

def add_cards(headers):
    print("Fetching dashboard...")
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers
    )
    dashboard = response.json()

    # Get existing dashcards
    existing_dashcards = dashboard.get('dashcards', [])
    existing_card_ids = [dc.get('card_id') for dc in existing_dashcards]

    print(f"Current dashcards: {len(existing_dashcards)}")
    print(f"Existing card IDs: {existing_card_ids}\n")

    # Check if our cards already exist
    our_cards = [97, 98, 99]
    cards_to_add = [c for c in our_cards if c not in existing_card_ids]

    if not cards_to_add:
        print("✅ All cards already exist!")
        return True

    print(f"Cards to add: {cards_to_add}\n")

    # Create minimal dashcard entries
    new_dashcards = []

    # Find next negative ID
    existing_ids = [dc.get('id', 0) for dc in existing_dashcards]
    next_id = min([i for i in existing_ids if i < 0], default=-1) - 1

    # R1.4 - Package Compliance Matrix
    if 97 in cards_to_add:
        new_dashcards.append({
            "size_x": 8,
            "size_y": 4,
            "row": 4,
            "col": 0,
            "id": next_id,
            "card_id": 97,
            "dashboard_tab_id": 13,
            "parameter_mappings": [],
            "visualization_settings": {}
        })
        print(f"Adding R1.4 (Card 97) with ID {next_id}")
        next_id -= 1

    # R1.5 - Real-Time Threshold Alerts
    if 98 in cards_to_add:
        new_dashcards.append({
            "size_x": 8,
            "size_y": 4,
            "row": 4,
            "col": 8,
            "id": next_id,
            "card_id": 98,
            "dashboard_tab_id": 13,
            "parameter_mappings": [],
            "visualization_settings": {}
        })
        print(f"Adding R1.5 (Card 98) with ID {next_id}")
        next_id -= 1

    # R1.6 - PoP-Level Incident Table
    if 99 in cards_to_add:
        new_dashcards.append({
            "size_x": 16,
            "size_y": 4,
            "row": 8,
            "col": 0,
            "id": next_id,
            "card_id": 99,
            "dashboard_tab_id": 13,
            "parameter_mappings": [],
            "visualization_settings": {}
        })
        print(f"Adding R1.6 (Card 99) with ID {next_id}")

    # Copy existing dashcards but ensure proper format
    clean_existing = []
    for dc in existing_dashcards:
        # Keep only essential fields
        clean_dc = {
            "id": dc.get('id'),
            "card_id": dc.get('card_id'),
            "dashboard_tab_id": dc.get('dashboard_tab_id'),
            "row": dc.get('row', 0),
            "col": dc.get('col', 0),
            "size_x": dc.get('size_x', dc.get('sizeX', 4)),
            "size_y": dc.get('size_y', dc.get('sizeY', 4)),
            "parameter_mappings": dc.get('parameter_mappings', []),
            "visualization_settings": dc.get('visualization_settings', {})
        }
        clean_existing.append(clean_dc)

    # Combine
    all_dashcards = clean_existing + new_dashcards

    print(f"\nTotal dashcards after add: {len(all_dashcards)}")
    print("Updating dashboard...")

    # Update using PUT
    update_data = {
        "dashcards": all_dashcards
    }

    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{REGULATORY_DASHBOARD_ID}",
        headers=headers,
        json=update_data
    )

    if response.status_code in [200, 202]:
        print(f"\n✅ Successfully added {len(new_dashcards)} cards!")
        return True
    else:
        print(f"\n❌ Failed: {response.status_code}")
        error_text = response.text
        # Extract just the key error message
        if "foreign key constraint" in error_text:
            print("Error: Foreign key constraint violation")
            if "dashboard_tab_id" in error_text:
                print("Issue with dashboard_tab_id")
        else:
            print(f"Error: {error_text[:300]}")
        return False

def main():
    print("=" * 70)
    print("Add R1 Cards - Manual Approach")
    print("=" * 70)
    print()

    headers = login()
    success = add_cards(headers)

    if success:
        print("\n" + "=" * 70)
        print("✅ Dashboard updated!")
        print("=" * 70)
        print(f"\nView: {METABASE_URL}/dashboard/{REGULATORY_DASHBOARD_ID}")
    else:
        print("\n❌ Update failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
