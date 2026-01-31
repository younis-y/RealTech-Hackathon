# System Architecture: Veo Housing Platform

## Overview

The Veo Housing Platform is an AI-powered property recommendation engine designed to provide personalised, data-driven area recommendations for London property seekers. The system employs a unique 3-layer AI orchestration architecture that separates directive-based instructions (Layer 1) from intelligent routing and decision-making (Layer 2), and deterministic script execution (Layer 3). This architectural pattern ensures reliability, maintainability, and self-improvement capabilities whilst leveraging the probabilistic nature of large language models only where appropriate.

The primary goal of the system is to automate the complex process of location research, providing users with data-driven insights tailored to their specific lifestyle personas (e.g., students, parents, or investors).

## Key Requirements

### Functional
- **Persona-Driven Recommendations**: Tailor results based on specific user profiles and priorities.
- **Multi-Source Data Enrichment**: Integrate data from ScanSan, TfL, UK Police, and Ofsted APIs.
- **Natural Language Generation**: Provide human-readable explanations for all recommendations.
- **Multimedia Output**: Generate AI video explainers for top-ranked areas.

### Non-Functional
- **Scalability**: Handle concurrent API requests and data processing for multiple users.
- **Reliability**: Implement robust error handling, retries, and fallback mechanisms for external API dependencies.
- **Performance**: Minimise latency through aggressive caching and parallel execution.
- **Maintainability**: Use a directive-based approach to allow system updates without core code changes.

## High-Level Architecture

The system is built on a **3-Layer Orchestration Pattern**:

1.  **Layer 1: Directives (The Brain)**: Markdown-based Standard Operating Procedures (SOPs) that define the "how-to" for every system task.
2.  **Layer 2: Orchestrator (The Manager)**: An LLM-powered (Anthropic Claude) decision-making layer that reads directives and routes tasks.
3.  **Layer 3: Execution (The Workers)**: Deterministic Python scripts that perform the actual API calls and data processing.

```mermaid
graph TD
    User[User Interface/API] --> Orchestrator[Layer 2: AI Orchestrator
Claude LLM]
    Orchestrator --> Directives[Layer 1: Directives
Markdown SOPs]
    
    subgraph "Layer 3: Execution Scripts"
        Orchestrator --> ScanSan[scansan_api.py]
        Orchestrator --> TfL[tfl_commute.py]
        Orchestrator --> Crime[crime_data.py]
        Orchestrator --> Schools[schools_ofsted.py]
        Orchestrator --> Video[generate_video.py]
    end
    
    subgraph "External Services"
        ScanSan --> ScanSanAPI[ScanSan Property API]
        TfL --> TfLAPI[TfL Unified API]
        Crime --> PoliceAPI[UK Police Data API]
        Schools --> GIAS[GIAS / Ofsted API]
        Video --> VideoAI[Veo / Sora / LTX]
    end
    
    ScanSanAPI --> Cache[(Redis Cache)]
    TfLAPI --> Cache
    PoliceAPI --> Cache
    GIAS --> Cache
```

*This diagram illustrates the flow from a user request through the intelligent orchestration layer to the deterministic execution workers and external data providers.*

## Component Details

### AI Orchestrator (Layer 2)
- **Responsibilities**: Interpreting user intent, reading task-specific directives, routing calls to execution scripts, and synthesizing final results.
- **Technologies**: Anthropic Claude API, Python.
- **Communication**: Communicates with the UI via REST/CLI and with the Execution Layer via subprocess calls or function imports.

### Directives (Layer 1)
- **Responsibilities**: Defining the logic for data fetching, scoring weights for different personas, and output formats.
- **Technologies**: Markdown.
- **Ownership**: Owns the "system knowledge" and business logic.

### Execution Scripts (Layer 3)
- **Responsibilities**: Performing specific, deterministic tasks like API requests, data cleaning, and scoring.
- **Technologies**: Python (Pandas, NumPy, Requests, aiohttp).
- **Communication**: Stateless scripts that return structured JSON data to the Orchestrator.

