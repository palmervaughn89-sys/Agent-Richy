"""Net Worth Tracker — sum assets minus liabilities, compare to
Fed Survey of Consumer Finances benchmarks by age, flag
house-rich/cash-poor, track over time.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# FED SCF BENCHMARKS (2022 Survey of Consumer Finances, 2024 dollars)
# median & mean net worth by age bracket
# ═══════════════════════════════════════════════════════════════════════════

_SCF_BENCHMARKS: dict[str, dict[str, float]] = {
    "under_35": {"median":  39_000,  "mean":  183_500,  "label": "Under 35"},
    "35_44":    {"median": 135_600,  "mean":  549_600,  "label": "35-44"},
    "45_54":    {"median": 247_200,  "mean":  975_800,  "label": "45-54"},
    "55_64":    {"median": 364_500,  "mean": 1_566_900, "label": "55-64"},
    "65_74":    {"median": 409_900,  "mean": 1_794_600, "label": "65-74"},
    "75_plus":  {"median": 335_600,  "mean": 1_624_100, "label": "75+"},
}

# Wealth milestones (Fidelity rule of thumb: multiples of income by age)
_FIDELITY_MULTIPLES: dict[int, float] = {
    30: 1.0, 35: 2.0, 40: 3.0, 45: 4.0,
    50: 6.0, 55: 7.0, 60: 8.0, 67: 10.0,
}


def _age_bracket(age: int) -> str:
    if age < 35:
        return "under_35"
    if age < 45:
        return "35_44"
    if age < 55:
        return "45_54"
    if age < 65:
        return "55_64"
    if age < 75:
        return "65_74"
    return "75_plus"


def _fidelity_target(age: int, income: float) -> float | None:
    """Income-multiple target for given age (interpolated)."""
    keys = sorted(_FIDELITY_MULTIPLES.keys())
    if age < keys[0]:
        return None
    if age >= keys[-1]:
        return income * _FIDELITY_MULTIPLES[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= age < keys[i + 1]:
            lo, hi = keys[i], keys[i + 1]
            frac = (age - lo) / (hi - lo)
            mult = _FIDELITY_MULTIPLES[lo] + frac * (
                _FIDELITY_MULTIPLES[hi] - _FIDELITY_MULTIPLES[lo]
            )
            return income * mult
    return None


# ═══════════════════════════════════════════════════════════════════════════
# NET WORTH TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class NetWorthTracker(RichyToolBase):
    """Sum assets − liabilities. Compare to Fed SCF benchmarks."""

    tool_id = 12
    tool_name = "net_worth"
    description = (
        "Net worth calculation: assets minus liabilities with "
        "Fed SCF age benchmarks and house-rich/cash-poor check"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan),
            data_used=["assets", "liabilities", "age", "income"],
            accuracy_score=0.88,
            sources=[
                "Federal Reserve Survey of Consumer Finances 2022",
                "Fidelity Investments savings milestones",
            ],
            raw_data=plan,
        )

    # ─── Analysis ─────────────────────────────────────────────────────────

    def analyze(self, p: dict) -> dict:
        age = int(p.get("age", 35) or 35)
        income = float(p.get("income", 60_000) or 60_000)

        # ── Assets ────────────────────────────────────────────────────────
        assets_detail: dict[str, float] = {}
        raw_assets = p.get("assets", {})
        if isinstance(raw_assets, dict):
            for k, v in raw_assets.items():
                assets_detail[k] = float(v or 0)
        else:
            assets_detail["total_reported"] = float(raw_assets or 0)

        # Common fields users might supply at top level
        for key in (
            "checking", "savings", "investments", "retirement_accounts",
            "home_value", "car_value", "other_assets", "crypto",
            "cash", "brokerage", "hsa",
        ):
            if key in p and key not in assets_detail:
                assets_detail[key] = float(p[key] or 0)

        total_assets = sum(assets_detail.values())

        # ── Liabilities ──────────────────────────────────────────────────
        liab_detail: dict[str, float] = {}
        raw_liab = p.get("liabilities", {})
        if isinstance(raw_liab, dict):
            for k, v in raw_liab.items():
                liab_detail[k] = float(v or 0)
        else:
            liab_detail["total_reported"] = float(raw_liab or 0)

        for key in (
            "mortgage_balance", "auto_loan", "student_loans",
            "credit_card_debt", "personal_loan", "medical_debt",
            "other_debts",
        ):
            if key in p and key not in liab_detail:
                liab_detail[key] = float(p[key] or 0)

        total_liabilities = sum(liab_detail.values())

        # ── Net worth ────────────────────────────────────────────────────
        net_worth = total_assets - total_liabilities

        # ── SCF benchmark ────────────────────────────────────────────────
        bracket = _age_bracket(age)
        bench = _SCF_BENCHMARKS[bracket]
        median_nw = bench["median"]
        mean_nw = bench["mean"]
        vs_median = net_worth - median_nw
        percentile_est = _estimate_percentile(net_worth, median_nw, mean_nw)

        # Fidelity target
        fidelity_target = _fidelity_target(age, income)

        # ── House-rich / cash-poor ───────────────────────────────────────
        home_equity = assets_detail.get("home_value", 0) - liab_detail.get(
            "mortgage_balance", 0
        )
        home_equity = max(home_equity, 0)
        house_rich = False
        if net_worth > 0 and home_equity / max(net_worth, 1) > 0.60:
            house_rich = True

        liquid_assets = sum(
            assets_detail.get(k, 0)
            for k in ("checking", "savings", "cash", "brokerage",
                       "investments", "hsa", "crypto")
        )

        # ── Confidence ───────────────────────────────────────────────────
        items = sum(1 for v in assets_detail.values() if v > 0) + sum(
            1 for v in liab_detail.values() if v > 0
        )
        confidence = min(0.70 + items * 0.03, 0.92)

        return {
            "net_worth": round(net_worth, 2),
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "assets_detail": assets_detail,
            "liabilities_detail": liab_detail,
            "age": age,
            "scf_bracket": bench["label"],
            "scf_median": median_nw,
            "scf_mean": mean_nw,
            "vs_median": round(vs_median, 2),
            "percentile_est": percentile_est,
            "fidelity_target": round(fidelity_target, 2) if fidelity_target else None,
            "fidelity_on_track": (
                net_worth >= fidelity_target if fidelity_target else None
            ),
            "house_rich_cash_poor": house_rich,
            "home_equity": round(home_equity, 2),
            "liquid_assets": round(liquid_assets, 2),
            "confidence": round(confidence, 2),
        }

    # ─── Narration ────────────────────────────────────────────────────────

    def _narrate(self, plan: dict) -> str:
        nw = plan["net_worth"]
        lines: list[str] = []

        emoji = "📈" if nw > 0 else "📉"
        lines.append(
            f"{emoji} **Net Worth Tracker** — Age {plan['age']} | "
            f"{plan['scf_bracket']}"
        )
        lines.append("")

        # Summary
        lines.append(
            f"**Net worth: {self.fmt_currency(nw)}**"
        )
        lines.append(
            f"  Assets: {self.fmt_currency(plan['total_assets'])}  |  "
            f"Liabilities: {self.fmt_currency(plan['total_liabilities'])}"
        )
        lines.append("")

        # Detail
        if plan["assets_detail"]:
            lines.append("**Assets breakdown:**")
            for k, v in sorted(
                plan["assets_detail"].items(), key=lambda x: -x[1]
            ):
                if v > 0:
                    lines.append(
                        f"  {k.replace('_', ' ').title()}: "
                        f"{self.fmt_currency(v)}"
                    )
            lines.append("")

        if plan["liabilities_detail"]:
            lines.append("**Liabilities breakdown:**")
            for k, v in sorted(
                plan["liabilities_detail"].items(), key=lambda x: -x[1]
            ):
                if v > 0:
                    lines.append(
                        f"  {k.replace('_', ' ').title()}: "
                        f"{self.fmt_currency(v)}"
                    )
            lines.append("")

        # SCF comparison
        lines.append("**How you compare (Fed SCF):**")
        lines.append(
            f"  Median for {plan['scf_bracket']}: "
            f"{self.fmt_currency(plan['scf_median'])}"
        )
        diff = plan["vs_median"]
        direction = "above" if diff >= 0 else "below"
        lines.append(
            f"  You are {self.fmt_currency(abs(diff))} {direction} median"
        )
        lines.append(f"  Estimated percentile: ~{plan['percentile_est']}")
        lines.append("")

        # Fidelity
        ft = plan.get("fidelity_target")
        if ft:
            on_track = plan.get("fidelity_on_track")
            mark = "✅" if on_track else "⚠️"
            lines.append(
                f"**Fidelity milestone:** {mark} Target "
                f"{self.fmt_currency(ft)} | "
                f"{'On track' if on_track else 'Behind — focus on savings rate'}"
            )
            lines.append("")

        # House-rich / cash-poor
        if plan["house_rich_cash_poor"]:
            lines.append(
                f"⚠️ **House-rich / cash-poor:** Home equity "
                f"({self.fmt_currency(plan['home_equity'])}) is >60% of "
                f"net worth. Liquid assets only "
                f"{self.fmt_currency(plan['liquid_assets'])}. "
                f"Consider building liquid reserves."
            )
            lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: Fed SCF 2022, Fidelity milestones"
        )
        return "\n".join(lines)


def _estimate_percentile(nw: float, median: float, mean: float) -> str:
    """Rough percentile estimate from median/mean + position."""
    if nw <= 0:
        return "bottom 20%"
    if nw < median * 0.25:
        return "~15th"
    if nw < median * 0.50:
        return "~25th"
    if nw < median * 0.75:
        return "~35th"
    if nw < median:
        return "~45th"
    if nw < median * 1.5:
        return "~55th"
    if nw < mean:
        return "~65th"
    if nw < mean * 1.5:
        return "~80th"
    if nw < mean * 3:
        return "~90th"
    return "~95th+"
