from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

import yaml
import uvicorn
import requests
from dotenv import load_dotenv
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from shared.data_types.llm_models import *
from apps.llm_chat_essentials.settings import (
    YAML_TRIP_INTAKE_SCHEMA_V11,
    YAML_UPDATE_SYSTEM_INSTRUCTIONS,
)

load_dotenv()
app = FastAPI(title="LLM Chat Essentials Service")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    print("WARNING: PERPLEXITY_API_KEY not found in environment.")


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

    # Sometimes the model starts a fenced block but forgets to close it.
    # Strip a leading ```yaml/```yml/``` line and any remaining backticks.
    if s.startswith("```"):
        lines = s.splitlines()
        if len(lines) > 1:
            s = "\n".join(lines[1:]).strip()
        else:
            s = ""

        if s.endswith("```"):
            s = s.rsplit("```", 1)[0].strip()

        s = s.replace("```", "").strip()

    return s


# -------------------------
# YAML validation / parsing
# -------------------------

def validate_yaml_root_mapping(yaml_text: str) -> Dict[str, Any]:
    """Parse YAML into dict. Raises ValueError if invalid YAML or non-mapping root."""
    def _cleanup_common_llm_yaml_issues(text: str) -> str:
        cleaned = extract_yaml_text(text)

        # Fix common dangling quote issue (e.g. - "Some text) by removing the lone quote.
        fixed_lines: List[str] = []
        for line in cleaned.splitlines():
            if line.count('"') == 1:
                fixed_lines.append(line.replace('"', ""))
            else:
                fixed_lines.append(line)
        return "\n".join(fixed_lines).strip()

    try:
        data = yaml.safe_load(yaml_text)
    except Exception:
        try:
            repaired = _cleanup_common_llm_yaml_issues(yaml_text)
            data = yaml.safe_load(repaired)
        except Exception as e:
            raise ValueError(f"Invalid YAML returned by LLM: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping/object (dict).")

    return data

def _as_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []

def _destination_item_is_set(item: Any) -> bool:
    d = _as_dict(item)
    return (
        _has_text(d.get("iata"))
        or _has_text(d.get("city"))
        or _has_text(d.get("region"))
    )

# -------------------------
# LLM call
# -------------------------

def call_llm(
    prompt: str,
    *,
    model: str = "sonar",
    max_tokens: int = 1000,
    system_message: Optional[str] = None,
) -> str:
    if not PERPLEXITY_API_KEY:
        raise ValueError("Set PERPLEXITY_API_KEY environment variable")

    url = "https://api.perplexity.ai/chat/completions"

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    print("LLM RESPONSE:", text)
    return text
# -------------------------
# Update state (YAML)
# -------------------------


def build_yaml_update_prompt(
    raw_user_message: str,
    current_yaml_state: Optional[str],
    schema_template_yaml: str = YAML_TRIP_INTAKE_SCHEMA_V11,
) -> str:
    current = (current_yaml_state or "").strip() or schema_template_yaml.strip()

    today_iso = date.today().isoformat()

    return (
        f"CURRENT DATE (ISO): {today_iso}\n\n"
        "CURRENT STATE YAML:\n"
        f"{current}\n\n"
        "NEW RAW USER MESSAGE:\n"
        f"{raw_user_message}\n"
    )


def _update_trip_yaml_state(
    raw_user_message: str,
    current_yaml_state: Optional[str],
    *,
    schema_template_yaml: str = YAML_TRIP_INTAKE_SCHEMA_V11,
    max_tokens: int = 2200,
) -> str:
    prompt = build_yaml_update_prompt(
        raw_user_message=raw_user_message,
        current_yaml_state=current_yaml_state,
        schema_template_yaml=schema_template_yaml,
    )

    result = call_llm(
        prompt,
        max_tokens=max_tokens,
        system_message=YAML_UPDATE_SYSTEM_INSTRUCTIONS
    )

    yaml_text = extract_yaml_text(result)
    validate_yaml_root_mapping(yaml_text)
    return yaml_text


# -------------------------
# Missing essentials logic
# -------------------------



def _get_destinations_from_essentials(essentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    # New canonical field
    dests = essentials.get("destinations")
    if isinstance(dests, list):
        return [d for d in dests if isinstance(d, dict)]

    # Back-compat (old single destination object)
    single = essentials.get("destination")
    if isinstance(single, dict):
        return [single]

    return []
def _as_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}

def _as_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []

def _has_text(x: Any) -> bool:
    return isinstance(x, str) and x.strip() != ""

def _is_date_like(x: Any) -> bool:
    # PyYAML often parses YYYY-MM-DD into datetime.date automatically
    return isinstance(x, (date, datetime)) or _has_text(x)

def _to_int(x: Any) -> Optional[int]:
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        s = x.strip()
        if s.isdigit():
            return int(s)
    return None

def _destination_item_is_set(x: Any) -> bool:
    d = _as_dict(x)
    return _has_text(d.get("iata")) or _has_text(d.get("city")) or _has_text(d.get("region"))

