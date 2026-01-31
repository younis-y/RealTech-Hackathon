# 01 Data Pipeline Architecture
## End-to-End Data Flow Specification

### Purpose
Define the complete data pipeline from user input to final recommendations, including all transformations, validations, and caching strategies.

---

## Pipeline Overview

```
User Input (Preferences Form)
  ↓
Input Validation & Sanitization
  ↓
Candidate Area Generation (ScanSan Query)
  ↓
┌─────────────────────────────────────────────────────┐
│ PARALLEL ENRICHMENT (5 concurrent API calls)        │
├─────────────────────────────────────────────────────┤
│ 1. ScanSan    │ 2. TfL      │ 3. Crime    │ 4. Schools │ 5. Amenities │
│ Property Data │ Commute     │ Safety      │ Ratings    │ Density      │
└─────────────────────────────────────────────────────┘
  ↓
Data Aggregation & Normalization
  ↓
Score Calculation (Persona-Specific Weights)
  ↓
Ranking & Filtering
  ↓
Explanation Generation (Claude API)
  ↓
Response Formatting
  ↓
Delivery to User (JSON/UI)
```

---

## Stage 1: Input Validation

### Tool
`tools/validate_user_input.py` (to be created)

### Schema
Input: `UserInput` (see gemini.md Data Schema #1)

### Validation Rules

**Persona Validation**:
```python
if persona not in ["student", "parent", "developer"]:
    raise ValueError("Invalid persona")
```

**Budget Validation**:
```python
if budget_max <= 0:
    raise ValueError("Budget must be positive")
if budget_min and budget_min > budget_max:
    raise ValueError("Min budget cannot exceed max budget")
```

**Location Validation**:
```python
# For student/parent personas, require destination
if persona in ["student", "parent"] and not (campus_location or work_location):
    raise ValueError("Destination required for commute calculation")
```

**Importance Weights Validation**:
```python
# All weights must be 0-10
for factor, weight in importance_weights.items():
    if not 0 <= weight <= 10:
        raise ValueError(f"Weight for {factor} must be 0-10")
```

### Output
Validated `UserInput` object ready for pipeline

---

## Stage 2: Candidate Area Generation

### Tool
`tools/fetch_scansan.py`

### Input
- `budget_max`: From user preferences
- `budget_min`: Optional
- `location_type`: "rent" or "buy"
- `candidate_areas`: Optional user-specified areas

### Process

**If user provides candidate_areas**:
1. Use those areas directly
2. Skip affordability filtering

**If no candidate_areas provided**:
1. Query ScanSan API for areas matching budget
2. Filter by `affordability_score` >= 60 (configurable threshold)
3. Limit to top 20 affordable areas (to control API costs downstream)

### Output
List of area codes: `["E1", "E2", "SE1", "SW9", ...]`

---

## Stage 3: Parallel Enrichment

### Concurrency Strategy
Run all 5 API calls concurrently using Python `asyncio` or `concurrent.futures`

**Tools** (run in parallel):
1. `tools/fetch_scansan.py` - Already called in Stage 2, reuse/cache
2. `tools/fetch_tfl_commute.py`
3. `tools/fetch_crime_data.py`
4. `tools/fetch_schools.py` (skip for student persona)
5. `tools/fetch_amenities.py`

### Caching Check (Before API Call)

For each tool, before making API request:
```python
from cache_manager import read_cache

# Example for ScanSan
cached = read_cache("scansan_property", area_code)
if cached:
    return cached  # Use cache, skip API call

# Otherwise, fetch from API and cache result
data = call_scansan_api(area_code)
write_cache("scansan_property", area_code, data)
return data
```

### Error Handling

**Critical Data** (ScanSan):
- If fails: Skip that area entirely
- Reason: Can't score without primary data

**Important Data** (TfL, Crime):
- If fails: Use neutral score (50/100)
- Log warning to console

**Nice-to-Have** (Schools, Amenities):
- If fails: Use neutral score (50/100)
- Continue with recommendation

### Output
`EnrichmentData` object (see gemini.md Data Schema #7)

---

## Stage 4: Data Aggregation & Normalization

### Tool
`tools/aggregate_enrichment_data.py` (to be created)

### Process

**1. Combine All Data Sources**:
```python
aggregated_data = {}
for area_code in candidate_areas:
    aggregated_data[area_code] = {
        "scansan": scansan_results.get(area_code),
        "commute": commute_results.get(area_code),
        "crime": crime_results.get(area_code),
        "schools": schools_results.get(area_code),
        "amenities": amenities_results.get(area_code)
    }
```

**2. Normalize All Scores to 0-100**:

```python
def normalize_score(value, min_val, max_val):
    """Normalize any value to 0-100 scale"""
    if value is None:
        return 50  # Neutral if missing
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, normalized))  # Clamp to 0-100
```

Examples:
- Commute time (inverse): `100 - (duration_minutes / 60 * 100)`
- Crime score: Already 0-100 from tool
- School quality: Average of school quality scores

**3. Handle Missing Data**:
- If entire area has no ScanSan data: Remove from candidates
- If specific factor is null: Use 50 (neutral) as default

### Output
Normalized `EnrichmentData` ready for scoring

---

## Stage 5: Score Calculation

### Tool
`tools/score_areas.py`

### Input
- Persona
- User importance weights
- Enrichment data

### Process

See `architecture/02_scoring_engine.md` (to be created) for detailed scoring logic.

**Summary**:
1. Apply persona-specific base weights
2. Adjust by user importance ratings
3. Calculate weighted composite score
4. Identify factor contributions

### Output
`RecommendationOutput` with ranked recommendations (see gemini.md Data Schema #8)

---

## Stage 6: Explanation Generation

### Tool
`tools/generate_text_explanation.py`

### Input
- Top 3-5 `RecommendationItem` objects
- Persona
- Output format: "medium" for web UI

### Process

For each recommendation:
1. Call Claude API with structured prompt
2. Include all factor scores and contributions
3. Temperature=0.3 (low hallucination risk)
4. Validate output for hallucinations
5. Attach explanation to recommendation object

### Cost Control
- Only generate explanations for top 5 (not all 10)
- Cache explanations by (area_code, persona, format) key
- Reuse cached explanations for 7 days

### Output
Recommendations with `explanation` field populated

---

## Stage 7: Response Formatting

### Tool
`tools/format_response.py` (to be created)

### Input
`RecommendationOutput`

### Output Formats

**For Web UI (Next.js)**:
```json
{
  "status": "success",
  "persona": "student",
  "recommendations": [...],
  "cache_used": true,
  "generation_time_ms": 1234
}
```

**For API**:
Same JSON structure, add pagination metadata if needed

**For Video Script Generation**:
Extract top 1 recommendation, call `tools/generate_text_explanation.py` with format="video_script"

---

## Performance Optimization Strategies

### 1. Parallel Execution
- Stage 3 (Enrichment): Run all 5 API calls concurrently
- Expected time: ~2-5 seconds (vs 10-25 seconds sequential)

### 2. Aggressive Caching
- Stage 3: Check cache before every API call
- Expected cache hit rate: >50% after warmup period
- Cost savings: ~50% reduction in API calls

### 3. Lazy Video Generation
- Never auto-generate videos in pipeline
- Only when user clicks "Generate Video" button
- Saves ~£0.10-0.50 per request

### 4. Batch Candidate Filtering
- Stage 2: Limit to top 20 areas by affordability
- Prevents excessive enrichment API calls
- Reduces pipeline time and cost

### 5. Score Calculation Caching
- If user adjusts weights, recalculate scores WITHOUT re-fetching APIs
- Reuse cached enrichment data from Stage 3

---

## Error Recovery Patterns

### Scenario: All APIs Fail (Internet Outage)

**Recovery**:
1. Check `.tmp/` cache for any area
2. If cache available: Return cached recommendations with disclaimer
3. If no cache: Return 503 error "Service temporarily unavailable"

### Scenario: ScanSan API Down (Primary Source)

**Recovery**:
1. Cannot proceed without ScanSan (it's the core intelligence)
2. Return error: "Primary data source unavailable. Please try again later."
3. Log incident to gemini.md Self-Annealing Log

### Scenario: 1-2 Enrichment APIs Fail

**Recovery**:
1. Continue with available data
2. Use neutral scores (50/100) for missing factors
3. Include disclaimer in UI: "Some data sources unavailable; scores may be less accurate"
4. Log which APIs failed

---

## Data Freshness Policy

| Data Source | Cache Duration | Reason |
|-------------|----------------|--------|
| ScanSan property | 24 hours | Prices change daily |
| ScanSan trends | 7 days | Trends are stable |
| TfL commute | 7 days | Routes don't change often |
| Crime data | 30 days | Police data has 1-2 month lag |
| Schools | 90 days | Ofsted inspections are infrequent |
| Amenities | 30 days | Businesses change occasionally |

**Cache Invalidation**:
- Automatic: `tools/cache_manager.py clean` (run daily cron)
- Manual: User clicks "Refresh Data" button (forces re-fetch)

---

## Pipeline Monitoring

### Metrics to Track

1. **Pipeline Duration**:
   - Target: <5 seconds with cache, <10 seconds without
   - Alert if >15 seconds

2. **Cache Hit Rate**:
   - Target: >50% after warmup
   - Alert if <30%

3. **API Failure Rate**:
   - Target: <5% per API
   - Alert if >10%

4. **Cost per Request**:
   - Target: £0.02-0.10 (without video)
   - Alert if >£0.15

### Logging

Log to `.tmp/pipeline_metrics.json`:
```json
{
  "timestamp": "2026-01-31T14:30:00Z",
  "persona": "student",
  "duration_ms": 3456,
  "cache_hits": 8,
  "cache_misses": 2,
  "api_failures": 0,
  "cost_usd": 0.03,
  "recommendations_returned": 10
}
```

---

## Testing the Pipeline

### Unit Tests (Per Tool)
```bash
pytest tools/test_fetch_scansan.py
pytest tools/test_score_areas.py
```

### Integration Test (Full Pipeline)
```bash
python tools/test_pipeline_integration.py --persona student --budget 1000
```

Expected output:
- 10 recommendations with scores
- All scores between 0-100
- All explanations present (top 5)
- Total time <10 seconds
- No errors

---

## Pipeline Diagram (Detailed)

```
┌─────────────────────────────────────────────────────────┐
│ USER INPUT                                              │
│ persona: "student"                                      │
│ budget_max: 1000, max_commute: 30, campus: "UCL"       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 1: VALIDATION                                     │
│ ✓ Persona valid  ✓ Budget valid  ✓ Destination set    │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 2: CANDIDATE GENERATION (ScanSan)                │
│ Query: affordability + budget filter                    │
│ Result: [E1, E2, E3, SE1, SE15, N1, N7, SW9, ...]      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 3: PARALLEL ENRICHMENT (5 concurrent calls)      │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ ScanSan  │   TfL    │  Crime   │ Schools  │ Amenities  │
│ (cache✓) │ (cache✓) │ (cache✓) │ (cache✓) │  (cache✓)  │
│  2-5s    │  1-3s    │  1-2s    │  1-3s    │   1-3s     │
└──────────┴──────────┴──────────┴──────────┴────────────┘
                     ↓ (aggregate)
┌─────────────────────────────────────────────────────────┐
│ STAGE 4: DATA NORMALIZATION                            │
│ All scores normalized to 0-100                          │
│ Missing data filled with neutral scores (50)            │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 5: SCORING & RANKING                             │
│ Apply student weights: affordability 35%, commute 25%   │
│ Calculate composite scores                              │
│ Rank top 10 areas                                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 6: EXPLANATION GENERATION (Claude API)           │
│ Generate explanations for top 5 recommendations         │
│ Cost: ~£0.003 × 5 = £0.015                             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ STAGE 7: RESPONSE FORMATTING                           │
│ JSON with recommendations array                         │
│ Ready for Next.js UI rendering                          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ DELIVERY                                                │
│ • Web UI: Rendered cards with scores + explanations     │
│ • API: JSON response                                    │
│ • Total time: ~5 seconds (cached) to ~10s (cold)       │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

The data pipeline is the backbone of the Veo platform. It follows the **Data-First Rule**: all schemas are defined before implementation (see gemini.md), ensuring type safety and predictability.

**Key Principles**:
1. **Parallel where possible** (Stage 3)
2. **Cache aggressively** (all stages)
3. **Fail gracefully** (neutral scores for missing data)
4. **Monitor continuously** (metrics and logs)
5. **Self-anneal** (update SOPs when errors occur)

**Next**: See `architecture/02_scoring_engine.md` for detailed scoring logic.
