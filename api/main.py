from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv, find_dotenv
from api.perplexity_functions import perplexity_search, perplexity_summarize, perplexity_search_simple
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from api.models import Base, Article
from api.services.article_service import add_article, get_all_articles, get_article_by_id
import logging
from api.database import engine, get_db, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables if they don't exist (for ORM it creates tables for all models that inherit from Base)
# These models are in our models.py file in this same directory
Base.metadata.create_all(bind=engine)

app = FastAPI()

ALLOWED_ORIGINS = [
    "https://ai-trends-intelligence-platform.vercel.app",
    "https://ai-trends-intelligence-pl-git-263e86-charlies-projects-a3f87fbc.vercel.app",
    "https://ai-trends-intelligence-platform-kcanrbje9.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/summary/add")
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

@app.post("/test-post")
def test_post(message: str):
    return {"received": message, "status": "success"}

@app.get("/articles")
def get_articles(db: Session = Depends(get_db)):
    try:
        articles = get_all_articles(db)
        logger.info(f"Successfully returned {len(articles)} articles")
        return articles
    except Exception as e:
        logger.error(f"Error in get_articles: {e}", exc_info=True)
        raise

@app.get("/articles/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    try:
        article = get_article_by_id(db, article_id)
        return article
    except Exception as e:
        logger.error(f"Error in get_article: {e}", exc_info=True)
        raise