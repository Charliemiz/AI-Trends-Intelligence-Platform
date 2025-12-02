from dotenv import find_dotenv, load_dotenv
import requests
import os, datetime
from perplexity import *
from backend.config import settings
import re

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

def perplexity_search_simple(query: str, count: int = 5):
    api_key = settings.PERPLEXITY_API_KEY
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Single call to get article with sources
    payload = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                        "content": f"Find the top {count} recent(published in the last 90 days) news articles about: {query}. "
                    "For each article, provide title, url, source, description, and published_at (ISO 8601 or null)."
            },
            {
                "role": "user",
                "content": (
                    f"Research and write a comprehensive, in-depth article about: {query}\n\n"
                    f"Your response must include:\n"
                    f"1. A compelling title (one line)\n"
                    f"2. A thorough, detailed article (800-1200 words) that deeply explores the topic\n\n"
                    f"CRITICAL RULES:\n"
                    f"- USE AND FIND ONLY SOURCES PUBLISHED IN THE LAST 90 DAYS\n"
                    f"- Use ONLY information from sources you find\n"
                    f"- Synthesize information from MULTIPLE sources effectively\n"
                    f"- Include specific details, quotes, statistics, and examples from the sources\n"
                    f"- Act as a NEUTRAL party\n"
                    f"- Do NOT use poetic or creative writing language\n"
                    f"- Write like a professional, comprehensive news article\n"
                    f"- Cover different angles and perspectives found in the sources\n\n"
                    f"TAGS REQUIREMENTS:\n"
                    f"- Include 5-10 relevant tags\n"
                    f"- Tags should include: companies mentioned, technologies discussed, key people, industries, concepts, or products\n"
                    f"- Use proper capitalization for company/product names (e.g., 'OpenAI', 'GPT-4', 'Microsoft')\n"
                    f"- Keep tags concise (1-3 words each)\n"
                    f"- Separate tags with commas\n\n"
                    f"Format your response as:\n"
                    f"TITLE: [your title here]\n\n"
                    f"ARTICLE:\n[your article here]"
                    f"TAGS: [tag1, tag2, tag3, ...]"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]

    # Extract using regex
    title_match = re.search(r'TITLE:\s*(.+)', content)
    article_match = re.search(r'ARTICLE:\s*(.+?)(?=TAGS:|$)', content, re.DOTALL)
    tags_match = re.search(r'TAGS:\s*(.+)', content)
    
    title = title_match.group(1).strip() if title_match else f"Article about {query}"
    article = article_match.group(1).strip() if article_match else content
    tags = [tag.strip() for tag in tags_match.group(1).split(",")] if tags_match else []

    # Fallback if parsing fails
    if not title:
        title = f"Article about {query}"
    if not article:
        article = content
    if not tags:
        tags = []

    # Extract sources from search_results
    sources = []
    search_results = data.get("search_results", [])
    
    for result in search_results:
        sources.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "source": result.get("url", "").split("/")[2] if result.get("url") else ""
        })

    return {
        "title": title,
        "article": article,
        "sources": sources,
        "query": query,
        "tags": tags,
        "created_at": datetime.datetime.now().isoformat()
    }


def perplexity_search_trends(sector: str, tags: list, count: int = 3):
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Create query with sector and tags
    tags_str = ", ".join(tags)  
    query = f"What are the top {count} most trending and newsworthy topics in {sector}?"

    payload = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a trend analyst specializing in {sector}. "
                    f"Find the most current, trending, and newsworthy topics related to: {tags_str} as they concern to AI."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Find the top {count} most trending topics in {sector} right now MUST RELATE TO AI.\n\n"
                    f"Focus on topics related to: {tags_str}\n\n"
                    f"CRITICAL RULES:\n"
                    f"- Topics must be CURRENT and TRENDING (last 30 days)\n"
                    f"- Topics must be SPECIFIC (not generic)\n"
                    f"- Topics must be NEWSWORTHY (actual events, announcements, developments)\n"
                    f"- Topics must be about or in somewhat related to AI\n"
                    f"- Development or news regarding AI in {count}\n"
                    f"- Topics must be be the same\n"
                    f"- Topics must 3 distinct topics\n"
                    f"- List ONLY the topic titles, one per line\n"
                    f"- No descriptions, no explanations, no numbering\n"
                    f"- Each topic should be 5-15 words\n\n"
                    f"Format your response as:\n"
                    f"[Topic 1]\n"
                    f"[Topic 2]\n"
                    f"[Topic 3]"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Parse topics from response
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    
    trending_topics = []
    for line in lines[:count * 2]:  # Look at twice as many lines to be safe
        # Remove common prefixes (1., •, -, *, etc.)
        cleaned = line.lstrip('0123456789.-•*# \t')
        
        # Remove "Topic:" or similar prefixes
        if ':' in cleaned:
            cleaned = cleaned.split(':', 1)[1].strip()
        
        # Must be substantial (not just a word)
        if cleaned and len(cleaned) > 15 and len(cleaned) < 200:
            trending_topics.append(cleaned)
        
        if len(trending_topics) >= count:
            break
    
    # Return empty list if not enough valid topics found
    if len(trending_topics) < 2:
        print(f"⚠️  Only found {len(trending_topics)} AI-related topics for {sector}, returning empty list")
        return []
    
    return trending_topics[:count]

