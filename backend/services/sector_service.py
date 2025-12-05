from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

# Manages sector rotation state using database storage. State is stored in the database instead of a JSON file.
class SectorRotationManager:
    def __init__(self, db: Session):
        self.db = db
        self.state = self._load_state()

    # Load rotation state from file
    def _load_state(self) -> dict:
        from backend.db import models
        
        # Get or create state record
        state_record = self.db.query(models.SystemState).filter(
            models.SystemState.key == "sector_rotation"
        ).first()
        
        if state_record:
            import json
            return json.loads(state_record.value)
        else:
            # Create default state
            return {
                "current_index": 0,
                "sectors_queue": [],
                "last_run": None,
                "cycle_count": 0
            }
    # Save rotation state to file
    def _save_state(self):
        from backend.db import models
        import json
        
        state_record = self.db.query(models.SystemState).filter(
            models.SystemState.key == "sector_rotation"
        ).first()
        
        if state_record:
            state_record.value = json.dumps(self.state)
            state_record.updated_at = datetime.now()
        else:
            state_record = models.SystemState(
                key="sector_rotation",
                value=json.dumps(self.state)
            )
            self.db.add(state_record)
        
        self.db.commit()
    
    # Initialize or reset the sectors queue
    # Args: sectors: List of sectors names to cycle through
    def initialize_sectors(self, sectors: list):
        if not self.state["sectors_queue"] or set(sectors) != set(self.state["sectors_queue"]):
            self.state["sectors_queue"] = sectors.copy()
            self.state["current_index"] = 0
            self._save_state()

    # Get the next sector in rotation
    def get_next_sectors(self) -> Optional[str]:
        if not self.state["sectors_queue"]:
            return None
        
        # Get current sector
        sector = self.state["sectors_queue"][self.state["current_index"]]
        
        # Move to next index
        self.state["current_index"] += 1
        
        # Reset if we've gone through all sectors
        if self.state["current_index"] >= len(self.state["sectors_queue"]):
            self.state["current_index"] = 0
            self.state["cycle_count"] += 1
        
        # Update last run time
        self.state["last_run"] = datetime.now().isoformat()
        
        self._save_state()
        
        return sector
    
    # Get current rotation state
    def get_current_state(self) -> dict:
        return {
            "current_sector": self.state["sectors_queue"][self.state["current_index"]] 
                           if self.state["sectors_queue"] else None,
            "sectors_remaining": len(self.state["sectors_queue"]) - self.state["current_index"],
            "total_sectors": len(self.state["sectors_queue"]),
            "cycle_count": self.state["cycle_count"],
            "last_run": self.state["last_run"]
        }
    
    # Reset rotation to beginning
    def reset(self):
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

# FUNCTIONS FOR TOPIC ROTATION

# Get enabled sectors 
def get_enabled_sectors():
    return [sector for sector, config in SECTOR_CONFIG.items() if config["enabled"]]

# Get tags for a specific sector
def get_sector_tags(sector):
    return SECTOR_CONFIG.get(sector, {}).get("tags", [])

# Get complete config for a sector
def get_sector_config(sector):
    return SECTOR_CONFIG.get(sector, {})
