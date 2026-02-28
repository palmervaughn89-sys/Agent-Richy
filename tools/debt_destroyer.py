"""Debt Destroyer — personalised debt payoff engine.

Produces avalanche, snowball, and hybrid payoff plans with month-by-month
calendars, refinance opportunity detection, balance-transfer analysis,
Fed-rate trajectory projections, and DTI health checks.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from tools.base import RichyToolBase, ToolResult
from tools.data_layer import get_latest_indicator, get_indicator_trend

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# Map debt type → FRED series for market-average rate
_MARKET_RATE_SERIES: dict[str, str] = {
    "credit_card":  "TERMCBCCALLNS",      #  avg CC rate (~21.5%)
    "auto":         "RIFLPBCIANM60NM",    #  5-yr new auto (~8.65%)
    "student":      "RIFLPBCIANM60NM",    #  proxy; we override with manual ref
    "mortgage":     "MORTGAGE30US",        #  30-yr fixed (~6.85%)
    "personal":     "TERMCBPER24NS",       #  24-month personal (~12.35%)
    "heloc":        "DPRIME",              #  Prime + spread (~7.50%)
    "medical":      "TERMCBPER24NS",       #  proxy
}

# Manual reference rates for debts that don't have clean FRED series
_MANUAL_REF_RATES: dict[str, dict] = {
    "student": {
        "federal_avg":       5.50,  # blended avg of undergrad / grad
        "private_avg":       9.75,
        "refi_best_case":    4.50,
        "warning": (
            "Federal student loans have protections (IDR, PSLF, deferment). "
            "Refinancing converts them to private — you lose those protections."
        ),
    },
    "mortgage": {
        "refi_cost_pct":     2.0,   # typical closing costs as % of balance
        "refi_threshold_bps": 75,   # 0.75% rate drop before refi makes sense
    },
    "auto": {
        "refi_best_case":    5.75,
        "refi_threshold_bps": 100,  # 1% drop
    },
    "personal": {
        "refi_best_case":    8.00,
    },
}

# Balance-transfer defaults
_BT_PROMO_MONTHS = 18        # typical 0% promo period
_BT_FEE_PCT = 3.0            # 3% transfer fee
_BT_MIN_BALANCE = 2_000.0    # don't bother below this
_BT_MIN_APR = 18.0           # only flag high-rate cards
_BT_BREAKEVEN_MAX = 3        # months — if breakeven < this, strong yes

# DTI thresholds
_DTI_HEALTHY = 15.0
_DTI_CAUTION = 20.0
_DTI_DANGER = 36.0


# ═══════════════════════════════════════════════════════════════════════════
# DEBT DESTROYER TOOL
# ═══════════════════════════════════════════════════════════════════════════

class DebtDestroyer(RichyToolBase):
    """Personalised debt payoff planner.

    Compares avalanche / snowball / hybrid strategies, detects refinance
    and balance-transfer opportunities, projects rate changes, and
    generates a month-by-month payoff calendar with milestones.
    """

    tool_id = 4
    tool_name = "debt_destroyer"
    description = (
        "Debt payoff strategy engine — avalanche, snowball, hybrid, "
        "refinance detection, balance-transfer analysis, rate trajectory"
    )
    required_profile: list[str] = ["debts"]

    # ── Router entry point ────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        """Run the full analysis and return a narrated ToolResult."""
        debts = user_profile.get("debts", [])
        if not debts:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=0.5,
                response=(
                    "I can build a personalised payoff plan! "
                    "Tell me about your debts — type, balance, APR, and "
                    "minimum payment for each."
                ),
                data_used=[],
                sources=["debt_destroyer"],
            )

        plan = self.analyze(debts, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=0.94,
            response=self._narrate(plan),
            data_used=plan.get("data_sources", []),
            accuracy_score=0.91,
            sources=[
                "FEDFUNDS", "DPRIME", "TERMCBCCALLNS",
                "MORTGAGE30US", "RIFLPBCIANM60NM",
                "TDSP (Debt-service ratio)",
            ],
            raw_data=plan,
        )

    # ── Main analysis ────────────────────────────────────────────────────

    def analyze(self, debts: list[dict], user_profile: dict) -> dict:
        """Produce the full payoff plan.

        Args:
            debts: ``[{type, balance, apr, min_payment, lender,
                       months_remaining}, ...]``
            user_profile: Must contain ``monthly_income``.  Optional:
                ``extra_monthly`` (extra $ beyond minimums).

        Returns:
            Plan dict (see module-level docstring for full schema).
        """
        now = datetime.now()
        monthly_income = float(user_profile.get("monthly_income", 0) or 0)
        extra_monthly = float(user_profile.get("extra_monthly", 0) or 0)

        # Normalise debt records
        debts = self._normalise_debts(debts)

        total_debt = sum(d["balance"] for d in debts)
        total_minimums = sum(d["min_payment"] for d in debts)
        data_sources: list[str] = []

        # ── 1. Rate comparison ────────────────────────────────────────────
        rate_gaps = self._compare_to_market_rates(debts)
        data_sources.extend(
            rg["series"] for rg in rate_gaps if rg.get("series")
        )

        # ── 2. Payoff strategies ──────────────────────────────────────────
        avalanche = self._calculate_payoff(debts, extra_monthly, "avalanche")
        snowball = self._calculate_payoff(debts, extra_monthly, "snowball")
        hybrid = self._calculate_payoff(debts, extra_monthly, "hybrid")

        # Pick recommended strategy
        strategy, reason = self._recommend_strategy(
            avalanche, snowball, hybrid, debts
        )
        chosen = {"avalanche": avalanche, "snowball": snowball, "hybrid": hybrid}[strategy]

        # ── 3. Balance-transfer check ─────────────────────────────────────
        cc_debts = [d for d in debts if d["type"] == "credit_card"]
        bt_analysis = self._check_balance_transfer(cc_debts)

        # ── 4. Rate trajectory ────────────────────────────────────────────
        rate_forecast = self._project_rate_changes(debts)
        data_sources.append("FEDFUNDS")

        # ── 5. DTI health ─────────────────────────────────────────────────
        dti = self._dti_health(total_minimums, monthly_income)
        data_sources.append("TDSP")

        # ── 6. Payoff calendar ────────────────────────────────────────────
        calendar = self._generate_calendar(chosen, debts, extra_monthly)

        # ── Quick wins ────────────────────────────────────────────────────
        quick_wins = self._find_quick_wins(debts, rate_gaps, bt_analysis)

        return {
            "total_debt": round(total_debt, 2),
            "monthly_minimums": round(total_minimums, 2),
            "dti_ratio": dti["ratio"],
            "dti_assessment": dti,
            "strategy": strategy,
            "strategy_reason": reason,
            "payoff_order": chosen["payoff_order"],
            "avalanche_interest": round(avalanche["total_interest"], 2),
            "snowball_interest": round(snowball["total_interest"], 2),
            "hybrid_interest": round(hybrid["total_interest"], 2),
            "chosen_interest": round(chosen["total_interest"], 2),
            "freedom_date": chosen["freedom_date"],
            "freedom_months": chosen["total_months"],
            "refinance_opps": rate_gaps,
            "balance_transfer": bt_analysis,
            "rate_forecast": rate_forecast,
            "calendar": calendar,
            "quick_wins": quick_wins,
            "data_sources": list(set(data_sources)),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    # ── Normalise ─────────────────────────────────────────────────────────

    @staticmethod
    def _normalise_debts(raw: list[dict]) -> list[dict]:
        """Ensure every debt dict has all required keys with sane types."""
        result = []
        for i, d in enumerate(raw):
            balance = float(d.get("balance", 0))
            if balance <= 0:
                continue
            apr = float(d.get("apr", 0))
            min_pay = float(d.get("min_payment", 0))
            # If no min_payment provided, estimate as 1% of balance or $25
            if min_pay <= 0:
                min_pay = max(balance * 0.01, 25.0)
            result.append({
                "id": i,
                "name": d.get("lender", d.get("name", f"Debt #{i+1}")),
                "type": d.get("type", "personal").lower().replace(" ", "_"),
                "balance": balance,
                "apr": apr,
                "min_payment": min_pay,
                "months_remaining": int(d.get("months_remaining", 0) or 0),
                "is_federal": d.get("is_federal", False),
            })
        return result

    # ── 1. Rate comparison ────────────────────────────────────────────────

    def _compare_to_market_rates(self, debts: list[dict]) -> list[dict]:
        """For each debt, compare user rate to market average.

        Flags debts where user rate exceeds market by ≥ 2 pp.
        """
        gaps: list[dict] = []
        for d in debts:
            dtype = d["type"]
            series = _MARKET_RATE_SERIES.get(dtype)
            market_rate: float | None = None
            source = "static_reference"

            if series:
                ind = get_latest_indicator(series)
                market_rate = ind.get("value")
                source = series

            # Override for student loans
            if dtype == "student":
                manual = _MANUAL_REF_RATES["student"]
                market_rate = (
                    manual["federal_avg"] if d.get("is_federal")
                    else manual["private_avg"]
                )
                source = "manual_reference"

            if market_rate is None:
                continue

            gap = d["apr"] - market_rate
            overpaying = gap >= 2.0

            action = ""
            savings_annually = 0.0
            if overpaying:
                savings_annually = d["balance"] * (gap / 100)
                if dtype == "student" and d.get("is_federal"):
                    action = (
                        "Your rate is high, but refinancing loses federal "
                        "protections (IDR, PSLF, deferment). Only refi if "
                        "income is very stable and savings are significant."
                    )
                elif dtype == "credit_card":
                    action = "Call your issuer and ask for a rate reduction."
                elif dtype == "mortgage":
                    action = (
                        f"Refinance could save ~${savings_annually:,.0f}/yr. "
                        f"Check closing costs (~2% of balance)."
                    )
                else:
                    action = (
                        f"Shop for a refinance — market avg is "
                        f"{market_rate:.1f}%. You'd save ~${savings_annually:,.0f}/yr."
                    )

            gaps.append({
                "debt": d["name"],
                "type": dtype,
                "current_apr": d["apr"],
                "market_avg": round(market_rate, 2),
                "gap_pp": round(gap, 2),
                "overpaying": overpaying,
                "savings_annual": round(savings_annually, 2),
                "action": action,
                "series": source,
            })

        return gaps

    # ── 2. Payoff strategies ──────────────────────────────────────────────

    def _calculate_payoff(
        self,
        debts: list[dict],
        extra_monthly: float,
        method: str,
    ) -> dict:
        """Simulate month-by-month payoff under a given strategy.

        Args:
            method: ``"avalanche"`` | ``"snowball"`` | ``"hybrid"``

        Returns:
            ``{payoff_order, total_interest, total_months, freedom_date,
               timeline}``
        """
        # Deep-copy balances so we don't mutate originals
        active = [
            {**d, "remaining": d["balance"], "interest_paid": 0.0,
             "payoff_month": 0}
            for d in debts
        ]

        # Sort order
        if method == "avalanche":
            active.sort(key=lambda d: -d["apr"])
        elif method == "snowball":
            active.sort(key=lambda d: d["remaining"])
        elif method == "hybrid":
            # Quick-win first: knock out any balance < $500, then avalanche
            quick = [d for d in active if d["remaining"] < 500]
            rest = [d for d in active if d["remaining"] >= 500]
            quick.sort(key=lambda d: d["remaining"])
            rest.sort(key=lambda d: -d["apr"])
            active = quick + rest

        month = 0
        total_interest = 0.0
        timeline: list[dict] = []         # detailed month-by-month
        payoff_events: list[dict] = []    # order of payoff
        freed_extra = 0.0                 # min payments freed up from paid-off debts
        max_months = 600                  # 50-year safety cap

        while any(d["remaining"] > 0.01 for d in active) and month < max_months:
            month += 1
            month_interest = 0.0
            month_payments: dict[str, float] = {}

            # Accrue interest on all active debts
            for d in active:
                if d["remaining"] <= 0:
                    continue
                monthly_rate = (d["apr"] / 100) / 12
                interest = d["remaining"] * monthly_rate
                d["remaining"] += interest
                d["interest_paid"] += interest
                month_interest += interest
                total_interest += interest

            # Pay minimums on all debts
            available_extra = extra_monthly + freed_extra
            for d in active:
                if d["remaining"] <= 0:
                    continue
                payment = min(d["min_payment"], d["remaining"])
                d["remaining"] -= payment
                month_payments[d["name"]] = payment
                if d["remaining"] <= 0.01:
                    d["remaining"] = 0
                    d["payoff_month"] = month
                    freed_extra += d["min_payment"]
                    payoff_events.append({
                        "name": d["name"],
                        "type": d["type"],
                        "original_balance": d["balance"],
                        "apr": d["apr"],
                        "months": month,
                        "interest_paid": round(d["interest_paid"], 2),
                    })

            # Apply extra to target debt (first still active)
            for d in active:
                if d["remaining"] <= 0 or available_extra <= 0:
                    continue
                payment = min(available_extra, d["remaining"])
                d["remaining"] -= payment
                available_extra -= payment
                month_payments[d["name"]] = (
                    month_payments.get(d["name"], 0) + payment
                )
                if d["remaining"] <= 0.01:
                    d["remaining"] = 0
                    d["payoff_month"] = month
                    freed_extra += d["min_payment"]
                    payoff_events.append({
                        "name": d["name"],
                        "type": d["type"],
                        "original_balance": d["balance"],
                        "apr": d["apr"],
                        "months": month,
                        "interest_paid": round(d["interest_paid"], 2),
                    })
                break  # extra goes to ONE target at a time

            # Record timeline entry
            balances = {d["name"]: round(d["remaining"], 2) for d in active}
            milestone = ""
            for evt in payoff_events:
                if evt["months"] == month:
                    freed = evt.get("apr", 0)  # just for label
                    milestone = (
                        f"🎉 {evt['name']} PAID OFF! "
                        f"+${self._find_min_payment(debts, evt['name']):,.0f}/mo freed up!"
                    )
                    break

            timeline.append({
                "month_num": month,
                "label": self._month_label(month),
                "payments": {k: round(v, 2) for k, v in month_payments.items()},
                "balances": balances,
                "milestone": milestone,
            })

        freedom_date = self._month_label(month)

        return {
            "method": method,
            "payoff_order": payoff_events,
            "total_interest": total_interest,
            "total_months": month,
            "freedom_date": freedom_date,
            "timeline": timeline,
        }

    @staticmethod
    def _find_min_payment(debts: list[dict], name: str) -> float:
        for d in debts:
            if d["name"] == name:
                return d["min_payment"]
        return 0.0

    @staticmethod
    def _month_label(months_from_now: int) -> str:
        """E.g. 'May 2026'."""
        now = datetime.now()
        future = now + timedelta(days=months_from_now * 30.44)
        return future.strftime("%b %Y")

    # ── Strategy recommendation ───────────────────────────────────────────

    @staticmethod
    def _recommend_strategy(
        avalanche: dict, snowball: dict, hybrid: dict,
        debts: list[dict],
    ) -> tuple[str, str]:
        """Pick the best strategy and explain why."""
        interest_diff = snowball["total_interest"] - avalanche["total_interest"]
        months_to_first_win_snowball = (
            snowball["payoff_order"][0]["months"] if snowball["payoff_order"] else 999
        )
        months_to_first_win_avalanche = (
            avalanche["payoff_order"][0]["months"] if avalanche["payoff_order"] else 999
        )

        # Check hybrid eligibility: any balance < $500 that isn't the highest APR?
        smallest = min(debts, key=lambda d: d["balance"]) if debts else None
        highest_apr = max(debts, key=lambda d: d["apr"]) if debts else None
        hybrid_eligible = (
            smallest and highest_apr
            and smallest["balance"] < 500
            and smallest["id"] != highest_apr["id"]
        )

        # If savings < $50 or < 2%, snowball is fine — motivation matters more
        if interest_diff < 50 or (
            avalanche["total_interest"] > 0
            and interest_diff / avalanche["total_interest"] < 0.02
        ):
            return "snowball", (
                f"Avalanche only saves ${interest_diff:,.0f} in interest — not "
                f"enough to offset the motivational boost of quick wins. "
                f"Snowball gives you your first payoff in "
                f"{months_to_first_win_snowball} months."
            )

        if hybrid_eligible and hybrid["total_interest"] <= avalanche["total_interest"] * 1.03:
            return "hybrid", (
                f"A quick hybrid win: pay off {smallest['name']} "
                f"(${smallest['balance']:,.0f}) first for momentum, then switch "
                f"to avalanche for the big-rate debts. Only costs "
                f"${hybrid['total_interest'] - avalanche['total_interest']:,.0f} "
                f"extra in interest."
            )

        return "avalanche", (
            f"Avalanche saves ${interest_diff:,.0f} vs snowball. "
            f"Your highest-rate debt ({highest_apr['name']} at "
            f"{highest_apr['apr']:.1f}%) should be attacked first."
        )

    # ── 3. Balance-transfer check ─────────────────────────────────────────

    @staticmethod
    def _check_balance_transfer(cc_debts: list[dict]) -> dict:
        """Analyse whether a 0% balance transfer card makes sense."""
        eligible: list[dict] = []
        total_savings = 0.0

        for d in cc_debts:
            if d["balance"] < _BT_MIN_BALANCE or d["apr"] < _BT_MIN_APR:
                continue

            transfer_fee = d["balance"] * (_BT_FEE_PCT / 100)
            monthly_interest_now = d["balance"] * (d["apr"] / 100 / 12)

            # Interest saved over promo period if balance paid off evenly
            months_to_payoff = min(
                _BT_PROMO_MONTHS,
                math.ceil(d["balance"] / max(d["min_payment"], 1)) + 1,
            )
            # Approximate total interest saved (declining balance)
            avg_balance = d["balance"] / 2  # simple midpoint
            interest_saved = avg_balance * (d["apr"] / 100) * (months_to_payoff / 12)
            net_savings = interest_saved - transfer_fee

            # Breakeven in months
            if monthly_interest_now > 0:
                breakeven_months = transfer_fee / monthly_interest_now
            else:
                breakeven_months = 999

            strength = "no"
            if breakeven_months < _BT_BREAKEVEN_MAX:
                strength = "strong_yes"
            elif net_savings > 100:
                strength = "yes"
            elif net_savings > 0:
                strength = "maybe"

            eligible.append({
                "debt": d["name"],
                "balance": d["balance"],
                "current_apr": d["apr"],
                "transfer_fee": round(transfer_fee, 2),
                "interest_saved": round(interest_saved, 2),
                "net_savings": round(net_savings, 2),
                "breakeven_months": round(breakeven_months, 1),
                "strength": strength,
            })
            if net_savings > 0:
                total_savings += net_savings

        recommendation = ""
        if any(e["strength"] == "strong_yes" for e in eligible):
            recommendation = (
                "Strong yes — at least one card would save you significant "
                "money with a balance transfer. Apply for a 0% BT card ASAP."
            )
        elif any(e["strength"] == "yes" for e in eligible):
            recommendation = (
                "Worth considering — a balance transfer saves real money, "
                "but make sure you can pay it off within the promo period."
            )
        elif any(e["strength"] == "maybe" for e in eligible):
            recommendation = (
                "Marginal — savings are small. Only do it if the annual fee "
                "is $0 and you won't rack up new charges."
            )
        else:
            recommendation = (
                "Not recommended right now — your balances or rates "
                "don't meet the threshold for a worthwhile transfer."
            )

        return {
            "eligible": eligible,
            "total_potential_savings": round(total_savings, 2),
            "recommendation": recommendation,
        }

    # ── 4. Rate trajectory ────────────────────────────────────────────────

    def _project_rate_changes(self, debts: list[dict]) -> dict:
        """Project how Fed rate changes will affect each debt type."""
        fed = get_latest_indicator("FEDFUNDS")
        fed_trend = get_indicator_trend("FEDFUNDS", months=6)

        fed_rate = fed.get("value", 4.50)
        direction = fed_trend.get("direction", "flat")
        change_pct = fed_trend.get("change_pct", 0)

        # Estimate future Fed rate (simple extrapolation)
        if direction == "rising":
            est_move_12mo = min(abs(change_pct) * 2, 1.0)  # cap at 100bp
            label = "hiking"
        elif direction == "falling":
            est_move_12mo = -min(abs(change_pct) * 2, 1.0)
            label = "cutting"
        else:
            est_move_12mo = 0.0
            label = "holding"

        # Per-debt-type impact
        impacts: list[dict] = []
        for d in debts:
            dtype = d["type"]
            # Variable-rate sensitivity (CC and HELOC move with Fed)
            if dtype in ("credit_card", "heloc"):
                projected_change = est_move_12mo  # 1:1 with Fed
                new_rate = d["apr"] + projected_change
                monthly_delta = d["balance"] * (projected_change / 100 / 12)
            elif dtype in ("auto", "personal", "student"):
                # Fixed-rate — no change on existing debt, but refi rates move
                projected_change = 0.0
                new_rate = d["apr"]
                monthly_delta = 0.0
            elif dtype == "mortgage":
                projected_change = 0.0  # fixed rate locked in
                new_rate = d["apr"]
                monthly_delta = 0.0
            else:
                projected_change = 0.0
                new_rate = d["apr"]
                monthly_delta = 0.0

            impacts.append({
                "debt": d["name"],
                "type": dtype,
                "current_apr": d["apr"],
                "projected_change_pp": round(projected_change, 2),
                "projected_new_apr": round(new_rate, 2),
                "monthly_cost_delta": round(monthly_delta, 2),
            })

        # Headline advice
        if label == "hiking":
            headline = (
                f"⚠️ Fed is hiking — variable rates are getting worse. "
                f"Lock in fixed rates or pay down credit cards FAST. "
                f"Expect ~{abs(est_move_12mo):.2f}% higher CC rates over "
                f"the next 12 months."
            )
        elif label == "cutting":
            headline = (
                f"📉 Fed is cutting rates — relief is coming. Your CC rates "
                f"should drop ~{abs(est_move_12mo):.2f}% over the next 12 months. "
                f"But still pay aggressively — even lower rates compound."
            )
        else:
            headline = (
                "📊 Fed is holding steady. No rate changes expected soon. "
                "Focus on the payoff plan — your rates won't change on their own."
            )

        return {
            "fed_rate": fed_rate,
            "direction": label,
            "est_12mo_move_pp": round(est_move_12mo, 2),
            "headline": headline,
            "impacts": impacts,
        }

    # ── 5. DTI health ─────────────────────────────────────────────────────

    @staticmethod
    def _dti_health(total_minimums: float, monthly_income: float) -> dict:
        """Calculate and assess debt-to-income ratio."""
        if monthly_income <= 0:
            return {
                "ratio": 0.0,
                "national_avg": 11.3,
                "assessment": "unknown",
                "message": "Can't calculate DTI without monthly income.",
            }

        dti = (total_minimums / monthly_income) * 100
        national = get_latest_indicator("TDSP")
        nat_avg = national.get("value", 11.3)

        if dti > _DTI_DANGER:
            assessment = "critical"
            msg = (
                f"🚨 Your DTI is {dti:.1f}% — mortgage-denial territory "
                f"(national avg: {nat_avg:.1f}%). Aggressive paydown is "
                f"essential before any major borrowing."
            )
        elif dti > _DTI_CAUTION:
            assessment = "elevated"
            msg = (
                f"⚠️ Your DTI is {dti:.1f}% — above the national average "
                f"of {nat_avg:.1f}%. Prioritise debt reduction to improve "
                f"borrowing power and reduce financial stress."
            )
        elif dti > _DTI_HEALTHY:
            assessment = "fair"
            msg = (
                f"Your DTI is {dti:.1f}% — slightly above the ideal range "
                f"but manageable. National avg is {nat_avg:.1f}%."
            )
        else:
            assessment = "healthy"
            msg = (
                f"✅ Your DTI is {dti:.1f}% — well below the national "
                f"average of {nat_avg:.1f}%. You're in solid shape."
            )

        return {
            "ratio": round(dti, 1),
            "national_avg": nat_avg,
            "assessment": assessment,
            "message": msg,
        }

    # ── 6. Calendar ───────────────────────────────────────────────────────

    @staticmethod
    def _generate_calendar(
        chosen: dict, debts: list[dict], extra: float,
    ) -> list[dict]:
        """Extract a condensed calendar from the chosen strategy timeline.

        Only includes months with milestones and every 3rd month for
        progress checks. Keeps calendar manageable for display.
        """
        timeline = chosen.get("timeline", [])
        calendar: list[dict] = []

        for entry in timeline:
            m = entry["month_num"]
            has_milestone = bool(entry.get("milestone"))
            # Include milestones, first month, every 3rd month, last month
            is_checkpoint = (m == 1 or m % 3 == 0 or m == len(timeline))

            if has_milestone or is_checkpoint:
                calendar.append({
                    "month": entry["label"],
                    "month_num": m,
                    "payments": entry["payments"],
                    "balances": entry["balances"],
                    "milestone": entry.get("milestone", ""),
                })

        return calendar

    # ── Quick wins ────────────────────────────────────────────────────────

    @staticmethod
    def _find_quick_wins(
        debts: list[dict],
        rate_gaps: list[dict],
        bt: dict,
    ) -> list[str]:
        """Generate a ranked list of actionable quick-win suggestions."""
        wins: list[str] = []

        # 1. Tiny debts that can be killed fast
        for d in sorted(debts, key=lambda x: x["balance"]):
            if d["balance"] < 300:
                wins.append(
                    f"💥 Kill {d['name']} (${d['balance']:,.0f}) this month — "
                    f"frees up ${d['min_payment']:,.0f}/mo for the next target."
                )
            elif d["balance"] < 1_000:
                months = math.ceil(d["balance"] / max(d["min_payment"], 1))
                wins.append(
                    f"💪 {d['name']} (${d['balance']:,.0f}) can be gone in "
                    f"~{months} months with just minimum payments."
                )
            if len(wins) >= 2:
                break

        # 2. Rate-negotiation calls
        for rg in rate_gaps:
            if rg["overpaying"] and rg["type"] == "credit_card":
                wins.append(
                    f"📞 Call {rg['debt']} and request a rate reduction — "
                    f"you're at {rg['current_apr']:.1f}% vs market "
                    f"{rg['market_avg']:.1f}%. Even 2-3% lower saves "
                    f"${rg['savings_annual']:,.0f}/yr."
                )
                break

        # 3. Balance transfer
        for e in bt.get("eligible", []):
            if e["strength"] in ("strong_yes", "yes"):
                wins.append(
                    f"💳 Transfer {e['debt']} (${e['balance']:,.0f}) to a 0% BT "
                    f"card — saves ~${e['net_savings']:,.0f} after fees."
                )
                break

        # 4. Refinance
        for rg in rate_gaps:
            if rg["overpaying"] and rg["type"] not in ("credit_card",):
                wins.append(
                    f"🔄 Refinance {rg['debt']} — you're paying "
                    f"{rg['current_apr']:.1f}% vs market {rg['market_avg']:.1f}%. "
                    f"Potential savings: ${rg['savings_annual']:,.0f}/yr."
                )
                break

        return wins[:5]

    # ── Narration ─────────────────────────────────────────────────────────

    def _narrate(self, plan: dict) -> str:
        """Build a human-readable summary from the plan dict."""
        lines: list[str] = []

        # Header
        lines.append(
            f"💣 **Debt Destroyer Plan** — "
            f"{self.fmt_currency(plan['total_debt'])} total debt"
        )
        lines.append("")

        # DTI
        dti = plan.get("dti_assessment", {})
        if dti.get("message"):
            lines.append(dti["message"])
            lines.append("")

        # Strategy headline
        lines.append(
            f"📋 **Recommended strategy: {plan['strategy'].upper()}**"
        )
        lines.append(plan["strategy_reason"])
        lines.append("")

        # Interest comparison
        lines.append("**Interest comparison:**")
        lines.append(
            f"  • Avalanche: {self.fmt_currency(plan['avalanche_interest'])} "
            f"in interest"
        )
        lines.append(
            f"  • Snowball: {self.fmt_currency(plan['snowball_interest'])} "
            f"in interest"
        )
        if plan.get("hybrid_interest") != plan["avalanche_interest"]:
            lines.append(
                f"  • Hybrid: {self.fmt_currency(plan['hybrid_interest'])} "
                f"in interest"
            )
        diff = plan["snowball_interest"] - plan["avalanche_interest"]
        if diff > 0:
            lines.append(
                f"  → Avalanche saves {self.fmt_currency(diff)} vs snowball."
            )
        lines.append("")

        # Payoff order
        lines.append("**Payoff order:**")
        for i, p in enumerate(plan["payoff_order"], 1):
            lines.append(
                f"  {i}. {p['name']} — {self.fmt_currency(p['original_balance'])} "
                f"at {p['apr']:.1f}% → paid off in **{p['months']} months** "
                f"({self.fmt_currency(p['interest_paid'])} interest)"
            )
        lines.append("")

        # Freedom date
        lines.append(
            f"🗓️ **DEBT-FREE DATE: {plan['freedom_date']}** "
            f"({plan['freedom_months']} months)"
        )
        lines.append(
            f"   Total interest: {self.fmt_currency(plan['chosen_interest'])}"
        )
        lines.append("")

        # Refinance
        refi_flags = [r for r in plan.get("refinance_opps", []) if r["overpaying"]]
        if refi_flags:
            lines.append("**🔍 Refinance opportunities:**")
            for r in refi_flags[:3]:
                lines.append(
                    f"  • {r['debt']}: your {r['current_apr']:.1f}% vs market "
                    f"{r['market_avg']:.1f}% → {r['action']}"
                )
            lines.append("")

        # Balance transfer
        bt = plan.get("balance_transfer", {})
        if bt.get("eligible"):
            lines.append("**💳 Balance transfer analysis:**")
            for e in bt["eligible"][:2]:
                lines.append(
                    f"  • {e['debt']} (${e['balance']:,.0f} at "
                    f"{e['current_apr']:.1f}%): fee {self.fmt_currency(e['transfer_fee'])}, "
                    f"saves {self.fmt_currency(e['interest_saved'])}. "
                    f"Breakeven: {e['breakeven_months']:.0f} months. "
                    f"Verdict: **{e['strength'].replace('_', ' ').title()}**"
                )
            lines.append(f"  → {bt['recommendation']}")
            lines.append("")

        # Rate forecast
        rf = plan.get("rate_forecast", {})
        if rf.get("headline"):
            lines.append(rf["headline"])
            lines.append("")

        # Quick wins
        qw = plan.get("quick_wins", [])
        if qw:
            lines.append("**⚡ Quick wins:**")
            for w in qw:
                lines.append(f"  {w}")

        return "\n".join(lines)
