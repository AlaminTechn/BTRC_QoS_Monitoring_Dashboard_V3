#!/usr/bin/env python3
"""
Configure Metabase Native Drill-Through for BTRC Dashboard
Implements hierarchical navigation: Division → District → ISP
"""

import requests
import json

# Metabase configuration
METABASE_URL = "http://localhost:3000"
USERNAME = "alamin.technometrics22@gmail.com"
PASSWORD = "Test@123"

def get_session():
    """Get Metabase session token"""
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": USERNAME, "password": PASSWORD}
    )
    response.raise_for_status()
    return response.json()['id']

def update_question_click_behavior(session_token, question_id, click_behavior_config):
    """Update question with click behavior configuration"""

    # First, get the current question
    response = requests.get(
        f"{METABASE_URL}/api/card/{question_id}",
        headers={"X-Metabase-Session": session_token}
    )
    response.raise_for_status()
    question = response.json()

    # Update visualization_settings with click_behavior
    if 'visualization_settings' not in question:
        question['visualization_settings'] = {}

    # Merge click behavior config
    question['visualization_settings'].update(click_behavior_config)

    # Update the question
    response = requests.put(
        f"{METABASE_URL}/api/card/{question_id}",
        headers={"X-Metabase-Session": session_token},
        json=question
    )
    response.raise_for_status()

    return response.json()

def configure_division_table_drillthrough(session_token):
    """
    Configure Question 79: Division Performance Summary Table
    Click Division name → Filters dashboard by division
    """
    print("\n" + "="*60)
    print("Configuring Q79: Division Performance Summary Table")
    print("="*60)

    click_behavior_config = {
        "column_settings": {
            '["name","Division"]': {
                "click_behavior": {
                    "type": "link",
                    "linkType": "dashboard",
                    "targetId": 6,  # Dashboard ID
                    "parameterMapping": {
                        "29ce015d-049e-4239-aab6-1c2a64c015ba": {  # Division parameter ID
                            "source": {
                                "type": "column",
                                "id": "Division",
                                "name": "Division"
                            },
                            "target": {
                                "type": "parameter",
                                "id": "29ce015d-049e-4239-aab6-1c2a64c015ba"
                            },
                            "id": "29ce015d-049e-4239-aab6-1c2a64c015ba"
                        }
                    },
                    "linkTextTemplate": "View {{Division}} Districts"
                }
            }
        }
    }

    try:
        result = update_question_click_behavior(session_token, 79, click_behavior_config)
        print("✅ Division Table drill-through configured!")
        print(f"   Click 'Division' column → Filters to that division")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def configure_division_map_drillthrough(session_token):
    """
    Configure Question 94: Division Performance Map
    Click map region → Filters dashboard by division
    """
    print("\n" + "="*60)
    print("Configuring Q94: Division Performance Map (Choropleth)")
    print("="*60)

    click_behavior_config = {
        "click_behavior": {
            "type": "link",
            "linkType": "dashboard",
            "targetId": 6,  # Dashboard ID
            "parameterMapping": {
                "29ce015d-049e-4239-aab6-1c2a64c015ba": {  # Division parameter ID
                    "source": {
                        "type": "column",
                        "id": "Division",
                        "name": "Division"
                    },
                    "target": {
                        "type": "parameter",
                        "id": "29ce015d-049e-4239-aab6-1c2a64c015ba"
                    },
                    "id": "29ce015d-049e-4239-aab6-1c2a64c015ba"
                }
            }
        }
    }

    try:
        result = update_question_click_behavior(session_token, 94, click_behavior_config)
        print("✅ Division Map drill-through configured!")
        print(f"   Click map region → Filters to that division")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def configure_district_table_drillthrough(session_token):
    """
    Configure Question 80: District Ranking Table
    Click District name → Filters dashboard by district
    """
    print("\n" + "="*60)
    print("Configuring Q80: District Ranking Table")
    print("="*60)

    click_behavior_config = {
        "column_settings": {
            '["name","District"]': {
                "click_behavior": {
                    "type": "link",
                    "linkType": "dashboard",
                    "targetId": 6,  # Dashboard ID
                    "parameterMapping": {
                        "6a2b8a1e-7c3d-4e5f-9a8b-1c2d3e4f5a6b": {  # District parameter ID
                            "source": {
                                "type": "column",
                                "id": "District",
                                "name": "District"
                            },
                            "target": {
                                "type": "parameter",
                                "id": "6a2b8a1e-7c3d-4e5f-9a8b-1c2d3e4f5a6b"
                            },
                            "id": "6a2b8a1e-7c3d-4e5f-9a8b-1c2d3e4f5a6b"
                        }
                    },
                    "linkTextTemplate": "View {{District}} ISPs"
                }
            }
        }
    }

    try:
        result = update_question_click_behavior(session_token, 80, click_behavior_config)
        print("✅ District Table drill-through configured!")
        print(f"   Click 'District' column → Filters to that district")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def configure_district_map_drillthrough(session_token):
    """
    Configure Question 95: District Performance Map
    Click map region → Filters dashboard by district
    """
    print("\n" + "="*60)
    print("Configuring Q95: District Performance Map")
    print("="*60)

    click_behavior_config = {
        "click_behavior": {
            "type": "link",
            "linkType": "dashboard",
            "targetId": 6,  # Dashboard ID
            "parameterMapping": {
                "6a2b8a1e-7c3d-4e5f-9a8b-1c2d3e4f5a6b": {  # District parameter ID
                    "source": {
                        "type": "column",
                        "id": "District",
                        "name": "District"
                    },
                    "target": {
                        "type": "parameter",
                        "id": "6a2b8a1e-7c3d-4e5f-9a8b-1c2d3e4f5a6b"
                    },
                    "id": "6a2b8a1e-7c3d-4e5f-9a8b-1c2d3e4f5a6b"
                }
            }
        }
    }

    try:
        result = update_question_click_behavior(session_token, 95, click_behavior_config)
        print("✅ District Map drill-through configured!")
        print(f"   Click map region → Filters to that district")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("BTRC Dashboard - Configure Metabase Native Drill-Through")
    print("="*60)

    # Get session token
    print("\n📡 Connecting to Metabase...")
    try:
        session_token = get_session()
        print(f"✅ Session established: {session_token[:20]}...")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # Configure each question
    results = []

    # Division level → District level
    results.append(("Division Table", configure_division_table_drillthrough(session_token)))
    results.append(("Division Map", configure_division_map_drillthrough(session_token)))

    # District level → ISP level
    results.append(("District Table", configure_district_table_drillthrough(session_token)))
    results.append(("District Map", configure_district_map_drillthrough(session_token)))

    # Summary
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {name}")

    print("\n" + "="*60)
    print("TESTING INSTRUCTIONS")
    print("="*60)
    print("1. Open: http://localhost:3000/dashboard/6")
    print("2. Go to Tab R2.2: Regional Analysis")
    print("3. Click on 'Dhaka' in the Division table")
    print("   → Should filter dashboard to show Dhaka's districts")
    print("4. Click on 'Gazipur' in the District table")
    print("   → Should filter dashboard to show Gazipur's ISPs")
    print("5. Click on division/district regions in maps")
    print("   → Should apply corresponding filters")
    print("\n" + "="*60)

    success_count = sum(1 for _, s in results if s)
    print(f"\n✅ {success_count}/{len(results)} configurations successful!")

if __name__ == "__main__":
    main()
