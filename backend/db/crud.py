from sqlalchemy.orm import Session
from backend.db import models

# because I'm going to forget: create, read, update, delete (CRUD)

# -----------------
# SOURCE FUNCTIONS
# -----------------
def get_or_create_sources_bulk(db: Session, sources_data: list[dict]):
    """
    Take in a list of dictionaries with 'title' and 'url' keys,
    return a list of Source objects, creating any that don't already exist.
    """
    urls = [s["url"] for s in sources_data]

    # Query for sources that already exist
    existing_sources = db.query(models.Source).filter(models.Source.url.in_(urls)).all()
    existing_urls = {source.url: source.id for source in existing_sources}

    sourceIds = []
    new_sources = []  # Collect new sources to add in batch
    
    for source in sources_data:
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
# ARTICLE FUNCTIONS
# -----------------
def create_article_with_sources(db: Session, title: str, content: str, sources_data: list[dict]):
    article = create_article(db=db, title=title, content=content)

    # Get or create all the sources and get their IDs
    # This step will eliminate duplicates added to the db
    sources = get_or_create_sources_bulk(db=db, sources_data=sources_data)

    # Link sources to the article
    for source_id in sources:
        link_article_to_source(db=db, article_id=article.id, source_id=source_id)

    return article

def create_article(db: Session, title: str, content: str):
    art = models.Article(title=title, content=content)
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

def get_article_by_id(db: Session, article_id: int):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()

    result = {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "sources": [
            {
                "id": s.id,
                "title": s.title,
                "url": s.url,
            }
            for s in article.sources
        ],
    }

    return result

def get_all_articles(db: Session):
    return db.query(models.Article).all()

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