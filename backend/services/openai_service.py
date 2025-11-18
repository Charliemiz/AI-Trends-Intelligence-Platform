from openai import OpenAI
from backend.config import settings
from typing import Optional, Union
from backend.db.schemas import ChatMessage

client = OpenAI(api_key=settings.OPENAI_API_KEY)

from backend.services.session_service import get_session

def openai_chat_service(
    data: Optional[ChatMessage] = None,
    message: Optional[str] = None,
    conversation_history: Optional[list] = None,
    article_id: Optional[int] = None,
    session_id: Optional[str] = None
):
    """
    Receives a message and returns an OpenAI response.
    
    Can be called in two ways:
    1. Legacy: openai_chat_service(data=ChatMessage) - returns dict
    2. Session-based: openai_chat_service(message=str, conversation_history=list, article_id=int) - returns str
    """
    
    # Legacy mode for backward compatibility
    if data is not None:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an economic analyst providing clear, concise explanations."},
                {"role": "user", "content": data.message},
            ],
        )
        answer = response.choices[0].message.content
        return {"response": answer}
    
    # Session-based mode with conversation history
    if message is not None:
        # Build messages array with conversation history
        messages = []

        # Add system message with context if available
        system_content = "You are an economic analyst providing clear, concise explanations."
        context_str = ""
        if session_id:
            session = get_session(session_id)
            if session:
                article_content = session.get("article_content")
                sources = session.get("sources", [])
                # Try to get the article title from the first source or from a new session key if available
                article_title = None
                # If the frontend sends the title as part of sources[0], use it
                if sources and sources[0].get('article_title'):
                    article_title = sources[0]['article_title']
                # Or, if the session has a 'article_title' key (future-proof)
                if session.get('article_title'):
                    article_title = session['article_title']
                # Or, try to get it from the content (not ideal)
                # If the frontend sends the title as a separate field, prefer that
                if session.get('article_title'):
                    article_title = session['article_title']
                # Compose context string
                if article_title:
                    context_str += f"\n\nArticle Title: {article_title}"
                if article_content:
                    context_str += f"\n\nArticle Content:\n{article_content}"
                if sources:
                    context_str += "\n\nSources:\n"
                    for s in sources:
                        context_str += f"- {s.get('title', '')} ({s.get('url', '')})\n"
        elif article_id:
            system_content += f"\nYou are discussing an article (ID: {article_id}). Use the conversation context to provide relevant insights."

        if context_str:
            system_content += f"\n{context_str}"

        messages.append({"role": "system", "content": system_content})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        answer = response.choices[0].message.content
        return answer
    
    raise ValueError("Either 'data' (ChatMessage) or 'message' (str) parameter is required")