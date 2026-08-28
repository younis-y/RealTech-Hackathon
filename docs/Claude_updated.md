CLAUDE.md

Project Context

We are building an explainable, multi‑persona location and housing recommendation platform, powered primarily by ScanSan’s property/area intelligence, that returns ranked recommendations with transparent factor breakdowns and auto‑generated 30–60 second explainer videos for each top option.



Tech Stack

Framework: Next.js (App Router) for the web app, API routes for backend endpoints.



Language: TypeScript for frontend and backend, Python optional for data prep/notebooks.



Database: PostgreSQL (e.g. Supabase) for users, saved searches, feedback, cached API results.



Styling: Tailwind CSS + simple component library (e.g. Headless UI / Radix) for speed.



Hosting: Vercel (frontend) + managed Postgres (Supabase/RDS) or a single platform if preferred.



External AI services:



ScanSan API as primary source of property/area intelligence.



Perplexity + Claude APIs for generating faithful natural‑language explanations.



Veo / Sora / LTX / Nano video APIs for short explainer videos.



External data/APIs (enrichment and visuals):



TfL Unified API for London commute times and transport context.



Google Maps (Maps, Places, Directions) and OpenStreetMap Overpass for maps and amenities.



ONS Open Geography for UK boundaries and area‑level stats.



data.police.uk for UK crime rates.



Schools in England + Ofsted APIs for nearby schools and ratings.



Optional: Zillow / FRED / US Census / HUD if you show a US demo as well.



Problem Statement

Non‑technical users making housing and schooling decisions are overwhelmed by fragmented, technical and opaque data. Existing portals provide long lists of properties and dense tables but do not explain why one location suits a specific person better than another. Students, parents and small developers must manually balance budget, commute, safety, schools, amenities and long‑term prospects, often without understanding the trade‑offs or the underlying risks.



At the same time, powerful property intelligence APIs like ScanSan aggregate rich signals about affordability, risk and investment quality, but their scores are not directly exposed in human‑friendly, persona‑specific narratives. There is a gap between these sophisticated predictions and the way people actually decide — quickly, visually, and often on mobile, where short, shareable formats like video are preferred.



The project aims to close this gap by putting ScanSan’s predictions at the core and wrapping them with an explainable scoring layer, intuitive visualisations, and short auto‑generated videos that clearly communicate why a particular area or property is a good match for a given persona.



High‑Level Scope

Build a web app where three personas (student, parent, developer/investor) can:



Fill out a short checklist of priorities and constraints.



Receive a ranked list of areas/properties sourced from ScanSan and enriched by other APIs.



See transparent factor breakdowns and trade‑offs for each recommendation.



Optionally generate and watch a 30–60 second explainer video per top option.



Use ScanSan as the primary prediction/intelligence engine, with:



Area/property scores (affordability, risk, investment quality, etc.).



Our layer adding persona‑specific weighting and explanation.



Use external APIs (TfL, ONS, police, schools/Ofsted, OSM/Google Maps) to:



Compute commute times and transport accessibility.



Attach safety, school quality, and amenity density to each ScanSan area/property.



Feed these as explicit, auditable features to the explanation engine and UI.



Use LLMs (Perplexity/Claude) to:



Convert structured factor scores into concise, persona‑specific natural‑language explanations, with strict constraints to avoid hallucinating beyond numeric inputs.



Use video generation APIs (Veo/Sora/LTX/Nano) to:



Turn the same explanation and feature set into short “property/area story” videos that highlight maps, icons, key stats and a simple narrative.



Detailed Website Specifications

1\. User personas and flows

Personas:



Student (likely renting; cares about rent, commute to campus, safety, nightlife/amenities).



Parent (buying or renting; cares about schools, safety, family amenities, budget, commute).



Developer/investor (buying; cares about yields, price trends, demand, infrastructure, risk).



Core flows (MVP):



Landing → persona selection.



Persona checklist (5–8 questions).



Results page: ranked recommendations with explanations.



Detail page for a selected area/property, including:



Factor breakdown card.



Map with key amenities and schools.



“Generate explainer video” button and embedded player.



Optional: save/share a recommendation and feedback (“helpful/not helpful”).



2\. Checklist and preferences

Dynamic form per persona, e.g.:



Student: budget range, max commute time, preferred transport modes, safety importance, nightlife/amenities importance.



Parent: purchase vs rent, budget, min school rating, safety priority, green space, max commute.



Developer: investment budget, focus (yield vs growth), risk tolerance, infrastructure importance.



Each question maps directly to weights or constraints on:



ScanSan‑provided scores (affordability, risk, demand).



Enrichment scores (commute time, crime, school quality, amenity density).



3\. Scoring and ranking engine

Input:



Candidate areas/properties from ScanSan (by area code or property IDs).



For each candidate: core ScanSan scores + enrichment features from other APIs.



Persona‑specific scoring:



Weighted sum or interpretable model where each factor has:



Weight (importance).



Normalised

