"""Financial calculation utilities for Agent Richy."""

import math
from typing import Optional


def compound_growth(monthly_contribution: float, annual_rate: float,
                    years: int, initial_balance: float = 0.0) -> float:
    """Calculate compound growth of regular monthly contributions.

    Args:
        monthly_contribution: Monthly investment amount.
        annual_rate: Annual return rate (e.g., 0.07 for 7%).
        years: Number of years.
        initial_balance: Starting balance.

    Returns:
        Future value after compound growth.
    """
    monthly_rate = annual_rate / 12
    months = years * 12
    balance = initial_balance
    for _ in range(months):
        balance = balance * (1 + monthly_rate) + monthly_contribution
    return balance


def debt_payoff_schedule(balance: float, annual_rate: float,
                         monthly_payment: float) -> list[dict]:
    """Calculate month-by-month debt payoff schedule.

    Args:
        balance: Current debt balance.
        annual_rate: Annual interest rate (e.g., 0.22 for 22%).
        monthly_payment: Monthly payment amount.

    Returns:
        List of dicts with month, payment, interest, principal, remaining.
    """
    if balance <= 0 or monthly_payment <= 0:
        return []
    monthly_rate = annual_rate / 12
    if monthly_payment <= balance * monthly_rate:
        return []  # Payment doesn't cover interest

    schedule = []
    month = 0
    remaining = balance

    while remaining > 0.01 and month < 600:
        month += 1
        interest = remaining * monthly_rate
        payment = min(monthly_payment, remaining + interest)
        principal = payment - interest
        remaining = max(0, remaining - principal)

        schedule.append({
            "month": month,
            "payment": round(payment, 2),
            "interest": round(interest, 2),
            "principal": round(principal, 2),
            "remaining": round(remaining, 2),
        })

    return schedule


def months_to_goal(goal_amount: float, monthly_savings: float,
                   current_balance: float = 0.0,
                   annual_rate: float = 0.045) -> int:
    """Calculate months needed to reach a savings goal.

    Args:
        goal_amount: Target amount.
        monthly_savings: Monthly savings contribution.
        current_balance: Current savings balance.
        annual_rate: Annual interest rate (HYSA).

    Returns:
        Number of months to reach goal.
    """
    if monthly_savings <= 0:
        return 0

    monthly_rate = annual_rate / 12
    balance = current_balance
    months = 0

    while balance < goal_amount and months < 600:
        months += 1
        balance = balance * (1 + monthly_rate) + monthly_savings

    return months


def estimate_federal_tax(annual_income: float,
                         filing_status: str = "single") -> dict:
    """Estimate federal income tax.

    Args:
        annual_income: Annual gross income.
        filing_status: 'single' or 'married'.

    Returns:
        Dict with tax breakdown details.
    """
    # 2024 tax brackets
    if filing_status == "married":
        standard_deduction = 29_200
        brackets = [
            (23_200, 0.10),
            (94_300 - 23_200, 0.12),
            (201_050 - 94_300, 0.22),
            (383_900 - 201_050, 0.24),
            (487_450 - 383_900, 0.32),
            (731_200 - 487_450, 0.35),
            (float("inf"), 0.37),
        ]
    else:
        standard_deduction = 14_600
        brackets = [
            (11_600, 0.10),
            (47_150 - 11_600, 0.12),
            (100_525 - 47_150, 0.22),
            (191_950 - 100_525, 0.24),
            (243_725 - 191_950, 0.32),
            (609_350 - 243_725, 0.35),
            (float("inf"), 0.37),
        ]

    taxable = max(0, annual_income - standard_deduction)
    federal_tax = 0.0
    remaining = taxable

    for bracket_size, rate in brackets:
        if remaining <= 0:
            break
        taxed = min(remaining, bracket_size)
        federal_tax += taxed * rate
        remaining -= taxed

    # FICA
    ss_tax = min(annual_income, 168_600) * 0.062
    medicare_tax = annual_income * 0.0145
    if annual_income > 200_000:
        medicare_tax += (annual_income - 200_000) * 0.009
    fica_tax = ss_tax + medicare_tax

    total_tax = federal_tax + fica_tax
    take_home = annual_income - total_tax
    effective_rate = (total_tax / annual_income * 100) if annual_income > 0 else 0

    return {
        "gross_income": annual_income,
        "standard_deduction": standard_deduction,
        "taxable_income": taxable,
        "federal_tax": federal_tax,
        "fica_tax": fica_tax,
        "total_tax": total_tax,
        "take_home": take_home,
        "effective_rate": effective_rate,
    }


def mortgage_payment(principal: float, annual_rate: float,
                     years: int = 30) -> dict:
    """Calculate monthly mortgage payment.

    Args:
        principal: Loan amount.
        annual_rate: Annual interest rate (e.g., 0.065 for 6.5%).
        years: Loan term in years.

    Returns:
        Dict with payment details.
    """
    monthly_rate = annual_rate / 12
    num_payments = years * 12

    if monthly_rate == 0:
        monthly = principal / num_payments
    else:
        monthly = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                  ((1 + monthly_rate) ** num_payments - 1)

    total_paid = monthly * num_payments
    total_interest = total_paid - principal

    return {
        "monthly_payment": monthly,
        "total_paid": total_paid,
        "total_interest": total_interest,
        "principal": principal,
    }


def savings_rate_pct(income: float, expenses: float) -> float:
    """Calculate savings rate as a percentage.

    Args:
        income: Monthly income.
        expenses: Monthly expenses.

    Returns:
        Savings rate percentage.
    """
    if income <= 0:
        return 0.0
    surplus = income - expenses
    return max(0.0, (surplus / income) * 100)


def debt_to_income(monthly_debt_payments: float, monthly_income: float) -> float:
    """Calculate debt-to-income ratio.

    Args:
        monthly_debt_payments: Total monthly debt payments.
        monthly_income: Monthly gross income.

    Returns:
        DTI ratio as a percentage.
    """
    if monthly_income <= 0:
        return 0.0
    return (monthly_debt_payments / monthly_income) * 100


def emergency_fund_months(fund_balance: float, monthly_expenses: float) -> float:
    """Calculate emergency fund coverage in months.

    Args:
        fund_balance: Current emergency fund balance.
        monthly_expenses: Monthly expenses.

    Returns:
        Months of coverage.
    """
    if monthly_expenses <= 0:
        return 0.0
    return fund_balance / monthly_expenses
