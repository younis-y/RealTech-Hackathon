# 00 Master System Architecture
## Veo Housing Recommendation Platform

### Purpose
Technical specification for the complete Veo system using B.L.A.S.T. protocol and A.N.T. 3-layer architecture.

---

## System Overview

**Mission**: Deliver persona-specific, explainable housing recommendations with transparent factor breakdowns and optional auto-generated explainer videos.

**Personas**: Student, Parent, Developer/Investor

**Core Flow**:
```
User Input (persona + preferences)
  ↓
Data Fetching (ScanSan + enrichment APIs)
  ↓
Scoring Engine (persona-specific weights)
  ↓
Ranking & Explanation
  ↓
Output (JSON + web UI + optional video)
```

---

## Architecture Layers

### Layer 1: Architecture (architecture/)
- **This directory** - Technical SOPs in Markdown
- Define goals, inputs, tool logic, edge cases
- **Golden Rule**: Update SOP before updating code

### Layer 2: Navigation (AI Decision Making)
- AI reads architecture SOPs and routes data
- Calls tools/ in correct sequence
- Handles errors via self-annealing loop
- Never guesses at business logic

### Layer 3: Tools (tools/)
- Atomic, deterministic Python scripts
- One responsibility per tool
- Environment variables from .env
- Intermediate files in .tmp/

---

## Data Flow Pipeline

### 1. Input Capture
**Tool**: Frontend form → API route
**Data**: Persona, budget, commute destination, importance weights

### 2. Candidate Generation
**Tool**: `tools/fetch_scansan.py`
**Input**: Budget range, persona
**Output**: List of area codes meeting affordability criteria

### 3. Enrichment (Parallel)
**Tools**:
- `tools/fetch_tfl_commute.py` - Commute times
- `tools/fetch_crime_data.py` - Safety scores
- `tools/fetch_schools.py` - School ratings (parent only)
- `tools/fetch_amenities.py` - Nearby amenities

**Output**: Enriched dataset with all factor scores

### 4. Scoring & Ranking
**Tool**: `tools/score_areas.py`
**Input**: Enriched data + user weights
**Output**: Ranked recommendations with factor contributions

### 5. Explanation Generation
**Tool**: `tools/generate_text_explanation.py`
**Input**: Top recommendation + scores
**Output**: Natural language explanation (Claude API)

### 6. Video Generation (Optional)
**Tool**: `tools/generate_video.py`
**Input**: Recommendation + explanation + map assets
**Output**: MP4 video URL

---

## Persona Logic

### Student (35% affordability, 25% commute, 20% amenities, 15% safety, 5% investment)
**Data Sources**: ScanSan affordability, TfL commute, crime, amenities (nightlife)
**Constraints**: Budget £800-1200/month, max 30-40min commute
**Amenities**: Pubs, bars, cafes, gyms, nightclubs

### Parent (30% schools, 25% safety, 20% affordability, 15% commute, 10% amenities)
**Data Sources**: Schools/Ofsted, crime, ScanSan, TfL, amenities (family)
**Constraints**: Budget £1500-3000/month or £400k-700k purchase, min Ofsted "Good"
**Amenities**: Parks, playgrounds, leisure centres, GP surgeries

### Developer (40% investment, 25% demand, 20% risk, 15% infrastructure)
**Data Sources**: ScanSan (investment quality, yields, demand, risk), TfL infrastructure
**Constraints**: Budget £300k-1M+, target yield 4%+
**Focus**: Transport improvements, regeneration zones

---

## API Integration Strategy

### Primary Intelligence
**ScanSan API**
- Endpoint: `https://api.scansan.com/v1/area/{postcode}`
- Rate limit: 100/hour (free), 1000/hour (paid)
- Cache: 24 hours (property), 7 days (trends)
- Auth: Bearer token in header

### Enrichment APIs

**TfL Unified**
- Endpoint: `https://api.tfl.gov.uk/Journey/JourneyResults/{from}/to/{to}`
- Rate limit: 500/min (no auth), 5000/min (with key)
- Cache: 7 days

**data.police.uk**
- Endpoint: `https://data.police.uk/api/crimes-at-location`
- Rate limit: 15 req/sec, 10k/day
- Cache: 30 days
- Auth: None required

**Schools (GIAS)**
- Endpoint: `https://get-information-schools.service.gov.uk/`
- Rate limit: Fair use
- Cache: 90 days
- Auth: None required

**OpenStreetMap Overpass**
- Endpoint: `https://overpass-api.de/api/interpreter`
- Rate limit: 1 req/sec fair use
- Cache: 30 days
- Auth: None required