### External Integrations
- **ScanSan API**: Provides property intelligence, investment quality, and affordability scores.
- **TfL API**: Calculates precise commute times to specific destinations.
- **UK Police API**: Fetches localized crime statistics and safety ratings.
- **GIAS/Ofsted**: Provides school performance data and catchment area information.

## Data Flow

### Typical Recommendation Flow
1. **Request**: User provides persona (e.g., "Student") and preferences (Budget, Destination).
2. **Orchestration**: The Orchestrator reads `MASTER_ORCHESTRATION.md` to determine the workflow.
3. **Fetching**: The Orchestrator triggers Layer 3 scripts in parallel to fetch data from ScanSan, TfL, and Crime APIs.
4. **Scoring**: Data is passed to the Scoring Engine which applies weights defined in the persona directives.
5. **Synthesis**: Results are ranked, and the Explainer Generator creates a natural language summary.
6. **Delivery**: The final ranked list and explanations are returned to the user.

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant D as Directives
    participant E as Execution Scripts
    participant C as Cache/APIs

    U->>O: Provide Persona & Preferences
    O->>D: Read Orchestration Rules
    D-->>O: Workflow Steps
    O->>E: Trigger Parallel Data Fetching
    E->>C: Check Cache / Call APIs
    C-->>E: Return Raw Data
    E-->>O: Return JSON Results
    O->>O: Rank & Synthesise
    O->>U: Deliver Recommendations
```

## Data Model (High-Level)

The system primarily handles structured JSON data objects:
- **AreaProfile**: Contains aggregated scores (Safety, Affordability, Commute) and raw metadata for a specific postcode district.
- **PersonaDefinition**: A configuration object defining the importance (weights) of different metrics for a specific user type.
- **RecommendationSet**: A ranked collection of AreaProfiles with generated narrative explanations.

## Infrastructure & Deployment

- **Deployment**: The system is designed to run in **Docker containers**, orchestrated by **Kubernetes** for production environments.
- **Environments**:
    - **Dev**: Local environment using `.env` files and local Redis.
    - **Staging**: Cloud-hosted environment for integration testing with full API access.
    - **Prod**: High-availability environment with auto-scaling and persistent Redis caching.

## Scalability & Reliability

- **Caching**: Aggressive caching using **Redis** ensures that repeated area requests do not hit external API rate limits and reduce latency.
- **Parallelism**: Uses **aiohttp** and Python's `asyncio` for non-blocking I/O during multi-source data fetching.
- **Fault Tolerance**: Exponential backoff retries for all external API calls and a fallback chain for video generation services.

## Security & Compliance

- **Auth**: API key management via environment variables and secret managers (e.g., AWS Secrets Manager).
- **Data Protection**: No personally identifiable information (PII) is stored; all property data is aggregated at the postcode district level.
- **Compliance**: Adheres to the terms of use for all integrated UK government and third-party APIs.

## Observability

- **Logging**: Structured logging using **structlog** to track orchestration decisions and execution script performance.
- **Metrics**: Monitoring API latency, cache hit rates, and LLM token usage.

## Trade-offs & Decisions

- **LLM vs. Hardcoded Logic**: We chose LLM orchestration to allow for flexible, natural language interactions and easier system updates via Markdown, at the cost of slight latency and token expenses.
- ** পোস্টকোড District vs. Full Postcode**: Data is aggregated at the district level (e.g., E1) to ensure high cache hit rates and comply with data privacy while remaining useful for area-level recommendations.

## Future Improvements

- **Real-time Market Data**: Integrating live property listings to show current availability.
- **Feedback Loop**: Implementing a reinforcement learning layer to improve recommendation accuracy based on user interactions.
- **Geo-Spatial Visualisation**: Adding a full map interface to the front-end for better area comparison.
