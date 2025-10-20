# backend/app/api/routes/ingest.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.services.perplexity_service import fetch_ai_news
from app.services.openai_service import summarize_articles

router = APIRouter(prefix="/api", tags=["Ingest"])

@router.post("/ingest")
def ingest_ai_news(query: str = "latest AI news", db: Session = Depends(get_db)):
    # 1️⃣ Pull sources from Perplexity
    sources = fetch_ai_news(query=query, count=5)
    if not sources:
        return {"error": "No sources found."}

    # 2️⃣ Summarize them via OpenAI
    summary_text = summarize_articles(sources)

    # 3️⃣ Create an article in NeonDB
    article = crud.create_article(db, title=f"Summary: {query}", summary_text=summary_text)

    # 4️⃣ Store and link sources
    for src in sources:
        s = crud.create_source(
            db,
            title=src.get("title", "Untitled"),
            domain=src.get("source", None),
            url=src.get("url", None),
            sector=src.get("sector", "General"),
            published_at=src.get("published_at", None)
        )
        crud.link_article_to_source(db, article.id, s.id)

    return {
        "message": "Ingested successfully.",
        "article_id": article.id,
        "linked_sources": len(sources)
    }
