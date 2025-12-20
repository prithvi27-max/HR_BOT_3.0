import requests
import os

def call_llm(prompt, language="en"):
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return f"❌ No GROQ_API_KEY found. Please set it in Streamlit Secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": f"You reply in {language}."},
            {"role": "user", "content": prompt}
        ]
    }

    resp = requests.post(url, headers=headers, json=payload).json()

    # Error handling
    if "error" in resp:
        return f"❌ Groq API Error: {resp['error'].get('message', 'Unknown')}"

    try:
        return resp["choices"][0]["message"]["content"]
    except:
        return f"❌ Unexpected LLM Response: {resp}"
