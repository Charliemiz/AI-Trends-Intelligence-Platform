import json
from pathlib import Path
from datetime import datetime
from typing import Optional

class TopicRotationManager:
    def __init__(self, state_file: str = "topic_rotation_state.json"):
        """
        Initialize the rotation manager
        
        Args:
            state_file: Path to JSON file storing rotation state
        """
        self.state_file = Path(state_file)
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load rotation state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "current_index": 0,
                "topics_queue": [],
                "last_run": None,
                "cycle_count": 0
            }
    
    def _save_state(self):
        """Save rotation state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def initialize_topics(self, topics: list):
        """
        Initialize or reset the topics queue
        
        Args:
            topics: List of topic names to cycle through
        """
        if not self.state["topics_queue"] or set(topics) != set(self.state["topics_queue"]):
            self.state["topics_queue"] = topics.copy()
            self.state["current_index"] = 0
            self._save_state()
    
    def get_next_topic(self) -> Optional[str]:
        """
        Get the next topic in rotation
        
        Returns:
            Topic name, or None if no topics available
        """
        if not self.state["topics_queue"]:
            return None
        
        # Get current topic
        topic = self.state["topics_queue"][self.state["current_index"]]
        
        # Move to next index
        self.state["current_index"] += 1
        
        # Reset if we've gone through all topics
        if self.state["current_index"] >= len(self.state["topics_queue"]):
            self.state["current_index"] = 0
            self.state["cycle_count"] += 1
        
        # Update last run time
        self.state["last_run"] = datetime.now().isoformat()
        
        self._save_state()
        
        return topic
    
    def get_current_state(self) -> dict:
        """Get current rotation state"""
        return {
            "current_topic": self.state["topics_queue"][self.state["current_index"]] 
                           if self.state["topics_queue"] else None,
            "topics_remaining": len(self.state["topics_queue"]) - self.state["current_index"],
            "total_topics": len(self.state["topics_queue"]),
            "cycle_count": self.state["cycle_count"],
            "last_run": self.state["last_run"]
        }
    
    def reset(self):
        """Reset rotation to beginning"""
        self.state["current_index"] = 0
        self.state["cycle_count"] = 0
        self._save_state()

# Define all sectors with their search tags/keywords
SECTOR_CONFIG = {
    "Education": {
        "tags": [
            "education", "learning", "teaching", "school", "university",
            "student", "classroom", "academic", "edtech"
        ],
        "enabled": True
    },
    "Healthcare": {
        "tags": [
            "health", "medical", "hospital", "doctor", "patient",
            "medicine", "clinical", "healthcare", "pharmaceutical"
        ],
        "enabled": True
    },
    "Finance": {
        "tags": [
            "finance", "banking", "investment", "financial", "stock",
            "trading", "cryptocurrency", "fintech", "economy"
        ],
        "enabled": True
    },
    "Technology": {
        "tags": [
            "technology", "tech", "software", "hardware", "computing",
            "digital", "internet", "cloud", "cybersecurity"
        ],
        "enabled": True
    },
    "Business": {
        "tags": [
            "business", "enterprise", "corporate", "company", "startup",
            "entrepreneur", "management", "commerce"
        ],
        "enabled": True
    },
    "Science": {
        "tags": [
            "science", "research", "scientific", "study", "experiment",
            "laboratory", "physics", "biology", "chemistry"
        ],
        "enabled": True
    },
    "Government": {
        "tags": [
            "government", "policy", "regulation", "law", "legislation",
            "congress", "senate", "federal", "political"
        ],
        "enabled": True
    },
    "Media": {
        "tags": [
            "media", "news", "journalism", "publication", "broadcasting",
            "entertainment", "press", "content"
        ],
        "enabled": True
    },
    "Environment": {
        "tags": [
            "environment", "climate", "sustainability", "green", "renewable",
            "carbon", "ecological", "conservation"
        ],
        "enabled": True
    },
    "Transportation": {
        "tags": [
            "transportation", "automotive", "vehicle", "car", "travel",
            "logistics", "shipping", "mobility"
        ],
        "enabled": True
    },
    "Energy": {
        "tags": [
            "energy", "power", "electricity", "solar", "wind",
            "nuclear", "oil", "gas", "battery"
        ],
        "enabled": True
    },
    "Manufacturing": {
        "tags": [
            "manufacturing", "production", "factory", "industrial", "assembly",
            "automation", "supply chain"
        ],
        "enabled": True
    },
    "Retail": {
        "tags": [
            "retail", "shopping", "ecommerce", "store", "consumer",
            "sales", "marketplace", "e-commerce"
        ],
        "enabled": True
    },
    "Real Estate": {
        "tags": [
            "real estate", "property", "housing", "construction", "building",
            "architecture", "mortgage"
        ],
        "enabled": True
    },
    "Agriculture": {
        "tags": [
            "agriculture", "farming", "crop", "livestock", "food production",
            "agricultural", "agritech"
        ],
        "enabled": True
    },
    "Sports": {
        "tags": [
            "sports", "athletic", "fitness", "game", "competition",
            "recreation", "exercise", "olympics"
        ],
        "enabled": True
    },
    "Arts": {
        "tags": [
            "arts", "music", "film", "theater", "design",
            "creative", "culture", "entertainment", "gallery"
        ],
        "enabled": True
    },
    "Security": {
        "tags": [
            "security", "cybersecurity", "defense", "military", "protection",
            "surveillance", "safety", "privacy"
        ],
        "enabled": True
    },
    "Telecommunications": {
        "tags": [
            "telecommunications", "telecom", "mobile", "wireless", "5g",
            "broadband", "network", "connectivity"
        ],
        "enabled": True
    }
}

# ==========================================
# FUNCTIONS FOR TOPIC ROTATION
# ==========================================

def get_enabled_sectors():
    """Get list of enabled sectors for rotation"""
    return [sector for sector, config in SECTOR_CONFIG.items() if config["enabled"]]


def get_sector_tags(sector):
    """Get tags for a specific sector"""
    return SECTOR_CONFIG.get(sector, {}).get("tags", [])


def get_sector_config(sector):
    """Get complete config for a sector"""
    return SECTOR_CONFIG.get(sector, {})

# ==========================================
# FUNCTIONS FOR QUERY CATEGORIZATION
# ==========================================

def categorize_sector(query: str) -> str:
    query_lower = query.lower()
    
    # Check each sector's keywords
    for sector, config in SECTOR_CONFIG.items():
        keywords = config.get("tags", [])
        for keyword in keywords:
            if keyword in query_lower:
                return sector
    
    # No match found
    return "General"
