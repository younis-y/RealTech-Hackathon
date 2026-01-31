# 05 API Integrations
## External Service Integration Specifications

### Purpose
Technical specifications for all external API integrations, including authentication, rate limits, error handling, and caching strategies.

---

## Integration Checklist (Phase 2: Link)

Before any tool uses an API:
1. ✅ API key added to .env
2. ✅ Minimal handshake test successful
3. ✅ Rate limits documented in this SOP
4. ✅ Caching strategy defined
5. ✅ Error handling implemented

---

## ScanSan Property Intelligence API

### Authentication
```python
headers = {
    "Authorization": f"Bearer {SCANSAN_API_KEY}",
    "Content-Type": "application/json"
}
```

### Endpoints

**Get Area Intelligence**
```
GET https://api.scansan.com/v1/area/{postcode_district}
```

**Query Parameters**:
- `metrics`: Comma-separated list (optional)
  - Options: `affordability_score`, `risk_score`, `investment_quality`, `demand_index`, `price_trends`, `yield_estimates`
  - Default: All metrics

**Response Schema**:
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
  "avg_price_rent_pm": integer,
  "avg_price_purchase": integer
}
```

### Rate Limits
- Free tier: 100 requests/hour
- Paid tier: 1000 requests/hour
- Burst: 10 requests/second (short duration)

### Error Codes
- `401`: Invalid API key → Check .env
- `404`: Area code not found → Return null, continue with other areas
- `429`: Rate limited → Exponential backoff, check Retry-After header
- `500`: Server error → Retry with backoff (max 3 attempts)

### Caching
- **Property data**: 24 hours
- **Area trends**: 7 days
- **File**: `.tmp/scansan_{area_code}_{timestamp}.json`

### Tool
`tools/fetch_scansan.py`

---

## TfL Unified API

### Authentication
```python
params = {
    "app_key": TFL_APP_KEY,
    "app_id": TFL_APP_ID  # optional but recommended
}
```

### Endpoints

**Journey Planner**
```
GET https://api.tfl.gov.uk/Journey/JourneyResults/{from}/to/{to}
```

**Query Parameters**:
- `mode`: Transport modes (tube, bus, rail, walking, cycling)
- `time`: Departure time (optional, format: HHmm)
- `timeIs`: "Departing" or "Arriving"
- `date`: Date (optional, format: YYYYMMDD)

**Response Schema** (simplified):
```json
{
  "journeys": [
    {
      "duration": minutes,
      "legs": [
        {
          "mode": {"name": "tube"},
          "duration": minutes,
          "instruction": {
            "summary": "District line to Circle line"
          }
        }
      ]
    }
  ]
}
```

### Rate Limits
- No auth: 500 requests/minute
- With app_key: 5000 requests/minute

### Error Codes
- `300`: Multiple locations found → Use most specific
- `400`: Invalid parameters → Check postcode format
- `404`: No journey found → Return null with reason
- `503`: Service disruption → Flag in response, use cached data

### Caching
- **Duration**: 7 days
- **Invalidate on**: TfL disruption alerts
- **File**: `.tmp/tfl_{from}_{to}_{mode}_{timestamp}.json`

### Tool
`tools/fetch_tfl_commute.py`

---

## data.police.uk Crime API

### Authentication
None required (open API)

### Endpoints

**Crimes at Location**
```
GET https://data.police.uk/api/crimes-at-location
```

**Query Parameters**:
- `lat`: Latitude
- `lng`: Longitude
- `date`: YYYY-MM format (optional, defaults to latest)

**Response Schema**:
```json
[
  {
    "category": "violent-crime",
    "location": {
      "latitude": "51.5014",
      "longitude": "-0.1419"
    },
    "month": "2024-11",
    "outcome_status": {...}
  }
]
```

### Rate Limits
- 15 requests/second
- 10,000 requests/day
- **Strategy**: 100ms delay between requests

### Data Lag
- **1-2 months** behind current date
- Don't rely on current month data

### Caching
- **Duration**: 30 days
- **File**: `.tmp/crime_{lat}_{lon}_{timestamp}.json`

### Tool
`tools/fetch_crime_data.py`

---

## Get Information About Schools (GIAS)

### Authentication
None required (open API)

### Endpoints

**Search Schools**
```
GET https://get-information-schools.service.gov.uk/api/edubase/schools
```

**Query Parameters**:
- `lat`: Latitude
- `lon`: Longitude
- `radius`: Search radius in km
- `phase`: School phase (primary, secondary, etc.)

### Ofsted Data
Ofsted ratings come from school records:
- 1: Outstanding
- 2: Good
- 3: Requires Improvement
- 4: Inadequate

### Rate Limits
- Fair use policy (no hard limit)
- Recommended: 1 request/second

### Caching
- **Duration**: 90 days (Ofsted inspections infrequent)
- **File**: `.tmp/schools_{lat}_{lon}_{radius}_{timestamp}.json`

### Tool
`tools/fetch_schools.py`

---

## OpenStreetMap Overpass API

### Authentication
None required

### Endpoints

**Overpass Query**
```
POST https://overpass-api.de/api/interpreter
```

**Query Format** (Overpass QL):
```
[out:json];
(
  node["amenity"="pub"](around:1000,51.5014,-0.1419);
  node["amenity"="cafe"](around:1000,51.5014,-0.1419);
);
out;
```

### Response Schema
```json
{
  "elements": [
    {
      "type": "node",
      "id": 123456,
      "lat": 51.5014,
      "lon": -0.1419,
      "tags": {
        "amenity": "pub",
        "name": "The Red Lion"
      }
    }
  ]
}
```

### Rate Limits
- **Fair use**: ~1 request/second
- **Timeout**: Queries >180 seconds are killed
- **Strategy**: Keep queries simple, small radius

### Caching
- **Duration**: 30 days
- **File**: `.tmp/amenities_osm_{lat}_{lon}_{radius}_{timestamp}.json`

### Tool
`tools/fetch_amenities.py`

---

## Google Maps APIs (Optional/Fallback)

### Authentication
```python
params = {"key": GOOGLE_MAPS_API_KEY}
```

### Endpoints Used

**Geocoding API**
```
GET https://maps.googleapis.com/maps/api/geocode/json?address={postcode}
```

**Places API**
```
GET https://maps.googleapis.com/maps/api/place/nearbysearch/json
```

**Static Maps API** (for video generation)
```
GET https://maps.googleapis.com/maps/api/staticmap
```

### Rate Limits
- Free tier: 1,000 requests/day (total across all APIs)
- Paid: $200 free credit/month, then pay-as-go

### Caching
- **Geocoding**: 90 days
- **Places**: 30 days
- **Static Maps**: Cache generated images indefinitely

### Tool
`tools/fetch_amenities.py` (fallback to OSM)

---

## Anthropic Claude API

### Authentication
```python
from anthropic import Anthropic
client = Anthropic(api_key=ANTHROPIC_API_KEY)
```

### Model
`claude-sonnet-4-5-20250929`

### Usage
```python
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=500,
    temperature=0.3,  # Low to reduce hallucination
    system="System prompt here",
    messages=[{"role": "user", "content": "Prompt"}]
)
```

### Rate Limits
- Tier 1: 50 requests/minute, 40,000 tokens/minute
- Tier 2+: Higher limits based on usage

### Cost
- Input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens
- **Per explanation**: ~$0.003 (150-200 word output)

### Caching
- **System prompts**: Use prompt caching feature (saves 90% cost on repeated prompts)
- **Explanations**: Cache by (area_code, persona, format) key for 7 days

### Tool
`tools/generate_text_explanation.py`

---

## Video Generation APIs

### Google Veo (Priority 1)

**Status**: Beta access required
**Cost**: ~$0.10-0.30 per video
**Duration**: 30-180 seconds generation time
**Rate Limit**: ~10 videos/day in beta

### OpenAI Sora (Priority 2)

**Status**: Limited access
**Cost**: ~$0.20-0.50 per video
**Rate Limit**: 50 videos/month (paid tier)

### LTX Studio (Priority 3)

**Cost**: ~$0.10 per video
**Rate Limit**: TBD

### Nano (Priority 4)

**Cost**: ~$0.05 per video (fastest, lowest quality)
**Rate Limit**: 100/day

### Strategy
Try APIs in order 1→2→3→4 until one succeeds.

### Caching
- **Generated videos**: Store in S3/CDN indefinitely
- **Mapping**: `.tmp/videos_{area_code}_{persona}_url.json`

### Tool
`tools/generate_video.py`

---

## API Verification (Phase 2: Link)

### Handshake Tests

Create minimal test scripts in `tools/verify_*.py`:

```python
# tools/verify_scansan.py
import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("SCANSAN_API_KEY")

