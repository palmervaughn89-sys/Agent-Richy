"""Pydantic models for chat request/response."""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "coach_richy"
    session_id: Optional[str] = "default"
    context: Optional[dict] = None
    skill: Optional[str] = None  # "coupon" | "optimizer" | None
    optimizer_expenses: Optional[str] = None  # expense summary for context continuity


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    agent: Optional[str] = None
