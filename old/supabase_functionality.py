from supabase import create_client, Client
from dotenv import load_dotenv
import os

def get_supabase_client() -> Client:
    """Initialize Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    
    return create_client(url, key)

def get_or_create_topic(supabase: Client, topic_name: str) -> int:
    """Get existing topic or create new one, return topic_id."""
    # Try to find existing topic
    result = supabase.table("topics").select("id").eq("name", topic_name).execute()
    
    if result.data:
        return result.data[0]["id"]
    
    # Create new topic
    result = supabase.table("topics").insert({"name": topic_name}).execute()
    return result.data[0]["id"]

def save_to_database(supabase: Client, topic_name: str, query_text: str, 
                     content: str, citations: list, summary: str):
    """Save search results to Supabase database."""
    
    # 1. Get or create topic
    topic_id = get_or_create_topic(supabase, topic_name)
    
    # 2. Create query record
    query_result = supabase.table("queries").insert({
        "topic_id": topic_id,
        "query_text": query_text
    }).execute()
    query_id = query_result.data[0]["id"]
    
    # 3. Create summary record
    summary_result = supabase.table("summaries").insert({
        "query_id": query_id,
        "summary_text": summary,
        "full_content": content,
        "model_used": "sonar-pro"
    }).execute()
    summary_id = summary_result.data[0]["id"]
    
    # 4. Create source records for each citation
    if citations:
        sources_to_insert = []
        for idx, citation in enumerate(citations, 1):
            sources_to_insert.append({
                "summary_id": summary_id,
                "url": citation,
                "source_order": idx
            })
        
        if sources_to_insert:
            supabase.table("sources").insert(sources_to_insert).execute()
    
    print(f"✓ Saved to database: Query ID {query_id}, Summary ID {summary_id}")
    return query_id
