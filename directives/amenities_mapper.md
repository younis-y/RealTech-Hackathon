# Amenities Mapper Directive

## Goal
Map nearby amenities around candidate areas using OpenStreetMap Overpass API and Google Places API, focusing on persona-specific amenities (nightlife for students, parks for parents, infrastructure for investors).

## Inputs
- **area_codes**: List of UK postcodes or coordinates
- **radius_meters**: Search radius (default: 1000m)
- **persona**: Which persona to optimize for
  - student: pubs, bars, cafes, restaurants, gyms, supermarkets, nightclubs
  - parent: parks, playgrounds, leisure centres, libraries, GP surgeries, supermarkets
  - developer: transport hubs, upcoming infrastructure, commercial zones
- **custom_amenities**: Optional list of specific amenity types

## Execution Tool
Use `execution/amenities_map.py`

## Process
1. Convert postcodes to coordinates
2. Query OpenStreetMap Overpass API for amenities within radius
   - Primary source: fast, free, comprehensive
3. Fallback/supplement with Google Places API for missing categories
   - Use for ratings, opening hours, popularity
4. Calculate amenity density score (0-100) based on:
   - Count of relevant amenities within walking distance (500m)
   - Count within moderate distance (1000m)
   - Diversity of amenity types
   - Quality indicators (Google ratings if available)
5. Generate map data for visualization
6. Cache in `.tmp/amenities_{area}_{persona}_{timestamp}.json`

## Outputs
JSON structure per area:
```json
{
  "area_code": "SW1A 1AA",
  "persona": "student",
  "amenities": [
    {
      "type": "pub",
      "name": "The Red Lion",
      "distance_m": 250,
      "lat": 51.5014,
      "lon": -0.1419,
      "rating": 4.2,
      "source": "google_places"
    }
  ],
  "amenity_counts": {
    "pubs": 12,
    "cafes": 8,
    "supermarkets": 3,
    "gyms": 2
  },
  "density_score": 88,
  "walkability_score": 92,
  "diversity_score": 75,
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **Rate limits**:
  - OSM Overpass: No hard limit, but respect fair use (1 request/second)
  - Google Places: 1000 requests/day free tier, paid beyond
- **Data quality**: OSM has better coverage in urban areas; rural may be sparse
- **Duplicate detection**: Same amenity may appear in both OSM and Google; dedupe by location
- **Amenity classification**: Map OSM tags to amenity types
  - amenity=pub, amenity=bar, amenity=cafe, shop=supermarket, etc.
- **Temporal changes**: Businesses close; OSM data can be outdated
  - Use Google for validation of current status if budget allows
- **Persona weighting**: Different amenities weighted differently per persona
  - Student: nightlife > restaurants > gyms
  - Parent: parks > schools > GP surgeries
  - Developer: transport > commercial > planning zones

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates]
