# TfL Commute Calculator Directive

## Goal
Give each candidate district a commute time to one of the four covered
destinations (UCL, KCL, LSE, Imperial), for the scoring engine to weight.

> **Synthetic unless keyed.** `tools/fetch_tfl_commute.py` sets
> `USE_MOCK_DATA = not TFL_APP_KEY`. With no key — the documented default — the
> journey time is haversine distance between two fixed centroids at an assumed
> 20 km/h, plus a random offset of −5 to +15 minutes. The line name in
> `route_summary` is drawn at random from a list of seven and means nothing.

## Inputs
- **from_area**: one of the 30 covered postcode districts (e.g. `E1`)
- **to_location**: `UCL` | `KCL` | `LSE` | `Imperial`
- **use_cache**: read from `.tmp/` if a cached result is still valid (7 days)

## Execution Tool
Use `tools/fetch_tfl_commute.py`

## Process
1. Look both ends up in `AREA_COORDS` / the destination table. An unknown code
   silently falls back to central London.
2. If `TFL_APP_KEY` is set, call the TfL Journey Planner
   (`/Journey/JourneyResults/{from}/to/{to}`) and read the first journey.
3. Otherwise generate the mock journey described above.
4. Cache the result in `.tmp/` for 7 days.

## Outputs
```json
{
  "duration_minutes": 27,
  "changes": 1,
  "walking_minutes": 10,
  "accessibility_score": 78,
  "route_summary": "Victoria line direct"
}
```
The scorer reads only `duration_minutes`, and converts it with
`100 - min(100, duration/60*100)` — so 60 minutes or more scores 0. A missing
result defaults to 30 minutes.

## Edge Cases & Learnings
- **No key**: the mock path is silent apart from a `[MOCK]` line on stdout.
  Anything downstream that presents a commute time should say where it came
  from.
- **One mode only**: there is no mode, time-of-day or disruption handling. The
  TfL branch takes the first journey the API returns.
- **Caching**: keyed on `(from_area, to_location)` for 7 days, so a mock time
  is stable within that window and changes when the cache expires.
