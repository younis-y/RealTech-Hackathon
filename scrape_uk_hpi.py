#!/usr/bin/env python3
"""
UK House Price Index (UK HPI) Data Scraper
Scrapes GOV.UK collection pages to download official house price data.

Target: UK HPI Full File CSV (cumulative data covering all previous dates)
Source: https://www.gov.uk/government/collections/uk-house-price-index-reports-*
"""

import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Configuration
BASE_URL = "https://www.gov.uk"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")

COLLECTION_URLS = [
    "https://www.gov.uk/government/collections/uk-house-price-index-reports-2025",
    "https://www.gov.uk/government/collections/uk-house-price-index-reports-2024",
    "https://www.gov.uk/government/collections/uk-house-price-index-reports-2023",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Domus-Research-Bot/1.0"
}


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """Fetch and parse a webpage."""
    try:
        print(f"  Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        else:
            print(f"  [ERROR] Status {response.status_code}")
            return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


def get_monthly_report_links(collection_url: str) -> List[Tuple[str, str]]:
    """
    Parse a collection page to extract monthly report links.
    Returns list of (month_name, url) tuples.
    """
    soup = fetch_page(collection_url)
    if not soup:
        return []
    
    reports = []
    # Look for links containing "UK House Price Index:"
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        if "UK House Price Index:" in text and "data downloads" not in text.lower():
            href = link["href"]
            if href.startswith("/"):
                href = BASE_URL + href
            # Extract month/year from text
            reports.append((text, href))
    
    print(f"  Found {len(reports)} monthly reports")
    return reports


def get_download_page_link(report_url: str) -> Optional[str]:
    """
    From a monthly report page, find the "data downloads" link.
    """
    soup = fetch_page(report_url)
    if not soup:
        return None
    
    # Look for "data downloads" link
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True).lower()
        if "data downloads" in text:
            href = link["href"]
            if href.startswith("/"):
                href = BASE_URL + href
            return href
    
    return None


def get_csv_download_links(download_page_url: str) -> List[Dict[str, str]]:
    """
    From a download page, extract CSV file links.
    Returns list of {name, url, size} dicts.
    """
    soup = fetch_page(download_page_url)
    if not soup:
        return []
    
    csvs = []
    
    # Look for CSV links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".csv" in href.lower():
            text = link.get_text(strip=True)
            if href.startswith("/"):
                href = BASE_URL + href
            elif not href.startswith("http"):
                continue
            
            # Try to get file size
            size = ""
            parent = link.find_parent()
            if parent:
                size_match = re.search(r"(\d+\.?\d*\s*[KMGT]B)", parent.get_text())
                if size_match:
                    size = size_match.group(1)
            
            csvs.append({
                "name": text or href.split("/")[-1],
                "url": href,
                "size": size
            })
    
    return csvs


def download_file(url: str, filename: str) -> bool:
    """Download a file to the output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        print(f"  Downloading: {url}")
        response = requests.get(url, headers=HEADERS, stream=True, timeout=60)
        
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        print(f"\r  Progress: {pct:.1f}%", end="", flush=True)
            
            print(f"\n  ✓ Saved: {filepath} ({os.path.getsize(filepath):,} bytes)")
            return True
        else:
            print(f"  [ERROR] Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        return False


def find_full_file_csv(csvs: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """Find the UK HPI full file CSV (priority) or average price CSV."""
    for csv in csvs:
        name_lower = csv["name"].lower()
        if "full file" in name_lower or "full-file" in name_lower:
            return csv
    
    # Fallback to average price
    for csv in csvs:
        name_lower = csv["name"].lower()
        if "average price" in name_lower or "average-price" in name_lower:
            return csv
    
    # Return first CSV if available
    return csvs[0] if csvs else None


def main():
    """Main scraper execution."""
    print("=" * 80)
    print("UK House Price Index Data Scraper")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    downloaded_files = []
    
    # We only need the most recent full file (it contains all historical data)
    # Start with 2025, then 2024, then 2023
    
    for collection_url in COLLECTION_URLS:
        year = collection_url.split("-")[-1]
        print(f"\n[{year}] Scanning collection...")
        
        reports = get_monthly_report_links(collection_url)
        
        if not reports:
            print(f"  No reports found for {year}")
            continue
        
        # Get the first (most recent) report
        report_name, report_url = reports[0]
        print(f"\n  Most recent: {report_name}")
        
        # Get download page
        download_page = get_download_page_link(report_url)
        if not download_page:
            print("  [WARN] No download page found, trying next...")
            continue
        
        # Get CSV links
        csvs = get_csv_download_links(download_page)
        print(f"  Found {len(csvs)} CSV files")
        
        for csv in csvs:
            print(f"    - {csv['name']} ({csv['size']})")
        
        # Find and download the full file
        target_csv = find_full_file_csv(csvs)
        
        if target_csv:
            print(f"\n  Target: {target_csv['name']}")
            
            # Generate filename
            safe_name = re.sub(r"[^\w\s-]", "", target_csv["name"]).strip()
            safe_name = re.sub(r"\s+", "_", safe_name)
            filename = f"uk_hpi_{year}_{safe_name}.csv"
            
            if download_file(target_csv["url"], filename):
                downloaded_files.append({
                    "year": year,
                    "name": target_csv["name"],
                    "path": os.path.join(OUTPUT_DIR, filename)
                })
                
                # If we got a "full file", we don't need older years
                if "full" in target_csv["name"].lower():
                    print("\n  [INFO] Full file downloaded - contains all historical data")
                    break
        else:
            print("  [WARN] No suitable CSV found")
    
    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    
    if downloaded_files:
        for f in downloaded_files:
            print(f"  ✓ {f['year']}: {f['name']}")
            print(f"    Path: {f['path']}")
    else:
        print("  No files downloaded")
    
    print()
    return downloaded_files


if __name__ == "__main__":
    main()
