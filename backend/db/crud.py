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
    sourceIDs: list[int] = []
        
    for source in sources:
        if source["url"] in existing_urls:
            sourceIDs.append(cast(int, existing_urls[source["url"]]))
        else:
            new_source = models.Source(title=source["title"], url=source["url"], domain=source["domain"], sector=source["sector"])
            db.add(new_source)
            db.flush()
            sourceIDs.append(cast(int, new_source.id))
    
    return sourceIDs

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
    sourceIDs = get_or_create_sources_bulk(db=db, sources=sources)
    tagIDs = get_or_create_tags_bulk(db=db, tags=tags)

    for source_id, index in enumerate(sourceIDs):
        # insert article citation updates here
        update_article_citation_numbering(db=db, article_id=cast(int, article.id), source_id=source_id, citation_number=index)
        link_article_to_source(db=db, article_id=cast(int, article.id), source_id=source_id)

    for tag_id in tagIDs:
        link_article_to_tag(db=db, article_id=cast(int, article.id), tag_id=tag_id)

    return article

def create_article(db: Session, title: str, content: str, impact_score: int = -1):
    article = models.Article(title=title, content=content, impact_score=impact_score)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def update_article_citation_numbering(db: Session, article_id: int, source_id: int, citation_number: int):
    # plan here: open article, regex find citation number, replace with source_id, update article
    return

def get_article_by_id(db: Session, article_id: int): 
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    return article

def get_all_articles(db: Session, search: str | None = None, limit: int = 20, offset: int = 0):
    """
    Get paginated articles, optionally filtered by search query.
    Returns a tuple of (articles, total_count)
    """
    query = db.query(models.Article)
    
    if search:
        query = query.filter(models.Article.title.ilike(f"%{search}%"))
    
    # Get total count before applying limit/offset
    total_count = query.count()
    
    # Apply ordering and pagination
    articles = query.order_by(models.Article.created_at.desc()).limit(limit).offset(offset).all()
    
    return articles, total_count

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