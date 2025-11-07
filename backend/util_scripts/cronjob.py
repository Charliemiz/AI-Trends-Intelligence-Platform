from backend.services.perplexity_service import perplexity_search_simple
from backend.db.database import get_db
from backend.db.crud import create_article, create_source
from fastapi import Depends
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting cron job...")
    db = Depends(get_db)
    
    try:
        query = "Recent AI trends in education sector"
        logger.info(f"Searching for: {query}")
        result = perplexity_search_simple(query)
        article = create_article(db=db, title=result['title'], content=result['article'])

        for source_data in result['sources']:
            source = create_source(db=db, name=(source_data['title'] or source_data['source']), url=source_data['url'])
            article.sources.append(source)

        logger.info(f"Successfully added article with ID: {article.id}")
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()