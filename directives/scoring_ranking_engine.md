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
Use `tools/score_areas.py`

## Process
1. **Normalize all scores to 0-100 scale**
   - ScanSan scores already 0-100
   - Commute: inverse (shorter = higher score)
   - Crime: safety_score from crime directive
   - Schools: average quality score
   - Amenities: density_score

2. **Apply persona-specific base weights**

   These are the weights in `tools/score_areas.py` (`PERSONA_WEIGHTS`). They are
   hand-set defaults, not fitted to any data.
   ```
   Student:                Parent:                 Developer:
     affordability: 35%      affordability: 20%      affordability: 10%
     commute:       25%      commute:       15%      commute:        5%
     safety:        15%      safety:        25%      safety:        10%
     amenities:     15%      amenities:     10%      amenities:     15%
     schools:        0%      schools:       30%      schools:       20%
     investment:    10%      investment:     0%      investment:    40%
   ```

3. **Adjust weights by user importance ratings**
   - User provides 0-10 importance for each factor
   - Scale base weights proportionally

4. **Filter by budget before scoring**
   - The only filter implemented is the budget filter in
     `get_candidate_areas()` (`tools/fetch_scansan.py`), applied before
     enrichment. The scorer itself does not drop candidates, so
     max_commute / min_safety / min_school_rating are not enforced anywhere.

5. **Calculate weighted composite score**
   - composite_score = Σ(factor_score × adjusted_weight)
   - Store individual factor contributions for transparency

6. **Rank candidates by composite score**

7. **Generate factor breakdown for each candidate**
   - Show which factors helped/hurt the score
   - Identify trade-offs between top candidates

8. **Output top N recommendations** (default N=10)

## Outputs
One dict per area, ranked. This is the real shape returned by
`rank_areas()`; a missing factor falls back to a neutral 50 (30 minutes for
commute), so a factor score of exactly 50 usually means "no data".
```json
{
  "area_code": "E1",
  "area_name": "Whitechapel",
  "rank": 1,
  "composite_score": 73.9,
  "factor_breakdown": {
    "affordability": 85,
    "commute": 63.3,
    "safety": 62,
    "amenities": 80,
    "schools": 65,
    "investment": 70
  },
  "strengths": ["affordability", "amenities"],
  "weaknesses": [],
  "explanation": null,
  "enrichment_data": {"...": "the raw fetcher output, kept for the explainer"}
}
```
Strengths are the highest-scoring factors that clear 70 (at most two);
weaknesses are every factor below 50.

## Edge Cases & Learnings
- **Missing data**: If a factor has no data for an area, exclude that area or use neutral score (50)
  - Log which areas excluded and why
- **Weight normalization**: Ensure adjusted weights sum to 100%
- **Tied scores**: not handled; `sort()` is stable, so ties keep fetch order
- **No candidates pass the budget filter**: the pipeline reports zero areas
  rather than relaxing the budget
- **Explanation generation**: Use factor contributions to generate natural language
  - Top contributor → "primarily because..."
  - Secondary contributors → "also benefits from..."

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates based on user feedback and actual scoring behavior]
