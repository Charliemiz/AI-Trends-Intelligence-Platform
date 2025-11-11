"""
Sector Categorization Utilities
Simple keyword-based sector matching from search queries
"""

# Define sectors with their keywords
SECTOR_KEYWORDS = {
    "Education": ["education", "learning", "teaching", "school", "university", "student", "classroom", "academic", "edtech"],
    "Healthcare": ["health", "medical", "hospital", "doctor", "patient", "medicine", "clinical", "healthcare", "pharmaceutical"],
    "Finance": ["finance", "banking", "investment", "financial", "stock", "trading", "cryptocurrency", "fintech", "economy"],
    "Technology": ["technology", "tech", "software", "hardware", "computing", "digital", "internet", "cloud", "cybersecurity"],
    "Business": ["business", "enterprise", "corporate", "company", "startup", "entrepreneur", "management", "commerce"],
    "Science": ["science", "research", "scientific", "study", "experiment", "laboratory", "physics", "biology", "chemistry"],
    "Government": ["government", "policy", "regulation", "law", "legislation", "congress", "senate", "federal", "political"],
    "Media": ["media", "news", "journalism", "publication", "broadcasting", "entertainment", "press", "content"],
    "Environment": ["environment", "climate", "sustainability", "green", "renewable", "carbon", "ecological", "conservation"],
    "Transportation": ["transportation", "automotive", "vehicle", "car", "travel", "logistics", "shipping", "mobility"],
    "Energy": ["energy", "power", "electricity", "solar", "wind", "nuclear", "oil", "gas", "battery"],
    "Manufacturing": ["manufacturing", "production", "factory", "industrial", "assembly", "automation", "supply chain"],
    "Retail": ["retail", "shopping", "ecommerce", "store", "consumer", "sales", "marketplace", "e-commerce"],
    "Real Estate": ["real estate", "property", "housing", "construction", "building", "architecture", "mortgage"],
    "Agriculture": ["agriculture", "farming", "crop", "livestock", "food production", "agricultural", "agritech"],
    "Sports": ["sports", "athletic", "fitness", "game", "competition", "recreation", "exercise", "olympics"],
    "Arts": ["arts", "music", "film", "theater", "design", "creative", "culture", "entertainment", "gallery"],
    "Security": ["security", "cybersecurity", "defense", "military", "protection", "surveillance", "safety", "privacy"],
    "Telecommunications": ["telecommunications", "telecom", "mobile", "wireless", "5g", "broadband", "network", "connectivity"]
}

def categorize_sector(query: str) -> str:
    query_lower = query.lower()
    
    # Check each sector's keywords
    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                return sector
    
    # No match found
    return "General"