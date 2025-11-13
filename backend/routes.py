from typing import Union
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.crud import get_all_articles, get_article_by_id
from backend.db.schemas import ArticleSchema, ArticleListSchema
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@router.get("/articles", response_model=list[ArticleListSchema])
def get_articles(db: Session = Depends(get_db)):
    try:
        articles = get_all_articles(db)
        logger.info(f"Successfully returned {len(articles)} articles")
        return articles
    except Exception as e:
        logger.error(f"Error in get_articles: {e}", exc_info=True)
        raise

@router.get("/articles/{article_id}", response_model=ArticleSchema)
def get_article(article_id: int, db: Session = Depends(get_db)):
    try:
        return get_article_by_id(db, article_id)
    except Exception as e:
        logger.error(f"Error in get_article: {e}", exc_info=True)
        raise