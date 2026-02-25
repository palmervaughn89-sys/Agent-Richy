"""Helper utilities for Agent Richy."""

import os
import re
from typing import Optional


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


def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text to a given width for cleaner CLI display."""
    words = text.split()
    lines = []
    current = []
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


def print_header(title: str) -> None:
    """Print a formatted section header."""
    border = "=" * 60
    print(f"\n{border}")
    print(f"  {title}")
    print(f"{border}\n")


def print_divider() -> None:
    """Print a thin divider line."""
    print("-" * 60)


def prompt(question: str) -> str:
    """Print a question and return the user's input stripped."""
    print(f"\n{question}")
    return input(">>> ").strip()
