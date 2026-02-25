"""Helper utilities for Agent Richy."""

import json
import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# OpenAI / LLM helpers
# ---------------------------------------------------------------------------

def get_openai_client():
    """Return an OpenAI client if the API key is configured, otherwise None."""
    try:
        import openai  # noqa: F401
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
    except ImportError:
        pass
    return None


def get_gemini_client():
    """Return a Google Generative AI client if API key is configured, otherwise None."""
    try:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai
    except ImportError:
        pass
    return None


def get_llm_client():
    """Return the best available LLM client — OpenAI first, Gemini fallback.

    Returns:
        Tuple of (client, provider_name) where provider is 'openai' or 'gemini',
        or (None, None) if no API key is configured.
    """
    openai_client = get_openai_client()
    if openai_client:
        return openai_client, "openai"
    gemini_client = get_gemini_client()
    if gemini_client:
        return gemini_client, "gemini"
    return None, None


def ask_llm(client, system_prompt: str, user_message: str, model: str = "gpt-4o") -> Optional[str]:
    """Send a message to the LLM and return the response text, or None on failure."""
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CLI formatting helpers
# ---------------------------------------------------------------------------

def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text to a given width for cleaner CLI display."""
    words = text.split()
    lines: List[str] = []
    current: List[str] = []
    current_len = 0
    for word in words:
        if current_len + len(word) + (1 if current else 0) > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + (1 if current_len else 0)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def format_currency(amount: float) -> str:
    """Format a float as a US dollar string."""
    return f"${amount:,.2f}"


def print_header(title: str) -> None:
    """Print a formatted section header."""
    border = "=" * 60
    print(f"\n{border}")
    print(f"  {title}")
    print(f"{border}\n")


def print_divider() -> None:
    """Print a thin divider line."""
    print("-" * 60)


def print_tip(text: str) -> None:
    """Print a highlighted tip line."""
    print(f"\n💡 {wrap_text(text)}")


def print_warning(text: str) -> None:
    """Print a highlighted warning."""
    print(f"\n⚠️  {wrap_text(text)}")


def print_success(text: str) -> None:
    """Print a highlighted success message."""
    print(f"\n✅ {wrap_text(text)}")


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def prompt(question: str) -> str:
    """Print a question and return the user's input stripped."""
    print(f"\n{question}")
    return input(">>> ").strip()


def parse_yes_no(response: str) -> Optional[bool]:
    """Parse a yes/no answer from user input. Returns True, False, or None."""
    r = response.strip().lower()
    if r in ("y", "yes", "yeah", "yep", "sure", "absolutely", "1"):
        return True
    if r in ("n", "no", "nope", "nah", "0"):
        return False
    return None


def parse_number(response: str) -> Optional[float]:
    """Extract a numeric value from user input."""
    cleaned = re.sub(r"[,$%]", "", response.strip())
    try:
        return float(cleaned)
    except ValueError:
        return None


def choose_one(label: str, options: List[str]) -> Optional[int]:
    """Display numbered options and return selected 0-based index, or None."""
    print(f"\n{label}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    raw = prompt("Choose a number:")
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return idx
    print("Invalid choice.")
    return None


def choose_many(label: str, options: List[str]) -> List[int]:
    """Display numbered options and let user pick several (comma-separated).
    Returns list of 0-based indices.
    """
    print(f"\n{label}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    raw = prompt("Enter numbers separated by commas (e.g. 1,3,5):")
    chosen: List[int] = []
    for part in raw.replace(" ", "").split(","):
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(options):
                chosen.append(idx)
    return chosen


# ---------------------------------------------------------------------------
# Data loader for investments.json
# ---------------------------------------------------------------------------

_INVESTMENTS_CACHE: Optional[Dict[str, Any]] = None


def load_investments() -> Dict[str, Any]:
    """Load data/investments.json once and cache it."""
    global _INVESTMENTS_CACHE
    if _INVESTMENTS_CACHE is not None:
        return _INVESTMENTS_CACHE
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "investments.json"
    try:
        with open(data_path, "r") as f:
            _INVESTMENTS_CACHE = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _INVESTMENTS_CACHE = {}
    return _INVESTMENTS_CACHE


def filter_investments(
    risk: Optional[str] = None,
    themes: Optional[List[str]] = None,
    esg_min: Optional[str] = None,
    asset_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return instruments from investments.json matching the given filters."""
    data = load_investments()
    esg_rank = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "N/A": 0}
    min_esg = esg_rank.get(esg_min, 0) if esg_min else 0

    results: List[Dict[str, Any]] = []
    categories = [asset_type] if asset_type else list(data.keys())
    for cat in categories:
        for item in data.get(cat, []):
            if risk and item.get("risk") != risk:
                continue
            if themes and not any(t.lower() in [x.lower() for x in item.get("themes", [])] for t in themes):
                continue
            if min_esg and esg_rank.get(item.get("esg_score", "N/A"), 0) < min_esg:
                continue
            results.append(item)
    return results


def progress_bar(current: float, target: float, width: int = 30) -> str:
    """Return a simple ASCII progress bar string."""
    if target <= 0:
        return "[" + "?" * width + "]"
    pct = min(current / target, 1.0)
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct * 100:.0f}%"
