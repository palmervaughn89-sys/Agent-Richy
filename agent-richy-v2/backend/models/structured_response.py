"""Structured response format for Agent Richy v2.

Every chat response returns this rich format with charts, evidence, 
time horizons, and avatar emotion data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ChartConfig(BaseModel):
    """Recharts-compatible chart configuration."""
    type: str = "line"  # line | bar | pie | area
    title: str = ""
    data: List[dict] = Field(default_factory=list)
    x_key: str = "x"
    y_key: str = "y"
    color: str = "#10B981"


class Example(BaseModel):
    """Scenario example for recommendations."""
    title: str
    description: str
    projected_savings: Optional[str] = None
    timeline: Optional[str] = None
    data: Optional[dict] = None


class Milestone(BaseModel):
    date: str
    label: str


class TimeHorizon(BaseModel):
    start: str
    end: str
    milestones: List[Milestone] = Field(default_factory=list)


class Evidence(BaseModel):
    source: str
    fact: str
    confidence: float = 0.8


class StructuredResponse(BaseModel):
    """The full structured response returned by /api/chat."""
    message: str
    agent: str = "coach_richy"
    charts: List[ChartConfig] = Field(default_factory=list)
    examples: List[Example] = Field(default_factory=list)
    time_horizon: Optional[TimeHorizon] = None
    evidence: List[Evidence] = Field(default_factory=list)
    avatar_emotion: str = "friendly"
    suggested_agent: Optional[str] = None
    calculator_result: Optional[dict] = None
