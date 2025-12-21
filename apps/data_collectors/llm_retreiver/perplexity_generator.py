import requests
import os
import json
from google import genai
from google.genai import types
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.json_format import ParseDict
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

def _generate_with_perplexity(system_prompt: str, user_prompt: str) -> str:
    if not PERPLEXITY_API_KEY:
        raise ValueError("Set PERPLEXITY_API_KEY environment variable")

    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar-pro",  # or "sonar"
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"]
