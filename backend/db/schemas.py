"""Pydantic schemas for API request/response validation.

These models mirror the SQLAlchemy models for use as input/output
models in FastAPI route handlers.
"""

from pydantic import BaseModel
from datetime import datetime

class SourceSchema(BaseModel):
    """Schema representing a source returned in API responses.

    :ivar id: Source id.
    :ivar title: Title of the source.
    :ivar url: Source URL.
    :ivar domain: Domain of the source.
    :ivar sector: Sector classification.
    """
    id: int
    title: str
    url: str
    domain: str
    sector: str

    class Config:
        from_attributes = True

class TagSchema(BaseModel):
    """Schema representing a lightweight tag object.

    :ivar id: Tag id.
    :ivar name: Tag name.
    """
    id: int
    name: str
    
    class Config:
        from_attributes = True

class ArticleSchema(BaseModel):
    """Detailed article schema used for article-detail responses.

    :ivar id: Article id.
    :ivar title: Article title.
    :ivar content: Article content.
    :ivar created_at: Creation timestamp.
    :ivar sources: List of attached sources.
    :ivar tags: List of tags.
    :ivar impact_score: Impact score integer.
    """
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
    """Compact article schema for lists (no sources included).

    :ivar id: Article id.
    :ivar title: Article title.
    :ivar content: Article content (truncated).
    :ivar created_at: Creation timestamp.
    :ivar impact_score: Optional impact score.
    :ivar tags: List of tags.
    """
    id: int
    title: str
    content: str
    created_at: datetime
    impact_score: int | None = None
    tags: list[TagSchema] = []

    class Config:
        from_attributes = True

class PaginatedArticlesResponse(BaseModel):
    """Response model for paginated article lists.

    :ivar items: List of article list entries.
    :ivar total_count: Total number of matching articles.
    :ivar page: Current page number.
    :ivar page_size: Items per page.
    :ivar total_pages: Total pages available.
    """
    items: list[ArticleListSchema]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class SessionCreateRequest(BaseModel):
    """Payload used to create a new chat session with article context.

    :ivar article_id: ID of the article to attach.
    :ivar article_title: Title of the article.
    :ivar article_content: Full article content.
    :ivar sources: List of source dicts attached to the session.
    :ivar tags: List of tag dicts (with id and name) associated with the article.
    :ivar impact_score: Impact score or severity ranking for the article.
    """
    article_id: int
    article_title: str
    article_content: str
    sources: list[dict] = []
    tags: list[dict] = []
    impact_score: int | None = None

class SessionResponse(BaseModel):
    """Response containing the created session identifier and initial messages.

    :ivar session_id: UUID string for the created session.
    :ivar messages: Initial conversation history (includes greeting).
    """
    session_id: str
    messages: list[dict] = []

class ChatRequest(BaseModel):
    """Payload for sending a chat message within a session.

    :ivar session_id: Session UUID to send the message to.
    :ivar message: Message text to send.
    """
    session_id: str
    message: str

class ChatResponse(BaseModel):
    """Response returned after processing a chat request.

    :ivar response: Assistant response text.
    :ivar messages: Conversation history after the request.
    """
    response: str
    messages: list[dict]