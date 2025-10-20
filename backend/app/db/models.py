from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import Base

article_sources = Table(
    "article_sources",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", Integer, ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)
    summary_model = Column(String, default="gpt-4o-mini")

    sources = relationship("Source", secondary=article_sources, back_populates="articles")


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    domain = Column(Text)
    url = Column(Text, unique=True)
    sector = Column(Text)
    published_at = Column(TIMESTAMP, nullable=True)
    scraped_text = Column(Text, nullable=True)

    articles = relationship("Article", secondary=article_sources, back_populates="sources")
