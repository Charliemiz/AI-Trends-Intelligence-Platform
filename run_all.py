import os, json, sys, datetime, requests
from dotenv import load_dotenv
from google import genai
from bs4 import BeautifulSoup
from urllib.parse import urlparse


NEWS_ENDPOINT = "https://api.search.brave.com/res/v1/news/search"
WEB_ENDPOINT  = "https://api.search.brave.com/res/v1/web/search"   

def braveQuery(query: str, count: int = 5, country: str = "us", search_lang: str = "en"):
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

def scrape_articles(hits):
    scraped = []
    for hit in hits:
        url = hit.get("url")
        if not url:
            continue
        try:
            headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Referer": "https://www.google.com"
                    }
            request = requests.get(url, headers=headers, timeout=25)
            request.raise_for_status()
            html = request.text

            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe"]):
                tag.decompose()

            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            text = "\n".join([t for t in paragraphs if t])
            domain = (urlparse(url).hostname or "").removeprefix("www.")
            hit["text"] = text
            hit["domain"] = domain
        except Exception as e:
            hit["text"] = f"Error scraping: {e}"
            hit["domain"] = ""
        scraped.append(hit)
    return scraped

def geminiSummary(context: str) -> str:
    """Call Gemini API to summarize the given text."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    resp = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Summarize this in 3 bullets: {context}" 
    )

    return(resp.text)

def main():
    load_dotenv() 

    q = input("Brave query (e.g., renewable energy policy OR grid interconnection rule): ").strip()
    if not q:
        q = "renewable energy policy"

    rawHits = braveQuery(q, count=5, country="us", search_lang="en")

    if not rawHits:
        print("No results.")
        return
    
    scrapedHits = scrape_articles(rawHits)

    print(f"\nTop {len(scrapedHits)} results for: {q}\n")
    for i, h in enumerate(scrapedHits, start=1):
        print(f"Result {i}:")
        print(f"Title: {h['title']}")
        print(f"Source: {h['source']}")
        print(f"URL: {h['url']}")
        print(f"Domain: {h.get('domain','')}")

        text = h.get("text", "")
        if text.startswith("Error scraping:"):
            print(f"\n{text}")
        elif text:
            print(f'\n{geminiSummary(text)}')
        print("-" * 40)

    return

if __name__ == "__main__":
    main()
