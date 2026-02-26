"""Calculators router — /api/calculators."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from core.financial_calculators import (
    compound_interest,
    debt_payoff,
    debt_snowball_vs_avalanche,
    emergency_fund_status,
    budget_50_30_20,
    savings_goal_timeline,
    net_worth_calculator,
)
from services.chart_generator import generate_charts_from_calculator

router = APIRouter(prefix="/api/calculators", tags=["calculators"])


class CompoundInterestRequest(BaseModel):
    principal: float
    annual_rate: float = 8.0
    years: int = 30
    monthly_contribution: float = 0


class DebtPayoffRequest(BaseModel):
    balance: float
    apr: float
    monthly_payment: float


class DebtCompareRequest(BaseModel):
    debts: List[Dict]


class EmergencyFundRequest(BaseModel):
    monthly_expenses: float
    current_savings: float = 0


class BudgetRequest(BaseModel):
    monthly_income: float
    current_expenses: Optional[Dict] = None


class SavingsGoalRequest(BaseModel):
    goal_amount: float
    current_savings: float = 0
    monthly_contribution: float = 100
    annual_return: float = 0


class NetWorthRequest(BaseModel):
    assets: Dict[str, float]
    liabilities: Dict[str, float]


def _with_charts(calc_name: str, result: dict) -> dict:
    """Attach chart configs to calculator result."""
    charts = generate_charts_from_calculator(calc_name, result)
    result["charts"] = [c.model_dump() for c in charts]
    return result


@router.post("/compound-interest")
async def calc_compound_interest(req: CompoundInterestRequest):
    result = compound_interest(req.principal, req.annual_rate, req.years, req.monthly_contribution)
    return _with_charts("compound_interest", result)


@router.post("/debt-payoff")
async def calc_debt_payoff(req: DebtPayoffRequest):
    result = debt_payoff(req.balance, req.apr, req.monthly_payment)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return _with_charts("debt_payoff", result)


@router.post("/debt-compare")
async def calc_debt_compare(req: DebtCompareRequest):
    result = debt_snowball_vs_avalanche(req.debts)
    return _with_charts("debt_snowball_vs_avalanche", result)


@router.post("/emergency-fund")
async def calc_emergency_fund(req: EmergencyFundRequest):
    result = emergency_fund_status(req.monthly_expenses, req.current_savings)
    return _with_charts("emergency_fund_status", result)


@router.post("/budget")
async def calc_budget(req: BudgetRequest):
    result = budget_50_30_20(req.monthly_income, req.current_expenses)
    return _with_charts("budget_50_30_20", result)


@router.post("/savings-goal")
async def calc_savings_goal(req: SavingsGoalRequest):
    result = savings_goal_timeline(req.goal_amount, req.current_savings, req.monthly_contribution, req.annual_return)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return _with_charts("savings_goal_timeline", result)


@router.post("/net-worth")
async def calc_net_worth(req: NetWorthRequest):
    result = net_worth_calculator(req.assets, req.liabilities)
    return _with_charts("net_worth_calculator", result)
