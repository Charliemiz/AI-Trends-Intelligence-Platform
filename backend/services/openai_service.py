from openai import OpenAI
from backend.config import settings
from typing import Optional, Union
from backend.db.schemas import ChatMessage

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def openai_chat_service(
    data: Optional[ChatMessage] = None,
    message: Optional[str] = None,
    conversation_history: Optional[list] = None,
    article_id: Optional[int] = None
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
        
        # Add system message
        system_content = "You are an economic analyst providing clear, concise explanations."
        if article_id:
            system_content += f"\nYou are discussing an article (ID: {article_id}). Use the conversation context to provide relevant insights."
        
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