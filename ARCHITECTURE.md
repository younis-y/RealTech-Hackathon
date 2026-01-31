# System Architecture: RealTech-Hackathon

## Overview
RealTech-Hackathon is an AI-powered property recommendation engine designed to provide highly personalised area recommendations for UK property seekers. The system employs a **3-Layer AI Orchestration Architecture** that separates high-level directives from intelligent orchestration and deterministic execution scripts. By synthesising data from property intelligence, transport, crime, and education sources, it delivers ranked recommendations with natural language explanations and AI-generated video summaries.

## High-Level Architecture

```mermaid
flowchart TD
    subgraph ClientLayer [Client Layer]
        User([User]) --&gt; Frontend[Next.js Web App]
    end

    subgraph OrchestrationLayer [Layer 2: Orchestration]
        Frontend --&gt; Orchestrator[AI Orchestrator - Claude]
        Orchestrator --&gt; Directives[Layer 1: Directives - Markdown SOPs]
    end

    subgraph ExecutionLayer [Layer 3: Execution]
        Orchestrator --&gt; Scripts[Python Execution Scripts]
        Scripts --&gt; APIClients[API Clients]
    end

    subgraph DataLayer [Data &amp; External Services]
        APIClients --&gt; ScanSan[ScanSan Property Intelligence]
        APIClients --&gt; TfL[TfL Unified API]
        APIClients --&gt; Crime[UK Police Data API]
        APIClients --&gt; Ofsted[Ofsted Education Data]
        APIClients --&gt; Cache[(Redis Cache)]
        APIClients --&gt; DB[(PostgreSQL / Supabase)]
    end

    subgraph OutputLayer [Output Generation]
        Orchestrator --&gt; Explainer[NLG Explanation Generator]
        Orchestrator --&gt; Video[Video Explainer Generator]
    end
```

## Component Details

### 1. Client Layer (Next.js)
- **Role**: Provides an interactive interface for users to input their persona, budget, and preferences.
- **Technologies**: Next.js, TypeScript, Tailwind CSS.
- **State Management**: React Context / Hooks for managing user filters and result display.

### 2. Layer 1: Directives (The Brain)
- **Role**: Markdown-based Standard Operating Procedures (SOPs) that define the "how-to" for every system task (e.g., how to score a student persona).
- **Ownership**: Owns the business logic and system knowledge without hardcoded logic.

### 3. Layer 2: Orchestrator (The Manager)
- **Role**: An LLM-powered (Anthropic Claude) decision-making layer that reads directives, interprets user intent, and routes tasks to the appropriate execution scripts.
- **Technologies**: Anthropic Claude API, Python.

### 4. Layer 3: Execution (The Workers)
- **Role**: Deterministic Python scripts that perform the actual API calls, data cleaning, and scoring calculations.
- **Technologies**: Python, Pandas, NumPy, aiohttp.

### 5. Data &amp; Caching
- **Redis**: Used for aggressive caching of area-level data to reduce latency and API costs.
- **PostgreSQL**: Stores user profiles, saved recommendations, and historical feedback for system improvement.

## Data Flow
1. **Input**: User submits preferences via the Next.js frontend.
2. **Orchestration**: The Orchestrator reads `MASTER_ORCHESTRATION.md` and chooses the relevant directive SOP.
3. **Execution**: Python scripts are triggered in parallel to fetch data from ScanSan, TfL, and Crime APIs.
4. **Synthesis**: Data is aggregated, scored according to persona weights, and ranked.
5. **Output**: The Orchestrator generates natural language explanations and triggers video asset generation before returning results to the UI.

## Deployment &amp; Infrastructure
- **Frontend**: Hosted on Vercel.
- **Backend**: Containerised using Docker, deployed via Kubernetes / Managed Cloud Functions.
- **Database**: Managed PostgreSQL (Supabase).
- **Caching**: Managed Redis instance.
