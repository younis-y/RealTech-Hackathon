#!/usr/bin/env python3
"""
UK Domestic Energy Performance Certificates (EPC) API Fetcher
Fetches property specifications from the official EPC Open Data API.

Data provides:
- Floor area (sq meters)
- Number of rooms
- Energy rating (A-G)
- Property age indicators

API: https://epc.opendatacommunities.org
"""

import os
import sys
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

# Load environment variables
load_dotenv()

# API Configuration
EPC_BASE_URL = "https://epc.opendatacommunities.org"
EPC_USERNAME = os.getenv("EPC_API_USERNAME", "ucbvymy@ucl.ac.uk")
EPC_PASSWORD = os.getenv("EPC_API_PASSWORD", "5ebcdeb46aa403568974472cf668941f114ba0a9")

# Use mock data if API unavailable
USE_MOCK_DATA = os.getenv("USE_MOCK_EPC", "false").lower() == "true"


def fetch_epc_real(postcode: str, size: int = 25) -> Optional[List[Dict]]:
    """
    Fetch real EPC data from the API.
    
    Args:
        postcode: UK postcode (e.g., "SW1A 1AA")
        size: Max results to return
        
    Returns:
        List of EPC certificate data or None if error
    """
    try:
        url = f"{EPC_BASE_URL}/api/v1/domestic/search"
        
        params = {
            "postcode": postcode,
            "size": size
        }
        
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            auth=(EPC_USERNAME, EPC_PASSWORD),
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get("rows", [])
            print(f"[EPC API] Found {len(rows)} certificates for {postcode}")
            return rows
        else:
            print(f"[EPC API] Error {response.status_code} for {postcode}")
            return None
            
    except Exception as e:
        print(f"[EPC API] Failed to fetch data for {postcode}: {e}")
        return None


def generate_mock_epc_data(postcode: str) -> List[Dict]:
    """
    Generate realistic mock EPC data for development.
    """
    import random
    
    # Generate 3-8 mock certificates
    num_certs = random.randint(3, 8)
    certs = []
    
    energy_ratings = ["A", "B", "C", "D", "E", "F", "G"]
    rating_weights = [2, 10, 25, 35, 18, 7, 3]  # D is most common
    
    for i in range(num_certs):
        floor_area = random.randint(35, 180)  # sq meters
        rooms = max(1, floor_area // 25)  # rough rooms estimate
        current_rating = random.choices(energy_ratings, weights=rating_weights)[0]
        potential_idx = max(0, energy_ratings.index(current_rating) - random.randint(1, 3))
        
        certs.append({
            "lmk-key": f"MOCK-{postcode.replace(' ', '')}-{i}",
            "address": f"{random.randint(1, 200)} {random.choice(['HIGH', 'MAIN', 'CHURCH', 'STATION'])} STREET",
            "postcode": postcode.upper(),
            "total-floor-area": str(floor_area),
            "number-habitable-rooms": str(rooms),
            "current-energy-rating": current_rating,
            "potential-energy-rating": energy_ratings[potential_idx],
            "lodgement-date": f"202{random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "_mock": True
        })
    
    return certs


def fetch_epc_data(postcode: str, use_cache: bool = True) -> Optional[List[Dict]]:
    """
    Fetch EPC data for a postcode (cached).
    
    Args:
        postcode: UK postcode
        use_cache: Whether to use cached data
        
    Returns:
        List of EPC certificates or None
    """
    cache_key = postcode.replace(" ", "").upper()
    
    # Check cache
    if use_cache:
        cached = read_cache("epc_certificates", cache_key)
        if cached:
            print(f"[CACHE] Using cached EPC data for {postcode}")
            return cached
    
    # Fetch data
    if USE_MOCK_DATA:
        print(f"[MOCK] Generating mock EPC data for {postcode}")
        data = generate_mock_epc_data(postcode)
    else:
        print(f"[API] Fetching real EPC data for {postcode}")
        data = fetch_epc_real(postcode)
        
        # Fallback to mock if API fails
        if data is None:
            print(f"[FALLBACK] Using mock EPC data for {postcode}")
            data = generate_mock_epc_data(postcode)
    
    # Cache result
    if data and use_cache:
        write_cache("epc_certificates", cache_key, data)
    
    return data


def get_area_epc_summary(postcode_prefix: str) -> Dict:
    """
    Get aggregated EPC statistics for an area.
    
    Args:
        postcode_prefix: Area code like "SW1A", "E1", "N16"
        
    Returns:
        Summary dict with avg floor area, rooms, energy ratings
    """
    # For area codes, we need to search with just the prefix
    # The API requires a full postcode, so we'll use sample postcodes
    sample_postcodes = {
        "E1": "E1 1AA", "E2": "E2 0AA", "E3": "E3 2AA",
        "N1": "N1 1AA", "N7": "N7 8AA", "N16": "N16 5AA",
        "SW1": "SW1A 1AA", "SW2": "SW2 1AA", "SE1": "SE1 1AA",
        # Add more as needed
    }
    
    postcode = sample_postcodes.get(postcode_prefix, f"{postcode_prefix} 1AA")
    
    certs = fetch_epc_data(postcode)
    
    if not certs:
        return {
            "avg_floor_area_sqm": 65,
            "avg_rooms": 3,
            "energy_rating_distribution": {"D": 100},
            "most_common_rating": "D",
            "sample_size": 0
        }
    
    # Calculate averages
    floor_areas = []
    rooms = []
    ratings = {}
    
    for cert in certs:
        try:
            area = int(cert.get("total-floor-area", 0))
            if area > 0:
                floor_areas.append(area)
        except ValueError:
            pass
            
        try:
            room_count = int(cert.get("number-habitable-rooms", 0))
            if room_count > 0:
                rooms.append(room_count)
        except ValueError:
            pass
            
        rating = cert.get("current-energy-rating", "D")
        ratings[rating] = ratings.get(rating, 0) + 1
    
    avg_area = sum(floor_areas) / len(floor_areas) if floor_areas else 65
    avg_rooms = sum(rooms) / len(rooms) if rooms else 3
    most_common = max(ratings, key=ratings.get) if ratings else "D"
    
    return {
        "avg_floor_area_sqm": round(avg_area, 1),
        "avg_rooms": round(avg_rooms, 1),
        "energy_rating_distribution": ratings,
        "most_common_rating": most_common,
        "sample_size": len(certs),
        "postcode_sampled": postcode
    }


if __name__ == "__main__":
    print("=" * 80)
    print("UK EPC API Fetcher - Test Mode")
    print("=" * 80)
    print()
    
    # Test 1: Fetch for specific postcode
    print("Test 1: Fetch EPC data for E1 1AA")
    certs = fetch_epc_data("E1 1AA")
    if certs:
        print(f"  Found {len(certs)} certificates")
        if certs:
            cert = certs[0]
            print(f"  Sample: {cert.get('address')}")
            print(f"  Floor area: {cert.get('total-floor-area')} sqm")
            print(f"  Rooms: {cert.get('number-habitable-rooms')}")
            print(f"  Energy: {cert.get('current-energy-rating')}")
    print()
    
    # Test 2: Get area summary
    print("Test 2: Get area summary for N16")
    summary = get_area_epc_summary("N16")
    print(f"  Avg floor area: {summary['avg_floor_area_sqm']} sqm")
    print(f"  Avg rooms: {summary['avg_rooms']}")
    print(f"  Most common rating: {summary['most_common_rating']}")
    print(f"  Sample size: {summary['sample_size']}")
    print()
    
    print("=" * 80)