response = requests.get(
    "https://api.scansan.com/v1/area/SW1A",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    print("✅ ScanSan API: Connected")
else:
    print(f"❌ ScanSan API: Failed ({response.status_code})")
```

Run all verification scripts before proceeding to full tool development.

---

## Error Handling Patterns

### Retry with Exponential Backoff
```python
import time

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                time.sleep(retry_after)
            else:
                time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    return None
```

### Graceful Degradation
```python
# If one API fails, continue with others
enrichment_data = {}

try:
    enrichment_data["scansan"] = fetch_scansan(area_code)
except Exception as e:
    log_error(f"ScanSan failed: {e}")
    enrichment_data["scansan"] = None  # Continue without it

# ... continue with other APIs
```

---

## Logging & Monitoring

### Log to gemini.md Self-Annealing Log

When API behavior changes:
1. Document the change
2. Update rate limits/costs in this SOP
3. Adjust caching strategy if needed

### Monitor API Costs

Track in `.tmp/api_costs_log.json`:
```json
{
  "date": "2026-01-31",
  "scansan_calls": 150,
  "claude_calls": 45,
  "google_maps_calls": 12,
  "estimated_cost_usd": 2.45
}
```

---

**Golden Rule**: Never proceed to full tool development until API handshake is verified in Phase 2: Link.
