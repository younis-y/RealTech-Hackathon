# Veo - Explainable Housing Recommendation Platform

Multi-persona location and housing recommendation platform powered by ScanSan's property intelligence, with transparent factor breakdowns and auto-generated explainer videos.

## 🏗️ 3-Layer Architecture

This project uses a 3-layer architecture designed to maximize reliability by separating concerns:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Directives (WHAT to do)                       │
│  • SOPs in Markdown (directives/)                       │
│  • Define goals, inputs, tools, outputs, edge cases     │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Orchestration (DECISION making)               │
│  • AI agent (Claude) reads directives                   │
│  • Routes requests, handles errors, asks questions      │
│  • Updates directives with learnings                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Execution (DOING the work)                    │
│  • Deterministic Python scripts (execution/)            │
│  • API calls, data processing, file operations          │
│  • Reliable, testable, fast                             │
└─────────────────────────────────────────────────────────┘
```

**Why this works**: If the AI does everything directly, errors compound. 90% accuracy per step = 59% success over 5 steps. By pushing complexity into deterministic code, the AI focuses on decision-making where it excels.

## 📁 Project Structure

```
veo/
├── directives/              # Layer 1: SOPs and instructions
│   ├── MASTER_ORCHESTRATION.md
│   ├── scansan_property_intelligence.md
│   ├── tfl_commute_calculator.md
│   ├── crime_data_fetcher.md
│   ├── schools_ofsted_fetcher.md
│   ├── amenities_mapper.md
│   ├── scoring_ranking_engine.md
│   ├── explanation_generator.md
│   └── video_explainer_generation.md
│
├── execution/               # Layer 3: Python scripts
│   ├── scansan_api.py
│   ├── tfl_commute.py       # (to be created)
│   ├── crime_data.py        # (to be created)
│   ├── schools_ofsted.py    # (to be created)
│   ├── amenities_map.py     # (to be created)
│   ├── score_and_rank.py
│   ├── generate_explanation.py
│   ├── generate_video.py    # (to be created)
│   └── requirements.txt
│
├── .tmp/                    # Temporary/intermediate files
│   └── (cache files, scraped data, video assets)
│
├── .env.template            # Environment variables template
├── .gitignore
├── Agents.md                # Architecture documentation
├── Claude_updated.md        # Project specification
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r execution/requirements.txt

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r execution/requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy template to .env
cp .env.template .env

# Edit .env and add your API keys
# At minimum, you need:
# - SCANSAN_API_KEY
# - ANTHROPIC_API_KEY
# - TFL_APP_KEY (optional but recommended)
# - GOOGLE_MAPS_API_KEY (optional but recommended)
```

### 3. Test Execution Scripts

```bash
# Test ScanSan API
python execution/scansan_api.py SW1A E1

# Test explanation generator
python execution/generate_explanation.py

# Test scoring engine
python execution/score_and_rank.py
```

### 4. Use the AI Orchestrator

The AI orchestrator (Claude) reads directives and calls execution scripts. Start by asking:

```
"I'm a student looking for housing in London. Budget £1000/month, need to commute to UCL, care about nightlife."
```

The AI will:
1. Identify persona and preferences
2. Call relevant execution scripts (ScanSan, TfL, crime, amenities)
3. Score and rank areas
4. Generate natural language explanations
5. Present top recommendations
6. Offer to generate explainer videos

## 🎯 User Personas

### Student
- **Focus**: Affordability, commute to campus, nightlife, safety
- **Budget**: Typically £800-1200/month rent
- **Data sources**: ScanSan affordability, TfL commute, crime, amenities (pubs, cafes)

### Parent
- **Focus**: Schools, safety, family amenities, commute, budget
- **Budget**: £1500-3000/month rent or £400k-700k purchase
- **Data sources**: Ofsted ratings, crime, parks, TfL, ScanSan

### Developer/Investor
- **Focus**: ROI, yields, price trends, demand, risk
- **Budget**: £300k-1M+ purchase
- **Data sources**: ScanSan investment quality, demand index, yields, infrastructure

## 📊 How It Works

### Example: Student Request

**User**: "Find me student housing in London under £1000/month, max 30-minute commute to UCL"

**Orchestration Flow**:

1. **Preference Capture**
   - Persona: student
   - Budget: max £1000/month
   - Destination: UCL campus
   - Max commute: 30 minutes

2. **Data Fetching** (parallel)
   ```python
   # ScanSan: affordability scores for London areas
   scansan_api.py E1 E2 E3 SE1 SE15 N1 N7 SW9

   # TfL: commute times from each area to UCL
   tfl_commute.py --from E1,E2,E3 --to "UCL Gower St"

   # Crime: safety scores
   crime_data.py E1 E2 E3 SE1 SE15 N1 N7 SW9

   # Amenities: nightlife density
   amenities_map.py --persona student E1 E2 E3 ...
   ```

3. **Scoring**
   ```python
   score_and_rank.py \
     --persona student \
     --budget-max 1000 \
     --max-commute 30 \
     --weights affordability:8,commute:7,amenities:6
   ```

4. **Explanation**
   ```python
   generate_explanation.py \
     --area E1_6AN \
     --persona student \
     --format medium
   ```

5. **Output**: Top 10 ranked areas with explanations

**Sample Result**:
```
1. Shoreditch (E1) - Score: 87/100
   "Shoreditch scores 87 out of 100 for students. Rent averages £950/month,
   with a 22-minute commute to UCL. Strong nightlife (90/100) with 12 pubs
   and 8 cafes nearby. Safety is decent at 78/100. Great for social students
   who prioritize convenience."

