"""Skill prompt loader — reads additional system prompt sections for detected skills."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

_SKILL_FILES = {
    "coupon": "coupon-finder.md",
    "optimizer": "spending-optimizer.md",
}

# In-memory cache so we only read from disk once per process
_cache: dict[str, str] = {}


def load_skill_prompt(skill: str) -> Optional[str]:
    """Load the additional system prompt for a detected skill.

    Args:
        skill: The detected skill key ("coupon" or "optimizer").

    Returns:
        The prompt text or None if not found / not a known skill.
    """
    if skill not in _SKILL_FILES:
        return None

    if skill in _cache:
        return _cache[skill]

    path = _PROMPTS_DIR / _SKILL_FILES[skill]
    if not path.is_file():
        logger.warning(f"Skill prompt file not found: {path}")
        return None

    try:
        text = path.read_text(encoding="utf-8")
        _cache[skill] = text
        logger.info(f"[skill-detection] Loaded prompt for skill: {skill}")
        return text
    except Exception as e:
        logger.error(f"Failed to read skill prompt {path}: {e}")
        return None


def build_skill_context(skill: Optional[str], optimizer_expenses: Optional[str] = None) -> str:
    """Build the full additional context string for a detected skill.

    Args:
        skill: Detected skill key or None.
        optimizer_expenses: Summary of user's known expenses (for optimizer continuity).

    Returns:
        Additional system prompt text to append, or empty string.
    """
    if not skill:
        return ""

    parts: list[str] = []

    prompt = load_skill_prompt(skill)
    if prompt:
        parts.append(prompt)

    if skill == "optimizer" and optimizer_expenses:
        parts.append(
            f"\n\n## USER'S KNOWN EXPENSES (from this session)\n{optimizer_expenses}"
        )

    return "\n\n".join(parts)
