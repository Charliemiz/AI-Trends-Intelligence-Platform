from dotenv import find_dotenv, load_dotenv
import requests
import os, datetime
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
    load_dotenv(find_dotenv())
    api_key = os.getenv("PERPLEXITY_API_KEY")
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
                    f"Format your response as:\n"
                    f"TITLE: [your title here]\n\n"
                    f"ARTICLE:\n[your article here]"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Parse title and article from response
    lines = content.split("\n")
    title = ""
    article = ""
    
    for i, line in enumerate(lines):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("ARTICLE:"):
            article = "\n".join(lines[i+1:]).strip()
            break
    
    # Fallback if parsing fails
    if not title:
        title = f"Article about {query}"
    if not article:
        article = content

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
    
    # Fallback if we didn't find enough topics
    if len(trending_topics) < count:
        print(f"⚠️  Only found {len(trending_topics)} topics, using fallback")
        while len(trending_topics) < count:
            trending_topics.append(f"Recent developments in {sector} - {tags[len(trending_topics) % len(tags)]}")
    
    return trending_topics[:count]

def perplexity_find_articles(query: str, count: int = 5):
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
                    f"Article Title Here | https://example.com/article\n"
                    f"Another Article | https://example.com/another"
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
    
    for result in search_results[:count]:
        articles.append({
            "title": result.get("title", ""),
            "url": result.get("url", "")
        })
    
    # Fallback: parse from content if search_results is empty
    if not articles:
        content = data["choices"][0]["message"]["content"]
        lines = content.split("\n")
        
        for line in lines[:count * 2]: 
            if "|" in line and "http" in line:
                parts = line.split("|", 1)
                if len(parts) == 2:
                    title = parts[0].strip().lstrip("0123456789.-•* ")
                    url = parts[1].strip()
                    
                    if title and url.startswith("http"):
                        articles.append({
                            "title": title,
                            "url": url
                        })
            
            if len(articles) >= count:
                break
    
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

    # Extract URLs from articles and format for the prompt
    article_urls = [article["url"] for article in articles]
    urls_list = "\n".join([f"- {url}" for url in article_urls])

    payload = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You must read and use ONLY these specific URLs as sources:\n\n{urls_list}\n\n"
                    f"Do NOT search for other sources. Use ONLY the information from these {len(article_urls)} URLs."
                )
            },
            {
                "role": "user",
                "content": (
                    f"You are a professional research journalist writing an evidence-based article.\n\n"
                    
                    f"TASK: Write a comprehensive article synthesizing information from ALL {len(article_urls)} URLs about: {query}\n\n"
                    
                    f"MANDATORY SOURCE USAGE:\n"
                    f"- You MUST use information from ALL {len(article_urls)} sources provided\n"
                    f"- Each source must be cited at least once in the article\n"
                    f"- If a source seems less relevant, find at least one piece of information from it to include\n\n"
                    
                    f"CRITICAL CITATION RULES:\n"
                    f"- After EVERY factual claim, statistic, or statement, immediately cite the source number in brackets\n"
                    f"- Format: 'The market grew to $2.79 billion[1]' NOT 'The market grew to $2.79 billion. [1]'\n"
                    f"- NEVER bundle citations like [1][2][3] unless both sources say the EXACT same thing\n"
                    f"- If sources say different things, separate them: 'Study A found X[1], while study B found Y[2]'\n"
                    f"- If sources say similar things, be specific: 'Both studies found X, with source [1] emphasizing Y and source [2] noting Z'\n"
                    f"- Each sentence may have MULTIPLE separate citations if drawing from multiple sources\n"
                    f"- Example: 'Sora can generate 60-second videos[1], while Runway offers 4K upscaling[2] and lower costs[3]'\n\n"
                    
                    f"FORBIDDEN - DO NOT DO THESE THINGS:\n"
                    f"- Writing ANY sentence without a citation if it contains factual claims\n"
                    f"- Bundling citations [1][2][3] without explaining what each source contributes\n"
                    f"- Starting paragraphs with uncited context-setting or framing\n"
                    f"- Adding transitional sentences like 'Research shows...' or 'The impact is complex...' without citations\n"
                    f"- Using interpretive language like 'This challenges...', 'This reveals...', 'This underscores...' unless sources explicitly use those words\n"
                    f"- Making claims about what sources are doing ('challenging narratives', 'revealing insights') unless sources say that\n"
                    f"- Adding ANY information, context, or framing not explicitly in the provided sources\n\n"
                    
                    f"CONTENT RESTRICTIONS:\n"
                    f"- Use ONLY information explicitly stated in the {len(article_urls)} provided URLs\n"
                    f"- Do NOT add external knowledge, assumptions, or general context not in the sources\n"
                    f"- Do NOT editorialize or add your own interpretations\n"
                    f"- Every factual statement must be traceable to a specific source\n"
                    f"- If you need to write a transition, either cite it or make it purely structural (not factual)\n"
                    f"- Structural transitions OK: 'The next section examines...', 'Three findings emerged...'\n"
                    f"- Factual transitions MUST BE CITED: 'The environmental impact varies by region[2]'\n\n"
                    
                    f"WHAT TO INCLUDE:\n"
                    f"- Direct quotes from sources (use quotation marks + citation)\n"
                    f"- Specific statistics, numbers, and data points with citations\n"
                    f"- Concrete examples, case studies, or real-world applications mentioned in sources\n"
                    f"- Named individuals, companies, or organizations mentioned\n"
                    f"- Dates, timeframes, and specific events\n"
                    f"- Technical details and methodologies if described in sources\n\n"
                    
                    f"STRUCTURE REQUIREMENTS:\n"
                    f"- Write 800-1200 words\n"
                    f"- Use clear section headers (2-4 sections)\n"
                    f"- Lead with the most important/recent information\n"
                    f"- Each paragraph should focus on one main idea\n"
                    f"- Maintain neutral, journalistic tone - report what sources say, don't interpret\n\n"
                    
                    f"OUTPUT FORMAT:\n"
                    f"[Create a specific, title that reflects the actual content, must be compeling]\n\n"
                    f"[Your article text with inline citations]\n\n"
                    
                    f"QUALITY CHECKS BEFORE SUBMITTING:\n"
                    f"1. Does every factual claim have a citation immediately after it?\n"
                    f"2. Did I avoid bundling citations [1][2][3] and instead specify what each source contributes?\n"
                    f"3. Did I use ALL {len(article_urls)} sources and cite each at least once?\n"
                    f"4. Are ALL transitions either cited or purely structural (not factual)?\n"
                    f"5. Did I avoid adding ANY interpretation, context, or framing not in sources?\n"
                    f"6. Did I include specific quotes, numbers, and examples from sources?\n"
                    f"7. Is the tone neutral - reporting what sources say, not what they 'reveal' or 'challenge'?\n"
                    f"8. Can every sentence be traced back to a specific source?\n\n"
                    
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Parse title and article from response
    lines = content.split("\n")
    title = ""
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
        article_text = content

    # Use the articles we passed in (not search_results from Perplexity)
    sources = []
    for src in articles:
        sources.append({
            "title": src.get("title", ""),
            "url": src.get("url", ""),
            "source": src.get("url", "").split("/")[2] if src.get("url") else ""
        })

    return {
        "title": title,
        "article": article_text,
        "sources": sources,
        "query": query,
        "created_at": datetime.datetime.now().isoformat()
    }