**Google Maps**
- Fallback for amenities, geocoding
- Rate limit: 1000 req/day (free tier)
- Cache: 30 days
- Auth: API key

### Video Generation APIs (Priority Order)

1. **Google Veo** (preferred, best quality)
2. **OpenAI Sora** (fallback)
3. **LTX Studio** (secondary fallback)
4. **Nano** (fast/cheap last resort)

---

## Caching Strategy

**Location**: `.tmp/` directory

**File Naming**:
- `scansan_{area_code}_{timestamp}.json`
- `tfl_{from}_{to}_{mode}_{timestamp}.json`
- `crime_{area_code}_{timestamp}.json`
- `schools_{area_code}_{timestamp}.json`
- `amenities_{area_code}_{persona}_{timestamp}.json`

**Cache Validity**:
- ScanSan property: 24 hours
- ScanSan trends: 7 days
- TfL commute: 7 days
- Crime: 30 days
- Schools: 90 days
- Amenities: 30 days

**Cache Tool**: `tools/cache_manager.py`
- Read cache before API call
- Validate timestamp
- Clean old entries (> 90 days)

---

## Error Handling (Self-Annealing)

### When Tool Fails:

1. **Analyze**: Read stack trace, identify root cause
2. **Patch**: Fix Python script in tools/
3. **Test**: Verify fix works with real data
4. **Update SOP**: Document learning in relevant architecture/ file
5. **Update gemini.md**: Log error and fix in Self-Annealing Log

### Common Error Patterns:

**API Rate Limit**
- Implement exponential backoff in tool
- Increase cache duration
- Document actual rate limit in SOP

**Invalid API Key**
- Check .env file
- Verify key with minimal test request
- Update gemini.md Link status

**Missing Data**
- Return null for that specific field
- Continue with other data sources
- Log which areas had missing data

**Network Timeout**
- Retry with increased timeout (max 3 attempts)
- Cache any partial results
- Fail gracefully, return what we have

---

## Testing Strategy

### Unit Tests (per tool)
- Test with mock API responses
- Verify data transformations
- Edge case handling

### Integration Tests
- Full pipeline with real API keys (dev tier)
- Verify caching works
- Test persona weight calculations

### Cost Tests
- Track API calls per user request
- Verify caching reduces redundant calls
- Monitor video generation costs

---

## Deployment Architecture

### Development
- Local: tools/ run from command line
- .env with dev API keys
- .tmp/ for cache

### Production
- Frontend: Vercel (Next.js)
- API: Vercel serverless functions call tools/
- Database: Supabase (PostgreSQL)
- Videos: S3 + CloudFront CDN
- Cache: Redis (optional, for distributed caching)

---

## Security & Compliance

**Secrets Management**:
- All API keys in .env (never commit)
- .gitignore includes .env, .tmp/, credentials.json
- Use environment variables in production (Vercel env vars)

**Data Privacy**:
- No user PII stored in .tmp/
- Video generation: user-initiated only (no auto-generation)
- Cache files: area-level data only (no user tracking)

**API Key Rotation**:
- Document key rotation procedure in gemini.md
- Test with new keys before rotating old ones

---

## Performance Targets

**User Request → Results**:
- Without cache: < 10 seconds
- With cache: < 2 seconds
- Video generation: 30-180 seconds (async, user notified when ready)

**Concurrent Users**:
- Target: 100 concurrent users
- Strategy: API rate limits, caching, async video generation

**Cost per User**:
- Target: £0.02-0.10 per recommendation set
- Video: £0.10-0.50 (user-initiated only)

---

## Maintenance Procedures

**Daily**:
- Monitor error logs in gemini.md
- Check API status dashboards

**Weekly**:
- Clean .tmp/ cache (files > 90 days)
- Review API costs and usage

**Monthly**:
- Update architecture SOPs with learnings
- Review and optimize caching strategy
- Update persona weights if user feedback suggests

**Quarterly**:
- Refresh school data (Ofsted inspections)
- Update area boundaries (ONS updates)

---

## Golden Rules

1. **Data-First**: Define schema in gemini.md before coding
2. **SOP Before Code**: Update architecture/ before updating tools/
3. **Never Guess**: If business logic is unclear, ask user
4. **Cache Aggressively**: Every API call costs money/quota
5. **Fail Gracefully**: One data source failure ≠ total failure
6. **Test Then Deploy**: Verify fix works before marking complete
7. **Document Learning**: Update SOP with every new edge case discovered

---

**References**:
- [gemini.md](../gemini.md) - Project Map & State
- [BLAST.md](../BLAST.md) - Protocol Reference
- Individual SOPs: 01-06 in this directory
