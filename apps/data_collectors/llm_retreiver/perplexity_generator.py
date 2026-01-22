import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

def _generate_with_perplexity(system_prompt: str, user_prompt: str, response_model: dict = None) -> str:
    if not PERPLEXITY_API_KEY:
        raise ValueError("Set PERPLEXITY_API_KEY environment variable")

    client = OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )

    kwargs = {
        "model": "sonar", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }

    if response_model:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "schema": response_model
            }
        }

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
