import os, json, sys, datetime
import requests
from dotenv import load_dotenv
from google import genai

NEWS_ENDPOINT = "https://api.search.brave.com/res/v1/news/search"
WEB_ENDPOINT  = "https://api.search.brave.com/res/v1/web/search"   

def brave_news(query: str, count: int = 5, country: str = "us", search_lang: str = "en"):
    """Call Brave News Search and return a list of simplified results."""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing BRAVE_API_KEY. Put it in .env")

    params = {
        "q": query,
        "count": str(count),
        "country": country,
        "search_lang": search_lang
    }
    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json"
    }
    r = requests.get(NEWS_ENDPOINT, params=params, headers=headers, timeout=20)

    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        print("Brave error:", r.status_code, r.text[:400], file=sys.stderr)
        raise e

    data = r.json()
    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "source": (item.get("source") or {}).get("name"),
            "description": item.get("description"),
        })
    return results

def main():
    load_dotenv() 

    q = input("Brave query (e.g., renewable energy policy OR grid interconnection rule): ").strip()
    if not q:
        q = "renewable energy policy"

    hits = brave_news(q, count=5, country="us", search_lang="en")

    if not hits:
        print("No results.")
        return

    print(f"\nTop {len(hits)} results for: {q}\n")
    # for i, h in enumerate(hits, 1):

    #     print(f"{i}. {h['title'] or '(no title)'}")
    #     print(f"   {h['url']}")
    #     print(f"   source: {h.get('source') or 'unknown'}")
    #     if h.get("description"):
    #         print(f"   desc: {h['description'][:140]}{'...' if len(h['description'])>140 else ''}")
    #     print()

    # with open("brave_results.json", "w", encoding="utf-8") as f:
    #     json.dump(out, f, ensure_ascii=False, indent=2)

    # This is really messy but will be changed later (URL's need to be fetched and cleaned first)
    # Nothings being fetched or cleaned right now, its just sending URL's to Gemini
    gemini_summarize("\n\n".join([f"{h['title']}\n{h['description']}\n{h['url']}" for h in hits]))

def gemini_summarize(context: str) -> str:
    """Call Gemini API to summarize the given text."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    resp = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Summarize this in 3 bullets: {context}" 
    )

    print(resp.text)

if __name__ == "__main__":
    main()
