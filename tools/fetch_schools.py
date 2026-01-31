#!/usr/bin/env python3
"""
Schools Data Fetcher
Fetches school ratings using OpenStreetMap + mock Ofsted ratings.
Architecture SOP: architecture/01_data_pipeline.md (Stage 3)
Data Schema: gemini.md (#5 Schools Data Response Schema)
"""

import os
import sys
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

# Load environment variables
load_dotenv()

# Configuration
OVERPASS_API = "https://overpass-api.de/api/interpreter"

# Area coordinates
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


def fetch_schools_osm(area_code: str, radius_km: float = 1.5) -> List[Dict]:
    """Fetch schools from OpenStreetMap."""
    coords = AREA_COORDS.get(area_code)
    if not coords:
        return []

    lat, lon = coords
    radius_m = radius_km * 1000

    # Overpass query for schools
    query = f"""
    [out:json];
    (
      node["amenity"="school"](around:{radius_m},{lat},{lon});
      way["amenity"="school"](around:{radius_m},{lat},{lon});
    );
    out body;
    """

    try:
        response = requests.post(OVERPASS_API, data={"data": query}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            schools = []

            for element in data.get("elements", [])[:10]:  # Limit to 10 schools
                tags = element.get("tags", {})
                schools.append({
                    "name": tags.get("name", "Unnamed School"),
                    "type": "primary" if "primary" in tags.get("name", "").lower() else "secondary",
                    "lat": element.get("lat", coords[0]),
                    "lon": element.get("lon", coords[1])
                })

            return schools

        return []
    except Exception as e:
        print(f"[ERROR] Failed to fetch schools from OSM: {e}")
        return []


def generate_mock_school_ratings(schools: List[Dict]) -> Dict:
    """Generate mock Ofsted ratings for schools."""
    if not schools:
        # No schools found, return neutral scores
        return {
            "school_count": 0,
            "avg_quality_score": 50,
            "primary_schools": 0,
            "secondary_schools": 0,
            "top_schools": [],
            "ofsted_ratings": {"outstanding": 0, "good": 0, "requires_improvement": 0, "inadequate": 0}
        }

    # Generate ratings
    ratings = {"outstanding": 0, "good": 0, "requires_improvement": 0, "inadequate": 0}
    school_scores = []

    for school in schools:
        # Random Ofsted rating (weighted toward good/outstanding)
        rating_choice = random.choices(
            ["outstanding", "good", "requires_improvement", "inadequate"],
            weights=[15, 60, 20, 5]
        )[0]

        ratings[rating_choice] += 1

        # Convert to score
        score_map = {"outstanding": 95, "good": 75, "requires_improvement": 55, "inadequate": 30}
        score = score_map[rating_choice] + random.randint(-5, 5)

        school["ofsted_rating"] = rating_choice
        school["quality_score"] = score
        school_scores.append(score)

    # Calculate averages
    avg_score = sum(school_scores) / len(school_scores) if school_scores else 50
    primary_count = sum(1 for s in schools if s["type"] == "primary")
    secondary_count = len(schools) - primary_count

    # Top 3 schools
    top_schools = sorted(schools, key=lambda s: s["quality_score"], reverse=True)[:3]

    return {
        "school_count": len(schools),
        "avg_quality_score": int(avg_score),
        "primary_schools": primary_count,
        "secondary_schools": secondary_count,
        "top_schools": [{"name": s["name"], "score": s["quality_score"], "rating": s["ofsted_rating"]} for s in top_schools],
        "ofsted_ratings": ratings
    }


def fetch_schools_data(area_code: str, use_cache: bool = True) -> Optional[Dict]:
    """Fetch schools data (cached)."""
    # Check cache
    if use_cache:
        cached = read_cache("schools_data", area_code)
        if cached:
            print(f"[CACHE] Using cached schools data for {area_code}")
            return cached

    # Fetch from OSM
    print(f"[API] Fetching schools data for {area_code}")
    schools = fetch_schools_osm(area_code)
    ratings_data = generate_mock_school_ratings(schools)

    data = {
        "area_code": area_code,
        **ratings_data,
        "timestamp": datetime.now().isoformat(),
        "data_source": "osm_schools_mock_ratings"
    }

    # Cache
    if use_cache:
        write_cache("schools_data", area_code, data)

    return data


if __name__ == "__main__":
    print("="*80)
    print("Schools Data Fetcher - Test Mode")
    print("="*80)
    print("")

    print("Test: Schools data for N1 (Islington)")
    data = fetch_schools_data("N1")
    if data:
        print(f"  Schools found: {data['school_count']}")
        print(f"  Average quality: {data['avg_quality_score']}/100")
        print(f"  Primary: {data['primary_schools']}, Secondary: {data['secondary_schools']}")
        print(f"  Ofsted ratings: {data['ofsted_ratings']}")
        if data['top_schools']:
            print(f"  Top school: {data['top_schools'][0]['name']} ({data['top_schools'][0]['score']}/100)")
    print("")
    print("="*80)
