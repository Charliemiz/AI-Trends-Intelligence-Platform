from fastapi import APIRouter, Depends
from app.services.perplexity_service import fetch_ai_articles
from app.db.crud import save_articles
from app.db.database import SessionLocal

router = APIRouter()

SECTORS = ["Healthcare", "Finance", "Retail", "Manufacturing", "Education"]

@router.post("/ingest")
def ingest_articles():
    db = SessionLocal()
    all_articles = []
    for sector in SECTORS:
        articles = fetch_ai_articles(sector)
        save_articles(db, articles)
        all_articles.extend(articles)
    db.close()
    return {"status": "success", "count": len(all_articles)}
