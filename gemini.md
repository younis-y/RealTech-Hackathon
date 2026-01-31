# 🗺️ GEMINI.md - Veo Project Map
## Source of Truth | Last Updated: 2026-01-31 (Phase 2 Complete)

> This is the Project Map for Veo, an explainable multi-persona housing recommendation platform built using the B.L.A.S.T. protocol and A.N.T. 3-layer architecture.

---

## 🎯 Phase 0: Initialization Status

✅ **BLAST Protocol**: Active
✅ **Architecture Directories**: Created (architecture/, tools/, .tmp/)
⚠️ **Discovery Questions**: Pending user responses
⚠️ **Data Schema**: To be defined after Discovery
⚠️ **API Verification**: Pending .env configuration

---

## 🧭 Phase 1: Blueprint - Discovery Questions

### Required Before Coding Begins

**1. North Star (Singular Desired Outcome)**
```
Question: What is the ONE primary outcome this system must deliver?

Answer: ✅ CONFIRMED

Deliver persona-specific, ranked housing/area recommendations with transparent
factor breakdowns and natural language explanations that users can trust and act on.

Success criteria:
- User inputs persona + preferences → System returns top 10 ranked areas
- Each recommendation includes: composite score, factor breakdown, explanation
- Explanations are faithful to data (no hallucinations)
- Optional: User can generate shareable explainer video for top choices
```

**2. Integrations (External Services)**
```
Question: Which external services do we need? Are API keys ready?

Answer: ✅ CONFIRMED - Integration list finalized

CRITICAL (Required for MVP):
✅ ScanSan API - Property intelligence (SCANSAN_API_KEY) - PRIMARY SOURCE
✅ Anthropic Claude API - Natural language explanations (ANTHROPIC_API_KEY)

HIGH PRIORITY (Recommended):
✅ TfL Unified API - London commute times (TFL_APP_KEY)
✅ Google Maps API - Maps, places, directions (GOOGLE_MAPS_API_KEY)

MEDIUM PRIORITY (Free APIs, nice-to-have):
✅ data.police.uk - Crime data (Free, no key)
✅ Get Information About Schools - UK schools (Free, no key)
✅ ONS Open Geography - UK boundaries (Free, no key)
✅ OpenStreetMap Overpass - Amenities (Free, no key)

OPTIONAL (Video Generation - Phase 4):
○ Google Veo API (GOOGLE_VEO_API_KEY) - Priority 1
○ OpenAI Sora API (OPENAI_API_KEY) - Priority 2
○ LTX Studio API (LTX_API_KEY) - Priority 3
○ Nano Video API (NANO_API_KEY) - Priority 4

Status: .env.template created with all placeholders
Action: User must populate .env with at minimum SCANSAN_API_KEY and ANTHROPIC_API_KEY
```

**3. Source of Truth (Primary Data Location)**
```
Question: Where does the primary data live?

Answer: ✅ CONFIRMED - Multi-tier data architecture

PRIMARY SOURCE (Ground Truth):
- ScanSan API - Authoritative property/area intelligence
  - Affordability scores, risk assessments, investment quality, demand, yields
  - This is THE source of truth for property data

ENRICHMENT SOURCES (Supplement Primary):
- TfL Unified API - Commute times and transport context
- data.police.uk - Crime statistics and safety scores
- Get Information About Schools + Ofsted - School ratings
- OpenStreetMap Overpass + Google Maps - Amenities and POIs
- ONS Open Geography - Area boundaries and demographics

INTERMEDIATE STORAGE (Ephemeral):
- .tmp/ directory - Cached API responses, temporary processing files
- Validity: 24 hours (property) to 90 days (schools)
- Purpose: Reduce API costs, improve response time
- Not committed to git, can be regenerated

PERSISTENT STORAGE (Application Data):
- PostgreSQL (Supabase) - User profiles, saved searches, feedback
- CDN/S3 - Generated explainer videos (permanent URLs)

DELIVERABLE FORMAT:
- Web UI - Next.js application (primary interface)
- JSON API - Programmatic access to recommendations
- MP4 Videos - Shareable explainer content
```

