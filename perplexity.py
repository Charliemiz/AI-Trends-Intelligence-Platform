import requests
import os

def main():
    API_KEY = os.getenv("PERPLEXITY_API_KEY")
    # Set up the API endpoint and headers
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",  # Replace with your actual API key
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": "What were the results of the 2025 French Open Finals?"}
        ]
    }

    # Make the POST request to the Perplexity API
    response = requests.post(url, headers=headers, json=payload)
    print(response.json()["choices"][0]['message']['content'])

if __name__ == "__main__":
    main()