# Video Explainer Generation Directive

## Goal
Generate 30-60 second explainer videos for top property/area recommendations using video AI APIs (Veo/Sora/LTX/Nano), combining map visualizations, key stats, and persona-specific narratives.

## Inputs
- **area_data**: Full recommendation object from scoring engine
- **persona**: student | parent | developer
- **user_preferences**: To personalize narrative
- **map_image**: Static map image of the area with key amenities marked
- **factor_breakdown**: Visual elements showing scores
- **script**: Natural language explanation from LLM (Claude/Perplexity)

## Execution Tool
Use `execution/generate_video.py`

## Process

### 1. Script Generation (pre-video)
Before calling execution script, use Claude API to generate video script:
- Input: factor scores, strengths, weaknesses, persona
- Output: 150-200 word script in persona voice
- Constraints: Only reference data points provided; no hallucinations

Example script (student persona):
```
"Let's look at Shoreditch, East London. This area scores 87 out of 100 for student life.

Here's why: rent averages £950 per month, well within your budget. The Overground gets you to campus in just 22 minutes.

Safety is solid at 78 out of 100, with crime rates improving over the past year.

What really shines is nightlife and amenities, scoring 90 out of 100. You'll find 12 pubs, 8 cafes, and 3 supermarkets within a 10-minute walk.

The trade-off? It's slightly pricier than East Ham, but you're paying for convenience and vibrant social life.

For students who want easy commutes and great weekend options, Shoreditch is a top choice."
```

### 2. Visual Asset Preparation
- **Map**: Static Google Maps image with markers (home, campus, key amenities)
- **Score cards**: PNG overlays showing factor breakdown
- **Icons**: Transport, safety, money, school, building icons
- Store assets in `.tmp/video_assets_{area_code}/`

### 3. Video Generation API Selection
Try APIs in order of availability:
1. **Google Veo** (preferred for quality)
2. **OpenAI Sora** (if Veo unavailable)
3. **LTX Studio** (fallback)
4. **Nano** (fast, lower quality backup)

### 4. Video Generation Call
- Input: script, visual assets, style guide
- Duration: 30-60 seconds
- Style: "Clean, professional explainer video with map overlays and animated text"
- Aspect ratio: 16:9 (web) or 9:16 (mobile)
- Output format: MP4

### 5. Post-processing
- Add branded intro/outro (optional, 2 seconds each)
- Add subtitles/captions (accessibility requirement)
- Compress for web delivery
- Upload to CDN or store in cloud storage
- Return video URL

## Outputs
JSON structure:
```json
{
  "area_code": "E1 6AN",
  "video_url": "https://cdn.example.com/videos/E1_6AN_student_v1.mp4",
  "thumbnail_url": "https://cdn.example.com/thumbnails/E1_6AN.jpg",
  "duration_seconds": 45,
  "script": "Let's look at Shoreditch...",
  "generation_api": "veo",
  "generation_time_seconds": 127,
  "cost_usd": 0.15,
  "has_subtitles": true,
  "timestamp": "ISO-8601"
}
```

## Edge Cases & Learnings
- **API costs**: Video generation is expensive
  - Veo: ~$0.10-0.30 per video
  - Sora: ~$0.20-0.50 per video
  - Only generate on user request, not automatically
  - Cache generated videos for 30 days
- **Generation time**: 30-180 seconds depending on API
  - Show "Generating your video..." with progress indicator
  - Run generation asynchronously; notify when ready
- **API failures**: Have fallback chain; if all fail, offer static slideshow
- **Script quality**: Critical for video quality
  - Use Claude for script generation (better than GPT for factual adherence)
  - Pass structured data, not free-form text, to prevent hallucinations
- **Visual consistency**: Maintain brand colors, fonts, style across all videos
- **Accessibility**: Always include subtitles (legal requirement in many jurisdictions)
- **Mobile optimization**: Provide 9:16 vertical version for mobile users
- **Rate limits**:
  - Veo: 10 videos/day in beta
  - Sora: 50 videos/month on paid tier
  - Implement queueing system if demand high

## Self-Annealing Notes
- 2024-01-31: Initial directive created
- [Future updates: actual API performance, cost optimization, user engagement metrics]
