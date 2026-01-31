# Research Findings: Modern Serverless Architecture for Veo Platform

**Researcher**: Data & Strategy Lead  
**Date**: 2026-01-31  
**Status**: Phase 2 Technology Research  
**Focus Areas**: Serverless Deployment, Caching, Rate Limiting, Monitoring

---

## Executive Summary

This document provides research findings for modernizing the Veo Housing Platform backend infrastructure. The focus is on serverless-friendly, production-ready libraries and services that integrate seamlessly with Next.js 14, Modal, and TypeScript.

**Key Recommendations**:
1. **Serverless Deployment**: Modal + Vercel Edge for hybrid architecture
2. **Caching**: Vercel KV (Redis) for seamless integration
3. **Rate Limiting**: Upstash Rate Limit for serverless-native solution
4. **Monitoring**: Vercel Analytics + Sentry for observability
5. **Queue Management**: Inngest for durable workflows

---

## 1. Serverless Deployment Architecture

### Current State
- Python scripts executed via `child_process.spawn()` in Next.js API routes
- Inefficient, slow cold starts, no scalability
- [`modal_config.py`](modal_config.py) exists but not fully integrated

### Recommended Solution: **Modal + Vercel Hybrid**

#### Modal (Python Backend)
**Why Modal?**
- Purpose-built for serverless Python
- Zero infrastructure management
- Automatic scaling and retries
- Native support for long-running tasks
- Built-in secret management
- Cold start optimization with container caching

**Implementation Strategy**:
```python
# modal_config.py enhancement
import modal

stub = modal.Stub("veo-housing-platform")

# Container image with all dependencies
image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

# Secrets management
secrets = [
    modal.Secret.from_name("scansan-api-key"),
    modal.Secret.from_name("tfl-api-key"),
    modal.Secret.from_name("openai-api-key")
]

@stub.function(
    image=image,
    secrets=secrets,
    timeout=300,  # 5 min timeout
    retries=2
)
def fetch_recommendations(persona: str, budget: int, location_type: str, **kwargs):
    """Main recommendation pipeline as serverless function"""
    # Import execution scripts
    from execution.score_and_rank import score_areas
    # ... implementation
    return results

# Scheduled cache warming
@stub.function(schedule=modal.Cron("0 2 * * *"))  # Daily at 2 AM
def warm_cache():
    """Pre-fetch common area data"""
    pass
```

**Key Features**:
- **Web endpoints**: Modal can expose functions as HTTPS endpoints
- **Async execution**: Non-blocking Python execution
- **Volume mounts**: Persistent storage for caching
- **GPU support**: Future AI model deployment
- **Automatic retries**: Built-in fault tolerance

**Integration with Next.js**:
```typescript
// frontend/lib/modal-client.ts
export async function callModalFunction<T>(
  functionName: string,
  params: Record<string, any>
): Promise<T> {
  const modalUrl = process.env.MODAL_ENDPOINT_URL;
  const response = await fetch(`${modalUrl}/${functionName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  return response.json();
}
```

**Cost Efficiency**:
- Pay-per-use model (no idle costs)
- First 30 hours/month free
- ~$0.00004 per CPU-second after free tier

**Alternatives Considered**:
- ❌ **AWS Lambda**: Complex setup, cold starts, IAM management
- ❌ **Google Cloud Functions**: Limited Python support, vendor lock-in
- ✅ **Modal**: Python-first, developer-friendly, minimal config

---

## 2. Caching Strategy

### Current State
- No caching implemented
- Every request hits external APIs
- High latency and rate limit risk

### Recommended Solution: **Vercel KV (Upstash Redis)**

#### Why Vercel KV?
- **Serverless-native**: No connection pooling issues
- **Edge network**: Global low-latency access
- **Zero config**: Native Vercel integration
- **Generous free tier**: 10k commands/day
- **REST API**: Works in Edge Runtime

**Implementation**:
```typescript
// frontend/lib/cache.ts
import { kv } from '@vercel/kv';

