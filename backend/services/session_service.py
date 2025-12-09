"""Session management for chat interactions tied to articles.

This module provides in-memory session storage for article-based chat
conversations. Each session maintains article context (title, content,
sources, tags, impact score) and conversation history. Sessions are
identified by UUID and persist until explicitly closed.

Functions
---------
create_session_with_context
    Create a new chat session with article context and initial greeting.
get_session
    Retrieve session data by session ID.
add_message_to_session
    Append a message to a session's conversation history.
get_session_messages
    Get all messages in a session's conversation history.
end_session
    Terminate and clean up a session.
get_session_article_id
    Get the article ID associated with a session.
"""

from typing import Optional
from datetime import datetime
import uuid

# In-memory session storage
# Format: { session_id: { "article_id": int, "messages": [...], "created_at": datetime } }
SESSIONS = {}

def create_session_with_context(article_id: int, article_title: str, article_content: str, sources: list, tags: list | None = None, impact_score: int | None = None) -> str:
    """Create a new chat session tied to an article with conversational context.

    Creates a session with an initial greeting message and stores all article
    metadata (title, content, sources, tags, impact score) for use in AI
    conversation context. The greeting is added to the message history so
    it's included in conversation context sent to the AI model.

    :param article_id: ID of the article this session is bound to.
    :type article_id: int
    :param article_title: Title of the article.
    :type article_title: str
    :param article_content: Full content of the article.
    :type article_content: str
    :param sources: List of source dicts associated with the article.
    :type sources: list
    :param tags: List of tag dicts (with id and name) associated with the article.
    :type tags: list or None
    :param impact_score: Impact score or severity ranking for the article.
    :type impact_score: int or None
    :returns: UUID string identifier for the new session.
    :rtype: str
    """
    session_id = str(uuid.uuid4())
    
    # Create initial greeting message
    greeting = f'Hello! I\'m here to answer any questions you may have about this article, "{article_title}".'
    
    SESSIONS[session_id] = {
        "article_id": article_id,
        "article_title": article_title,
        "messages": [
            {"role": "assistant", "content": greeting}
        ],
        "created_at": datetime.now(),
        "article_content": article_content,
        "sources": sources or [],
        "tags": tags or [],
        "impact_score": impact_score,
    }
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """Get session data by ID.

    :param session_id: UUID of the session to retrieve.
    :returns: Session dict with context and messages, or ``None`` if not found.
    """
    return SESSIONS.get(session_id)

def add_message_to_session(session_id: str, role: str, content: str) -> bool:
    """Add a message to a session's chat history.

    :param session_id: UUID of the session to add the message to.
    :param role: Message role, typically 'user' or 'assistant'.
    :param content: Message content/text.
    :returns: True if message was added, False if session not found.
    """
    if session_id not in SESSIONS:
        return False
    
    SESSIONS[session_id]["messages"].append({
        "role": role,
        "content": content,
    })
    return True

def get_session_messages(session_id: str) -> list:
    """Get all messages in a session.

    :param session_id: UUID of the session.
    :returns: List of message dicts with 'role' and 'content' keys, or empty list if session not found.
    """
    session = get_session(session_id)
    return session["messages"] if session else []

def end_session(session_id: str) -> bool:
    """Terminate a session and clean up.

    :param session_id: UUID of the session to terminate.
    :returns: True if session was closed, False if session not found.
    """
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        return True
    return False

def get_session_article_id(session_id: str) -> Optional[int]:
    """Get the article ID associated with a session.

    :param session_id: UUID of the session.
    :returns: The article ID bound to the session, or ``None`` if session not found.
    """
    session = get_session(session_id)
    return session["article_id"] if session else None