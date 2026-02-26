"""Response cache — instant answers for common finance questions.

Refactored for FastAPI: removed all Streamlit (st.session_state) dependencies.
Uses a simple in-memory dict for session-level caching.
"""

import re
import hashlib
from typing import Optional, Tuple

# ── Pre-written Q&A cache ────────────────────────────────────────────────

CACHED_RESPONSES: list[dict] = [
    {
        "keywords": ["compound interest", "what is compound"],
        "response": (
            "### What Is Compound Interest? 🌱\n\n"
            "Compound interest is when you earn interest **on your interest** — it's "
            "the single most powerful force in building wealth.\n\n"
            "**Example:** Put **$5,000** in a savings account earning **5% annually**, "
            "and in 10 years you'll have **$8,144** — without adding another dime.\n\n"
            "The key? **Start early.**\n\n"
            "**Next Step:** Want me to calculate how much YOUR savings could grow?"
        ),
    },
    {
        "keywords": ["start investing", "how to invest", "begin investing"],
        "response": (
            "### How to Start Investing 📈\n\n"
            "1. **Emergency fund first** — 3-6 months of expenses in a HYSA\n"
            "2. **401(k) match** — Get the free employer match\n"
            "3. **Roth IRA** — Up to **$7,000/year** of tax-free growth\n"
            "4. **Max 401(k)** — Up to **$23,500/year**\n"
            "5. **Taxable brokerage** — Index funds like VTI\n\n"
            "**Next Step:** How much can you set aside monthly?"
        ),
    },
    {
        "keywords": ["50/30/20", "fifty thirty twenty", "50 30 20 rule"],
        "response": (
            "### The 50/30/20 Budget Rule 📋\n\n"
            "- **50% Needs:** Rent, groceries, utilities, insurance\n"
            "- **30% Wants:** Dining, entertainment, subscriptions\n"
            "- **20% Savings:** Emergency fund, retirement, debt payoff\n\n"
            "**Next Step:** Tell me your monthly income for a personal breakdown."
        ),
    },
    {
        "keywords": ["emergency fund", "rainy day fund"],
        "response": (
            "### Emergency Fund Guide 🛟\n\n"
            "Target: **3-6 months of essential expenses** in a HYSA (4-5% APY).\n\n"
            "Starting from zero? Aim for $1,000 first, then build up.\n\n"
            "**Next Step:** What are your monthly essentials? I'll calculate your target."
        ),
    },
    {
        "keywords": ["pay off debt or invest", "debt vs invest"],
        "response": (
            "### Debt vs. Investing Priority Ladder 🪜\n\n"
            "1. Minimum payments on all debts\n"
            "2. 401(k) match (free money)\n"
            "3. High-interest debt (>7% APR) — pay aggressively\n"
            "4. Emergency fund (3-6 months)\n"
            "5. Low-interest debt + investing\n\n"
            "**Next Step:** Share your debts and I'll prioritize them."
        ),
    },
    {
        "keywords": ["debt snowball", "snowball method"],
        "response": (
            "### The Debt Snowball Method ⛄\n\n"
            "Pay off debts from **smallest balance to largest**.\n"
            "Quick wins build motivation. 70% completion rate.\n\n"
            "**Next Step:** List your debts and I'll compare snowball vs avalanche."
        ),
    },
    {
        "keywords": ["debt avalanche", "avalanche method"],
        "response": (
            "### The Debt Avalanche Method 🏔️\n\n"
            "Pay off debts from **highest interest rate to lowest**.\n"
            "Mathematically optimal — saves the most money.\n\n"
            "**Next Step:** Share your debts for an exact comparison."
        ),
    },
]


# ── Matching engine ──────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def _similarity_score(query: str, keywords: list[str]) -> float:
    q = _normalize(query)
    if not q:
        return 0.0
    score = 0.0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in q:
            score += 50
            if len(kw_lower) / len(q) > 0.4:
                score += 30
    return min(score, 100.0)


def find_cached_response(query: str) -> Tuple[Optional[str], float]:
    """Look for a high-confidence cached response."""
    best_response = None
    best_score = 0.0

    for entry in CACHED_RESPONSES:
        score = _similarity_score(query, entry["keywords"])
        if score > best_score:
            best_score = score
            best_response = entry["response"]

    return (best_response, best_score) if best_score >= 50 else (None, 0.0)


# ── In-memory session cache (replaces st.session_state) ─────────────────

_session_cache: dict[str, dict[str, str]] = {}


def _cache_key(text: str) -> str:
    normalized = _normalize(text)
    return hashlib.md5(normalized.encode()).hexdigest()


def get_session_cached(session_id: str, query: str) -> Optional[str]:
    cache = _session_cache.get(session_id, {})
    return cache.get(_cache_key(query))


def set_session_cache(session_id: str, query: str, response: str) -> None:
    if session_id not in _session_cache:
        _session_cache[session_id] = {}
    _session_cache[session_id][_cache_key(query)] = response
