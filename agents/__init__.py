"""Agent registry — factory and routing for all Agent Richy agents."""

from agents.base_agent import BaseAgent
from agents.coach_richy import CoachRichy
from agents.budget_bot import BudgetBot
from agents.invest_intel import InvestIntel
from agents.debt_destroyer import DebtDestroyer
from agents.savings_sage import SavingsSage
from agents.kid_coach import KidCoach

# Singleton agent instances
_agents: dict[str, BaseAgent] = {}


def get_agent(agent_key: str) -> BaseAgent:
    """Get or create an agent instance by key.

    Args:
        agent_key: One of 'coach_richy', 'budget_bot', 'invest_intel',
                   'debt_destroyer', 'savings_sage', 'kid_coach'.

    Returns:
        The corresponding BaseAgent instance.
    """
    if agent_key not in _agents:
        _agents[agent_key] = _create_agent(agent_key)
    return _agents[agent_key]


def _create_agent(agent_key: str) -> BaseAgent:
    """Factory method to create agent instances."""
    mapping = {
        "coach_richy": CoachRichy,
        "budget_bot": BudgetBot,
        "invest_intel": InvestIntel,
        "debt_destroyer": DebtDestroyer,
        "savings_sage": SavingsSage,
        "kid_coach": KidCoach,
    }
    cls = mapping.get(agent_key)
    if not cls:
        raise ValueError(f"Unknown agent key: {agent_key}")
    return cls()


def get_all_agents() -> dict[str, BaseAgent]:
    """Get all available agents."""
    keys = ["coach_richy", "budget_bot", "invest_intel",
            "debt_destroyer", "savings_sage", "kid_coach"]
    return {k: get_agent(k) for k in keys}


def route_to_agent(message: str, current_agent: str = "coach_richy") -> str:
    """Suggest the best agent for a given user message.

    Args:
        message: The user's message text.
        current_agent: Currently active agent key.

    Returns:
        Suggested agent key.
    """
    topic = BaseAgent.detect_topic(message)
    suggested = BaseAgent.suggest_agent(topic)

    # Only suggest switching if the topic is clearly different
    if suggested != current_agent and topic != "general":
        return suggested
    return current_agent
