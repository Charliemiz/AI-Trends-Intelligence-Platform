import os, json, sys, datetime
import requests
from dotenv import load_dotenv

PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"

def perplexity_search(query: str, count: int = 5):
    """Call Perplexity API to search and return results with sources."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY. Put it in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a search assistant. Provide recent news and information with sources."
            },
            {
                "role": "user",
                "content": f"Find the top {count} recent news articles about: {query}. For each result, provide: title, source, brief description, and URL if available."
            }
        ]
    }
    
    r = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=30)
    
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        print("Perplexity error:", r.status_code, r.text[:400], file=sys.stderr)
        raise e

    data = r.json()
    
    # Extract the response content
    content = data['choices'][0]['message']['content']
    
    # Extract citations if available
    citations = data.get('citations', [])
    
    return {
        "content": content,
        "citations": citations
    }

def main():
    load_dotenv() 

    q = input("Search query (e.g., renewable energy policy OR grid interconnection rule): ").strip()
    if not q:
        q = "renewable energy policy"

    result = perplexity_search(q, count=5)

    if not result:
        print("No results.")
        return

    output_lines = []
    output_lines.append(f"Search results for: {q}\n")
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
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"perplexity_results_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_output)
    
    print(f"\n✓ Results saved to: {filename}")

def perplexity_summarize(context: str) -> str:
    """Call Perplexity API to summarize the given text."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY. Put it in .env")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": f"Summarize this in 3 bullets:\n\n{context}"
            }
        ]
    }

    resp = requests.post(PERPLEXITY_ENDPOINT, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    
    data = resp.json()
    summary = data['choices'][0]['message']['content']
    
    return summary

if __name__ == "__main__":
    main()