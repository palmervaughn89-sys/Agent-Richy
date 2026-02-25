"""Session state management for Agent Richy."""

import logging
from typing import Any

import streamlit as st

from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client
from config import FREE_MESSAGE_LIMIT

logger = logging.getLogger(__name__)


def init_session_state() -> None:
    """Initialize all session state variables with defaults. Call once on app startup."""
    defaults = {
        # User
        "profile": UserProfile(name="", age=0),
        "onboarded": False,
        "onboarding_step": 1,
        "is_premium": False,

        # LLM
        "llm_client": None,
        "llm_initialized": False,

        # Chat
        "chat_history": {},          # agent_key -> list of messages
        "active_agent": "coach_richy",
        "message_count": 0,          # For free tier limit

        # Financial plan
        "financial_plan": {},
        "plan_generated": False,
        "extraction_log": [],

        # Learning
        "completed_lessons": set(),
        "completed_videos": set(),
        "quiz_scores": {},
        "earned_badges": [],

        # Avatar
        "last_expression": "happy",
    }

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Initialize LLM client once
    if not st.session_state.llm_initialized:
        st.session_state.llm_client = get_openai_client()
        st.session_state.llm_initialized = True


def get_profile() -> UserProfile:
    """Get the current user profile from session state."""
    return st.session_state.get("profile", UserProfile(name="", age=0))


def get_chat_history(agent_key: str = None) -> list:
    """Get chat history for a specific agent.

    Args:
        agent_key: Agent key. Defaults to active agent.

    Returns:
        List of message dicts.
    """
    if agent_key is None:
        agent_key = st.session_state.get("active_agent", "coach_richy")
    histories = st.session_state.get("chat_history", {})
    if agent_key not in histories:
        histories[agent_key] = []
    return histories[agent_key]


def add_message(role: str, content: str, agent_key: str = None) -> None:
    """Add a message to chat history.

    Args:
        role: 'user' or 'assistant'.
        content: Message text.
        agent_key: Agent key. Defaults to active agent.
    """
    if agent_key is None:
        agent_key = st.session_state.get("active_agent", "coach_richy")
    history = get_chat_history(agent_key)
    history.append({"role": role, "content": content})

    if role == "user":
        st.session_state.message_count = st.session_state.get("message_count", 0) + 1


def is_message_limit_reached() -> bool:
    """Check if the free tier message limit has been reached."""
    if st.session_state.get("is_premium", False):
        return False
    return st.session_state.get("message_count", 0) >= FREE_MESSAGE_LIMIT


def can_access_premium(feature: str = "") -> bool:
    """Check if user can access a premium feature.

    Args:
        feature: Optional feature name for logging.

    Returns:
        True if premium access is allowed.
    """
    is_premium = st.session_state.get("is_premium", False)
    if not is_premium and feature:
        logger.info(f"Premium feature blocked: {feature}")
    return is_premium


def apply_extracted_data(data: dict) -> list[str]:
    """Apply extracted financial data from AI responses to profile and plan.

    Args:
        data: Dict of extracted financial data.

    Returns:
        List of change descriptions.
    """
    profile = get_profile()
    changes = []

    if "monthly_income" in data and data["monthly_income"]:
        profile.monthly_income = float(data["monthly_income"])
        changes.append(f"Income: ${profile.monthly_income:,.0f}/mo")

    if "monthly_expenses" in data and data["monthly_expenses"]:
        profile.monthly_expenses = float(data["monthly_expenses"])
        changes.append(f"Expenses: ${profile.monthly_expenses:,.0f}/mo")

    if "savings" in data and data["savings"]:
        profile.savings_balance = float(data["savings"])
        changes.append(f"Savings: ${profile.savings_balance:,.0f}")

    if "emergency_fund" in data and data["emergency_fund"]:
        profile.emergency_fund = float(data["emergency_fund"])
        changes.append(f"Emergency fund: ${profile.emergency_fund:,.0f}")

    if "credit_score" in data and data["credit_score"]:
        profile.credit_score = int(data["credit_score"])
        changes.append(f"Credit score: {profile.credit_score}")

    if "debts" in data and isinstance(data["debts"], dict):
        for name, info in data["debts"].items():
            if isinstance(info, dict):
                profile.debts[name] = float(info.get("balance", 0))
                profile.debt_interest_rates[name] = float(info.get("rate", 0))
                changes.append(f"Debt: {name} ${info.get('balance', 0):,.0f}")
            elif isinstance(info, (int, float)):
                profile.debts[name] = float(info)
                changes.append(f"Debt: {name} ${info:,.0f}")

    if "goals" in data and isinstance(data["goals"], list):
        profile.goals = data["goals"]
        changes.append(f"Goals: {', '.join(data['goals'])}")

    # Store plan components
    plan = st.session_state.financial_plan
    if "budget" in data:
        plan["budget"] = data["budget"]
        changes.append("Budget plan updated")
    if "recommendations" in data:
        plan["recommendations"] = data["recommendations"]
        changes.append("Recommendations updated")
    if "risk_level" in data:
        plan["risk_level"] = data["risk_level"]
        profile.risk_tolerance = data["risk_level"]

    if profile.monthly_income > 0 and profile.monthly_expenses > 0:
        profile.completed_assessment = True
    if plan.get("recommendations"):
        st.session_state.plan_generated = True

    if changes:
        st.session_state.extraction_log.append(changes)

    return changes


def complete_video(lesson_id: str) -> None:
    """Mark a video lesson as completed.

    Args:
        lesson_id: The lesson identifier.
    """
    st.session_state.completed_videos.add(lesson_id)
    _check_badges()


def _check_badges() -> None:
    """Check and award achievement badges based on progress."""
    from config import KIDS_MODULES
    completed = st.session_state.completed_videos
    badges = st.session_state.earned_badges

    for module in KIDS_MODULES:
        lesson_ids = {l["id"] for l in module["lessons"]}
        if lesson_ids.issubset(completed):
            badge = f"🏆 {module['title']}"
            if badge not in badges:
                badges.append(badge)
                st.toast(f"Achievement unlocked: {badge}!", icon="🏆")
