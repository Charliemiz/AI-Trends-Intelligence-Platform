from backend.services.perplexity_service import perplexity_search_simple
from backend.services.extract_domain import extract_domain
from backend.services.categorize_sector import categorize_sector
from backend.db.database import SessionLocal
from backend.db.crud import create_article_with_sources
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting cron job...")
    db = SessionLocal()

    try:
        query = "Recent AI trends in education sector"
        logger.info(f"Searching for: {query}")

        result = perplexity_search_simple(query)
        sector = categorize_sector(query)
        logger.info(f"Query categorized as sector: {sector}")
        
        sources_data = []
        for source in result['sources']:
            source_name = source.get("title") or source.get("name", "Unknown Source")
            source_url = source["url"]
            
            sources_data.append({
                "name": source_name,
                "url": source_url,
                "domain": extract_domain(source_url),
                "sector": sector  # All sources from this query get the same sector
            })
        
        # Create article with sources
        article = create_article_with_sources(
            db=db,
            title=result['title'],
            content=result['article'],
            sources_data=sources_data
        )

        logger.info(f"Successfully added article with ID: {article.id}")
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise

if __name__ == "__main__":
    main()