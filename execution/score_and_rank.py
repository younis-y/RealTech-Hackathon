#!/usr/bin/env python3
"""
Scoring and Ranking Engine
Combines ScanSan + enrichment data to produce persona-specific ranked recommendations.
Directive: directives/scoring_ranking_engine.md
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


# Persona-specific base weights (sum to 100)
PERSONA_WEIGHTS = {
    "student": {
        "affordability": 35,
        "commute": 25,
        "safety": 15,
        "amenities": 20,
        "investment_quality": 5
    },
    "parent": {
        "affordability": 20,
        "schools": 30,
        "safety": 25,
        "commute": 15,
        "amenities": 10
    },
    "developer": {
        "investment_quality": 40,
        "demand_index": 25,
        "risk_score": 20,
        "infrastructure": 15
    }
}


def score_and_rank(
    persona: str,
    user_preferences: Dict,
    enrichment_data: Dict,
    top_n: int = 10
) -> Dict:
    """
    Score and rank candidate areas based on persona and preferences.

    Args:
        persona: "student" | "parent" | "developer"
        user_preferences: User-specified weights and constraints
        enrichment_data: Pre-fetched data from all API directives
        top_n: Number of top recommendations to return

    Returns:
        Dictionary with ranked recommendations and metadata
    """
    if persona not in PERSONA_WEIGHTS:
        raise ValueError(f"Invalid persona: {persona}")

    # Extract candidates from enrichment data
    candidates = list(enrichment_data.keys())

    # Calculate adjusted weights
    adjusted_weights = calculate_adjusted_weights(
        persona,
        user_preferences.get("importance_weights", {})
    )

    # Score each candidate
    scored_candidates = []
    filtered_out = []

    for area_code in candidates:
        area_data = enrichment_data[area_code]

        # Apply hard constraints (filters)
        if not passes_constraints(area_data, user_preferences):
            filtered_out.append({
                "area_code": area_code,
                "reason": get_filter_reason(area_data, user_preferences)
            })
            continue

        # Calculate composite score
        scores = calculate_factor_scores(area_data, persona)
        composite_score, contributions = calculate_composite_score(
            scores,
            adjusted_weights
        )

        # Identify strengths and weaknesses
        strengths, weaknesses = identify_strengths_weaknesses(scores, persona)

        scored_candidates.append({
            "area_code": area_code,
            "composite_score": round(composite_score, 1),
            "factor_scores": {k: round(v, 0) for k, v in scores.items()},
            "factor_contributions": {k: round(v, 1) for k, v in contributions.items()},
            "strengths": strengths,
            "weaknesses": weaknesses,
            "raw_data": area_data
        })

    # Sort by composite score (descending)
    scored_candidates.sort(key=lambda x: x["composite_score"], reverse=True)

    # Add trade-off analysis for top candidates
    top_candidates = scored_candidates[:top_n]
    for i, candidate in enumerate(top_candidates):
        candidate["rank"] = i + 1
        candidate["trade_offs"] = generate_trade_offs(
            candidate,
            top_candidates,
            persona
        )

    return {
        "persona": persona,
        "user_preferences": user_preferences,
        "adjusted_weights": adjusted_weights,
        "recommendations": top_candidates,
        "filtered_out_count": len(filtered_out),
        "filtered_out_reasons": filtered_out[:5],  # Show sample
        "timestamp": datetime.now().isoformat()
    }


def calculate_adjusted_weights(persona: str, user_importance: Dict) -> Dict:
    """Adjust base weights by user importance ratings (0-10 scale)."""
    base_weights = PERSONA_WEIGHTS[persona].copy()

    if not user_importance:
        return base_weights

    # Scale base weights by user importance
    adjusted = {}
    for factor, base_weight in base_weights.items():
        importance = user_importance.get(factor, 5)  # default 5 (neutral)
        adjusted[factor] = base_weight * (importance / 5.0)

    # Normalize to sum to 100
    total = sum(adjusted.values())
    if total > 0:
        adjusted = {k: (v / total) * 100 for k, v in adjusted.items()}

    return adjusted


def calculate_factor_scores(area_data: Dict, persona: str) -> Dict:
    """Extract and normalize factor scores from area data."""
    scores = {}

    # ScanSan scores (already 0-100)
    if "scansan" in area_data:
        ss = area_data["scansan"]
        scores["affordability"] = ss.get("affordability_score", 50)
        scores["investment_quality"] = ss.get("investment_quality", 50)
        scores["demand_index"] = ss.get("demand_index", 50)
        scores["risk_score"] = ss.get("risk_score", 50)

    # Commute score (inverse of duration)
    if "commute" in area_data:
        duration = area_data["commute"].get("duration_minutes", 60)
        # 0 min = 100, 60 min = 0, linear
        scores["commute"] = max(0, min(100, 100 - (duration / 60 * 100)))

    # Safety score (from crime data)
    if "crime" in area_data:
        scores["safety"] = area_data["crime"].get("safety_score", 50)

    # Schools score
    if "schools" in area_data:
        scores["schools"] = area_data["schools"].get("avg_primary_score", 50)

    # Amenities score
    if "amenities" in area_data:
        scores["amenities"] = area_data["amenities"].get("density_score", 50)

    # Infrastructure (for developers)
    if "infrastructure" in area_data:
        scores["infrastructure"] = area_data["infrastructure"].get("score", 50)

    return scores


def calculate_composite_score(scores: Dict, weights: Dict) -> tuple:
    """Calculate weighted composite score and individual contributions."""
    composite = 0.0
    contributions = {}

    for factor, weight in weights.items():
        if factor in scores:
            contribution = (scores[factor] * weight) / 100
            contributions[factor] = contribution
            composite += contribution
        else:
            contributions[factor] = 0.0

    return composite, contributions


def passes_constraints(area_data: Dict, preferences: Dict) -> bool:
    """Check if area passes hard constraints (filters)."""
    # Budget constraint
    if "budget_max" in preferences and "scansan" in area_data:
        price = area_data["scansan"].get("avg_price", float('inf'))
        if price > preferences["budget_max"]:
            return False

    # Max commute constraint
    if "max_commute_minutes" in preferences and "commute" in area_data:
        duration = area_data["commute"].get("duration_minutes", float('inf'))
        if duration > preferences["max_commute_minutes"]:
            return False

    # Min safety constraint
    if "min_safety_score" in preferences and "crime" in area_data:
        safety = area_data["crime"].get("safety_score", 0)
        if safety < preferences["min_safety_score"]:
            return False

    # Min school rating constraint
    if "min_school_rating" in preferences and "schools" in area_data:
        school_score = area_data["schools"].get("avg_primary_score", 0)
        if school_score < preferences["min_school_rating"]:
            return False

    return True


def get_filter_reason(area_data: Dict, preferences: Dict) -> str:
    """Determine why area was filtered out."""
    if "budget_max" in preferences and "scansan" in area_data:
        price = area_data["scansan"].get("avg_price", 0)
        if price > preferences["budget_max"]:
            return f"Over budget: £{price} > £{preferences['budget_max']}"

    if "max_commute_minutes" in preferences and "commute" in area_data:
        duration = area_data["commute"].get("duration_minutes", 0)
        if duration > preferences["max_commute_minutes"]:
            return f"Commute too long: {duration} min > {preferences['max_commute_minutes']} min"

    return "Did not meet constraints"


def identify_strengths_weaknesses(scores: Dict, persona: str) -> tuple:
    """Identify top strengths and weaknesses based on scores."""
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    strengths = []
    weaknesses = []

    for factor, score in sorted_scores[:3]:
        if score >= 80:
            strengths.append(factor.replace("_", " ").title())

    for factor, score in reversed(sorted_scores[-2:]):
        if score < 60:
            weaknesses.append(factor.replace("_", " ").title())

    return strengths, weaknesses


def generate_trade_offs(candidate: Dict, all_top: List[Dict], persona: str) -> str:
    """Generate trade-off description comparing to other top candidates."""
    rank = candidate["rank"]

    if rank == 1:
        return "Top-ranked with best overall balance of factors"

    # Find what this candidate excels at vs #1
    top_candidate = all_top[0]
    better_factors = []
    worse_factors = []

    for factor, score in candidate["factor_scores"].items():
        top_score = top_candidate["factor_scores"].get(factor, 50)
        if score > top_score + 5:
            better_factors.append(factor.replace("_", " "))
        elif score < top_score - 5:
            worse_factors.append(factor.replace("_", " "))

    if better_factors and worse_factors:
        return f"Better {', '.join(better_factors[:2])} but lower {', '.join(worse_factors[:2])}"
    elif worse_factors:
        return f"Lower {', '.join(worse_factors[:2])} than top choice"
    else:
        return "Similar profile to top choice"


if __name__ == "__main__":
    # Example usage
    sample_data = {
        "E1 6AN": {
            "scansan": {"affordability_score": 92, "investment_quality": 72},
            "commute": {"duration_minutes": 25},
            "crime": {"safety_score": 78},
            "amenities": {"density_score": 90}
        }
    }

    sample_prefs = {
        "budget_max": 1200,
        "max_commute_minutes": 30,
        "importance_weights": {"affordability": 8, "commute": 7}
    }

    results = score_and_rank("student", sample_prefs, sample_data)
    print(json.dumps(results, indent=2))
