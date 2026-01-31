#!/usr/bin/env python3
"""
ScanSan Property Intelligence Fetcher
Fetches property/area data from ScanSan API or generates mock data for development.
Architecture SOP: architecture/01_data_pipeline.md (Stage 2)
Data Schema: gemini.md (#2 ScanSan API Response Schema)
"""

import os
import sys
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

# Load environment variables
load_dotenv()

# Configuration
SCANSAN_API_KEY = os.getenv("SCANSAN_API_KEY")
SCANSAN_BASE_URL = os.getenv("SCANSAN_BASE_URL", "https://api.scansan.com/v1")
USE_MOCK_DATA = True  # Set to False when ScanSan API is working

# London area codes for mock data (realistic areas)
LONDON_AREAS = {
    # East London - More affordable
    "E1": {"name": "Whitechapel", "tier": "affordable"},
    "E2": {"name": "Bethnal Green", "tier": "affordable"},
    "E3": {"name": "Bow", "tier": "affordable"},
    "E8": {"name": "Hackney", "tier": "moderate"},
    "E9": {"name": "Homerton", "tier": "affordable"},
    "E14": {"name": "Canary Wharf", "tier": "expensive"},
    "E15": {"name": "Stratford", "tier": "moderate"},

    # Southeast London
    "SE1": {"name": "Southwark", "tier": "expensive"},
    "SE5": {"name": "Camberwell", "tier": "moderate"},
    "SE8": {"name": "Deptford", "tier": "affordable"},
    "SE10": {"name": "Greenwich", "tier": "moderate"},
    "SE15": {"name": "Peckham", "tier": "affordable"},
    "SE22": {"name": "East Dulwich", "tier": "moderate"},

    # Southwest London
    "SW1": {"name": "Westminster", "tier": "very_expensive"},
    "SW2": {"name": "Brixton", "tier": "moderate"},
    "SW4": {"name": "Clapham", "tier": "expensive"},
    "SW9": {"name": "Stockwell", "tier": "affordable"},
    "SW11": {"name": "Battersea", "tier": "expensive"},
    "SW18": {"name": "Wandsworth", "tier": "moderate"},

    # North London
    "N1": {"name": "Islington", "tier": "expensive"},
    "N4": {"name": "Finsbury Park", "tier": "moderate"},
    "N7": {"name": "Holloway", "tier": "moderate"},
    "N8": {"name": "Crouch End", "tier": "expensive"},
    "N16": {"name": "Stoke Newington", "tier": "moderate"},
    "N19": {"name": "Archway", "tier": "moderate"},

    # West London
    "W1": {"name": "Mayfair", "tier": "very_expensive"},
    "W2": {"name": "Paddington", "tier": "expensive"},
    "W6": {"name": "Hammersmith", "tier": "expensive"},
    "W11": {"name": "Notting Hill", "tier": "very_expensive"},
    "W12": {"name": "Shepherds Bush", "tier": "moderate"},
}

# Price tiers for mock data
PRICE_TIERS = {
    "affordable": {
        "rent_range": (800, 1200),
        "purchase_range": (300000, 450000),
        "affordability": (65, 85),
        "investment": (55, 70),
    },
    "moderate": {
        "rent_range": (1200, 1800),
        "purchase_range": (450000, 650000),
        "affordability": (45, 65),
        "investment": (60, 75),
    },
    "expensive": {
        "rent_range": (1800, 2500),
        "purchase_range": (650000, 900000),
        "affordability": (30, 50),
        "investment": (65, 80),
    },
    "very_expensive": {
        "rent_range": (2500, 4000),
        "purchase_range": (900000, 1500000),
        "affordability": (15, 35),
        "investment": (70, 90),
    },
}


def generate_mock_scansan_data(area_code: str) -> Dict:
    """
    Generate realistic mock ScanSan property data for development.

    Args:
        area_code: London area code (e.g., "SW1A", "E1")

    Returns:
        Dict matching ScanSan API Response Schema
    """
    # Get area info or use defaults
    area_info = LONDON_AREAS.get(area_code, {"name": f"Area {area_code}", "tier": "moderate"})
    tier = area_info["tier"]
    tier_data = PRICE_TIERS[tier]

    # Generate scores
    affordability = random.randint(*tier_data["affordability"])
    risk = random.randint(30, 70)  # Lower is better (less risk)
    investment = random.randint(*tier_data["investment"])
    demand = random.randint(50, 90)

    # Generate prices
    rent = random.randint(*tier_data["rent_range"])
    purchase = random.randint(*tier_data["purchase_range"])

    # Calculate realistic yield (annual rent / purchase price * 100)
    annual_rent = rent * 12
    yield_estimate = round((annual_rent / purchase) * 100, 2)

    # Generate price trends (historical growth)
    price_trends = {
        "1yr": round(random.uniform(-2, 8), 1),  # % change
        "3yr": round(random.uniform(5, 20), 1),
        "5yr": round(random.uniform(15, 40), 1),
    }

    return {
        "area_code": area_code,
        "area_name": area_info["name"],
        "affordability_score": affordability,
        "risk_score": risk,
        "investment_quality": investment,
        "demand_index": demand,
        "price_trends": price_trends,
        "yield_estimate": yield_estimate,
        "avg_price_rent_pm": rent,
        "avg_price_purchase": purchase,
        "timestamp": datetime.now().isoformat(),
        "data_source": "scansan_mock",
    }


