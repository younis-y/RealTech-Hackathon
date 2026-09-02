# Crime Data Fetcher Directive

## Goal
Give each candidate district a safety score from reported street-level crime,
for the scoring engine to weight.

This is one of the two factors that come from a live API on every run.

## Inputs
- **area_code**: one of the 30 covered postcode districts (e.g. `E1`)
- **use_cache**: read from `.tmp/` if a cached result is still valid (30 days)

## Execution Tool
Use `tools/fetch_crime_data.py`

## Process
1. Look the district up in `AREA_COORDS` (fixed centroids; unknown codes return
   `None`).
2. Call `https://data.police.uk/api/crimes-street/all-crime?lat=&lng=`. No key
   is needed. The endpoint returns **the most recent single month** the Home
   Office has published, for the streets around that point.
3. Count the crimes and bucket the categories the API reports into six coarse
   groups.
4. Band the total into a safety score: <30 → 90, <60 → 75, <90 → 60,
   <120 → 45, otherwise 30. These thresholds are hand-set guesses, not
   calibrated against any London-wide distribution.
5. Cache the result in `.tmp/` for 30 days.

## Outputs
```json
{
  "area_code": "E1",
  "lat": 51.5154,
  "lon": -0.0616,
  "time_period_months": 1,
  "total_crimes": 84,
  "safety_score": 60,
  "crime_breakdown": {"violent-crime": 31, "burglary": 4, "theft": 22,
                      "vehicle-crime": 3, "antisocial-behaviour": 18, "other": 6},
  "data_source": "uk_police_data"
}
```
The scorer reads only `safety_score`.

Two fields in the returned dict are placeholders and should not be used:
`trend` is always the string `"stable"` (no historical comparison is made) and
`percentile_vs_london` is just a copy of `safety_score`. `crimes_per_1000_people`
is the raw count — no population figure is involved.

## Edge Cases & Learnings
- **Rate limits**: data.police.uk asks for reasonable use. The fetcher does not
  throttle, so a large batch is on the caller.
- **Lag**: the published data runs one to two months behind, and the most
  recent month can be incomplete.
- **Anonymised locations**: the API snaps each crime to a nearby street point,
  so counts are indicative of an area, not a street.
- **A failed call** returns `None`, and the scorer falls back to 50.
- **Not normalised by population**: a busy district with many visitors will look
  worse than a quiet residential one of the same size. Comparing districts on
  this score is the weakest link in the ranking.