export class CacheManager {
  private static TTL = {
    AREA_DATA: 86400,      // 24 hours
    COMMUTE: 604800,       // 7 days
    CRIME_DATA: 2592000,   // 30 days
    SCHOOL_DATA: 7776000   // 90 days
  };

  static async get<T>(key: string): Promise<T | null> {
    return await kv.get<T>(key);
  }

  static async set<T>(
    key: string,
    value: T,
    ttl: number
  ): Promise<void> {
    await kv.set(key, value, { ex: ttl });
  }

  static async cacheAreaData(areaCode: string, data: any): Promise<void> {
    await this.set(`area:${areaCode}`, data, this.TTL.AREA_DATA);
  }

  static async getAreaData(areaCode: string): Promise<any> {
    return await this.get(`area:${areaCode}`);
  }
}
```

**Cache Key Strategy**:
```
area:{areaCode}                    # Full area data
commute:{origin}:{destination}     # Commute calculations
crime:{areaCode}:{month}           # Monthly crime stats
schools:{areaCode}                 # School ratings
recommendations:{hash}             # Full recommendation results
```

**Cache Invalidation**:
- Time-based expiry (TTL)
- Manual invalidation via admin endpoint
- Version-based invalidation (add version to key)

**Fallback Strategy**:
```typescript
async function getCachedOrFetch<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number
): Promise<T> {
  const cached = await CacheManager.get<T>(key);
  if (cached) return cached;
  
  const fresh = await fetchFn();
  await CacheManager.set(key, fresh, ttl);
  return fresh;
}
```

**Alternatives Considered**:
- ❌ **Redis Cloud**: Requires connection pooling, complex setup
- ❌ **Memcached**: No persistence, limited features
- ✅ **Vercel KV**: Serverless-native, zero config

---

## 3. Rate Limiting

### Current State
- No rate limiting
- Vulnerable to abuse and API quota exhaustion

### Recommended Solution: **Upstash Rate Limit**

#### Why Upstash Rate Limit?
- **Serverless-optimized**: Works with Edge Runtime
- **Zero config**: Built on Upstash Redis
- **Multiple algorithms**: Sliding window, token bucket
- **Global**: Works across all serverless instances
- **Vercel integration**: Native support

**Implementation**:
```typescript
// frontend/lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

// Create rate limiter instances
export const rateLimiters = {
  // 60 requests per minute per IP
  perMinute: new Ratelimit({
    redis: Redis.fromEnv(),
    limiter: Ratelimit.slidingWindow(60, '1 m'),
    analytics: true,
    prefix: 'ratelimit:minute'
  }),
  
  // 1000 requests per day per IP
  perDay: new Ratelimit({
    redis: Redis.fromEnv(),
    limiter: Ratelimit.slidingWindow(1000, '1 d'),
    analytics: true,
    prefix: 'ratelimit:day'
  }),
  
  // Expensive operations (AI explanations) - 10 per hour
  expensive: new Ratelimit({
    redis: Redis.fromEnv(),
    limiter: Ratelimit.slidingWindow(10, '1 h'),
    analytics: true,
    prefix: 'ratelimit:expensive'
  })
};

// Middleware for API routes
export async function checkRateLimit(
  identifier: string,
  limiter: Ratelimit = rateLimiters.perMinute
): Promise<{ success: boolean; limit: number; remaining: number; reset: number }> {
  const { success, limit, remaining, reset } = await limiter.limit(identifier);
  return { success, limit, remaining, reset };
}
```

**Usage in API Routes**:
```typescript
// frontend/app/api/recommendations/route.ts
import { checkRateLimit, rateLimiters } from '@/lib/rate-limit';
import { getClientIp } from '@/lib/utils';

