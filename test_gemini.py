import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

for model in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Hello"}]}]
    }
    r = requests.post(url, json=payload)
    print(f"Model {model}: status={r.status_code}")
    if r.status_code == 200:
        print("Response sample:", r.json()['candidates'][0]['content']['parts'][0]['text'][:100])
