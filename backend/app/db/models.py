from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.db.database import Base

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    url = Column(String)
    content = Column(Text)
    sector = Column(String)
    published_at = Column(DateTime, default=datetime.now)
    summary = Column(Text, nullable=True)
    impact_score = Column(Float, nullable=True)
    novelty_score = Column(Float, nullable=True)
    cluster_id = Column(Integer, nullable=True)
