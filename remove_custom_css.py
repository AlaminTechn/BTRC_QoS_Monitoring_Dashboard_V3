#!/usr/bin/env python3
"""
Remove Custom CSS from All Dashboard Cards
Cleans up visualization_settings to remove any custom styling
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

def get_dashboard_cards(headers, dashboard_id):
    """Get all cards on a dashboard"""
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}",
        headers=headers
    )

    if response.status_code == 200:
        dashboard = response.json()
        return dashboard.get("dashcards", [])
    else:
        print(f"❌ Failed to get dashboard: {response.status_code}")
        return []

def clean_card_settings(headers, card_id, card_name):
    """Remove custom CSS and styling from a card"""
    print(f"Cleaning {card_name} (Card {card_id})...")

    # Get current card
    response = requests.get(
        f"{METABASE_URL}/api/card/{card_id}",
        headers=headers
    )

    if response.status_code != 200:
        print(f"  ⚠️  Could not retrieve card")
        return False

    card = response.json()
    viz_settings = card.get("visualization_settings", {})

    # Check if there's custom styling
    has_custom = any(key in viz_settings for key in [
        "graph.colors",
        "card.description",
        "text.align_vertical",
        "text.align_horizontal",
        "scalar.font_size",
        "scalar.compact_primary_value"
    ])

    if not has_custom and not viz_settings:
        print(f"  ✓ No custom styling found")
        return True

    # Keep only essential settings, remove styling
    clean_settings = {}

    # Keep display type
    if "scalar.field" in viz_settings:
        clean_settings["scalar.field"] = viz_settings["scalar.field"]

    # Keep card title if it exists
    if "card.title" in viz_settings and viz_settings["card.title"]:
        clean_settings["card.title"] = viz_settings["card.title"]

    # Update card with clean settings
    update_response = requests.put(
        f"{METABASE_URL}/api/card/{card_id}",
        headers=headers,
        json={"visualization_settings": clean_settings}
    )

    if update_response.status_code == 200:
        print(f"  ✅ Cleaned successfully")
        return True
    else:
        print(f"  ❌ Failed to update: {update_response.status_code}")
        return False

def main():
    print("=" * 70)
    print("Remove Custom CSS from Dashboard Cards")
    print("=" * 70)
    print()

    headers = login()
    if not headers:
        print("❌ Failed to login.")
        return

    # Check both dashboards
    dashboards = [
        (5, "Executive Dashboard"),
        (6, "Regulatory Dashboard")
    ]

    total_cleaned = 0

    for dashboard_id, dashboard_name in dashboards:
        print(f"\n{'=' * 70}")
        print(f"Checking {dashboard_name} (ID: {dashboard_id})")
        print(f"{'=' * 70}\n")

        dashcards = get_dashboard_cards(headers, dashboard_id)
        print(f"Found {len(dashcards)} cards on dashboard\n")

        for dashcard in dashcards:
            card_id = dashcard.get("card_id")
            if not card_id:
                continue

            # Get card details
            card_response = requests.get(
                f"{METABASE_URL}/api/card/{card_id}",
                headers=headers
            )

            if card_response.status_code == 200:
                card = card_response.json()
                card_name = card.get("name", f"Card {card_id}")

                if clean_card_settings(headers, card_id, card_name):
                    total_cleaned += 1

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"\n✅ Cleaned {total_cleaned} cards")

    print("\n📝 Additional cleanup:")
    print("1. Go to Admin Settings → Appearance")
    print("2. Clear any CSS in 'Custom Styling' field")
    print("3. Click 'Save changes'")
    print("4. Refresh dashboards (Ctrl+Shift+R)")

    print(f"\n🔗 Check dashboards:")
    print(f"   Executive: {METABASE_URL}/dashboard/5")
    print(f"   Regulatory: {METABASE_URL}/dashboard/6")

if __name__ == "__main__":
    main()
