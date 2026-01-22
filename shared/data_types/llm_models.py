from typing import List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: ChatRole = ChatRole.USER
    content: str = ""


class ChatRequest(BaseModel):
    """Represents a chat request.

    - `raw_message` is a convenience single raw text message (user),
      used when the caller just wants to send plain text.
    - `messages` is the full list of structured messages (role + content).
    """
    raw_message: Optional[str] = ""
    messages: List[ChatMessage] = Field(default_factory=list)
    model: str = "sonar-pro"
    max_tokens: int = 512
    temperature: float = 0.0


class ChatResponse(BaseModel):
    answer: str = ""
    # raw provider response (kept for debugging / downstream consumers)
    raw: dict = Field(default_factory=dict)
