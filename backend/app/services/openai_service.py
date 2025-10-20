# backend/app/services/openai_service.py
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_articles(articles):
    """Generate one summary from multiple source snippets."""
    context = "\n\n".join([f"{a['title']}: {a['description']}" for a in articles])

    prompt = (
        "You are an AI news analyst. Create a clear, factual summary from the following sources. "
        "Return a headline and a 150-word plain-English explanation."
    )

    messages = [
        {"role": "system", "content": "You summarize AI news for executives."},
        {"role": "user", "content": f"{prompt}\n\n{context}"}
    ]

    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.3)
    text = resp.choices[0].message.content
    return text
