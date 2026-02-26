"""Intent detection & smart response pipeline.

Analyzes user messages to:
1. Detect intent category (calculation, budget, debt, investing, etc.)
2. Extract numbers from the message
3. Route to the right tool (calculator, knowledge base, agent)
4. Build enriched prompts with calculator results and RAG context
"""

import re
from typing import Optional

from utils.response_cache import find_cached_response, get_session_cached, set_session_cache, fake_thinking_delay
from utils.knowledge_retrieval import retrieve_context
from utils.financial_calculators import CALCULATOR_REGISTRY

# ── Intent categories and keyword mapping ────────────────────────────────

INTENTS: dict[str, dict] = {
    "compound_interest": {
        "keywords": [
            "compound interest", "how much will grow", "investment growth",
            "if i invest", "savings grow", "interest on interest",
            "how much will i have", "money grow",
        ],
        "calculator": "compound_interest",
        "agent": "invest_intel",
    },
    "debt_payoff": {
        "keywords": [
            "pay off debt", "credit card payoff", "how long to pay",
            "debt free", "payoff time", "pay off my card",
            "pay off loan", "debt payment",
        ],
        "calculator": "debt_payoff",
        "agent": "debt_destroyer",
    },
    "debt_strategy": {
        "keywords": [
            "snowball", "avalanche", "which debt first",
            "debt strategy", "debt method", "debt order",
        ],
        "calculator": "debt_snowball_vs_avalanche",
        "agent": "debt_destroyer",
    },
    "emergency_fund": {
        "keywords": [
            "emergency fund", "rainy day", "how much emergency",
            "emergency savings", "financial cushion",
        ],
        "calculator": "emergency_fund_status",
        "agent": "savings_sage",
    },
    "budget": {
        "keywords": [
            "budget", "50/30/20", "50 30 20", "spending plan",
            "allocate my money", "needs wants savings",
        ],
        "calculator": "budget_50_30_20",
        "agent": "budget_bot",
    },
    "savings_goal": {
        "keywords": [
            "save for", "savings goal", "how long to save",
            "saving up", "reach my goal", "save enough",
            "down payment", "save for house",
        ],
        "calculator": "savings_goal_timeline",
        "agent": "savings_sage",
    },
    "net_worth": {
        "keywords": [
            "net worth", "total assets", "what am i worth",
            "assets minus liabilities", "financial snapshot",
        ],
        "calculator": "net_worth_calculator",
        "agent": "coach_richy",
    },
    "investing": {
        "keywords": [
            "invest", "stock", "etf", "index fund", "portfolio",
            "roth ira", "401k", "retirement", "diversif",
            "asset allocation", "bonds",
        ],
        "calculator": None,
        "agent": "invest_intel",
    },
    "debt_help": {
        "keywords": [
            "debt", "owe", "loan", "credit card", "interest rate",
            "balance", "payoff", "consolidat",
        ],
        "calculator": None,
        "agent": "debt_destroyer",
    },
    "savings": {
        "keywords": [
            "save", "savings", "high yield", "hysa", "sinking fund",
            "save money", "cut expenses",
        ],
        "calculator": None,
        "agent": "savings_sage",
    },
    "budget_help": {
        "keywords": [
            "spending", "expense", "subscription", "cut cost",
            "overspend", "track spending",
        ],
        "calculator": None,
        "agent": "budget_bot",
    },
    "kids_question": {
        "keywords": [
            "teach kids", "kids money", "child", "allowance",
            "teenager", "young", "my son", "my daughter",
            "financial literacy kids",
        ],
        "calculator": None,
        "agent": "kid_coach",
    },
    "general": {
        "keywords": [],
        "calculator": None,
        "agent": "coach_richy",
    },
}


# ── Number extraction ────────────────────────────────────────────────────

def extract_numbers(text: str) -> list[float]:
    """Extract all numeric values from text, handling $, commas, % etc."""
    # Match: $1,234.56, 1234, 12.5%, 10,000
    patterns = [
        r'\$[\d,]+(?:\.\d+)?',     # $1,234.56
        r'[\d,]+(?:\.\d+)?%',      # 12.5%
        r'[\d,]+(?:\.\d+)?',       # 1234.56
    ]
    numbers = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            value = match.group().replace('$', '').replace(',', '').replace('%', '')
            try:
                numbers.append(float(value))
            except ValueError:
                pass
    return numbers


def extract_percentage(text: str) -> Optional[float]:
    """Extract a percentage value and convert to decimal."""
    match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if match:
        return float(match.group(1)) / 100
    return None


# ── Intent detection ─────────────────────────────────────────────────────

def detect_intent(message: str) -> dict:
    """Detect the user's intent from their message.

    Returns:
        {
            "intent": str,
            "calculator": str | None,
            "agent": str,
            "confidence": float,
            "numbers": list[float],
        }
    """
    msg_lower = message.lower()
    best_intent = "general"
    best_score = 0

    for intent_name, intent_data in INTENTS.items():
        if intent_name == "general":
            continue
        score = 0
        for kw in intent_data["keywords"]:
            if kw in msg_lower:
                score += len(kw)  # Longer keyword matches have higher weight
        if score > best_score:
            best_score = score
            best_intent = intent_name

    intent_data = INTENTS[best_intent]
    return {
        "intent": best_intent,
        "calculator": intent_data.get("calculator"),
        "agent": intent_data.get("agent", "coach_richy"),
        "confidence": min(best_score / 20, 1.0),  # Normalize
        "numbers": extract_numbers(message),
    }


# ── Calculator auto-run ──────────────────────────────────────────────────

