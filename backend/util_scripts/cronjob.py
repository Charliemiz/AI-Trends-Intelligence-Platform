from backend.services.perplexity_service import perplexity_search_simple
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
        article = create_article_with_sources(
            db=db,
            title=result['title'],
            content=result['article'],
            sources_data=result['sources']
        )

        logger.info(f"Successfully added article with ID: {article.id}")
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise

if __name__ == "__main__":
    main()