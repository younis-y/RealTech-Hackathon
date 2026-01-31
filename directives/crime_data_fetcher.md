# Crime Data Fetcher Directive

## Goal
Fetch and aggregate crime statistics for candidate areas using data.police.uk API to provide safety scores and crime breakdowns by category.

## Inputs
- **area_codes**: List of UK postcodes or coordinates
- **radius_meters**: Search radius around each location (default: 1000m, max: 5000m)
- **time_period**: Number of recent months to aggregate (default: 12, max: 24)
- **crime_categories**: Optional filter (default: all)
  - Available: violent-crime, burglary, robbery, theft, vehicle-crime, antisocial-behaviour, etc.

## Execution Tool
Use `execution/crime_data.py`

## Process
1. Convert postcodes to coordinates (use UK postcode API if needed)
2. For each location, call data.police.uk crimes-at-location endpoint
3. Aggregate crime counts by category over specified time period
4. Calculate safety score (0-100) based on:
   - Total crime count relative to national/London average
   - Crime type severity weighting (violent > burglary > antisocial)
   - Trend direction (improving vs worsening)
5. Store raw data in `.tmp/crime_data_{area}_{timestamp}.json`
6. Return aggregated safety metrics

## Outputs
JSON structure per area:
```json
{
  "area_code": "SW1A 1AA",
  "lat": 51.5014,
  "lon": -0.1419,
  "time_period_months": 12,
  "total_crimes": 234,
  "crimes_per_1000_people": 45.2,
  "safety_score": 72,
  "crime_breakdown": {
    "violent-crime": 45,
    "burglary": 12,
    "theft": 89,
    "antisocial-behaviour": 67,
    "other": 21
  },
  "trend": "improving",
  "percentile_vs_london": 65,
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **Rate limits**: data.police.uk has 15 requests/second, 10,000/day
  - Script includes 100ms delay between requests
  - Batch nearby areas to reduce API calls
- **No data**: Some areas may have no crimes reported; return score of 100 (safest)
- **Outdated data**: API has 1-2 month lag; most recent month may be incomplete
- **Population normalization**: Crimes per 1000 people requires population data
  - Use ONS population estimates (see `ons_demographics.md` directive)
- **Coordinate accuracy**: data.police.uk anonymizes exact locations to nearest street
- **Trend calculation**: Compare last 6 months to previous 6 months

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates]
