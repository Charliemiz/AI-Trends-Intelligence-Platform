from dotenv import find_dotenv, load_dotenv
import requests
import os, json, sys, datetime
from perplexity import *

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

def perplexity_search_rest(query: str, count: int = 5):

    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    #Get sources from Perplexity search
    payload_search = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": f"Find the top {count} recent news articles about: {query}. "
                    "For each article, provide title, url, source, description, and published_at (ISO 8601 or null)."
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload_search, headers=headers, timeout=45)
    r.raise_for_status()
    data = r.json()

    # Extract sources from search_results
    search_results = data.get("search_results", [])
    sources = []
    
    for result in search_results[:count]:
        sources.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "source": result.get("url", "").split("/")[2] if result.get("url") else "",
            "description": result.get("snippet", ""),
            "published_at": result.get("date", None)
        })

    #Fetch full content from each source URL using web_fetch
    print("Fetching full content from sources...")
    for i, source in enumerate(sources):
        payload_fetch = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "user",
                    "content": f"Read and extract the main content from this article: {source['url']}\n\nProvide a detailed summary of the article's key points and findings."
                }
            ]
        }
        
        try:
            r_fetch = requests.post(PERPLEXITY_ENDPOINT, json=payload_fetch, headers=headers, timeout=45)
            r_fetch.raise_for_status()
            fetch_data = r_fetch.json()
            full_content = fetch_data["choices"][0]["message"]["content"]
            sources[i]["full_content"] = full_content
            print(f"  Fetched content for source {i+1}")
        except Exception as e:
            print(f"  Failed to fetch content for source {i+1}: {e}")
            sources[i]["full_content"] = source["description"]


    #Generate individual summary for each source
    for i, source in enumerate(sources):
        payload_summary = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "user",
                    "content": f"Summarize this article in 2-3 sentences:\n\n{source['full_content']}"
                }
            ]
        }
        
        try:
            r_sum = requests.post(PERPLEXITY_ENDPOINT, json=payload_summary, headers=headers, timeout=30)
            r_sum.raise_for_status()
            sum_data = r_sum.json()
            sources[i]["summary"] = sum_data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Warning: Failed to generate summary for source {i+1}: {e}")
            sources[i]["summary"] = source["description"]

    #Generate big summary and title from all sources
    sources_text = "\n\n==========\n\n".join([
        f"SOURCE {i+1}:\nTitle: {s['title']}\nURL: {s['url']}\nPublished: {s['published_at']}\n\nContent:\n{s['full_content']}"
        for i, s in enumerate(sources)
    ])

    payload_article = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a journalist who writes comprehensive articles by synthesizing information from multiple sources. You ONLY use information explicitly provided in the sources. You NEVER add information from your general knowledge or training data."
            },
            {
                "role": "user",
                "content": (
                    f"Using ONLY the information from the sources below, write:\n"
                    f"1. A compelling title (one line)\n"
                    f"2. A comprehensive article (400-600 words) that synthesizes the information from these sources\n\n"
                    f"CRITICAL RULES:\n"
                    f"- Use ONLY information explicitly stated in the sources below\n"
                    f"- ACT as a NUETRAL party while creating summary\n"
                    f"- Do NOT use poetic language or language used for creative writing, this should read like a profesional summary\n"
                    f"- Do NOT add any information from your general knowledge\n"
                    f"- Do NOT mention topics not covered in these specific sources\n"
                    f"- If the sources don't cover something, don't write about it\n\n"
                    f"SOURCES:\n\n{sources_text}\n\n"
                    f"Format your response as:\n"
                    f"TITLE: [your title here]\n\n"
                    f"ARTICLE:\n[your article here]"
                )
            }
        ]
    }

    r2 = requests.post(PERPLEXITY_ENDPOINT, json=payload_article, headers=headers, timeout=60)
    r2.raise_for_status()
    data2 = r2.json()

    content = data2["choices"][0]["message"]["content"]
    
    #Parse title and article from response
    lines = content.split("\n")
    title = ""
    article = ""
    
    for i, line in enumerate(lines):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("ARTICLE:"):
            article = "\n".join(lines[i+1:]).strip()
            break
    
    #Fallback if parsing fails
    if not title:
        title = f"Article about {query}"
    if not article:
        article = content

    for source in sources:
        if "full_content" in source:
            del source["full_content"]

    return {
        "title": title,
        "big_summary": article,
        "sources": sources,
        "query": query,
        "created_at": datetime.datetime.utcnow().isoformat()
    }