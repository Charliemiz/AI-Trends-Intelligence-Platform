from dotenv import find_dotenv, load_dotenv
import requests
import os, json, sys, datetime
from perplexity import Perplexity

PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"

# New function using the official Perplexity SDK
# We may need to make a new api key for this
def perplexity_search(query: str, count: int = 5):
    """Call Perplexity API to search and return results with sources."""
    client = Perplexity()
    
    search = client.search.create(
        query="latest AI developments 2024",
        max_results=5,
        max_tokens_per_page=1024
    )

    return search.results

def perplexity_search_rest(query: str, count: int = 5):
    """Simple Perplexity REST search that returns parsed JSON if valid, else empty list."""
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY. Put it in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Find the top {count} recent news articles about: {query}. "
                    "For each article, provide title, url, source, description, and published_at (ISO 8601 or null)."
                )
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "source": {"type": "string"},
                                    "description": {"type": "string"},
                                    "published_at": {"type": ["string", "null"]}
                                },
                                "required": ["title", "url", "source", "description", "published_at"]
                            }
                        }
                    },
                    "required": ["results"]
                }
            }
        },
        "max_tokens": 1200
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=45)
    r.raise_for_status()
    data = r.json()

    raw = data["choices"][0]["message"]["content"]
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"results": []}

    return parsed

def perplexity_summarize(context: str) -> str:
    """Call Perplexity API to summarize the given text."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY. Put it in .env")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": f"Summarize this in 3 bullets:\n\n{context}"
            }
        ]
    }

    resp = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    
    data = resp.json()
    summary = data['choices'][0]['message']['content']
    
    return summary