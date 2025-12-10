"""Scheduled job to discover, summarize and persist trending articles.

This script is intended to be run from a scheduler (cron, task scheduler)
or invoked manually. It rotates through enabled sectors and uses Perplexity
and other helpers to build and store article summaries.
"""

from backend.services.perplexity_service import perplexity_search_trends, perplexity_find_articles, perplexity_summarize, perplexity_impact_score
from backend.services.source_services import extract_domain, filter_and_renumber_sources
from backend.db.database import SessionLocal
from backend.db.crud import create_article_with_sources_and_tags
from backend.services.sector_service import SectorRotationManager, get_enabled_sectors, get_sector_tags
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entrypoint for the cron job flow.

    Orchestrates sector rotation, topic discovery, article search, summary
    generation and persistence. Intended for use by a scheduler.
    """
    logger.info("Starting cron job...")
    db = SessionLocal()

    try:
        # Get enabled sectors
        enabled_sectors = get_enabled_sectors()
        
        # Create rotation manager with database
        manager = SectorRotationManager(db=db)
        manager.initialize_sectors(enabled_sectors)

        # Get current sector in rotation
        sector = manager.get_next_sectors()

        # Get tags
        tags = get_sector_tags(sector)

        logger.info(f"Current sector: {sector}")

        # Find trending topics
        trending_topics = perplexity_search_trends(sector, tags, count=3)

        if not trending_topics or len(trending_topics) < 2:
            logger.warning(f"Not enough valid AI-related topics found for {sector} ({len(trending_topics) if trending_topics else 0}/3)")
            logger.warning("Skipping to next sector. Sector already advanced in rotation.")
            return

        for trend in trending_topics:
            try:
                articles = perplexity_find_articles(trend, count=20)
                
                # Remove blacklisted entirely
                valid_articles = [a for a in articles if not a.get("blacklisted", False)]

                # Filter to trusted and uncertain
                trusted_articles = [a for a in valid_articles if a.get("trusted", False)]
                uncertain_articles = [a for a in valid_articles if not a.get("trusted", False)]

                # Track how many sources we're providing
                sources_provided_count = len(trusted_articles) + len(uncertain_articles)

                # Log source distribution
                logger.info(f"Sources found: {len(trusted_articles)} trusted, {len(uncertain_articles)} uncertain (total: {sources_provided_count})")

                query = f"Write an article summarizing and explaining {trend}"
                logger.info(f"Searching for: {query}")

                result = perplexity_summarize(query, trusted_articles, uncertain_articles)
                
                impact_score = perplexity_impact_score(
                    article_title=trend,
                    article_content=result['article'],
                    sector=sector
                )
                
                # Filter unused sources AND renumber citations
                renumbered_article, filtered_sources_list, filter_stats = filter_and_renumber_sources(
                    article_text=result['article'],
                    sources=result['sources'],
                    sources_provided_count=sources_provided_count
                )
                
                # Log filtering results
                logger.info(f"Citations: {filter_stats['cited_numbers_original']} -> {list(range(1, len(filter_stats['cited_numbers_original']) + 1))}")
                
                if filter_stats['citation_mapping'] != {i: i for i in filter_stats['cited_numbers_original']}:
                    logger.info(f"Renumbered citations: {filter_stats['citation_mapping']}")
                
                # Check if Perplexity added extra sources
                if filter_stats['extra_sources_added']:
                    logger.warning(f"Perplexity added {filter_stats['extra_sources_count']} extra source(s)!")
                    logger.warning(f"Provided {filter_stats['total_sources_provided']}, returned {filter_stats['total_sources_returned']}")
                
                logger.info(f"Source usage: {filter_stats['sources_filtered']}/{filter_stats['total_sources_returned']} (removed {filter_stats['sources_removed']} unused)")
                
                if filter_stats['sources_removed'] > 0 and filter_stats['unused_numbers']:
                    logger.info(f"Removed sources at positions: {filter_stats['unused_numbers']}")
                
                # Build final sources list for database (only cited sources, in citation order)
                sources = []
                for source in filtered_sources_list:
                    source_name = source.get("title") 
                    source_url = source["url"]
                    
                    sources.append({
                        "title": source_name,
                        "url": source_url,
                        "domain": extract_domain(source_url),
                        "sector": sector
                    })
                
                # Create article with renumbered citations and filtered sources
                article = create_article_with_sources_and_tags(
                    db=db,
                    title=trend,
                    content=renumbered_article,
                    sources=sources,
                    tags=result['tags'],
                    impact_score=impact_score,
                    sector=sector
                )

                logger.info(f"Article ID {article.id}: Impact {impact_score}/10, Sources: {len(sources)}")
            
            except Exception as e:
                logger.error(f"Error on trend '{trend}': {e}, skipping...")
                continue
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        raise

if __name__ == "__main__":
    main()
