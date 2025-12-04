from typing import cast
from sqlalchemy.orm import Session
from backend.db import models

# because I'm going to forget: create, read, update, delete (CRUD)

# -----------------
# SOURCE FUNCTIONS
# -----------------
def get_or_create_sources_bulk(db: Session, sources: list[dict]):
    """
    Take in a list of dictionaries with 'title' and 'url' keys,
    return a list of Source objects, creating any that don't already exist.
    """
    urls = [s["url"] for s in sources]

    # Query for sources that already exist
    existing_sources = db.query(models.Source).filter(models.Source.url.in_(urls)).all()
    existing_urls = {source.url: source.id for source in existing_sources}

    sourceIds = []
        
    for source in sources:
        if source["url"] in existing_urls:
            sourceIds.append(existing_urls[source["url"]])
        else:
            new_source = models.Source(title=source["title"], url=source["url"], domain=source["domain"], sector=source["sector"])
            db.add(new_source)
            db.flush()
            sourceIds.append(new_source.id)
    
    return sourceIds

def get_source_by_url(db: Session, url: str):
    return db.query(models.Source).filter(models.Source.url == url).first()

def get_source_by_id(db: Session, source_id: int):
    return db.query(models.Source).filter(models.Source.id == source_id).first()

# -----------------
# TAG FUNCTIONS
# -----------------
def get_or_create_tags_bulk(db: Session, tag_names: list[str]):
    """
    Take in a list of tag names,
    return a list of Tag objects, creating any that don't already exist.
    """
    # Query for tags that already exist
    existing_tags = db.query(models.Tag).filter(models.Tag.name.in_(tag_names)).all()
    existing_tag_names = {tag.name: tag.id for tag in existing_tags}

    tagIds = []
        
    for name in tag_names:
        if name in existing_tag_names:
            tagIds.append(existing_tag_names[name])
        else:
            new_tag = models.Tag(name=name)
            db.add(new_tag)
            db.flush()
            tagIds.append(new_tag.id)
    
    return tagIds

# -----------------
# ARTICLE FUNCTIONS
# -----------------
def create_article_with_sources_and_tags(db: Session, title: str, content: str, sources: list[dict], tags: list[str] = None):
    article = create_article(db=db, title=title, content=content)

    # Get or create all the sources and get their IDs
    # This step will eliminate duplicates added to the db
    sourcesIds = get_or_create_sources_bulk(db=db, sources=sources)
    tagIds = get_or_create_tags_bulk(db=db, tag_names=tags) if tags else []

    # Link sources to the article
    # Extract article_id as int to satisfy type checker
    for source_id in sourcesIds:
        link_article_to_source(db=db, article_id=cast(int, article.id), source_id=source_id)

    for tag_id in tagIds:
        link_article_to_tag(db=db, article_id=cast(int, article.id), tag_id=tag_id)

    return article

def create_article(db: Session, title: str, content: str):
    article = models.Article(title=title, content=content)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_article_by_id(db: Session, article_id: int): 
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    return article

def get_all_articles(db: Session, search: str = None):
    if search:
        search_pattern = f"%{search}%"
        return db.query(models.Article).filter(
            (models.Article.title.ilike(search_pattern))
        ).all()
    return db.query(models.Article).order_by(models.Article.created_at.desc()).all()

def update_article_impact_score(db: Session, article_id: int, impact_score: int):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        return None
    article.impact_score = cast(int, impact_score)
    db.commit()
    db.refresh(article)
    return article

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

def link_article_to_tag(db: Session, article_id: int, tag_id: int):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not article or not tag:
        return None

    if tag not in article.tags:
        article.tags.append(tag)
        db.commit()
        db.refresh(article)
    
    return article