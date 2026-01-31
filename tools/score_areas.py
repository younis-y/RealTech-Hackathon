#!/usr/bin/env python3
"""
Area Scoring Engine
Calculates persona-specific scores for areas based on enrichment data.
Architecture SOP: architecture/02_scoring_engine.md (to be created)
Data Schema: gemini.md (#8 Recommendation Output Schema)
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Persona-specific weights (from gemini.md Discovery Questions)
PERSONA_WEIGHTS = {
    "student": {
        "affordability": 0.35,      # 35% - Most important for students
        "commute": 0.25,             # 25% - Important to get to campus
        "safety": 0.15,              # 15% - Moderate concern
        "amenities": 0.15,           # 15% - Nightlife and cafes
        "schools": 0.00,             # 0% - Not relevant
        "investment": 0.10,          # 10% - Minor concern
    },
    "parent": {
        "affordability": 0.20,       # 20% - Important but not primary
        "commute": 0.15,             # 15% - Moderate
        "safety": 0.25,              # 25% - High priority for families
        "amenities": 0.10,           # 10% - Parks and family facilities
        "schools": 0.30,             # 30% - Most important for parents!
        "investment": 0.00,          # 0% - Usually renting/already own
    },
    "developer": {
        "affordability": 0.10,       # 10% - Looking for value, not cheap
        "commute": 0.05,             # 5% - Not relevant
        "safety": 0.10,              # 10% - Affects property value
        "amenities": 0.15,           # 15% - Attracts tenants
        "schools": 0.20,             # 20% - Attracts families (tenants)
        "investment": 0.40,          # 40% - Primary concern!
    }
}


def calculate_composite_score(
    enrichment_data: Dict,
    persona: str,
    user_weights: Optional[Dict] = None
) -> Dict:
    """
    Calculate persona-specific composite score.

    Args:
        enrichment_data: Dict with all enriched data for an area
        persona: "student", "parent", or "developer"
        user_weights: Optional user adjustments to weights

    Returns:
        Dict with scores and breakdown
    """
    # Get base weights for persona
    weights = PERSONA_WEIGHTS.get(persona, PERSONA_WEIGHTS["student"]).copy()

    # Apply user weight adjustments if provided
    if user_weights:
        for factor, user_weight in user_weights.items():
            if factor in weights:
                # User weight is 0-10, convert to multiplier 0.5-1.5
                multiplier = 0.5 + (user_weight / 10)
                weights[factor] *= multiplier

        # Renormalize weights to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

    # Extract scores from enrichment data
    scansan = enrichment_data.get("scansan", {})
    commute = enrichment_data.get("commute", {})
    crime = enrichment_data.get("crime", {})
    schools = enrichment_data.get("schools", {})
    amenities = enrichment_data.get("amenities", {})

    # Get factor scores (all normalized to 0-100)
    factor_scores = {
        "affordability": scansan.get("affordability_score", 50),
        "commute": 100 - min(100, (commute.get("duration_minutes", 30) / 60 * 100)),  # Shorter is better
        "safety": crime.get("safety_score", 50),
        "amenities": amenities.get("density_score", 50),
        "schools": schools.get("avg_quality_score", 50),
        "investment": scansan.get("investment_quality", 50),
    }

    # Calculate weighted composite score
    composite_score = sum(
        factor_scores[factor] * weight
        for factor, weight in weights.items()
    )

    # Calculate contributions (for explanation)
    contributions = {
        factor: {
            "score": factor_scores[factor],
            "weight": weights[factor],
            "contribution": factor_scores[factor] * weights[factor]
        }
        for factor in factor_scores
    }

    # Identify strengths and weaknesses
    sorted_factors = sorted(contributions.items(), key=lambda x: x[1]["score"], reverse=True)
    strengths = [f for f, _ in sorted_factors[:2] if contributions[f]["score"] >= 70]
    weaknesses = [f for f, _ in sorted_factors if contributions[f]["score"] < 50]

    return {
        "composite_score": round(composite_score, 1),
        "factor_scores": factor_scores,
        "weights_applied": weights,
        "contributions": contributions,
        "strengths": strengths,
        "weaknesses": weaknesses
    }


def rank_areas(
    enriched_areas: List[Dict],
    persona: str,
    user_weights: Optional[Dict] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Rank areas by persona-specific scores.

    Args:
        enriched_areas: List of dicts with area enrichment data
        persona: User persona
        user_weights: Optional user weight adjustments
        limit: Max recommendations to return

    Returns:
        List of ranked recommendations
    """
    recommendations = []

    for area_data in enriched_areas:
        area_code = area_data.get("area_code")

        # Calculate score
        score_data = calculate_composite_score(area_data, persona, user_weights)

        # Build recommendation
        rec = {
            "area_code": area_code,
            "area_name": area_data.get("scansan", {}).get("area_name", area_code),
            "rank": 0,  # Will be set after sorting
            "composite_score": score_data["composite_score"],
            "factor_breakdown": score_data["factor_scores"],
            "strengths": score_data["strengths"],
            "weaknesses": score_data["weaknesses"],
            "explanation": None,  # To be filled by generate_text_explanation.py
            "enrichment_data": area_data  # Keep for explanation generation
        }

        recommendations.append(rec)

    # Sort by composite score
    recommendations.sort(key=lambda x: x["composite_score"], reverse=True)

    # Assign ranks
    for i, rec in enumerate(recommendations[:limit], 1):
        rec["rank"] = i

    return recommendations[:limit]


if __name__ == "__main__":
    print("="*80)
    print("Area Scoring Engine - Test Mode")
    print("="*80)
    print("")

    # Mock enrichment data for test
    mock_areas = [
        {
            "area_code": "E1",
            "scansan": {"area_name": "Whitechapel", "affordability_score": 75, "investment_quality": 60},
            "commute": {"duration_minutes": 15},
            "crime": {"safety_score": 45},
            "schools": {"avg_quality_score": 65},
            "amenities": {"density_score": 70}
        },
        {
            "area_code": "SW1",
            "scansan": {"area_name": "Westminster", "affordability_score": 25, "investment_quality": 90},
            "commute": {"duration_minutes": 10},
            "crime": {"safety_score": 60},
            "schools": {"avg_quality_score": 85},
            "amenities": {"density_score": 95}
        }
    ]

    print("Test: Ranking for Student persona")
    results = rank_areas(mock_areas, "student")
    for rec in results:
        print(f"  #{rec['rank']}: {rec['area_name']} - Score: {rec['composite_score']}/100")
        print(f"    Strengths: {', '.join(rec['strengths']) if rec['strengths'] else 'None'}")
        print(f"    Weaknesses: {', '.join(rec['weaknesses']) if rec['weaknesses'] else 'None'}")
    print("")

    print("="*80)