export async function POST(request: Request) {
  const ip = getClientIp(request);
  
  // Check rate limits
  const minuteLimit = await checkRateLimit(ip, rateLimiters.perMinute);
  if (!minuteLimit.success) {
    return new Response(JSON.stringify({
      error: 'Rate limit exceeded',
      limit: minuteLimit.limit,
      remaining: 0,
      reset: minuteLimit.reset
    }), { 
      status: 429,
      headers: {
        'X-RateLimit-Limit': String(minuteLimit.limit),
        'X-RateLimit-Remaining': String(0),
        'X-RateLimit-Reset': String(minuteLimit.reset)
      }
    });
  }
  
  // Process request...
}
```

**Features**:
- **Multiple strategies**: Per-IP, per-user, per-API-key
- **Tiered limits**: Different limits for different operations
- **Analytics**: Track usage patterns
- **Graceful degradation**: Return 429 with retry information

**Cost**: Free up to 10k requests/day, then $0.20 per 100k requests

**Alternatives Considered**:
- ❌ **Custom Redis implementation**: Reinventing the wheel
- ❌ **Express-rate-limit**: Not serverless-compatible
- ✅ **Upstash Rate Limit**: Purpose-built, serverless-native

---

## 4. Monitoring & Observability

### Current State
- No structured logging
- No error tracking
- No performance monitoring

### Recommended Solution: **Vercel Analytics + Sentry + Axiom**

#### 4.1 Vercel Analytics
**Purpose**: Web vitals and traffic analytics

```typescript
// Next.js automatic integration
// Just add to package.json:
"@vercel/analytics": "^1.1.0"

// Add to app/layout.tsx:
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

**Tracks**:
- Page load times
- API response times
- User interactions
- Geographic distribution

#### 4.2 Sentry (Error Tracking)
**Purpose**: Exception monitoring and debugging

```typescript
// frontend/lib/sentry.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,  // 10% of transactions
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Sentry.Integrations.Prisma({ client: null })
  ],
  beforeSend(event, hint) {
    // Filter out sensitive data
    if (event.request?.data) {
      delete event.request.data.apiKey;
    }
    return event;
  }
});

// Usage in API routes
export function handleError(error: Error, context: Record<string, any>) {
  Sentry.captureException(error, {
    tags: { service: 'api' },
    contexts: { details: context }
  });
}
```

**Features**:
- Real-time error alerts
- Stack trace analysis
- Performance monitoring
- User impact tracking
- Integration with GitHub for code context

**Cost**: Free up to 5k errors/month

#### 4.3 Axiom (Structured Logging)
**Purpose**: Serverless-friendly log aggregation

```typescript
// frontend/lib/logger.ts
import { Axiom } from '@axiomhq/js';

const axiom = new Axiom({
  token: process.env.AXIOM_TOKEN,
  orgId: process.env.AXIOM_ORG_ID
});

export class Logger {
  static async log(
    level: 'info' | 'warn' | 'error',
    message: string,
    metadata: Record<string, any> = {}
  ) {
    await axiom.ingest('veo-platform', [{
      _time: new Date().toISOString(),
      level,
      message,
      ...metadata,
      environment: process.env.NODE_ENV
    }]);
  }

  static info(message: string, meta?: Record<string, any>) {
    return this.log('info', message, meta);
  }

  static error(message: string, error: Error, meta?: Record<string, any>) {
    return this.log('error', message, {
      ...meta,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    });
  }
}

// Flush logs at end of serverless function
export async function flushLogs() {
  await axiom.flush();
}
```

**Usage Pattern**:
```typescript
export async function POST(request: Request) {
  const startTime = Date.now();
  
  try {
    await Logger.info('Recommendation request started', {
      method: 'POST',
      path: '/api/recommendations'
    });
    
    // ... process request
    
    await Logger.info('Recommendation request completed', {
      duration: Date.now() - startTime
    });
  } catch (error) {
    await Logger.error('Recommendation request failed', error, {
      duration: Date.now() - startTime
    });
  } finally {
    await flushLogs();
  }
}
```

