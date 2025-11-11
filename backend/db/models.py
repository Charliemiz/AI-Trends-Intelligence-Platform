from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, TIMESTAMP
from sqlalchemy.orm import relationship
from backend.db.database import Base

source_articles = Table(
    "source_articles",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", Integer, ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    # created_at = Column(TIMESTAMP) # implement later
    
    # Relationship to sources through the junction table
    sources = relationship('Source', secondary=source_articles, back_populates='articles')

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, unique=True, nullable=False)
    domain = Column(String)  # e.g., "example.com"
    sector = Column(String)  # e.g., "Technology", "Government", etc.
    published_at = Column(TIMESTAMP)  # When the source content was published
    scraped_text = Column(Text)  # Full text content from the source
    
    # Relationship to articles through the junction table
    articles = relationship('Article', secondary=source_articles, back_populates='sources')