from db import models
from sqlalchemy.orm import Session

# because I'm going to forget: create, read, update, delete (CRUD)

def save_articles(db: Session, articles: list[dict]):
    print(f"💾 Saving {len(articles)} articles...")
    for art in articles:
        db_article = models.Article(
            title=art["title"],
            url=art["url"],
            content=art["content"],
            sector=art["sector"]
        )
        db.add(db_article)
    db.commit()
