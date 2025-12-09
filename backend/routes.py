"""API route definitions for the backend.

This module defines HTTP endpoints used by the frontend and internal jobs.
Routes return Pydantic response models when appropriate and perform
dependency injection for database sessions.

Endpoints
---------
get_articles
    Return a paginated list of articles.
get_article
    Return a single article by id.
chat_with_analyst
    Legacy chat endpoint.
create_chat_session
    Create a chat session for an article with context.
send_message
    Send a message in a chat session and return assistant response.
close_chat_session
    Close and cleanup a chat session.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.crud import get_all_articles, get_article_by_id
from backend.db.schemas import (
    ArticleSchema, SessionCreateRequest, SessionResponse,
    ChatRequest, ChatResponse, PaginatedArticlesResponse
)
from backend.services.openai_service import openai_chat_service
from backend.services.session_service import (
    create_session_with_context, get_session, add_message_to_session,
    get_session_messages, end_session, get_session_article_id
)
import logging
from typing import Optional
from fastapi import Query

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/articles", response_model=PaginatedArticlesResponse)
def get_articles(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)):
    """Retrieve a paginated list of articles, optionally filtered by search.

    :param db: Injected database session.
    :param search: Optional search string to filter articles by title.
    :param page: Page number (1-indexed, default 1).
    :param page_size: Number of articles per page (default 20, max 100).
    :returns: Paginated articles response with metadata.
    :raises: Exception on database or processing errors.
    """
    try:
        offset = (page - 1) * page_size
        
        if search:
            logger.info(f"Searching articles with query: {search}, page: {page}, size: {page_size}")
        else:
            logger.info(f"Fetching articles - page: {page}, size: {page_size}")
        
        articles, total_count = get_all_articles(db, search=search, limit=page_size, offset=offset)
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        
        logger.info(f"Returned {len(articles)} articles ({total_count} total)")
        return {
            "items": articles,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error in get_articles: {e}", exc_info=True)
        raise

@router.get("/articles/{article_id}", response_model=ArticleSchema)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Retrieve a single article by id with all associated sources and tags.

    :param article_id: The ID of the article to retrieve.
    :param db: Injected database session.
    :returns: Full article details including sources and tags.
    :raises: Exception on database or processing errors.
    """
    try:
        return get_article_by_id(db, article_id)
    except Exception as e:
        logger.error(f"Error in get_article: {e}", exc_info=True)
        raise

@router.post("/chat/session", response_model=SessionResponse)
def create_chat_session(request: SessionCreateRequest):
    """Create a new chat session for an article with context.

    Initializes a server-side session storing article metadata (title, content,
    sources, tags, impact score) and creates an initial greeting message. Returns
    the session ID and initial message history for the frontend to display.

    :param request: Session creation request containing article metadata.
    :type request: SessionCreateRequest
    :returns: Session response with the newly created session ID and initial messages.
    :rtype: SessionResponse
    :raises: Exception on session creation or processing errors.
    """
    try:
        session_id = create_session_with_context(
            article_id=request.article_id,
            article_title=request.article_title,
            article_content=request.article_content,
            sources=request.sources,
            tags=request.tags,
            impact_score=request.impact_score
        )
        logger.info(f"Created session {session_id} for article {request.article_id}")
        
        # Get initial messages (includes greeting)
        initial_messages = get_session_messages(session_id)
        
        return {
            "session_id": session_id,
            "messages": initial_messages
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise


@router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message in an active chat session and receive an AI response.

    :param request: Chat request containing session ID and user message.
    :type request: ChatRequest
    :returns: Chat response with the assistant's reply and updated message history.
    :rtype: ChatResponse
    :raises: HTTPException with 404 if session not found, or Exception on processing errors.
    """
    try:
        # Validate session exists
        session = get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        article_id = get_session_article_id(request.session_id)
        
        # Add user message to history
        add_message_to_session(request.session_id, "user", request.message)
        
        # Get all messages in session for context
        messages = get_session_messages(request.session_id)
        
        # Call OpenAI with full conversation history
        response_obj = openai_chat_service(
            message=request.message,
            conversation_history=messages,
            article_id=article_id,
            session_id=request.session_id
        )

        # Normalize the response object to a text string. openai_chat_service
        # now returns {'response': str} for session mode; keep fallback for
        # unexpected types.
        if isinstance(response_obj, dict):
            response_text = response_obj.get("response", "")
        else:
            response_text = str(response_obj)
        
        # Add assistant response to history
        add_message_to_session(request.session_id, "assistant", response_text)
        
        # Return response and updated history
        updated_messages = get_session_messages(request.session_id)
        return {
            "response": response_text,
            "messages": updated_messages
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise


@router.delete("/chat/session/{session_id}")
def close_chat_session(session_id: str):
    """Close an active chat session and remove cached data.

    :param session_id: The unique identifier of the chat session to close.
    :type session_id: str
    :returns: Confirmation message indicating successful session closure.
    :rtype: dict
    :raises: HTTPException with 404 if session not found, or Exception on cleanup errors.
    """
    try:
        if end_session(session_id):
            logger.info(f"Closed session {session_id}")
            return {"message": "Session closed"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error closing session: {e}", exc_info=True)
        raise