#!/usr/bin/env python3
"""
Natural Language Explanation Generator
Converts structured scores into persona-specific explanations using Claude API.
Directive: directives/explanation_generator.md
"""

import os
import json
from typing import Dict, Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# Persona tone and focus
PERSONA_CONTEXT = {
    "student": {
        "tone": "casual, friendly, encouraging",
        "focus": "budget, commute, social life, nightlife",
        "language": "Use 'you' and 'your'. Keep it conversational."
    },
    "parent": {
        "tone": "careful, detailed, reassuring",
        "focus": "schools, safety, family amenities, long-term value",
        "language": "Use 'you' and 'your'. Be thorough but clear."
    },
    "developer": {
        "tone": "analytical, data-driven, professional",
        "focus": "ROI, risk, fundamentals, market trends",
        "language": "Use precise numbers and percentages. Be concise."
    }
}


def generate_explanation(
    recommendation_data: Dict,
    persona: str,
    output_format: str = "medium",
    comparison_areas: Optional[list] = None
) -> Dict:
    """
    Generate natural language explanation from structured recommendation data.

    Args:
        recommendation_data: Full recommendation object from scoring engine
        persona: "student" | "parent" | "developer"
        output_format: "short" (50 words) | "medium" (150 words) | "video_script" (200 words)
        comparison_areas: Optional list of other top candidates

    Returns:
        Dictionary with explanation text and metadata
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")

    if persona not in PERSONA_CONTEXT:
        raise ValueError(f"Invalid persona: {persona}")

    # Build structured prompt
    prompt = build_prompt(
        recommendation_data,
        persona,
        output_format,
        comparison_areas
    )

    # Call Claude API
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            temperature=0.3,  # Low temperature to reduce creativity/hallucination
            system=get_system_prompt(persona),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        explanation_text = message.content[0].text

        # Validate (basic check for hallucination)
        is_valid = validate_explanation(explanation_text, recommendation_data)

        return {
            "explanation": explanation_text,
            "format": output_format,
            "persona": persona,
            "validation_passed": is_valid,
            "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
            "cost_usd": calculate_cost(message.usage)
        }

    except Exception as e:
        return {
            "explanation": None,
            "error": str(e),
            "format": output_format,
            "persona": persona
        }


def get_system_prompt(persona: str) -> str:
    """Get system prompt for Claude API."""
    context = PERSONA_CONTEXT[persona]

    return f"""You are explaining property/area recommendations to a {persona}.

CRITICAL CONSTRAINT: Only reference data points explicitly provided. Do not introduce external facts, assumptions, or general knowledge. If a data point is not provided, do not mention it.

Tone: {context['tone']}
Focus areas: {context['focus']}
Language style: {context['language']}

Format requirements:
- Use specific numbers from the data provided
- Use UK English (flats not apartments, high street not main street)
- Format prices as £X,XXX
- Format percentages as X.X%
- Use "out of 100" for scores

Your job is to translate structured data into clear, helpful explanations."""


def build_prompt(
    recommendation: Dict,
    persona: str,
    output_format: str,
    comparison_areas: Optional[list]
) -> str:
    """Build the user prompt with all data."""
    area_code = recommendation.get("area_code", "Unknown")
    composite_score = recommendation.get("composite_score", 0)
    factor_scores = recommendation.get("factor_scores", {})
    factor_contributions = recommendation.get("factor_contributions", {})
    strengths = recommendation.get("strengths", [])
    weaknesses = recommendation.get("weaknesses", [])
    trade_offs = recommendation.get("trade_offs", "")

    # Word count targets
    word_counts = {
        "short": "approximately 50 words",
        "medium": "approximately 150 words",
        "video_script": "approximately 200 words"
    }

    prompt = f"""Generate a {output_format} explanation for this recommendation.

DATA PROVIDED:
- Area: {area_code}
- Overall composite score: {composite_score}/100
- Factor scores: {json.dumps(factor_scores, indent=2)}
- Factor contributions to overall score: {json.dumps(factor_contributions, indent=2)}
- Key strengths: {', '.join(strengths) if strengths else 'None identified'}
- Weaknesses: {', '.join(weaknesses) if weaknesses else 'None identified'}
- Trade-offs: {trade_offs}
"""

    if comparison_areas:
        prompt += f"\nComparison areas: {json.dumps(comparison_areas, indent=2)}\n"

    prompt += f"""
Target length: {word_counts[output_format]}

Format:
"""

    if output_format == "short":
        prompt += "- One paragraph, punchy summary\n- Lead with area name and overall score\n- Hit 2-3 key highlights\n- End with who this is best for"
    elif output_format == "medium":
        prompt += "- 2-3 paragraphs\n- Lead with area name and overall score\n- Break down key factors with specific numbers\n- Mention trade-offs\n- Conclude with recommendation"
    elif output_format == "video_script":
        prompt += "- Intro hook (5-10 words)\n- Overall score statement\n- 2-3 key factors with numbers\n- Trade-off or comparison\n- Closing recommendation\n- Write as if narrating a video"

    prompt += "\n\nGenerate explanation (remember: ONLY use data provided above):"

    return prompt


def validate_explanation(explanation: str, data: Dict) -> bool:
    """
    Basic validation to check for hallucinations.
    Returns False if explanation contains suspicious patterns.
    """
    # This is a simple check; more sophisticated validation could be added
    area_code = data.get("area_code", "")

    # Check that area code is mentioned
    if area_code and area_code not in explanation:
        return False

    # Check for common hallucination patterns
    hallucination_indicators = [
        "according to recent",
        "studies show",
        "it is known",
        "typically",
        "usually",
        "most areas"
    ]

    explanation_lower = explanation.lower()
    for indicator in hallucination_indicators:
        if indicator in explanation_lower:
            return False

    return True


def calculate_cost(usage) -> float:
    """Calculate approximate cost based on Claude Sonnet pricing."""
    # Claude Sonnet 4.5 pricing (as of Jan 2025, approximate)
    INPUT_COST_PER_1M = 3.0  # $3 per 1M input tokens
    OUTPUT_COST_PER_1M = 15.0  # $15 per 1M output tokens

    input_cost = (usage.input_tokens / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (usage.output_tokens / 1_000_000) * OUTPUT_COST_PER_1M

    return round(input_cost + output_cost, 4)


if __name__ == "__main__":
    # Example usage
    sample_recommendation = {
        "area_code": "E1 6AN",
        "composite_score": 87.3,
        "factor_scores": {
            "affordability": 92,
            "commute": 85,
            "safety": 78,
            "amenities": 90
        },
        "factor_contributions": {
            "affordability": 32.2,
            "commute": 21.3,
            "safety": 11.7,
            "amenities": 18.0
        },
        "strengths": ["Excellent nightlife", "Quick commute", "Very affordable"],
        "weaknesses": ["Slightly higher crime"],
        "trade_offs": "Prioritizes convenience over safety margin"
    }

    result = generate_explanation(
        sample_recommendation,
        persona="student",
        output_format="medium"
    )

    print(json.dumps(result, indent=2))