**4. Delivery Payload (Final Result Location)**
```
Question: How and where should the final result be delivered?

Answer: ✅ CONFIRMED - Multi-channel delivery strategy

PRIMARY DELIVERY (Web Application):
- Platform: Next.js 14+ (App Router) hosted on Vercel
- User Flow:
  1. Landing page → Persona selection
  2. Preference form (5-8 questions per persona)
  3. Results page → Top 10 ranked areas with scores + explanations
  4. Detail page → Factor breakdown, map, video generation button
- Output Format: Rendered HTML/React components + Tailwind CSS styling

API DELIVERY (Programmatic Access):
- Endpoint: Next.js API routes (serverless functions on Vercel)
- Format: JSON responses with full recommendation data
- Authentication: API key (for future integration partners)
- Example: POST /api/recommend → Returns ranked recommendations JSON

DATABASE STORAGE (Persistent):
- Platform: Supabase (PostgreSQL)
- Stored Data:
  - User profiles and preferences
  - Saved searches and favorite areas
  - User feedback ("helpful/not helpful")
  - Cached API results (optional, for performance)
- Purpose: Enable personalization, A/B testing, analytics

VIDEO DELIVERY (Shareable Content):
- Storage: AWS S3 or Vercel Blob Storage
- CDN: CloudFront or Vercel Edge Network
- Format: MP4 (16:9 for web, 9:16 for mobile)
- Duration: 30-60 seconds
- Access: Public URLs, shareable on social media
- Generation: On-demand only (user clicks "Generate Video" button)

PAYLOAD STRUCTURE (Core Recommendation Object):
{
  "persona": "student|parent|developer",
  "area_code": "E1 6AN",
  "rank": 1,
  "composite_score": 87.3,
  "factor_scores": {...},
  "factor_contributions": {...},
  "explanation": "Natural language text...",
  "video_url": "https://cdn.example.com/videos/E1_6AN_student.mp4" (optional)
}
```

**5. Behavioral Rules (System Personality & Constraints)**
```
Question: How should the system "act"? Any "Do Not" rules?

Answer: ✅ CONFIRMED - System behavioral contract

CORE PRINCIPLES:

1. FAITHFULNESS TO DATA (Anti-Hallucination)
   - DO: Only reference numeric data points actually provided by APIs
   - DO: Include data source attribution (e.g., "ScanSan reports...", "TfL data shows...")
   - DO NOT: Invent facts, statistics, or general knowledge not in API responses
   - DO NOT: Make assumptions about areas beyond provided data
   - Validation: Every claim in explanation must trace to API response field

2. TRANSPARENCY (Explainability First)
   - DO: Show factor breakdown for every recommendation (what contributed to score)
   - DO: Explain trade-offs clearly (e.g., "Better schools but longer commute")
   - DO: Surface data limitations (e.g., "Crime data is 2 months old")
   - DO NOT: Hide how scores are calculated (no black boxes)
   - Tone: Confident but honest about uncertainty

3. PERSONA APPROPRIATENESS
   - DO: Adjust language and priorities for each persona
     - Student: Casual, focus on lifestyle and budget
     - Parent: Careful, focus on safety and education
     - Developer: Analytical, focus on ROI and risk
   - DO: Use persona-specific weights (Student: 35% affordability, Parent: 30% schools, etc.)
   - DO NOT: Mix persona priorities (don't show nightlife scores to parents)

4. UK LOCALIZATION
   - DO: Use UK English spelling (flat, not apartment; postcode, not zip code)
   - DO: Use UK-specific terminology (Ofsted ratings, council tax, etc.)
   - DO: Format prices as £XXX,XXX (comma separators)
   - DO: Use UK date format (DD/MM/YYYY) in UI

5. COST OPTIMIZATION
   - DO: Cache aggressively (24h for property, 7d for commute, 30d for crime)
   - DO: Batch API requests where possible
   - DO: Load video generation only on user request (never auto-generate)
   - DO NOT: Make redundant API calls if cached data is fresh
   - DO NOT: Use expensive APIs (video gen) without explicit user action

6. SECURITY & PRIVACY
   - DO: Store API keys in .env only (never in code)
   - DO: Use .gitignore for .env, .tmp/, credentials.json
   - DO: Validate user inputs to prevent injection attacks
   - DO NOT: Log API keys or sensitive user data
   - DO NOT: Commit cache files or temporary data to git

7. GRACEFUL DEGRADATION
   - DO: Continue with partial data if one API fails
   - DO: Return "best effort" recommendations with disclaimers
   - DO: Provide fallback scores (50/100 neutral) for missing data
   - DO NOT: Fail entirely if non-critical API is down
   - DO NOT: Return error to user if 1 of 5 data sources fails

8. USER EXPERIENCE
   - DO: Show loading states ("Fetching crime data...")
   - DO: Provide "helpful/not helpful" feedback buttons
   - DO: Allow users to adjust weights and re-rank without re-fetching data
   - DO NOT: Block UI for > 10 seconds (use async for slow operations)
   - DO NOT: Overwhelm users with technical jargon or raw data

9. SELF-IMPROVEMENT (Self-Annealing)
   - DO: Log all errors to gemini.md Self-Annealing Log
   - DO: Update architecture SOPs when new edge cases discovered
   - DO: Test fixes before deploying
   - DO NOT: Guess at business logic; ask for clarification if unclear
   - DO NOT: Repeat the same error twice (learn from failures)

TONE & VOICE:
- Confident: "This area scores 87/100 for students."
- Helpful: "Here's why Shoreditch suits your priorities..."
- Transparent: "Safety is lower here (78/100) due to higher crime rates in the past year."
- Not salesy: Avoid "perfect", "ideal", "amazing" unless data supports it
- Data-driven: Lead with numbers, follow with interpretation

DEFINITION OF DONE:
- All recommendations have factor breakdowns
- All explanations trace to API data
- Cache hit rate > 50%
- No hallucinated facts in testing
- User can understand why each area ranked where it did
```

