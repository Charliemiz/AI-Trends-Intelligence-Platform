from backend.services.perplexity_service import perplexity_search_trends, perplexity_find_articles, perplexity_summarize, perplexity_impact_score
from backend.services.source_services import extract_domain
from backend.db.database import SessionLocal
from backend.db.crud import create_article_with_sources_and_tags
from backend.services.sector_service import SectorRotationManager, get_enabled_sectors, get_sector_tags
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting cron job...")
    db = SessionLocal()

    try:
        # Get enabled sectors
        enabled_sectors = get_enabled_sectors()
        
        # Create rotation manager with database
        manager = SectorRotationManager(db=db)
        manager.initialize_sectors(enabled_sectors)

        #Get current sector in rotation
        sector = manager.get_next_sectors()
        #Get tags
        tags = get_sector_tags(sector)

        logger.info(f"Current sector: {sector}")

        # Find trending topics
        trending_topics = perplexity_search_trends(sector, tags, count=3)

        if not trending_topics or len(trending_topics) < 2:
            logger.warning(f"⚠️  Not enough valid AI-related topics found for {sector} ({len(trending_topics) if trending_topics else 0}/3)")
            logger.warning(f"Skipping to next sector. Sector already advanced in rotation.")
            return

        for trend in trending_topics:
            try:
                articles = perplexity_find_articles(trend, count=20)
                
                # Remove blacklisted entirely
                valid_articles = [a for a in articles if not a.get("blacklisted", False)]

                # Filter to trusted and uncertain
                trusted_articles = [a for a in valid_articles if a.get("trusted", False)]
                uncertain_articles = [a for a in valid_articles if not a.get("trusted", False)]
                
                # Skip if no trusted sources
                if not trusted_articles:
                    logger.warning(f"No trusted sources for: {trend}, skipping...")
                    continue

                query = f"Write an article summarizing and explaining {trend}"
                logger.info(f"Searching for: {query}")

                result = perplexity_summarize(query, trusted_articles, uncertain_articles)
                
                impact_score = perplexity_impact_score(
                    article_title=trend,
                    article_content=result['article'],
                    sector=sector
                )
            
                sources = []
                for source in result['sources']:
                    source_name = source.get("title") 
                    source_url = source["url"]
                    
                    sources.append({
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
                    sources=sources,
                    tags=result['tags'],
                    impact_score=impact_score
                )

                logger.info(f"Successfully added article with ID: {article.id}")
            
            except Exception as e:
                logger.error(f"Error on trend '{trend}': {e}, skipping...")
                continue
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise

if __name__ == "__main__":
    main()
