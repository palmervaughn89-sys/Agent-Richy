"""User profile management for Agent Richy."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class UserProfile:
    """Stores information about the current user session."""

    name: str = "Friend"
    user_type: str = "unknown"          # "youth" | "adult"
    grade_level: Optional[str] = None   # "middle" | "high" for youth
    age: Optional[int] = None

    # Adult financial snapshot
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    savings_balance: float = 0.0
    debt_balance: float = 0.0

    # Goals (adults)
    goals: List[str] = field(default_factory=list)

    # Robo Agent preferences
    investment_types: List[str] = field(default_factory=list)
    risk_tolerance: str = "medium"       # "low" | "medium" | "high" | "very high"
    themes: List[str] = field(default_factory=list)
    esg_preference: bool = False

    def is_youth(self) -> bool:
        return self.user_type == "youth"

    def is_adult(self) -> bool:
        return self.user_type == "adult"

    def monthly_surplus(self) -> float:
        return self.monthly_income - self.monthly_expenses

    def savings_rate(self) -> float:
        """Return savings rate as a percentage of income."""
        if self.monthly_income == 0:
            return 0.0
        surplus = self.monthly_surplus()
        return max(0.0, (surplus / self.monthly_income) * 100)
