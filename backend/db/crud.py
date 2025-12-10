"""CRUD helpers for database models.

This module contains convenience functions to create, read, update and link
database objects used by the application (articles, sources, tags). Functions
are small wrappers around SQLAlchemy sessions and preserve existing behaviour.

Design goals:
- Provide clear, well-documented helper functions used by higher-level
    services and cron jobs.
- Keep SQLAlchemy session usage explicit via the `db: Session` parameter.
"""

from typing import cast
from sqlalchemy.orm import Session
from backend.db import models

def get_or_create_sources_bulk(db: Session, sources: list[dict]):
    """Bulk get or create sources from a list of source dicts.

    :param db: Active SQLAlchemy ``Session``.
    :param sources: List of dicts with keys 'title', 'url', 'domain', 'sector'.
    :returns: List of source IDs (int) for the sources created or found.
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
    """Return a :class:`models.Source` matching ``url``, or ``None``.

    :param db: Active SQLAlchemy ``Session``.
    :param url: The source URL to look up.
    :returns: The matching :class:`models.Source` instance or ``None`` if not found.
    """
    return db.query(models.Source).filter(models.Source.url == url).first()

def get_source_by_id(db: Session, source_id: int):
    """Return a :class:`models.Source` by its integer id, or ``None``.

    :param db: Active SQLAlchemy ``Session``.
    :param source_id: Primary key of the source to retrieve.
    :returns: The matching :class:`models.Source` instance or ``None``.
    """
    return db.query(models.Source).filter(models.Source.id == source_id).first()

def get_or_create_tags_bulk(db: Session, tags: list[str]):
    """Bulk get or create tags from a list of tag names.

    :param db: Active SQLAlchemy ``Session``.
    :param tags: List of tag name strings.
    :returns: List of tag IDs (int) for the tags created or found.
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

def create_article_with_sources_and_tags(db: Session, title: str, content: str, sources: list[dict], tags: list[str], impact_score: int = -1, sector: str = "General"):
    """Create an article and link it to sources and tags in one transaction.

    :param db: Active SQLAlchemy ``Session``.
    :param title: Article title.
    :param content: Article body/content.
    :param sources: List of source dicts to link.
    :param tags: List of tag names to link.
    :param impact_score: Integer impact score (default ``-1`` when unknown).
    :returns: The newly created :class:`models.Article` instance.
    """
    article = create_article(db=db, title=title, content=content, impact_score=impact_score, sector=sector)
    sourceIDs = get_or_create_sources_bulk(db=db, sources=sources)
    tagIDs = get_or_create_tags_bulk(db=db, tags=tags)

    for source_id in sourceIDs:
        link_article_to_source(db=db, article_id=cast(int, article.id), source_id=source_id)

    for tag_id in tagIDs:
        link_article_to_tag(db=db, article_id=cast(int, article.id), tag_id=tag_id)

    return article

def create_article(db: Session, title: str, content: str, impact_score: int = -1, sector: str = "General"):
    """Create and persist an :class:`models.Article`.

    The function commits the transaction and refreshes the returned instance.

    :param db: Active SQLAlchemy ``Session``.
    :param title: Article title.
    :param content: Article body/content.
    :param impact_score: Integer impact score (default ``-1`` when unknown).
    :returns: The newly created and refreshed :class:`models.Article` instance.
    """
    article = models.Article(title=title, content=content, impact_score=impact_score, sector=sector)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_article_by_id(db: Session, article_id: int): 
    """Return an :class:`models.Article` by id or ``None``.

    :param db: Active SQLAlchemy ``Session``.
    :param article_id: Primary key of the article to retrieve.
    :returns: The matching :class:`models.Article` or ``None``.
    """
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    return article

def get_all_articles(db: Session, search: str | None = None, limit: int = 20, offset: int = 0):
    """Get paginated articles, optionally filtered by search query.

    :param db: Active SQLAlchemy ``Session``.
    :param search: Optional search string to filter articles by title.
    :param limit: Maximum number of articles to return (default 20).
    :param offset: Number of articles to skip (pagination offset).
    :returns: Tuple of ``(articles_list, total_count)``.
    """
    query = db.query(models.Article)
    
    if search:
        query = query.filter(models.Article.title.ilike(f"%{search}%") | models.Article.tags.any(models.Tag.name.ilike(f"%{search}%")))
    
    # Get total count before applying limit/offset
    total_count = query.count()
    
    # Apply ordering and pagination
    articles = query.order_by(models.Article.created_at.desc()).limit(limit).offset(offset).all()
    
    return articles, total_count

def link_article_to_source(db: Session, article_id: int, source_id: int):
    """Associate a source with an article (many-to-many).

    If either the article or source cannot be found, returns ``None``.

    :param db: Active SQLAlchemy ``Session``.
    :param article_id: ID of the article to link.
    :param source_id: ID of the source to link.
    :returns: Updated :class:`models.Article` instance after linking, or ``None``.
    """
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
    """Associate a tag with an article (many-to-many).

    If either the article or tag cannot be found, returns ``None``.

    :param db: Active SQLAlchemy ``Session``.
    :param article_id: ID of the article to link.
    :param tag_id: ID of the tag to link.
    :returns: Updated :class:`models.Article` instance after linking, or ``None``.
    """
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not article or not tag:
        return None

    if tag not in article.tags:
        article.tags.append(tag)
        db.commit()
        db.refresh(article)
    
    return article