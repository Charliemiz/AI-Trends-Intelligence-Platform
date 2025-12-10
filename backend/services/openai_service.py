"""OpenAI integration helpers.

Provides a thin wrapper around the OpenAI client used to generate
assistant responses in the context of article-based conversations.
The service maintains session state and conversation history for
multi-turn dialogues.

Functions
---------
openai_chat_service
    Primary entrypoint used by routes to request an assistant response.
"""

from openai import OpenAI
from typing import Optional

from backend.config import settings
from backend.services.session_service import get_session

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def openai_chat_service(
    message: Optional[str] = None,
    conversation_history: Optional[list] = None,
    article_id: Optional[int] = None,
    session_id: Optional[str] = None,
):
    """Generate an AI response using OpenAI's chat completion API.

    Builds a system prompt with article context (title, content, tags, impact score,
    and sources) retrieved from the session store. Appends conversation history and
    the current user message, then sends to GPT-4o-mini for response generation.

    :param message: The user's message or question (required).
    :type message: str or None
    :param conversation_history: List of prior message dicts with 'role' and 'content' keys.
    :type conversation_history: list or None
    :param article_id: (Optional) Legacy article ID parameter; ignored if session_id is provided.
    :type article_id: int or None
    :param session_id: Unique session identifier to retrieve article context and conversation state.
    :type session_id: str or None
    :returns: Dict with key 'response' containing the AI-generated answer as a string.
    :rtype: dict
    :raises ValueError: If message parameter is not provided.
    """

    if message is not None:
        # Build messages array with conversation history
        messages = []

        # Build system prompt with article context
        system_prompt = (
            "You are a helpful analyst assistant discussing the provided article. "
            "Your primary focus is answering questions about the article's content, themes, and related topics. "
            "You can help clarify terms, concepts, and provide context related to the article. "
            "If a user asks a question completely unrelated to the article or its themes, "
            "politely guide them back to the article topic. Return your answers unformatted in plaintext."
        )

        if session_id:
            session = get_session(session_id)
            if session:
                article_title = session.get("article_title")
                article_content = session.get("article_content")
                sources = session.get("sources", [])
                tags = session.get("tags", [])
                impact_score = session.get("impact_score")

                # Append article context to system prompt
                if article_title:
                    system_prompt += f"\n\nArticle Title: {article_title}"
                if impact_score is not None:
                    system_prompt += f"\nImpact Score: {impact_score}"
                if tags:
                    tag_names = [t.get("name", "") for t in tags]
                    system_prompt += f"\nTags: {', '.join(tag_names)}"
                if article_content:
                    system_prompt += f"\n\nArticle Content:\n{article_content}"
                if sources:
                    system_prompt += "\n\nSources:\n"
                    for s in sources:
                        system_prompt += f"- {s.get('title', '')} ({s.get('url', '')})\n"
        elif article_id:
            system_prompt += f"\nYou are discussing an article (ID: {article_id}). Use the conversation context to provide relevant insights."

        messages.append({"role": "system", "content": system_prompt})

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
        # Normalize return shape to a dict for consistency across callers
        return {"response": answer}
    else:
        raise ValueError("message parameter is required for openai_chat_service")