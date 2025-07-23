#!/usr/bin/env python3
"""
Minimal API test script for Gemini, Perplexity, Unsplash, and Pexels
"""

import os
import requests
from dotenv import load_dotenv
load_dotenv()

resp = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}", "Content-Type": "application/json"},
    json={"model": "sonar", "messages": [{"role": "user", "content": "Explain drone photography techniques for beginners"}], "max_tokens": 200}
)
print(resp.json()['choices'][0]['message']['content'] if resp.ok else f"Perplexity error: {resp.text}")

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print(genai.GenerativeModel('gemini-pro').generate_content("Write a short paragraph about drone photography").text)
except: print('Gemini failed')

try:
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"},
        params={"query": "hexacopter with remote control", "per_page": 1}
    )
    print(resp.json()['results'][0]['urls']['regular'] if resp.ok and resp.json()['results'] else f"Unsplash error: {resp.text}")
except: print("Unsplash failed")

try:
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": os.getenv('PEXELS_API_KEY')},
        params={"query": "swarm drone", "per_page": 1}
    )
    print(resp.json()['photos'][0]['src']['large2x'] if resp.ok and resp.json()['photos'] else f"Pexels error: {resp.text}")
except: print("Pexels failed")
