#!/usr/bin/env python3
"""
Fix Scalar Card Display Issues
- Reduce font size
- Ensure proper text wrapping
- Fix percentage display
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

def fix_scalar_card(headers, card_id, card_name):
    print(f"Fixing {card_name} (Card {card_id})...")

    # Get current card settings
    response = requests.get(
        f"{METABASE_URL}/api/card/{card_id}",
        headers=headers
    )

    if response.status_code != 200:
        print(f"❌ Failed to get card: {response.status_code}")
        return False

    card = response.json()

    # Update visualization settings for better display
    viz_settings = card.get("visualization_settings", {})

    # Better scalar display settings
    viz_settings.update({
        "scalar.style": "decimal",
        "scalar.field": "result",
        "scalar.switch_positive_negative": False,

        # Text formatting
        "text.align_vertical": "middle",
        "text.align_horizontal": "center",

        # Font sizing
        "scalar.font_size": "medium",  # Use medium instead of large

        # Card styling
        "card.title": card.get("name", "").upper(),
        "card.description": card.get("description", ""),

        # Make text wrap properly
        "scalar.compact_primary_value": False,

        # Colors based on card
        "graph.colors": [
            "#10b981" if "76" in str(card_id) else  # Green for Compliant
            "#f59e0b" if "77" in str(card_id) else  # Orange for At Risk
            "#ef4444"  # Red for Violation
        ]
    })

    # Update card
    update_response = requests.put(
        f"{METABASE_URL}/api/card/{card_id}",
        headers=headers,
        json={"visualization_settings": viz_settings}
    )

    if update_response.status_code == 200:
        print(f"✅ {card_name} updated successfully!")
        return True
    else:
        print(f"❌ Failed to update: {update_response.status_code}")
        print(f"   {update_response.text[:200]}")
        return False

def main():
    print("=" * 70)
    print("Fix Scalar Card Display Issues")
    print("=" * 70)
    print()

    headers = login()
    if not headers:
        print("❌ Failed to login.")
        return

    # Fix all three scalar cards
    cards = [
        (76, "R1.1 Compliant ISPs"),
        (77, "R1.2 At Risk ISPs"),
        (78, "R1.3 Violation ISPs")
    ]

    results = []
    for card_id, card_name in cards:
        result = fix_scalar_card(headers, card_id, card_name)
        results.append(result)
        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    success_count = sum(results)
    print(f"\n✅ {success_count}/3 cards updated successfully")

    print("\n📝 Additional Steps:")
    print("1. Clear browser cache (Ctrl+Shift+Delete)")
    print("2. Hard refresh dashboard (Ctrl+Shift+R)")
    print("3. If still too large, apply CSS from fix_scalar_cards_css.css")
    print("4. Admin Settings → Appearance → Custom Styling")

    print(f"\n🔗 View dashboard: {METABASE_URL}/dashboard/6")

if __name__ == "__main__":
    main()
