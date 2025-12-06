from backend.services.source_services import extract_domain, CREDIBLE_SOURCES, BLACKLISTED_SOURCES
from backend.config import settings
import re, requests, datetime

PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"

#Find trends
def perplexity_search_trends(sector: str | None, tags: list, count: int = 3):
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    # Create query with sector and tags
    tags_str = ", ".join(tags) 
    payload = {
        "model": "sonar",  # Changed from sonar-pro to avoid meta-commentary
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": f"You are a trend analyst. Find current trending AI topics in {sector}."
            },
            {
                "role": "user",
                "content": (
                    f"What are the top {count} trending AI topics in {sector} right now? "
                    f"Focus on: {tags_str}. "
                    f"Requirements: Current (last 30 days), specific, newsworthy, AI-related. "
                    f"List {count} topic titles only, one per line, 8-20 words each, no numbering or descriptions."
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    
    print(f"\n{'='*60}")
    print(f"Searching for trending topics in {sector}...")
    print(f"Raw response: {content[:200]}...")  # Debug
    
    # Parse topics from response
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    trending_topics = []

    for line in lines[:count * 3]: 
        # Remove common prefixes (1., •, -, *, etc.)
        cleaned = line.lstrip('0123456789.-•*# \t')
        
        # Remove "Topic:" or similar prefixes
        if ':' in cleaned:
            cleaned = cleaned.split(':', 1)[1].strip()
        
        # Remove quotes if present
        cleaned = cleaned.strip('"\'')

        # Less strict validation - just needs to be reasonable length
        if cleaned and 10 <= len(cleaned) <= 250:  
            # Make sure it's not meta-commentary
            if not any(skip in cleaned.lower() for skip in ['here are', 'trending topics', 'let me', 'i will', 'based on']):
                trending_topics.append(cleaned)
                print(f"  ✓ Found: {cleaned}")

        if len(trending_topics) >= count:
            break

    # Return empty list if not enough valid topics found
    if len(trending_topics) < 2:
        print(f"⚠️  Only found {len(trending_topics)} AI-related topics for {sector}, returning empty list")
        return []
    
    print(f"✓ Found {len(trending_topics)} valid topics")
    print('='*60 + "\n")
    
    return trending_topics[:count]

# Find articles
def perplexity_find_articles(query: str, count: int = 5):
   
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
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
        is_trusted = domain in CREDIBLE_SOURCES if CREDIBLE_SOURCES else False
        black_listed = domain in BLACKLISTED_SOURCES if BLACKLISTED_SOURCES else False
        
        articles.append({
            "title": result.get("title", ""),
            "url": url,
            "domain": domain,
            "trusted": is_trusted,
            "blacklisted": black_listed
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
                is_trusted = domain in CREDIBLE_SOURCES if CREDIBLE_SOURCES else False   
                black_listed = domain in BLACKLISTED_SOURCES if BLACKLISTED_SOURCES else False            
                articles.append({
                    "title": "",  
                    "url": url,
                    "domain": domain,
                    "trusted": is_trusted,
                    "blacklisted": black_listed
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

    # Writes a summary about our trends using source articles we recieved
def perplexity_summarize(query: str, trusted_articles: list, uncertain_articles: list | None = None):
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    # Combine articles but mark which are trusted
    all_articles = []
    
    for article in trusted_articles:
        all_articles.append({**article, "is_trusted": True})
    
    if uncertain_articles:
        for article in uncertain_articles:
            all_articles.append({**article, "is_trusted": False})
    
    print(f"Providing {len(all_articles)} URLs to Perplexity ({len(trusted_articles)} trusted, {len(uncertain_articles) if uncertain_articles else 0} uncertain)...")
    
    # Build URL list with trust markers
    trusted_urls = []
    uncertain_urls = []
    
    for article in all_articles:
        url = article.get("url", "")
        title = article.get("title", "")
        
        if article.get("is_trusted"):
            trusted_urls.append(f"- {title}: {url}")
        else:
            uncertain_urls.append(f"- {title}: {url}")
    
    # Build the URL context
    urls_text = ""
    
    if trusted_urls:
        urls_text += "TRUSTED SOURCES (prioritize these):\n"
        urls_text += "\n".join(trusted_urls)
    
    if uncertain_urls:
        urls_text += "\n\nUNCERTAIN SOURCES (use for additional context):\n"
        urls_text += "\n".join(uncertain_urls)
    
    # Let Perplexity search and fetch from these URLs
    payload = {
        "model": "sonar",  
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional research journalist writing comprehensive articles. "
                    "Write directly without explaining your process."
                )
            },
            {
                "role": "user",
                "content": (
                    f"{query}\n\n"
                    
                    f"Use information from these sources:\n\n"
                    f"{urls_text}\n\n"
                    
                    f"CRITICAL RULES:\n"
                    f"- Read and synthesize information from the URLs provided above\n"
                    f"- PRIORITIZE information from TRUSTED sources\n"
                    f"- Use UNCERTAIN sources only for additional context when TRUSTED sources are limited\n"
                    f"- When information conflicts, prefer TRUSTED sources\n"
                    f"- Include specific details, quotes, statistics from the sources\n"
                    f"- Act as a NEUTRAL party\n"
                    f"- Write like a professional, comprehensive news article\n\n"
                    
                    f"STRUCTURE:\n"
                    f"- Write 800-1200 words\n"
                    f"- Start with a properly-formatted (e.g., capitalization), no citations (e.g., '[3]'), compelling title\n"
                    f"- Use 2-4 clear section headers wrapped in double-asterisks (e.g., '**Conclusion**')\n"
                    f"- Maintain a neutral, clear, concise, journalistic tone, you're speaking to the layman\n"
                    f"- Cite sources naturally within the text. When using parenthetical citations, wrap the source number in brackets (e.g., '[3]')\n"
                    f"- Include newline and tab characters, if needed, wrapped in brackets (e.g., '[\\n]', '[\\t]')\n"
                    f"- Avoid using any additional text features (e.g., bullet lists). Stick to strictly text, headers, newlines, tabs, and citations\n\n"
                    
                    f"TAGS REQUIREMENTS:\n"
                    f"- Include 5-10 relevant tags\n"
                    f"- Tags should include: companies mentioned, technologies discussed, key people, industries, concepts, or products\n"
                    f"- Use proper capitalization for company/product names (e.g., 'OpenAI', 'GPT-4', 'Microsoft')\n"
                    f"- Do not lead or wrap tags with characters (e.g., '## AI', '[Technology]')\n"
                    f"- Keep tags concise (1-3 words each)\n"
                    f"- Separate tags with commas\n\n"

                    f"FORMAT:\n"
                    f"[Title]\n\n"
                    f"[Article]\n\n"
                    f"TAGS: [tag1, tag2, tag3, ...]"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=90)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Parse response
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
        if line.startswith("##"):
            title = line.replace("##", "").strip()
        elif line.startswith("ARTICLE:"):
            article_text = "\n".join(lines[i+1:]).strip()
            break
    
    if not title and lines:
        title = lines[0].strip()
        article_text = "\n".join(lines[1:]).strip()
    
    if not title:
        title = f"Article about {query}"
    if not article_text:
        article_text = main_content

    # Return sources (the URLs we provided)
    sources = []
    for article in all_articles:
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

    # Returns an impact score for our end article 
def perplexity_impact_score(article_title: str, article_content: str, sector: str | None):
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are an expert analyst evaluating the long-term impact and importance "
                    f"of AI developments in {sector}. You assess whether news represents "
                    f"transformational change or incremental updates."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Evaluate the IMPACT SCORE (0-10) for this article about AI in {sector}.\n\n"
                    f"SCORING SCALE:\n"
                    f"10/10 = Revolutionary change equivalent to industrial/agricultural revolution for {sector}\n"
                    f"Examples: First autonomous vehicles approved nationwide, AGI breakthrough, \n"
                    f"AI cures major disease, AI replaces entire job category\n"
                    f"9/10  = Transformational shift that will reshape the entire sector within 1-2 years\n"
                    f"8/10  = Major breakthrough that significantly changes industry practices\n"
                    f"7/10  = Important development with clear widespread adoption path\n"
                    f"6/10  = Significant progress that will affect many organizations\n"
                    f"5/10  = Notable advancement with medium-term implications\n"
                    f"4/10  = Interesting development with limited scope\n"
                    f"3/10  = Incremental improvement to existing technology\n"
                    f"2/10  = Minor update or niche application\n"
                    f"1/10  = Trivial news with no real impact\n"
                    f"0/10  = No importance, will be forgotten immediately\n\n"
                    f"EVALUATION CRITERIA:\n"
                    f"Consider:\n"
                    f"- Scale of impact (how many people/organizations affected?)\n"
                    f"- Timeline (immediate vs years away?)\n"
                    f"- Novelty (truly new or incremental?)\n"
                    f"- Adoption barriers (easy to implement or major obstacles?)\n"
                    f"- Permanence (lasting change or temporary trend?)\n"
                    f"- Competitive advantage (game-changer or table stakes?)\n\n"
                    f"ARTICLE TO EVALUATE:\n"
                    f"Title: {article_title}\n\n"
                    f"Content: {article_content[:3000]}\n\n"
                    f'WHAT TO RETURN'
                    f'Integer between 0-10'
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Extract just the number
    try:
        score = int(content)
    except ValueError:
        # If there's extra text, extract first number found
        match = re.search(r'\d+', content)
        score = int(match.group()) if match else 5
    
    # Clamp to 0-10
    return max(0, min(10, score))