def _get_destinations_from_essentials(essentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    # New canonical field
    dests = essentials.get("destinations")
    if isinstance(dests, list):
        return [d for d in dests if isinstance(d, dict)]

    # Back-compat (old single destination object)
    single = essentials.get("destination")
    if isinstance(single, dict):
        return [single]

    return []
def first_missing_essential(d: Dict[str, Any]) -> Optional[str]:
    """
    Returns the FIRST missing essential field in priority order, else None.
    1) travelers.adults
    2) origin: iata OR city
    3) dates: (departureDate+returnDate) OR (departureDate+nights>0)
    4) destinations: at least one item with iata OR city OR region
    """
    trip = _as_dict(d.get("trip"))
    essentials = _as_dict(trip.get("essentials"))

    # 1) travelers.adults
    travelers = _as_dict(essentials.get("travelers"))
    adults = travelers.get("adults")
    if adults in (None, "", 0):
        return "travelers.adults"

    # 2) origin
    origin = _as_dict(essentials.get("origin"))
    if not (_has_text(origin.get("iata")) or _has_text(origin.get("city"))):
        return "origin.(iata|city)"

    # 3) dates (date-like, not only strings)
    dates = _as_dict(essentials.get("dates"))
    dep = dates.get("departureDate")
    ret = dates.get("returnDate")
    nights_raw = dates.get("nights")

    dep_ok = _is_date_like(dep)
    ret_ok = _is_date_like(ret)

    nights = _to_int(nights_raw)
    nights_ok = isinstance(nights, int) and nights > 0

    if not (dep_ok and (ret_ok or nights_ok)):
        return "dates.(departureDate+returnDate OR departureDate+nights)"

    # 4) destinations (new list, with back-compat)
    dests = _get_destinations_from_essentials(essentials)
    if not dests or not any(_destination_item_is_set(x) for x in dests):
        return "destinations.(iata|city|region)"

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
    "destinations.(iata|city|region)": "your destination(s) (city, airport, or region)",
}

def summarize_known_essentials(d: Dict[str, Any]) -> Dict[str, Any]:
    trip = _as_dict(d.get("trip"))
    essentials = _as_dict(trip.get("essentials"))

    travelers = _as_dict(essentials.get("travelers"))
    origin = _as_dict(essentials.get("origin"))
    dates = _as_dict(essentials.get("dates"))

    dests = _get_destinations_from_essentials(essentials)
    # keep it compact
    destinations_summary = [
        {
            "iata": dd.get("iata"),
            "city": dd.get("city"),
            "region": dd.get("region"),
            "countryCode": dd.get("countryCode"),
        }
        for dd in dests[:3]  # cap to avoid token bloat
        if isinstance(dd, dict)
    ]

    return {
        "adults": travelers.get("adults"),
        "children": travelers.get("children", 0),
        "origin": {
            "iata": origin.get("iata"),
            "city": origin.get("city"),
            "countryCode": origin.get("countryCode"),
        },
        "destinations": destinations_summary,
        "dates": {
            "departureDate": dates.get("departureDate"),
            "returnDate": dates.get("returnDate"),
            "nights": dates.get("nights"),
        },
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


def _get_single_missing_question(
    yaml_state: str,
) -> FillResponse:
    yaml_state_clean = extract_yaml_text(yaml_state)
    decoded = validate_yaml_root_mapping(yaml_state_clean)

    missing = first_missing_essential(decoded)
    if not missing:
        return FillResponse(yaml=yaml_state_clean, status=FillStatus.ready, message=None)

    known = summarize_known_essentials(decoded)
    prompt = build_single_missing_question_prompt(missing, known)

    raw = call_llm(
        prompt,
        max_tokens=1000,
        system_message=QUESTION_SYSTEM_MESSAGE
    )

    question = sanitize_question(extract_yaml_text(raw))
    if not question:
        fallback = {
            "travelers.adults": "How many adults are traveling?",
            "origin.(iata|city)": "What city or airport are you departing from?",
            "dates.(departureDate+returnDate OR departureDate+nights)": "What are your travel dates (departure and return), or your departure date and number of nights?",
            "destinations.(iata|city|region)": "Where would you like to go (city, airport, or region)? You can name more than one destination.",
        }

        question = fallback.get(missing, "What detail is missing so I can continue?")

    return FillResponse(
        yaml=yaml_state_clean,
        status=FillStatus.needs_more_info if missing else FillStatus.ready,
        message=question if missing else None,
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "llm_chat_essentials"}


@app.post("/api/get_single_missing_question", response_model=FillResponse)
def get_single_missing_question(request: UpdateTripRequest) -> FillResponse:
    return _get_single_missing_question(
        yaml_state=request.current_yaml_state,
    )


@app.post("/api/update_trip_yaml", response_model=FillResponse)
def update_trip_yaml_state(request: UpdateTripRequest) -> FillResponse:
    result = _update_trip_yaml_state(
        raw_user_message=request.raw_user_message,
        current_yaml_state=request.current_yaml_state or None,
    )

    decoded = validate_yaml_root_mapping(result)
    missing = first_missing_essential(decoded)
    return FillResponse(
        yaml=result,
        status=FillStatus.needs_more_info if missing else FillStatus.ready,
        message=None,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)