---

## 📊 Data Schema (Data-First Rule)

### Status: ✅ DEFINED - Ready for Implementation

All tools/ scripts must conform to these schemas. No coding begins without schema compliance.

---

### 1. User Input Schema

```typescript
interface UserInput {
  persona: "student" | "parent" | "developer";
  preferences: {
    // Common to all personas
    budget_min?: number;          // £ per month (rent) or total (purchase)
    budget_max: number;           // Required
    location_type: "rent" | "buy";

    // Student-specific
    campus_location?: string;     // e.g., "UCL Gower Street"
    max_commute_minutes?: number; // default: 30
    nightlife_importance?: number; // 0-10 scale

    // Parent-specific
    work_location?: string;
    min_school_rating?: number;   // 1-4 (Ofsted scale)
    green_space_importance?: number; // 0-10 scale
    num_bedrooms?: number;

    // Developer-specific
    target_yield?: number;        // % annual yield
    risk_tolerance?: "low" | "medium" | "high";
    investment_focus?: "yield" | "growth" | "balanced";

    // Importance weights (0-10 scale, optional)
    importance_weights?: {
      affordability?: number;
      commute?: number;
      safety?: number;
      schools?: number;
      amenities?: number;
      investment_quality?: number;
      demand?: number;
    };
  };
  candidate_areas?: string[];     // Optional: user-specified areas to evaluate
}
```

---

### 2. ScanSan API Response Schema

```typescript
interface ScanSanResponse {
  area_code: string;              // e.g., "SW1A", "E1 6AN"
  affordability_score: number;    // 0-100
  risk_score: number;             // 0-100
  investment_quality: number;     // 0-100
  demand_index: number;           // 0-100
  price_trends: {
    "1yr": number;                // % change
    "3yr": number;
    "5yr": number;
  };
  yield_estimate: number;         // % annual yield
  avg_price_rent_pm: number;      // £ per month
  avg_price_purchase: number;     // £ total
  timestamp: string;              // ISO-8601
  data_source: "scansan";
}
```

---

### 3. TfL Commute Response Schema

```typescript
interface TfLCommuteResponse {
  from: string;                   // Postcode or area code
  to: string;                     // Destination postcode
  mode: "tube" | "bus" | "rail" | "walking" | "cycling";
  duration_minutes: number;
  changes: number;                // Number of transfers
  walking_minutes: number;        // Total walking time
  accessibility_score: number;    // 0-100 (calculated)
  route_summary: string;          // e.g., "District line to Circle line"
  disruptions: string[];          // Active service disruptions
  timestamp: string;
  data_source: "tfl";
}
```

---

### 4. Crime Data Response Schema

