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
    
    print(f"Providing {len(all_articles)} numbered sources to Perplexity ({len(trusted_articles)} trusted, {len(uncertain_articles) if uncertain_articles else 0} uncertain)...")
    
    # Build NUMBERED source list (prevents reordering)
    sources_text = ""
    
    # Add trusted sources first
    source_num = 1
    for article in trusted_articles:
        sources_text += f"[{source_num}] [TRUSTED] {article.get('title', 'No title')}\n"
        sources_text += f"    URL: {article.get('url', '')}\n\n"
        source_num += 1
    
    # Add uncertain sources after
    for article in uncertain_articles if uncertain_articles else []:
        sources_text += f"[{source_num}] [UNCERTAIN] {article.get('title', 'No title')}\n"
        sources_text += f"    URL: {article.get('url', '')}\n\n"
        source_num += 1
    
    # Use sonar model with strict numbered source instructions
    payload = {
        "model": "sonar",  
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional research journalist. "
                    "You will be given a numbered list of sources. "
                    "USE ONLY these sources and cite them by their assigned numbers. "
                    "DO NOT reorder sources. DO NOT search for additional sources. "
                    "PRIORITIZE [TRUSTED] sources over [UNCERTAIN] sources."
                )
            },
            {
                "role": "user",
                "content": (
                    f"{query}\n\n"
                    
                    f"SOURCES (cite using the exact numbers shown):\n\n"
                    f"{sources_text}\n"
                    
                    f"CRITICAL INSTRUCTIONS:\n"
                    f"- Write an 800-1200 word comprehensive article\n"
                    f"- USE ONLY the numbered sources listed above\n"
                    f"- Cite sources using their EXACT numbers: [1], [2], [3], etc.\n"
                    f"- DO NOT reorder or renumber sources\n"
                    f"- DO NOT search for or add additional sources\n"
                    f"- Prioritize [TRUSTED] sources over [UNCERTAIN] sources\n"
                    f"- When sources conflict, prefer [TRUSTED] sources\n\n"
                    
                    f"STRUCTURE:\n"
                    f"- Start with a compelling title (proper capitalization, NO citations)\n"
                    f"- Use 2-4 section headers with double-asterisks (e.g., '**Conclusion**')\n"
                    f"- Maintain neutral, clear, journalistic tone for general audience\n"
                    f"- Cite sources naturally in text using brackets: [1], [2], etc.\n"
                    f"- Format citations like: 'The market grew[3]' NOT 'The market grew. [3]'\n"
                    f"- Avoid bullet lists - use prose paragraphs only\n\n"
                    
                    f"TAGS REQUIREMENTS (CRITICAL):\n"
                    f"- Include EXACTLY 5-10 relevant tags\n"
                    f"- Tags: companies, technologies, people, industries, concepts, products\n"
                    f"- Use proper capitalization (e.g., 'OpenAI', 'Microsoft', 'GPT-4')\n"
                    f"- DO NOT use symbols: NO '**', NO '##', NO '#', NO '['\n"
                    f"- Format: 'tag1, tag2, tag3' NOT '**tag1**, **tag2**'\n"
                    f"- Separate with commas only\n\n"

                    f"FORMAT (MUST FOLLOW EXACTLY):\n"
                    f"[Title with no markdown]\n\n"
                    f"[Article with **headers** and [X] citations]\n\n"
                    f"TAGS: tag1, tag2, tag3, tag4, tag5\n\n"
                    
                    f"EXAMPLE CORRECT TAGS:\n"
                    f"TAGS: Artificial Intelligence, Federal Preemption, AI Policy, Digital Government\n\n"
                    
                    f"EXAMPLE WRONG TAGS (DO NOT USE):\n"
                    f"TAGS: **AI Policy** **Federal Government** (WRONG - no asterisks)\n"
                    f"TAGS: #AI #Policy (WRONG - no hashtags)"
                )
            }
        ]
    }

    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=90)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    
    # Parse tags with cleaning
    tags = []
    
    # Split content to extract tags
    if "TAGS:" in content:
        main_content, tags_part = content.split("TAGS:", 1)
        tags_part = tags_part.strip()
        tags_part = tags_part.strip('*#[]"\'')
        raw_tags = tags_part.split(",")
        
        for tag in raw_tags:
            cleaned = tag.strip()
            cleaned = cleaned.strip('*#[]"\'')
            if cleaned and 2 <= len(cleaned) <= 50:
                tags.append(cleaned)
        
        print(f"  📎 Extracted {len(tags)} tags")
    else:
        main_content = content
        print(f"No TAGS: found in response")
    
    # Parse title and article
    lines = main_content.split("\n")  
    title = ""                         
    article_text = ""

    for i, line in enumerate(lines):
        if line.startswith("##") or line.startswith("# "):
            title = line.replace("##", "").replace("#", "").strip()
        elif line.startswith("ARTICLE:"):
            article_text = "\n".join(lines[i+1:]).strip()
            break
    
    if not title and lines:
        title = lines[0].strip()
        article_text = "\n".join(lines[1:]).strip()
    
    if not title:
        title = query
    if not article_text:
        article_text = main_content
    
    # Check if Perplexity used search_results (web search beyond our sources)
    search_results = data.get("search_results", [])
    
    if search_results:
        # Perplexity searched the web - use what it actually found
        sources = []
        for result in search_results:
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "source": result.get("url", "").split("/")[2] if result.get("url") else ""
            })
        
        # Warn if different from what we provided
        if len(search_results) != len(all_articles):
            print(f"WARNING: Perplexity used {len(search_results)} sources, we provided {len(all_articles)}")
            if len(search_results) > len(all_articles):
                print(f"Perplexity searched beyond our sources and found {len(search_results) - len(all_articles)} extra!")
        else:
            print(f"  sources match: {len(sources)} sources used")
    else:
        # No search_results, return our original sources
        sources = []
        for article in all_articles:
            sources.append({
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "source": article.get("url", "").split("/")[2] if article.get("url") else ""
            })
        print(f"  Using provided sources: {len(sources)}")

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
