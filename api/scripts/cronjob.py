from perplexity_functions import perplexity_search_rest
from services.article_service import add_article
from database import SessionLocal
import logging
from models import Article, Source, SourceArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting cron job...")
    db = SessionLocal()
    try: 
        # Create article object
        article = Article(
            title="Recent AI Trends",
            content="Content about recent AI trends...",
        )

        # Create source object
        source = Source(
            name="Tech News",
            url="https://technews.example.com/recent-ai-trends"
        )

        # Establish many-to-many relationship
        article.sources.append(source)
        
        # Add to database using your service
        added_article = add_article(db, article)
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise


if __name__ == "__main__":
    main()