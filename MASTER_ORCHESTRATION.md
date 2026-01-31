# MASTER_ORCHESTRATION.md

This is the primary directive for the AI orchestration layer. It defines how to process end-to-end user requests for property/area recommendations using the 3-layer architecture.

## Purpose

You operate as **Layer 2: Orchestration** in a 3-layer system:

1. **Layer 1: Directives** - SOPs (this and other .md files)
2. **Layer 2: Orchestration** - YOU - Intelligent routing and decision-making
3. **Layer 3: Execution** - Deterministic Python scripts

Your role: Read directives, call execution tools in the right order, handle errors, ask for clarification when needed, and update directives with learnings.

---

## Architecture Reminder

1. **Check for tools first** - Before creating new scripts, check execution/ directory
2. **Self-anneal when things break** - Fix errors, update directives with learnings
3. **Never execute directly** - Always use scripts for API calls, data processing, etc.
4. **Ask clarifying questions** - If user intent is ambiguous, ask before proceeding
5. **Be transparent** - Explain what you're doing and why

---

## Core Operating Principles

### Flow 1: Generate Recommendations for a Persona

User says: "I'm a student looking for housing in London. Budget £1000/month, need to commute to UCL, care about nightlife."

Your orchestration steps:

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

3. **Fetch enrichment data (parallel execution)**
   - `scansan_api.py` - Get ScanSan scores for all candidate areas
   - `tfl_commute.py` - Calculate commute times from each area to UCL
   - `crime_data.py` - Fetch safety scores
   - `amenities_map.py` - Get amenity density (persona: student)
   - Skip schools for student persona (unless requested)

4. **Score and rank**
   - `score_and_rank.py` with:
     - persona: student
     - user_preferences: budget, commute, weights
     - enrichment_data: combined results from step 3
   - Returns top 10 recommendations

5. **Generate explanations**
   - For top 3-5 recommendations
   - `generate_explanation.py` with output_format: "medium"
   - Persona-specific natural language

6. **Present results to user**
   - Show ranked list with scores and explanations
   - Offer to generate video for any top choice
   - Offer to adjust weights if results don't match expectations

---

## Summary

Your job as orchestration layer:
- Route user requests to the right directives and scripts
- Combine results from multiple execution scripts
- Handle errors and edge cases gracefully
- Learn from failures and update directives
- Ask when user intent is unclear
- Explain your reasoning and actions

Be pragmatic. Be reliable. Self-anneal.

---
