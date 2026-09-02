# Amenities Mapper Directive

## Goal
Give each candidate district an amenity density score, for the scoring engine
to weight.

## Inputs
- **area_code**: one of the 30 covered postcode districts (e.g. `E1`)
- **radius_km**: search radius around the district centroid (default 1.0)
- **use_cache**: read from `.tmp/` if a cached result is still valid (30 days)

## Execution Tool
Use `tools/fetch_amenities.py`

## Process
1. Look the district up in `AREA_COORDS` (fixed centroids).
2. Ask the OpenStreetMap Overpass API for a **count** of nodes within the
   radius matching `amenity=cafe|restaurant|pub|bar`,
   `amenity=supermarket|convenience` or `leisure=gym|fitness_centre|park`.
3. Band the count into a density score: >100 → 95, >50 → 80, >25 → 65,
   >10 → 50, otherwise 30.
4. Cache the result in `.tmp/` for 30 days.

There is no persona filter, no Google Places lookup and no per-venue detail;
the query returns one number and everything else is derived from it.

## Outputs
```json
{
  "area_code": "E1",
  "amenity_count": 137,
  "density_score": 95,
  "cafes_restaurants": 45,
  "supermarkets": 6,
  "gyms": 4,
  "parks": 5,
  "data_source": "osm_amenities"
}
```
`cafes_restaurants`, `supermarkets`, `gyms` and `parks` are **not measured** —
they are the total divided by 3, 20, 30 and 25 respectively. Do not present
them as counts of anything. The scorer reads only `density_score`.

## Edge Cases & Learnings
- **Overpass is slow and rate-limited**: the call has a 15 second timeout and
  frequently returns 504 under load. On any failure the fetcher returns `{}`
  and the scorer falls back to 50.
- **A cached failure is not stored**, but a cached success lasts 30 days.
- **`out count;` reply shape**: Overpass answers a count query with a single
  synthetic element whose `tags.total` holds the number; the fetcher reads that
  field, and falls back to `len(elements)` if it is given a node list instead.
