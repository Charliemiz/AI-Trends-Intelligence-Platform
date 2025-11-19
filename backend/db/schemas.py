from pydantic import BaseModel

class SourceSchema(BaseModel):
    """Schema for Source objects in responses."""
    id: int
    title: str
    url: str
    domain: str
    sector: str

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy ORM objects

class ArticleSchema(BaseModel):
    """Schema for Article objects in responses, including related sources."""
    id: int
    title: str
    content: str
    created_at: str
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

class ChatMessage(BaseModel):
    message: str

class SessionCreateRequest(BaseModel):
    """Request to create a new chat session for an article, with context."""
    article_id: int
    article_title: str
    article_content: str
    sources: list[dict] = []

class SessionResponse(BaseModel):
    """Response containing session ID."""
    session_id: str

class ChatRequest(BaseModel):
    """Request to send a message in a session."""
    session_id: str
    message: str

class ChatResponse(BaseModel):
    """Response from the AI analyst."""
    response: str
    messages: list[dict]