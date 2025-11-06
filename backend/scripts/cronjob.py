from backend.perplexity_functions import perplexity_search_simple
from backend.database import SessionLocal
from backend.models import Article, Source
from backend.services.article_service import add_article
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting cron job...")
    db = SessionLocal()
    try:
        query = "Recent AI trends in education sector"
        
        logger.info(f"Searching for: {query}")
        
        # Get article and sources from Perplexity
        result = perplexity_search_simple(query)

        # Create article object
        article = Article(
            title=result['title'],
            content=result['article'],
        )

        # Create source objects from the search results
        for source_data in result['sources']:
            source = Source(
                name=source_data['title'] or source_data['source'],
                url=source_data['url']
            )
            article.sources.append(source)
        
        # Add to database using your service
        added_article = add_article(db, article)

        logger.info(f"Successfully added article with ID: {added_article.id}")
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()