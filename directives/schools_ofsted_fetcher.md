# Schools & Ofsted Data Directive

## Goal
Give each candidate district a school quality score, so the parent persona has
something to weight.

> **The Ofsted ratings are invented.** `tools/fetch_schools.py` finds real
> school locations, then assigns each one a random rating. Nothing in this
> repository reads a real inspection result. See the provenance table in the
> root README before using any of these numbers.

## Inputs
- **area_code**: one of the 30 covered postcode districts (e.g. `E1`)
- **radius_km**: search radius around the district centroid (default 1.5)
- **use_cache**: read from `.tmp/` if a cached result is still valid (90 days)

## Execution Tool
Use `tools/fetch_schools.py`

## Process
1. Look the district up in `AREA_COORDS` (fixed centroids; unknown codes return
   an empty result).
2. Query the OpenStreetMap Overpass API for `amenity=school` nodes and ways
   within the radius, keeping at most 10.
3. Label each school `primary` if its name contains "primary", otherwise
   `secondary`. That is the whole of the type classification.
4. **Invent an Ofsted rating** per school with
   `random.choices(["outstanding","good","requires_improvement","inadequate"],
   weights=[15,60,20,5])`, map it to 95/75/55/30 and jitter by ±5.
5. Average the scores. If no schools were found, return a neutral 50.
6. Cache the result in `.tmp/` for 90 days.

## Outputs
```json
{
  "school_count": 7,
  "avg_quality_score": 76,
  "primary_schools": 3,
  "secondary_schools": 4,
  "top_schools": [{"name": "Example School", "score": 95, "rating": "outstanding"}],
  "ofsted_ratings": {"outstanding": 1, "good": 4, "requires_improvement": 2, "inadequate": 0}
}
```
The scorer reads only `avg_quality_score`.

## Edge Cases & Learnings
- **Overpass is slow and rate-limited**: the call has a 15 second timeout and
  frequently returns 504 under load. On any failure the fetcher returns an
  empty result, `school_count` is 0 and the scorer falls back to 50.
- **A cached empty result is sticky**: a failed fetch caches `school_count: 0`
  for 90 days. Delete the file in `.tmp/` to retry.
- **The ratings are not stable between runs** unless the result is cached,
  because they are drawn at random each time.
- **To make this real**: replace step 4 with the Get Information About Schools
  (GIAS) feed, which publishes URNs and inspection outcomes.
