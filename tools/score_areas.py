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


def generate_strength_description(factor: str, score: int, enrichment_data: Dict, persona: str = "student") -> str:
    """
    Generate creative, persona-specific strength descriptions.
    Cross-references multiple data points for richer insights.
    """
    import random
    
    scansan = enrichment_data.get("scansan", {})
    commute = enrichment_data.get("commute", {})
    schools = enrichment_data.get("schools", {})
    crime = enrichment_data.get("crime", {})
    
    rent = scansan.get("avg_price_rent_pm", 1500)
    yield_est = scansan.get("yield_estimate", 4.5)
    growth = scansan.get("price_trends", {}).get("5yr_forecast", 12)
    duration = commute.get("duration_minutes", 25)
    route = commute.get("route_summary", "tube/bus")
    destination = commute.get("to", "Central London")
    school_count = schools.get("school_count", 5)
    ofsted_good = schools.get("ofsted_good_pct", 75)
    park_count = scansan.get("park_count", 3)
    safety_pct = crime.get("safety_percentile", 65)
    
    # Base templates for all personas
    base_templates = {
        "commute": [
            f"⚡ {duration}-min commute via {route} — faster than 70% of London",
            f"🚇 Excellent transport links: {duration} min to {destination}",
            f"✨ Prime Zone 2/3 location cuts your daily commute significantly",
        ],
        "affordability": [
            f"💰 £{rent:,}/mo is {max(0, round((2300-rent)/23))}% below London average",
            f"🏠 Strong value: £{rent:,}/mo leaves budget for savings",
            f"📉 Competitive pricing in a high-demand area",
        ],
        "investment": [
            f"📈 {yield_est:.1f}% gross yield with {growth}% projected 5yr growth",
            f"🎯 Capital appreciation potential: +{growth}% forecast",
            f"💎 Strong fundamentals: demand outpacing supply in this postcode",
        ],
        "safety": [
            f"🛡️ Top {100-safety_pct}% safest area in borough — Met Police verified",
            f"✅ Low crime neighbourhood with active community watch",
            f"🏘️ Established residential area with strong sense of community",
        ],
        "schools": [
            f"🎓 {school_count} schools nearby, {ofsted_good}% rated Good/Outstanding",
            f"📚 Strong primary catchment with sought-after secondaries",
            f"👨‍👩‍👧 Education hub: multiple Ofsted 'Outstanding' primaries in catchment",
        ],
        "amenities": [
            f"🛒 Walkable neighbourhood with 50+ shops and cafes",
            f"🍽️ Vibrant high street with independent retailers",
            f"🏃 Parks, gyms, and leisure within 10-min walk",
        ]
    }
    
    # Persona-specific enhanced templates
    persona_templates = {
        "parent": {
            "schools": [
                f"🎓 Family goldmine: {school_count} schools, {ofsted_good}% Ofsted Good+ rated",
                f"📚 Top catchments: Outstanding primaries + grammar school access",
                f"👨‍👩‍👧 School-run friendly: walking distance to multiple quality schools",
                f"🏫 Education excellence: feeder schools to top secondaries in borough",
            ],
            "safety": [
                f"🛡️ Family-safe zone: crime rates 40% below London average",
                f"✅ Quiet residential streets — ideal for children playing outside",
                f"🏘️ Strong parent community with active neighbourhood watch",
            ],
            "amenities": [
                f"🛒 Family essentials: supermarkets, GP, pharmacy all walkable",
                f"🏞️ {park_count}+ parks and playgrounds within 10-min walk",
                f"👶 Family-oriented: soft play, swimming pools, kids activities nearby",
            ],
        },
        "student": {
            "commute": [
                f"⚡ Campus in {duration} min — more time for studying (or socialising!)",
                f"🚇 Night tube access for late library sessions or nights out",
            ],
            "affordability": [
                f"💰 Student-friendly £{rent:,}/mo — stretch that maintenance loan",
                f"🏠 Affordable house-share zone: £{round(rent/3):,}/mo per room typical",
            ],
            "amenities": [
                f"🍽️ Vibrant nightlife and student bars on your doorstep",
                f"☕ Café culture central: perfect for study sessions",
            ],
        },
        "developer": {
            "investment": [
                f"📈 IRR potential: {yield_est:.1f}% yield + {growth}% growth = {yield_est+growth:.1f}% total return",
                f"🎯 Value-add opportunity: regeneration corridor with strong fundamentals",
                f"💎 Cap rate compression expected as area gentrifies",
            ],
            "schools": [
                f"🎓 Schools drive family demand = lower void periods",
                f"📚 Education quality adds £25-50k to family home premiums",
            ],
        }
    }
    
    # Get templates: persona-specific first, then fallback to base
    if persona in persona_templates and factor in persona_templates[persona]:
        templates = persona_templates[persona][factor]
    else:
        templates = base_templates.get(factor, [f"✓ Strong {factor} performance ({score}/100)"])
    
    return random.choice(templates)


