#!/usr/bin/env python3
"""
ScanSan Property Intelligence API Client
Fetches property and area intelligence data from ScanSan API.
Directive: directives/scansan_property_intelligence.md
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCANSAN_API_KEY = os.getenv("SCANSAN_API_KEY")
SCANSAN_BASE_URL = os.getenv("SCANSAN_BASE_URL", "https://api.scansan.com/v1")

# Rate limiting
RATE_LIMIT_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponential backoff multiplier


def fetch_area_intelligence(
    area_codes: List[str],
    metrics_requested: Optional[List[str]] = None,
    cache_dir: str = ".tmp"
) -> Dict:
    """
    Fetch ScanSan intelligence for list of area codes.

    Args:
        area_codes: List of UK postcode districts (e.g., ["SW1A", "E1"])
        metrics_requested: List of specific metrics to fetch (default: all)
        cache_dir: Directory to store cache files

    Returns:
        Dictionary with area codes as keys and intelligence data as values
    """
    if not SCANSAN_API_KEY:
        raise ValueError("SCANSAN_API_KEY not found in environment variables")

    if metrics_requested is None:
        metrics_requested = [
            "affordability_score",
            "risk_score",
            "investment_quality",
            "demand_index",
            "price_trends",
            "yield_estimates"
        ]

    results = {}
    timestamp = datetime.now().isoformat()

    for area_code in area_codes:
        area_code = area_code.strip().upper()

        # Validate UK postcode format (basic)
        if not area_code or len(area_code) < 2:
            print(f"[WARNING] Invalid area code: {area_code}, skipping")
            results[area_code] = None
            continue

        # Fetch with retry logic
        data = fetch_with_retry(area_code, metrics_requested)

        if data:
            data["area_code"] = area_code
            data["timestamp"] = timestamp
            results[area_code] = data
        else:
            results[area_code] = None

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    # Cache results
    cache_file = os.path.join(cache_dir, f"scansan_cache_{int(time.time())}.json")
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[INFO] Cached results to {cache_file}")

    return results


def fetch_with_retry(area_code: str, metrics: List[str]) -> Optional[Dict]:
    """Fetch data with exponential backoff retry logic."""
    headers = {
        "Authorization": f"Bearer {SCANSAN_API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{SCANSAN_BASE_URL}/area/{area_code}"
    params = {"metrics": ",".join(metrics)}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"[WARNING] Area code {area_code} not found in ScanSan database")
                return None
            elif response.status_code == 429:
                # Rate limited
                retry_after = int(response.headers.get("Retry-After", 60))
                print(f"[WARNING] Rate limited. Retrying after {retry_after}s")
                time.sleep(retry_after)
            else:
                print(f"[ERROR] API error {response.status_code}: {response.text}")
                if attempt < MAX_RETRIES - 1:
                    backoff = RETRY_BACKOFF ** attempt
                    print(f"[INFO] Retrying in {backoff}s...")
                    time.sleep(backoff)

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            if attempt < MAX_RETRIES - 1:
                backoff = RETRY_BACKOFF ** attempt
                print(f"[INFO] Retrying in {backoff}s...")
                time.sleep(backoff)

    print(f"[ERROR] Failed to fetch data for {area_code} after {MAX_RETRIES} attempts")
    return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scansan_api.py <area_code1> [area_code2] ...")
        sys.exit(1)

    area_codes = sys.argv[1:]
    results = fetch_area_intelligence(area_codes)

    # Pretty print results
    print("\n" + "="*80)
    print("SCANSAN INTELLIGENCE RESULTS")
    print("="*80)
    print(json.dumps(results, indent=2))
