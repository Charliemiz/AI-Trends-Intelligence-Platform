# backend/app/services/perplexity_service.py

from dotenv import find_dotenv, load_dotenv
import requests, os, json
from typing import List, Dict, Any, Optional

PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"

def _get_api_key() -> str:
    """Load API key from environment."""
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY. Put it in .env or Railway Secrets.")
    return api_key


def perplexity_search_rest(query: str, count: int = 5) -> Dict[str, Any]:
    """Query Perplexity API for recent articles related to a topic."""
    api_key = _get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
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
                ),
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
                                    "published_at": {"type": ["string", "null"]},
                                },
                                "required": ["title", "url", "source", "description", "published_at"],
                            },
                        }
                    },
                    "required": ["results"],
                }
            },
        },
        "max_tokens": 1200,
    }

    resp = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=45)
    resp.raise_for_status()

    try:
        raw = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(raw)
    except Exception:
        parsed = {"results": []}

    return parsed


def perplexity_summarize(context: str) -> str:
    """Summarize a text block in 3 concise bullets using Perplexity."""
    api_key = _get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": f"Summarize this in 3 bullets:\n\n{context}"}],
    }

    resp = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"]

def fetch_ai_news(query="latest AI developments", count=5):
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY")
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
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

    response = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=45)
    response.raise_for_status()

    data = response.json()
    raw = data["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(raw)

        print(parsed)
        return parsed.get("results", [])
    except:
        return []