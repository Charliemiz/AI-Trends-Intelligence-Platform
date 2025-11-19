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
    created_at = Column(TIMESTAMP)
    
    # Relationship to sources through the junction table
    sources = relationship('Source', secondary=source_articles, back_populates='articles')

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)  
    url = Column(String, unique=True, nullable=False)
    domain = Column(String)  
    sector = Column(String)  
    
    # Relationship to articles through the junction table
    articles = relationship('Article', secondary=source_articles, back_populates='sources')