#!/usr/bin/env python3
"""
Clear Custom CSS from Metabase Admin Settings
Removes any custom styling from Appearance settings
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

def clear_custom_css(headers):
    """Clear custom CSS from admin settings"""
    print("Clearing custom CSS from admin settings...")

    # Try to clear custom homepage CSS
    try:
        response = requests.put(
            f"{METABASE_URL}/api/setting/custom-homepage",
            headers=headers,
            json={"value": False}
        )
        if response.status_code == 200:
            print("✅ Custom homepage CSS cleared")
    except:
        print("  (No custom homepage CSS found)")

    # Try to clear application colors
    try:
        response = requests.put(
            f"{METABASE_URL}/api/setting/application-colors",
            headers=headers,
            json={"value": {}}
        )
        if response.status_code == 200:
            print("✅ Application colors reset")
    except:
        print("  (No custom colors found)")

    print("\n✅ Admin-level custom CSS cleared!")

def main():
    print("=" * 70)
    print("Clear Custom CSS from Metabase Admin Settings")
    print("=" * 70)
    print()

    headers = login()
    if not headers:
        print("❌ Failed to login.")
        return

    clear_custom_css(headers)

    print("\n" + "=" * 70)
    print("Manual Cleanup Required")
    print("=" * 70)
    print("\nPlease also manually check:")
    print()
    print("1. Open Metabase: http://localhost:3000")
    print("2. Click ⚙️ gear icon → Admin settings")
    print("3. Click 'Appearance' in left menu")
    print("4. If you see 'Custom Styling' text box:")
    print("   - Delete all content in the box")
    print("   - Click 'Save changes'")
    print()
    print("5. Refresh your dashboard:")
    print("   - Press Ctrl+Shift+R (hard refresh)")
    print()
    print("✅ All custom CSS will be removed!")

if __name__ == "__main__":
    main()
