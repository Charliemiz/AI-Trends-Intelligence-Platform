"""
Topic/Sector Configuration and Categorization
"""

# Define all sectors with their search tags/keywords
SECTOR_CONFIG = {
    "AI": {
        "tags": [
            "ai", "artificial intelligence", "machine learning", "deep learning",
            "neural networks", "llm", "gpt", "generative ai", "chatgpt",
            "computer vision", "natural language processing", "ai ethics",
            "ai regulation", "ai models", "transformer models"
        ],
        "enabled": True
    },
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
    """
    Categorize a query into a sector by matching keywords.
    Returns sector name or "General" if no match.
    
    Args:
        query: Search query string
        
    Returns:
        Sector name (e.g., "AI", "Healthcare") or "General"
    """
    query_lower = query.lower()
    
    # Check each sector's keywords
    for sector, config in SECTOR_CONFIG.items():
        keywords = config.get("tags", [])
        for keyword in keywords:
            if keyword in query_lower:
                return sector
    
    # No match found
    return "General"