2. Camden (NW1) - Score: 85/100
   [...]
```

## 🎥 Video Generation

Generate 30-60 second explainer videos for top recommendations:

**User**: "Generate video for Shoreditch recommendation"

**Orchestration Flow**:

1. Generate video script (200 words, narration-ready)
2. Prepare visual assets (map with markers, score cards)
3. Call video API (Veo → Sora → LTX → Nano fallback)
4. Return video URL

**Cost**: ~£0.10-0.50 per video (depending on API)

## 🔧 Self-Annealing Loop

When errors occur, the system learns and improves:

1. **Error**: API call fails
2. **Diagnose**: Read error message, check directive
3. **Fix**: Update script, add error handling
4. **Test**: Confirm fix works
5. **Update Directive**: Document learning in edge cases
6. **System is stronger**: Won't fail the same way again

**Example**:
```
Error: TfL API rate limited (hit 500 requests/minute)
Fix: Added 100ms delay between requests, implemented caching
Directive Update: Updated tfl_commute_calculator.md with rate limit info
Result: No longer hits rate limit
```

## 📝 Creating New Directives

When you need new functionality:

1. Create directive in `directives/new_feature.md`
2. Follow existing template:
   - Goal
   - Inputs
   - Execution Tool
   - Process
   - Outputs
   - Edge Cases & Learnings
3. Create corresponding script in `execution/new_feature.py`
4. Test with sample data
5. Update `MASTER_ORCHESTRATION.md` to reference new directive

## 🔑 Required API Keys

### Essential
- **SCANSAN_API_KEY**: Primary property intelligence
- **ANTHROPIC_API_KEY**: Natural language explanations

### Recommended
- **TFL_APP_KEY**: London commute times
- **GOOGLE_MAPS_API_KEY**: Maps, places, directions

### Optional
- **GOOGLE_VEO_API_KEY**: Video generation (primary)
- **OPENAI_API_KEY**: Sora video generation (fallback)
- **PERPLEXITY_API_KEY**: Research and fact-checking

### Free/Open APIs (no key needed)
- data.police.uk (UK crime data)
- Get Information About Schools (UK schools)
- ONS Open Geography (UK boundaries and stats)
- OpenStreetMap Overpass (amenities)
- postcodes.io (UK postcode geocoding)

## 📊 Data Flow Example

```
User Input
  ↓
Persona Identification (Student/Parent/Developer)
  ↓
Preference Capture (budget, commute, priorities)
  ↓
┌─────────────────────────────────────────────────┐
│         Parallel Data Fetching                  │
├─────────────────────────────────────────────────┤
│ ScanSan  │ TfL    │ Crime  │ Schools │ Amenities│
│ Scores   │Commute │ Safety │ Ofsted  │ Density  │
└─────────────────────────────────────────────────┘
  ↓
Scoring Engine (weighted composite score)
  ↓
Ranking (top 10 recommendations)
  ↓
Explanation Generation (Claude API)
  ↓
Present to User
  ↓
[Optional] Video Generation
  ↓
Deliverable (shareable recommendations + video)
```

## 🧪 Testing

```bash
# Test individual execution scripts
python execution/scansan_api.py SW1A
python execution/score_and_rank.py

# Test with sample data
python execution/generate_explanation.py < sample_recommendation.json
```

## 📈 Cost Estimation

Typical cost per user request:

| Component | Cost | Notes |
|-----------|------|-------|
| ScanSan API | £0.01-0.05 | Per area queried |
| TfL API | Free | With app key |
| Crime/Schools/OSM | Free | Open APIs |
| Claude explanations | £0.003 | Per explanation |
| **Subtotal (no video)** | **£0.02-0.10** | For 10 recommendations |
| Video generation | £0.10-0.50 | Only if user requests |

## 🛡️ Best Practices

1. **Always use execution scripts** - Don't call APIs directly from orchestration layer
2. **Cache aggressively** - Store results in `.tmp/` to avoid redundant API calls
3. **Fail gracefully** - If one data source fails, continue with others
4. **Ask when unclear** - If user intent is ambiguous, ask clarifying questions
5. **Update directives** - Document learnings in edge cases sections
6. **Test changes** - Confirm fixes work before marking tasks complete

## 🔄 Workflow Summary

```
User Request
  → Read relevant directives
  → Call execution scripts in proper order
  → Handle errors (self-anneal if needed)
  → Combine results
  → Generate explanations
  → Present to user
  → Update directives with learnings
```

## 📚 Further Reading

- [Agents.md](Agents.md) - Full architecture documentation
- [Claude_updated.md](Claude_updated.md) - Project specification
- [MASTER_ORCHESTRATION.md](directives/MASTER_ORCHESTRATION.md) - Orchestration guide

## 🤝 Contributing

When adding new features:

1. Create directive first (what should happen)
2. Create execution script (how it happens)
3. Test with real data
4. Update master orchestration
5. Document edge cases as you discover them

## 📄 License

[Your license here]

---

**Remember**: Directives are living documents. Update them as you learn. The system gets stronger with every error you fix.
