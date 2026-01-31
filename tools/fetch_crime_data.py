#!/usr/bin/env python3
"""
Crime Data Fetcher
Fetches crime statistics from UK Police Data API (data.police.uk).
Architecture SOP: architecture/01_data_pipeline.md (Stage 3)
Data Schema: gemini.md (#4 Crime Data Response Schema)
"""

import os
import sys
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
POLICE_API_BASE = "https://data.police.uk/api"

# Area coordinates (same as TfL)
AREA_COORDS = {
    "E1": (51.5154, -0.0616),
    "E2": (51.5272, -0.0559),
    "E3": (51.5266, -0.0188),
    "E8": (51.5461, -0.0553),
    "E9": (51.5539, -0.0427),
    "E14": (51.5045, -0.0194),
    "E15": (51.5397, 0.0031),
    "SE1": (51.5040, -0.0925),
    "SE5": (51.4736, -0.0903),
    "SE8": (51.4786, -0.0270),
    "SE10": (51.4826, 0.0077),
    "SE15": (51.4739, -0.0673),
    "SE22": (51.4483, -0.0725),
    "SW1": (51.4975, -0.1357),
    "SW2": (51.4627, -0.1145),
    "SW4": (51.4623, -0.1379),
    "SW9": (51.4733, -0.1233),
    "SW11": (51.4643, -0.1647),
    "SW18": (51.4571, -0.1877),
    "N1": (51.5392, -0.1030),
    "N4": (51.5697, -0.1064),
    "N7": (51.5533, -0.1155),
    "N8": (51.5891, -0.1224),
    "N16": (51.5613, -0.0764),
    "N19": (51.5644, -0.1393),
    "W1": (51.5155, -0.1445),
    "W2": (51.5156, -0.1715),
    "W6": (51.4927, -0.2241),
    "W11": (51.5164, -0.1967),
    "W12": (51.5055, -0.2243),
}


def fetch_crime_data_api(area_code: str) -> Optional[Dict]:
    """
    Fetch real crime data from UK Police Data API.

    Args:
        area_code: Area code (e.g., "E1")

    Returns:
        Crime data dict or None if error
    """
    # Get coordinates for area
    coords = AREA_COORDS.get(area_code)
    if not coords:
        print(f"[ERROR] Unknown area code: {area_code}")
        return None

    lat, lon = coords

    try:
        # Get crime data for location (last 12 months)
        # Note: Police API returns last available data, typically 1-2 months lag
        url = f"{POLICE_API_BASE}/crimes-street/all-crime"
        params = {
            "lat": lat,
            "lng": lon
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 200:
            crimes = response.json()

            # Count crime types
            crime_breakdown = {
                "violent-crime": 0,
                "burglary": 0,
                "theft": 0,
                "vehicle-crime": 0,
                "antisocial-behaviour": 0,
                "other": 0
            }

            for crime in crimes:
                category = crime.get("category", "other")
                if category in crime_breakdown:
                    crime_breakdown[category] += 1
                elif category in ["robbery", "violence-and-sexual-offences"]:
                    crime_breakdown["violent-crime"] += 1
                elif category in ["shoplifting", "theft-from-the-person", "bicycle-theft"]:
                    crime_breakdown["theft"] += 1
                else:
                    crime_breakdown["other"] += 1

            total_crimes = len(crimes)

            # Calculate safety score (0-100, higher is safer)
            # London average is ~70-80 crimes per month in a small area
            # Fewer crimes = higher score
            if total_crimes < 30:
                safety_score = 90
            elif total_crimes < 60:
                safety_score = 75
            elif total_crimes < 90:
                safety_score = 60
            elif total_crimes < 120:
                safety_score = 45
            else:
                safety_score = 30

            # Estimate trend (simplified - would need historical data for real trend)
            trend = "stable"

            # Percentile vs London (mock - would need city-wide data)
            percentile = safety_score

            return {
                "area_code": area_code,
                "lat": lat,
                "lon": lon,
                "time_period_months": 1,  # Police API returns 1 month
                "total_crimes": total_crimes,
                "crimes_per_1000_people": total_crimes,  # Simplified
                "safety_score": safety_score,
                "crime_breakdown": crime_breakdown,
                "trend": trend,
                "percentile_vs_london": percentile,
                "timestamp": datetime.now().isoformat(),
                "data_source": "uk_police_data"
            }

        else:
            print(f"[ERROR] Police API error {response.status_code} for {area_code}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to fetch crime data for {area_code}: {e}")
        return None


def fetch_crime_data(area_code: str, use_cache: bool = True) -> Optional[Dict]:
    """
    Fetch crime data (cached).

    Args:
        area_code: Area code
        use_cache: Whether to check cache first

    Returns:
        Crime data dict or None
    """
    # Check cache
    if use_cache:
        cached = read_cache("crime_data", area_code)
        if cached:
            print(f"[CACHE] Using cached crime data for {area_code}")
            return cached

    # Fetch from API
    print(f"[API] Fetching crime data for {area_code}")
    data = fetch_crime_data_api(area_code)

    # Cache if successful
    if data and use_cache:
        write_cache("crime_data", area_code, data)

    return data


if __name__ == "__main__":
    # Test the tool
    print("="*80)
    print("Crime Data Fetcher - Test Mode")
    print("="*80)
    print("")

    # Test 1: Fetch crime data for E1
    print("Test 1: Crime data for E1 (Whitechapel)")
    data = fetch_crime_data("E1")
    if data:
        print(f"  Area: {data['area_code']}")
        print(f"  Total crimes: {data['total_crimes']} (last month)")
        print(f"  Safety score: {data['safety_score']}/100")
        print(f"  Trend: {data['trend']}")
        print(f"  Crime breakdown:")
        for crime_type, count in data['crime_breakdown'].items():
            if count > 0:
                print(f"    - {crime_type}: {count}")
        print(f"  Source: {data['data_source']}")
    print("")

    # Test 2: Different area
    print("Test 2: Crime data for SW1 (Westminster)")
    data2 = fetch_crime_data("SW1")
    if data2:
        print(f"  Total crimes: {data2['total_crimes']}")
        print(f"  Safety score: {data2['safety_score']}/100")
    print("")

    # Test 3: Cache check
    print("Test 3: Fetch E1 again (should use cache)")
    data3 = fetch_crime_data("E1")
    print(f"  Source: {data3['data_source'] if data3 else 'None'}")
    print("")

    print("="*80)
