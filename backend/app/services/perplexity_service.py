import requests
from app.config import settings

def fetch_ai_articles(sector: str):
    """
    Fetch latest AI news and research summaries for a given sector.
    """
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
