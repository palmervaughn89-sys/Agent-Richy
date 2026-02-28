"""Savings Sage — answers "where should I put my money RIGHT NOW?"

Uses heartbeat Fed trajectory data, yield curves, inflation breakevens,
and manual reference rates to compare HYSA, CDs, I-Bonds, T-Bills,
bond funds, and TIPS — then recommends the optimal vehicle for the
user's amount, goal, and timeline.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta
from typing import Optional

from tools.base import RichyToolBase, ToolResult
from tools.data_layer import get_latest_indicator, get_indicator_trend

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# ── Manual reference rates (updated manually; FRED doesn't track HYSA) ───
_MANUAL_RATES: dict[str, dict] = {
    "hysa": {
        "name": "High-Yield Savings Account",
        "rate": 4.60,     # APY, top-tier online banks Feb 2026
        "type": "variable",
        "fdic": True,
        "min": 0,
        "tax": "federal + state",
        "liquidity": "instant",
        "notes": "Rate tracks Fed. Drops ~0.5% within 2 months of each Fed cut.",
    },
    "cd_3mo": {
        "name": "3-Month CD",
        "rate": 4.50,
        "type": "fixed",
        "fdic": True,
        "min": 500,
        "tax": "federal + state",
        "liquidity": "3 months",
        "penalty": "~60 days interest",
    },
    "cd_6mo": {
        "name": "6-Month CD",
        "rate": 4.55,
        "type": "fixed",
        "fdic": True,
        "min": 500,
        "tax": "federal + state",
        "liquidity": "6 months",
        "penalty": "~90 days interest",
    },
    "cd_1yr": {
        "name": "1-Year CD",
        "rate": 4.40,
        "type": "fixed",
        "fdic": True,
        "min": 500,
        "tax": "federal + state",
        "liquidity": "12 months",
        "penalty": "~150 days interest",
    },
    "cd_18mo": {
        "name": "18-Month CD",
        "rate": 4.25,
        "type": "fixed",
        "fdic": True,
        "min": 500,
        "tax": "federal + state",
        "liquidity": "18 months",
        "penalty": "~180 days interest",
    },
    "cd_2yr": {
        "name": "2-Year CD",
        "rate": 4.15,
        "type": "fixed",
        "fdic": True,
        "min": 500,
        "tax": "federal + state",
        "liquidity": "24 months",
        "penalty": "~180 days interest",
    },
    "cd_5yr": {
        "name": "5-Year CD",
        "rate": 4.00,
        "type": "fixed",
        "fdic": True,
        "min": 500,
        "tax": "federal + state",
        "liquidity": "60 months",
        "penalty": "~365 days interest",
    },
    "ibond": {
        "name": "I-Bond (Series I Savings Bond)",
        "composite_rate": 3.11,   # current composite (fixed + inflation)
        "fixed_rate": 1.20,        # locked for life of bond
        "inflation_rate": 1.90,    # semiannual, resets May & Nov
        "annual_limit": 10_000,
        "type": "inflation-linked",
        "tax": "federal only (deferred until redemption)",
        "liquidity": "1-year lockup, 3-month interest penalty if < 5yr",
        "next_reset": "May 2026",
    },
    "tbill_4wk": {
        "name": "4-Week T-Bill",
        "series": "DGS1MO",
        "type": "fixed",
        "tax": "federal only — state tax exempt",
        "liquidity": "4 weeks",
        "min": 100,
    },
    "tbill_13wk": {
        "name": "13-Week T-Bill",
        "series": "DGS3MO",
        "type": "fixed",
        "tax": "federal only — state tax exempt",
        "liquidity": "13 weeks",
        "min": 100,
    },
    "tbill_26wk": {
        "name": "26-Week T-Bill",
        "series": "DGS6MO",
        "type": "fixed",
        "tax": "federal only — state tax exempt",
        "liquidity": "26 weeks",
        "min": 100,
    },
    "tnote_1yr": {
        "name": "1-Year Treasury",
        "series": "DGS1",
        "type": "fixed",
        "tax": "federal only — state tax exempt",
        "liquidity": "1 year (or sell on secondary market)",
        "min": 100,
    },
}

# ── State income tax rates (top marginal, for T-Bill advantage calc) ─────
_STATE_TAX_RATES: dict[str, float] = {
    "AL": 5.0,  "AK": 0.0,  "AZ": 2.5,  "AR": 4.4,  "CA": 13.3,
    "CO": 4.4,  "CT": 6.99, "DE": 6.6,  "FL": 0.0,  "GA": 5.49,
    "HI": 11.0, "ID": 5.8,  "IL": 4.95, "IN": 3.05, "IA": 5.7,
    "KS": 5.7,  "KY": 4.0,  "LA": 4.25, "ME": 7.15, "MD": 5.75,
    "MA": 5.0,  "MI": 4.25, "MN": 9.85, "MS": 5.0,  "MO": 4.8,
    "MT": 5.9,  "NE": 5.84, "NV": 0.0,  "NH": 0.0,  "NJ": 10.75,
    "NM": 5.9,  "NY": 10.9, "NC": 4.5,  "ND": 1.95, "OH": 3.5,
    "OK": 4.75, "OR": 9.9,  "PA": 3.07, "RI": 5.99, "SC": 6.4,
    "SD": 0.0,  "TN": 0.0,  "TX": 0.0,  "UT": 4.65, "VT": 8.75,
    "VA": 5.75, "WA": 0.0,  "WV": 5.12, "WI": 7.65, "WY": 0.0,
    "DC": 10.75,
}

# ── Timeline buckets (months) ────────────────────────────────────────────
_TIMELINE_MONTHS: dict[str, tuple[int, int]] = {
    "<6mo":   (0, 6),
    "6-12mo": (6, 12),
    "1-3yr":  (12, 36),
    "3-5yr":  (36, 60),
    "5+yr":   (60, 360),
}

# ── Goal → required liquidity notes ──────────────────────────────────────
_GOAL_NOTES: dict[str, dict] = {
    "emergency": {
        "liquidity": "Must be instant-access. HYSA only.",
        "products": ["hysa"],
        "force_liquid": True,
    },
    "house": {
        "liquidity": "Need date-certain access for down payment.",
        "products": ["hysa", "cd_6mo", "cd_1yr", "cd_18mo", "tbill_26wk"],
        "force_liquid": False,
    },
    "vacation": {
        "liquidity": "Moderate — know the trip date.",
        "products": ["hysa", "cd_3mo", "cd_6mo", "tbill_13wk", "tbill_26wk"],
        "force_liquid": False,
    },
    "college": {
        "liquidity": "Long horizon — can lock up.",
        "products": ["cd_1yr", "cd_2yr", "cd_5yr", "ibond", "tnote_1yr"],
        "force_liquid": False,
    },
    "retirement": {
        "liquidity": "Long-term — maximise yield, link to InvestIntel.",
        "products": ["ibond", "cd_5yr", "tnote_1yr"],
        "force_liquid": False,
    },
    "general": {
        "liquidity": "Flexible.",
        "products": ["hysa", "cd_6mo", "cd_1yr", "ibond", "tbill_26wk", "tnote_1yr"],
        "force_liquid": False,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# SavingsSage TOOL
# ═══════════════════════════════════════════════════════════════════════════

class SavingsSage(RichyToolBase):
    """Answers 'where should I put my money RIGHT NOW?'

    Compares HYSA, CDs, I-Bonds, T-Bills, and bond funds using
    real rate data, Fed trajectory, and inflation breakevens.
    """

    tool_id = 5
    tool_name = "savings_sage"
    description = (
        "Savings vehicle recommender — HYSA vs CD vs I-Bond vs T-Bill, "
        "with Fed trajectory, real yields, CD ladders, and I-Bond timing"
    )
    required_profile: list[str] = []

    # ── Router entry point ────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        """Extract params from profile/question and run ``analyze``."""
        amount = float(user_profile.get("savings_amount", 0) or 0)
        goal = user_profile.get("goal", "general")
        timeline = user_profile.get("timeline", "1-3yr")
        risk = int(user_profile.get("risk_tolerance", 3) or 3)

        if amount <= 0:
            # Try to parse from question
            amount = self._extract_amount(question) or 0.0

        if amount <= 0:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=0.5,
                response=(
                    "I can tell you exactly where to park your cash! "
                    "How much are you looking to save, and what's it for? "
                    "(e.g. \"$10,000 for a house down payment in 2 years\")"
                ),
                data_used=[],
                sources=["savings_sage"],
            )

        plan = self.analyze(amount, goal, timeline, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=0.93,
            response=self._narrate(plan),
            data_used=plan.get("data_sources", []),
            accuracy_score=0.90,
            sources=[
                "FEDFUNDS", "DGS1", "DGS2", "DGS5", "DGS10",
                "T5YIE", "PSAVERT",
                "Manual HYSA/CD/I-Bond reference rates",
            ],
            raw_data=plan,
        )

    # ── Main analysis ─────────────────────────────────────────────────────

    def analyze(
        self,
        amount: float,
        goal: str,
        timeline: str,
        user_profile: dict,
    ) -> dict:
        """Full savings analysis pipeline.

        Args:
            amount: Dollar amount to allocate.
            goal: ``"emergency"|"house"|"vacation"|"college"|"retirement"|"general"``
            timeline: ``"<6mo"|"6-12mo"|"1-3yr"|"3-5yr"|"5+yr"``
            user_profile: Optional keys: ``risk_tolerance``, ``state``,
                ``monthly_expenses``.

        Returns:
            Plan dict (see module docstring for schema).
        """
        state = user_profile.get("state", "").upper()[:2]
        risk = int(user_profile.get("risk_tolerance", 3) or 3)
        monthly_expenses = float(user_profile.get("monthly_expenses", 0) or 0)
        goal = goal.lower() if goal else "general"
        if goal not in _GOAL_NOTES:
            goal = "general"
        if timeline not in _TIMELINE_MONTHS:
            timeline = "1-3yr"

        tl_lo, tl_hi = _TIMELINE_MONTHS[timeline]
        tl_months = (tl_lo + tl_hi) / 2 or 3  # midpoint
        data_sources: list[str] = []

        # ── 1. Fed trajectory ─────────────────────────────────────────────
        fed_trajectory = self._fed_trajectory()
        data_sources.append("FEDFUNDS")

        # ── 2. Inflation context ──────────────────────────────────────────
        inflation = self._inflation_context()
        data_sources.extend(["T5YIE", "CPIAUCSL"])

        # ── 3. Product comparison ─────────────────────────────────────────
        comparison = self._build_comparison(
            amount, tl_months, state, inflation, fed_trajectory,
        )
        data_sources.extend([
            "DGS1MO", "DGS3MO", "DGS6MO", "DGS1",
            "DGS2", "DGS5", "DGS10",
        ])

        # ── 4. Timeline matching — filter to appropriate products ─────────
        goal_info = _GOAL_NOTES[goal]
        allowed = set(goal_info["products"])

        # Expand based on timeline
        if tl_hi <= 6:
            allowed &= {"hysa", "tbill_4wk", "tbill_13wk", "tbill_26wk", "cd_3mo"}
        elif tl_hi <= 12:
            allowed |= {"cd_6mo", "cd_1yr", "ibond"}
        elif tl_hi <= 36:
            allowed |= {"cd_1yr", "cd_18mo", "cd_2yr", "ibond", "tnote_1yr"}
        elif tl_hi <= 60:
            allowed |= {"cd_2yr", "cd_5yr", "ibond", "tnote_1yr"}
        else:
            allowed |= {"cd_5yr", "ibond", "tnote_1yr"}

        # Emergency fund always HYSA
        if goal_info.get("force_liquid"):
            allowed = {"hysa"}

        filtered = [c for c in comparison if c["product_id"] in allowed]
        if not filtered:
            filtered = comparison  # fallback — show everything

        # Sort by effective_rate descending
        filtered.sort(key=lambda c: c["effective_rate"], reverse=True)

        # Best option
        best = filtered[0] if filtered else comparison[0]

        # ── 5. CD ladder ──────────────────────────────────────────────────
        cd_ladder = self._cd_ladder(amount, timeline, fed_trajectory)

        # ── 6. I-Bond analysis ────────────────────────────────────────────
        ibond = self._ibond_analysis(amount, inflation, fed_trajectory)

        # ── 7. HYSA vs CD crossover ───────────────────────────────────────
        crossover = self._hysa_cd_crossover(fed_trajectory)

        # ── 8. Savings rate context ───────────────────────────────────────
        psavert = get_latest_indicator("PSAVERT")
        savings_rate_national = psavert.get("value", 4.6)
        data_sources.append("PSAVERT")

        # Emergency fund check
        ef_note = ""
        if monthly_expenses > 0:
            months_covered = amount / monthly_expenses
            if months_covered < 3:
                ef_note = (
                    f"⚠️ This covers only {months_covered:.1f} months of "
                    f"expenses. Aim for 3-6 months before locking money up."
                )
            elif months_covered < 6:
                ef_note = (
                    f"You have {months_covered:.1f} months covered. "
                    f"Consider building to 6 months before investing."
                )

        # ── Action items ──────────────────────────────────────────────────
        actions = self._action_items(
            best, fed_trajectory, ibond, cd_ladder,
            goal, amount, ef_note,
        )

        return {
            "amount": amount,
            "goal": goal,
            "timeline": timeline,
            "fed_trajectory": fed_trajectory,
            "best_option": {
                "product": best["product"],
                "rate": best["nominal_rate"],
                "effective_rate": best["effective_rate"],
                "reason": best["recommendation"],
            },
            "comparison": filtered,
            "cd_ladder": cd_ladder,
            "ibond_analysis": ibond,
            "hysa_cd_crossover": crossover,
            "inflation_context": inflation,
            "savings_rate_national": savings_rate_national,
            "emergency_fund_note": ef_note,
            "action_items": actions,
            "data_sources": list(set(data_sources)),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    # ── 1. Fed trajectory ─────────────────────────────────────────────────

    @staticmethod
    def _fed_trajectory() -> dict:
        """Determine Fed direction and savings implication."""
        fed = get_latest_indicator("FEDFUNDS")
        fed_trend = get_indicator_trend("FEDFUNDS", months=6)

        fed_rate = fed.get("value", 4.50)
        direction = fed_trend.get("direction", "flat")
        change = fed_trend.get("change_pct", 0)

        if direction == "rising":
            phase = "hiking"
            confidence = min(abs(change) * 10, 95)
            implication = (
                "Stay in HYSA — rates are still going up. Every hike lifts "
                "your HYSA rate. Don't lock into CDs until the Fed pauses."
            )
        elif direction == "falling":
            phase = "cutting"
            confidence = min(abs(change) * 10, 95)
            implication = (
                "Lock the longest CD you can afford to lock up. "
                "HYSA rates are dropping with each cut. Today's CD rate "
                "will look great in 6 months."
            )
        else:
            # Flat / holding
            phase = "peak_hold"
            confidence = 70
            implication = (
                "Lock CD rates NOW — this is likely the top. "
                "The next move is almost always a cut. "
                "Today's rates are the best forward-looking deal."
            )

        return {
            "fed_rate": fed_rate,
            "direction": phase,
            "confidence": round(confidence, 0),
            "implication": implication,
        }

    # ── 2. Inflation context ──────────────────────────────────────────────

    @staticmethod
    def _inflation_context() -> dict:
        """Gather inflation data for real-return calculations."""
        t5yie = get_latest_indicator("T5YIE")
        cpi_trend = get_indicator_trend("CPIAUCSL", months=12)

        breakeven = t5yie.get("value", 2.35)
        cpi_direction = cpi_trend.get("direction", "flat")
        cpi_change = cpi_trend.get("change_pct", 0)

        note = f"Market expects {breakeven:.2f}% avg inflation over 5 years."
        if breakeven > 3.0:
            note += (
                " That's elevated — prioritise inflation-protected products "
                "(I-Bonds, TIPS) for money beyond 1 year."
            )
        elif breakeven < 2.0:
            note += (
                " That's well-contained — nominal-rate products (CDs, HYSA) "
                "keep most of their purchasing power."
            )

        return {
            "breakeven_5yr": breakeven,
            "cpi_direction": cpi_direction,
            "cpi_change_12mo_pct": round(cpi_change, 2),
            "note": note,
        }

    # ── 3. Product comparison ─────────────────────────────────────────────

    def _build_comparison(
        self,
        amount: float,
        tl_months: float,
        state: str,
        inflation: dict,
        fed_traj: dict,
    ) -> list[dict]:
        """Build a comparison row for every savings product."""
        breakeven = inflation["breakeven_5yr"]
        state_rate = _STATE_TAX_RATES.get(state, 5.0)
        rows: list[dict] = []

        for pid, ref in _MANUAL_RATES.items():
            # Nominal rate
            if "series" in ref:
                ind = get_latest_indicator(ref["series"])
                nominal = ind.get("value", ref.get("rate", 4.0))
            else:
                nominal = ref.get("rate", ref.get("composite_rate", 0))

            # Effective rate (after state tax advantage for Treasuries)
            tax_note = ref.get("tax", "federal + state")
            tax_exempt_state = "state tax exempt" in tax_note.lower() or \
                               "federal only" in tax_note.lower()
            if tax_exempt_state and state_rate > 0:
                effective = nominal / (1 - state_rate / 100)
                tax_equiv_note = (
                    f"In {state or 'your state'}, the tax-equivalent yield "
                    f"is {effective:.2f}% (no state tax on interest)."
                )
            else:
                effective = nominal
                tax_equiv_note = ""

            # Real return
            real_return = round(nominal - breakeven, 2)

            # Dollar earnings over timeline
            years = tl_months / 12
            if pid == "ibond":
                cap = min(amount, ref["annual_limit"])
                earnings = cap * (nominal / 100) * years
            else:
                earnings = amount * (nominal / 100) * years

            # Liquidity label
            liquidity = ref.get("liquidity", "varies")

            # Recommendation note
            rec = self._product_rec(pid, fed_traj, real_return, amount)

            rows.append({
                "product_id": pid,
                "product": ref["name"],
                "nominal_rate": round(nominal, 2),
                "effective_rate": round(effective, 2),
                "real_return": real_return,
                "dollar_earnings": round(earnings, 2),
                "liquidity": liquidity,
                "tax_advantage": tax_equiv_note,
                "fdic": ref.get("fdic", False),
                "type": ref.get("type", "fixed"),
                "recommendation": rec,
            })

        return rows

    @staticmethod
    def _product_rec(
        pid: str, fed_traj: dict, real_return: float, amount: float,
    ) -> str:
        """Generate a one-line recommendation for a product."""
        phase = fed_traj["direction"]

        if pid == "hysa":
            if phase == "hiking":
                return "✅ Best right now — rate is still climbing with the Fed."
            if phase == "cutting":
                return "⚠️ Rate is declining. Good for emergency fund only."
            return "👍 Solid for emergency fund + short-term parking."

        if pid.startswith("cd_"):
            if phase == "peak_hold":
                return "🔒 Lock it in — this is likely the rate peak."
            if phase == "cutting":
                return "🔒 Lock NOW before rates drop further."
            if phase == "hiking":
                return "⏳ Wait — rates may go higher. Consider shorter terms."
            return "👍 Good if you can lock the money up."

        if pid == "ibond":
            fixed = _MANUAL_RATES["ibond"]["fixed_rate"]
            if fixed >= 1.0:
                return (
                    f"🌟 Fixed rate of {fixed:.2f}% is historically high — "
                    f"locks for the life of the bond. Buy now."
                )
            return "👍 Solid inflation hedge. $10K annual limit."

        if pid.startswith("tbill") or pid.startswith("tnote"):
            if real_return > 1.5:
                return "✅ Strong real return + state-tax-free."
            return "👍 State-tax-free, very safe, decent yield."

        return ""

    # ── 4. CD ladder ──────────────────────────────────────────────────────

    @staticmethod
    def _cd_ladder(
        amount: float, timeline: str, fed_traj: dict,
    ) -> dict:
        """Build a CD ladder strategy if appropriate."""
        tl_lo, tl_hi = _TIMELINE_MONTHS.get(timeline, (12, 36))

        if amount < 5_000 or tl_hi < 12:
            return {
                "applicable": False,
                "reason": (
                    "CD ladder works best with $5K+ and a 1+ year horizon."
                ),
                "strategy": [],
            }

        # Pick rungs based on timeline
        rungs: list[dict] = []
        if tl_hi <= 24:
            terms = [("cd_3mo", 3), ("cd_6mo", 6), ("cd_1yr", 12)]
        elif tl_hi <= 36:
            terms = [("cd_6mo", 6), ("cd_1yr", 12), ("cd_18mo", 18), ("cd_2yr", 24)]
        else:
            terms = [("cd_6mo", 6), ("cd_1yr", 12), ("cd_2yr", 24), ("cd_5yr", 60)]

        per_rung = round(amount / len(terms), 2)
        total_earnings = 0.0

        for pid, months in terms:
            rate = _MANUAL_RATES.get(pid, {}).get("rate", 4.0)
            earnings = per_rung * (rate / 100) * (months / 12)
            total_earnings += earnings
            rungs.append({
                "term": _MANUAL_RATES.get(pid, {}).get("name", pid),
                "months": months,
                "amount": per_rung,
                "rate": rate,
                "earnings": round(earnings, 2),
            })

        phase = fed_traj["direction"]
        if phase == "cutting":
            ladder_note = (
                "CD ladder is ideal right now — lock today's rates before "
                "they drop. Each rung matures at a different time, giving "
                "you periodic access."
            )
        elif phase == "peak_hold":
            ladder_note = (
                "Perfect timing — rates are at or near peak. A ladder "
                "captures today's top rates while maintaining flexibility."
            )
        else:
            ladder_note = (
                "Consider shorter-term rungs — rates may still rise. "
                "You can extend when the Fed pauses."
            )

        return {
            "applicable": True,
            "reason": ladder_note,
            "total_earnings": round(total_earnings, 2),
            "strategy": rungs,
        }

    # ── 5. I-Bond analysis ────────────────────────────────────────────────

    @staticmethod
    def _ibond_analysis(
        amount: float, inflation: dict, fed_traj: dict,
    ) -> dict:
        """Detailed I-Bond recommendation."""
        ref = _MANUAL_RATES["ibond"]
        composite = ref["composite_rate"]
        fixed = ref["fixed_rate"]
        infl_component = ref["inflation_rate"]
        limit = ref["annual_limit"]
        next_reset = ref["next_reset"]

        buyable = min(amount, limit)
        earnings_1yr = buyable * (composite / 100)

        # Estimate next reset from CPI trend
        cpi_dir = inflation.get("cpi_direction", "flat")
        if cpi_dir == "rising":
            reset_note = (
                f"CPI is rising — the inflation component will likely "
                f"increase at the {next_reset} reset. Buy before then to "
                f"lock the current fixed rate and still get the higher "
                f"inflation adjustment."
            )
        elif cpi_dir == "falling":
            reset_note = (
                f"CPI is cooling — the inflation component may drop at the "
                f"{next_reset} reset. The fixed rate ({fixed:.2f}%) stays "
                f"forever, though, and that's historically excellent."
            )
        else:
            reset_note = (
                f"Inflation is stable. Next composite rate resets {next_reset}. "
                f"The {fixed:.2f}% fixed rate is locked for life."
            )

        # Fixed rate assessment
        if fixed >= 1.5:
            fixed_verdict = (
                f"🌟 The {fixed:.2f}% fixed rate is the highest in 15+ years. "
                f"This rate is locked for the LIFE of the bond — a rare deal."
            )
        elif fixed >= 1.0:
            fixed_verdict = (
                f"✅ The {fixed:.2f}% fixed rate is historically high. "
                f"Worth buying for the fixed component alone."
            )
        elif fixed >= 0.5:
            fixed_verdict = (
                f"👍 Fixed rate of {fixed:.2f}% is above recent averages. "
                f"Decent, but not exceptional."
            )
        else:
            fixed_verdict = (
                f"The fixed rate is {fixed:.2f}% — low. I-Bonds are only "
                f"useful as an inflation hedge, not for real growth."
            )

        rec = "buy" if fixed >= 0.9 or composite > 4.0 else "consider"
        if amount > limit:
            rec_note = (
                f"You can only buy ${limit:,}/year. Put ${buyable:,.0f} in "
                f"I-Bonds and park the rest elsewhere."
            )
        else:
            rec_note = f"Your full ${amount:,.0f} fits within the annual limit."

        return {
            "composite_rate": composite,
            "fixed_rate": fixed,
            "inflation_component": infl_component,
            "annual_limit": limit,
            "buyable": buyable,
            "earnings_1yr": round(earnings_1yr, 2),
            "next_reset": next_reset,
            "reset_note": reset_note,
            "fixed_verdict": fixed_verdict,
            "recommendation": rec,
            "note": rec_note,
        }

    # ── 6. HYSA vs CD crossover ───────────────────────────────────────────

    @staticmethod
    def _hysa_cd_crossover(fed_traj: dict) -> dict:
        """Model when a CD beats HYSA under Fed rate trajectory.

        If the Fed is cutting, HYSA rate declines ~0.5% per 25bp cut,
        lagging by ~2 months. A CD locks the current rate.
        """
        phase = fed_traj["direction"]
        hysa_now = _MANUAL_RATES["hysa"]["rate"]
        cd_1yr = _MANUAL_RATES["cd_1yr"]["rate"]

        if phase == "cutting":
            # Model HYSA declining 0.25% every 3 months
            hysa_projected: list[dict] = []
            rate = hysa_now
            cd_cumulative = 0.0
            hysa_cumulative = 0.0
            crossover_month = 0

            for m in range(1, 13):
                if m % 3 == 0:
                    rate = max(rate - 0.25, 1.0)
                cd_monthly = cd_1yr / 12
                hysa_monthly = rate / 12
                cd_cumulative += cd_monthly
                hysa_cumulative += hysa_monthly

                hysa_projected.append({
                    "month": m,
                    "hysa_rate": round(rate, 2),
                    "hysa_cumulative_pct": round(hysa_cumulative, 3),
                    "cd_cumulative_pct": round(cd_cumulative, 3),
                })

                if cd_cumulative > hysa_cumulative and crossover_month == 0:
                    crossover_month = m

            return {
                "applicable": True,
                "crossover_month": crossover_month,
                "note": (
                    f"With Fed cutting, HYSA will decline ~0.25%/quarter. "
                    f"A 1-year CD at {cd_1yr:.2f}% beats HYSA by month "
                    f"{crossover_month}."
                ) if crossover_month > 0 else (
                    f"CD at {cd_1yr:.2f}% is already a better deal than "
                    f"a declining HYSA."
                ),
                "projection": hysa_projected,
            }

        if phase == "hiking":
            return {
                "applicable": False,
                "crossover_month": 0,
                "note": (
                    "HYSA rates are rising — no crossover expected. "
                    "Stick with HYSA until the Fed pauses."
                ),
                "projection": [],
            }

        # Peak / hold
        return {
            "applicable": True,
            "crossover_month": 1,
            "note": (
                f"Fed is on hold — HYSA and CD rates are similar. "
                f"CD wins on certainty: {cd_1yr:.2f}% is locked vs HYSA's "
                f"variable {hysa_now:.2f}%."
            ),
            "projection": [],
        }

    # ── Action items ──────────────────────────────────────────────────────

    @staticmethod
    def _action_items(
        best: dict,
        fed_traj: dict,
        ibond: dict,
        cd_ladder: dict,
        goal: str,
        amount: float,
        ef_note: str,
    ) -> list[str]:
        """Generate a prioritised list of action items."""
        actions: list[str] = []

        # Emergency fund warning first
        if ef_note:
            actions.append(ef_note)

        # Best product
        actions.append(
            f"1️⃣ Open/fund a **{best['product']}** — "
            f"{best['effective_rate']:.2f}% APY. "
            f"{best.get('recommendation', '')}"
        )

        # I-Bond if worth it
        if ibond["recommendation"] == "buy" and amount <= ibond["annual_limit"]:
            actions.append(
                f"2️⃣ Buy I-Bonds at TreasuryDirect.gov — "
                f"{ibond['fixed_rate']:.2f}% fixed rate locked for life. "
                f"({ibond['fixed_verdict'].split('.')[0]}.)"
            )
        elif ibond["recommendation"] == "buy" and amount > ibond["annual_limit"]:
            actions.append(
                f"2️⃣ Max out I-Bonds (${ibond['annual_limit']:,}/yr) at "
                f"TreasuryDirect.gov. Put the rest in "
                f"{best['product']}."
            )

        # CD ladder
        if cd_ladder.get("applicable"):
            total_e = cd_ladder.get("total_earnings", 0)
            actions.append(
                f"3️⃣ Consider a CD ladder — {cd_ladder['reason'][:80]}... "
                f"Projected earnings: ${total_e:,.2f}."
            )

        # Fed trajectory alert
        phase = fed_traj["direction"]
        if phase == "cutting":
            actions.append(
                "⚡ Act fast — every Fed cut drops HYSA and new CD rates. "
                "Lock in today's rates before the next meeting."
            )
        elif phase == "peak_hold":
            actions.append(
                "📌 Rates are at the peak. This is the best window to lock "
                "CDs and I-Bonds for long-term holding."
            )

        # Goal-specific
        if goal == "emergency":
            actions.append(
                "🛡️ Emergency fund = liquidity first. Keep it all in HYSA — "
                "never lock emergency money in CDs."
            )
        elif goal == "retirement" or goal == "college":
            actions.append(
                "📈 For 5+ year goals, talk to Invest Intel about moving "
                "a portion into diversified index funds for higher growth."
            )

        return actions

    # ── Extract amount from question ──────────────────────────────────────

    @staticmethod
    def _extract_amount(question: str) -> float:
        """Try to pull a dollar amount from the question text."""
        import re
        # Match $10,000 or $10000 or 10000 or 10k
        m = re.search(
            r"\$?([\d,]+(?:\.\d{1,2})?)\s*(?:k|K)?", question,
        )
        if m:
            raw = m.group(1).replace(",", "")
            val = float(raw)
            if "k" in question.lower() or "K" in question:
                # Only multiply if there's a k right after the number
                k_match = re.search(r"\$?[\d,]+\.?\d*\s*[kK]\b", question)
                if k_match:
                    val *= 1000
            return val
        return 0.0

    # ── Narration ─────────────────────────────────────────────────────────

    def _narrate(self, plan: dict) -> str:
        """Build a human-readable summary."""
        lines: list[str] = []

        amount = plan["amount"]
        goal = plan["goal"]
        timeline = plan["timeline"]

        lines.append(
            f"💰 **Savings Sage** — Where to put "
            f"{self.fmt_currency(amount)} ({goal}, {timeline})"
        )
        lines.append("")

        # Fed trajectory
        fed = plan["fed_trajectory"]
        phase_emoji = {"hiking": "📈", "cutting": "📉", "peak_hold": "📌"}
        lines.append(
            f"{phase_emoji.get(fed['direction'], '📊')} **Fed status: "
            f"{fed['direction'].upper()}** (confidence {fed['confidence']:.0f}%)"
        )
        lines.append(f"   {fed['implication']}")
        lines.append("")

        # Best option
        best = plan["best_option"]
        lines.append(
            f"🏆 **Best option: {best['product']}** at "
            f"**{best['rate']:.2f}% APY**"
        )
        if best.get("effective_rate") and best["effective_rate"] != best["rate"]:
            lines.append(
                f"   (Tax-equivalent: {best['effective_rate']:.2f}%)"
            )
        lines.append(f"   {best.get('reason', '')}")
        lines.append("")

        # Comparison table (top 4)
        lines.append("**Product comparison:**")
        for c in plan.get("comparison", [])[:5]:
            star = "→" if c["product"] == best["product"] else " "
            sale = " 🏷️" if c.get("recommendation", "").startswith("🔒") else ""
            lines.append(
                f"  {star} **{c['product']}**: "
                f"{c['nominal_rate']:.2f}% "
                f"(real {c['real_return']:+.2f}%) — "
                f"earns {self.fmt_currency(c['dollar_earnings'])} "
                f"over timeline{sale}"
            )
            if c.get("tax_advantage"):
                lines.append(f"    💡 {c['tax_advantage']}")
        lines.append("")

        # CD ladder
        cdl = plan.get("cd_ladder", {})
        if cdl.get("applicable"):
            lines.append("**🪜 CD Ladder Strategy:**")
            lines.append(f"   {cdl['reason']}")
            for rung in cdl.get("strategy", []):
                lines.append(
                    f"   • {rung['term']}: "
                    f"{self.fmt_currency(rung['amount'])} at "
                    f"{rung['rate']:.2f}% → earns "
                    f"{self.fmt_currency(rung['earnings'])}"
                )
            lines.append("")

        # I-Bond
        ib = plan.get("ibond_analysis", {})
        if ib:
            lines.append(
                f"**🇺🇸 I-Bond**: {ib['composite_rate']:.2f}% composite "
                f"({ib['fixed_rate']:.2f}% fixed + "
                f"{ib['inflation_component']:.2f}% inflation)"
            )
            lines.append(f"   {ib['fixed_verdict']}")
            lines.append(f"   {ib['reset_note']}")
            lines.append(f"   {ib['note']}")
            lines.append("")

        # HYSA vs CD crossover
        xo = plan.get("hysa_cd_crossover", {})
        if xo.get("applicable") and xo.get("note"):
            lines.append(f"**📊 HYSA vs CD**: {xo['note']}")
            lines.append("")

        # Inflation
        infl = plan.get("inflation_context", {})
        if infl.get("note"):
            lines.append(f"**📈 Inflation**: {infl['note']}")
            lines.append("")

        # Emergency fund note
        ef = plan.get("emergency_fund_note", "")
        if ef:
            lines.append(ef)
            lines.append("")

        # Action items
        actions = plan.get("action_items", [])
        if actions:
            lines.append("**⚡ Action items:**")
            for a in actions:
                lines.append(f"  {a}")

        return "\n".join(lines)
