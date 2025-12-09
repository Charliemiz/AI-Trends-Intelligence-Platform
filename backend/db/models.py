"""SQLAlchemy ORM models for application data.

Defines the primary tables and association tables used by the system:
- Article, Source, Tag and SystemState plus the many-to-many association
    tables used to link articles to sources and tags.
"""

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
    """Persistent representation of a news/article entry.

    :ivar id: Primary key.
    :ivar title: Short article title.
    :ivar content: Full article body.
    :ivar created_at: Timestamp of creation.
    :ivar impact_score: Integer score for estimated impact.
    """
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)
    impact_score = Column(Integer, default=-1)
    
    sources = relationship('Source', secondary=source_articles, back_populates='articles')
    tags = relationship('Tag', secondary='article_tags', back_populates='articles')

class Source(Base):
    """Represents an origin/source for an article (news site, blog, etc.).

    :ivar id: Primary key.
    :ivar title: Human-readable source title.
    :ivar url: Canonical URL for the source (unique).
    :ivar domain: Extracted domain string.
    :ivar sector: Sector classification for the source.
    """
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)  
    url = Column(String, unique=True, nullable=False)
    domain = Column(String)  
    sector = Column(String)  
    
    articles = relationship('Article', secondary=source_articles, back_populates='sources')

class Tag(Base):
    """Simple tag model used for article categorization.

    :ivar id: Primary key.
    :ivar name: Unique tag name.
    """
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    articles = relationship('Article', secondary='article_tags', back_populates='tags')

class SystemState(Base):
    """Key/value store table for small application state blobs.

    :ivar id: Primary key.
    :ivar key: Unique key used to identify the state record.
    :ivar value: JSON/text value containing state.
    :ivar updated_at: Last updated timestamp.
    """
    __tablename__ = 'sector_state'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)