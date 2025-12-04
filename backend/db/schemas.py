from pydantic import BaseModel
from datetime import datetime

class SourceSchema(BaseModel):
    """Schema for Source objects in responses."""
    id: int
    title: str
    url: str
    domain: str
    sector: str

    class Config:
        from_attributes = True

class TagSchema(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class ArticleSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    sources: list[SourceSchema] = []
    tags: list[TagSchema] = []
    impact_score: int

    class Config:
        from_attributes = True

class ArticleListSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str

class SessionCreateRequest(BaseModel):
    article_id: int
    article_title: str
    article_content: str
    sources: list[dict] = []

class SessionResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    messages: list[dict]