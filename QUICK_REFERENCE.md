# Quick Reference Guide

## 🚀 Getting Started

### Initial Setup
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

### Configure API Keys
Edit `.env` and add your keys:
```bash
# Required
SCANSAN_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Recommended
TFL_APP_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here

# Optional
GOOGLE_VEO_API_KEY=your_key_here
```

## 📋 Common Commands

### Test Execution Scripts
```bash
# Test ScanSan API
python execution/scansan_api.py SW1A E1

# Test scoring engine
python execution/score_and_rank.py

# Test explanation generator
python execution/generate_explanation.py
```

### AI Orchestrator Examples

**Student Request:**
```
"I'm a student looking for housing in London. Budget £1000/month,
need to commute to UCL, care about nightlife and safety."
```

**Parent Request:**
```
"I'm a parent looking to buy in London. Budget £500k, need good schools
(Outstanding preferred), max 40-minute commute to Canary Wharf,
safety is very important."
```

**Developer Request:**
```
"I'm an investor looking for buy-to-let in London. Budget £400k,
focusing on high yields, moderate risk tolerance, interested in
areas with infrastructure development."
```

## 🎯 Orchestration Patterns

### Full Recommendation Flow
1. User states persona + preferences
2. AI identifies candidate areas
3. AI fetches data (ScanSan, TfL, crime, schools, amenities)
4. AI scores and ranks
5. AI generates explanations
6. AI presents top 10 recommendations
7. User can request video for any recommendation

### Video Generation
```
"Generate video for [area name] recommendation"
```

### Adjust Preferences
```
"Show me cheaper options"
"What if I'm willing to commute 45 minutes?"
"Show areas with better schools"
```

## 📁 Directory Structure

```
veo/
├── directives/          # What to do (SOPs)
├── execution/           # How to do it (Python scripts)
├── .tmp/               # Temporary data (regenerable)
├── .env                # API keys (not committed)
└── venv/               # Python virtual environment
```

## 🔄 Self-Annealing Workflow

When errors occur:
1. Error occurs → AI diagnoses
2. AI fixes script
3. AI tests fix
4. AI updates directive with learning
5. System is stronger

## 📊 Persona Weight Profiles

### Student
- Affordability: 35%
- Commute: 25%
- Amenities: 20%
- Safety: 15%
- Investment: 5%

### Parent
- Schools: 30%
- Safety: 25%
- Affordability: 20%
- Commute: 15%
- Amenities: 10%

### Developer
- Investment Quality: 40%
- Demand Index: 25%
- Risk Score: 20%
- Infrastructure: 15%

## 🛠️ Troubleshooting

### "API key not found"
→ Check `.env` file exists and has correct key names

### "Rate limited"
→ Execution scripts have retry logic; wait and retry

### "No areas found"
→ Constraints too strict; AI will suggest relaxing filters

### "Script not found"
→ Check you're in project root directory and venv is activated

## 📝 Creating New Features

1. Create directive: `directives/new_feature.md`
2. Create script: `execution/new_feature.py`
3. Test with sample data
4. Update `MASTER_ORCHESTRATION.md`
5. Document edge cases as discovered

## 🔑 API Cost Reference

| Service | Free Tier | Paid Tier | Cost per Request |
|---------|-----------|-----------|------------------|
| ScanSan | 100/hour | 1000/hour | £0.01-0.05 |
| TfL | 500/min | 5000/min | Free |
| Claude API | N/A | Pay-as-go | £0.003/explanation |
| Google Veo | Beta | Limited | £0.10-0.30/video |
| Crime/Schools | Unlimited | N/A | Free |

## 📚 Key Files to Read

1. **README.md** - Overview and architecture
2. **directives/MASTER_ORCHESTRATION.md** - How AI should operate
3. **Agents.md** - Deep dive on 3-layer architecture
4. **Claude_updated.md** - Full project specification

## 💡 Tips

- **Cache aggressively** - Avoid redundant API calls
- **Test scripts individually** before orchestrating
- **Update directives** with learnings as you go
- **Ask clarifying questions** when user intent is unclear
- **Use parallel execution** where possible
- **Fail gracefully** - one data source failure shouldn't break everything

## 🎬 Video Generation Options

Priority order (AI tries in sequence):
1. Google Veo (best quality, £0.10-0.30)
2. OpenAI Sora (good quality, £0.20-0.50)
3. LTX Studio (moderate, £0.10)
4. Nano (fast/cheap, £0.05)

Videos are:
- 30-60 seconds
- 16:9 aspect ratio (web) or 9:16 (mobile)
- Include subtitles (accessibility)
- Stored in CDN/cloud storage

## 🔐 Security Notes

- Never commit `.env` to git (in `.gitignore`)
- Never commit `.tmp/` directory
- Never commit `credentials.json` or `token.json`
- API keys are loaded from environment variables only

## 📈 Scaling Considerations

- Use Redis for distributed caching (optional)
- Batch API calls where possible
- Cache validity: 24 hours (properties), 7 days (area trends)
- Queue video generation for high demand

---

**Need help?** Read `directives/MASTER_ORCHESTRATION.md` for detailed orchestration patterns.
