from sqlalchemy.orm import Session
from models import Article
from database import get_db

def add_article(db: Session, article: Article) -> Article:
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Article).offset(skip).limit(limit).all()
