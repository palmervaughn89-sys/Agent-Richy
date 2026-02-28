"""Goal Planner — user sets a goal (house, car, vacation, wedding,
college). Calculate monthly savings needed. Factor expected price
changes from CPI. Show timeline with milestones.
Where to save linked by timeline.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# GOAL TEMPLATES & COST DATA
# ═══════════════════════════════════════════════════════════════════════════

_GOAL_TEMPLATES: dict[str, dict[str, Any]] = {
    "house_down_payment": {
        "label": "House Down Payment",
        "default_cost": 60_000,  # 20% on $300K home
        "inflation_rate": 0.04,  # housing price growth
        "description": "20% down on a median-priced home",
    },
    "car": {
        "label": "Car Purchase",
        "default_cost": 35_000,
        "inflation_rate": 0.02,
        "description": "New car average transaction price",
    },
    "used_car": {
        "label": "Used Car",
        "default_cost": 15_000,
        "inflation_rate": 0.01,
        "description": "Reliable used car (3-5 years old)",
    },
    "vacation": {
        "label": "Vacation",
        "default_cost": 5_000,
        "inflation_rate": 0.03,
        "description": "Average family vacation",
    },
    "wedding": {
        "label": "Wedding",
        "default_cost": 35_000,
        "inflation_rate": 0.04,
        "description": "Average US wedding (The Knot 2024)",
    },
    "college": {
        "label": "College Fund (4 years)",
        "default_cost": 100_000,
        "inflation_rate": 0.04,
        "description": "4-year public university in-state",
    },
    "emergency_fund": {
        "label": "Emergency Fund",
        "default_cost": 15_000,
        "inflation_rate": 0.03,
        "description": "3-6 months expenses",
    },
    "baby": {
        "label": "Having a Baby",
        "default_cost": 15_000,
        "inflation_rate": 0.03,
        "description": "First-year baby costs (USDA estimate)",
    },
    "renovation": {
        "label": "Home Renovation",
        "default_cost": 25_000,
        "inflation_rate": 0.04,
        "description": "Kitchen or bathroom remodel",
    },
    "debt_payoff": {
        "label": "Debt Payoff",
        "default_cost": 20_000,
        "inflation_rate": 0.0,
        "description": "Pay off existing debt",
    },
    "custom": {
        "label": "Custom Goal",
        "default_cost": 10_000,
        "inflation_rate": 0.03,
        "description": "Your custom savings goal",
    },
}

# Savings vehicle recommendations by timeline
_SAVINGS_VEHICLES: dict[str, list[dict[str, str]]] = {
    "short": [  # < 1 year
        {"vehicle": "High-Yield Savings (HYSA)", "rate": "4.0-5.0% APY",
         "why": "Liquid, FDIC insured, no risk"},
    ],
    "medium": [  # 1-3 years
        {"vehicle": "HYSA", "rate": "4.0-5.0%",
         "why": "Liquidity for 1-2 year goals"},
        {"vehicle": "CD Ladder", "rate": "4.0-4.8%",
         "why": "Locked-in rate, FDIC insured"},
        {"vehicle": "I-Bonds", "rate": "Variable (inflation-linked)",
         "why": "Inflation protection, 1-year lockup"},
    ],
    "long": [  # 3-5 years
        {"vehicle": "I-Bonds", "rate": "Variable",
         "why": "Inflation hedge, up to $10K/yr"},
        {"vehicle": "Conservative ETF (bonds + stocks)", "rate": "5-7% avg",
         "why": "Higher return potential, some volatility"},
        {"vehicle": "CD Ladder", "rate": "4.0-4.5%",
         "why": "Guaranteed rate for locked horizon"},
    ],
    "very_long": [  # 5+ years
        {"vehicle": "Index Fund (VTI / VOO)", "rate": "8-10% historical avg",
         "why": "Best long-term growth for 5+ year goals"},
        {"vehicle": "529 Plan", "rate": "7-9% avg",
         "why": "Tax-free growth for education goals"},
        {"vehicle": "Target-Date Fund", "rate": "7-9% avg",
         "why": "Hands-off, auto-rebalances as deadline approaches"},
    ],
}


def _timeline_tier(months: int) -> str:
    if months < 12:
        return "short"
    if months < 36:
        return "medium"
    if months < 60:
        return "long"
    return "very_long"


def _build_milestones(target: float, months: int) -> list[dict]:
    """Create milestone checkpoints at 25%, 50%, 75%, 100%."""
    milestones = []
    for pct in [25, 50, 75, 100]:
        mo = round(months * pct / 100)
        amt = round(target * pct / 100, 2)
        milestones.append({
            "pct": pct,
            "month": mo,
            "amount": amt,
            "label": f"{pct}% — {_format_month(mo)}",
        })
    return milestones


def _format_month(months: int) -> str:
    if months < 12:
        return f"{months} months"
    years = months // 12
    rem = months % 12
    if rem == 0:
        return f"{years} year{'s' if years > 1 else ''}"
    return f"{years}yr {rem}mo"


class GoalPlanner(RichyToolBase):
    """Goal-based savings planner with CPI-adjusted targets."""

    tool_id = 41
    tool_name = "goal_planner"
    description = (
        "Goal planner: monthly savings, CPI-adjusted costs, "
        "timeline milestones, savings vehicle recommendations"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan),
            data_used=["goal_type", "target_amount", "timeline_months",
                        "current_saved", "income"],
            accuracy_score=0.86,
            sources=[
                "BLS CPI category inflation rates",
                "NAR housing price index",
                "The Knot wedding cost survey 2024",
                "College Board Trends in College Pricing",
            ],
            raw_data=plan,
        )

    def analyze(self, p: dict) -> dict:
        goal_type = (p.get("goal_type", "custom") or "custom").lower().replace(" ", "_")
        template = _GOAL_TEMPLATES.get(goal_type, _GOAL_TEMPLATES["custom"])

        target_amount = float(p.get("target_amount", 0) or 0)
        if target_amount == 0:
            target_amount = template["default_cost"]

        timeline_months = int(p.get("timeline_months", 24) or 24)
        current_saved = float(p.get("current_saved", 0) or 0)
        income = float(p.get("income", 60_000) or 60_000)
        goal_name = p.get("goal_name", template["label"])

        # CPI-adjusted target
        inflation_rate = template.get("inflation_rate", 0.03)
        custom_inflation = p.get("inflation_rate")
        if custom_inflation is not None:
            inflation_rate = float(custom_inflation)

        years = timeline_months / 12
        adjusted_target = target_amount * ((1 + inflation_rate) ** years)
        inflation_cost = adjusted_target - target_amount

        # Remaining after current savings
        remaining = max(adjusted_target - current_saved, 0)

        # Monthly savings needed (with HYSA interest)
        hysa_rate = 0.045
        monthly_no_interest = remaining / max(timeline_months, 1)
        # With interest: solve for PMT given FV, r, n
        monthly_rate = hysa_rate / 12
        if monthly_rate > 0 and timeline_months > 0:
            # FV of annuity: PMT * ((1+r)^n - 1)/r = remaining
            factor = ((1 + monthly_rate) ** timeline_months - 1) / monthly_rate
            monthly_with_interest = remaining / factor if factor > 0 else monthly_no_interest
        else:
            monthly_with_interest = monthly_no_interest

        interest_earned = (monthly_with_interest * timeline_months) - remaining
        interest_earned = max(0, abs(remaining - monthly_with_interest * timeline_months))

        # Savings rate as % of income
        monthly_income = income / 12
        savings_rate_pct = (monthly_with_interest / max(monthly_income, 1)) * 100

        # Feasibility
        if savings_rate_pct > 50:
            feasibility = "VERY_DIFFICULT"
        elif savings_rate_pct > 30:
            feasibility = "CHALLENGING"
        elif savings_rate_pct > 15:
            feasibility = "MODERATE"
        else:
            feasibility = "ACHIEVABLE"

        # Progress
        pct_complete = min(current_saved / max(adjusted_target, 1), 1.0) * 100

        # Timeline tier + vehicles
        tier = _timeline_tier(timeline_months)
        vehicles = _SAVINGS_VEHICLES[tier]
        # For college goals, prioritize 529
        if goal_type == "college" and tier in ("long", "very_long"):
            vehicles = [
                {"vehicle": "529 Plan", "rate": "7-9% avg",
                 "why": "Tax-free growth for education — best vehicle for college"},
            ] + [v for v in vehicles if v["vehicle"] != "529 Plan"]

        milestones = _build_milestones(adjusted_target, timeline_months)

        # Alternative timelines
        alternatives = []
        for alt_months in [12, 24, 36, 48, 60]:
            if alt_months == timeline_months:
                continue
            if monthly_rate > 0 and alt_months > 0:
                factor = ((1 + monthly_rate) ** alt_months - 1) / monthly_rate
                alt_monthly = remaining / factor if factor > 0 else remaining / alt_months
            else:
                alt_monthly = remaining / max(alt_months, 1)
            alt_pct = (alt_monthly / max(monthly_income, 1)) * 100
            alternatives.append({
                "months": alt_months,
                "label": _format_month(alt_months),
                "monthly": round(alt_monthly, 2),
                "pct_income": round(alt_pct, 1),
            })

        confidence = 0.82 if target_amount != template["default_cost"] else 0.78

        return {
            "goal_name": goal_name,
            "goal_type": goal_type,
            "original_target": round(target_amount, 2),
            "adjusted_target": round(adjusted_target, 2),
            "inflation_rate": inflation_rate,
            "inflation_cost": round(inflation_cost, 2),
            "current_saved": round(current_saved, 2),
            "remaining": round(remaining, 2),
            "pct_complete": round(pct_complete, 1),
            "timeline_months": timeline_months,
            "timeline_label": _format_month(timeline_months),
            "monthly_needed": round(monthly_with_interest, 2),
            "monthly_no_interest": round(monthly_no_interest, 2),
            "interest_earned": round(interest_earned, 2),
            "savings_rate_pct": round(savings_rate_pct, 1),
            "feasibility": feasibility,
            "tier": tier,
            "savings_vehicles": vehicles,
            "milestones": milestones,
            "alternatives": alternatives,
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        feas_emoji = {
            "ACHIEVABLE": "✅", "MODERATE": "🟡",
            "CHALLENGING": "⚠️", "VERY_DIFFICULT": "🚨",
        }
        emoji = feas_emoji.get(plan["feasibility"], "🎯")

        lines.append(
            f"🎯 **Goal Planner** — {plan['goal_name']}"
        )
        lines.append("")

        lines.append(
            f"**Target:** {self.fmt_currency(plan['original_target'])}"
        )
        if plan["inflation_cost"] > 0:
            lines.append(
                f"  + {self.fmt_currency(plan['inflation_cost'])} inflation "
                f"({plan['inflation_rate'] * 100:.1f}%/yr over "
                f"{plan['timeline_label']})"
            )
            lines.append(
                f"  **Adjusted target: "
                f"{self.fmt_currency(plan['adjusted_target'])}**"
            )
        lines.append("")

        # Progress
        if plan["current_saved"] > 0:
            pct = plan["pct_complete"]
            bar_len = 20
            filled = int(bar_len * min(pct / 100, 1.0))
            bar = "█" * filled + "░" * (bar_len - filled)
            lines.append(
                f"**Progress:** {self.fmt_currency(plan['current_saved'])} / "
                f"{self.fmt_currency(plan['adjusted_target'])} ({pct:.0f}%)"
            )
            lines.append(f"  [{bar}]")
            lines.append("")

        # Monthly needed
        lines.append(
            f"{emoji} **Save {self.fmt_currency(plan['monthly_needed'])}/mo** "
            f"for {plan['timeline_label']} "
            f"({plan['savings_rate_pct']:.1f}% of income)"
        )
        lines.append(
            f"  Feasibility: {plan['feasibility'].replace('_', ' ').title()}"
        )
        lines.append("")

        # Milestones
        lines.append("**📍 Milestones:**")
        for m in plan["milestones"]:
            lines.append(
                f"  {m['pct']}% → {self.fmt_currency(m['amount'])} "
                f"at {m['label'].split(' — ')[1] if ' — ' in m['label'] else _format_month(m['month'])}"
            )
        lines.append("")

        # Alternative timelines
        lines.append("**⏱️ Alternative timelines:**")
        for a in plan["alternatives"][:4]:
            lines.append(
                f"  {a['label']}: "
                f"{self.fmt_currency(a['monthly'])}/mo "
                f"({a['pct_income']:.1f}% of income)"
            )
        lines.append("")

        # Where to save
        lines.append(
            f"**🏦 Where to save ({plan['tier'].replace('_', ' ')} horizon):**"
        )
        for v in plan["savings_vehicles"][:3]:
            lines.append(
                f"  • {v['vehicle']} ({v['rate']}) — {v['why']}"
            )
        lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: BLS CPI, NAR, College Board"
        )
        return "\n".join(lines)
