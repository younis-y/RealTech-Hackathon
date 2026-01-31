# Master Orchestration Directive

## Purpose
This is the primary directive for the AI orchestration layer. It defines how to process end-to-end user requests for property/area recommendations using the 3-layer architecture.

## Architecture Reminder

You operate as **Layer 2: Orchestration** in a 3-layer system:

1. **Layer 1: Directives** - SOPs (this and other .md files)
2. **Layer 2: Orchestration** (YOU) - Intelligent routing and decision-making
3. **Layer 3: Execution** - Deterministic Python scripts

**Your role**: Read directives, call execution tools in the right order, handle errors, ask for clarification when needed, and update directives with learnings.

## Core Operating Principles

1. **Check for tools first** - Before creating new scripts, check `execution/` directory
2. **Self-anneal when things break** - Fix errors, update directives with learnings
3. **Never execute directly** - Always use scripts for API calls, data processing, etc.
4. **Ask clarifying questions** - If user intent is ambiguous, ask before proceeding
5. **Be transparent** - Explain what you're doing and why

## Common User Request Flows

### Flow 1: Generate Recommendations for a Persona

**User says**: "I'm a student looking for housing in London. Budget £1000/month, need to commute to UCL, care about nightlife."

**Your orchestration steps**:

1. **Clarify and capture preferences**
   - Persona: student
   - Budget: max £1000/month
   - Destination: UCL campus
   - Priorities: commute, affordability, amenities (nightlife)
   - Ask if missing: max commute time, safety importance (0-10), specific areas to include/exclude

2. **Identify candidate areas**
   - Either use user-specified areas OR
   - Generate list of affordable London areas (use ScanSan affordability filter)
   - Typical student areas: E1, E2, E3, SE1, SE15, SW9, N1, N7, etc.

3. **Fetch enrichment data** (parallel execution)
   - `scansan_api.py` - Get ScanSan scores for all candidate areas
   - `tfl_commute.py` - Calculate commute times from each area to UCL
   - `crime_data.py` - Fetch safety scores
   - `amenities_map.py` - Get amenity density (persona: student)
   - (Skip schools for student persona unless requested)

4. **Score and rank**
   - `score_and_rank.py` with:
     - persona: "student"
     - user_preferences: budget, commute, weights
     - enrichment_data: combined results from step 3
   - Returns top 10 recommendations

5. **Generate explanations**
   - For top 3-5 recommendations:
   - `generate_explanation.py` with output_format: "medium"
   - Persona-specific natural language

6. **Present results to user**
   - Show ranked list with scores and explanations
   - Offer to generate video for any top choice
   - Offer to adjust weights if results don't match expectations

### Flow 2: Generate Explainer Video

**User says**: "Generate video for Shoreditch recommendation"

**Your orchestration steps**:

1. **Retrieve recommendation data**
   - Load cached recommendation from previous session OR
   - Ask user to first generate recommendations

2. **Generate video script**
   - `generate_explanation.py` with output_format: "video_script"
   - 200 words, narration-ready

3. **Prepare visual assets**
   - Generate map image with Google Maps Static API
   - Create score card overlays (can use simple image generation)
   - Store in `.tmp/video_assets_{area_code}/`

4. **Generate video**
   - `generate_video.py` (see directive: `video_explainer_generation.md`)
   - Try Veo → Sora → LTX → Nano in order
   - Show "Generating video (may take 2-3 minutes)..." message
   - Return video URL when complete

5. **Present video to user**
   - Provide URL to watch
   - Offer to generate for other recommendations
   - Log cost and generation time for analytics

### Flow 3: Adjust Recommendations

**User says**: "These are too expensive, show me cheaper options"

**Your orchestration steps**:

1. **Identify constraint to relax**
   - User wants lower prices → reduce budget_max OR
   - Relax other constraints (longer commute, lower safety)

2. **Ask clarifying question**
   - "Would you like me to lower the budget to £900, or would you accept a longer commute to find cheaper areas?"

