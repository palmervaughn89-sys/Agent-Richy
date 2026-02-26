"""Avatar emotion engine.

Determines the avatar emotion from response context / intent / content analysis.
"""

import re
from typing import Optional


# Keyword → emotion rules (priority ordered)
_EMOTION_RULES: list[dict] = [
    {
        "keywords": ["congratulations", "paid off", "milestone", "achieved", "great job",
                      "you did it", "well done", "celebrate"],
        "emotion": "celebrating",
        "priority": 10,
    },
    {
        "keywords": ["warning", "overspend", "risk", "danger", "careful",
                      "high interest", "penalty", "late fee", "avoid"],
        "emotion": "serious",
        "priority": 8,
    },
    {
        "keywords": ["debt", "owe", "behind", "struggling", "paycheck to paycheck",
                      "stressed", "worried", "overwhelmed", "difficult"],
        "emotion": "empathetic",
        "priority": 7,
    },
    {
        "keywords": ["growth", "compound", "projection", "increase", "return",
                      "savings goal", "built", "you'll have", "passive income"],
        "emotion": "excited",
        "priority": 6,
    },
    {
        "keywords": ["chart", "breakdown", "analysis", "comparison", "data",
                      "table", "numbers", "calculation", "result"],
        "emotion": "presenting",
        "priority": 5,
    },
    {
        "keywords": ["learn", "explain", "understand", "concept", "means",
                      "think of it", "analogy", "example", "here's how"],
        "emotion": "teaching",
        "priority": 4,
    },
]

# Agent → default emotion mapping
_AGENT_EMOTIONS: dict[str, str] = {
    "coach_richy": "friendly",
    "budget_bot": "presenting",
    "invest_intel": "presenting",
    "debt_destroyer": "empathetic",
    "savings_sage": "teaching",
    "kid_coach": "excited",
}


def determine_emotion(
    response_text: str,
    agent: str = "coach_richy",
    intent: Optional[str] = None,
) -> str:
    """Determine the avatar emotion based on response content analysis.

    Priority: content keywords > intent mapping > agent default > 'friendly'
    """
    text_lower = response_text.lower()

    best_emotion = None
    best_priority = 0

    for rule in _EMOTION_RULES:
        for kw in rule["keywords"]:
            if kw in text_lower:
                if rule["priority"] > best_priority:
                    best_priority = rule["priority"]
                    best_emotion = rule["emotion"]
                break

    if best_emotion:
        return best_emotion

    # Intent-based fallback
    intent_emotions = {
        "compound_interest": "excited",
        "debt_payoff": "empathetic",
        "debt_strategy": "presenting",
        "emergency_fund": "teaching",
        "budget": "presenting",
        "savings_goal": "excited",
        "investing": "presenting",
        "kids_question": "excited",
    }
    if intent and intent in intent_emotions:
        return intent_emotions[intent]

    # Agent default
    return _AGENT_EMOTIONS.get(agent, "friendly")
