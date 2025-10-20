import requests
from app.config import settings

def fetch_ai_articles(sector: str):
    """
    Fetch latest AI news and research summaries for a given sector.
    """
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a search assistant. Provide recent news and information with sources."
            },
            {
                "role": "user",
                "content": f"Find the top recent news articles about: {sector}. For each result, provide: title, source, brief description, and URL if available."
            }
        ]
    }
    
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        json={"q": payload, "source": "news"},
        headers=headers
    )
    data = response.json()
    return [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("text"),
            "sector": sector,
        }
        for item in data.get("results", [])
    ]

# chatGPT given perplexity_service.py for reference
"""
import requests
from app.config import settings

def fetch_ai_articles(sector: str):
    
    # Fetch latest AI news and research summaries for a given sector.
    
    headers = {"Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}"}
    query = f"Latest AI developments in {sector} sector"
    response = requests.post(
        "https://api.perplexity.ai/search",
        json={"q": query, "source": "news"},
        headers=headers
    )
    data = response.json()
    return [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("text"),
            "sector": sector,
        }
        for item in data.get("results", [])
    ]
"""
