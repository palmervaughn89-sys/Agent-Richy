"""Emergency Fund Calculator — calculate ACTUAL monthly essentials,
factor job stability by industry, single/dual income, dependents.
Baby step: $1K first, then full target. Link to Savings Sage.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# Industry job-stability tiers (BLS layoff rates / JOLTS 2024)
_INDUSTRY_STABILITY: dict[str, dict[str, Any]] = {
    "government":       {"tier": "very_stable",  "months": 3, "layoff_rate": 0.5},
    "healthcare":       {"tier": "very_stable",  "months": 3, "layoff_rate": 0.8},
    "education":        {"tier": "stable",       "months": 3, "layoff_rate": 1.0},
    "utilities":        {"tier": "stable",       "months": 3, "layoff_rate": 0.9},
    "finance":          {"tier": "stable",       "months": 4, "layoff_rate": 1.2},
    "tech":             {"tier": "moderate",     "months": 5, "layoff_rate": 2.0},
    "professional":     {"tier": "moderate",     "months": 5, "layoff_rate": 1.5},
    "manufacturing":    {"tier": "moderate",     "months": 5, "layoff_rate": 1.8},
    "retail":           {"tier": "unstable",     "months": 6, "layoff_rate": 2.5},
    "hospitality":      {"tier": "unstable",     "months": 6, "layoff_rate": 3.5},
    "construction":     {"tier": "unstable",     "months": 6, "layoff_rate": 2.8},
    "gig":              {"tier": "very_unstable","months": 8, "layoff_rate": None},
    "self_employed":    {"tier": "very_unstable","months": 9, "layoff_rate": None},
    "freelance":        {"tier": "very_unstable","months": 9, "layoff_rate": None},
    "entertainment":    {"tier": "unstable",     "months": 6, "layoff_rate": 3.0},
    "real_estate":      {"tier": "moderate",     "months": 5, "layoff_rate": 2.2},
    "other":            {"tier": "moderate",     "months": 5, "layoff_rate": 2.0},
}

# Month targets by scenario
_MONTH_MATRIX: dict[str, dict[str, int]] = {
    #                   stable industry   unstable industry
    "dual_no_dep":    {"stable": 3, "unstable": 4},
    "dual_with_dep":  {"stable": 4, "unstable": 6},
    "single_no_dep":  {"stable": 6, "unstable": 8},
    "single_with_dep":{"stable": 6, "unstable": 9},
    "self_employed":  {"stable": 9, "unstable": 12},
}

# Baby-step thresholds (Dave Ramsey inspired)
_BABY_STEP_1 = 1_000
_BABY_STEP_2_LABEL = "Full emergency fund"

# Average monthly essentials as % of gross income (BLS CEX 2024)
_ESSENTIALS_PCT_DEFAULT = {
    "housing":        0.28,
    "food":           0.10,
    "transportation": 0.08,
    "insurance":      0.06,
    "utilities":      0.04,
    "min_debt_pmts":  0.05,
    "healthcare":     0.03,
    "childcare":      0.00,   # added if dependents
}


class EmergencyFund(RichyToolBase):
    """Emergency fund calculator with industry-adjusted targets."""

    tool_id = 14
    tool_name = "emergency_fund"
    description = (
        "Emergency fund calculator: actual monthly essentials, "
        "industry stability adjustment, baby-step roadmap"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan),
            data_used=["income", "monthly_expenses", "industry",
                        "dual_income", "dependents", "current_savings"],
            accuracy_score=0.87,
            sources=[
                "BLS Consumer Expenditure Survey 2024",
                "BLS JOLTS layoff rates 2024",
                "Fidelity / Vanguard emergency fund guidelines",
            ],
            raw_data=plan,
        )

    def analyze(self, p: dict) -> dict:
        income = float(p.get("income", 60_000) or 60_000)
        monthly_gross = income / 12
        dependents = int(p.get("dependents", 0) or 0)
        dual_income = bool(p.get("dual_income", False))
        industry = (p.get("industry", "other") or "other").lower().replace(" ", "_")
        current_savings = float(p.get("current_savings", 0) or 0)
        if current_savings == 0:
            current_savings = float(p.get("emergency_fund", 0) or 0)

        # ── Monthly essentials ───────────────────────────────────────────
        essentials: dict[str, float] = {}
        custom = p.get("monthly_essentials", {})
        if isinstance(custom, dict) and custom:
            for k, v in custom.items():
                essentials[k] = float(v or 0)
        else:
            # Estimate from income
            for cat, pct in _ESSENTIALS_PCT_DEFAULT.items():
                essentials[cat] = round(monthly_gross * pct, 2)
            if dependents > 0:
                essentials["childcare"] = round(monthly_gross * 0.06 * dependents, 2)

        # Also allow top-level overrides
        for key in ("rent", "mortgage_payment", "housing"):
            if key in p:
                essentials["housing"] = float(p[key] or 0)

        monthly_essentials = sum(essentials.values())

        # ── Months target ────────────────────────────────────────────────
        ind_data = _INDUSTRY_STABILITY.get(industry, _INDUSTRY_STABILITY["other"])
        ind_tier = ind_data["tier"]
        is_stable = ind_tier in ("very_stable", "stable")
        stability_label = "stable" if is_stable else "unstable"

        if industry in ("self_employed", "freelance", "gig"):
            scenario = "self_employed"
        elif dual_income and dependents == 0:
            scenario = "dual_no_dep"
        elif dual_income:
            scenario = "dual_with_dep"
        elif dependents == 0:
            scenario = "single_no_dep"
        else:
            scenario = "single_with_dep"

        months_target = _MONTH_MATRIX[scenario][stability_label]

        # ── Fund target ──────────────────────────────────────────────────
        fund_target = monthly_essentials * months_target

        # ── Progress ─────────────────────────────────────────────────────
        pct_complete = min(current_savings / max(fund_target, 1), 1.0) * 100
        gap = max(fund_target - current_savings, 0)

        # Baby steps
        baby_step_1_done = current_savings >= _BABY_STEP_1
        baby_step_2_done = current_savings >= fund_target

        # Monthly savings needed to reach target in 6/12 months
        months_6 = max(gap / 6, 0) if gap > 0 else 0
        months_12 = max(gap / 12, 0) if gap > 0 else 0

        # ── Where to keep it ─────────────────────────────────────────────
        where_to_save = [
            {"vehicle": "High-Yield Savings (HYSA)", "rate": "4.0-5.0% APY",
             "best_for": "Primary emergency fund — liquid + FDIC insured"},
            {"vehicle": "Money Market Account", "rate": "4.0-4.5% APY",
             "best_for": "Larger balances, check-writing access"},
            {"vehicle": "No-Penalty CD", "rate": "4.0-4.5% APY",
             "best_for": "Portion you won't need for 3+ months"},
        ]

        # ── Confidence ───────────────────────────────────────────────────
        has_custom = bool(custom)
        filled = sum(1 for v in [income, industry, dual_income,
                                  current_savings, has_custom] if v)
        confidence = min(0.72 + filled * 0.04, 0.92)

        return {
            "monthly_essentials": round(monthly_essentials, 2),
            "essentials_breakdown": essentials,
            "months_target": months_target,
            "fund_target": round(fund_target, 2),
            "current_savings": round(current_savings, 2),
            "gap": round(gap, 2),
            "pct_complete": round(pct_complete, 1),
            "scenario": scenario,
            "industry": industry,
            "industry_tier": ind_tier,
            "stability": stability_label,
            "baby_step_1_done": baby_step_1_done,
            "baby_step_2_done": baby_step_2_done,
            "monthly_to_fill_6mo": round(months_6, 2),
            "monthly_to_fill_12mo": round(months_12, 2),
            "where_to_save": where_to_save,
            "dependents": dependents,
            "dual_income": dual_income,
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        pct = plan["pct_complete"]
        emoji = "✅" if pct >= 100 else ("🟡" if pct >= 50 else "🚨")

        lines.append(
            f"{emoji} **Emergency Fund Calculator** — "
            f"{plan['industry'].replace('_', ' ').title()} | "
            f"{'Dual' if plan['dual_income'] else 'Single'} income | "
            f"{plan['dependents']} dependents"
        )
        lines.append("")

        # Target
        lines.append(
            f"**Monthly essentials:** {self.fmt_currency(plan['monthly_essentials'])}"
        )
        lines.append(
            f"**Target: {plan['months_target']} months = "
            f"{self.fmt_currency(plan['fund_target'])}**"
        )
        lines.append(
            f"  Why {plan['months_target']} months: "
            f"{plan['scenario'].replace('_', ' ')} + "
            f"{plan['stability']} industry ({plan['industry_tier']})"
        )
        lines.append("")

        # Progress
        lines.append(
            f"**Progress:** {self.fmt_currency(plan['current_savings'])} / "
            f"{self.fmt_currency(plan['fund_target'])} ({pct:.0f}%)"
        )
        bar_len = 20
        filled_len = int(bar_len * min(pct / 100, 1.0))
        bar = "█" * filled_len + "░" * (bar_len - filled_len)
        lines.append(f"  [{bar}]")

        if plan["gap"] > 0:
            lines.append(
                f"  Gap: {self.fmt_currency(plan['gap'])}"
            )
            lines.append("")

            # Baby steps
            if not plan["baby_step_1_done"]:
                lines.append(
                    f"**🥇 Baby Step 1:** Save $1,000 as fast as possible. "
                    f"Need {self.fmt_currency(max(1000 - plan['current_savings'], 0))} more."
                )
            else:
                lines.append("**🥇 Baby Step 1:** ✅ $1,000 starter fund — done!")

            lines.append(
                f"**🥈 Baby Step 2:** Full {plan['months_target']}-month fund"
            )
            lines.append(
                f"  Save {self.fmt_currency(plan['monthly_to_fill_6mo'])}/mo → "
                f"6 months  |  "
                f"{self.fmt_currency(plan['monthly_to_fill_12mo'])}/mo → 12 months"
            )
        else:
            lines.append("  🎉 **Fully funded!**")
        lines.append("")

        # Essentials breakdown
        lines.append("**Monthly essentials breakdown:**")
        for cat, val in sorted(
            plan["essentials_breakdown"].items(), key=lambda x: -x[1]
        ):
            if val > 0:
                lines.append(
                    f"  {cat.replace('_', ' ').title()}: "
                    f"{self.fmt_currency(val)}"
                )
        lines.append("")

        # Where to save
        lines.append("**Where to keep your emergency fund:**")
        for w in plan["where_to_save"]:
            lines.append(f"  • {w['vehicle']} ({w['rate']}) — {w['best_for']}")
        lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: BLS CEX, JOLTS, Fidelity/Vanguard guidelines"
        )
        return "\n".join(lines)
