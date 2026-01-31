# ScanSan Property Intelligence Directive

## Goal
Fetch property and area intelligence data from ScanSan API for candidate locations, including affordability scores, risk assessments, investment quality metrics, and demand indicators.

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
Use `execution/scansan_api.py`

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
- **Rate limits**: ScanSan API has 100 requests/hour on free tier, 1000/hour on paid
  - If hit rate limit, cache aggressively and batch requests
  - Script includes exponential backoff retry logic
- **Invalid area codes**: Return null for that area but continue with others
- **Missing metrics**: Some areas may not have all metrics; script returns null for unavailable data
- **Staleness**: Cache is valid for 24 hours for property data, 7 days for area trends
- **API key**: Stored in `.env` as `SCANSAN_API_KEY`

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates as we learn from actual API calls]
