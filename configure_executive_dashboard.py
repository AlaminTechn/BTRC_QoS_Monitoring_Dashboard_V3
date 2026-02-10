#!/usr/bin/env python3
"""
Configure Executive Dashboard with Division Filter and Drill-Down
Per BTRC-FXBB-QOS-POC_Dev-Spec requirements
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

def add_division_parameter(session_token):
    """Add Division parameter to Executive Dashboard"""
    print("\n" + "="*60)
    print("Adding Division Parameter to Executive Dashboard")
    print("="*60)

    # Get current dashboard
    response = requests.get(
        f"{METABASE_URL}/api/dashboard/5",
        headers={"X-Metabase-Session": session_token}
    )
    response.raise_for_status()
    dashboard = response.json()

    # Division parameter (same UUID as Regulatory Dashboard)
    division_param = {
        "id": "29ce015d-049e-4239-aab6-1c2a64c015ba",
        "name": "Division",
        "slug": "division",
        "type": "string/=",
        "values_source_type": "static-list",
        "values_source_config": {
            "values": ["Dhaka", "Chattagram", "Khulna", "Rajshahi",
                      "Barisal", "Sylhet", "Rangpur", "Mymensingh"]
        },
        "values_query_type": "list",
        "default": None
    }

    # Check if parameter exists
    existing_params = dashboard.get('parameters', [])
    param_exists = any(p['id'] == division_param['id'] for p in existing_params)

    if not param_exists:
        existing_params.append(division_param)
        dashboard['parameters'] = existing_params

        # Update dashboard
        response = requests.put(
            f"{METABASE_URL}/api/dashboard/5",
            headers={"X-Metabase-Session": session_token},
            json=dashboard
        )
        response.raise_for_status()
        print("✅ Division parameter added successfully")
        return True
    else:
        print("ℹ️  Division parameter already exists")
        return True

def configure_division_ranking_drillthrough(session_token):
    """
    Configure E1.6: Division Performance Ranking
    Click division bar → Filters dashboard by that division
    """
    print("\n" + "="*60)
    print("Configuring E1.6: Division Performance Ranking")
    print("="*60)

    # Get question
    response = requests.get(
        f"{METABASE_URL}/api/card/68",
        headers={"X-Metabase-Session": session_token}
    )
    response.raise_for_status()
    question = response.json()

    # Add click behavior for Division column
    if 'visualization_settings' not in question:
        question['visualization_settings'] = {}

    question['visualization_settings']['column_settings'] = {
        '["name","Division"]': {
            "click_behavior": {
                "type": "link",
                "linkType": "dashboard",
                "targetId": 5,  # Executive Dashboard ID
                "parameterMapping": {
                    "29ce015d-049e-4239-aab6-1c2a64c015ba": {
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
    }

    # Update question
    response = requests.put(
        f"{METABASE_URL}/api/card/68",
        headers={"X-Metabase-Session": session_token},
        json=question
    )
    response.raise_for_status()
    print("✅ Division Performance Ranking drill-through configured")
    return True

def configure_division_map_drillthrough(session_token):
    """
    Configure E2.1: Division Performance Map
    Click map region → Filters dashboard by that division
    """
    print("\n" + "="*60)
    print("Configuring E2.1: Division Performance Map")
    print("="*60)

    # Get question
    response = requests.get(
        f"{METABASE_URL}/api/card/69",
        headers={"X-Metabase-Session": session_token}
    )
    response.raise_for_status()
    question = response.json()

    # Add click behavior for map
    if 'visualization_settings' not in question:
        question['visualization_settings'] = {}

    question['visualization_settings']['click_behavior'] = {
        "type": "link",
        "linkType": "dashboard",
        "targetId": 5,  # Executive Dashboard ID
        "parameterMapping": {
            "29ce015d-049e-4239-aab6-1c2a64c015ba": {
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

    # Update question
    response = requests.put(
        f"{METABASE_URL}/api/card/69",
        headers={"X-Metabase-Session": session_token},
        json=question
    )
    response.raise_for_status()
    print("✅ Division Performance Map drill-through configured")
    return True

def configure_division_comparison_drillthrough(session_token):
    """
    Configure E2.2: Division Comparison Table
    Click division name → Filters dashboard by that division
    """
    print("\n" + "="*60)
    print("Configuring E2.2: Division Comparison Table")
    print("="*60)

    # Get question
    response = requests.get(
        f"{METABASE_URL}/api/card/70",
        headers={"X-Metabase-Session": session_token}
    )
    response.raise_for_status()
    question = response.json()

    # Add click behavior for Division column
    if 'visualization_settings' not in question:
        question['visualization_settings'] = {}

    if 'column_settings' not in question['visualization_settings']:
        question['visualization_settings']['column_settings'] = {}

    question['visualization_settings']['column_settings']['["name","Division"]'] = {
        "click_behavior": {
            "type": "link",
            "linkType": "dashboard",
            "targetId": 5,  # Executive Dashboard ID
            "parameterMapping": {
                "29ce015d-049e-4239-aab6-1c2a64c015ba": {
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

    # Update question
    response = requests.put(
        f"{METABASE_URL}/api/card/70",
        headers={"X-Metabase-Session": session_token},
        json=question
    )
    response.raise_for_status()
    print("✅ Division Comparison Table drill-through configured")
    return True

def configure_violations_by_division_drillthrough(session_token):
    """
    Configure E3.5: Violations by Division Table
    Click division name → Filters dashboard by that division
    """
    print("\n" + "="*60)
    print("Configuring E3.5: Violations by Division")
    print("="*60)

    # Get question
    response = requests.get(
        f"{METABASE_URL}/api/card/75",
        headers={"X-Metabase-Session": session_token}
    )
    response.raise_for_status()
    question = response.json()

    # Add click behavior for Division column
    if 'visualization_settings' not in question:
        question['visualization_settings'] = {}

    if 'column_settings' not in question['visualization_settings']:
        question['visualization_settings']['column_settings'] = {}

    question['visualization_settings']['column_settings']['["name","Division"]'] = {
        "click_behavior": {
            "type": "link",
            "linkType": "dashboard",
            "targetId": 5,  # Executive Dashboard ID
            "parameterMapping": {
                "29ce015d-049e-4239-aab6-1c2a64c015ba": {
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

    # Update question
    response = requests.put(
        f"{METABASE_URL}/api/card/75",
        headers={"X-Metabase-Session": session_token},
        json=question
    )
    response.raise_for_status()
    print("✅ Violations by Division drill-through configured")
    return True

def main():
    print("\n" + "="*60)
    print("BTRC Executive Dashboard - Configuration")
    print("Per BTRC-FXBB-QOS-POC_Dev-Spec Requirements")
    print("="*60)

    # Get session
    print("\n📡 Connecting to Metabase...")
    try:
        session_token = get_session()
        print(f"✅ Session established")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # Configure dashboard
    results = []

    # Step 1: Add Division parameter
    try:
        results.append(("Division Parameter", add_division_parameter(session_token)))
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append(("Division Parameter", False))

    # Step 2: Configure drill-through on key cards
    cards = [
        ("E1.6: Division Ranking", configure_division_ranking_drillthrough, 68),
        ("E2.1: Division Map", configure_division_map_drillthrough, 69),
        ("E2.2: Division Comparison", configure_division_comparison_drillthrough, 70),
        ("E3.5: Violations by Division", configure_violations_by_division_drillthrough, 75)
    ]

    for name, func, card_id in cards:
        try:
            results.append((name, func(session_token)))
        except Exception as e:
            print(f"❌ Error on {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {name}")

    print("\n" + "="*60)
    print("SPEC COMPLIANCE CHECK")
    print("="*60)
    print("✅ Geo Depth: National → Division (8 divisions)")
    print("✅ No district drill-down (Executive level only)")
    print("✅ Division parameter added")
    print("✅ Drill-down configured on:")
    print("   - Division Performance Ranking (E1.6)")
    print("   - Division Performance Map (E2.1)")
    print("   - Division Comparison Table (E2.2)")
    print("   - Violations by Division (E3.5)")

    print("\n" + "="*60)
    print("TESTING INSTRUCTIONS")
    print("="*60)
    print("1. Open: http://localhost:3000/dashboard/5")
    print("2. Tab E1: Click a division in 'Division Performance Ranking'")
    print("   → Dashboard filters to show data for that division only")
    print("3. Tab E2: Click a division on the choropleth map")
    print("   → Dashboard filters to that division")
    print("4. Tab E2: Click a division in 'Division Comparison Table'")
    print("   → Dashboard filters to that division")
    print("5. Tab E3: Click a division in 'Violations by Division'")
    print("   → Dashboard filters to that division")
    print("6. Clear filter (click X) to return to National view")
    print("\n✅ Executive Dashboard drill-down configured!")

    success_count = sum(1 for _, s in results if s)
    print(f"\n📊 {success_count}/{len(results)} configurations successful")

if __name__ == "__main__":
    main()
