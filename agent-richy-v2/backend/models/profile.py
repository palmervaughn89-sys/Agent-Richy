"""Pydantic models for financial profile."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class FinancialProfile(BaseModel):
    """User financial profile model."""
    id: Optional[str] = None
    name: str = "Friend"
    age: Optional[int] = None
    user_type: str = "adult"  # "youth" | "adult"

    # Income & expenses
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    savings_balance: float = 0.0
    emergency_fund: float = 0.0
    credit_score: Optional[int] = None

    # Debts
    debts: Dict[str, float] = Field(default_factory=dict)
    debt_interest_rates: Dict[str, float] = Field(default_factory=dict)

    # Goals & preferences
    goals: List[str] = Field(default_factory=list)
    risk_tolerance: str = "medium"

    # Experience
    experience_level: Optional[str] = None
    employment_status: Optional[str] = None

    def monthly_surplus(self) -> float:
        return self.monthly_income - self.monthly_expenses

    def total_debt(self) -> float:
        return sum(self.debts.values())


class ProfileUpdate(BaseModel):
    """Partial profile update."""
    name: Optional[str] = None
    age: Optional[int] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    savings_balance: Optional[float] = None
    emergency_fund: Optional[float] = None
    credit_score: Optional[int] = None
    debts: Optional[Dict[str, float]] = None
    debt_interest_rates: Optional[Dict[str, float]] = None
    goals: Optional[List[str]] = None
    risk_tolerance: Optional[str] = None
    experience_level: Optional[str] = None
    employment_status: Optional[str] = None
