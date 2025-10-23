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