**Features**:
- Serverless-optimized (no long-lived connections)
- Real-time log streaming
- SQL-like queries
- Dashboard creation
- Alerts and notifications

**Cost**: Free up to 500MB/month

**Alternatives Considered**:
- ❌ **Winston/Pino**: Not serverless-friendly (connection pooling issues)
- ❌ **CloudWatch**: AWS vendor lock-in
- ✅ **Axiom**: Purpose-built for serverless

---

## 5. Queue Management & Background Jobs

### Current State
- Long-running tasks block API responses
- No retry mechanism for failed operations
- AI explanation generation is synchronous

### Recommended Solution: **Inngest**

#### Why Inngest?
- **Serverless-native**: Works with Vercel/Next.js
- **Durable execution**: Automatic retries and recovery
- **Visual workflow**: Debug flow in real-time
- **Type-safe**: Full TypeScript support
- **Zero infrastructure**: No queue servers needed

**Implementation**:
```typescript
// frontend/lib/inngest/client.ts
import { Inngest } from 'inngest';

export const inngest = new Inngest({ 
  name: 'Veo Platform',
  id: 'veo-platform'
});

// Define events
export type Events = {
  'recommendation/requested': {
    data: {
      requestId: string;
      persona: string;
      budget: number;
      includeExplanations: boolean;
    };
  };
  'explanation/generate': {
    data: {
      areaCode: string;
      context: Record<string, any>;
    };
  };
  'cache/warm': {
    data: {
      areaCode: string;
    };
  };
};
```

**Background Job Functions**:
```typescript
// frontend/lib/inngest/functions/generate-explanation.ts
import { inngest } from '../client';

export const generateExplanation = inngest.createFunction(
  {
    name: 'Generate AI Explanation',
    id: 'generate-explanation',
    retries: 3,
    rateLimit: {
      limit: 10,
      period: '1m'
    }
  },
  { event: 'explanation/generate' },
  async ({ event, step }) => {
    // Step 1: Fetch area data (cached automatically)
    const areaData = await step.run('fetch-area-data', async () => {
      return await getAreaData(event.data.areaCode);
    });

    // Step 2: Generate explanation using AI
    const explanation = await step.run('generate-ai-text', async () => {
      return await callModalFunction('generate_explanation', {
        area_code: event.data.areaCode,
        context: event.data.context
      });
    });

    // Step 3: Cache result
    await step.run('cache-explanation', async () => {
      await CacheManager.set(
        `explanation:${event.data.areaCode}`,
        explanation,
        3600  // 1 hour
      );
    });

    return { explanation };
  }
);
```

**API Integration**:
```typescript
// frontend/app/api/recommendations/route.ts
import { inngest } from '@/lib/inngest/client';

export async function POST(request: Request) {
  const body = await request.json();
  
  // Return fast response
  const quickResults = await getQuickRecommendations(body);
  
  // Trigger background job for detailed explanations
  if (body.includeExplanations) {
    await inngest.send({
      name: 'explanation/generate',
      data: {
        areaCode: quickResults.recommendations[0].areaCode,
        context: body
      }
    });
  }
  
  return Response.json({
    ...quickResults,
    explanationsStatus: 'processing',
    checkBackUrl: `/api/results/${quickResults.id}`
  });
}
```

**Features**:
- **Step functions**: Break complex workflows into steps
- **Automatic retries**: Exponential backoff
- **Debouncing**: Prevent duplicate jobs
- **Scheduled jobs**: Cron-like scheduling
- **Event-driven**: React to events across your app
- **Middleware**: Add logging, auth, etc.

**Use Cases**:
1. **Async AI generation**: Generate explanations without blocking
2. **Cache warming**: Pre-populate cache for popular areas
3. **Batch processing**: Process multiple areas in parallel
4. **Retry logic**: Automatically retry failed API calls

**Cost**: Free up to 50k steps/month

