# Backend Implementation Plan - Domus Housing Platform

**Owner**: Builder (Functionality & Logic Lead)  
**Last Updated**: 2026-01-31  
**Status**: Phase 1 - Core API Infrastructure

---

## Overview

This document tracks the backend implementation for the Domus Housing Recommendation Platform. The backend focuses on building robust API routes, state management, data processing logic, and serverless infrastructure using Modal.

## Architecture Principles

### 3-Layer System
1. **Layer 1: Directives** - Business logic defined in `directives/*.md`
2. **Layer 2: Orchestration** - LLM-powered decision making (this layer)
3. **Layer 3: Execution** - Deterministic Python scripts in `execution/` and `tools/`

### Backend Responsibilities
- API route handlers (`frontend/app/api/*`)
- Business logic utilities (`frontend/lib/*`)
- Serverless function deployment (Modal)
- Data validation and transformation
- Error handling and retry logic
- Caching strategies

---

## Current State Analysis

### ✅ What's Working
- **Demo Pipeline**: [`demo_pipeline.py`](demo_pipeline.py) - Full end-to-end demo
- **Execution Scripts**: Core data fetching in [`execution/`](execution/) and [`tools/`](tools/)
  - [`scansan_api.py`](execution/scansan_api.py) - Property intelligence
  - [`score_and_rank.py`](execution/score_and_rank.py) - Scoring engine
  - TfL, Crime, Schools, Amenities fetchers
- **Basic API Route**: [`/api/recommendations`](frontend/app/api/recommendations/route.ts) - Works but needs improvement

### ⚠️ What Needs Work
1. **API Structure**: Current route spawns Python processes - inefficient for production
2. **Error Handling**: Minimal error handling and validation
3. **Response Format**: Parser is brittle, needs structured JSON output
4. **State Management**: No caching, session management, or request tracking
5. **Serverless**: No Modal deployment configuration
6. **Rate Limiting**: No API rate limiting or queue management

---

## Phase 1: Core API Infrastructure (Current)

### Goal
Build production-ready API endpoints with proper error handling, validation, and structured responses.

### Tasks

#### 1. Refactor `/api/recommendations` Route ✅ IN PROGRESS
**File**: [`frontend/app/api/recommendations/route.ts`](frontend/app/api/recommendations/route.ts)

**Current Issues**:
- Spawns Python subprocess for each request (slow, resource-intensive)
- String parsing of Python output (brittle)
- No request validation
- Poor error responses

**Improvements Needed**:
- Add Zod validation schemas for request body
- Improve error handling with typed errors
- Add request logging
- Return structured JSON with proper TypeScript types
- Add request timeout handling

#### 2. Create Backend Utilities Library 🔄 TODO
**Directory**: `frontend/lib/`

**Files to Create**:
- `frontend/lib/validators.ts` - Zod schemas for API validation
- `frontend/lib/types.ts` - TypeScript types for all data models
- `frontend/lib/errors.ts` - Custom error classes
- `frontend/lib/logger.ts` - Structured logging utility
- `frontend/lib/cache.ts` - Redis/memory cache abstraction
- `frontend/lib/python-bridge.ts` - Clean interface for Python script execution

#### 3. Add More API Endpoints 🔄 TODO

**`/api/areas/[code]`** - Get detailed area information
- Method: GET
- Params: area code (e.g., "E1")
- Returns: Comprehensive area data from all sources

**`/api/commute/calculate`** - Calculate commute times
- Method: POST
- Body: `{ origin: string, destination: string }`
- Returns: Commute details (duration, modes, routes)

**`/api/personas`** - Get persona definitions
- Method: GET
- Returns: Available personas and their weight configurations

**`/api/health`** - Health check endpoint
- Method: GET
- Returns: System status, API availability, cache status

#### 4. Python Output Standardization 🔄 TODO

**Update Python Scripts** to output structured JSON:
- [`demo_pipeline.py`](demo_pipeline.py) - Add `--json` flag for JSON output
- [`tools/score_areas.py`](tools/score_areas.py) - Already returns JSON, verify format
- All execution scripts - Ensure consistent error format

**Standard Response Format**:
```json
{
  "success": true,
  "data": { /* actual data */ },
  "metadata": {
    "timestamp": "2026-01-31T16:00:00Z",
    "execution_time_ms": 1234,
    "sources_used": ["scansan", "tfl", "crime"]
  },
  "errors": []
}
```

---

## Phase 2: Serverless Infrastructure (Modal)

### Goal
Deploy core processing functions to Modal for scalable, serverless execution.

### Tasks

#### 1. Modal Configuration 🔄 TODO
**File**: `modal_config.py` (root)

**Functions to Deploy**:
- `fetch_recommendations` - Main recommendation pipeline
- `fetch_area_data` - Single area data fetching
- `calculate_commute` - Commute calculations
- `generate_explanation` - AI explanation generation

