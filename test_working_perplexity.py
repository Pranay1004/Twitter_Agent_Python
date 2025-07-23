import requests

api_key = "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"

def chat(message):
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "sonar", "messages": [{"role": "user", "content": message}], "max_tokens": 200}
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text[:200]}"

# Test the working pattern
print("Testing your working Perplexity code...")
result = chat("Say hello and confirm you're working!")
print(f"Result: {result}")
