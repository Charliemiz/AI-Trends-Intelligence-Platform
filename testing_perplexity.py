import json, sys, datetime
from dotenv import load_dotenv
from supabase_functionality import *
from perplexity_functions import *

def main():
    load_dotenv()
    
    # Initialize Supabase client
    supabase = get_supabase_client()
    
    # Get topic category
    topic = input("Topic category (e.g., tech, medical, finance): ").strip()
    if not topic:
        topic = "other"
    
    # Get search query
    query = input("Search query (e.g., renewable energy policy): ").strip()
    if not query:
        query = "MISC"

    result = perplexity_search(query, count=5)

    if not result:
        print("No results.")
        return

    output_lines = []
    output_lines.append(f"Topic: {topic}\n")
    output_lines.append(f"Search results for: {query}\n")
    output_lines.append("=" * 60 + "\n")
    output_lines.append(result["content"])
    
    if result["citations"]:
        output_lines.append("\n\n--- Sources ---\n")
        for i, citation in enumerate(result["citations"], 1):
            output_lines.append(f"{i}. {citation}\n")
    
    summary = perplexity_summarize(result["content"])
    
    output_lines.append("\n\n--- Summary ---\n")
    output_lines.append(summary)
    
    full_output = "".join(output_lines)
    
    print("\n" + full_output)
    
    # Save to database
    try:
        query_id = save_to_database(
            supabase=supabase,
            topic_name=topic,
            query_text=query,
            content=result["content"],
            citations=result["citations"],
            summary=summary
        )
    except Exception as e:
        print(f"Error saving to database: {e}", file=sys.stderr)
    
    # Text files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"perplexity_results_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_output)
    
    print(f"✓ Results saved to: {filename}")

if __name__ == "__main__":
    main()