"""Portfolio Builder — age + risk + timeline → specific ETF allocation.
Lazy portfolios: 3-fund (VTI/VXUS/BND), target-date equivalent,
all-weather. Historical returns, max drawdown, expense ratios.
Rebalancing reminders.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# ETF DATABASE
# ═══════════════════════════════════════════════════════════════════════════

_ETFS: dict[str, dict[str, Any]] = {
    "VTI":  {"name": "Vanguard Total Stock Market",   "asset": "US Stock",
             "er": 0.03, "hist_return": 10.3, "max_dd": -50.9, "div_yield": 1.4},
    "VOO":  {"name": "Vanguard S&P 500",              "asset": "US Stock",
             "er": 0.03, "hist_return": 10.5, "max_dd": -50.3, "div_yield": 1.3},
    "VXUS": {"name": "Vanguard Total International",  "asset": "Intl Stock",
             "er": 0.07, "hist_return": 5.4,  "max_dd": -56.0, "div_yield": 3.2},
    "BND":  {"name": "Vanguard Total Bond Market",    "asset": "US Bond",
             "er": 0.03, "hist_return": 3.5,  "max_dd": -17.8, "div_yield": 3.8},
    "BNDX": {"name": "Vanguard Total Intl Bond",      "asset": "Intl Bond",
             "er": 0.07, "hist_return": 2.8,  "max_dd": -12.5, "div_yield": 3.3},
    "VNQ":  {"name": "Vanguard Real Estate (REIT)",    "asset": "REIT",
             "er": 0.12, "hist_return": 8.2,  "max_dd": -68.3, "div_yield": 3.7},
    "GLD":  {"name": "SPDR Gold Shares",               "asset": "Commodity",
             "er": 0.40, "hist_return": 7.5,  "max_dd": -42.9, "div_yield": 0.0},
    "TLT":  {"name": "iShares 20+ Year Treasury",     "asset": "Long Bond",
             "er": 0.15, "hist_return": 4.2,  "max_dd": -44.7, "div_yield": 3.9},
    "VTIP": {"name": "Vanguard Short-Term TIPS",       "asset": "TIPS",
             "er": 0.04, "hist_return": 3.0,  "max_dd": -5.2,  "div_yield": 5.2},
    "SCHD": {"name": "Schwab US Dividend Equity",     "asset": "US Dividend",
             "er": 0.06, "hist_return": 11.4, "max_dd": -32.1, "div_yield": 3.5},
    "AVUV": {"name": "Avantis US Small Cap Value",    "asset": "US Small Value",
             "er": 0.25, "hist_return": 12.8, "max_dd": -45.0, "div_yield": 1.8},
    "QQQ":  {"name": "Invesco Nasdaq 100",            "asset": "US Growth",
             "er": 0.20, "hist_return": 14.0, "max_dd": -82.0, "div_yield": 0.6},
}

# ═══════════════════════════════════════════════════════════════════════════
# LAZY PORTFOLIO TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

_LAZY_PORTFOLIOS: dict[str, dict[str, Any]] = {
    "three_fund": {
        "name": "3-Fund Portfolio (Bogleheads Classic)",
        "description": "Simple, diversified, low-cost core portfolio",
        "holdings": {
            "VTI":  {"base_pct": 60, "type": "equity"},
            "VXUS": {"base_pct": 20, "type": "equity"},
            "BND":  {"base_pct": 20, "type": "bond"},
        },
    },
    "four_fund": {
        "name": "4-Fund Portfolio",
        "description": "3-Fund + international bonds for global diversification",
        "holdings": {
            "VTI":  {"base_pct": 50, "type": "equity"},
            "VXUS": {"base_pct": 20, "type": "equity"},
            "BND":  {"base_pct": 20, "type": "bond"},
            "BNDX": {"base_pct": 10, "type": "bond"},
        },
    },
    "all_weather": {
        "name": "All-Weather Portfolio (Ray Dalio-inspired)",
        "description": "Designed to perform in any economic environment",
        "holdings": {
            "VTI":  {"base_pct": 30, "type": "equity"},
            "TLT":  {"base_pct": 40, "type": "bond"},
            "BND":  {"base_pct": 15, "type": "bond"},
            "GLD":  {"base_pct": 7.5, "type": "commodity"},
            "VTIP": {"base_pct": 7.5, "type": "tips"},
        },
    },
    "income_focus": {
        "name": "Income / Dividend Portfolio",
        "description": "Emphasizes dividend yield + bond income",
        "holdings": {
            "SCHD": {"base_pct": 40, "type": "equity"},
            "VTI":  {"base_pct": 15, "type": "equity"},
            "VNQ":  {"base_pct": 15, "type": "reit"},
            "BND":  {"base_pct": 20, "type": "bond"},
            "BNDX": {"base_pct": 10, "type": "bond"},
        },
    },
    "growth_tilt": {
        "name": "Growth-Tilted Portfolio",
        "description": "Heavier equity, small-cap value factor tilt",
        "holdings": {
            "VTI":  {"base_pct": 45, "type": "equity"},
            "AVUV": {"base_pct": 15, "type": "equity"},
            "VXUS": {"base_pct": 20, "type": "equity"},
            "BND":  {"base_pct": 20, "type": "bond"},
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# RISK PROFILES
# ═══════════════════════════════════════════════════════════════════════════

_RISK_PROFILES = {
    "conservative":  {"equity_max": 30, "bond_min": 60, "label": "Conservative"},
    "moderate-conservative": {"equity_max": 45, "bond_min": 45, "label": "Moderate-Conservative"},
    "moderate":      {"equity_max": 60, "bond_min": 30, "label": "Moderate"},
    "moderate-aggressive": {"equity_max": 75, "bond_min": 20, "label": "Moderate-Aggressive"},
    "aggressive":    {"equity_max": 90, "bond_min": 10, "label": "Aggressive"},
}

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════


def _infer_risk(age: int) -> str:
    """Rule-of-thumb risk from age (110 - age = equity %)."""
    equity_pct = max(10, min(90, 110 - age))
    if equity_pct >= 80:
        return "aggressive"
    if equity_pct >= 65:
        return "moderate-aggressive"
    if equity_pct >= 50:
        return "moderate"
    if equity_pct >= 35:
        return "moderate-conservative"
    return "conservative"


def _pick_portfolio(risk: str, preference: str | None) -> str:
    """Select best-fit lazy portfolio key."""
    if preference and preference in _LAZY_PORTFOLIOS:
        return preference
    mapping = {
        "conservative": "all_weather",
        "moderate-conservative": "four_fund",
        "moderate": "three_fund",
        "moderate-aggressive": "growth_tilt",
        "aggressive": "growth_tilt",
    }
    return mapping.get(risk, "three_fund")


def _adjust_allocations(
    holdings: dict[str, dict],
    risk: str,
    age: int,
) -> list[dict]:
    """Adjust portfolio allocations for age & risk."""
    risk_profile = _RISK_PROFILES.get(risk, _RISK_PROFILES["moderate"])
    equity_target = risk_profile["equity_max"]

    # Gather base allocations
    total_equity = sum(h["base_pct"] for h in holdings.values()
                       if h["type"] in ("equity", "reit"))
    total_bond = sum(h["base_pct"] for h in holdings.values()
                     if h["type"] in ("bond", "tips"))

    # Scale factor for equities
    if total_equity > 0:
        eq_scale = equity_target / total_equity
    else:
        eq_scale = 1.0
    bond_target = 100 - equity_target
    if total_bond > 0:
        bd_scale = bond_target / total_bond
    else:
        bd_scale = 1.0
    # Commodity/other keep their base pct proportionally
    other_total = sum(h["base_pct"] for h in holdings.values()
                      if h["type"] not in ("equity", "reit", "bond", "tips"))

    result = []
    for ticker, h in holdings.items():
        etf = _ETFS.get(ticker, {})
        if h["type"] in ("equity", "reit"):
            pct = round(h["base_pct"] * eq_scale, 1)
        elif h["type"] in ("bond", "tips"):
            pct = round(h["base_pct"] * bd_scale, 1)
        else:
            pct = round(h["base_pct"], 1)
        result.append({
            "ticker": ticker,
            "name": etf.get("name", ticker),
            "asset_class": etf.get("asset", h["type"]),
            "pct": pct,
            "expense_ratio": etf.get("er", 0),
            "hist_return": etf.get("hist_return", 0),
            "max_drawdown": etf.get("max_dd", 0),
            "div_yield": etf.get("div_yield", 0),
        })

    # Normalise to 100%
    total = sum(r["pct"] for r in result)
    if total > 0 and abs(total - 100) > 0.5:
        for r in result:
            r["pct"] = round(r["pct"] * 100 / total, 1)

    result.sort(key=lambda r: r["pct"], reverse=True)
    return result


def _portfolio_stats(alloc: list[dict]) -> dict:
    """Weighted return, drawdown, expense ratio."""
    w_ret = sum(a["pct"] / 100 * a["hist_return"] for a in alloc)
    w_dd = sum(a["pct"] / 100 * a["max_drawdown"] for a in alloc)
    w_er = sum(a["pct"] / 100 * a["expense_ratio"] for a in alloc)
    w_div = sum(a["pct"] / 100 * a["div_yield"] for a in alloc)
    return {
        "weighted_return": round(w_ret, 2),
        "weighted_drawdown": round(w_dd, 1),
        "weighted_expense_ratio": round(w_er, 3),
        "weighted_div_yield": round(w_div, 2),
    }


def _project_growth(amount: float, monthly_add: float,
                     rate: float, years: int) -> list[dict]:
    """Year-by-year projection."""
    balance = amount
    monthly_rate = rate / 100 / 12
    projections = [{"year": 0, "balance": round(balance, 2)}]
    for y in range(1, years + 1):
        for _ in range(12):
            balance = balance * (1 + monthly_rate) + monthly_add
        projections.append({"year": y, "balance": round(balance, 2)})
    return projections


class PortfolioBuilder(RichyToolBase):
    """Portfolio builder with lazy-portfolio allocation and projections."""

    tool_id = 42
    tool_name = "portfolio_builder"
    description = (
        "Build ETF portfolio based on age, risk tolerance, timeline. "
        "3-fund, all-weather, growth, income portfolios with projections."
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.82),
            response=self._narrate(plan),
            data_used=["age", "risk_tolerance", "investment_amount",
                        "monthly_contribution", "timeline_years"],
            accuracy_score=0.84,
            sources=[
                "Vanguard historical ETF data",
                "Bogleheads lazy portfolio research",
                "Ray Dalio All-Weather methodology",
                "Morningstar fund analysis",
            ],
            raw_data=plan,
        )

    def analyze(self, p: dict) -> dict:
        age = int(p.get("age", 35) or 35)
        risk_input = (p.get("risk_tolerance", "") or "").lower().replace(" ", "-")
        if risk_input not in _RISK_PROFILES:
            risk_input = _infer_risk(age)

        portfolio_pref = (p.get("portfolio_style", "") or "").lower().replace(" ", "_")
        portfolio_key = _pick_portfolio(risk_input, portfolio_pref or None)
        template = _LAZY_PORTFOLIOS[portfolio_key]

        investment_amount = float(p.get("investment_amount", 10_000) or 10_000)
        monthly_contribution = float(p.get("monthly_contribution", 500) or 500)
        timeline_years = int(p.get("timeline_years", 20) or 20)

        # Build allocation
        alloc = _adjust_allocations(template["holdings"], risk_input, age)
        stats = _portfolio_stats(alloc)

        # Dollar amounts per holding
        for a in alloc:
            a["amount"] = round(investment_amount * a["pct"] / 100, 2)

        # Project growth
        projections = _project_growth(
            investment_amount, monthly_contribution,
            stats["weighted_return"], min(timeline_years, 40),
        )
        total_contributed = investment_amount + monthly_contribution * 12 * timeline_years
        final_balance = projections[-1]["balance"]
        total_growth = final_balance - total_contributed

        # Rebalancing
        rebalance_schedule = {
            "frequency": "Semi-annually or when any holding drifts ±5%",
            "method": "Redirect new contributions to underweight holdings first",
            "tax_tip": "Rebalance inside tax-advantaged accounts (401k/IRA) to avoid capital gains",
        }

        # Risk label
        risk_profile = _RISK_PROFILES[risk_input]

        # Cost comparison: vs 1% AUM advisor
        advisor_drag = final_balance * 0.01 * timeline_years  # rough
        low_cost_total_er = stats["weighted_expense_ratio"] * final_balance

        confidence = 0.84 if risk_input != _infer_risk(age) else 0.80

        return {
            "portfolio_name": template["name"],
            "portfolio_description": template["description"],
            "risk_label": risk_profile["label"],
            "risk_key": risk_input,
            "age": age,
            "investment_amount": investment_amount,
            "monthly_contribution": monthly_contribution,
            "timeline_years": timeline_years,
            "allocations": alloc,
            "stats": stats,
            "projections": projections,
            "total_contributed": round(total_contributed, 2),
            "final_balance": round(final_balance, 2),
            "total_growth": round(total_growth, 2),
            "rebalance": rebalance_schedule,
            "cost_comparison": {
                "your_annual_cost": round(stats["weighted_expense_ratio"] / 100 * investment_amount, 2),
                "advisor_annual_cost": round(investment_amount * 0.01, 2),
                "annual_savings": round(investment_amount * (0.01 - stats["weighted_expense_ratio"] / 100), 2),
            },
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        lines.append(f"📊 **{plan['portfolio_name']}**")
        lines.append(f"  {plan['portfolio_description']}")
        lines.append(f"  Risk: {plan['risk_label']} | Age: {plan['age']}")
        lines.append("")

        # Allocation table
        lines.append("**🗂️ Allocation:**")
        lines.append(
            f"  {'Ticker':<6} {'Name':<32} {'%':>5}  {'Amount':>10}  "
            f"{'ER':>5}  {'Hist.Ret':>8}  {'MaxDD':>7}"
        )
        lines.append("  " + "─" * 82)
        for a in plan["allocations"]:
            lines.append(
                f"  {a['ticker']:<6} {a['name']:<32} "
                f"{a['pct']:>5.1f}% "
                f"{self.fmt_currency(a['amount']):>10}  "
                f"{a['expense_ratio']:>4.2f}%  "
                f"{a['hist_return']:>7.1f}%  "
                f"{a['max_drawdown']:>6.1f}%"
            )
        lines.append("")

        # Portfolio stats
        s = plan["stats"]
        lines.append("**📈 Portfolio Stats (weighted):**")
        lines.append(f"  Expected Return: {s['weighted_return']:.1f}%/yr")
        lines.append(f"  Max Drawdown:    {s['weighted_drawdown']:.1f}%")
        lines.append(f"  Expense Ratio:   {s['weighted_expense_ratio']:.3f}%")
        lines.append(f"  Dividend Yield:  {s['weighted_div_yield']:.1f}%")
        lines.append("")

        # Projection summary
        lines.append(
            f"**🚀 {plan['timeline_years']}-Year Projection** "
            f"({self.fmt_currency(plan['monthly_contribution'])}/mo contributions):"
        )
        # Show select years
        for proj in plan["projections"]:
            y = proj["year"]
            if y == 0 or y == plan["timeline_years"] or y % 5 == 0:
                lines.append(
                    f"  Year {y:>2}: {self.fmt_currency(proj['balance'])}"
                )
        lines.append("")
        lines.append(
            f"  Total contributed: {self.fmt_currency(plan['total_contributed'])}"
        )
        lines.append(
            f"  **Final balance:   {self.fmt_currency(plan['final_balance'])}**"
        )
        lines.append(
            f"  Growth earned:     {self.fmt_currency(plan['total_growth'])}"
        )
        lines.append("")

        # Cost comparison
        cc = plan["cost_comparison"]
        lines.append("**💰 Cost vs. Financial Advisor:**")
        lines.append(
            f"  Your annual cost: {self.fmt_currency(cc['your_annual_cost'])} "
            f"(ER only)"
        )
        lines.append(
            f"  Typical advisor:  {self.fmt_currency(cc['advisor_annual_cost'])} "
            f"(1% AUM fee)"
        )
        lines.append(
            f"  **You save:       {self.fmt_currency(cc['annual_savings'])}/yr**"
        )
        lines.append("")

        # Rebalance
        lines.append("**🔄 Rebalancing:**")
        rb = plan["rebalance"]
        lines.append(f"  When: {rb['frequency']}")
        lines.append(f"  How:  {rb['method']}")
        lines.append(f"  Tax tip: {rb['tax_tip']}")
        lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: Vanguard, Bogleheads, Morningstar"
        )
        return "\n".join(lines)
