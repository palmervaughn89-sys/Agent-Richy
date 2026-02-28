"""Subscription Tracker — list all subs, calculate annual total,
compare to cheaper alternatives, show 10-year invested equivalent,
rank by essential/cuttable.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# ALTERNATIVE DATABASE
# ═══════════════════════════════════════════════════════════════════════════

_ALTERNATIVES: dict[str, dict[str, Any]] = {
    # Streaming
    "netflix":       {"alt": "Netflix Basic w/Ads ($7.99)", "save_pct": 0.45, "category": "streaming"},
    "hulu":          {"alt": "Hulu Basic w/Ads ($9.99)", "save_pct": 0.30, "category": "streaming"},
    "disney+":       {"alt": "Disney+ Basic w/Ads ($9.99)", "save_pct": 0.25, "category": "streaming"},
    "disney plus":   {"alt": "Disney+ Basic w/Ads ($9.99)", "save_pct": 0.25, "category": "streaming"},
    "hbo max":       {"alt": "Max w/Ads ($9.99)", "save_pct": 0.40, "category": "streaming"},
    "max":           {"alt": "Max w/Ads ($9.99)", "save_pct": 0.40, "category": "streaming"},
    "peacock":       {"alt": "Peacock Free tier or w/Ads ($7.99)", "save_pct": 0.45, "category": "streaming"},
    "paramount+":    {"alt": "Paramount+ Essential ($7.99)", "save_pct": 0.35, "category": "streaming"},
    "apple tv+":     {"alt": "Often free w/ Apple device purchase", "save_pct": 1.0, "category": "streaming"},
    "apple tv":      {"alt": "Often free w/ Apple device purchase", "save_pct": 1.0, "category": "streaming"},
    "youtube premium":{"alt": "Free YouTube + uBlock Origin", "save_pct": 1.0, "category": "streaming"},
    "amazon prime":  {"alt": "Student discount ($7.49/mo) or annual ($139/yr vs monthly)", "save_pct": 0.20, "category": "shopping"},
    "spotify":       {"alt": "Spotify Free or family plan split", "save_pct": 0.50, "category": "music"},
    "apple music":   {"alt": "Spotify Free or family plan split", "save_pct": 0.50, "category": "music"},
    "tidal":         {"alt": "Spotify Free tier", "save_pct": 1.0, "category": "music"},

    # Fitness
    "gym":           {"alt": "Planet Fitness ($10/mo) or home workouts", "save_pct": 0.70, "category": "fitness"},
    "peloton":       {"alt": "Peloton App-only ($12.99) or free alternatives (Nike Training)", "save_pct": 0.55, "category": "fitness"},
    "orangetheory":  {"alt": "Planet Fitness + free HIIT YouTube", "save_pct": 0.80, "category": "fitness"},
    "crossfit":      {"alt": "Home equipment + free programming", "save_pct": 0.70, "category": "fitness"},
    "equinox":       {"alt": "LA Fitness / Planet Fitness", "save_pct": 0.85, "category": "fitness"},

    # Software / Cloud
    "microsoft 365": {"alt": "Google Workspace Free or LibreOffice", "save_pct": 1.0, "category": "software"},
    "adobe":         {"alt": "Canva Free / Affinity (one-time $70)", "save_pct": 0.80, "category": "software"},
    "dropbox":       {"alt": "Google Drive (15GB free) or iCloud ($1/mo 50GB)", "save_pct": 0.85, "category": "software"},
    "icloud":        {"alt": "Google Drive 15GB free", "save_pct": 1.0, "category": "software"},

    # Food delivery
    "doordash":      {"alt": "Cook at home, batch meal prep", "save_pct": 1.0, "category": "food"},
    "dashpass":      {"alt": "Cook at home, batch meal prep", "save_pct": 1.0, "category": "food"},
    "uber eats":     {"alt": "Cook at home, grocery delivery instead", "save_pct": 1.0, "category": "food"},
    "grubhub":       {"alt": "Cook at home, batch cooking", "save_pct": 1.0, "category": "food"},
    "meal kit":      {"alt": "Grocery store + online recipes", "save_pct": 0.60, "category": "food"},
    "hello fresh":   {"alt": "Grocery store + online recipes", "save_pct": 0.60, "category": "food"},
    "blue apron":    {"alt": "Grocery store + online recipes", "save_pct": 0.60, "category": "food"},

    # News / Misc
    "news":          {"alt": "Library free access (Libby app)", "save_pct": 1.0, "category": "news"},
    "nyt":           {"alt": "Library card + Libby app", "save_pct": 1.0, "category": "news"},
    "wsj":           {"alt": "Library card + Libby app", "save_pct": 1.0, "category": "news"},
    "audible":       {"alt": "Libby app (free audiobooks via library)", "save_pct": 1.0, "category": "news"},
    "kindle unlimited":{"alt": "Library + Libby app", "save_pct": 1.0, "category": "news"},
}

# Investment growth rate for "invested equivalent"
_INVEST_RETURN = 0.10  # 10% avg stock market


def _find_alternative(name: str) -> dict | None:
    """Fuzzy match subscription name to alternatives DB."""
    name_lower = name.lower().strip()
    # Direct match
    if name_lower in _ALTERNATIVES:
        return _ALTERNATIVES[name_lower]
    # Partial match
    for key, val in _ALTERNATIVES.items():
        if key in name_lower or name_lower in key:
            return val
    return None


def _invested_equivalent(monthly: float, years: int = 10) -> float:
    """What monthly subscription cost would grow to if invested instead."""
    annual = monthly * 12
    total = 0.0
    for _ in range(years):
        total = (total + annual) * (1 + _INVEST_RETURN)
    return round(total, 2)


class SubscriptionTracker(RichyToolBase):
    """List subscriptions, annual total, alternatives, invested equivalent."""

    tool_id = 34
    tool_name = "subscription_audit"
    description = (
        "Subscription audit: annual cost, cheaper alternatives, "
        "10-year invested equivalent, essential vs cuttable ranking"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan),
            data_used=["subscriptions", "income"],
            accuracy_score=0.85,
            sources=[
                "C+R Research subscription spending survey 2024",
                "S&P 500 10% historical average return",
            ],
            raw_data=plan,
        )

    def analyze(self, p: dict) -> dict:
        income = float(p.get("income", 60_000) or 60_000)
        subs_raw = p.get("subscriptions", [])
        if not isinstance(subs_raw, list):
            subs_raw = []

        results: list[dict] = []
        total_monthly = 0.0
        total_potential_savings = 0.0

        for sub in subs_raw:
            if isinstance(sub, str):
                # Simple name only — estimate $15/mo
                sub = {"name": sub, "monthly": 15.0}
            name = sub.get("name", "Unknown")
            monthly = float(sub.get("monthly", 0) or 0)
            annual_cost = float(sub.get("annual", 0) or 0)
            if monthly == 0 and annual_cost > 0:
                monthly = annual_cost / 12
            elif annual_cost == 0:
                annual_cost = monthly * 12
            essential = sub.get("essential", False)

            total_monthly += monthly
            invested_10yr = _invested_equivalent(monthly, 10)

            alt = _find_alternative(name)
            potential_save = 0.0
            alt_text = None
            if alt and not essential:
                potential_save = monthly * alt["save_pct"]
                alt_text = alt["alt"]
                total_potential_savings += potential_save

            results.append({
                "name": name,
                "monthly": round(monthly, 2),
                "annual": round(annual_cost, 2),
                "invested_10yr": invested_10yr,
                "essential": essential,
                "alternative": alt_text,
                "potential_monthly_savings": round(potential_save, 2),
                "category": alt["category"] if alt else "other",
            })

        # Sort: cuttable first (non-essential with highest savings)
        results.sort(key=lambda x: (x["essential"], -x["potential_monthly_savings"]))

        total_annual = total_monthly * 12
        pct_income = (total_annual / max(income, 1)) * 100
        total_invested_10yr = _invested_equivalent(total_monthly, 10)
        savings_invested_10yr = _invested_equivalent(total_potential_savings, 10)

        # Rating
        if pct_income > 5:
            rating = "HIGH"
        elif pct_income > 3:
            rating = "MODERATE"
        else:
            rating = "REASONABLE"

        confidence = min(0.75 + len(results) * 0.02, 0.92)

        return {
            "subscriptions": results,
            "total_monthly": round(total_monthly, 2),
            "total_annual": round(total_annual, 2),
            "total_invested_10yr": total_invested_10yr,
            "pct_income": round(pct_income, 1),
            "rating": rating,
            "potential_monthly_savings": round(total_potential_savings, 2),
            "potential_annual_savings": round(total_potential_savings * 12, 2),
            "savings_invested_10yr": savings_invested_10yr,
            "count": len(results),
            "essential_count": sum(1 for r in results if r["essential"]),
            "cuttable_count": sum(1 for r in results if not r["essential"]),
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        emoji = {"HIGH": "🚨", "MODERATE": "🟡", "REASONABLE": "✅"}.get(plan["rating"], "📋")

        lines.append(
            f"{emoji} **Subscription Audit** — "
            f"{plan['count']} subscriptions | "
            f"{self.fmt_currency(plan['total_monthly'])}/mo"
        )
        lines.append("")

        # Summary
        lines.append(
            f"**Total:** {self.fmt_currency(plan['total_monthly'])}/mo = "
            f"{self.fmt_currency(plan['total_annual'])}/yr "
            f"({plan['pct_income']:.1f}% of income)"
        )
        lines.append(
            f"**If invested instead (10yr at 10%):** "
            f"{self.fmt_currency(plan['total_invested_10yr'])}"
        )
        lines.append("")

        # Individual subs
        essentials = [s for s in plan["subscriptions"] if s["essential"]]
        cuttables = [s for s in plan["subscriptions"] if not s["essential"]]

        if cuttables:
            lines.append(f"**✂️ Cuttable ({len(cuttables)}):**")
            for s in cuttables:
                save_note = ""
                if s["alternative"]:
                    save_note = (
                        f" → 💡 {s['alternative']} "
                        f"(save {self.fmt_currency(s['potential_monthly_savings'])}/mo)"
                    )
                lines.append(
                    f"  • {s['name']}: {self.fmt_currency(s['monthly'])}/mo "
                    f"({self.fmt_currency(s['annual'])}/yr) "
                    f"[10yr invested: {self.fmt_currency(s['invested_10yr'])}]"
                    f"{save_note}"
                )
            lines.append("")

        if essentials:
            lines.append(f"**✅ Essential ({len(essentials)}):**")
            for s in essentials:
                lines.append(
                    f"  • {s['name']}: {self.fmt_currency(s['monthly'])}/mo "
                    f"({self.fmt_currency(s['annual'])}/yr)"
                )
            lines.append("")

        # Potential savings
        if plan["potential_monthly_savings"] > 0:
            lines.append(
                f"**💰 Potential savings:** "
                f"{self.fmt_currency(plan['potential_monthly_savings'])}/mo = "
                f"{self.fmt_currency(plan['potential_annual_savings'])}/yr"
            )
            lines.append(
                f"  Invested over 10 years: "
                f"{self.fmt_currency(plan['savings_invested_10yr'])}"
            )
            lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: C+R Research, S&P 500 historical"
        )
        return "\n".join(lines)