def perplexity_find_articles(query: str, count: int = 5, credible_sources=None):
    from backend.services.source_services import extract_domain
    
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": f"Find the top {count} most relevant and recent articles about: {query}"
            },
            {
                "role": "user",
                "content": (
                    f"Find {count} recent, high-quality articles about: {query}\n\n"
                    f"CRITICAL RULES:\n"
                    f"- Articles must be RECENT (within last 3 months)\n"
                    f"- Articles must be from CREDIBLE sources\n"
                    f"- Find NO MORE THAN {count} articles\n"
                    f"- Return ONLY article titles and URLs\n"
                    f"- List one per line in format: Title | URL\n"
                    f"- No descriptions, no explanations\n"
                    f"- Exactly {count} articles\n\n"
                    f"Example format:\n"
                    f"https://example.com/article1, https://example.com/article2, https://example.com/article3"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    # Extract articles from search_results
    articles = []
    search_results = data.get("search_results", [])
    
    #temporary prints
    print(f"\n{'='*80}")
    print(f"{query[:60]}...")
    print(f"  Requested: {count} articles")
    print(f"  search_results returned: {len(search_results)} results")
    
    for result in search_results[:count]:
        url = result.get("url", "")
        domain = extract_domain(url) if url else ""
        is_trusted = domain in credible_sources if credible_sources else False
        
        articles.append({
            "title": result.get("title", ""),
            "url": url,
            "domain": domain,
            "trusted": is_trusted
        })
    
    print(f"  Articles from search_results: {len(articles)}")
    
    # Fallback: parse from content if search_results is empty
    if not articles:
        print(f"  search_results was empty, trying content parsing...")
        content = data["choices"][0]["message"]["content"]
        print(f"  Content length: {len(content)} chars")
        
        # Split by commas to get individual URLs
        urls = [url.strip() for url in content.split(",")]
        
        for url in urls[:count]:
            url = url.strip()
            # Clean up any line breaks or extra characters
            url = url.split()[0] if url else ""
            
            if url.startswith("http"):
                domain = extract_domain(url)
                is_trusted = domain in credible_sources if credible_sources else False               
                articles.append({
                    "title": "",  
                    "url": url,
                    "domain": domain,
                    "trusted": is_trusted
                })
            
            if len(articles) >= count:
                break
        
        print(f"  Articles from content parsing: {len(articles)}")
    
    # Summary of trusted vs uncertain
    trusted_count = sum(1 for a in articles if a.get("trusted", False))
    print(f"  Trusted sources: {trusted_count}/{len(articles)}")
    print(f"  TOTAL articles returned: {len(articles)}")
    print('='*80 + "\n")
    
    return articles[:count]

def perplexity_summarize(query: str, articles: list):
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Step 1: Fetch full content from each article URL using sonar-pro
    print(f"Fetching content from {len(articles)} articles...")
    articles_with_content = []
    
    for i, article in enumerate(articles):
        url = article.get("url", "")
        if not url:
            continue
            
        fetch_payload = {
            "model": "sonar-pro",
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": f"Read and extract the full text content from this article: {url}\n\nProvide the complete article text with all key information, statistics, quotes, and details."
                }
            ]
        }
        
        try:
            r_fetch = requests.post(PERPLEXITY_ENDPOINT, json=fetch_payload, headers=headers, timeout=45)
            r_fetch.raise_for_status()
            fetch_data = r_fetch.json()
            
            full_content = fetch_data["choices"][0]["message"]["content"]
            articles_with_content.append({
                "url": url,
                "title": article.get("title", ""),
                "content": full_content,
                "index": i + 1
            })
            print(f"  ✓ Fetched content from article {i+1}/{len(articles)}")
        except Exception as e:
            print(f"  ✗ Failed to fetch article {i+1}: {e}")
            # Add with empty content so we can still track it
            articles_with_content.append({
                "url": url,
                "title": article.get("title", ""),
                "content": "",
                "index": i + 1
            })
    
    if not articles_with_content:
        raise RuntimeError("Failed to fetch any article content")
    
    # Step 2: Prepare the context with all fetched articles
    articles_sections = []
    for article in articles_with_content:
        if article['content']:
            articles_sections.append(
                f"SOURCE [{article['index']}]:\n"
                f"Title: {article['title']}\n"
                f"URL: {article['url']}\n\n"
                f"Content:\n{article['content']}"
            )
    
    articles_text = "\n\n" + "="*80 + "\n\n"
    articles_text += ("\n\n" + "="*80 + "\n\n").join(articles_sections)
    
    # Check if content is too long
    max_chars = 100000  # Conservative limit
    if len(articles_text) > max_chars:
        print(f"  ⚠ Content too long ({len(articles_text)} chars), truncating...")
        articles_text = articles_text[:max_chars] + "\n\n[Content truncated due to length]"
    
    # Step 3: Use sonar model with explicit instructions to NOT search
    
    payload = {
        "model": "sonar",  
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a professional research journalist. "
                    f"You have been provided with the complete content from {len(articles_with_content)} specific articles below. "
                    f"You must write ONLY using information from these provided articles. "
                    f"Do NOT search for additional sources. Do NOT add any external knowledge."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Write a comprehensive article about: {query}\n\n"
                    
                    f"CRITICAL RULES:\n"
                    f"- Use ONLY information from the articles provided below\n"
                    f"- Each article is marked with [SOURCE X] - cite using [X]\n"
                    f"- After EVERY factual claim, immediately cite the source number in brackets\n"
                    f"- Format: 'The market grew to $2.79 billion[1]' NOT 'The market grew to $2.79 billion. [1]'\n"
                    f"- NEVER bundle citations like [1][2][3] unless sources say the EXACT same thing\n"
                    f"- Do NOT add information not in the provided articles\n"
                    f"- Do NOT use your general knowledge\n\n"
                    f"- Synthesize information from MULTIPLE sources effectively\n"
                    f"- Include specific details, quotes, statistics, and examples from the sources\n"
                    f"- Act as a NEUTRAL party\n"
                    f"- Do NOT use poetic or creative writing language\n"
                    f"- Write like a professional, comprehensive news article\n"
                    f"- Cover different angles and perspectives found in the sources\n\n"
                    
                    f"STRUCTURE:\n"
                    f"- Write 800-1200 words\n"
                    f"- Use 2-4 clear section headers\n"
                    f"- Maintain neutral, journalistic tone\n\n"
                    
                    f"TAGS REQUIREMENTS:\n"
                    f"- Include 5-10 relevant tags\n"
                    f"- Tags should include: companies mentioned, technologies discussed, key people, industries, concepts, or products\n"
                    f"- Use proper capitalization for company/product names (e.g., 'OpenAI', 'GPT-4', 'Microsoft')\n"
                    f"- Keep tags concise (1-3 words each)\n"
                    f"- Separate tags with commas\n\n"

                    f"FORMAT:\n"
                    f"[Title]\n\n"
                    f"[Article with citations]\n\n"
                    f"TAGS: [tag1, tag2, tag3, ...]\n\n"
                    
                    f"ARTICLES:\n"
                    f"{articles_text}"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=90)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Parse title, article, and tags from response
    tags = []
    
    # Split content to extract tags
    if "TAGS:" in content:
        main_content, tags_part = content.split("TAGS:", 1)
        tags = [tag.strip() for tag in tags_part.split(",") if tag.strip()]
    else:
        main_content = content
    
    lines = main_content.split("\n")  
    title = ""                         
    article_text = ""

    for i, line in enumerate(lines): 
        article_text = ""
    
    for i, line in enumerate(lines):
        if line.startswith("##"):
            title = line.replace("##", "").strip()
        elif line.startswith("ARTICLE:"):
            article_text = "\n".join(lines[i+1:]).strip()
            break
    
    # If no ## header found, look for content after first line
    if not title and lines:
        title = lines[0].strip()
        article_text = "\n".join(lines[1:]).strip()
    
    # Fallback if parsing fails
    if not title:
        title = f"Article about {query}"
    if not article_text:
        article_text = main_content

    # Return the original articles as sources
    sources = []
    for article in articles:
        sources.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("url", "").split("/")[2] if article.get("url") else ""
        })

    return {
        "title": title,
        "article": article_text,
        "sources": sources,
        "tags": tags,
        "query": query,
        "created_at": datetime.datetime.now().isoformat()
    }