from sqlalchemy.orm import Session
from api.models import Article

def add_article(db: Session, article: Article) -> Article:
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    articles = db.query(Article).offset(skip).limit(limit).all()

    # Format the response to include sources
    result = []
    for article in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "sources": [
                {
                    "id": source.id,
                    "name": source.name,
                    "url": source.url
                }
                for source in article.sources 
            ]
        })
    
    return result

def get_article_by_id(db: Session, article_id: int) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return None

    result = {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "url": s.url,
            }
            for s in article.sources
        ],
    }

    return result