**Alternatives Considered**:
- ❌ **Bull/BullMQ**: Requires Redis connection pooling
- ❌ **AWS SQS**: Vendor lock-in, complex setup
- ✅ **Inngest**: Serverless-native, developer-friendly

---

## 6. Additional Recommendations

### 6.1 Request Deduplication
**Library**: `p-memoize` with Redis backend

```typescript
import pMemoize from 'p-memoize';
import { CacheManager } from '@/lib/cache';

const memoizedFetch = pMemoize(
  async (key: string) => {
    return await expensiveOperation(key);
  },
  {
    cacheKey: (args) => args[0],
    cache: {
      async get(key) {
        return await CacheManager.get(key);
      },
      async set(key, value) {
        await CacheManager.set(key, value, 3600);
      },
      async has(key) {
        return (await CacheManager.get(key)) !== null;
      },
      async delete(key) {
        // Implement if needed
      }
    }
  }
);
```

### 6.2 API Client with Retry Logic
**Library**: `ky` (modern fetch wrapper)

```typescript
import ky from 'ky';

export const apiClient = ky.create({
  timeout: 30000,
  retry: {
    limit: 3,
    methods: ['get', 'post'],
    statusCodes: [408, 413, 429, 500, 502, 503, 504],
    backoffLimit: 3000
  },
  hooks: {
    beforeRequest: [
      async (request) => {
        // Add auth headers
        const apiKey = process.env.API_KEY;
        if (apiKey) {
          request.headers.set('Authorization', `Bearer ${apiKey}`);
        }
      }
    ],
    afterResponse: [
      async (_request, _options, response) => {
        // Log response times
        await Logger.info('API call completed', {
          url: response.url,
          status: response.status,
          duration: response.headers.get('X-Response-Time')
        });
      }
    ]
  }
});
```

### 6.3 Input Validation at Edge
**Library**: `zod` + Edge Runtime

Already implemented in [`frontend/lib/validators.ts`](frontend/lib/validators.ts), but ensure it runs at Edge:

```typescript
// frontend/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: '/api/:path*',
  runtime: 'edge'  // Run at edge for fastest validation
};

export async function middleware(request: NextRequest) {
  // Validate before hitting API routes
  if (request.method === 'POST') {
    try {
      const body = await request.json();
      // Validate with Zod schema
      recommendationRequestSchema.parse(body);
    } catch (error) {
      return NextResponse.json(
        { error: 'Invalid request body' },
        { status: 400 }
      );
    }
  }
  
  return NextResponse.next();
}
```

### 6.4 OpenAPI Specification Generation
**Library**: `@anatine/zod-openapi`

```typescript
import { extendZodWithOpenApi } from '@anatine/zod-openapi';
import { z } from 'zod';

extendZodWithOpenApi(z);

// Enhance existing schemas with OpenAPI metadata
export const recommendationRequestSchema = z.object({
  persona: z.enum(['student', 'parent', 'developer'])
    .openapi({ 
      description: 'User persona type',
      example: 'student'
    }),
  budget: z.number().positive()
    .openapi({
      description: 'Budget in GBP',
      example: 1000
    })
  // ... rest of schema
}).openapi({
  title: 'RecommendationRequest',
  description: 'Request body for generating area recommendations'
});

// Auto-generate OpenAPI spec
import { generateOpenApiDocument } from '@anatine/zod-openapi';

export const openApiSpec = generateOpenApiDocument({
  info: {
    title: 'Veo Housing Platform API',
    version: '1.0.0'
  },
  servers: [{ url: '/api' }],
  schemas: [recommendationRequestSchema]
});
```

---

## 7. Technology Stack Summary

### Production Stack (Recommended)

