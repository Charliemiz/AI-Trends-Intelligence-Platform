from backend.services.perplexity_service import perplexity_search_simple, perplexity_search_trends, perplexity_find_articles, perplexity_summarize
from backend.services.extract_domain import extract_domain
from backend.services.topics_config import categorize_sector, get_enabled_sectors, get_sector_tags
from backend.db.database import SessionLocal
from backend.db.crud import create_article_with_sources
from backend.services.topic_rotation import TopicRotationManager
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

        for trend in trending_topics:
            articles = perplexity_find_articles(trend, count=5)
            
            query = f"Write an article summarizing and explaining {trend}"
            logger.info(f"Searching for: {query}")

            result = perplexity_summarize(query, articles)
            sector = categorize_sector(query)
            # logger.info(f"Query categorized as sector: {sector}")
        
            sources_data = []
            for source in result['sources']:
                source_name = source.get("title") 
                source_url = source["url"]
                
                sources_data.append({
                    "title": source_name,
                    "url": source_url,
                    "domain": extract_domain(source_url),
                    "sector": sector  # All sources from this query get the same sector
                })
            
            # Create article with sources
            article = create_article_with_sources(
                db=db,
                title=trend,
                content=result['article'],
                sources_data=sources_data
            )

            logger.info(f"Successfully added article with ID: {article.id}")
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise

if __name__ == "__main__":
    main()
