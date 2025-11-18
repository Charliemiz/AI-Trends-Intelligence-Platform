"""
Session management for chat interactions tied to articles.
Each article creates a new session with its own chat history.
"""

from typing import Optional
from datetime import datetime
import uuid

# In-memory session storage
# Format: { session_id: { "article_id": int, "messages": [...], "created_at": datetime } }
SESSIONS = {}

def create_session(article_id: int) -> str:
    """Create a new session for an article. Accepts optional context."""
    return _create_session_with_context(article_id)

def _create_session_with_context(article_id: int, article_title: str = None, article_content: str = None, sources: list = None) -> str:
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "article_id": article_id,
        "article_title": article_title,
        "messages": [],
        "created_at": datetime.now(),
        "article_content": article_content,
        "sources": sources or [],
    }
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """Get session data by ID."""
    return SESSIONS.get(session_id)

def add_message_to_session(session_id: str, role: str, content: str) -> bool:
    """Add a message to a session's chat history."""
    if session_id not in SESSIONS:
        return False
    
    SESSIONS[session_id]["messages"].append({
        "role": role,
        "content": content,
    })
    return True

def get_session_messages(session_id: str) -> list:
    """Get all messages in a session."""
    session = get_session(session_id)
    return session["messages"] if session else []

def end_session(session_id: str) -> bool:
    """Terminate a session and clean up."""
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        return True
    return False

def get_session_article_id(session_id: str) -> Optional[int]:
    """Get the article ID associated with a session."""
    session = get_session(session_id)
    return session["article_id"] if session else None