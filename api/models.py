from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    summary = Column(Text)
    source = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