def fetch_scansan_real(area_code: str) -> Optional[Dict]:
    """
    Fetch real data from ScanSan API.

    Args:
        area_code: Area code to fetch

    Returns:
        ScanSan data dict or None if error
    """
    if not SCANSAN_API_KEY:
        print("[WARNING] SCANSAN_API_KEY not set in .env")
        return None

    try:
        url = f"{SCANSAN_BASE_URL}/area/{area_code}"
        headers = {
            "Authorization": f"Bearer {SCANSAN_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Normalize to our schema
            return {
                "area_code": area_code,
                "affordability_score": data.get("affordability", 50),
                "risk_score": data.get("risk", 50),
                "investment_quality": data.get("investment_quality", 50),
                "demand_index": data.get("demand", 50),
                "price_trends": data.get("price_trends", {"1yr": 0, "3yr": 0, "5yr": 0}),
                "yield_estimate": data.get("yield", 0),
                "avg_price_rent_pm": data.get("rent_pm", 0),
                "avg_price_purchase": data.get("purchase", 0),
                "timestamp": datetime.now().isoformat(),
                "data_source": "scansan",
            }
        else:
            print(f"[ERROR] ScanSan API error {response.status_code} for {area_code}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to fetch ScanSan data for {area_code}: {e}")
        return None


def fetch_scansan_data(area_code: str, use_cache: bool = True) -> Optional[Dict]:
    """
    Fetch ScanSan property data for an area (cached).

    Args:
        area_code: Area code (e.g., "SW1A", "E1")
        use_cache: Whether to check cache first

    Returns:
        ScanSan data dict or None
    """
    # Check cache first
    if use_cache:
        cached = read_cache("scansan_property", area_code)
        if cached:
            print(f"[CACHE] Using cached ScanSan data for {area_code}")
            return cached

    # Fetch data (real or mock)
    if USE_MOCK_DATA:
        print(f"[MOCK] Generating mock ScanSan data for {area_code}")
        data = generate_mock_scansan_data(area_code)
    else:
        print(f"[API] Fetching real ScanSan data for {area_code}")
        data = fetch_scansan_real(area_code)

    # Cache if successful
    if data and use_cache:
        write_cache("scansan_property", area_code, data)

    return data


def get_candidate_areas(
    budget_max: int,
    budget_min: Optional[int] = None,
    location_type: str = "rent",
    candidate_areas: Optional[List[str]] = None,
    affordability_threshold: int = 60
) -> List[str]:
    """
    Get candidate areas matching budget criteria.

    Args:
        budget_max: Maximum budget (£/month for rent, £ total for purchase)
        budget_min: Minimum budget (optional)
        location_type: "rent" or "buy"
        candidate_areas: Optional list of specific areas to check
        affordability_threshold: Minimum affordability score (0-100)

    Returns:
        List of area codes matching criteria
    """
    # If user provides specific areas, use those
    if candidate_areas:
        print(f"[INFO] Using user-specified areas: {candidate_areas}")
        return candidate_areas

    # Otherwise, search all areas and filter by budget
    print(f"[INFO] Searching areas for budget £{budget_max} ({location_type})")

    matching_areas = []

    for area_code in LONDON_AREAS.keys():
        data = fetch_scansan_data(area_code)

        if not data:
            continue

        # Check affordability threshold
        if data["affordability_score"] < affordability_threshold:
            continue

        # Check budget
        if location_type == "rent":
            price = data["avg_price_rent_pm"]
        else:
            price = data["avg_price_purchase"]

        if price <= budget_max:
            if budget_min is None or price >= budget_min:
                matching_areas.append(area_code)

    # Limit to top 20 by affordability
    matching_areas.sort(
        key=lambda ac: fetch_scansan_data(ac)["affordability_score"],
        reverse=True
    )

    top_areas = matching_areas[:20]
    print(f"[INFO] Found {len(matching_areas)} areas, returning top {len(top_areas)}")

    return top_areas


if __name__ == "__main__":
    # Test the tool
    print("="*80)
    print("ScanSan Property Intelligence Fetcher - Test Mode")
    print("="*80)
    print("")

    # Test 1: Fetch single area
    print("Test 1: Fetch data for E1 (Whitechapel)")
    data = fetch_scansan_data("E1")
    if data:
        print(f"  Area: {data['area_code']} - {data.get('area_name', 'N/A')}")
        print(f"  Affordability: {data['affordability_score']}/100")
        print(f"  Investment Quality: {data['investment_quality']}/100")
        print(f"  Risk: {data['risk_score']}/100")
        print(f"  Rent: £{data['avg_price_rent_pm']}/month")
        print(f"  Purchase: £{data['avg_price_purchase']:,}")
        print(f"  Yield: {data['yield_estimate']}%")
        print(f"  Source: {data['data_source']}")
    print("")

    # Test 2: Get candidate areas
    print("Test 2: Find areas for student (£1000/month max rent)")
    areas = get_candidate_areas(
        budget_max=1000,
        location_type="rent",
        affordability_threshold=60
    )
    print(f"  Found {len(areas)} areas: {', '.join(areas[:10])}")
    print("")

    # Test 3: Cache check
    print("Test 3: Fetch E1 again (should use cache)")
    data2 = fetch_scansan_data("E1")
    print(f"  Source: {data2['data_source'] if data2 else 'None'}")
    print("")

    print("="*80)
