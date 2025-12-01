from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.crud import get_all_articles, get_article_by_id
from backend.db.schemas import ArticleSchema, ArticleListSchema, ChatMessage, SessionCreateRequest, SessionResponse, ChatRequest, ChatResponse
from backend.services.openai_service import openai_chat_service
from backend.services.session_service import (
    create_session_with_context, get_session, add_message_to_session,
    get_session_messages, end_session, get_session_article_id
)
import logging
from typing import Optional
from fastapi import Query
from backend.services.perplexity_service import perplexity_search_simple

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# get routes (webpages)

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@router.get("/articles", response_model=list[ArticleListSchema])
def get_articles(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None)):
    try:
        if search:
            logger.info(f"Searching articles with query: {search}")
            articles = get_all_articles(db, search=search)
            logger.info(f"Found {len(articles)} articles matching search query")
            return articles
        else:
            articles = get_all_articles(db)
        logger.info(f"Successfully returned {len(articles)} articles")
        return articles
    except Exception as e:
        logger.error(f"Error in get_articles: {e}", exc_info=True)
        raise

@router.get("/articles/{article_id}", response_model=ArticleSchema)
def get_article(article_id: int, db: Session = Depends(get_db)):
    try:
        return get_article_by_id(db, article_id)
    except Exception as e:
        logger.error(f"Error in get_article: {e}", exc_info=True)
        raise

# post routes (chat interactions)

@router.post("/chat")
async def chat_with_analyst(data: ChatMessage):
    return openai_chat_service(data=data)

@router.post("/chat/session", response_model=SessionResponse)
def create_chat_session(request: SessionCreateRequest):
    """Create a new chat session for an article, with context."""
    try:
        session_id = create_session_with_context(
            article_id=request.article_id,
            article_title=request.article_title,
            article_content=request.article_content,
            sources=request.sources
        )
        logger.info(f"Created session {session_id} for article {request.article_id}")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise


@router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message in a chat session."""
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
        response = openai_chat_service(
            message=request.message,
            conversation_history=messages,
            article_id=article_id,
            session_id=request.session_id
        )
        
        # Ensure response is a string
        response_text = response if isinstance(response, str) else str(response)
        
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
    """Close a chat session and clean up."""
    try:
        if end_session(session_id):
            logger.info(f"Closed session {session_id}")
            return {"message": "Session closed"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error closing session: {e}", exc_info=True)
        raise

@router.get("/perplexity/test")
def perplexity_test():
    test_query = "What are the latest trends in artificial intelligence?"
    result = perplexity_search_simple(test_query)
    return result