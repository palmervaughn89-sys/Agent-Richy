"""Agent registry — factory and routing for all Agent Richy agents."""

from agents.base_agent import BaseAgent
from agents.coach_richy import CoachRichy
from agents.budget_bot import BudgetBot
from agents.invest_intel import InvestIntel
from agents.debt_destroyer import DebtDestroyer
from agents.savings_sage import SavingsSage
from agents.kid_coach import KidCoach

_agents: dict[str, BaseAgent] = {}


def get_agent(agent_key: str) -> BaseAgent:
    if agent_key not in _agents:
        _agents[agent_key] = _create_agent(agent_key)
    return _agents[agent_key]


def _create_agent(agent_key: str) -> BaseAgent:
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
    keys = ["coach_richy", "budget_bot", "invest_intel",
            "debt_destroyer", "savings_sage", "kid_coach"]
    return {k: get_agent(k) for k in keys}


def route_to_agent(message: str, current_agent: str = "coach_richy") -> str:
    topic = BaseAgent.detect_topic(message)
    suggested = BaseAgent.suggest_agent(topic)
    if suggested != current_agent and topic != "general":
        return suggested
    return current_agent
