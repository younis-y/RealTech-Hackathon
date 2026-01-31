# TfL Commute Calculator Directive

## Goal
Calculate commute times from candidate areas to user-specified destinations using Transport for London's Unified API, supporting multiple transport modes and time-of-day scenarios.

## Inputs
- **from_locations**: List of postcodes or coordinates for candidate areas
- **to_locations**: List of destination postcodes/coordinates (e.g., university campus, office)
- **transport_modes**: List of modes (default: ["tube", "bus", "rail", "walking"])
  - Options: tube, bus, rail, overground, dlr, tram, walking, cycling
- **time_scenario**: When to calculate journey (default: "weekday_morning")
  - Options: weekday_morning (8-9am), weekday_evening (5-6pm), weekend, now
- **max_acceptable_time**: Optional filter in minutes

## Execution Tool
Use `execution/tfl_commute.py`

## Process
1. Validate inputs (postcodes converted to coordinates if needed)
2. For each from-to pair and transport mode combination:
   - Call TfL Journey Planner API
   - Extract duration, number of changes, walking time
3. Return aggregated results with best route per mode
4. Calculate accessibility score (0-100) based on journey time and convenience
5. Cache results in `.tmp/commute_cache_{session_id}.json`

## Outputs
JSON structure per route:
```json
{
  "from": "SW1A 1AA",
  "to": "WC1E 6BT",
  "mode": "tube",
  "duration_minutes": 25,
  "changes": 1,
  "walking_minutes": 8,
  "accessibility_score": 85,
  "route_summary": "District line to Circle line",
  "disruptions": [],
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **Rate limits**: TfL API allows 500 requests/minute (no auth) or 5000/minute (with app key)
  - Use app key stored in `.env` as `TFL_APP_KEY`
- **No route available**: Return null with reason (e.g., "Too far for walking", "No public transport")
- **Service disruptions**: API returns current disruptions; flag in output
- **Postcode to coordinates**: Use TfL or UK postcode API to geocode
- **Journey time variance**: Weekend journeys often 10-20% longer; weekday peak is baseline
- **Caching strategy**: Cache by (from, to, mode, time_scenario) tuple; valid for 7 days

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates]
