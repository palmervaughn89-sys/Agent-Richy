"""Backward-compatible UserProfile dataclass for agent consumption.

The v2 backend uses Pydantic models (models/profile.py) for API I/O,
but the migrated agents were written against the original dataclass.
This module provides a lightweight dataclass that keeps agent code working
without pulling in the parent ``agent_richy`` package.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class UserProfile:
    """In-process user profile consumed by agents.

    Field names deliberately mirror the original agent_richy.profiles.UserProfile
    so that ``get_system_prompt``, ``_offline_response``, and ``_build_known_data``
    work without changes.
    """

    name: str = "Friend"
    user_type: str = "unknown"        # "youth" | "adult"
    grade_level: Optional[str] = None  # "middle" | "high" for youth
    age: Optional[int] = None

    # ── Adult financial snapshot ──
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    savings_balance: float = 0.0
    debt_balance: float = 0.0
    emergency_fund: float = 0.0
    credit_score: Optional[int] = None

    # Detailed debt tracking (label -> amount)
    debts: Dict[str, float] = field(default_factory=dict)
    debt_interest_rates: Dict[str, float] = field(default_factory=dict)

    # Subscription tracking (name -> monthly cost)
    subscriptions: Dict[str, float] = field(default_factory=dict)

    # Paycheck-to-paycheck flag
    paycheck_to_paycheck: bool = False

    # Bad financial habits the user self-identifies
    bad_habits: List[str] = field(default_factory=list)

    # Goals
    goals: List[str] = field(default_factory=list)
    vacation_fund: float = 0.0
    vacation_target: float = 0.0
    vacation_deadline_months: int = 0

    # ── Youth-specific ──
    talents: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    has_job: bool = False
    job_description: str = ""
    weekly_hours: float = 0.0
    hourly_rate: float = 0.0
    allowance: float = 0.0
    side_hustles: List[str] = field(default_factory=list)

    # ── Investment preferences ──
    investment_types: List[str] = field(default_factory=list)
    risk_tolerance: str = "medium"
    themes: List[str] = field(default_factory=list)
    esg_preference: bool = False

    # ── Session flags ──
    completed_assessment: bool = False
    sessions_count: int = 0

    # ── Helpers ──

    def is_youth(self) -> bool:
        return self.user_type == "youth"

    def is_adult(self) -> bool:
        return self.user_type == "adult"

    def monthly_surplus(self) -> float:
        return self.monthly_income - self.monthly_expenses

    def savings_rate(self) -> float:
        if self.monthly_income == 0:
            return 0.0
        surplus = self.monthly_surplus()
        return max(0.0, (surplus / self.monthly_income) * 100)

    def total_debt(self) -> float:
        return sum(self.debts.values()) if self.debts else self.debt_balance

    def total_subscriptions(self) -> float:
        return sum(self.subscriptions.values())

    def youth_monthly_income(self) -> float:
        job_income = self.hourly_rate * self.weekly_hours * 4.33
        return job_income + self.allowance

    def months_of_emergency(self) -> float:
        if self.monthly_expenses <= 0:
            return 0.0
        return self.emergency_fund / self.monthly_expenses

    def debt_to_income_ratio(self) -> float:
        if self.monthly_income <= 0:
            return 0.0
        monthly_debt_payments = sum(self.debts.values()) * 0.02  # rough min payment
        return (monthly_debt_payments / self.monthly_income) * 100
