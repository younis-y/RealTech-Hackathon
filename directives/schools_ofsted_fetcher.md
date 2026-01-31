# Schools & Ofsted Data Directive

## Goal
Find nearby schools and their Ofsted ratings for candidate areas, focusing on primary and secondary schools within reasonable catchment distance.

## Inputs
- **area_codes**: List of UK postcodes or coordinates
- **max_distance_km**: Maximum distance to search for schools (default: 2km for primary, 5km for secondary)
- **school_types**: Filter by school type (default: all)
  - Options: primary, secondary, nursery, sixth-form, special
- **min_ofsted_rating**: Minimum acceptable Ofsted rating (1=Outstanding, 4=Inadequate)
- **include_faith_schools**: Boolean (default: true)

## Execution Tool
Use `execution/schools_ofsted.py`

## Process
1. Convert postcodes to coordinates
2. Query Get Information About Schools (GIAS) API for schools within radius
3. For each school, fetch latest Ofsted inspection report data
4. Calculate school quality score (0-100) based on:
   - Ofsted rating (Outstanding=100, Good=75, Requires Improvement=50, Inadequate=25)
   - Attainment metrics (if available)
   - Distance from area (closer = better)
   - Oversubscription ratio (proxy for demand)
5. Return ranked list of schools per area
6. Cache in `.tmp/schools_{area}_{timestamp}.json`

## Outputs
JSON structure per area:
```json
{
  "area_code": "SW1A 1AA",
  "primary_schools": [
    {
      "name": "Example Primary School",
      "urn": "123456",
      "distance_km": 0.8,
      "ofsted_rating": "Outstanding",
      "ofsted_rating_numeric": 1,
      "last_inspection": "2023-05-12",
      "school_type": "Academy",
      "faith_school": false,
      "pupils_on_roll": 420,
      "quality_score": 95,
      "catchment_area": true
    }
  ],
  "secondary_schools": [...],
  "avg_primary_score": 82,
  "avg_secondary_score": 78,
  "outstanding_schools_count": 3,
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **Rate limits**: GIAS API is open, Ofsted data portal has fair use policy
  - Cache aggressively; school data changes infrequently
  - Full refresh only quarterly
- **Missing Ofsted data**: Some new schools not yet inspected; return null with flag
- **Catchment areas**: Not available via API; use distance as proxy
  - Primary schools: most families use within 1km
  - Secondary schools: families travel up to 5km
- **Oversubscription**: Not directly available; use pupil-to-capacity ratio if data exists
- **Faith schools**: Some users prefer secular schools; make filterable
- **Special schools**: Exclude from general scoring unless specifically requested
- **Data freshness**: GIAS updated termly; Ofsted data updated within weeks of inspection

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates]
