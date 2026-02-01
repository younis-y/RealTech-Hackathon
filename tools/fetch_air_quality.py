#!/usr/bin/env python3
"""
TfL Air Quality Fetcher
Fetches air quality data for London areas using Transport for London API.
"""

import os
import sys
import requests
import json
from datetime import datetime
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

# Load environment variables
load_dotenv()

# Configuration
TFL_APP_KEY = os.getenv("TFL_APP_KEY")
TFL_BASE_URL = "https://api.tfl.gov.uk"

def fetch_air_quality(use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """
    Fetch current air quality data for London.
    
    Args:
        use_cache: Whether to use cached data
        
    Returns:
        Dict containing air quality data or None if failed
    """
    cache_key = "london_air_quality"
    
    if use_cache:
        cached = read_cache("tfl_air_quality", cache_key)
        if cached:
            print(f"[CACHE] Using cached air quality data")
            return cached

    if not TFL_APP_KEY:
        print("[WARNING] TFL_APP_KEY not set, cannot fetch real air quality data")
        # Return mock data if no key
        return {
            "current_forecast": [
                {
                    "forecastType": "Current",
                    "forecastID": "mock_1",
                    "publishedDate": datetime.now().isoformat(),
                    "fromDate": datetime.now().isoformat(),
                    "toDate": datetime.now().isoformat(),
                    "forecastBand": "Low",
                    "forecastSummary": "Low air pollution mock data",
                    "nO2Band": "Low",
                    "o3Band": "Low",
                    "pM10Band": "Low",
                    "pM25Band": "Low",
                    "sO2Band": "Low",
                    "forecastText": "Air pollution is expected to remain low."
                }
            ],
            "data_source": "mock"
        }

    try:
        url = f"{TFL_BASE_URL}/AirQuality"
        params = {}
        if TFL_APP_KEY:
            params["app_key"] = TFL_APP_KEY
            
        print(f"[API] Fetching real Air Quality data from TfL")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = {
                "raw_data": data,
                "current_forecast": data.get("currentForecast", []),
                "timestamp": datetime.now().isoformat(),
                "data_source": "tfl_api"
            }
            
            if use_cache:
                write_cache("tfl_air_quality", cache_key, result)
                
            return result
        else:
            print(f"[WARN] TfL AirQuality API error {response.status_code}. Using mock data.")
            # Fallback to mock
            return {
                "current_forecast": [
                    {
                        "forecastType": "Current",
                        "forecastID": "mock_fallback",
                        "publishedDate": datetime.now().isoformat(),
                        "fromDate": datetime.now().isoformat(),
                        "toDate": datetime.now().isoformat(),
                        "forecastBand": "Low",
                        "forecastSummary": "Low air pollution (Mock Data)",
                        "nO2Band": "Low",
                        "o3Band": "Low",
                        "pM10Band": "Low",
                        "pM25Band": "Low",
                        "sO2Band": "Low",
                        "forecastText": "Air pollution is expected to remain low."
                    }
                ],
                "data_source": "mock_fallback"
            }
            
    except Exception as e:
        print(f"[WARN] Failed to fetch Air Quality data: {e}. Using mock data.")
        return {
            "current_forecast": [],
            "data_source": "mock_error"
        }

if __name__ == "__main__":
    print("Fetching Air Quality...")
    aq = fetch_air_quality(use_cache=False)
    if aq:
        print(json.dumps(aq.get("current_forecast", []), indent=2))
