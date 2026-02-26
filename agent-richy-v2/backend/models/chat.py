"""Pydantic models for chat request/response."""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "coach_richy"
    session_id: Optional[str] = "default"
    context: Optional[dict] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    agent: Optional[str] = None
