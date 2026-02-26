"""Precise financial calculator tools for Agent Richy.

These functions give agents EXACT math instead of LLM approximations.
Every function returns a dict with detailed breakdowns.
"""

import math
from typing import Dict, List, Optional


def compound_interest(principal: float, annual_rate: float, years: int,
                      monthly_contribution: float = 0) -> Dict:
    """Calculate compound interest with optional monthly contributions."""
    monthly_rate = annual_rate / 100 / 12
    months = years * 12
    year_by_year = []

    balance = principal
    total_contributed = principal

    for month in range(1, months + 1):
        balance = balance * (1 + monthly_rate) + monthly_contribution
        total_contributed += monthly_contribution
        if month % 12 == 0:
            year_by_year.append({
                "year": month // 12,
                "balance": round(balance, 2),
                "contributed": round(total_contributed, 2),
                "interest_earned": round(balance - total_contributed, 2),
            })

    return {
        "final_amount": round(balance, 2),
        "total_contributed": round(total_contributed, 2),
        "total_interest": round(balance - total_contributed, 2),
        "year_by_year": year_by_year,
    }


def debt_payoff(balance: float, apr: float, monthly_payment: float) -> Dict:
    """Calculate debt payoff timeline."""
    monthly_rate = apr / 100 / 12
    remaining = balance
    total_paid = 0.0
    total_interest = 0.0
    months = 0
    month_by_month = []

    while remaining > 0.01 and months < 600:
        interest = remaining * monthly_rate
        if monthly_payment <= interest:
            return {
                "error": (
                    f"Payment too low — doesn't cover interest. "
                    f"Need at least ${interest + 1:.2f}/month"
                )
            }
        principal_payment = min(monthly_payment - interest, remaining)
        remaining -= principal_payment
        total_paid += monthly_payment
        total_interest += interest
        months += 1

        if months <= 60 or months % 12 == 0:
            month_by_month.append({
                "month": months,
                "payment": round(monthly_payment, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest, 2),
                "remaining": round(max(remaining, 0), 2),
            })

    return {
        "months_to_payoff": months,
        "years_to_payoff": round(months / 12, 1),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "month_by_month": month_by_month,
    }


def debt_snowball_vs_avalanche(debts: List[Dict]) -> Dict:
    """Compare snowball (smallest balance) vs avalanche (highest interest)."""

    def _simulate(debts_list, sort_key):
        copies = [d.copy() for d in debts_list]
        copies.sort(key=sort_key)
        total_interest = 0.0
        months = 0
        payoff_order = []

        while any(d["balance"] > 0.01 for d in copies) and months < 600:
            months += 1
            extra = 0.0
            for debt in copies:
                if debt["balance"] <= 0.01:
                    extra += debt["min_payment"]
                    continue
                interest = debt["balance"] * (debt["apr"] / 100 / 12)
                total_interest += interest
                payment = debt["min_payment"] + extra
                extra = 0.0
                debt["balance"] = max(0, debt["balance"] + interest - payment)
                if debt["balance"] <= 0.01:
                    if debt["name"] not in [p["name"] for p in payoff_order]:
                        payoff_order.append({"name": debt["name"], "month": months})
        return {
            "months": months,
            "years": round(months / 12, 1),
            "total_interest": round(total_interest, 2),
            "payoff_order": payoff_order,
        }

    snowball = _simulate(debts, lambda d: d["balance"])
    avalanche = _simulate(debts, lambda d: -d["apr"])
    saved = round(snowball["total_interest"] - avalanche["total_interest"], 2)

    return {
        "snowball": snowball,
        "avalanche": avalanche,
        "interest_saved_with_avalanche": saved,
        "recommendation": "avalanche" if saved > 0 else "snowball",
    }


def emergency_fund_status(monthly_expenses: float,
                          current_savings: float) -> Dict:
    """Evaluate emergency fund health."""
    months_covered = (current_savings / monthly_expenses
                      if monthly_expenses > 0 else 0)
    target_3 = monthly_expenses * 3
    target_6 = monthly_expenses * 6

    if months_covered >= 6:
        status, msg = "excellent", "Strong emergency fund! Consider investing excess."
    elif months_covered >= 3:
        status, msg = "good", "Good shape. Try to build toward 6 months."
    elif months_covered >= 1:
        status, msg = "needs_work", "You have a start — aim for 3 months minimum."
    else:
        status, msg = "critical", "Building an emergency fund should be your top priority."

    return {
        "months_covered": round(months_covered, 1),
        "current_savings": current_savings,
        "target_3_months": round(target_3, 2),
        "target_6_months": round(target_6, 2),
        "gap_to_3_months": round(max(0, target_3 - current_savings), 2),
        "gap_to_6_months": round(max(0, target_6 - current_savings), 2),
        "status": status,
        "message": msg,
    }


def budget_50_30_20(monthly_income: float,
                    current_expenses: Optional[Dict] = None) -> Dict:
    """Calculate 50/30/20 budget breakdown."""
    recommended = {
        "needs": round(monthly_income * 0.50, 2),
        "wants": round(monthly_income * 0.30, 2),
        "savings": round(monthly_income * 0.20, 2),
    }
    result: Dict = {"monthly_income": monthly_income, "recommended": recommended}

    if current_expenses:
        result["current"] = current_expenses
        result["adjustments"] = {}
        for cat in ("needs", "wants", "savings"):
            current = current_expenses.get(cat, 0)
            diff = current - recommended[cat]
            result["adjustments"][cat] = {
                "current": current,
                "recommended": recommended[cat],
                "difference": round(diff, 2),
                "status": "over" if diff > 0 else ("under" if diff < 0 else "on_track"),
            }
    return result


def savings_goal_timeline(goal_amount: float, current_savings: float,
                          monthly_contribution: float,
                          annual_return: float = 0) -> Dict:
    """Calculate timeline to reach a savings goal."""
    remaining = goal_amount - current_savings
    if remaining <= 0:
        return {"already_reached": True, "surplus": round(-remaining, 2)}
    if monthly_contribution <= 0:
        return {"error": "Need a positive monthly contribution to reach your goal."}

    if annual_return == 0:
        months = math.ceil(remaining / monthly_contribution)
    else:
        r = annual_return / 100 / 12
        months = math.ceil(
            math.log(1 + (remaining * r / monthly_contribution))
            / math.log(1 + r)
        )

    return {
        "months_to_goal": months,
        "years_to_goal": round(months / 12, 1),
        "total_contributed": round(months * monthly_contribution, 2),
        "goal_amount": goal_amount,
        "monthly_contribution": monthly_contribution,
    }


def net_worth_calculator(assets: Dict, liabilities: Dict) -> Dict:
    """Calculate net worth from assets and liabilities."""
    total_a = sum(assets.values())
    total_l = sum(liabilities.values())
    nw = total_a - total_l
    return {
        "assets": assets,
        "total_assets": round(total_a, 2),
        "liabilities": liabilities,
        "total_liabilities": round(total_l, 2),
        "net_worth": round(nw, 2),
        "debt_to_asset_ratio": round(total_l / total_a * 100, 1) if total_a > 0 else 0,
    }


CALCULATOR_REGISTRY = {
    "compound_interest": compound_interest,
    "debt_payoff": debt_payoff,
    "debt_snowball_vs_avalanche": debt_snowball_vs_avalanche,
    "emergency_fund_status": emergency_fund_status,
    "budget_50_30_20": budget_50_30_20,
    "savings_goal_timeline": savings_goal_timeline,
    "net_worth_calculator": net_worth_calculator,
}
