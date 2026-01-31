#!/usr/bin/env python3
"""
TfL Commute Calculator
Calculates commute times using Transport for London API or mock data.
Architecture SOP: architecture/01_data_pipeline.md (Stage 3)
Data Schema: gemini.md (#3 TfL Commute Response Schema)
"""

import os
import sys
import random
import requests
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

# Load environment variables
load_dotenv()

# Configuration
TFL_APP_KEY = os.getenv("TFL_APP_KEY")
TFL_BASE_URL = "https://api.tfl.gov.uk"
USE_MOCK_DATA = not TFL_APP_KEY  # Use mock if no key

# London area coordinates (for distance calculations in mock mode)
AREA_COORDS = {
    "E1": (51.5154, -0.0616),    # Whitechapel
    "E2": (51.5272, -0.0559),    # Bethnal Green
    "E3": (51.5266, -0.0188),    # Bow
    "E8": (51.5461, -0.0553),    # Hackney
    "E9": (51.5539, -0.0427),    # Homerton
    "E14": (51.5045, -0.0194),   # Canary Wharf
    "E15": (51.5397, 0.0031),    # Stratford
    "SE1": (51.5040, -0.0925),   # Southwark
    "SE5": (51.4736, -0.0903),   # Camberwell
    "SE8": (51.4786, -0.0270),   # Deptford
    "SE10": (51.4826, 0.0077),   # Greenwich
    "SE15": (51.4739, -0.0673),  # Peckham
    "SE22": (51.4483, -0.0725),  # East Dulwich
    "SW1": (51.4975, -0.1357),   # Westminster
    "SW2": (51.4627, -0.1145),   # Brixton
    "SW4": (51.4623, -0.1379),   # Clapham
    "SW9": (51.4733, -0.1233),   # Stockwell
    "SW11": (51.4643, -0.1647),  # Battersea
    "SW18": (51.4571, -0.1877),  # Wandsworth
    "N1": (51.5392, -0.1030),    # Islington
    "N4": (51.5697, -0.1064),    # Finsbury Park
    "N7": (51.5533, -0.1155),    # Holloway
    "N8": (51.5891, -0.1224),    # Crouch End
    "N16": (51.5613, -0.0764),   # Stoke Newington
    "N19": (51.5644, -0.1393),   # Archway
    "W1": (51.5155, -0.1445),    # Mayfair
    "W2": (51.5156, -0.1715),    # Paddington
    "W6": (51.4927, -0.2241),    # Hammersmith
    "W11": (51.5164, -0.1967),   # Notting Hill
    "W12": (51.5055, -0.2243),   # Shepherds Bush
    # Universities
    "UCL": (51.5246, -0.1340),   # University College London
    "KCL": (51.5115, -0.1160),   # King's College London
    "LSE": (51.5145, -0.1167),   # London School of Economics
    "Imperial": (51.4988, -0.1749),  # Imperial College
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in km using Haversine formula.

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth's radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


def generate_mock_commute_data(from_area: str, to_location: str) -> Dict:
    """
    Generate realistic mock TfL commute data.

    Args:
        from_area: Origin area code (e.g., "E1")
        to_location: Destination (e.g., "UCL", "KCL")

    Returns:
        Dict matching TfL Commute Response Schema
    """
    # Get coordinates
    from_coords = AREA_COORDS.get(from_area, (51.5074, -0.1278))  # Default to central London
    to_coords = AREA_COORDS.get(to_location, (51.5074, -0.1278))

    # Calculate distance
    distance_km = haversine_distance(from_coords[0], from_coords[1], to_coords[0], to_coords[1])

    # Estimate travel time based on distance
    # Assume average tube speed ~20km/h in central London
    base_duration = (distance_km / 20) * 60  # minutes

    # Add variation
    duration_minutes = int(base_duration + random.randint(-5, 15))
    duration_minutes = max(5, duration_minutes)  # Minimum 5 minutes

    # Generate changes (transfers)
    if duration_minutes < 15:
        changes = 0
    elif duration_minutes < 30:
        changes = random.choice([0, 1])
    else:
        changes = random.choice([1, 2])

    # Walking time (platform transfers + first/last mile)
    walking_minutes = 5 + (changes * 3) + random.randint(0, 5)

    # Accessibility score (0-100, higher is better)
    # Fewer changes = better accessibility
    accessibility = 100 - (changes * 15) - random.randint(0, 20)
    accessibility = max(30, min(100, accessibility))

    # Route summary
    lines = ["District", "Circle", "Central", "Northern", "Piccadilly", "Victoria", "Jubilee"]
    if changes == 0:
        route = f"{random.choice(lines)} line direct"
    elif changes == 1:
        route = f"{random.choice(lines)} line to {random.choice(lines)} line"
    else:
        route = f"{random.choice(lines)} line via {random.choice(lines)} line"

    return {
        "from": from_area,
        "to": to_location,
        "mode": "tube",
        "duration_minutes": duration_minutes,
        "changes": changes,
        "walking_minutes": walking_minutes,
        "accessibility_score": accessibility,
        "route_summary": route,
        "disruptions": [],  # No disruptions in mock data
        "timestamp": datetime.now().isoformat(),
        "data_source": "tfl_mock",
    }


def fetch_tfl_commute_real(from_area: str, to_location: str) -> Optional[Dict]:
    """
    Fetch real commute data from TfL API.

    Args:
        from_area: Origin area code
        to_location: Destination

    Returns:
        TfL commute data dict or None if error
    """
    if not TFL_APP_KEY:
        print("[WARNING] TFL_APP_KEY not set in .env, using free API")

    try:
        # TfL Journey Planner API
        url = f"{TFL_BASE_URL}/Journey/JourneyResults/{from_area}/to/{to_location}"
        params = {}
        if TFL_APP_KEY:
            params["app_key"] = TFL_APP_KEY

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Parse TfL response (simplified)
            journey = data.get("journeys", [{}])[0] if data.get("journeys") else {}

            if not journey:
                return None

            duration = journey.get("duration", 30)
            legs = journey.get("legs", [])

            # Count changes
            changes = len(legs) - 1 if len(legs) > 1 else 0

            # Calculate walking time
            walking_mins = sum(
                leg.get("duration", 0)
                for leg in legs
                if leg.get("mode", {}).get("name") == "walking"
            )

            # Extract route summary
            modes = [leg.get("mode", {}).get("name", "tube") for leg in legs]
            route = " to ".join(set(modes))

            return {
                "from": from_area,
                "to": to_location,
                "mode": "tube",
                "duration_minutes": duration,
                "changes": changes,
                "walking_minutes": walking_mins,
                "accessibility_score": max(30, 100 - (changes * 20)),
                "route_summary": route,
                "disruptions": [],
                "timestamp": datetime.now().isoformat(),
                "data_source": "tfl",
            }
        else:
            print(f"[ERROR] TfL API error {response.status_code}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to fetch TfL data: {e}")
        return None


def fetch_commute_data(
    from_area: str,
    to_location: str,
    use_cache: bool = True
) -> Optional[Dict]:
    """
    Fetch commute data (cached).

    Args:
        from_area: Origin area code
        to_location: Destination
        use_cache: Whether to check cache first

    Returns:
        Commute data dict or None
    """
    cache_key = f"{from_area}_to_{to_location}"

    # Check cache
    if use_cache:
        cached = read_cache("tfl_commute", cache_key)
        if cached:
            print(f"[CACHE] Using cached commute data for {cache_key}")
            return cached

    # Fetch data
    if USE_MOCK_DATA:
        print(f"[MOCK] Generating mock commute data for {cache_key}")
        data = generate_mock_commute_data(from_area, to_location)
    else:
        print(f"[API] Fetching real TfL data for {cache_key}")
        data = fetch_tfl_commute_real(from_area, to_location)

    # Cache if successful
    if data and use_cache:
        write_cache("tfl_commute", cache_key, data)

    return data


if __name__ == "__main__":
    # Test the tool
    print("="*80)
    print("TfL Commute Calculator - Test Mode")
    print("="*80)
    print("")

    # Test 1: Calculate commute from E1 to UCL
    print("Test 1: E1 (Whitechapel) to UCL")
    data = fetch_commute_data("E1", "UCL")
    if data:
        print(f"  Route: {data['from']} -> {data['to']}")
        print(f"  Duration: {data['duration_minutes']} minutes")
        print(f"  Changes: {data['changes']}")
        print(f"  Walking: {data['walking_minutes']} minutes")
        print(f"  Accessibility: {data['accessibility_score']}/100")
        print(f"  Route: {data['route_summary']}")
        print(f"  Source: {data['data_source']}")
    print("")

    # Test 2: Different route
    print("Test 2: SW9 (Stockwell) to Imperial")
    data2 = fetch_commute_data("SW9", "Imperial")
    if data2:
        print(f"  Duration: {data2['duration_minutes']} minutes")
        print(f"  Changes: {data2['changes']}")
        print(f"  Accessibility: {data2['accessibility_score']}/100")
    print("")

    # Test 3: Cache check
    print("Test 3: E1 to UCL again (should use cache)")
    data3 = fetch_commute_data("E1", "UCL")
    print(f"  Source: {data3['data_source'] if data3 else 'None'}")
    print("")

    print("="*80)
