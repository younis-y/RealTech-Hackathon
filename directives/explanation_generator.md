# Explanation Generator Directive

## Goal
Convert structured factor scores and breakdowns into concise, persona-specific natural language explanations using Claude/Perplexity APIs, with strict constraints to prevent hallucinations.

## Inputs
- **recommendation_data**: Full recommendation object from scoring engine
  - area_code, composite_score, factor_scores, factor_contributions
  - strengths, weaknesses, trade_offs
- **persona**: student | parent | developer
- **output_format**: "short" (50 words) | "medium" (150 words) | "video_script" (200 words)
- **comparison_areas**: Optional list of other top candidates for trade-off explanation

## Execution Tool
Use `execution/generate_explanation.py`

## Process
1. **Prepare structured prompt for LLM**
   - Include all numeric data points
   - Provide persona context
   - Specify output format and constraints
   - Include example output for consistency

2. **Call Claude API** (preferred) or Perplexity
   - Model: Claude Sonnet 4.5 (good balance of quality and cost)
   - Temperature: 0.3 (low to reduce creativity/hallucination)
   - System prompt emphasizes: "Only reference provided data. Do not invent facts."

3. **Validate output**
   - Check that explanation only references data points provided
   - Verify no external facts introduced
   - Ensure persona-appropriate language
   - If validation fails, retry with stricter prompt

4. **Return explanation** with metadata

## Output Formats by Persona

### Student - Short (50 words)
```
"Shoreditch scores 87/100 for students. Rent averages £950/month, with a 22-minute commute to campus. Strong nightlife (90/100) with 12 pubs and 8 cafes nearby. Safety is decent at 78/100. Great for social students who prioritize convenience."
```

### Parent - Medium (150 words)
```
"Kingston upon Thames is an excellent choice for families, scoring 89/100. Here's what makes it stand out:

Schools: Average Ofsted rating of Outstanding, with 3 outstanding primary schools within 1.5km. Secondary schools score 85/100.

Safety: Crime rate is 65% below London average, giving a safety score of 92/100.

Budget: 3-bed homes average £2,100/month rent or £520k purchase, fitting your budget.

Commute: 35 minutes to Central London via rail, within your acceptable range.

Amenities: 4 parks, 2 leisure centres, and excellent high street shopping (amenity score 88/100).

The trade-off: Slightly longer commute than Clapham, but you get significantly better schools and more green space. For families prioritizing education and safety, Kingston is hard to beat."
```

### Developer - Video Script (200 words)
```
"Let's analyze Stratford as an investment opportunity. This area scores 91 out of 100 for developers.

Investment quality is exceptional at 94 out of 100. Here's the data: average yields are 5.2%, compared to the London average of 3.8%. That's a 37% premium.

Price trends show 8% annual growth over the past 3 years, outpacing the London average of 5.4%. Demand index sits at 89 out of 100, driven by the Elizabeth Line and ongoing regeneration.

Risk assessment scores 82 out of 100. The market is stable, with high liquidity and strong rental demand from young professionals.

Infrastructure is the real story. The Elizabeth Line cut commute times to the City by 15 minutes. Two new residential towers are under construction, and the council has approved planning for a third commercial hub.

Budget fit: 2-bed flats average £380k, fitting your £400k maximum.

The trade-off: You're buying at a premium relative to neighboring Leyton, but you're paying for proven rental demand and infrastructure that's already delivered.

For developers seeking strong yields with manageable risk, Stratford offers compelling fundamentals backed by solid data."
```

## Prompt Template Structure
```
You are explaining a property/area recommendation to a [PERSONA].

HARD CONSTRAINT: Only reference the data points provided below. Do not introduce external facts or assumptions.

Data:
- Area: [area_code]
- Composite score: [score]/100
- Factor scores: [JSON]
- Factor contributions: [JSON]
- Strengths: [list]
- Weaknesses: [list]
- Trade-offs vs other areas: [comparison data]

Persona context:
- Student: casual, friendly, focus on budget, commute, social life
- Parent: careful, detailed, focus on schools, safety, family needs
- Developer: analytical, data-driven, focus on ROI, risk, fundamentals

Output format: [short/medium/video_script]

Tone: Confident, helpful, transparent about trade-offs. Use specific numbers from data.

Generate explanation:
```

## Edge Cases & Learnings
- **Hallucination prevention**: Most critical concern
  - Use low temperature (0.3 or below)
  - Include "HARD CONSTRAINT" in prompt
  - Validate output against input data
  - Retry up to 3 times if hallucinations detected
- **Tone consistency**: Different LLMs have different styles
  - Provide example outputs in prompt for consistency
  - Claude tends to be more formal; adjust with "casual, friendly" if needed
- **Number formatting**: "5.2%" not "5.20000%", "£950" not "£950.00"
- **Comparison language**: When comparing areas, always cite specific numbers
  - "15% more affordable" not "much cheaper"
- **API costs**:
  - Claude Sonnet 4.5: ~$0.003 per explanation (medium format)
  - Cache system prompts to reduce costs
- **Rate limits**: Claude API: 1000 requests/minute on paid tier
- **Language**: UK English spelling and terminology (flats not apartments, high street not main street)

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates: user feedback on explanation quality, hallucination incidents, cost optimization]
