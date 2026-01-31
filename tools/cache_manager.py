#!/usr/bin/env python3
"""
Cache Manager - Atomic tool for caching API responses
Part of Layer 3: Tools (deterministic operations)
Architecture SOP: architecture/00_master_system.md
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


CACHE_DIR = ".tmp"
CACHE_VALIDITY = {
    "scansan_property": 24,      # hours
    "scansan_trends": 168,        # 7 days
    "tfl_commute": 168,           # 7 days
    "crime": 720,                 # 30 days
    "schools": 2160,              # 90 days
    "amenities": 720,             # 30 days
    "video_url": float('inf'),    # never expire
}


def get_cache_path(cache_type: str, key: str) -> Path:
    """
    Generate cache file path.

    Args:
        cache_type: Type of cache (e.g., "scansan_property")
        key: Unique key (e.g., area code, lat_lon)

    Returns:
        Path object for cache file
    """
    cache_dir = Path(CACHE_DIR)
    cache_dir.mkdir(exist_ok=True)

    # Sanitize key for filename
    safe_key = key.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filename = f"{cache_type}_{safe_key}.json"

    return cache_dir / filename


def read_cache(cache_type: str, key: str, max_age_hours: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Read data from cache if it exists and is fresh.

    Args:
        cache_type: Type of cache (e.g., "scansan_property")
        key: Unique key
        max_age_hours: Maximum age in hours (overrides default for cache_type)

    Returns:
        Cached data if fresh, None otherwise
    """
    cache_path = get_cache_path(cache_type, key)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)

        # Check freshness
        cached_timestamp = cached_data.get("_cache_timestamp")
        if not cached_timestamp:
            print(f"[WARNING] Cache file {cache_path.name} missing timestamp, invalidating")
            return None

        # Determine max age
        if max_age_hours is None:
            max_age_hours = CACHE_VALIDITY.get(cache_type, 24)  # default 24 hours

        # Check if cache is still valid
        cached_time = datetime.fromisoformat(cached_timestamp)
        age = datetime.now() - cached_time
        max_age = timedelta(hours=max_age_hours)

        if age > max_age:
            print(f"[INFO] Cache expired for {cache_path.name} (age: {age.total_seconds() / 3600:.1f}h)")
            return None

        print(f"[INFO] Cache hit: {cache_path.name} (age: {age.total_seconds() / 3600:.1f}h)")
        return cached_data.get("data")

    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] Failed to read cache {cache_path.name}: {e}")
        return None


def write_cache(cache_type: str, key: str, data: Dict[str, Any]) -> bool:
    """
    Write data to cache.

    Args:
        cache_type: Type of cache
        key: Unique key
        data: Data to cache

    Returns:
        True if successful, False otherwise
    """
    cache_path = get_cache_path(cache_type, key)

    try:
        cache_data = {
            "_cache_timestamp": datetime.now().isoformat(),
            "_cache_type": cache_type,
            "_cache_key": key,
            "data": data
        }

        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"[INFO] Cached data to {cache_path.name}")
        return True

    except IOError as e:
        print(f"[ERROR] Failed to write cache {cache_path.name}: {e}")
        return False


def invalidate_cache(cache_type: str, key: str) -> bool:
    """
    Invalidate (delete) a specific cache entry.

    Args:
        cache_type: Type of cache
        key: Unique key

    Returns:
        True if deleted, False if not found or error
    """
    cache_path = get_cache_path(cache_type, key)

    try:
        if cache_path.exists():
            cache_path.unlink()
            print(f"[INFO] Invalidated cache: {cache_path.name}")
            return True
        else:
            print(f"[INFO] Cache not found: {cache_path.name}")
            return False
    except OSError as e:
        print(f"[ERROR] Failed to invalidate cache {cache_path.name}: {e}")
        return False


def clean_old_cache(max_age_days: int = 90) -> int:
    """
    Remove cache files older than max_age_days.

    Args:
        max_age_days: Maximum age in days

    Returns:
        Number of files deleted
    """
    cache_dir = Path(CACHE_DIR)
    if not cache_dir.exists():
        return 0

    count_deleted = 0
    max_age = timedelta(days=max_age_days)
    now = datetime.now()

    for cache_file in cache_dir.glob("*.json"):
        try:
            # Read timestamp from file
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)

            cached_timestamp = cached_data.get("_cache_timestamp")
            if cached_timestamp:
                cached_time = datetime.fromisoformat(cached_timestamp)
                age = now - cached_time

                if age > max_age:
                    cache_file.unlink()
                    print(f"[INFO] Deleted old cache: {cache_file.name} (age: {age.days} days)")
                    count_deleted += 1

        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"[WARNING] Error processing {cache_file.name}: {e}")

    print(f"[INFO] Cleaned {count_deleted} old cache files (> {max_age_days} days)")
    return count_deleted


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about current cache.

    Returns:
        Dictionary with cache statistics
    """
    cache_dir = Path(CACHE_DIR)
    if not cache_dir.exists():
        return {"total_files": 0, "total_size_mb": 0}

    cache_files = list(cache_dir.glob("*.json"))
    total_size = sum(f.stat().st_size for f in cache_files)

    cache_types = {}
    for cache_file in cache_files:
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            cache_type = cached_data.get("_cache_type", "unknown")
            cache_types[cache_type] = cache_types.get(cache_type, 0) + 1
        except:
            pass

    return {
        "total_files": len(cache_files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "by_type": cache_types
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Cache Manager - Atomic caching tool")
        print("")
        print("Usage:")
        print("  python cache_manager.py stats              - Show cache statistics")
        print("  python cache_manager.py clean [days]       - Clean cache older than [days] (default 90)")
        print("  python cache_manager.py read <type> <key>  - Read cache entry")
        print("")
        print("Example:")
        print("  python cache_manager.py stats")
        print("  python cache_manager.py clean 30")
        print("  python cache_manager.py read scansan_property SW1A")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        stats = get_cache_stats()
        print(json.dumps(stats, indent=2))

    elif command == "clean":
        max_age_days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        deleted = clean_old_cache(max_age_days)
        print(f"Deleted {deleted} files")

    elif command == "read":
        if len(sys.argv) < 4:
            print("Usage: python cache_manager.py read <type> <key>")
            sys.exit(1)
        cache_type = sys.argv[2]
        key = sys.argv[3]
        data = read_cache(cache_type, key)
        if data:
            print(json.dumps(data, indent=2))
        else:
            print("Cache miss or expired")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
