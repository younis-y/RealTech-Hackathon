#!/usr/bin/env python3
"""
API Verification Tool - Phase 2: Link Handshake Tests
Tests all external API connections before proceeding to full development.
Architecture SOP: architecture/05_api_integrations.md
"""

import os
import sys
import requests
from dotenv import load_dotenv
from typing import Dict, Tuple

# Load environment variables
load_dotenv()

# API Configuration
APIS = {
    "scansan": {
        "name": "ScanSan Property Intelligence",
        "required": True,
        "env_var": "SCANSAN_API_KEY",
        "test_endpoint": "https://api.scansan.com/v1/area/SW1A",
        "auth_type": "bearer"
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "required": True,
        "env_var": "ANTHROPIC_API_KEY",
        "test_endpoint": None,  # Use SDK test
        "auth_type": "sdk"
    },
    "tfl": {
        "name": "Transport for London",
        "required": False,
        "env_var": "TFL_APP_KEY",
        "test_endpoint": "https://api.tfl.gov.uk/Line/Meta/Modes",
        "auth_type": "param"
    },
    "google_maps": {
        "name": "Google Maps",
        "required": False,
        "env_var": "GOOGLE_MAPS_API_KEY",
        "test_endpoint": "https://maps.googleapis.com/maps/api/geocode/json?address=SW1A+1AA",
        "auth_type": "param"
    },
    "police": {
        "name": "UK Police Data",
        "required": False,
        "env_var": None,
        "test_endpoint": "https://data.police.uk/api/crimes-at-location?lat=51.5014&lng=-0.1419&date=2024-11",
        "auth_type": "none"
    },
    "osm": {
        "name": "OpenStreetMap Overpass",
        "required": False,
        "env_var": None,
        "test_endpoint": "https://overpass-api.de/api/status",
        "auth_type": "none"
    }
}


def verify_api(api_id: str, config: Dict) -> Tuple[bool, str]:
    """
    Verify a single API connection.

    Args:
        api_id: API identifier
        config: API configuration dict

    Returns:
        Tuple of (success: bool, message: str)
    """
    name = config["name"]
    env_var = config["env_var"]
    endpoint = config["test_endpoint"]
    auth_type = config["auth_type"]

    # Check if API key is required and present
    if env_var:
        api_key = os.getenv(env_var)
        if not api_key:
            return False, f"Missing {env_var} in .env"

    # Handle different authentication types
    try:
        if auth_type == "none":
            # No authentication required
            response = requests.get(endpoint, timeout=10)

        elif auth_type == "bearer":
            # Bearer token in Authorization header
            api_key = os.getenv(env_var)
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(endpoint, headers=headers, timeout=10)

        elif auth_type == "param":
            # API key as query parameter
            api_key = os.getenv(env_var)
            # Different param names for different APIs
            if api_id == "tfl":
                params = {"app_key": api_key}
            elif api_id == "google_maps":
                params = {"key": api_key}
            else:
                params = {"api_key": api_key}

            response = requests.get(endpoint, params=params, timeout=10)

        elif auth_type == "sdk":
            # Special handling for SDK-based APIs
            if api_id == "anthropic":
                return verify_anthropic()
            else:
                return False, "SDK verification not implemented"

        else:
            return False, f"Unknown auth type: {auth_type}"

        # Check response
        if response.status_code == 200:
            return True, "[OK] Connected"
        elif response.status_code == 401:
            return False, f"[FAIL] Authentication failed (check {env_var})"
        elif response.status_code == 403:
            return False, f"[FAIL] Forbidden (check API permissions)"
        elif response.status_code == 429:
            return False, "[WARN] Rate limited (but connection works)"
        else:
            return False, f"[FAIL] HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "[FAIL] Connection timeout"
    except requests.exceptions.ConnectionError:
        return False, "[FAIL] Connection failed (check internet)"
    except Exception as e:
        return False, f"[FAIL] Error: {str(e)}"


def verify_anthropic() -> Tuple[bool, str]:
    """Special verification for Anthropic Claude API."""
    try:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return False, "Missing ANTHROPIC_API_KEY in .env"

        client = anthropic.Anthropic(api_key=api_key)

        # Minimal test message
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        if message.content:
            return True, "[OK] Connected"
        else:
            return False, "[FAIL] No response from API"

    except ImportError:
        return False, "[FAIL] anthropic package not installed (pip install anthropic)"
    except anthropic.AuthenticationError:
        return False, "[FAIL] Authentication failed (check ANTHROPIC_API_KEY)"
    except Exception as e:
        return False, f"[FAIL] Error: {str(e)}"


def verify_all_apis(verbose: bool = False) -> Dict[str, Dict]:
    """
    Verify all configured APIs.

    Args:
        verbose: Print detailed output

    Returns:
        Dictionary of results per API
    """
    results = {}

    if verbose:
        print("="*80)
        print("API VERIFICATION - Phase 2: Link")
        print("="*80)
        print("")

    for api_id, config in APIS.items():
        name = config["name"]
        required = config["required"]

        if verbose:
            status_text = "[REQUIRED]" if required else "[OPTIONAL]"
            print(f"{status_text} {name}...", end=" ")

        success, message = verify_api(api_id, config)
        results[api_id] = {
            "name": name,
            "required": required,
            "success": success,
            "message": message
        }

        if verbose:
            print(message)

    return results


def print_summary(results: Dict[str, Dict]) -> None:
    """Print verification summary."""
    print("")
    print("="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    required_pass = sum(1 for r in results.values() if r["required"] and r["success"])
    required_total = sum(1 for r in results.values() if r["required"])
    optional_pass = sum(1 for r in results.values() if not r["required"] and r["success"])
    optional_total = sum(1 for r in results.values() if not r["required"])

    print(f"Required APIs: {required_pass}/{required_total} passed")
    print(f"Optional APIs: {optional_pass}/{optional_total} passed")
    print("")

    # Check if ready to proceed
    all_required_pass = required_pass == required_total

    if all_required_pass:
        print("[SUCCESS] READY TO PROCEED - All required APIs verified")
        print("")
        print("Next steps:")
        print("1. Proceed to Phase 3: Architect (build tools/)")
        print("2. Update gemini.md Link status to verified")
    else:
        print("[FAILED] NOT READY - Some required APIs failed")
        print("")
        print("Action required:")
        for api_id, result in results.items():
            if result["required"] and not result["success"]:
                print(f"  - Fix: {result['name']} - {result['message']}")
        print("")
        print("After fixing, run this script again.")

    print("="*80)


def update_gemini_md(results: Dict[str, Dict]) -> None:
    """
    Update gemini.md with verification results.

    Args:
        results: Verification results dict
    """
    try:
        # This would update the gemini.md file programmatically
        # For now, just print what to update
        print("")
        print("Update gemini.md:")
        print("-" * 80)
        for api_id, result in results.items():
            status = "[OK] VERIFIED" if result["success"] else "[FAIL] FAILED"
            print(f"| {result['name']:30} | {status:15} | {result['message']:30} |")
        print("-" * 80)

    except Exception as e:
        print(f"[WARNING] Could not update gemini.md: {e}")


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print("Starting API verification...")
    print("")

    results = verify_all_apis(verbose=True)

    print_summary(results)

    if "--update-gemini" in sys.argv:
        update_gemini_md(results)

    # Exit code: 0 if all required pass, 1 otherwise
    all_required_pass = all(
        result["success"]
        for result in results.values()
        if result["required"]
    )

    sys.exit(0 if all_required_pass else 1)
