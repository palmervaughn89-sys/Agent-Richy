"""Keystroke router — /api/keystroke for real-time avatar reactions.

Lightweight endpoint that must respond in <50ms.
Does NOT call any LLM — only keyword matching.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/keystroke", tags=["keystroke"])

# Keyword → expression mapping (priority ordered)
_TRIGGERS: list[dict] = [
    {"keywords": ["debt", "owe", "behind", "late payment", "collections"], "expression": "empathetic", "priority": 3},
    {"keywords": ["crypto", "bitcoin", "moon", "yolo", "nft", "meme coin"], "expression": "confused", "priority": 3},
    {"keywords": ["save", "invest", "grow", "compound", "retirement", "roth"], "expression": "excited", "priority": 2},
    {"keywords": ["help", "how do i", "explain", "what is", "teach me"], "expression": "teaching", "priority": 1},
    {"keywords": ["lost", "scared", "worried", "stressed", "anxious", "overwhelmed"], "expression": "empathetic", "priority": 3},
    {"keywords": ["budget", "plan", "goal", "track", "organize"], "expression": "thinking", "priority": 1},
    {"keywords": ["lol", "haha", "funny", "😂", "joke"], "expression": "laughing", "priority": 2},
    {"keywords": ["rich", "million", "lambo", "retire early", "passive income", "fire"], "expression": "excited", "priority": 2},
    {"keywords": ["tax", "irs", "deduction", "filing"], "expression": "serious", "priority": 1},
    {"keywords": ["kid", "child", "son", "daughter", "teach", "allowance"], "expression": "excited", "priority": 1},
]

# Reaction bubbles — short quips keyed by expression
REACTION_BUBBLES: dict[str, list[str]] = {
    "empathetic": [
        "Oof, let's work through this together 💪",
        "I hear you — we'll figure this out",
        "It's okay, everyone starts somewhere",
    ],
    "confused": [
        "Oh boy, here we go... 👀",
        "Hmm, let me think about that one...",
        "Interesting choice... 🤔",
    ],
    "excited": [
        "Now you're speaking my language! 🎯",
        "Love where this is going! 🚀",
        "YES! Let's talk about this! 💰",
    ],
    "teaching": [
        "Great question! Let me explain... 📚",
        "Ooh, I love teaching this!",
        "Perfect — here's the deal...",
    ],
    "thinking": [
        "Let's get you organized! 📊",
        "Hmm, running some numbers...",
        "Good thinking — let me crunch this",
    ],
    "laughing": [
        "Ha! Good one 😄",
        "LOL, okay okay... 😂",
        "You're funny — but seriously...",
    ],
    "serious": [
        "Nobody's favorite topic... but I got you 😅",
        "Important stuff — pay attention!",
        "Let's make sure you're covered",
    ],
}


class KeystrokeRequest(BaseModel):
    partial_text: str


class KeystrokeResponse(BaseModel):
    expression: str
    bubble: str | None = None


@router.post("", response_model=KeystrokeResponse)
async def analyze_keystroke(request: KeystrokeRequest):
    """Analyze partial text and return avatar expression. Must be <50ms."""
    text = request.partial_text.lower().strip()

    if not text:
        return KeystrokeResponse(expression="idle")

    best_expression = "watching"
    best_priority = 0

    for trigger in _TRIGGERS:
        for kw in trigger["keywords"]:
            if kw in text:
                if trigger["priority"] > best_priority:
                    best_priority = trigger["priority"]
                    best_expression = trigger["expression"]
                break

    # Pick a reaction bubble
    import random
    bubble = None
    if best_expression in REACTION_BUBBLES:
        bubble = random.choice(REACTION_BUBBLES[best_expression])

    return KeystrokeResponse(expression=best_expression, bubble=bubble)
