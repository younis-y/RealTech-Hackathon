"""
INSPIRE Index Polygons Scraper - London Boroughs
Downloads GML files for London property boundaries from HM Land Registry.

Since the main page requires JavaScript, we use known borough data.
Source: https://use-land-property-data.service.gov.uk/datasets/inspire/download
Target: All London Borough boundary files (~33 files)
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

# Configuration
BASE_URL = "https://use-land-property-data.service.gov.uk"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "geo", "london_polygons")

# Polite delay between downloads (seconds)
DOWNLOAD_DELAY = 1.0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Complete list of London boroughs with their Land Registry area codes
# Format: (Display Name, URL slug / file name pattern)
LONDON_BOROUGHS = [
    ("City of London", "city-of-london"),
    ("City of Westminster", "city-of-westminster"),
    ("London Borough of Barking and Dagenham", "barking-and-dagenham"),
    ("London Borough of Barnet", "barnet"),
    ("London Borough of Bexley", "bexley"),
    ("London Borough of Brent", "brent"),
    ("London Borough of Bromley", "bromley"),
    ("London Borough of Camden", "camden"),
    ("London Borough of Croydon", "croydon"),
    ("London Borough of Ealing", "ealing"),
    ("London Borough of Enfield", "enfield"),
    ("London Borough of Greenwich", "greenwich"),
    ("London Borough of Hackney", "hackney"),
    ("London Borough of Hammersmith and Fulham", "hammersmith-and-fulham"),
    ("London Borough of Haringey", "haringey"),
    ("London Borough of Harrow", "harrow"),
    ("London Borough of Havering", "havering"),
    ("London Borough of Hillingdon", "hillingdon"),
    ("London Borough of Hounslow", "hounslow"),
    ("London Borough of Islington", "islington"),
    ("London Borough of Lambeth", "lambeth"),
    ("London Borough of Lewisham", "lewisham"),
    ("London Borough of Merton", "merton"),
    ("London Borough of Newham", "newham"),
    ("London Borough of Redbridge", "redbridge"),
    ("London Borough of Richmond upon Thames", "richmond-upon-thames"),
    ("London Borough of Southwark", "southwark"),
    ("London Borough of Sutton", "sutton"),
    ("London Borough of Tower Hamlets", "tower-hamlets"),
    ("London Borough of Waltham Forest", "waltham-forest"),
    ("London Borough of Wandsworth", "wandsworth"),
    ("Royal Borough of Greenwich", "royal-borough-of-greenwich"),
    ("Royal Borough of Kensington and Chelsea", "kensington-and-chelsea"),
    ("Royal Borough of Kingston upon Thames", "kingston-upon-thames"),
]


def get_download_links() -> List[Dict[str, str]]:
    """
    Generate download links for all London boroughs.
    Uses known URL patterns from the INSPIRE download service.
    """
    links = []
    
    for name, slug in LONDON_BOROUGHS:
        # The download URL pattern (may need adjustment based on actual site)
        url = f"{BASE_URL}/datasets/inspire/{slug}/download"
        links.append({
            "name": name,
            "slug": slug,
            "url": url
        })
    
    return links


def download_gml(url: str, borough_name: str) -> bool:
    """
    Download the GML file for a borough.
    The URL might be a landing page that redirects to the actual file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create safe filename
    safe_name = re.sub(r"[^\w\s-]", "", borough_name).strip()
    safe_name = re.sub(r"\s+", "_", safe_name)
    filename = f"{safe_name}.gml"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        print(f"  Downloading: {borough_name}")
        
        # First request - might be a landing page or direct download
        response = requests.get(url, headers=HEADERS, timeout=60, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"    [ERROR] Status {response.status_code}")
            return False
        
        content_type = response.headers.get("content-type", "")
        
        # If we got HTML, we need to find the actual download link
        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for the direct GML download link
            gml_link = None
            for a in soup.find_all("a", href=True):
                if ".gml" in a["href"].lower() or "download" in a.get_text(strip=True).lower():
                    gml_link = a["href"]
                    if gml_link.startswith("/"):
                        gml_link = BASE_URL + gml_link
                    break
            
            if gml_link:
                # Download the actual GML file
                response = requests.get(gml_link, headers=HEADERS, timeout=120, stream=True)
                if response.status_code != 200:
                    print(f"    [ERROR] GML download failed: {response.status_code}")
                    return False
        
        # Save the file
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"    ✓ Saved: {filename} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False


def main():
    """Main scraper execution."""
    print("=" * 80)
    print("INSPIRE Index Polygons Scraper - London Boroughs")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Get download links from hardcoded list
    print("\nPreparing download list for London boroughs...")
    london_links = get_download_links()
    
    print(f"\nFound {len(london_links)} London boroughs in configuration:")
    for link in london_links:
        print(f"  • {link['name']}")
    
    print()
    
    # Download each borough
    downloaded = []
    failed = []
    
    for i, link in enumerate(london_links, 1):
        print(f"\n[{i}/{len(london_links)}] {link['name']}")
        
        if download_gml(link["url"], link["name"]):
            downloaded.append(link["name"])
        else:
            failed.append(link["name"])
        
        # Polite delay
        if i < len(london_links):
            time.sleep(DOWNLOAD_DELAY)
    
    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"  ✓ Downloaded: {len(downloaded)}/{len(london_links)}")
    
    if failed:
        print(f"  ✗ Failed: {len(failed)}")
        for name in failed:
            print(f"      - {name}")
    
    print(f"\n  Files saved to: {OUTPUT_DIR}")
    print()
    
    return downloaded


if __name__ == "__main__":
    main()