```typescript
interface CrimeDataResponse {
  area_code: string;
  lat: number;
  lon: number;
  time_period_months: number;     // How many months aggregated
  total_crimes: number;
  crimes_per_1000_people: number; // Normalized
  safety_score: number;           // 0-100 (calculated)
  crime_breakdown: {
    "violent-crime": number;
    "burglary": number;
    "theft": number;
    "vehicle-crime": number;
    "antisocial-behaviour": number;
    "other": number;
  };
  trend: "improving" | "stable" | "worsening";
  percentile_vs_london: number;   // 0-100 (higher = safer)
  timestamp: string;
  data_source: "police_uk";
}
```

---

### 5. Schools Data Response Schema

```typescript
interface SchoolsDataResponse {
  area_code: string;
  primary_schools: SchoolInfo[];
  secondary_schools: SchoolInfo[];
  avg_primary_score: number;      // 0-100 (calculated)
  avg_secondary_score: number;    // 0-100 (calculated)
  outstanding_schools_count: number;
  timestamp: string;
  data_source: "gias_ofsted";
}

interface SchoolInfo {
  name: string;
  urn: string;                    // Unique Reference Number
  distance_km: number;
  ofsted_rating: "Outstanding" | "Good" | "Requires Improvement" | "Inadequate" | "Not Inspected";
  ofsted_rating_numeric: number;  // 1-4 (1=Outstanding)
  last_inspection: string;        // ISO date
  school_type: string;            // e.g., "Academy", "Community"
  faith_school: boolean;
  pupils_on_roll: number;
  quality_score: number;          // 0-100 (calculated)
  catchment_area: boolean;        // Estimated
}
```

---

### 6. Amenities Response Schema

```typescript
interface AmenitiesResponse {
  area_code: string;
  persona: "student" | "parent" | "developer";
  amenities: AmenityInfo[];
  amenity_counts: Record<string, number>; // e.g., {"pubs": 12, "cafes": 8}
  density_score: number;          // 0-100 (calculated)
  walkability_score: number;      // 0-100
  diversity_score: number;        // 0-100
  timestamp: string;
  data_source: "osm" | "google_places";
}

interface AmenityInfo {
  type: string;                   // e.g., "pub", "cafe", "park"
  name: string;
  distance_m: number;
  lat: number;
  lon: number;
  rating?: number;                // 0-5 (Google rating if available)
  source: "osm" | "google_places";
}
```

---

### 7. Enrichment Data (Combined) Schema

```typescript
interface EnrichmentData {
  [area_code: string]: {
    scansan: ScanSanResponse | null;
    commute: TfLCommuteResponse | null;
    crime: CrimeDataResponse | null;
    schools: SchoolsDataResponse | null;
    amenities: AmenitiesResponse | null;
  };
}
```

---

### 8. Recommendation Output Schema

```typescript
interface RecommendationOutput {
  persona: "student" | "parent" | "developer";
  user_preferences: UserInput["preferences"];
  adjusted_weights: Record<string, number>; // Persona weights adjusted by user importance
  recommendations: RecommendationItem[];
  filtered_out_count: number;
  filtered_out_reasons: Array<{area_code: string; reason: string}>;
  timestamp: string;
}

interface RecommendationItem {
  rank: number;                   // 1-10
  area_code: string;
  composite_score: number;        // 0-100
  factor_scores: {
    affordability?: number;
    commute?: number;
    safety?: number;
    schools?: number;
    amenities?: number;
    investment_quality?: number;
    demand_index?: number;
    risk_score?: number;
    infrastructure?: number;
  };
  factor_contributions: Record<string, number>; // How much each factor added to composite
  strengths: string[];            // e.g., ["Excellent nightlife", "Quick commute"]
  weaknesses: string[];           // e.g., ["Slightly higher crime"]
  trade_offs: string;             // Comparison to other top choices
  explanation?: string;           // Natural language (generated by Claude API)
  raw_data: EnrichmentData[string]; // Full underlying data
}
```

---

### 9. Explanation Generation Schema

```typescript
interface ExplanationRequest {
  recommendation: RecommendationItem;
  persona: "student" | "parent" | "developer";
  output_format: "short" | "medium" | "video_script";
  comparison_areas?: RecommendationItem[]; // Other top choices for trade-off analysis
}

interface ExplanationResponse {
  explanation: string;            // Natural language text
  format: "short" | "medium" | "video_script";
  persona: "student" | "parent" | "developer";
  validation_passed: boolean;     // No hallucinations detected
  tokens_used: number;
  cost_usd: number;
}
```