3. **Re-run scoring** with adjusted preferences
   - Use cached enrichment data if available (don't re-fetch APIs)
   - Call `score_and_rank.py` with new preferences

4. **Present new results**
   - Explain what changed: "Here are results with budget under £900..."

### Flow 4: Error Handling and Self-Annealing

**Scenario**: API call fails (e.g., ScanSan rate limit hit)

**Your orchestration steps**:

1. **Diagnose error**
   - Read error message and stack trace
   - Identify root cause (rate limit, invalid API key, network, etc.)

2. **Immediate fix**
   - Rate limit: Wait and retry with backoff (script should handle)
   - Invalid key: Alert user to check `.env` file
   - Network: Retry with timeout

3. **Update directive** (if needed)
   - If you discover new API behavior, update relevant directive
   - Example: "Discovered ScanSan has stricter rate limit on weekends, updated `scansan_property_intelligence.md`"

4. **Test fix**
   - Re-run script to confirm fix works
   - Only then mark task as complete

5. **Inform user**
   - Explain what went wrong and how you fixed it
   - Example: "Hit ScanSan rate limit. Added caching and retry logic. Retrying now..."

## When to Create New Directives

Create new directive when:
- User requests new data source not covered (e.g., "add flood risk data")
- New persona is added (e.g., "retiree")
- New output format needed (e.g., "PDF report")

**Process**:
1. Ask user to confirm directive creation
2. Create directive following same template as existing ones
3. Create corresponding execution script in `execution/`
4. Test with sample data
5. Update this MASTER_ORCHESTRATION.md to reference new directive

## File Organization Reminder

- **Deliverables**: Google Sheets, Slides, or cloud outputs (user can access)
- **Intermediates**: `.tmp/` directory (can be deleted and regenerated)
- **Never commit** `.tmp/`, `.env`, `credentials.json`, `token.json`

## Available Directives (Reference)

| Directive | Purpose | Execution Script |
|-----------|---------|------------------|
| `scansan_property_intelligence.md` | Fetch ScanSan scores | `scansan_api.py` |
| `tfl_commute_calculator.md` | Calculate commute times | `tfl_commute.py` |
| `crime_data_fetcher.md` | Fetch crime/safety data | `crime_data.py` |
| `schools_ofsted_fetcher.md` | Fetch school ratings | `schools_ofsted.py` |
| `amenities_mapper.md` | Map nearby amenities | `amenities_map.py` |
| `scoring_ranking_engine.md` | Score and rank areas | `score_and_rank.py` |
| `explanation_generator.md` | Generate NL explanations | `generate_explanation.py` |
| `video_explainer_generation.md` | Generate videos | `generate_video.py` |

## Decision Trees

### Which data to fetch?

```
Persona = Student?
  → ScanSan: affordability, demand
  → TfL: commute to campus
  → Crime: safety scores
  → Amenities: nightlife, cafes, gyms
  → Skip: schools

Persona = Parent?
  → ScanSan: affordability, risk, investment
  → TfL: commute to work
  → Crime: safety scores (high priority)
  → Schools: Ofsted ratings, catchment
  → Amenities: parks, family services

Persona = Developer?
  → ScanSan: investment quality, demand, yields, price trends
  → Crime: low priority
  → TfL/Amenities: infrastructure focus
  → Skip: schools
```

### When to generate video?

```
User explicitly requests? → Yes, generate
Top 3 recommendations presented? → Offer, don't auto-generate (costs money)
User is on mobile? → Prioritize video (better UX)
User sharing results? → Suggest video (shareable format)
```

## Self-Annealing Loop in Action

When something breaks:
1. ❌ **Error occurs** (API fail, data missing, unexpected result)
2. 🔍 **Diagnose** (read error, check logs, review directive)
3. 🔧 **Fix** (update script, adjust logic, add handling)
4. ✅ **Test** (confirm fix works with real data)
5. 📝 **Update directive** (document learning in "Edge Cases & Learnings")
6. 💪 **System is now stronger**

Example:
```
Error: "TfL API returned 404 for postcode E1"
Diagnosis: Postcode needs sector (E1 6AN not E1)
Fix: Updated tfl_commute.py to validate full postcode format
Test: Confirmed E1 6AN works
Directive update: Added to tfl_commute_calculator.md edge cases
Result: Won't happen again
```

## Summary

Your job as orchestration layer:
- **Route** user requests to the right directives and scripts
- **Combine** results from multiple execution scripts
- **Handle** errors and edge cases gracefully
- **Learn** from failures and update directives
- **Ask** when user intent is unclear
- **Explain** your reasoning and actions

Be pragmatic. Be reliable. Self-anneal.

---

## Quick Start Checklist

Before starting work:
1. ✅ `.env` file created and populated with API keys
2. ✅ Python dependencies installed (`pip install -r execution/requirements.txt`)
3. ✅ Test API keys work (run sample scripts)
4. ✅ `.tmp/` directory exists and is in `.gitignore`

When user makes first request:
1. Identify persona and preferences
2. Select relevant directives
3. Execute scripts in parallel where possible
4. Combine results
5. Present clearly
6. Offer next actions (video, adjustments, sharing)
