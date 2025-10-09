import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def fetch_article_text(url: str) -> dict:
    headers = {"User-Agent": "ai-news-py/0.1"}
    request = requests.get(url, headers=headers, timeout=25)
    request.raise_for_status()
    html = request.text

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe"]):
        tag.decompose()

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    text = "\n".join([t for t in paragraphs if t])[:15000]  # keep request small
    domain = (urlparse(url).hostname or "").removeprefix("www.")
    return {"text": text, "domain": domain}

if __name__ == "__main__":
    test_url = "https://finance.yahoo.com/news/feds-rate-decision-looms-as-markets-hover-near-records-what-to-watch-this-week-121006200.html"
    result = fetch_article_text(test_url)
    print(result)