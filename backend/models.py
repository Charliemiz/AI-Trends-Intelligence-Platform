from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session
from backend.database import Base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    
    # Relationship to sources through the junction table
    sources = relationship(
        'Source',
        secondary='source_articles',
        back_populates='articles'
    )

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    
    # Relationship to articles through the junction table
    articles = relationship(
        'Article',
        secondary='source_articles',
        back_populates='sources'
    )

class SourceArticle(Base):
    __tablename__ = 'source_articles'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    source_id = Column(Integer, ForeignKey('sources.id'))