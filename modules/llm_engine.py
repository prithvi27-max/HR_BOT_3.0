import requests, json
from config import GROQ_API_KEY

def call_llm(prompt, language="en"):
    system_message = f"Respond in {language}. Be concise and helpful."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    return data["choices"][0]["message"]["content"]
