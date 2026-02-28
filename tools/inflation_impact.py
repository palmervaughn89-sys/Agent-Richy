"""Inflation Impact Calculator — show users how inflation affects
THEIR specific basket: housing, food, gas, healthcare weighted
by their actual spending. Personal inflation rate vs national.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CPI CATEGORY DATA (BLS CPI-U, January 2025 year-over-year)
# ═══════════════════════════════════════════════════════════════════════════

_CPI_CATEGORIES: dict[str, dict[str, Any]] = {
    "housing": {
        "yoy_pct": 4.6,
        "weight_national": 0.345,
        "bls_series": "CUSR0000SAH",
        "label": "Housing (rent/mortgage, utilities)",
    },
    "food_at_home": {
        "yoy_pct": 1.8,
        "weight_national": 0.082,
        "bls_series": "CUSR0000SAF11",
        "label": "Food at home (groceries)",
    },
    "food_away": {
        "yoy_pct": 3.4,
        "weight_national": 0.058,
        "bls_series": "CUSR0000SEFV",
        "label": "Food away from home (restaurants)",
    },
    "energy": {
        "yoy_pct": -0.5,
        "weight_national": 0.063,
        "bls_series": "CUSR0000SA0E",
        "label": "Energy (gas, electricity)",
    },
    "gasoline": {
        "yoy_pct": -3.3,
        "weight_national": 0.031,
        "bls_series": "CUSR0000SETB01",
        "label": "Gasoline",
    },
    "healthcare": {
        "yoy_pct": 3.0,
        "weight_national": 0.088,
        "bls_series": "CUSR0000SAM",
        "label": "Medical care",
    },
    "transportation": {
        "yoy_pct": 1.2,
        "weight_national": 0.060,
        "bls_series": "CUSR0000SAT",
        "label": "Transportation (vehicle, maintenance)",
    },
    "auto_insurance": {
        "yoy_pct": 11.3,
        "weight_national": 0.029,
        "bls_series": "CUSR0000SETE",
        "label": "Auto insurance",
    },
    "apparel": {
        "yoy_pct": 0.9,
        "weight_national": 0.026,
        "bls_series": "CUSR0000SAA",
        "label": "Apparel",
    },
    "education": {
        "yoy_pct": 3.8,
        "weight_national": 0.059,
        "bls_series": "CUSR0000SAE",
        "label": "Education & communication",
    },
    "recreation": {
        "yoy_pct": 1.5,
        "weight_national": 0.055,
        "bls_series": "CUSR0000SAR",
        "label": "Recreation",
    },
    "childcare": {
        "yoy_pct": 4.2,
        "weight_national": 0.015,
        "bls_series": None,
        "label": "Childcare",
    },
    "other": {
        "yoy_pct": 2.5,
        "weight_national": 0.090,
        "bls_series": "CUSR0000SA0",
        "label": "Other goods & services",
    },
}

_NATIONAL_CPI = 3.0  # overall CPI-U YoY Jan 2025 (BLS)

# Purchasing power erosion
def _purchasing_power(rate: float, years: int) -> float:
    """$1 today is worth this much in `years` at `rate` inflation."""
    return round(1 / ((1 + rate / 100) ** years), 4)


class InflationImpact(RichyToolBase):
    """Personal inflation rate based on the user's actual spending."""

    tool_id = 40
    tool_name = "inflation_impact"
    description = (
        "Personal inflation calculator: your real inflation rate "
        "vs national CPI based on your actual spending basket"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.84),
            response=self._narrate(plan),
            data_used=["monthly_spending", "income"],
            accuracy_score=0.85,
            sources=[
                "BLS CPI-U January 2025",
                "BLS Consumer Expenditure Survey 2024",
            ],
            raw_data=plan,
        )

    def analyze(self, p: dict) -> dict:
        income = float(p.get("income", 60_000) or 60_000)
        monthly_income = income / 12

        # User's spending basket
        spending: dict[str, float] = {}
        raw = p.get("monthly_spending", {})
        if isinstance(raw, dict) and raw:
            for k, v in raw.items():
                # Map user keys to our categories
                k_lower = k.lower().replace(" ", "_")
                mapped = _map_category(k_lower)
                if mapped:
                    spending[mapped] = spending.get(mapped, 0) + float(v or 0)
        else:
            # Estimate from income using national weights
            for cat, data in _CPI_CATEGORIES.items():
                spending[cat] = round(monthly_income * data["weight_national"], 2)

        # Allow top-level overrides
        for key_map in [
            ("rent", "housing"), ("mortgage_payment", "housing"),
            ("groceries", "food_at_home"), ("restaurants", "food_away"),
            ("dining_out", "food_away"), ("gas", "gasoline"),
            ("electric", "energy"), ("utilities", "energy"),
            ("medical", "healthcare"), ("insurance", "auto_insurance"),
        ]:
            if key_map[0] in p:
                spending[key_map[1]] = float(p[key_map[0]] or 0)

        total_spending = sum(spending.values())
        if total_spending == 0:
            total_spending = monthly_income * 0.80

        # Calculate personal inflation rate (weighted average)
        personal_inflation = 0.0
        category_impacts: list[dict] = []

        for cat, amount in spending.items():
            cpi = _CPI_CATEGORIES.get(cat, _CPI_CATEGORIES["other"])
            weight = amount / max(total_spending, 1)
            contribution = weight * cpi["yoy_pct"]
            personal_inflation += contribution

            annual_cost = amount * 12
            annual_increase = annual_cost * (cpi["yoy_pct"] / 100)

            category_impacts.append({
                "category": cat,
                "label": cpi["label"],
                "monthly_spend": round(amount, 2),
                "weight": round(weight * 100, 1),
                "yoy_rate": cpi["yoy_pct"],
                "annual_impact": round(annual_increase, 2),
                "contribution": round(contribution, 2),
            })

        category_impacts.sort(key=lambda x: -abs(x["annual_impact"]))

        total_annual_impact = sum(c["annual_impact"] for c in category_impacts)

        # Purchasing power erosion
        pp_5yr = _purchasing_power(personal_inflation, 5)
        pp_10yr = _purchasing_power(personal_inflation, 10)
        pp_20yr = _purchasing_power(personal_inflation, 20)

        # Salary raise needed
        raise_needed = personal_inflation

        # Compare to national
        delta = personal_inflation - _NATIONAL_CPI
        if delta > 0.5:
            comparison = "ABOVE_NATIONAL"
        elif delta < -0.5:
            comparison = "BELOW_NATIONAL"
        else:
            comparison = "NEAR_NATIONAL"

        confidence = 0.80 if isinstance(p.get("monthly_spending"), dict) else 0.72

        return {
            "personal_inflation": round(personal_inflation, 2),
            "national_cpi": _NATIONAL_CPI,
            "delta_vs_national": round(delta, 2),
            "comparison": comparison,
            "total_monthly_spending": round(total_spending, 2),
            "total_annual_spending": round(total_spending * 12, 2),
            "annual_inflation_cost": round(total_annual_impact, 2),
            "monthly_inflation_cost": round(total_annual_impact / 12, 2),
            "category_impacts": category_impacts,
            "purchasing_power": {
                "5yr": pp_5yr,
                "10yr": pp_10yr,
                "20yr": pp_20yr,
            },
            "raise_needed": round(raise_needed, 2),
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        pi = plan["personal_inflation"]
        ni = plan["national_cpi"]

        emoji = "🔥" if pi > ni + 0.5 else ("✅" if pi <= ni else "📊")
        lines.append(
            f"{emoji} **Inflation Impact Calculator** — "
            f"Your personal inflation: **{pi:.1f}%** "
            f"vs national {ni:.1f}%"
        )
        lines.append("")

        # Annual cost
        lines.append(
            f"**Inflation is costing you "
            f"{self.fmt_currency(plan['annual_inflation_cost'])}/yr** "
            f"({self.fmt_currency(plan['monthly_inflation_cost'])}/mo)"
        )
        if plan["delta_vs_national"] > 0.5:
            lines.append(
                f"  ⚠️ Your spending leans into categories rising faster "
                f"than average (+{plan['delta_vs_national']:.1f}% above national)"
            )
        lines.append("")

        # Category breakdown
        lines.append("**Where inflation hits you hardest:**")
        for c in plan["category_impacts"][:8]:
            if c["annual_impact"] == 0:
                continue
            direction = "↑" if c["yoy_rate"] > 0 else "↓"
            lines.append(
                f"  {c['label']}: {self.fmt_currency(c['monthly_spend'])}/mo × "
                f"{direction}{abs(c['yoy_rate']):.1f}% = "
                f"{self.fmt_currency(c['annual_impact'])}/yr impact "
                f"({c['weight']:.0f}% of spending)"
            )
        lines.append("")

        # Purchasing power
        pp = plan["purchasing_power"]
        lines.append(
            f"**Purchasing power erosion at {pi:.1f}%:**"
        )
        lines.append(
            f"  $1 today → ${pp['5yr']:.2f} in 5yr | "
            f"${pp['10yr']:.2f} in 10yr | "
            f"${pp['20yr']:.2f} in 20yr"
        )
        lines.append("")

        # Raise needed
        lines.append(
            f"**💼 You need a {plan['raise_needed']:.1f}% annual raise "
            f"just to keep up.** Anything above beats inflation."
        )
        lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: BLS CPI-U Jan 2025, BLS CEX 2024"
        )
        return "\n".join(lines)


def _map_category(key: str) -> str | None:
    """Map user-supplied spending keys to CPI categories."""
    mapping: dict[str, str] = {
        "housing": "housing", "rent": "housing", "mortgage": "housing",
        "mortgage_payment": "housing",
        "food": "food_at_home", "groceries": "food_at_home",
        "food_at_home": "food_at_home",
        "restaurants": "food_away", "dining": "food_away",
        "dining_out": "food_away", "food_away": "food_away",
        "energy": "energy", "electric": "energy", "electricity": "energy",
        "utilities": "energy", "utility": "energy",
        "gas": "gasoline", "gasoline": "gasoline", "fuel": "gasoline",
        "healthcare": "healthcare", "medical": "healthcare",
        "health": "healthcare", "doctor": "healthcare",
        "transportation": "transportation", "car": "transportation",
        "auto_insurance": "auto_insurance", "car_insurance": "auto_insurance",
        "insurance": "auto_insurance",
        "clothes": "apparel", "apparel": "apparel", "clothing": "apparel",
        "education": "education", "tuition": "education", "school": "education",
        "entertainment": "recreation", "recreation": "recreation",
        "fun": "recreation", "streaming": "recreation",
        "childcare": "childcare", "daycare": "childcare",
    }
    return mapping.get(key)
