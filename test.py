import os, json, sys, datetime, requests
from dotenv import load_dotenv
from google import genai
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# step 1: get query from user
def get_user_query():
    query = input("Enter your search prompt: ").strip()
    if not query:
        query = "latest trends in artificial intelligence"
    return query

# step 2: call news search API to get list of articles
def brave_search(query, num=5):
    url="https://api.search.brave.com/res/v1/news/search"
    key = os.getenv("BRAVE_API_KEY")
    params = {
        "q": query,
        "count": str(num),
        "country": "us",
        "search_lang": "en"
    }
    headers = {
        "X-Subscription-Token": key,
        "Accept": "application/json"
    }
    response = requests.get(url, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    results = response.json().get("results", [])
    return [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "source": (item.get("source") or {}).get("name"),
            "description": item.get("description"),
        }
        for item in results
    ]

# step 3: scrape each article to get text content
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
        
        if hit["text"].startswith("Error scraping: "):
            continue
        scraped.append(hit)
    return scraped

# step 4: call Gemini API to get embeddings for each article

# step 5: store embeddings in Qdrant vector database

# step 6: when user asks a question, get embedding for question

# step 7: query Qdrant to get relevant articles

# step 8: call Gemini to get answer based on articles

# step 9: return answer to user

# step 10: log all interactions to a file for later analysis

# step 11: handle errors and edge cases

# step 0: main function to run all steps
if __name__ == "__main__":
    load_dotenv()

    query = get_user_query()
    results = brave_search(query)
    scraped_results = scrape_articles(results)

    for i in scraped_results:
        print(i['title'])
        print(i['url'])
        print(i['text'][:500])  # print first 500 characters of the article text
        print()

    
    #for i, r in enumerate(results, start=1):
    #    print(f"{i}. {r['title']}\n{r['link']}\n{r['snippet']}\n")