from sqlalchemy.orm import Session
from app.db import models

# because I'm going to forget: create, read, update, delete (CRUD)

# backend/app/db/crud.py
from sqlalchemy.orm import Session
from app.db import models

# -----------------
# SOURCE FUNCTIONS
# -----------------
def create_source(db: Session, title: str, domain: str, url: str, sector: str, published_at=None, scraped_text=None):
    existing = db.query(models.Source).filter(models.Source.url == url).first()
    if existing:
        return existing
    src = models.Source(
        title=title,
        domain=domain,
        url=url,
        sector=sector,
        published_at=published_at,
        scraped_text=scraped_text
    )
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


def get_source_by_url(db: Session, url: str):
    return db.query(models.Source).filter(models.Source.url == url).first()


# -----------------
# ARTICLE FUNCTIONS
# -----------------
def create_article(db: Session, title: str, summary_text: str, summary_model: str = "gpt-4o-mini"):
    art = models.Article(title=title, summary_text=summary_text, summary_model=summary_model)
    db.add(art)
    db.commit()
    db.refresh(art)
    return art


def get_article(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.id == article_id).first()


# -----------------
# LINK FUNCTIONS
# -----------------
def link_article_to_source(db: Session, article_id: int, source_id: int):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not article or not source:
        return None

    if source not in article.sources:
        article.sources.append(source)
        db.commit()
        db.refresh(article)
    return article
