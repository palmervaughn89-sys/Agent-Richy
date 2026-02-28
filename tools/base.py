"""Base class for all Richy financial tools.

Every tool in the engine inherits from RichyToolBase, providing
a uniform interface for execution, response formatting, and
accuracy/source tracking.
"""

from __future__ import annotations

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Standardised return envelope for every tool invocation."""

    tool_id: int
    tool_name: str
    confidence: float  # 0-1
    response: str
    data_used: list[str] = field(default_factory=list)
    accuracy_score: float = 0.0
    sources: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "confidence": round(self.confidence, 4),
            "response": self.response,
            "data_used": self.data_used,
            "accuracy_score": round(self.accuracy_score, 4),
            "sources": self.sources,
            "raw_data": self.raw_data,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }


class RichyToolBase(ABC):
    """Abstract base class every Richy tool must implement.

    Subclass this and override:
      - ``tool_id``          — unique integer identifier
      - ``tool_name``        — human-readable name
      - ``description``      — one-line description
      - ``required_profile`` — list of user_profile keys the tool needs
      - ``execute(question, profile)`` — run the tool and return a ToolResult
    """

    # ── Identity (override in subclasses) ─────────────────────────────────
    tool_id: int = 0
    tool_name: str = "base"
    description: str = ""
    required_profile: list[str] = []

    # ── Construction ──────────────────────────────────────────────────────

    def __init__(self, **kwargs):
        """Accept arbitrary keyword args so subclasses can receive config."""
        for k, v in kwargs.items():
            setattr(self, k, v)

    # ── Public API ────────────────────────────────────────────────────────

    def run(self, question: str, user_profile: dict) -> dict:
        """Validate inputs, execute, and return a result dict.

        This is the primary entry point called by ``ToolRouter``.
        """
        missing = self._check_profile(user_profile)
        if missing:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=0.0,
                response=(
                    f"I need more info to answer that. "
                    f"Missing profile fields: {', '.join(missing)}"
                ),
                data_used=[],
                accuracy_score=0.0,
                sources=[],
            ).to_dict()

        t0 = time.perf_counter()
        try:
            result = self.execute(question, user_profile)
            result.execution_time_ms = (time.perf_counter() - t0) * 1000
            return result.to_dict()
        except Exception as exc:
            logger.exception("Tool %s failed: %s", self.tool_name, exc)
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=0.0,
                response=f"Sorry, I hit an error running {self.tool_name}: {exc}",
                sources=[],
                execution_time_ms=(time.perf_counter() - t0) * 1000,
            ).to_dict()

    @abstractmethod
    def execute(self, question: str, user_profile: dict) -> ToolResult:
        """Run the tool logic. Must return a ``ToolResult``."""
        ...

    # ── Helpers ───────────────────────────────────────────────────────────

    def _check_profile(self, profile: dict) -> list[str]:
        """Return list of missing required profile keys (empty = OK)."""
        return [k for k in self.required_profile if not profile.get(k)]

    @staticmethod
    def fmt_currency(value: float) -> str:
        """Format a number as $X,XXX.XX."""
        return f"${value:,.2f}"

    @staticmethod
    def fmt_pct(value: float, decimals: int = 1) -> str:
        """Format a decimal as X.X% (0.07 → 7.0%)."""
        return f"{value * 100:.{decimals}f}%"

    def __repr__(self) -> str:
        return f"<Tool #{self.tool_id} {self.tool_name}>"
