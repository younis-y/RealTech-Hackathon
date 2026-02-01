import os
import json
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

def fetch_market_news(area_code: str, area_name: str) -> dict:
    """
    Fetch real-time market analysis from Perplexity Sonar.
    
    Args:
        area_code: London Area Code (e.g. E1)
        area_name: Full name (e.g. Whitechapel)
        
    Returns:
        Dict with keys: 'verdict', 'news_summary', 'growth_forecast', 'live_yield'
    """
    if not PERPLEXITY_API_KEY:
        return {"error": "No API Key"}

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Provide a concise real-time property market analysis for {area_name} ({area_code}) London for 2025.
    
    Return ONLY a raw JSON object (no markdown formatting) with these exact keys:
    - "verdict": A short punchy 2-3 word verdict (e.g. "Undervalued Gem", "Overpriced").
    - "yield": Estimated current rental yield percentage (number only).
    - "growth": Estimated 5-year capital growth percentage (number only).
    - "news": A one-sentence summary of the latest market news/sentiment.
    """

    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {"role": "system", "content": "You are a real-time property market analyst. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }

    try:
        response = requests.post(PERPLEXITY_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            
            # Clean up markdown if present
            clean_content = content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(clean_content)
            
    except Exception as e:
        print(f"[ERROR] Perplexity API failed: {e}")
        
    return {"error": "API Failure"}
