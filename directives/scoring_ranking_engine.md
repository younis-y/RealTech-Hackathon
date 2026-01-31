# Scoring & Ranking Engine Directive

## Goal
Combine ScanSan property intelligence with enrichment data (commute, crime, schools, amenities) to produce persona-specific ranked recommendations with transparent factor breakdowns.

## Inputs
- **persona**: student | parent | developer
- **user_preferences**: Dictionary of user-specified weights and constraints from checklist
  - budget_max, budget_min
  - max_commute_minutes
  - min_safety_score
  - min_school_rating (parent only)
  - importance_weights: {commute: 0-10, safety: 0-10, schools: 0-10, ...}
- **candidate_areas**: List of area codes to evaluate
- **enrichment_data**: Pre-fetched data from other directives
  - ScanSan scores (from `scansan_property_intelligence.md`)
  - Commute times (from `tfl_commute_calculator.md`)
  - Crime data (from `crime_data_fetcher.md`)
  - Schools (from `schools_ofsted_fetcher.md`)
  - Amenities (from `amenities_mapper.md`)

## Execution Tool
Use `execution/score_and_rank.py`

## Process
1. **Normalize all scores to 0-100 scale**
   - ScanSan scores already 0-100
   - Commute: inverse (shorter = higher score)
   - Crime: safety_score from crime directive
   - Schools: average quality score
   - Amenities: density_score

2. **Apply persona-specific base weights**
   ```
   Student:
     - affordability: 35%
     - commute: 25%
     - safety: 15%
     - amenities: 20%
     - investment_quality: 5%

   Parent:
     - affordability: 20%
     - schools: 30%
     - safety: 25%
     - commute: 15%
     - amenities: 10%

   Developer:
     - investment_quality: 40%
     - demand_index: 25%
     - risk_score: 20%
     - infrastructure: 15%
   ```

3. **Adjust weights by user importance ratings**
   - User provides 0-10 importance for each factor
   - Scale base weights proportionally

4. **Apply hard constraints (filters)**
   - budget_max, max_commute, min_safety, min_school_rating
   - Remove candidates that fail constraints

5. **Calculate weighted composite score**
   - composite_score = Σ(factor_score × adjusted_weight)
   - Store individual factor contributions for transparency

6. **Rank candidates by composite score**

7. **Generate factor breakdown for each candidate**
   - Show which factors helped/hurt the score
   - Identify trade-offs between top candidates

8. **Output top N recommendations** (default N=10)

## Outputs
JSON structure:
```json
{
  "persona": "student",
  "user_preferences": {...},
  "recommendations": [
    {
      "rank": 1,
      "area_code": "E1 6AN",
      "composite_score": 87.3,
      "factor_scores": {
        "affordability": 92,
        "commute": 85,
        "safety": 78,
        "amenities": 90,
        "investment_quality": 72
      },
      "factor_contributions": {
        "affordability": 32.2,
        "commute": 21.3,
        "safety": 11.7,
        "amenities": 18.0,
        "investment_quality": 3.6
      },
      "strengths": ["Excellent nightlife", "Quick commute to campus", "Very affordable"],
      "weaknesses": ["Slightly higher crime than ideal"],
      "trade_offs": "Prioritizes convenience and affordability over safety margin"
    }
  ],
  "filtered_out_count": 5,
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **Missing data**: If a factor has no data for an area, exclude that area or use neutral score (50)
  - Log which areas excluded and why
- **Weight normalization**: Ensure adjusted weights sum to 100%
- **Tied scores**: If two areas have identical scores, rank by affordability (students/parents) or investment quality (developers)
- **No candidates pass filters**: Relax constraints incrementally and inform user
  - "No areas found under £1200/month. Showing results up to £1400"
- **Extreme outliers**: Cap individual factor scores at 100 to prevent skewing
- **Explanation generation**: Use factor contributions to generate natural language
  - Top contributor → "primarily because..."
  - Secondary contributors → "also benefits from..."

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates based on user feedback and actual scoring behavior]
