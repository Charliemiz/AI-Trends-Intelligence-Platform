from pydantic import BaseModel

class SourceSchema(BaseModel):
    """Schema for Source objects in responses."""
    id: int
    title: str
    url: str
    domain: str | None = None
    sector: str | None = None

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy ORM objects

class ArticleSchema(BaseModel):
    """Schema for Article objects in responses, including related sources."""
    id: int
    title: str
    content: str
    sources: list[SourceSchema] = []

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy ORM objects

class ArticleListSchema(BaseModel):
    """Schema for a list of articles (without detailed sources)."""
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True