def try_auto_calculate(intent: dict, message: str) -> Optional[dict]:
    """Attempt to run a calculator based on detected intent + extracted numbers.

    Returns calculator result dict or None if insufficient data.
    """
    calc_name = intent.get("calculator")
    if not calc_name or calc_name not in CALCULATOR_REGISTRY:
        return None

    numbers = intent["numbers"]
    msg_lower = message.lower()

    try:
        if calc_name == "compound_interest" and len(numbers) >= 2:
            principal = numbers[0]
            pct = extract_percentage(message)
            rate = pct * 100 if pct else 8  # Calculator expects whole number (8 for 8%)
            years = numbers[1] if numbers[1] < 100 else 30
            monthly = numbers[2] if len(numbers) > 2 else 0
            return CALCULATOR_REGISTRY[calc_name](principal, rate, years, monthly)

        elif calc_name == "debt_payoff" and len(numbers) >= 2:
            balance = max(numbers)
            pct = extract_percentage(message)
            rate = pct * 100 if pct else 20  # Calculator expects whole number (20 for 20%)
            payment = min(n for n in numbers if n > 0 and n < balance) if len(numbers) >= 2 else balance * 0.03
            return CALCULATOR_REGISTRY[calc_name](balance, rate, payment)

        elif calc_name == "emergency_fund_status" and len(numbers) >= 1:
            expenses = numbers[0]
            savings = numbers[1] if len(numbers) > 1 else 0
            return CALCULATOR_REGISTRY[calc_name](expenses, savings)

        elif calc_name == "budget_50_30_20" and len(numbers) >= 1:
            income = numbers[0]
            # Try to extract expenses from message context
            return CALCULATOR_REGISTRY[calc_name](income, {})

        elif calc_name == "savings_goal_timeline" and len(numbers) >= 1:
            goal = max(numbers)
            current = numbers[1] if len(numbers) > 1 and numbers[1] < goal else 0
            monthly = min(n for n in numbers if 0 < n < goal) if len(numbers) > 1 else goal / 60
            return CALCULATOR_REGISTRY[calc_name](goal, current, monthly)

        elif calc_name == "net_worth_calculator" and len(numbers) >= 2:
            # Hard to auto-parse — let the agent handle it
            return None

    except (ValueError, ZeroDivisionError, IndexError):
        pass

    return None


# ── Smart response pipeline ──────────────────────────────────────────────

def build_enriched_context(message: str) -> dict:
    """Build an enriched context dict for a user message.

    This is the main pipeline entry point. It:
    1. Checks session cache for identical question
    2. Checks pre-written response cache
    3. Detects intent
    4. Runs calculator if appropriate
    5. Retrieves RAG knowledge base context
    6. Returns everything for the agent to use

    Returns:
        {
            "cached_response": str | None,        # Instant answer if available
            "intent": dict,                        # Intent detection result
            "calculator_result": dict | None,      # Auto-calculator result
            "knowledge_context": str,              # RAG-retrieved text
            "suggested_agent": str,                # Recommended agent key
            "enriched_prompt": str,                # Combined context for LLM
        }
    """
    # 1. Session cache (exact match)
    session_cached = get_session_cached(message)
    if session_cached:
        return {
            "cached_response": session_cached,
            "intent": {"intent": "cached", "confidence": 1.0},
            "calculator_result": None,
            "knowledge_context": "",
            "suggested_agent": "coach_richy",
            "enriched_prompt": "",
        }

    # 2. Pre-written cache (fuzzy keyword match)
    cached_text, confidence = find_cached_response(message)
    if cached_text and confidence >= 80:
        return {
            "cached_response": cached_text,
            "intent": {"intent": "cached", "confidence": confidence / 100},
            "calculator_result": None,
            "knowledge_context": "",
            "suggested_agent": "coach_richy",
            "enriched_prompt": "",
        }

    # 3. Detect intent
    intent = detect_intent(message)

    # 4. Try auto-calculator
    calc_result = try_auto_calculate(intent, message)

    # 5. Retrieve knowledge base context
    knowledge = retrieve_context(message, top_k=3)

    # 6. Build enriched prompt for LLM
    prompt_parts = []

    if calc_result:
        prompt_parts.append(
            f"[Calculator result — include these EXACT numbers in your response]\n"
            f"{_format_calc_result(calc_result)}"
        )

    if cached_text and confidence >= 50:
        prompt_parts.append(
            f"[Reference answer — use as inspiration but personalize]\n{cached_text[:500]}"
        )

    if knowledge:
        prompt_parts.append(knowledge)

    enriched_prompt = "\n\n".join(prompt_parts)

    return {
        "cached_response": None,
        "intent": intent,
        "calculator_result": calc_result,
        "knowledge_context": knowledge,
        "suggested_agent": intent.get("agent", "coach_richy"),
        "enriched_prompt": enriched_prompt,
    }


def _format_calc_result(result: dict) -> str:
    """Format calculator result dict into readable text."""
    lines = []
    for key, value in result.items():
        if isinstance(value, float):
            if abs(value) >= 1000:
                lines.append(f"- {key}: ${value:,.2f}")
            elif abs(value) < 1:
                lines.append(f"- {key}: {value:.2%}")
            else:
                lines.append(f"- {key}: {value:,.2f}")
        elif isinstance(value, int):
            lines.append(f"- {key}: {value:,}")
        elif isinstance(value, list):
            lines.append(f"- {key}: {len(value)} items")
            for item in value[:5]:  # Show first 5
                if isinstance(item, dict):
                    summary = ", ".join(f"{k}: {v}" for k, v in list(item.items())[:3])
                    lines.append(f"  • {summary}")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)
