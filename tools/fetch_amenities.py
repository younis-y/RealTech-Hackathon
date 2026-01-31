#!/usr/bin/env python3
"""
Amenities Mapper
Fetches nearby amenities (cafes, gyms, supermarkets) using OpenStreetMap.
Architecture SOP: architecture/01_data_pipeline.md (Stage 3)
Data Schema: gemini.md (#6 Amenities Response Schema)
"""

import os
import sys
import requests
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

load_dotenv()

OVERPASS_API = "https://overpass-api.de/api/interpreter"

AREA_COORDS = {
    "E1": (51.5154, -0.0616), "E2": (51.5272, -0.0559), "E3": (51.5266, -0.0188),
    "E8": (51.5461, -0.0553), "E9": (51.5539, -0.0427), "E14": (51.5045, -0.0194),
    "E15": (51.5397, 0.0031), "SE1": (51.5040, -0.0925), "SE5": (51.4736, -0.0903),
    "SE8": (51.4786, -0.0270), "SE10": (51.4826, 0.0077), "SE15": (51.4739, -0.0673),
    "SE22": (51.4483, -0.0725), "SW1": (51.4975, -0.1357), "SW2": (51.4627, -0.1145),
    "SW4": (51.4623, -0.1379), "SW9": (51.4733, -0.1233), "SW11": (51.4643, -0.1647),
    "SW18": (51.4571, -0.1877), "N1": (51.5392, -0.1030), "N4": (51.5697, -0.1064),
    "N7": (51.5533, -0.1155), "N8": (51.5891, -0.1224), "N16": (51.5613, -0.0764),
    "N19": (51.5644, -0.1393), "W1": (51.5155, -0.1445), "W2": (51.5156, -0.1715),
    "W6": (51.4927, -0.2241), "W11": (51.5164, -0.1967), "W12": (51.5055, -0.2243),
}


def fetch_amenities_osm(area_code: str, radius_km: float = 1.0) -> Dict:
    """Fetch amenities from OpenStreetMap."""
    coords = AREA_COORDS.get(area_code)
    if not coords:
        return {}

    lat, lon = coords
    radius_m = radius_km * 1000

    query = f"""
    [out:json];
    (
      node["amenity"~"cafe|restaurant|pub|bar"](around:{radius_m},{lat},{lon});
      node["amenity"~"supermarket|convenience"](around:{radius_m},{lat},{lon});
      node["leisure"~"gym|fitness_centre|park"](around:{radius_m},{lat},{lon});
    );
    out count;
    """

    try:
        response = requests.post(OVERPASS_API, data={"data": query}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("elements", []))

            # Calculate density score (0-100)
            if count > 100:
                density_score = 95
            elif count > 50:
                density_score = 80
            elif count > 25:
                density_score = 65
            elif count > 10:
                density_score = 50
            else:
                density_score = 30

            return {
                "area_code": area_code,
                "amenity_count": count,
                "density_score": density_score,
                "cafes_restaurants": count // 3,  # Rough estimate
                "supermarkets": max(1, count // 20),
                "gyms": max(1, count // 30),
                "parks": max(1, count // 25),
                "timestamp": datetime.now().isoformat(),
                "data_source": "osm_amenities"
            }

        return {}
    except Exception as e:
        print(f"[ERROR] Failed to fetch amenities: {e}")
        return {}


def fetch_amenities_data(area_code: str, use_cache: bool = True) -> Optional[Dict]:
    """Fetch amenities data (cached)."""
    if use_cache:
        cached = read_cache("amenities_data", area_code)
        if cached:
            print(f"[CACHE] Using cached amenities data for {area_code}")
            return cached

    print(f"[API] Fetching amenities data for {area_code}")
    data = fetch_amenities_osm(area_code)

    if data and use_cache:
        write_cache("amenities_data", area_code, data)

    return data


if __name__ == "__main__":
    print("="*80)
    print("Amenities Mapper - Test Mode")
    print("="*80)
    print("")

    print("Test: Amenities for W11 (Notting Hill)")
    data = fetch_amenities_data("W11")
    if data:
        print(f"  Total amenities: {data['amenity_count']}")
        print(f"  Density score: {data['density_score']}/100")
        print(f"  Cafes/Restaurants: {data['cafes_restaurants']}")
        print(f"  Supermarkets: {data['supermarkets']}")
    print("")
    print("="*80)
