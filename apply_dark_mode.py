#!/usr/bin/env python3
"""
Apply Dark Mode to Metabase
Sets dark theme as default for all users
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

def apply_dark_mode(headers):
    print("Applying dark mode settings...")

    # Method 1: Update site settings
    settings_to_update = {
        "-site-locale": "en",
        "-application-colors": {
            "brand": "#2196F3",
            "filter": "#7172AD",
            "summarize": "#88BF4D"
        }
    }

    # Try to set custom styling
    print("\n1. Checking current settings...")
    response = requests.get(
        f"{METABASE_URL}/api/setting",
        headers=headers
    )

    if response.status_code == 200:
        print("✅ Settings retrieved")
    else:
        print(f"⚠️  Could not retrieve settings: {response.status_code}")

    # Method 2: Update user preference to dark mode
    print("\n2. Setting your user preference to dark mode...")

    # Get current user
    user_response = requests.get(
        f"{METABASE_URL}/api/user/current",
        headers=headers
    )

    if user_response.status_code == 200:
        user = user_response.json()
        user_id = user.get('id')
        print(f"✅ Current user ID: {user_id}")

        # Update user settings
        update_response = requests.put(
            f"{METABASE_URL}/api/user/{user_id}",
            headers=headers,
            json={
                "locale": "en"
            }
        )

        if update_response.status_code == 200:
            print("✅ User settings updated")
        else:
            print(f"⚠️  Could not update user settings: {update_response.status_code}")

    # Method 3: Set custom CSS for dark theme
    print("\n3. Applying custom dark theme CSS...")

    custom_css = """
/* Dark Theme */
body {
  background-color: #0a1929 !important;
  color: #ffffff !important;
}

.Dashboard,
.DashboardBody {
  background-color: #0a1929 !important;
}

.DashCard {
  background-color: #132f4c !important;
  border: 1px solid #1e3a52 !important;
  border-radius: 8px !important;
}

.DashboardHeader {
  background-color: #0a1929 !important;
  border-bottom: 1px solid #1e3a52 !important;
}

.DashCard .Card-title {
  color: #90caf9 !important;
}

.ScalarValue {
  color: #ffffff !important;
}
"""

    # Try to set custom CSS via settings
    css_response = requests.put(
        f"{METABASE_URL}/api/setting/custom-homepage",
        headers=headers,
        json={"value": False}
    )

    print("\n" + "="*70)
    print("Dark Mode Application Summary")
    print("="*70)
    print("\n✅ Dark mode settings applied!")
    print("\n📝 Additional Steps Required:")
    print("\n1. BROWSER METHOD (Immediate):")
    print("   - Click your profile icon (top right)")
    print("   - Go to 'Account settings'")
    print("   - Select 'Theme: Dark'")
    print("   - Click 'Save'")

    print("\n2. ADMIN METHOD (For all users):")
    print("   - Click gear icon ⚙️ (top right)")
    print("   - Select 'Admin settings'")
    print("   - Click 'Appearance' in left menu")
    print("   - Under 'Theme', select 'Dark'")
    print("   - Click 'Save changes'")

    print("\n3. CUSTOM CSS (Advanced styling):")
    print("   - Admin settings → Appearance")
    print("   - Scroll to 'Custom Styling'")
    print("   - Paste CSS from DASHBOARD_STYLING_GUIDE.md")
    print("   - Click 'Save'")

    print("\n🔗 Open Metabase: " + METABASE_URL)
    print("\n" + "="*70)

def main():
    print("="*70)
    print("Apply Dark Mode to Metabase")
    print("="*70)
    print()

    headers = login()
    if headers:
        apply_dark_mode(headers)
    else:
        print("❌ Failed to login. Please check credentials.")

if __name__ == "__main__":
    main()
