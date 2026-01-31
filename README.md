# Veo Housing Platform
&gt; AI-powered property recommendation engine with persona-based scoring and intelligent multi-source data enrichment.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Node.js](https://img.shields.io/badge/node.js-18%2B-green)
![TypeScript](https://img.shields.io/badge/typescript-5.x-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## Description
Veo is an intelligent property recommendation system that helps users find the perfect London neighborhood based on their lifestyle and priorities. The platform leverages a sophisticated 3-layer AI orchestration architecture to synthesize live data from property intelligence APIs, transport networks, crime statistics, and education ratings—delivering personalized, data-driven area recommendations with transparent scoring and AI-generated explanations.

**Target Users:**
- **Students** seeking affordable areas with good transport links to universities.
- **Parents** prioritizing school quality, safety, and family-friendly neighborhoods.
- **Property Developers** looking for investment opportunities with high ROI potential.
- **Climate warrior** seeking eco-friendly neighborhoods with green spaces and sustainable living options.

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
- [Contact / Support](#contact--support)

## Features
- **🎯 Persona-Driven Scoring** - Customized ranking algorithms for Students, Parents, and Property Developers with tailored factor weights.
- **🏘️ Multi-Source Data Enrichment** - Integrates ScanSan property intelligence, TfL transport data, UK Police crime statistics, and Ofsted school ratings.
- **🤖 AI-Powered Explanations** - Natural language justifications for every recommendation using Claude AI.
- **📊 Transparent Factor Breakdown** - Clear visibility into affordability, commute, safety, amenities, and investment quality scores.
- **⚡ Real-Time Analysis** - Live API calls ensure up-to-date property market data.
- **🔄 Self-Annealing Architecture** - Automatically diagnoses and fixes API failures within the orchestration layer.

## Tech Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: Python 3.11+ (Data Processing), Node.js (API Layer), Anthropic Claude API (Orchestration)
- **Data Pipeline**: Pandas, NumPy, aiohttp (Async I/O)
- **Cache &amp; Infrastructure**: Redis, Modal (Python Serverless), Vercel
- **Testing**: Jest, Playwright, Pytest

## Architecture Overview

<img width="1017" height="670" alt="image" src="https://github.com/user-attachments/assets/08b83d8b-521b-4af1-99a7-ce8e35439e50" />



The system follows a modular 3-layer architecture where the **AI Orchestrator (Claude)** reads high-level **Directives** (Markdown SOPs) to determine which deterministic **Execution Scripts** (Python) to trigger. This approach ensures that business logic remains flexible while data processing remains reliable and fast.

## Installation
### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Redis (optional, for local caching)

### Step-by-Step Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/younis-y/RealTech-Hackathon.git
   cd RealTech-Hackathon
   ```

2. **Backend Setup (Python)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Frontend Setup (Node.js)**:
   ```bash
   cd frontend
   npm install
   ```

## Usage
### Web Interface
Start the development server and visit `http://localhost:3000`:
```bash
cd frontend
npm run dev
```

### CLI Demo Pipeline
Run the complete recommendation pipeline from the command line:
```bash
python demo_pipeline.py --persona student --budget 1200 --type rent --destination UCL
```

## Configuration
Create a `.env` file in the project root:
```ini
# Required API Keys
SCANSAN_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
TFL_API_KEY=your_key_here

# Caching
REDIS_URL=redis://localhost:6379
```

## Screenshots / Demo
&lt;!-- Placeholder for project screenshots --&gt;
![Dashboard Placeholder](https://via.placeholder.com/800x450?text=Veo+Housing+Platform+Dashboard)

*Live Demo: [https://github.com/younis-y/RealTech-Hackathon](https://github.com/younis-y/RealTech-Hackathon)*

## API / CLI Reference
### API Endpoint
**POST `/api/recommendations`**
```json
{
  "persona": "student",
  "budget": 1200,
  "locationType": "rent",
  "destination": "UCL"
}
```

### CLI Tools
**Area Data Fetcher**
```bash
python execution/scansan_api.py E1 SW1A N7
```

## Tests
### Frontend (Jest &amp; Playwright)
```bash
cd frontend
npm test
npm run test:e2e
```

### Backend (Pytest)
```bash
pytest
```

## Roadmap
- [x] Phase 1: Core 3-Layer Architecture
- [ ] Phase 2: Modal Serverless &amp; Redis Deployment
- [ ] Phase 3: Real-time Rental Listing Integration (Rightmove/Zoopla)
- [ ] Phase 4: AI-Generated Video Explainers with Narration

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact / Support
Maintainer: **Younis Y**
GitHub: [@younis-y](https://github.com/younis-y)
Project Link: [https://github.com/younis-y/RealTech-Hackathon](https://github.com/younis-y/RealTech-Hackathon)
