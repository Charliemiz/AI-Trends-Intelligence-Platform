from sqlalchemy.orm import Session
from backend.db import models

# because I'm going to forget: create, read, update, delete (CRUD)

# -----------------
# SOURCE FUNCTIONS
# -----------------
def create_source(db: Session, name: str, url: str):
    existing = db.query(models.Source).filter(models.Source.url == url).first()
    if existing:
        return existing
    src = models.Source(name=name, url=url)
    db.add(src)
    db.commit()
    db.refresh(src)
    return src

def get_source_by_url(db: Session, url: str):
    return db.query(models.Source).filter(models.Source.url == url).first()

def get_source_by_id(db: Session, source_id: int):
    return db.query(models.Source).filter(models.Source.id == source_id).first()

# -----------------
# ARTICLE FUNCTIONS
# -----------------
def create_article(db: Session, title: str, content: str):
    art = models.Article(title=title, content=content)
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

def get_article_by_id(db: Session, article_id: int):
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