---

### 10. Video Generation Schema

```typescript
interface VideoGenerationRequest {
  area_code: string;
  recommendation: RecommendationItem;
  script: string;                 // From ExplanationResponse (video_script format)
  persona: "student" | "parent" | "developer";
  map_image_url: string;          // Static map from Google Maps API
  aspect_ratio: "16:9" | "9:16";  // Web or mobile
}

interface VideoGenerationResponse {
  area_code: string;
  video_url: string;              // CDN URL (S3/CloudFront)
  thumbnail_url: string;
  duration_seconds: number;
  script: string;
  generation_api: "veo" | "sora" | "ltx" | "nano";
  generation_time_seconds: number;
  cost_usd: number;
  has_subtitles: boolean;
  timestamp: string;
}
```

---

### 11. Cache Data Schema

```typescript
interface CacheEntry<T> {
  _cache_timestamp: string;       // ISO-8601
  _cache_type: string;            // e.g., "scansan_property", "tfl_commute"
  _cache_key: string;             // Unique identifier
  data: T;                        // The actual cached data (any of the above response types)
}
```

---

### Schema Validation Rules

1. **Required Fields**: All fields without `?` are required
2. **Score Normalization**: All `*_score` fields must be 0-100
3. **Timestamp Format**: ISO-8601 (e.g., "2026-01-31T14:30:00Z")
4. **Null Handling**: If API fails, set response to `null` (not omit the key)
5. **Type Safety**: TypeScript interfaces must be enforced in all tools/
6. **Data Source Attribution**: Every response must have `data_source` field

---

### Schema Evolution

When schemas need to change:
1. Update this section in gemini.md FIRST
2. Then update TypeScript interfaces (if using TS)
3. Then update tools/ scripts to match new schema
4. Then update architecture/ SOPs to document changes
5. Log change to Self-Annealing Log with reason

**Current Schema Version**: 1.0.0 (2026-01-31)

---

## 🏗️ Phase 3: Architecture (3-Layer A.N.T. System)

### Layer 1: Architecture (architecture/ - Technical SOPs)

**Status**: Creating...

Planned SOPs:
- `00_master_system.md` - Overall system architecture
- `01_data_pipeline.md` - Data fetching and processing
- `02_scoring_engine.md` - Persona-specific scoring logic
- `03_explanation_generation.md` - NL explanation pipeline
- `04_video_generation.md` - Video creation workflow
- `05_api_integrations.md` - External API management
- `06_error_handling.md` - Self-annealing procedures

### Layer 2: Navigation (Decision Making - AI Orchestration)

**Role**: AI (Claude) reads architecture SOPs and calls tools/ scripts in proper sequence.

**Current State**: Operational (AI ready to orchestrate)

**Decision Trees**:
- Persona identification → Select relevant data sources
- API failure → Trigger self-annealing loop
- User request type → Route to appropriate tool chain

### Layer 3: Tools (tools/ - Deterministic Python Scripts)

**Status**: Creating atomic scripts...

Planned Tools:
- `fetch_scansan.py` - ScanSan API client
- `fetch_tfl_commute.py` - TfL commute calculator
- `fetch_crime_data.py` - Crime data aggregator
- `fetch_schools.py` - Schools and Ofsted ratings
- `fetch_amenities.py` - OSM/Google amenities
- `score_areas.py` - Scoring engine
- `generate_text_explanation.py` - Claude API for explanations
- `generate_video.py` - Video generation pipeline
- `cache_manager.py` - Cache operations for .tmp/

---

## 🔗 Phase 2: Link - API Verification Status

### ✅ Phase 2 COMPLETED (Partial - Hackathon Mode)

**Date Completed**: 2026-01-31
**Status**: Anthropic verified, ScanSan skipped for development

### Connection Handshake Status

| Service | Status | Last Tested | Notes |
|---------|--------|-------------|-------|
| ScanSan API | ⚠️ SKIPPED | 2026-01-31 | Auth failed - using mock data for hackathon |
| Anthropic Claude | ✅ VERIFIED | 2026-01-31 | Connected successfully |
| TfL Unified API | ⚠️ NOT CONFIGURED | N/A | No key provided - optional |
| Google Maps | ✅ VERIFIED | 2026-01-31 | Connected successfully |
| data.police.uk | ✅ VERIFIED | 2026-01-31 | Free API working |
| Schools API | ✅ VERIFIED | 2026-01-31 | Free API working (via OSM) |
| OSM Overpass | ✅ VERIFIED | 2026-01-31 | Free API working |