| Category | Library/Service | Version | Purpose |
|----------|----------------|---------|---------|
| **Serverless Functions** | Modal | Latest | Python backend execution |
| **Edge Runtime** | Vercel Edge | Built-in | Fast API responses |
| **Caching** | Vercel KV (Upstash) | ^1.0.0 | Redis-compatible cache |
| **Rate Limiting** | @upstash/ratelimit | ^1.0.0 | API rate limiting |
| **Error Tracking** | @sentry/nextjs | ^7.9 1.0 | Exception monitoring |
| **Logging** | @axiomhq/js | ^1.0.0 | Structured logs |
| **Analytics** | @vercel/analytics | ^1.1.0 | Web vitals tracking |
| **Background Jobs** | inngest | ^3.0.0 | Durable workflows |
| **API Client** | ky | ^1.0.0 | Retry-enabled HTTP |
| **Validation** | zod | ^3.22.4 | Runtime validation |
| **OpenAPI** | @anatine/zod-openapi | ^2.0.0 | API documentation |

### Development Dependencies

```json
{
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.3",
    "vitest": "^1.0.0",
    "openapi-typescript": "^6.7.0"
  }
}
```

### Python Dependencies (Modal)

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

---

## 8. Implementation Roadmap

### Phase 2A: Foundation (Week 1)
1. ✅ Set up Vercel KV for caching
2. ✅ Implement rate limiting with Upstash
3. ✅ Add Sentry error tracking
4. ✅ Deploy basic Modal functions

### Phase 2B: Optimization (Week 2)
1. 🔄 Add Axiom logging
2. 🔄 Implement Inngest for background jobs
3. 🔄 Set up monitoring dashboards
4. 🔄 Add request deduplication

### Phase 2C: Production Readiness (Week 3)
1. 📋 Load testing
2. 📋 Performance optimization
3. 📋 OpenAPI spec generation
4. 📋 Documentation updates

---

## 9. Cost Analysis

### Monthly Cost Estimates (Up to 10k users)

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| Vercel Hosting | 100GB bandwidth | $0-20/month |
| Vercel KV | 10k commands/day | $0-10/month |
| Modal | 30 CPU-hours/month | $0-50/month |
| Upstash Rate Limit | 10k requests/day | $0-5/month |
| Sentry | 5k errors/month | Free |
| Axiom | 500MB logs/month | Free |
| Inngest | 50k steps/month | Free |
| **Total** | | **$0-85/month** |

*Costs scale linearly with usage beyond free tiers*

---

## 10. Security Considerations

### API Key Management
```typescript
// Use environment variables, never hardcode
const SECRETS = {
  SCANSAN_KEY: process.env.SCANSAN_API_KEY,
  TFL_KEY: process.env.TFL_API_KEY,
  OPENAI_KEY: process.env.OPENAI_API_KEY
} as const;

// Verify secrets at startup
export function validateSecrets() {
  const missing = Object.entries(SECRETS)
    .filter(([_, value]) => !value)
    .map(([key]) => key);
  
  if (missing.length > 0) {
    throw new Error(`Missing secrets: ${missing.join(', ')}`);
  }
}
```

### CORS Configuration
```typescript
// frontend/middleware.ts
const ALLOWED_ORIGINS = [
  'https://veo-platform.vercel.app',
  'http://localhost:3000'  // Dev only
];

export function corsMiddleware(request: NextRequest) {
  const origin = request.headers.get('origin');
  
  if (origin && !ALLOWED_ORIGINS.includes(origin)) {
    return new NextResponse('CORS not allowed', { status: 403 });
  }
  
  return NextResponse.next({
    headers: {
      'Access-Control-Allow-Origin': origin || '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
  });
}
```

### Data Sanitization
```typescript
// Always sanitize user input
import DOMPurify from 'isomorphic-dompurify';

export function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, { 
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: []
  });
}
```

---

## 11. Performance Benchmarks

### Target Metrics (99th percentile)

| Operation | Current | Target | Strategy |
|-----------|---------|--------|----------|
| GET /api/personas | 50ms | 10ms | Edge caching |
| GET /api/health | 200ms | 50ms | Parallel checks |
| POST /api/recommendations (no AI) | 4s | 2s | Modal + cache |
| POST /api/recommendations (with AI) | 12s | 5s | Background jobs |
| Cache hit rate | 0% | 70% | Aggressive caching |

