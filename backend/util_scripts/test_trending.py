"""
Test Script for Perplexity Trending Topics
"""

import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir
while project_root != project_root.parent:
    if (project_root / 'backend').exists():
        break
    project_root = project_root.parent

sys.path.insert(0, str(project_root))

from backend.queuery_expermintation.topic_rotation import TopicRotationManager
from backend.queuery_expermintation.topics_config import get_enabled_sectors, get_sector_tags
from backend.services.perplexity_service import perplexity_search_trends


def test_trending_topics():
    """Test finding trending topics"""
    
    # Define state file location
    state_file = project_root / "backend" / "util_scripts" / "topic_rotation_state.json"
    
    # Get enabled sectors
    enabled_sectors = get_enabled_sectors()
    
    # Create rotation manager
    manager = TopicRotationManager(str(state_file))
    manager.initialize_topics(enabled_sectors)
    
    # Get next sector
    sector = manager.get_next_topic()
    
    # Get tags for this sector
    tags = get_sector_tags(sector)
    
    # Find trending topics
    trending_topics = perplexity_search_trends(sector, tags, count=3)
    
    # Print results
    print(f"Sector: {sector}\n")
    print("Trending Topics:")
    for i, topic in enumerate(trending_topics, 1):
        print(f"{i}. {topic}")


if __name__ == "__main__":
    test_trending_topics()