from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, TIMESTAMP
from sqlalchemy.orm import relationship
from backend.db.database import Base

source_articles = Table(
    "source_articles",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", Integer, ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)
    
    # Relationship to sources through the junction table
    sources = relationship('Source', secondary=source_articles, back_populates='articles')

    # Relatinship to tags (many-to-many)
    tags = relationship('Tag', secondary='article_tags', back_populates='articles')

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)  
    url = Column(String, unique=True, nullable=False)
    domain = Column(String)  
    sector = Column(String)  
    
    # Relationship to articles through the junction table
    articles = relationship('Article', secondary=source_articles, back_populates='sources')

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # Relationship to articles through the junction table
    articles = relationship('Article', secondary='article_tags', back_populates='tags')