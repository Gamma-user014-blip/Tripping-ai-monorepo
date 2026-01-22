from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from fastapi import FastAPI, HTTPException

from apps.llm_chat_essentials.settings import (
    YAML_TRIP_INTAKE_SCHEMA_V11,
    YAML_UPDATE_SYSTEM_INSTRUCTIONS,
)

load_dotenv()
app = FastAPI()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
# -------------------------
# Output cleaning
# -------------------------

_YAML_FENCE_RE = re.compile(r"```(?:yaml|yml)?\s*\n(.*?)\n```", flags=re.DOTALL | re.IGNORECASE)
_YAML_TAG_RE = re.compile(r"<YAML>\s*(.*?)\s*</YAML>", flags=re.DOTALL | re.IGNORECASE)


def extract_yaml_text(s: str) -> str:
    """Extract YAML from common wrappers; otherwise return as-is."""
    if not s:
        return ""
    s = s.strip()

    m = _YAML_TAG_RE.search(s)
    if m:
        return m.group(1).strip()

    m = _YAML_FENCE_RE.search(s)
    if m:
        return m.group(1).strip()

    return s


# -------------------------
# YAML validation / parsing
# -------------------------

def validate_yaml_root_mapping(yaml_text: str) -> Dict[str, Any]:
    """Parse YAML into dict. Raises ValueError if invalid YAML or non-mapping root."""
    try:
        data = yaml.safe_load(yaml_text)
    except Exception as e:
        raise ValueError(f"Invalid YAML returned by LLM: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping/object (dict).")

    return data


# -------------------------
# LLM call
# -------------------------

def call_llm(
    prompt: str,
    *,
    model: str = "gemini-3-flash-preview",
    max_tokens: int = 2200,
    system_message: Optional[str] = None,
) -> str:
    completion = client.models.generate_content(
        model="gemini-3-flash-preview",  
        contents=prompt
    )
    print("LLM RESPONSE:", completion.text)
    return completion.text
# -------------------------
# Update state (YAML)
# -------------------------

def build_yaml_update_prompt(
    raw_user_message: str,
    current_yaml_state: Optional[str],
    schema_template_yaml: str = YAML_TRIP_INTAKE_SCHEMA_V11,
) -> str:
    current = (current_yaml_state or "").strip() or schema_template_yaml.strip()
    return (
        "CURRENT STATE YAML:\n"
        f"{current}\n\n"
        "NEW RAW USER MESSAGE:\n"
        f"{raw_user_message}\n"
    )


def update_trip_yaml_state(
    raw_user_message: str,
    current_yaml_state: Optional[str],
    *,
    schema_template_yaml: str = YAML_TRIP_INTAKE_SCHEMA_V11,
    model: str = "gemini-3-flash-preview",
    max_tokens: int = 2200,
) -> str:
    prompt = build_yaml_update_prompt(
        raw_user_message=raw_user_message,
        current_yaml_state=current_yaml_state,
        schema_template_yaml=schema_template_yaml,
    )

    result = call_llm(
        prompt,
        model=model,
        max_tokens=max_tokens,
        system_message=YAML_UPDATE_SYSTEM_INSTRUCTIONS
    )

    yaml_text = extract_yaml_text(result)
    validate_yaml_root_mapping(yaml_text)
    return yaml_text


# -------------------------
# Missing essentials logic
# -------------------------

def _as_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _has_text(x: Any) -> bool:
    return isinstance(x, str) and x.strip() != ""


def first_missing_essential(d: Dict[str, Any]) -> Optional[str]:
    """
    Returns the FIRST missing essential field in priority order, else None.
    1) travelers.adults
    2) origin: iata OR city
    3) dates: departureDate + (returnDate OR nights>0)
    4) destination: iata OR city OR region
    """
    trip = _as_dict(d.get("trip"))
    essentials = _as_dict(trip.get("essentials"))

    travelers = _as_dict(essentials.get("travelers"))
    adults = travelers.get("adults")
    if adults in (None, "", 0):
        return "travelers.adults"

    origin = _as_dict(essentials.get("origin"))
    if not (_has_text(origin.get("iata")) or _has_text(origin.get("city"))):
        return "origin.(iata|city)"

    dates = _as_dict(essentials.get("dates"))
    dep_ok = _has_text(dates.get("departureDate"))
    ret_ok = _has_text(dates.get("returnDate"))
    nights = dates.get("nights")
    nights_ok = isinstance(nights, int) and nights > 0
    if not (dep_ok and (ret_ok or nights_ok)):
        return "dates.(departureDate+returnDate OR departureDate+nights)"

    dest = _as_dict(essentials.get("destination"))
    if not (_has_text(dest.get("iata")) or _has_text(dest.get("city")) or _has_text(dest.get("region"))):
        return "destination.(iata|city|region)"

    return None


# -------------------------
# Single missing question (minimal context, no YAML)
# -------------------------