**Features**:
- Environment variable management
- Secret handling (API keys)
- Scheduled cache warming
- Async execution
- Automatic retries

#### 2. Modal Functions 🔄 TODO
**Directory**: `backend/modal/`

Create Modal-specific wrappers:
- `backend/modal/recommendations.py` - Recommendation pipeline
- `backend/modal/enrichment.py` - Data enrichment functions
- `backend/modal/cache_warmer.py` - Periodic cache warming

#### 3. API Integration 🔄 TODO

Update API routes to call Modal functions instead of subprocess:
- Install Modal Python SDK
- Add Modal client to API routes
- Handle Modal-specific errors
- Add fallback to local execution for development

---

## Phase 3: State Management & Caching

### Goal
Implement intelligent caching and state management for performance.

### Tasks

#### 1. Redis Cache Integration 🔄 TODO
**File**: `frontend/lib/cache.ts`

**Cache Strategy**:
- Area data: 24 hour TTL
- Commute calculations: 7 day TTL
- Crime data: 30 day TTL (updates monthly)
- School data: 90 day TTL (updates quarterly)

#### 2. Request Tracking 🔄 TODO
**File**: `frontend/lib/request-tracker.ts`

**Features**:
- Track in-flight requests
- Deduplicate concurrent requests
- Request cancellation support
- Progress tracking for long-running operations

#### 3. Session Management 🔄 TODO

**User Preferences Storage**:
- Store user preferences in session
- Cache recent searches
- Personalization data

---

## Phase 4: Production Readiness

### Tasks

#### 1. Rate Limiting 🔄 TODO
- Implement rate limiting per IP/user
- Queue management for heavy operations
- Graceful degradation

#### 2. Monitoring & Observability 🔄 TODO
- Add OpenTelemetry tracing
- Performance metrics
- Error tracking (Sentry)
- Usage analytics

#### 3. Testing 🔄 TODO
- Unit tests for all utilities
- Integration tests for API routes
- E2E tests for critical flows
- Load testing

#### 4. Documentation 🔄 TODO
- OpenAPI/Swagger spec
- API usage examples
- Deployment guide

---

## API Endpoints Specification

### Current Endpoints

#### `POST /api/recommendations`
**Status**: ✅ Live (needs refactoring)

**Request**:
```typescript
{
  persona: "student" | "parent" | "developer"
  budget: number
  locationType: "rent" | "buy"
  destination?: string
  maxAreas?: number
}
```

**Response**:
```typescript
{
  success: boolean
  persona: string
  budget: number
  recommendations: Array<{
    rank: number
    name: string
    areaCode: string
    score: number
    factors: Record<string, number>
    strengths: string[]
    weaknesses: string[]
  }>
}
```

### Planned Endpoints

#### `GET /api/areas/[code]`
**Status**: 🔄 Planned

Get comprehensive data for a specific area.

#### `POST /api/commute/calculate`
**Status**: 🔄 Planned

Calculate commute between two locations.

#### `GET /api/personas`
**Status**: 🔄 Planned

Get available persona definitions and configurations.

#### `GET /api/health`
**Status**: 🔄 Planned

System health check.

---

## Technology Stack

### Current (Phase 1 Complete)
- **Runtime**: Node.js (Next.js API routes)
- **Language**: TypeScript + Python
- **Framework**: Next.js 14 (App Router)
- **Validation**: ✅ Zod schemas (implemented)
- **Python Bridge**: ✅ `python-bridge.ts` utility (implemented)

### Phase 2: Production Architecture (Research Complete)

#### Serverless & Compute
- **Python Backend**: Modal (serverless Python functions)
  - Zero infrastructure management
  - Automatic scaling and retries
  - Cold start optimization
  - Built-in secret management
  - Pay-per-use: ~$0.00004 per CPU-second
  - **Status**: Config exists, needs deployment

- **Edge Runtime**: Vercel Edge Functions
  - Fast API validation at CDN edge
  - Minimal latency for health checks
  - **Status**: Ready to implement

#### Caching & State
- **Primary Cache**: Vercel KV (Upstash Redis)
  - Serverless-native (no connection pooling)
  - Global low-latency access
  - REST API compatible
  - Free tier: 10k commands/day
  - **TTL Strategy**:
    - Area data: 24 hours
    - Commute: 7 days
    - Crime: 30 days
    - Schools: 90 days

#### Rate Limiting & Security
- **Rate Limiter**: @upstash/ratelimit
  - Sliding window algorithm
  - Multiple tiers: 60/min, 1000/day, 10/hour (expensive ops)
  - Analytics included
  - **Status**: Ready to implement

#### Monitoring & Observability
- **Error Tracking**: Sentry (@sentry/nextjs)
  - Real-time error alerts
  - Stack trace analysis
  - Performance monitoring
  - Free tier: 5k errors/month

