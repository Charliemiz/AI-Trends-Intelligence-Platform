from backend.services.perplexity_service import perplexity_search_trends, perplexity_find_articles, perplexity_summarize, perplexity_impact_score
from backend.services.source_services import extract_domain, CREDIBLE_SOURCES
from backend.db.database import SessionLocal
from backend.db.crud import create_article_with_sources_and_tags
from backend.services.topic_rotation import TopicRotationManager,categorize_sector, get_enabled_sectors, get_sector_tags
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting cron job...")
    db = SessionLocal()

    try:
        #topic_rotation_state.json location, (current topic state management)
        state_file = os.path.join(os.path.dirname(__file__), "topic_rotation_state.json")
        
        # Get enabled sectors
        enabled_sectors = get_enabled_sectors()
        
        # Create rotation manager
        manager = TopicRotationManager(str(state_file))
        manager.initialize_topics(enabled_sectors)

        #Get current topic in rotation
        topic = manager.get_next_topic()
        #Get tags
        tags = get_sector_tags(topic)

        # Find trending topics
        trending_topics = perplexity_search_trends(topic, tags, count=3)

        if not trending_topics or len(trending_topics) < 2:
            logger.warning(f"⚠️  Not enough valid AI-related topics found for {topic} ({len(trending_topics) if trending_topics else 0}/3)")
            logger.warning(f"Skipping to next sector. Sector already advanced in rotation.")
            return

        for trend in trending_topics:
            try:
                articles = perplexity_find_articles(trend, count=20, credible_sources=CREDIBLE_SOURCES)
                
                # Filter to trusted only
                trusted_articles = [a for a in articles if a.get("trusted", False)]
                
                # Skip if no trusted sources
                if not trusted_articles:
                    logger.warning(f"No trusted sources for: {trend}, skipping...")
                    continue

                query = f"Write an article summarizing and explaining {trend}"
                logger.info(f"Searching for: {query}")

                result = perplexity_summarize(query, trusted_articles)
                sector = categorize_sector(query)
            
                sources_data = []
                for source in result['sources']:
                    source_name = source.get("title") 
                    source_url = source["url"]
                    
                    sources_data.append({
                        "title": source_name,
                        "url": source_url,
                        "domain": extract_domain(source_url),
                        "sector": sector
                    })
                
                # Create article with sources
                article = create_article_with_sources_and_tags(
                    db=db,
                    title=trend,
                    content=result['article'],
                    sources_data=sources_data,
                    tags=result['tags']
                )

                logger.info(f"Successfully added article with ID: {article.id}")

                impact_score = perplexity_impact_score(
                    article_title=trend,
                    article_content=result['article'],
                    sector=sector
                )
                
                print(f"Impact Score: {impact_score}")
            
            except Exception as e:
                logger.error(f"Error on trend '{trend}': {e}, skipping...")
                continue
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise

if __name__ == "__main__":
    main()
