from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional
import yaml
from dotenv import load_dotenv
from google import genai

load_dotenv()

from apps.llm_chat_essentials.settings import (
    YAML_TRIP_INTAKE_SCHEMA_V11,
    YAML_UPDATE_SYSTEM_INSTRUCTIONS,
)


# Initialize the client with your API key
# Get one at: https://aistudio.google.com/
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
def update_trip_state(current_yaml, user_message):
    # Combine your system instructions with the actual data
    prompt = f"Hello, here is the current trip state in YAML format\n\n"
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview", # Use flash for speed/cost in extraction tasks
        contents=prompt
    )
    
    return response

# Example Usage
old_state = "trip: { essentials: { destination: null } }"
new_message = "I want to go to Paris"
updated_yaml = update_trip_state(old_state, new_message)
print(updated_yaml)