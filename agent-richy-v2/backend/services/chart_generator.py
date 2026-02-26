"""Chart generator service.

Takes financial calculator outputs and generates Recharts-compatible chart configs.
"""

from typing import Optional
from models.structured_response import ChartConfig


def generate_charts_from_calculator(
    calc_name: str,
    calc_result: dict,
) -> list[ChartConfig]:
    """Generate Recharts chart configs from calculator results."""
    charts: list[ChartConfig] = []

    if not calc_result or "error" in calc_result:
        return charts

    if calc_name == "compound_interest":
        year_by_year = calc_result.get("year_by_year", [])
        if year_by_year:
            charts.append(ChartConfig(
                type="area",
                title="Investment Growth Over Time",
                data=[
                    {
                        "year": f"Year {item['year']}",
                        "balance": item["balance"],
                        "contributed": item["contributed"],
                        "interest": item["interest_earned"],
                    }
                    for item in year_by_year
                ],
                x_key="year",
                y_key="balance",
                color="#10B981",
            ))

    elif calc_name == "debt_payoff":
        month_data = calc_result.get("month_by_month", [])
        if month_data:
            charts.append(ChartConfig(
                type="line",
                title="Debt Payoff Timeline",
                data=[
                    {
                        "month": f"Month {item['month']}",
                        "remaining": item["remaining"],
                        "principal": item["principal"],
                        "interest": item["interest"],
                    }
                    for item in month_data[:48]  # Cap at 4 years for readability
                ],
                x_key="month",
                y_key="remaining",
                color="#EF4444",
            ))

    elif calc_name == "debt_snowball_vs_avalanche":
        snowball = calc_result.get("snowball", {})
        avalanche = calc_result.get("avalanche", {})
        charts.append(ChartConfig(
            type="bar",
            title="Snowball vs Avalanche Comparison",
            data=[
                {
                    "strategy": "Snowball",
                    "months": snowball.get("months", 0),
                    "total_interest": snowball.get("total_interest", 0),
                },
                {
                    "strategy": "Avalanche",
                    "months": avalanche.get("months", 0),
                    "total_interest": avalanche.get("total_interest", 0),
                },
            ],
            x_key="strategy",
            y_key="total_interest",
            color="#F59E0B",
        ))

    elif calc_name == "budget_50_30_20":
        recommended = calc_result.get("recommended", {})
        if recommended:
            charts.append(ChartConfig(
                type="pie",
                title="50/30/20 Budget Breakdown",
                data=[
                    {"name": "Needs (50%)", "value": recommended.get("needs", 0)},
                    {"name": "Wants (30%)", "value": recommended.get("wants", 0)},
                    {"name": "Savings (20%)", "value": recommended.get("savings", 0)},
                ],
                x_key="name",
                y_key="value",
                color="#2563EB",
            ))

    elif calc_name == "emergency_fund_status":
        current = calc_result.get("current_savings", 0)
        target_3 = calc_result.get("target_3_months", 0)
        target_6 = calc_result.get("target_6_months", 0)
        charts.append(ChartConfig(
            type="bar",
            title="Emergency Fund Progress",
            data=[
                {"label": "Current", "amount": current},
                {"label": "3-Month Target", "amount": target_3},
                {"label": "6-Month Target", "amount": target_6},
            ],
            x_key="label",
            y_key="amount",
            color="#8B5CF6",
        ))

    elif calc_name == "savings_goal_timeline":
        goal = calc_result.get("goal_amount", 0)
        monthly = calc_result.get("monthly_contribution", 0)
        months = calc_result.get("months_to_goal", 0)
        if months > 0 and monthly > 0:
            data = []
            running = 0
            for m in range(1, min(months + 1, 61)):
                running += monthly
                data.append({"month": f"Month {m}", "saved": round(running, 2), "goal": goal})
            charts.append(ChartConfig(
                type="area",
                title="Savings Goal Progress",
                data=data,
                x_key="month",
                y_key="saved",
                color="#10B981",
            ))

    return charts
