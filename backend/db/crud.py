# in case you forget: create, read, update, delete (CRUD)
from typing import cast
from sqlalchemy.orm import Session
from backend.db import models

def get_or_create_sources_bulk(db: Session, sources: list[dict]):
    """
    Take in a list of dictionaries with 'title' and 'url' keys,
    return a list of Source objects, creating any that don't already exist.
    """
    urls = [s["url"] for s in sources]
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

def get_or_create_tags_bulk(db: Session, tags: list[str]):
    """
    Take in a list of tag names,
    return a list of Tag objects, creating any that don't already exist.
    """
    existing_tags = {cast(str, tag.name): cast(int, tag.id) for tag in db.query(models.Tag).filter(models.Tag.name.in_(tags)).all()}
    tagIDs: list[int] = []
        
    for name in tags:
        if name in existing_tags.keys():
            tagIDs.append(existing_tags[name])
        else:
            new_tag = models.Tag(name=name)
            db.add(new_tag)
            db.flush()
            tagIDs.append(cast(int, new_tag.id))
    
    return tagIDs

def create_article_with_sources_and_tags(db: Session, title: str, content: str, sources: list[dict], tags: list[str], impact_score: int = -1):
    article = create_article(db=db, title=title, content=content, impact_score=impact_score)
    sourcesIds = get_or_create_sources_bulk(db=db, sources=sources)
    tagIds = get_or_create_tags_bulk(db=db, tags=tags)

    for source_id in sourcesIds:
        link_article_to_source(db=db, article_id=cast(int, article.id), source_id=source_id)

    for tag_id in tagIds:
        link_article_to_tag(db=db, article_id=cast(int, article.id), tag_id=tag_id)

    return article

def create_article(db: Session, title: str, content: str, impact_score: int = -1):
    article = models.Article(title=title, content=content, impact_score=impact_score)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_article_by_id(db: Session, article_id: int): 
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    return article

def get_all_articles(db: Session, search: str | None = None):
    if search:
        return db.query(models.Article).filter((models.Article.title.ilike(f"%{search}%"))).all()
    return db.query(models.Article).order_by(models.Article.created_at.desc()).all()

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