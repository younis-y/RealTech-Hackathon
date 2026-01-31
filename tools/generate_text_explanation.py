#!/usr/bin/env python3
"""
Text Explanation Generator
Generates natural language explanations using Anthropic Claude API.
Architecture SOP: architecture/03_explanation_generation.md (to be created)
Data Schema: gemini.md (#9 Explanation Generation Schema)
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
import anthropic

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.cache_manager import read_cache, write_cache

# Load environment variables
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-5-20250929"


def generate_explanation(
    recommendation: Dict,
    persona: str,
    format_type: str = "medium",
    use_cache: bool = True
) -> Optional[str]:
    """
    Generate natural language explanation for a recommendation.

    Args:
        recommendation: Recommendation dict with scores and enrichment data
        persona: User persona
        format_type: "short" (1-2 sentences), "medium" (1 paragraph), "long" (2-3 paragraphs)
        use_cache: Whether to check cache first

    Returns:
        Explanation string or None if error
    """
    area_code = recommendation["area_code"]
    area_name = recommendation["area_name"]

    # Check cache
    cache_key = f"{area_code}_{persona}_{format_type}"
    if use_cache:
        cached = read_cache("explanation", cache_key)
        if cached:
            print(f"[CACHE] Using cached explanation for {cache_key}")
            return cached.get("explanation")

    # Build prompt
    composite_score = recommendation["composite_score"]
    factor_scores = recommendation["factor_breakdown"]
    strengths = recommendation["strengths"]
    weaknesses = recommendation["weaknesses"]

    # Format target length
    length_guides = {
        "short": "1-2 sentences",
        "medium": "1 short paragraph (3-4 sentences)",
        "long": "2 paragraphs (6-8 sentences total)"
    }

    prompt = f"""You are a housing recommendation assistant helping a {persona} find the best area in London.

Generate a natural language explanation for why {area_name} ({area_code}) is recommended for this {persona}.

SCORES (all 0-100):
- Overall Score: {composite_score:.1f}/100
- Affordability: {factor_scores['affordability']}/100
- Commute Time: {factor_scores['commute']}/100
- Safety: {factor_scores['safety']}/100
- Schools: {factor_scores['schools']}/100
- Amenities: {factor_scores['amenities']}/100
- Investment Quality: {factor_scores['investment']}/100

STRENGTHS: {', '.join(strengths) if strengths else 'None'}
WEAKNESSES: {', '.join(weaknesses) if weaknesses else 'None'}

REQUIREMENTS:
- Write {length_guides[format_type]}
- Focus on what matters most to a {persona}
- Be specific and use the actual score numbers
- Mention key strengths and acknowledge any significant weaknesses
- Be honest and balanced - don't oversell or hide problems
- Use UK English (e.g., "flats" not "apartments")
- Don't hallucinate - only reference the data provided above

Generate the explanation:"""

    try:
        if not ANTHROPIC_API_KEY:
            print("[ERROR] ANTHROPIC_API_KEY not set in .env")
            return None

        # Call Claude API
        print(f"[API] Generating explanation for {area_name}")
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=MODEL,
            max_tokens=300,
            temperature=0.3,  # Low temperature for factual, consistent output
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        explanation = message.content[0].text.strip()

        # Cache the result
        if use_cache:
            cache_data = {
                "area_code": area_code,
                "persona": persona,
                "format_type": format_type,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat(),
                "data_source": "claude_api"
            }
            write_cache("explanation", cache_key, cache_data)

        return explanation

    except Exception as e:
        print(f"[ERROR] Failed to generate explanation: {e}")
        return None


if __name__ == "__main__":
    print("="*80)
    print("Text Explanation Generator - Test Mode")
    print("="*80)
    print("")

    # Mock recommendation
    mock_rec = {
        "area_code": "E1",
        "area_name": "Whitechapel",
        "composite_score": 72.5,
        "factor_breakdown": {
            "affordability": 75,
            "commute": 85,
            "safety": 45,
            "schools": 65,
            "amenities": 70,
            "investment": 60
        },
        "strengths": ["affordability", "commute"],
        "weaknesses": ["safety"]
    }

    print("Test: Generate explanation for student persona")
    explanation = generate_explanation(mock_rec, "student", "medium")
    if explanation:
        print(f"Explanation:\n{explanation}")
    print("")

    print("="*80)