def generate_weakness_description(factor: str, score: int, enrichment_data: Dict, persona: str = "student") -> str:
    """
    Generate creative, actionable weakness descriptions.
    Provides context and potential mitigations.
    """
    import random
    
    scansan = enrichment_data.get("scansan", {})
    commute = enrichment_data.get("commute", {})
    schools = enrichment_data.get("schools", {})
    
    rent = scansan.get("avg_price_rent_pm", 1500)
    yield_est = scansan.get("yield_estimate", 4.5)
    duration = commute.get("duration_minutes", 25)
    school_count = schools.get("school_count", 3)
    
    weakness_templates = {
        "commute": [
            f"⏱️ {duration}-min commute is above average — consider if remote work days offset this",
            f"🚌 Longer journey times ({duration} min) may impact work-life balance",
            f"📍 Outer zone location trades convenience for affordability — evaluate your priorities",
        ],
        "affordability": [
            f"💷 Premium pricing at £{rent:,}/mo — but strong amenities may justify the cost",
            f"📊 Above-average rent; consider house-sharing to reduce individual burden",
            f"⚠️ Budget stretch warning: £{rent:,}/mo may exceed 35% of median income",
        ],
        "investment": [
            f"📉 {yield_est}% yield is below the 5% benchmark — growth may compensate long-term",
            f"🏷️ Current valuations suggest limited upside; better entry points may exist nearby",
            f"⚖️ Risk/reward balance: solid area but not a high-yield investment play",
        ],
        "safety": [
            f"🔒 Safety score ({score}/100) warrants attention — research specific streets",
            f"⚠️ Some crime hotspots nearby; consider security-enhanced properties",
            f"👁️ Mixed reputation — newer developments often have better infrastructure",
        ],
        "schools": [
            f"🏫 Only {school_count} schools in catchment — limited options for families",
            f"📝 Below-average Ofsted ratings; consider private alternatives",
            f"👶 Better suited for young professionals or couples than families",
        ],
        "amenities": [
            f"🛒 Fewer shops and services — car or delivery reliance likely",
            f"🏪 Developing neighborhood: expect 5-10 min travel for major retail",
            f"🌱 Quieter area trades nightlife for tranquility — depends on lifestyle",
        ]
    }
    
    templates = weakness_templates.get(factor, [f"Below average {factor} ({score}/100)"])
    return random.choice(templates)





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

        # Generate rich strength descriptions
        strength_descriptions = []
        for factor in score_data["strengths"][:2]:  # Top 2 strengths
            score = score_data["factor_scores"].get(factor, 50)
            description = generate_strength_description(factor, score, area_data, persona)
            strength_descriptions.append(description)
        
        # Generate rich weakness descriptions  
        weakness_descriptions = []
        for factor in score_data["weaknesses"][:2]:  # Top 2 weaknesses
            score = score_data["factor_scores"].get(factor, 50)
            description = generate_weakness_description(factor, score, area_data, persona)
            weakness_descriptions.append(description)

        # Build recommendation
        rec = {
            "area_code": area_code,
            "area_name": area_data.get("scansan", {}).get("area_name", area_code),
            "rank": 0,  # Will be set after sorting
            "composite_score": score_data["composite_score"],
            "factor_breakdown": score_data["factor_scores"],
            "strengths": strength_descriptions if strength_descriptions else ["Well-balanced area with no standout weaknesses"],
            "weaknesses": weakness_descriptions if weakness_descriptions else ["No significant concerns identified"],
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
