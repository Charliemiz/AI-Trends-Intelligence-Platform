from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.services.article_service import add_article, get_all_articles, get_article_by_id
import logging
from backend.database import get_db

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@router.post("/summary/add")
def add_summary(url: str, summary: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("INSERT INTO summary (url, summary) VALUES (:url, :summary)"),
            {"url": url, "summary": summary},
        )
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-post")
def test_post(message: str):
    return {"received": message, "status": "success"}

@router.get("/articles")
def get_articles(db: Session = Depends(get_db)):
    try:
        articles = get_all_articles(db)
        logger.info(f"Successfully returned {len(articles)} articles")
        return articles
    except Exception as e:
        logger.error(f"Error in get_articles: {e}", exc_info=True)
        raise

@router.get("/articles/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    try:
        article = get_article_by_id(db, article_id)
        return article
    except Exception as e:
        logger.error(f"Error in get_article: {e}", exc_info=True)
        raise