**Verification Results**:
- Required APIs: 1/2 passed (Anthropic ✅, ScanSan ⚠️ skipped)
- Optional APIs: 3/4 passed (Google Maps ✅, Police ✅, OSM ✅, TfL missing)
- **Decision**: Proceed to Phase 3 with mock ScanSan data for hackathon development

**Next Step**: Proceed to Phase 3: Architect (build remaining tools with mock data)

---

## ✨ Phase 4: Stylize - Output Refinement

**Status**: Not yet started (requires working tools first)

**Planned Refinements**:
- Slack message formatting (if Slack integration added)
- Email HTML templates (if email delivery added)
- Web UI styling (Next.js components with Tailwind CSS)
- Video overlays and branding
- Score visualization (charts, cards, maps)

---

## 🛰️ Phase 5: Trigger - Deployment

**Status**: Not yet started

**Planned Triggers**:
- Web app: User submits form → API route → Tool chain → Results
- Video generation: User clicks button → Async job → Video API → CDN upload
- Cron jobs: None initially (all on-demand)
- Webhooks: None initially

**Deployment Targets**:
- Frontend: Vercel
- Backend API: Vercel serverless functions
- Database: Supabase (PostgreSQL)
- Videos: AWS S3 or similar CDN

---

## 🔄 Self-Annealing Log

**Purpose**: Track errors and fixes to build system resilience.

### Error History

| Date | Error | Root Cause | Fix Applied | SOP Updated |
|------|-------|------------|-------------|-------------|
| 2026-01-31 | System initialized | N/A | Created BLAST structure | N/A |
| _TBD_ | _Will log errors as they occur_ | _..._ | _..._ | _..._ |

### Learning Repository

**API Rate Limits**:
- ScanSan: 100 req/hour (free), 1000 req/hour (paid) - [TBD: verify actual limits]
- TfL: 500 req/min (no auth), 5000 req/min (with key)
- Google Maps: 1000 req/day (free tier)

**Data Staleness Guidelines**:
- Property prices: Cache 24 hours
- Area trends: Cache 7 days
- Commute times: Cache 7 days (update if TfL disruptions)
- Crime data: Cache 30 days (police data has 1-2 month lag)
- School ratings: Cache 90 days (Ofsted inspections infrequent)

**Edge Cases Discovered**:
- _Will document as encountered_

---

## 📋 Current Project State

### What's Working
✅ Directory structure created (architecture/, tools/, .tmp/)
✅ .env.template created with all required API key placeholders
✅ .gitignore configured (excludes .env, .tmp/, credentials)
✅ Documentation scaffolded (README, QUICK_REFERENCE)
✅ Initial directives created (alternative Agents.md architecture)

### What's Pending
✅ Discovery Questions answered (Phase 1 complete)
✅ Data Schema defined (11 schemas)
✅ API keys added to .env
✅ API verification completed (partial - ScanSan skipped)
⚠️ Complete tools/ Python scripts (7 remaining)
⚠️ Complete architecture/ SOPs (3 remaining)
⚠️ Next.js frontend implementation

### Immediate Next Steps
1. **Phase 3**: Build remaining 7 tools/ Python scripts with mock ScanSan data
2. **Phase 4**: Build Next.js frontend
3. **Phase 5**: Deploy to Vercel for hackathon demo
3. **System**: Define Data Schema based on Discovery answers
4. **System**: Create verification tools for API handshakes
5. **System**: Build core tools/ scripts following Data Schema

---

## 🎯 Persona Profiles (Business Logic)

### Student Persona
**Priority Factors** (weights):
- Affordability: 35%
- Commute: 25%
- Amenities (nightlife): 20%
- Safety: 15%
- Investment Quality: 5%

**Typical Constraints**:
- Budget: £800-1200/month rent
- Max commute: 30-40 minutes
- Transport: Tube, bus, walking
- Amenity focus: Pubs, cafes, gyms, nightclubs

