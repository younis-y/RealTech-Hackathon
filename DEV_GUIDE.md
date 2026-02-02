# 🏠 Domus Developer Guide

> Complete setup, development workflow, and contribution guidelines for the Domus Housing Platform

---

## 📋 Quick Start (TL;DR)

```bash
# Clone & setup
git clone https://github.com/younis-y/RealTech-Hackathon.git
cd RealTech-Hackathon

# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install

# Run
npm run dev          # Frontend: http://localhost:3000
python demo_pipeline.py --help    # CLI tool
```

---

## 🛠️ Full Environment Setup

### Prerequisites

| Tool       | Version     | Installation                              |
|------------|-------------|-------------------------------------------|
| Python     | 3.11+       | [python.org](https://python.org)          |
| Node.js    | 18+         | [nodejs.org](https://nodejs.org)          |
| Git        | Latest      | [git-scm.com](https://git-scm.com)        |

### Step 1: Backend Setup (Python)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Frontend Setup (Next.js)

```bash
cd frontend
npm install
```

### Step 3: Environment Variables

Create a `.env` file in the project root:

```ini
# ═══════════════════════════════════════════════════════════
# REQUIRED - Core API Keys
# ═══════════════════════════════════════════════════════════
SCANSAN_API_KEY=your_scansan_key_here
ANTHROPIC_API_KEY=your_anthropic_claude_key_here

# ═══════════════════════════════════════════════════════════
# OPTIONAL - Enhanced Features
# ═══════════════════════════════════════════════════════════
TFL_APP_KEY=your_tfl_key            # Transport for London commute times
PERPLEXITY_API_KEY=your_key         # Live market news feature
GOOGLE_MAPS_API_KEY=your_key        # Enhanced location services
```

> **Tip:** Copy `.env.template` as your starting point.

---

## 🚀 Running the Platform

### Web Application (Frontend)

```bash
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

**Available Views:**
- `/` — Home page with recommendation form
- `/results` — Results display with scoring breakdown

### Command-Line Pipeline (Backend)

Run recommendations without the web interface:

```bash
# Basic usage
python demo_pipeline.py --persona student --budget 1200

# Full options
python demo_pipeline.py \
  --persona student \
  --budget 1500 \
  --type rent \
  --destination UCL \
  --max-areas 5

# Quick test (mock data, no AI explanations)
python demo_pipeline.py --max-areas 2 --no-explanations
```

### Verify API Connections

```bash
python tools/verify_apis.py
```

---

## 📁 Project Structure

```
RealTech-Hackathon/
│
├── 📂 frontend/                  # Next.js Web Application
│   ├── app/
│   │   ├── page.tsx             # Home page (persona form)
│   │   ├── results/page.tsx     # Results display
│   │   ├── api/
│   │   │   └── recommendations/
│   │   │       └── route.ts     # API endpoint (calls Python)
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Tailwind + custom styles
│   └── package.json
│
├── 📂 tools/                     # The "Tool Belt" - Data Fetchers
│   ├── fetch_scansan.py         # 🏘️ Property intelligence (ScanSan)
│   ├── fetch_tfl_commute.py     # 🚇 Transport times (TfL API)
│   ├── fetch_crime_data.py      # 🚔 Crime statistics (UK Police)
│   ├── fetch_schools.py         # 🏫 School ratings (Ofsted)
│   ├── fetch_market_news.py     # 📰 Live property news
│   ├── score_areas.py           # 📊 Persona-weighted scoring
│   └── verify_apis.py           # ✅ API connection checker
│
├── 📂 execution/                 # Orchestration Layer
│   └── scansan_api.py           # Low-level ScanSan API client
│
├── 📂 directives/                # Layer 1: Markdown SOPs
│   └── [persona]_directive.md   # Persona-specific instructions
│
├── demo_pipeline.py              # 🎯 Main CLI entry point
├── requirements.txt              # Python dependencies
├── .env                          # Your API keys (gitignored)
└── .env.template                 # Template for environment setup
```

---

## 🔄 API Data Flow

```
User Input (Web/CLI)
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  📋 Layer 1: Directives                                      │
│  Reads persona-specific scoring weights from Markdown files  │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  🧠 Layer 2: AI Orchestrator (Claude)                        │
│  Coordinates data fetching, applies scoring, generates text  │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  ⚙️ Layer 3: Execution Workers (Python Tools)                │
│  fetch_scansan.py → fetch_tfl.py → fetch_crime.py → ...     │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
   Ranked Area Recommendations with Explanations
```

---

## 🧪 Testing

### Frontend Tests

```bash
cd frontend
npm test              # Unit tests (Jest)
npm run test:e2e      # End-to-end (Playwright)
```

### Backend Tests

```bash
# Run pytest from project root
pytest

# With verbose output
pytest -v
```

### Manual Smoke Test

```bash
# Verify full pipeline works
python demo_pipeline.py --persona student --budget 1500 --max-areas 3
```

---

## 🤝 Contributing

### Before You Submit

1. **Does it fit the 3-Layer Architecture?**
   - Directives (Layer 1) for config changes
   - Orchestrator (Layer 2) for AI logic
   - Tools (Layer 3) for data fetching

2. **Error Handling**
   - Never crash on API failures
   - Use graceful fallbacks

3. **Run the Pipeline**
   ```bash
   python demo_pipeline.py --max-areas 3
   ```

4. **Code Style**
   - Python: Black/PEP8
   - TypeScript: ESLint/Prettier

### Workflow

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/RealTech-Hackathon.git

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes & test
python demo_pipeline.py --max-areas 2

# 4. Commit with clear message
git commit -m "Add amazing feature: brief description"

# 5. Push & open PR
git push origin feature/amazing-feature
```

---

## 🐛 Troubleshooting

| Issue                          | Solution                                         |
|--------------------------------|-------------------------------------------------|
| `ModuleNotFoundError`          | Activate venv: `source venv/bin/activate`       |
| `SCANSAN_API_KEY not set`      | Check `.env` file exists with valid keys        |
| Frontend won't start           | Run `npm install` in `frontend/` directory      |
| API rate limits                | Reduce `--max-areas` or add delays              |
| Python version issues          | Use Python 3.11+                                |

---

## 📞 Support

- **GitHub Issues:** [Report a bug](https://github.com/younis-y/RealTech-Hackathon/issues)
- **Maintainer:** [@younis-y](https://github.com/younis-y)

---

Happy Coding! 🚀
