from sqlalchemy.orm import Session
from models import Article

def add_article(db: Session, title: str, url: str, summary: str, source: str) -> Article:
    article = Article(title=title, url=url, summary=summary, source=source)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Article).offset(skip).limit(limit).all()