### Parent Persona
**Priority Factors** (weights):
- Schools: 30%
- Safety: 25%
- Affordability: 20%
- Commute: 15%
- Amenities (family): 10%

**Typical Constraints**:
- Budget: £1500-3000/month rent or £400k-700k purchase
- Max commute: 40-50 minutes
- School rating: Outstanding or Good (Ofsted)
- Amenity focus: Parks, playgrounds, leisure centres, GP surgeries

### Developer/Investor Persona
**Priority Factors** (weights):
- Investment Quality: 40%
- Demand Index: 25%
- Risk Score: 20%
- Infrastructure: 15%

**Typical Constraints**:
- Budget: £300k-1M+ purchase
- Target yield: 4%+ for buy-to-let
- Risk tolerance: Low to moderate
- Focus: Areas with transport improvements, regeneration

---

## 📊 File Structure Reference

```
veo/
├── gemini.md                    # ← YOU ARE HERE (Project Map)
├── BLAST.md                     # Protocol reference
├── .env                         # API keys (create from .env.template)
├── .env.template                # Template for API keys
├── .gitignore                   # Git exclusions
│
├── architecture/                # Layer 1: Technical SOPs
│   ├── 00_master_system.md
│   ├── 01_data_pipeline.md
│   ├── 02_scoring_engine.md
│   ├── 03_explanation_generation.md
│   ├── 04_video_generation.md
│   ├── 05_api_integrations.md
│   └── 06_error_handling.md
│
├── tools/                       # Layer 3: Python scripts (atomic)
│   ├── fetch_scansan.py
│   ├── fetch_tfl_commute.py
│   ├── fetch_crime_data.py
│   ├── fetch_schools.py
│   ├── fetch_amenities.py
│   ├── score_areas.py
│   ├── generate_text_explanation.py
│   ├── generate_video.py
│   ├── cache_manager.py
│   └── requirements.txt
│
├── .tmp/                        # Intermediate files (ephemeral)
│   └── (cache files, scraped data, temporary exports)
│
├── directives/                  # Alternative Agents.md architecture (coexists)
├── execution/                   # Alternative execution scripts (coexists)
│
└── [Next.js app structure]      # Frontend (to be created)
    ├── app/
    ├── components/
    ├── lib/
    └── public/
```

---

## 🚦 Protocol Status Checklist

### Phase 0: Initialization
- [x] gemini.md created as Project Map
- [x] Architecture directories created
- [ ] Discovery Questions answered by user
- [ ] Data Schema defined

### Phase 1: Blueprint
- [x] Discovery Questions completed
- [x] Data Schema documented in this file
- [x] Blueprint ready for Phase 2: Link

### Phase 2: Link
- [ ] .env populated with API keys
- [ ] API verification tools created
- [ ] All API handshakes successful

### Phase 3: Architect
- [ ] Architecture SOPs written
- [ ] Tools scripts implemented
- [ ] Self-annealing loop tested

### Phase 4: Stylize
- [ ] Output formatting refined
- [ ] UI/UX implemented
- [ ] User feedback incorporated

### Phase 5: Trigger
- [ ] Cloud deployment completed
- [ ] Automation triggers configured
- [ ] Maintenance documentation finalized

---

## 💬 Context Handoff (For New Sessions)

**Last Session**: 2026-01-31 - Phase 1 & 2 Complete

**What Changed**:
- ✅ Completed Phase 1: Blueprint (Discovery Questions answered, 11 schemas defined)
- ✅ Completed Phase 2: Link (API verification done - Anthropic, Google Maps, Police, OSM working)
- ⚠️ ScanSan API skipped for hackathon (using mock data approach)
- ✅ Python dependencies installed
- ✅ .env configured with working API keys

**Why It Matters**:
- System now has dual architecture: Agents.md (directives/) + BLAST (architecture/)
- All required infrastructure is in place
- Ready to build Phase 3 tools with mock ScanSan data
- Hackathon-ready development mode enabled

**Next Logical Step**:
- Phase 3: Build remaining 7 tools/ Python scripts
- Create mock ScanSan data generator
- Test full pipeline with mock data
- Build Next.js frontend for demo

---

**End of Project Map** | System Status: ✅ Phase 1 Complete → ✅ Phase 2 Complete (Partial) → 🟢 Ready for Phase 3: Architect
