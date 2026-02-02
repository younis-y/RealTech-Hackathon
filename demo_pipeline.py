#!/usr/bin/env python3
"""
Domus Housing Recommendation Pipeline - Full Demo
Demonstrates the complete end-to-end pipeline from user input to recommendations.
"""

import sys
import os
from datetime import datetime

# Add tools to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.fetch_scansan import fetch_scansan_data, get_candidate_areas
from tools.fetch_tfl_commute import fetch_commute_data
from tools.fetch_crime_data import fetch_crime_data
from tools.fetch_schools import fetch_schools_data
from tools.fetch_amenities import fetch_amenities_data
from tools.fetch_air_quality import fetch_air_quality
from tools.fetch_epc import get_area_epc_summary
from tools.score_areas import rank_areas
# from tools.generate_text_explanation import generate_explanation # Moved to inside function


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_user_input(persona, budget, location_type, destination):
    """Print user input summary."""
    print_header("USER INPUT")
    print(f"Persona: {persona.upper()}")
    print(f"Budget: £{budget:,}/month" if location_type == "rent" else f"Budget: £{budget:,}")
    print(f"Location Type: {location_type.upper()}")
    if destination:
        print(f"Destination: {destination}")
    print()


def enrich_area(area_code, destination=None):
    """
    Enrich an area with all data sources.

    Args:
        area_code: Area to enrich
        destination: Optional destination for commute calculation

    Returns:
        Dict with all enrichment data
    """
    print(f"  Enriching {area_code}...")

    # Fetch all data
    scansan = fetch_scansan_data(area_code)
    commute = fetch_commute_data(area_code, destination) if destination else None
    crime = fetch_crime_data(area_code)
    schools = fetch_schools_data(area_code)
    amenities = fetch_amenities_data(area_code)
    air_quality = fetch_air_quality()
    epc = get_area_epc_summary(area_code)

    return {
        "area_code": area_code,
        "scansan": scansan or {},
        "commute": commute or {},
        "crime": crime or {},
        "schools": schools or {},
        "amenities": amenities or {},
        "air_quality": air_quality or {},
        "epc": epc or {}
    }


def display_recommendations(recommendations, persona, show_explanations=True):
    """Display ranked recommendations with details."""
    print_header("RECOMMENDATIONS")

    for rec in recommendations:
        rank = rec["rank"]
        name = rec["area_name"]
        score = rec["composite_score"]

        print(f"#{rank}. {name} ({rec['area_code']}) - Score: {score:.1f}/100")
        print("-" * 80)

        # Factor breakdown
        print("\nFactor Scores:")
        factors = rec["factor_breakdown"]
        for factor, value in factors.items():
            bar_length = int(value / 5)  # 0-20 characters
            bar = "#" * bar_length
            print(f"  {factor:15s}: {value:3.0f}/100 {bar}")

        # Strengths and weaknesses
        if rec["strengths"]:
            print(f"\n[+] Strengths: {', '.join(rec['strengths'])}")
        if rec["weaknesses"]:
            print(f"[-] Weaknesses: {', '.join(rec['weaknesses'])}")

        # Explanation
        if show_explanations and rec.get("explanation"):
            print(f"\nExplanation:\n{rec['explanation']}")

        print("\n" + "="*80 + "\n")


def run_demo(
    persona="student",
    budget_max=1000,
    location_type="rent",
    destination="UCL",
    max_areas=5,
    generate_explanations=True
):
    """
    Run the full pipeline demo.

    Args:
        persona: "student", "parent", or "developer"
        budget_max: Maximum budget
        location_type: "rent" or "buy"
        destination: Destination for commute calculation
        max_areas: Number of areas to analyze
        generate_explanations: Whether to generate AI explanations
    """
    start_time = datetime.now()

    print("\n" + "="*80)
    print("  DOMUS HOUSING RECOMMENDATION PLATFORM - PIPELINE DEMO")
    print("="*80)

    # Display input
    print_user_input(persona, budget_max, location_type, destination)

    # Step 1: Get candidate areas
    print_header("STEP 1: FINDING CANDIDATE AREAS")
    print(f"Searching for affordable areas with max budget £{budget_max:,}...")

    candidate_areas = get_candidate_areas(
        budget_max=budget_max,
        location_type=location_type,
        affordability_threshold=20
    )

    print(f"\nFound {len(candidate_areas)} candidate areas")
    print(f"Analyzing top {min(max_areas, len(candidate_areas))} areas\n")

    # Limit to requested number
    areas_to_analyze = candidate_areas[:max_areas]

    # Step 2: Enrich areas
    print_header("STEP 2: ENRICHING DATA")
    print("Fetching property, commute, crime, schools, and amenities data...\n")

    enriched_areas = []
    for i, area in enumerate(areas_to_analyze, 1):
        print(f"[{i}/{len(areas_to_analyze)}] ", end="")
        enriched = enrich_area(area, destination)
        enriched_areas.append(enriched)

    print("\n[OK] Data enrichment complete")

    # Step 3: Score and rank
    print_header("STEP 3: SCORING & RANKING")
    print(f"Calculating persona-specific scores for {persona}...\n")

    recommendations = rank_areas(enriched_areas, persona, limit=len(areas_to_analyze))

    print(f"[OK] Scored and ranked {len(recommendations)} areas")

    # Step 4: Generate explanations
    if generate_explanations:
        print_header("STEP 4: GENERATING EXPLANATIONS")
        print("Using Claude AI to generate natural language explanations...\n")

        # Lazy import to avoid dependency issues if not using explanations
        try:
            from tools.generate_text_explanation import generate_explanation
        except ImportError:
            print("Warning: generate_text_explanation not available.")
            generate_explanation = lambda *args, **kwargs: "Explanation generation unavailable."

        for i, rec in enumerate(recommendations[:3], 1):
            print(f"[{i}/3] Generating explanation for {rec['area_name']}...")
            explanation = generate_explanation(rec, persona, format_type="medium")
            rec["explanation"] = explanation

        print("\n[OK] Explanations generated for top 3 areas")

    # Step 5: Display results
    display_recommendations(
        recommendations[:3],  # Show top 3
        persona,
        show_explanations=generate_explanations
    )

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_header("PIPELINE SUMMARY")
    print(f"Total execution time: {duration:.2f} seconds")
    print(f"Areas analyzed: {len(areas_to_analyze)}")
    print(f"Recommendations generated: {len(recommendations)}")
    print(f"Explanations generated: {3 if generate_explanations else 0}")
    print(f"\n[SUCCESS] Pipeline completed successfully!")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Domus Housing Recommendation Pipeline Demo")
    parser.add_argument("--persona", choices=["student", "parent", "developer"],
                        default="student", help="User persona")
    parser.add_argument("--budget", type=int, default=1000,
                        help="Maximum budget (£/month for rent, £ total for buy)")
    parser.add_argument("--type", choices=["rent", "buy"], default="rent",
                        help="Location type")
    parser.add_argument("--destination", default="UCL",
                        help="Destination for commute (e.g., UCL, Imperial, KCL)")
    parser.add_argument("--max-areas", type=int, default=5,
                        help="Maximum number of areas to analyze")
    parser.add_argument("--no-explanations", action="store_true",
                        help="Skip AI explanation generation")

    args = parser.parse_args()

    try:
        run_demo(
            persona=args.persona,
            budget_max=args.budget,
            location_type=args.type,
            destination=args.destination,
            max_areas=args.max_areas,
            generate_explanations=not args.no_explanations
        )
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
