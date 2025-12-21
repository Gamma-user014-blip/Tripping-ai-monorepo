import os
import json
from google import genai
from google.genai import types
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.json_format import ParseDict
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GEMINI_API_TOKEN") or os.getenv("GEMINI_API_KEY")
if not TOKEN:
    raise ValueError("Set GEMINI_API_TOKEN or GEMINI_API_KEY environment variable")

CLIENT = genai.Client(api_key=TOKEN)

def _generate_with_gemini(
    system_prompt: str,
    user_prompt: str,
    use_grounding: bool = False,
) -> str:
    tools = []
    if use_grounding:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=tools if tools else None,
        response_mime_type="application/json",
    )

    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=config,
    )

    return response.text
