"""Response formatter service.

Takes raw agent text output and enrichment context,
produces the structured response with charts, evidence, examples, etc.
"""

from typing import Optional
from models.structured_response import (
    StructuredResponse, ChartConfig, Example, Evidence, TimeHorizon, Milestone,
)
from services.avatar_emotion import determine_emotion
from services.chart_generator import generate_charts_from_calculator


def format_response(
    raw_text: str,
    agent: str = "coach_richy",
    intent: Optional[str] = None,
    calculator_name: Optional[str] = None,
    calculator_result: Optional[dict] = None,
    suggested_agent: Optional[str] = None,
) -> StructuredResponse:
    """Format raw agent output into a structured response.

    1. Strip any JSON extraction blocks from the text
    2. Generate charts from calculator results
    3. Determine avatar emotion
    4. Extract evidence/examples if present
    """
    import re

    # Strip JSON blocks (agents append these for data extraction)
    clean_text = re.sub(
        r"\s*```json\s*\{.*?\}\s*```\s*", "", raw_text, flags=re.DOTALL
    ).strip()

    # Generate charts from calculator
    charts: list[ChartConfig] = []
    if calculator_name and calculator_result:
        charts = generate_charts_from_calculator(calculator_name, calculator_result)

    # Determine avatar emotion
    emotion = determine_emotion(clean_text, agent=agent, intent=intent)

    # Extract evidence-like statements (lines with source citations)
    evidence: list[Evidence] = []
    evidence_patterns = [
        (r"(?:according to|source:|from)\s+(.+?)[\.,](.+)", 0.85),
        (r"(?:research shows|studies show|data shows)\s+(.+)", 0.75),
    ]
    for pattern, confidence in evidence_patterns:
        for match in re.finditer(pattern, clean_text, re.IGNORECASE):
            evidence.append(Evidence(
                source=match.group(1).strip()[:100],
                fact=match.group(0).strip()[:200],
                confidence=confidence,
            ))

    # Extract examples (markdown ### headers followed by content)
    examples: list[Example] = []

    return StructuredResponse(
        message=clean_text,
        agent=agent,
        charts=charts,
        examples=examples,
        evidence=evidence,
        avatar_emotion=emotion,
        suggested_agent=suggested_agent,
        calculator_result=calculator_result,
    )
