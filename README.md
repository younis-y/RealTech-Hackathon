# RealTech-Hackathon
&gt; AI-powered property recommendation engine with intelligent orchestration and multi-source data enrichment.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## Description
RealTech-Hackathon is an intelligent property recommendation system that leverages a 3-layer AI orchestration architecture to generate highly personalised area recommendations for London property seekers. The platform synthesises live data from property intelligence, transport, crime statistics, and education ratings to provide clear, data-driven justifications for every recommendation. It targets students, parents, and property developers looking for data-backed location insights.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Screenshots / Demo](#screenshots--demo)
- [API / CLI Reference](#api--cli-reference)
- [Tests](#tests)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **3-Layer AI Orchestration**: Decouples directive-based logic (Layer 1) from intelligent routing (Layer 2) and deterministic execution (Layer 3).
- **Persona-Driven Scoring**: Tailored ranking algorithms for specific lifestyle profiles (e.g., Student, Parent, Developer).
- **Multi-Source Enrichment**: Integrates ScanSan, TfL Unified API, UK Police Data, and Ofsted ratings.
- **AI-Powered Explanations**: Generates natural language justifications for every area recommendation.
- **Self-Annealing Error Handling**: Automatically diagnoses and fixes API-related failures within the orchestration layer.

## Tech Stack
- **Backend**: Python 3.9+, Anthropic Claude API (Orchestration & NLG)
- **Frontend**: Next.js (React), TypeScript, Tailwind CSS
- **Data Pipeline**: Pandas, NumPy, aiohttp (Async I/O)
- **Cache & Infra**: Redis, structlog, python-dotenv
- **External Services**: ScanSan API, TfL API, UK Police Data API

## Architecture Overview

```mermaid
flowchart TD
    User --&gt; Orchestrator
    Orchestrator --&gt; Directives
    Orchestrator --&gt; Execution
    Execution --&gt; ExternalAPIs
    Execution --&gt; Cache
    Orchestrator --&gt; Output

    subgraph Layer2 [Orchestrator]
    Orchestrator[AI Orchestrator - Claude]
    end

    subgraph Layer1 [Directives]
    Directives[Markdown SOPs]
    end

    subgraph Layer3 [Execution]
    Execution[Python Scripts]
    end

    subgraph External [Data Sources]
    ExternalAPIs[ScanSan, TfL, Crime]
    Cache[(Redis Cache)]
    end
```

The system follows a modular 3-layer design where the AI Orchestrator (Claude) reads high-level Markdown SOPs to determine which Python execution scripts to trigger. These scripts interact with external APIs and a Redis cache to return structured data for final ranking and synthesis.

## Installation
### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend)
- Redis server

### Step-by-Step Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/younis-y/RealTech-Hackathon.git
   cd RealTech-Hackathon
   ```

2. **Backend Setup**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

## Usage
### CLI Demo
To run the full recommendation pipeline via the CLI:
```bash
python demo_pipeline.py --persona student --budget 1200 --destination UCL
```

### Web Interface
To start the frontend development server:
```bash
cd frontend
npm run dev
```

## Configuration
Create a `.env` file in the root directory based on `.env.template`:
```ini
ANTHROPIC_API_KEY=your_key_here
SCANSAN_API_KEY=your_key_here
TFL_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379
```

## Screenshots / Demo
&lt;!-- Placeholder for project screenshots --&gt;
![Dashboard Placeholder](https://via.placeholder.com/800x450?text=RealTech+Hackathon+Dashboard)

*Live Demo: [https://github.com/younis-y/RealTech-Hackathon](https://github.com/younis-y/RealTech-Hackathon)*

## API / CLI Reference
The system can be used as a CLI tool:
```bash
# Basic usage
python scansan_api.py [AREA_CODE]

# Parameters:
# AREA_CODE: Postal district (e.g., E1, SW1A, N7)
```

## Tests
Run the backend test suite using pytest:
```bash
pytest
```

## Roadmap
- [ ] Integration with real-time rental listings (Rightmove/Zillow).
- [ ] Expansion to support major UK cities beyond London.
- [ ] Interactive Web Dashboard for area comparison.
- [ ] Support for non-narrated static video explainers.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Maintainer: **Younis Y**
GitHub: [younis-y](https://github.com/younis-y)
Project Link: [https://github.com/younis-y/RealTech-Hackathon](https://github.com/younis-y/RealTech-Hackathon)
