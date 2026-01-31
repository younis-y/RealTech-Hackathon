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

load_dotenv()

# Load environment variables
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
    
    results = {"timestamp": datetime.now().isoformat()}
    
    for area_code in area_codes:
        area_code = area_code.strip().upper()
        
        # Validate UK postcode format (basic)
        if not area_code or len(area_code) < 2:
            print(f"WARNING: Invalid area code '{area_code}', skipping")
            results[area_code] = None
            continue
        
        # Fetch with retry logic
        data = fetch_with_retry(area_code, metrics_requested)
        if data:
            data["area_code"] = area_code
            data["timestamp"] = results["timestamp"]
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
    print(f"INFO: Cached results to {cache_file}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scansan_api.py <area_code1> <area_code2> ...")
        sys.exit(1)
    
    area_codes = sys.argv[1:]
    results = fetch_area_intelligence(area_codes)
    
    print("=" * 80)
    print("SCANSAN INTELLIGENCE RESULTS")
    print("=" * 80)
    print(json.dumps(results, indent=2))
