"""
Test Script for Topic Rotation System
Simple demonstration of how the rotation works
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


def test_topic_rotation():
    """Test the topic rotation system"""
    
    # Define state file location
    state_file = project_root / "backend" / "util_scripts" / "topic_rotation_state.json"
    
    # Get enabled sectors
    enabled_sectors = get_enabled_sectors()
    
    # Create rotation manager
    manager = TopicRotationManager(str(state_file))
    
    # Initialize with enabled sectors (this will create the JSON if it doesn't exist)
    manager.initialize_topics(enabled_sectors)
    
    # Get next topic
    selected_topic = manager.get_next_topic()
    
    # Get tags for this topic
    tags = get_sector_tags(selected_topic)
    
    # Create sample query
    tags_sample = ", ".join(tags)
    sample_query = f"Recent trends and developments in {selected_topic} related to {tags_sample}"
    
    # Print only what we need
    print(f"Sector: {selected_topic}")
    print(f"\nQuery:\n{sample_query}")

if __name__ == "__main__":
    test_topic_rotation()