### Optimization Techniques

1. **Parallel Data Fetching**: Use `Promise.all()` for independent API calls
2. **Incremental Static Regeneration**: Pre-render popular areas
3. **Edge Caching**: Cache GET responses at CDN level
4. **Response Streaming**: Stream results as they're ready
5. **Code Splitting**: Lazy load non-critical modules

---

## 12. Migration Strategy

### Step 1: Non-Breaking Changes (Week 1)
- ✅ Add caching layer (no breaking changes)
- ✅ Add monitoring (invisible to users)
- ✅ Add rate limiting (graceful degradation)

### Step 2: Gradual Modal Migration (Week 2)
- Deploy Modal functions alongside existing Python subprocesses
- Use feature flags to route traffic
- Monitor performance and errors
- Gradually increase traffic to Modal

### Step 3: Deprecate Old System (Week 3)
- Once Modal functions are stable, remove subprocess calls
- Update documentation
- Archive old Python execution method

### Feature Flags
```typescript
// frontend/lib/feature-flags.ts
export const FEATURES = {
  USE_MODAL: process.env.NEXT_PUBLIC_USE_MODAL === 'true',
  USE_CACHE: process.env.NEXT_PUBLIC_USE_CACHE === 'true',
  USE_BACKGROUND_JOBS: process.env.NEXT_PUBLIC_USE_INNGEST === 'true'
} as const;

// Graceful fallback
export async function fetchWithFallback<T>(
  modalFn: () => Promise<T>,
  fallbackFn: () => Promise<T>
): Promise<T> {
  if (FEATURES.USE_MODAL) {
    try {
      return await modalFn();
    } catch (error) {
      Logger.warn('Modal function failed, falling back', { error });
      return await fallbackFn();
    }
  }
  return await fallbackFn();
}
```

---

## 13. Testing Strategy

### Unit Tests
```typescript
// frontend/__tests__/unit/lib/cache.test.ts
import { describe, it, expect, vi } from 'vitest';
import { CacheManager } from '@/lib/cache';

describe('CacheManager', () => {
  it('should cache and retrieve data', async () => {
    const testData = { foo: 'bar' };
    await CacheManager.set('test:key', testData, 60);
    
    const retrieved = await CacheManager.get('test:key');
    expect(retrieved).toEqual(testData);
  });

  it('should return null for expired cache', async () => {
    vi.useFakeTimers();
    
    await CacheManager.set('test:expire', 'value', 1);
    vi.advanceTimersByTime(2000);
    
    const retrieved = await CacheManager.get('test:expire');
    expect(retrieved).toBeNull();
  });
});
```

### Integration Tests
```typescript
// frontend/__tests__/integration/api/recommendations.test.ts
import { describe, it, expect } from 'vitest';

describe('POST /api/recommendations', () => {
  it('should return recommendations for valid request', async () => {
    const response = await fetch('http://localhost:3000/api/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        persona: 'student',
        budget: 1000,
        locationType: 'rent'
      })
    });
    
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.recommendations).toBeInstanceOf(Array);
  });

  it('should respect rate limits', async () => {
    // Make 61 requests rapidly
    const requests = Array(61).fill(null).map(() =>
      fetch('http://localhost:3000/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona: 'student',
          budget: 1000,
          locationType: 'rent'
        })
      })
    );
    
    const responses = await Promise.all(requests);
    const rateLimited = responses.filter(r => r.status === 429);
    
    expect(rateLimited.length).toBeGreaterThan(0);
  });
});
```

### Load Tests (k6)
```javascript
// loadtest/recommendations.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 50 },   // Stay at 50 for 3 min
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95% under 2s
    http_req_failed: ['rate<0.01'],     // <1% errors
  },
};

export default function () {
  const payload = JSON.stringify({
    persona: 'student',
    budget: 1000,
    locationType: 'rent'
  });

  const response = http.post(
    'https://veo-platform.vercel.app/api/recommendations',
    payload,
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });

  sleep(1);
}
```

