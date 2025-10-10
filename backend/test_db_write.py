# backend/tests/test_db_write.py
from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()
article = models.Article(
    title="Test Article",
    url="https://example.com",
    content="This is just a test entry.",
    sector="Test",
)
db.add(article)
db.commit()
db.close()
print("✅ Inserted test article")