- **Structured Logging**: Axiom (@axiomhq/js)
  - Serverless-optimized
  - Real-time log streaming
  - SQL-like queries
  - Free tier: 500MB/month

- **Analytics**: Vercel Analytics
  - Web vitals tracking
  - API response times
  - Geographic distribution

#### Background Jobs & Workflows
- **Job Queue**: Inngest
  - Durable execution with retries
  - Step functions for complex workflows
  - Event-driven architecture
  - Use cases: AI generation, cache warming, batch processing
  - Free tier: 50k steps/month

#### HTTP Client & Utilities
- **API Client**: ky
  - Modern fetch wrapper
  - Automatic retries with exponential backoff
  - Request/response hooks
  - Timeout handling

- **OpenAPI Generation**: @anatine/zod-openapi
  - Auto-generate API docs from Zod schemas
  - Type-safe and always in sync

### Research Documentation
See [`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md) for:
- Detailed comparison of alternatives
- Implementation examples
- Cost analysis ($0-85/month for 10k users)
- Migration strategy
- Performance benchmarks
- Security considerations

---

## Dependencies to Add

### TypeScript/Node.js (Production)
```json
{
  "dependencies": {
    "@vercel/kv": "^1.0.1",
    "@upstash/ratelimit": "^1.0.0",
    "@sentry/nextjs": "^7.91.0",
    "@axiomhq/js": "^1.0.0",
    "@vercel/analytics": "^1.1.0",
    "inngest": "^3.0.0",
    "ky": "^1.0.0",
    "@anatine/zod-openapi": "^2.0.0",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "k6": "^0.47.0",
    "openapi-typescript": "^6.7.0"
  }
}
```

**Status**:
- ✅ `zod` - Already installed and implemented
- 🔄 Others - Ready to install (see [`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md))

### Python (Modal Functions)
```txt
# execution/requirements.txt
modal-client>=0.55.0
requests>=2.31.0
aiohttp>=3.9.0
pandas>=2.1.0
numpy>=1.26.0
structlog>=23.3.0
redis>=5.0.0
```

**Status**: Base requirements exist, needs Modal client addition

### Environment Variables (Required)
```env
# Existing
SCANSAN_API_KEY=
TFL_API_KEY=
OPENAI_API_KEY=

# New (Phase 2)
# Caching
KV_REST_API_URL=
KV_REST_API_TOKEN=

# Rate Limiting (uses same Redis)
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# Monitoring
SENTRY_DSN=
NEXT_PUBLIC_SENTRY_DSN=
AXIOM_TOKEN=
AXIOM_ORG_ID=

# Background Jobs
INNGEST_EVENT_KEY=
INNGEST_SIGNING_KEY=

# Modal Deployment
MODAL_ENDPOINT_URL=
MODAL_TOKEN_ID=
MODAL_TOKEN_SECRET=

# Feature Flags
NEXT_PUBLIC_USE_MODAL=false
NEXT_PUBLIC_USE_CACHE=true
NEXT_PUBLIC_USE_INNGEST=false
```

---

## Success Metrics

- [ ] API response time < 2s for recommendations
- [ ] 99.9% uptime for core endpoints
- [ ] < 1% error rate
- [ ] Cache hit rate > 60%
- [ ] Support 100+ concurrent users

---

## Next Steps

### Phase 1 - COMPLETE ✅
1. ✅ Create PLAN.md
2. ✅ Refactor `/api/recommendations` with validation
3. ✅ Create TypeScript types and utilities
4. ✅ Create error handling system
5. ✅ Create Python bridge utility
6. ✅ Add `/api/personas` endpoint
7. ✅ Add `/api/health` endpoint
8. ✅ Set up Modal configuration
9. ✅ Create API documentation

### Phase 2 - In Progress 🔄
1. 🔄 Deploy Modal functions to production
2. 🔄 Integrate Modal endpoints in Python bridge
3. 🔄 Add structured JSON output to Python scripts
4. 🔄 Implement caching layer (Redis/Vercel KV)
5. 🔄 Add remaining API endpoints (`/api/areas`, `/api/commute`)
6. 🔄 Add rate limiting
7. 🔄 Add monitoring and observability
8. 🔄 Write unit and integration tests

### Phase 3 - Future 📋
1. 📋 OpenAPI/Swagger specification
2. 📋 Performance optimization
3. 📋 Advanced caching strategies
4. 📋 WebSocket support for real-time updates
5. 📋 GraphQL API layer

---

## Notes

- **No UI Changes**: This plan focuses purely on backend/API layer
- **Python Scripts**: Execution layer scripts are deterministic and shouldn't need major changes
- **Directives**: Business logic lives in `directives/*.md` files
- **Testing**: Test locally before deploying to Modal

---

**Legend**:
- ✅ Complete
- 🔄 In Progress / Todo
- ⚠️ Needs Attention
- ❌ Blocked