Run with: `k6 run loadtest/recommendations.js`

---

## 14. Documentation Requirements

### OpenAPI Spec
Auto-generate from Zod schemas using `@anatine/zod-openapi`

### Code Documentation
Use JSDoc comments for all public functions:
```typescript
/**
 * Fetches area recommendations based on user preferences
 * 
 * @param request - The recommendation request parameters
 * @returns Promise resolving to ranked area recommendations
 * @throws {ValidationError} If request parameters are invalid
 * @throws {ExternalAPIError} If external APIs fail
 * 
 * @example
 * ```ts
 * const recommendations = await getRecommendations({
 *   persona: 'student',
 *   budget: 1000,
 *   locationType: 'rent'
 * });
 * ```
 */
export async function getRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  // Implementation
}
```

### README Updates
Update [`PLAN.md`](PLAN.md) and [`BACKEND_README.md`](BACKEND_README.md) with:
- New architecture diagrams
- Setup instructions for new services
- Environment variable requirements
- Deployment procedures

---

## 15. Conclusion & Next Steps

### Key Takeaways

1. **Modal is the right choice** for serverless Python execution
   - Zero infrastructure, automatic scaling
   - Native retry and timeout handling
   - Cost-effective pay-per-use model

2. **Vercel KV + Upstash ecosystem** provides seamless integration
   - Caching, rate limiting, background jobs
   - All serverless-native, zero connection pooling issues

3. **Modern observability stack** ensures production readiness
   - Sentry for errors, Axiom for logs, Vercel Analytics for metrics
   - Real-time visibility into system health

4. **Gradual migration** minimizes risk
   - Feature flags allow A/B testing
   - Fallback mechanisms ensure reliability
   - Can roll back at any time

### Immediate Actions for Builder

1. **Add dependencies to [`frontend/package.json`](frontend/package.json)**:
   ```json
   {
     "dependencies": {
       "@vercel/kv": "^1.0.1",
       "@upstash/ratelimit": "^1.0.0",
       "@sentry/nextjs": "^7.91.0",
       "@axiomhq/js": "^1.0.0",
       "inngest": "^3.0.0",
       "ky": "^1.0.0",
       "@anatine/zod-openapi": "^2.0.0"
     }
   }
   ```

2. **Set up environment variables** (add to `.env.local`):
   ```env
   # Caching
   KV_REST_API_URL=
   KV_REST_API_TOKEN=

   # Rate Limiting
   UPSTASH_REDIS_REST_URL=
   UPSTASH_REDIS_REST_TOKEN=

   # Monitoring
   SENTRY_DSN=
   AXIOM_TOKEN=
   AXIOM_ORG_ID=

   # Background Jobs
   INNGEST_EVENT_KEY=
   INNGEST_SIGNING_KEY=

   # Modal
   MODAL_ENDPOINT_URL=
   MODAL_TOKEN_ID=
   MODAL_TOKEN_SECRET=
   ```

3. **Update [`modal_config.py`](modal_config.py)** with production functions

4. **Create new utility files**:
   - `frontend/lib/cache.ts`
   - `frontend/lib/rate-limit.ts`
   - `frontend/lib/logger.ts`
   - `frontend/lib/modal-client.ts`
   - `frontend/lib/inngest/client.ts`

5. **Update API routes** to use new infrastructure

### Success Criteria

- ✅ API response time < 2s (currently 4s)
- ✅ Cache hit rate > 60% (currently 0%)
- ✅ Error tracking in place
- ✅ Rate limiting active
- ✅ Modal functions deployed
- ✅ Background jobs for AI generation

---

**Research completed by**: Data & Strategy Agent  
**Ready for implementation by**: Builder Agent  
**Reviewed by**: N/A (pending)  
**Status**: Ready for Architecture section update in PLAN.md