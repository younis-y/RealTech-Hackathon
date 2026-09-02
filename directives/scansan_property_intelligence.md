# ScanSan Property Intelligence Directive

## Goal
Give each candidate district an affordability score, an investment quality
score and a headline price, for the scoring engine to weight.

> **No ScanSan data is ever fetched.** No working API key was available, so
> `tools/fetch_scansan.py` sets `USE_MOCK_DATA = True` and generates every
> figure with `random.randint` over hand-set per-district tiers.
> `execution/scansan_api.py` is the client written against the real API; it has
> never returned data. Every price, growth and yield number the pipeline prints
> is invented.

## Inputs
- **area_codes**: List of UK postcode districts or sectors (e.g., ["SW1A", "E1", "M1"])
- **property_ids**: Optional list of specific property IDs if searching individual properties
- **metrics_requested**: List of ScanSan metrics to retrieve (default: all)
  - affordability_score
  - risk_score
  - investment_quality
  - demand_index
  - price_trends
  - yield_estimates

## Execution Tool
The pipeline uses `tools/fetch_scansan.py` (mock). `execution/scansan_api.py`
is the real client, and needs `SCANSAN_API_KEY`.

## Process
1. Validate inputs (area codes must be valid UK postcodes)
2. Call execution script with parameters
3. Script returns structured JSON with ScanSan scores for each area/property
4. Cache results in `.tmp/scansan_cache_{timestamp}.json` for this session
5. Return data for orchestration layer to use in scoring engine

## Outputs
JSON structure per area/property:
```json
{
  "area_code": "SW1A",
  "affordability_score": 0-100,
  "risk_score": 0-100,
  "investment_quality": 0-100,
  "demand_index": 0-100,
  "price_trends": {
    "1yr": percentage,
    "3yr": percentage,
    "5yr": percentage
  },
  "yield_estimate": percentage,
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **Rate limits**: unknown — the API was never reached, so no limit has been
  observed. `execution/scansan_api.py` sleeps for the `Retry-After` header on
  429 and backs off exponentially on any other unexpected status.
- **Invalid area codes**: Return null for that area but continue with others
- **Missing metrics**: Some areas may not have all metrics; script returns null for unavailable data
- **Staleness**: Cache is valid for 24 hours for property data, 7 days for area trends
- **API key**: Stored in `.env` as `SCANSAN_API_KEY`

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates as we learn from actual API calls]