QUESTION_SYSTEM_MESSAGE = (
    "You are a trip-intake assistant.\n"
    "Task: ask ONE short, friendly question to collect exactly ONE missing essential detail.\n"
    "Output ONLY the question text.\n"
    "No markdown, no bullets, no numbering, no quotes, no explanations.\n"
    "Do NOT mention internal field names.\n"
)

MISSING_FIELD_TO_USER_LABEL: Dict[str, str] = {
    "travelers.adults": "how many adults are traveling",
    "origin.(iata|city)": "your departure city or airport",
    "dates.(departureDate+returnDate OR departureDate+nights)": "your travel dates (departure + return date, or departure date + number of nights)",
    "destination.(iata|city|region)": "your destination (city, airport, or region)",
}


def summarize_known_essentials(d: Dict[str, Any]) -> Dict[str, Any]:
    trip = _as_dict(d.get("trip"))
    essentials = _as_dict(trip.get("essentials"))

    travelers = _as_dict(essentials.get("travelers"))
    origin = _as_dict(essentials.get("origin"))
    dest = _as_dict(essentials.get("destination"))
    dates = _as_dict(essentials.get("dates"))

    return {
        "adults": travelers.get("adults"),
        "children": travelers.get("children", 0),
        "origin": {"iata": origin.get("iata"), "city": origin.get("city"), "countryCode": origin.get("countryCode")},
        "destination": {"iata": dest.get("iata"), "city": dest.get("city"), "region": dest.get("region"), "countryCode": dest.get("countryCode")},
        "dates": {"departureDate": dates.get("departureDate"), "returnDate": dates.get("returnDate"), "nights": dates.get("nights")},
    }


_BULLET_PREFIX_RE = re.compile(r"^\s*([-*•]+|\d+\.)\s+")
_MD_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
_MD_ITALIC_RE = re.compile(r"\*(.*?)\*")
_CODE_FENCE_RE = re.compile(r"```.*?```", flags=re.DOTALL)


def sanitize_question(text: str) -> str:
    if not text:
        return ""

    s = text.strip()
    s = _CODE_FENCE_RE.sub("", s).strip()

    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    s = lines[0] if lines else ""

    s = _MD_BOLD_RE.sub(r"\1", s)
    s = _MD_ITALIC_RE.sub(r"\1", s)
    s = _BULLET_PREFIX_RE.sub("", s).strip()

    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()

    if s and not s.endswith("?"):
        s += "?"

    return s


def build_single_missing_question_prompt(missing_field: str, known: Dict[str, Any]) -> str:
    missing_label = MISSING_FIELD_TO_USER_LABEL.get(missing_field, "a missing essential detail")
    return (
        f"Missing detail to ask for: {missing_label}\n"
        f"Known essentials so far (may include nulls): {known}\n"
        "Ask ONE question to collect ONLY the missing detail.\n"
    )

@app.post("api/get_single_missing_question", response_model=Dict[str, Any])
def get_single_missing_question(
    yaml_state: str,
    *,
    model: str = "gemini-3-flash-preview",
    max_tokens: int = 120,
) -> Dict[str, Any]:
    model: str = "gemini-3-flash-preview"
    yaml_state_clean = extract_yaml_text(yaml_state)
    decoded = validate_yaml_root_mapping(yaml_state_clean)

    missing = first_missing_essential(decoded)
    if not missing:
        return {"status": "ready", "missing_field": None, "question": None}

    known = summarize_known_essentials(decoded)
    prompt = build_single_missing_question_prompt(missing, known)

    raw = call_llm(
        prompt,
        model=model,
        max_tokens=max_tokens,
        system_message=QUESTION_SYSTEM_MESSAGE,
    )

    question = sanitize_question(extract_yaml_text(raw))
    if not question:
        fallback = {
            "travelers.adults": "How many adults are traveling?",
            "origin.(iata|city)": "What city or airport are you departing from?",
            "dates.(departureDate+returnDate OR departureDate+nights)": "What are your travel dates (departure and return), or your departure date and number of nights?",
            "destination.(iata|city|region)": "Where would you like to go (city, airport, or region)?",
        }
        question = fallback.get(missing, "What detail is missing so I can continue?")

    return {"status": "needs_input", "missing_field": missing, "question": question}


# -------------------------
# Demo
# -------------------------

if __name__ == "__main__":
    state = ""

    state = update_trip_yaml_state(
        raw_user_message="2 adults. I want a football trip, very foodie, sometime in March.",
        current_yaml_state=state)
    
    print("\n=== YAML STATE ===\n", state)

    missing_resp = get_single_missing_question(state)
    print("\n=== FIRST MISSING ===\n", missing_resp)

    state = update_trip_yaml_state(
        raw_user_message="Flying from TLV. March 10 to March 13.",
        current_yaml_state=state
    )
    print("\n=== UPDATED YAML STATE ===\n", state)

    missing_resp = get_single_missing_question(state)
    print("\n=== FIRST MISSING AFTER UPDATE ===\n", missing_resp)

    state = update_trip_yaml_state(
        raw_user_message="To Barcelona.",
        current_yaml_state=state
    )
    print("\n=== FINAL YAML STATE ===\n", state)
