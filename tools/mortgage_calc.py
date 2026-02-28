"""Mortgage Calculator — full cost of buying vs renting, rate
trajectory, ARM vs fixed, refinance analysis, and affordability
scoring powered by heartbeat engine data.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from tools.base import RichyToolBase, ToolResult
from tools.data_layer import get_latest_indicator, get_indicator_trend

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA (manual)
# ═══════════════════════════════════════════════════════════════════════════

# ── Property tax rates by state (effective rate %) ────────────────────────
_PROPERTY_TAX: dict[str, float] = {
    "AL": 0.39, "AK": 1.04, "AZ": 0.62, "AR": 0.62, "CA": 0.71,
    "CO": 0.49, "CT": 1.79, "DE": 0.53, "FL": 0.89, "GA": 0.83,
    "HI": 0.27, "ID": 0.63, "IL": 2.07, "IN": 0.81, "IA": 1.52,
    "KS": 1.33, "KY": 0.83, "LA": 0.51, "ME": 1.24, "MD": 1.00,
    "MA": 1.15, "MI": 1.38, "MN": 1.05, "MS": 0.67, "MO": 0.91,
    "MT": 0.74, "NE": 1.61, "NV": 0.55, "NH": 1.86, "NJ": 2.23,
    "NM": 0.67, "NY": 1.62, "NC": 0.77, "ND": 0.98, "OH": 1.53,
    "OK": 0.87, "OR": 0.93, "PA": 1.49, "RI": 1.40, "SC": 0.55,
    "SD": 1.14, "TN": 0.64, "TX": 1.68, "UT": 0.58, "VT": 1.83,
    "VA": 0.80, "WA": 0.87, "WV": 0.57, "WI": 1.61, "WY": 0.55,
    "DC": 0.56,
}
_DEFAULT_PROPERTY_TAX = 1.00  # national average

# ── Homeowners insurance (annual, % of home value) ────────────────────────
_INSURANCE_RATE = 0.0035  # 0.35% of home value (national avg ~$1,400/$400K)

# ── PMI rates by LTV band and credit score ───────────────────────────────
_PMI_RATES: dict[str, dict[str, float]] = {
    # credit_tier → {ltv_band: annual_rate}
    "excellent": {"85": 0.0019, "90": 0.0033, "95": 0.0051, "97": 0.0073},
    "good":      {"85": 0.0030, "90": 0.0044, "95": 0.0065, "97": 0.0095},
    "fair":      {"85": 0.0055, "90": 0.0076, "95": 0.0110, "97": 0.0150},
}

# ── Closing costs by scenario ────────────────────────────────────────────
_CLOSING_COST_BUY_PCT = 0.03    # 2-5%, use 3%
_CLOSING_COST_REFI_PCT = 0.02   # 1.5-3%, use 2%
_SELLING_COST_PCT = 0.07         # agent fees + transfer taxes + misc

# ── Maintenance / repair reserve ─────────────────────────────────────────
_MAINTENANCE_RATE = 0.01  # 1% of home value per year

# ── HOA default (user can override) ──────────────────────────────────────
_DEFAULT_HOA = 0.0

# ── Appreciation defaults ────────────────────────────────────────────────
_DEFAULT_APPRECIATION = 0.035   # 3.5% (historical avg ~3.5-4%)
_DEFAULT_RENT_INCREASE = 0.04   # 4% annual CPI shelter trend


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortisation monthly P&I payment."""
    if annual_rate <= 0 or principal <= 0:
        return principal / max(years * 12, 1)
    r = annual_rate / 12
    n = years * 12
    return principal * (r * (1 + r) ** n) / (((1 + r) ** n) - 1)


def _amortisation_schedule(
    principal: float,
    annual_rate: float,
    years: int,
) -> list[dict]:
    """Year-by-year amortisation with balance, interest, principal paid."""
    schedule: list[dict] = []
    r = annual_rate / 12
    n = years * 12
    pmt = _monthly_payment(principal, annual_rate, years)
    balance = principal
    for yr in range(1, years + 1):
        yr_interest = 0.0
        yr_principal = 0.0
        for _ in range(12):
            if balance <= 0:
                break
            interest = balance * r
            princ = pmt - interest
            yr_interest += interest
            yr_principal += princ
            balance = max(balance - princ, 0)
        schedule.append({
            "year": yr,
            "balance": round(balance, 2),
            "interest_paid": round(yr_interest, 2),
            "principal_paid": round(yr_principal, 2),
        })
    return schedule


def _credit_tier(score: int) -> str:
    if score >= 740:
        return "excellent"
    elif score >= 680:
        return "good"
    return "fair"


def _pmi_rate(ltv: float, score: int) -> float:
    """Annual PMI rate based on LTV and credit score."""
    tier = _credit_tier(score)
    tiers = _PMI_RATES.get(tier, _PMI_RATES["good"])
    if ltv <= 0.80:
        return 0.0
    elif ltv <= 0.85:
        return tiers.get("85", 0.003)
    elif ltv <= 0.90:
        return tiers.get("90", 0.005)
    elif ltv <= 0.95:
        return tiers.get("95", 0.007)
    return tiers.get("97", 0.010)


def _state_from_zip(zip_code: str) -> str:
    """Very rough ZIP → state prefix mapping (first 3 digits)."""
    _ZIP_RANGES: list[tuple[int, int, str]] = [
        (100, 149, "NY"), (150, 196, "PA"), (197, 199, "DE"),
        (200, 205, "DC"), (206, 246, "VA"), (247, 268, "WV"),
        (270, 289, "NC"), (290, 299, "SC"), (300, 319, "GA"),
        (320, 349, "FL"), (350, 369, "AL"), (370, 385, "TN"),
        (386, 397, "MS"), (400, 427, "KY"), (430, 459, "OH"),
        (460, 479, "IN"), (480, 499, "MI"), (500, 528, "IA"),
        (530, 549, "WI"), (550, 567, "MN"), (570, 577, "SD"),
        (580, 588, "ND"), (590, 599, "MT"), (600, 629, "IL"),
        (630, 658, "MO"), (660, 679, "KS"), (680, 693, "NE"),
        (700, 714, "LA"), (716, 729, "AR"), (730, 749, "OK"),
        (750, 799, "TX"), (800, 816, "CO"), (820, 831, "WY"),
        (832, 838, "ID"), (840, 847, "UT"), (850, 865, "AZ"),
        (870, 884, "NM"), (889, 898, "NV"), (900, 966, "CA"),
        (967, 968, "HI"), (970, 979, "OR"), (980, 994, "WA"),
        (995, 999, "AK"),
    ]
    try:
        prefix = int(zip_code[:3])
    except (ValueError, TypeError):
        return ""
    for lo, hi, st in _ZIP_RANGES:
        if lo <= prefix <= hi:
            return st
    return ""


# ═══════════════════════════════════════════════════════════════════════════
# MORTGAGE CALC TOOL
# ═══════════════════════════════════════════════════════════════════════════

class MortgageCalc(RichyToolBase):
    """Full mortgage / housing calculator with heartbeat-powered rate
    trajectory, rent-vs-buy, refinance, and affordability analysis.
    """

    tool_id = 39
    tool_name = "mortgage_calculator"
    description = (
        "Mortgage payment, rent vs buy, refinance, "
        "home affordability, and rate trajectory"
    )
    required_profile: list[str] = []

    # ── Router entry ──────────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        scenario = (
            user_profile.get("scenario", "buying") or "buying"
        ).lower().replace(" ", "_")
        plan = self.analyze(scenario, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan, scenario),
            data_used=[
                "home_price", "down_payment", "income", "monthly_debts",
                "credit_score", "zip_code",
            ],
            accuracy_score=0.87,
            sources=[
                "MORTGAGE30US", "MORTGAGE15US", "MORTGAGE5US",
                "MSPUS", "FIXHAI", "FEDFUNDS", "T10Y2Y",
                "CSUSHPINSA", "CUSR0000SAH1",
            ],
            raw_data=plan,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════

    def analyze(self, scenario: str, user_profile: dict) -> dict:
        """Run the full mortgage analysis pipeline.

        ``scenario``: "buying" | "refinancing" | "rent_vs_buy"

        Keys in ``user_profile``:
            home_price, down_payment_pct (0-100), loan_term (15|30),
            zip_code, credit_score, income, monthly_debts,
            hoa (monthly), first_time (bool),
            current_rent (for rent_vs_buy),
            current_mortgage: {balance, rate, payment, years_left} (for refi)
        """
        # ── Extract inputs ────────────────────────────────────────────────
        home_price = float(user_profile.get("home_price", 0) or 0)
        down_pct = float(user_profile.get("down_payment_pct", 20) or 20) / 100
        loan_term = int(user_profile.get("loan_term", 30) or 30)
        zip_code = str(user_profile.get("zip_code", "") or "")
        credit_score = int(user_profile.get("credit_score", 720) or 720)
        income = float(user_profile.get("income", 0) or 0)
        monthly_debts = float(user_profile.get("monthly_debts", 0) or 0)
        hoa = float(user_profile.get("hoa", _DEFAULT_HOA) or _DEFAULT_HOA)
        first_time = bool(user_profile.get("first_time", False))
        current_rent = float(user_profile.get("current_rent", 0) or 0)
        current_mortgage = user_profile.get("current_mortgage", {}) or {}

        state = _state_from_zip(zip_code) if zip_code else (
            user_profile.get("state", "") or ""
        ).upper()

        # ── Pull heartbeat rates ──────────────────────────────────────────
        rates = self._get_current_rates()
        rate_key = f"MORTGAGE{loan_term}US" if loan_term in (15, 30) else "MORTGAGE30US"
        note_rate = rates.get(rate_key, rates["MORTGAGE30US"])

        # ── Calculate use-case-default home price from MSPUS if missing ───
        if home_price <= 0:
            home_price = rates.get("MSPUS", 420_000)

        down_payment = home_price * down_pct
        loan_amount = home_price - down_payment
        ltv = loan_amount / home_price if home_price else 0.95

        # ── 1. Monthly breakdown ──────────────────────────────────────────
        monthly = self._monthly_breakdown(
            loan_amount, note_rate, loan_term,
            home_price, state, credit_score, ltv, hoa,
        )

        # ── 2. Affordability ─────────────────────────────────────────────
        affordability = self._affordability(
            monthly["total"], income, monthly_debts, rates,
        )

        # ── 3. Rate analysis + trajectory ─────────────────────────────────
        rate_analysis = self._rate_analysis(rates, note_rate, loan_amount, loan_term)

        # ── 4. ARM vs Fixed ───────────────────────────────────────────────
        arm_comparison = self._arm_vs_fixed(
            loan_amount, note_rate, rates.get("MORTGAGE5US", note_rate),
            loan_term,
        )

        # ── 5. Total cost of ownership ────────────────────────────────────
        total_cost = self._total_ownership_cost(
            loan_amount, note_rate, loan_term,
            home_price, monthly, down_payment,
        )

        # ── 6. Scenario-specific ──────────────────────────────────────────
        rent_vs_buy = None
        refinance = None

        if scenario == "rent_vs_buy" and current_rent > 0:
            rent_vs_buy = self._rent_vs_buy(
                home_price, down_payment, loan_amount, note_rate,
                loan_term, monthly, current_rent, state,
            )

        if scenario == "refinancing" and current_mortgage:
            refinance = self._refinance_analysis(
                current_mortgage, note_rate, rates,
            )

        # ── Confidence ────────────────────────────────────────────────────
        filled = sum(1 for v in [
            home_price, income, credit_score, zip_code,
            current_rent, bool(current_mortgage),
        ] if v)
        confidence = min(0.70 + filled * 0.04, 0.93)

        return {
            "scenario": scenario,
            "inputs": {
                "home_price": home_price,
                "down_payment": round(down_payment, 2),
                "down_payment_pct": round(down_pct * 100, 1),
                "loan_amount": round(loan_amount, 2),
                "loan_term": loan_term,
                "note_rate": note_rate,
                "ltv": round(ltv * 100, 1),
                "credit_score": credit_score,
                "state": state or "N/A",
            },
            "monthly_breakdown": monthly,
            "affordability": affordability,
            "rate_analysis": rate_analysis,
            "arm_vs_fixed": arm_comparison,
            "total_ownership_cost": total_cost,
            "rent_vs_buy": rent_vs_buy,
            "refinance": refinance,
            "confidence": round(confidence, 2),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1 — MONTHLY BREAKDOWN
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _monthly_breakdown(
        loan_amount: float,
        rate: float,
        term: int,
        home_price: float,
        state: str,
        credit_score: int,
        ltv: float,
        hoa: float,
    ) -> dict:
        pi = round(_monthly_payment(loan_amount, rate / 100, term), 2)

        prop_tax_rate = _PROPERTY_TAX.get(state, _DEFAULT_PROPERTY_TAX) / 100
        tax_monthly = round(home_price * prop_tax_rate / 12, 2)

        insurance_monthly = round(home_price * _INSURANCE_RATE / 12, 2)

        pmi_annual_rate = _pmi_rate(ltv, credit_score)
        pmi_monthly = round(loan_amount * pmi_annual_rate / 12, 2)

        maintenance_monthly = round(home_price * _MAINTENANCE_RATE / 12, 2)

        total = round(pi + tax_monthly + insurance_monthly + pmi_monthly + hoa + maintenance_monthly, 2)

        return {
            "principal_interest": pi,
            "property_tax": tax_monthly,
            "insurance": insurance_monthly,
            "pmi": pmi_monthly,
            "hoa": round(hoa, 2),
            "maintenance": maintenance_monthly,
            "total": total,
            "pmi_note": (
                f"PMI at {pmi_annual_rate:.2%}/yr until LTV reaches 80%"
                if pmi_monthly > 0
                else "No PMI required (≤80% LTV)"
            ),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2 — AFFORDABILITY
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _affordability(
        total_housing: float,
        annual_income: float,
        monthly_debts: float,
        rates: dict,
    ) -> dict:
        monthly_income = annual_income / 12 if annual_income else 0
        front_ratio = (
            (total_housing / monthly_income * 100) if monthly_income else 0
        )
        back_ratio = (
            ((total_housing + monthly_debts) / monthly_income * 100)
            if monthly_income else 0
        )

        if front_ratio <= 28 and back_ratio <= 36:
            status = "COMFORTABLE"
            note = (
                "Your ratios are within standard guidelines. "
                "Lenders will view this favourably."
            )
        elif front_ratio <= 31 and back_ratio <= 43:
            status = "STRETCHED"
            note = (
                "Ratios are above ideal but within FHA/VA limits. "
                "You'll qualify but have less breathing room."
            )
        else:
            status = "OVER_EXTENDED"
            note = (
                "Housing cost exceeds recommended guidelines. "
                "Consider a lower price, larger down payment, or paying off debts first."
            )

        # FIXHAI (Fed Housing Affordability Index — 100 = median family
        # can afford median home)
        fixhai = rates.get("FIXHAI", 100)
        affordability_context = ""
        if fixhai < 100:
            affordability_context = (
                f"National affordability index is {fixhai:.0f} "
                f"(below 100 = median family can't afford median home). "
                f"Affordability is historically poor."
            )
        else:
            affordability_context = (
                f"National affordability index is {fixhai:.0f} "
                f"(above 100 — median family can afford median home)."
            )

        return {
            "front_ratio": round(front_ratio, 1),
            "back_ratio": round(back_ratio, 1),
            "status": status,
            "note": note,
            "fixhai": fixhai,
            "affordability_context": affordability_context,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3 — RATE ANALYSIS + TRAJECTORY
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _get_current_rates() -> dict:
        """Pull latest mortgage rates and housing indicators."""
        series = [
            "MORTGAGE30US", "MORTGAGE15US", "MORTGAGE5US",
            "MSPUS", "FIXHAI", "FEDFUNDS", "T10Y2Y",
            "CSUSHPINSA", "CUSR0000SAH1",
        ]
        out: dict = {}
        for s in series:
            data = get_latest_indicator(s)
            out[s] = data.get("value", 0)
        return out

    def _rate_analysis(
        self,
        rates: dict,
        note_rate: float,
        loan_amount: float,
        term: int,
    ) -> dict:
        """Heartbeat-driven rate trajectory and lock recommendation."""
        fed_rate = rates.get("FEDFUNDS", 4.5)
        t10y2y = rates.get("T10Y2Y", 0.15)

        # Fed trend
        fed_trend = get_indicator_trend("FEDFUNDS", months=6)
        fed_dir = fed_trend.get("direction", "flat")

        # Mortgage trend
        m30_trend = get_indicator_trend("MORTGAGE30US", months=6)
        m30_dir = m30_trend.get("direction", "flat")

        # Rate projection (simple)
        if fed_dir == "falling":
            projected_6m = max(note_rate - 0.375, 3.0)
            trajectory = "FALLING"
            recommendation = (
                "Rates are trending down as the Fed eases. "
                "If buying soon, consider a float-down option. "
                "If you can wait 3-6 months, you may get a better rate."
            )
        elif fed_dir == "rising":
            projected_6m = note_rate + 0.25
            trajectory = "RISING"
            recommendation = (
                "Rates are trending up. Lock your rate as soon as possible. "
                "Every 0.25% increase adds to your monthly payment."
            )
        else:
            projected_6m = note_rate
            trajectory = "STABLE"
            if t10y2y < 0:
                recommendation = (
                    "Rates are stable but the yield curve is inverted — "
                    "recession risk could push rates lower. Consider a "
                    "shorter lock period."
                )
            else:
                recommendation = (
                    "Rates are stable. No urgency to rush, but no reason "
                    "to wait either. Lock when you find the right home."
                )

        # Impact of 0.25% change
        pmt_current = _monthly_payment(loan_amount, note_rate / 100, term)
        pmt_higher = _monthly_payment(loan_amount, (note_rate + 0.25) / 100, term)
        pmt_lower = _monthly_payment(loan_amount, (note_rate - 0.25) / 100, term)
        impact_per_quarter = round(pmt_higher - pmt_current, 2)

        return {
            "current_30yr": rates.get("MORTGAGE30US", 6.85),
            "current_15yr": rates.get("MORTGAGE15US", 6.10),
            "current_5_1_arm": rates.get("MORTGAGE5US", 6.30),
            "your_rate": note_rate,
            "trajectory": trajectory,
            "projected_6m": round(projected_6m, 3),
            "fed_funds": fed_rate,
            "fed_direction": fed_dir,
            "recommendation": recommendation,
            "rate_impact": {
                "per_quarter_pct_monthly": impact_per_quarter,
                "per_quarter_pct_yearly": round(impact_per_quarter * 12, 2),
                "note": (
                    f"Every 0.25% rate change = "
                    f"${abs(impact_per_quarter):,.0f}/month "
                    f"(${abs(impact_per_quarter * 12):,.0f}/year)"
                ),
            },
        }

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4 — ARM vs FIXED
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _arm_vs_fixed(
        loan_amount: float,
        fixed_rate: float,
        arm_rate: float,
        term: int,
    ) -> dict:
        """Compare 5/1 ARM vs fixed-rate over first 5 years + worst case."""
        fixed_pmt = _monthly_payment(loan_amount, fixed_rate / 100, term)
        arm_pmt = _monthly_payment(loan_amount, arm_rate / 100, term)

        monthly_savings = round(fixed_pmt - arm_pmt, 2)
        five_yr_savings = round(monthly_savings * 60, 2)

        # Worst-case: ARM resets to fixed + 2% after year 5
        worst_rate = arm_rate + 2.0
        # Remaining balance after 5 years on ARM
        schedule = _amortisation_schedule(loan_amount, arm_rate / 100, term)
        balance_yr5 = schedule[4]["balance"] if len(schedule) >= 5 else loan_amount * 0.9
        worst_pmt = _monthly_payment(balance_yr5, worst_rate / 100, term - 5)
        worst_increase = round(worst_pmt - fixed_pmt, 2)

        if monthly_savings > 150 and worst_increase < 300:
            recommendation = (
                f"ARM saves ${monthly_savings:,.0f}/mo for 5 years "
                f"(${five_yr_savings:,.0f} total). Worst-case year 6 is only "
                f"${worst_increase:,.0f}/mo more than the fixed. "
                f"Good option if you might move or refinance within 5-7 years."
            )
        elif monthly_savings > 0:
            recommendation = (
                f"ARM saves ${monthly_savings:,.0f}/mo initially, but "
                f"worst-case at year 6 could add ${worst_increase:,.0f}/mo. "
                f"Only consider if you're very confident you'll move/refi by year 5."
            )
        else:
            recommendation = (
                "ARM rate is not meaningfully lower than fixed. "
                "Go with the fixed-rate for certainty."
            )

        return {
            "fixed_rate": fixed_rate,
            "arm_rate": arm_rate,
            "fixed_payment": round(fixed_pmt, 2),
            "arm_payment": round(arm_pmt, 2),
            "monthly_savings": monthly_savings,
            "five_year_savings": five_yr_savings,
            "worst_case_rate_yr6": round(worst_rate, 2),
            "worst_case_payment": round(worst_pmt, 2),
            "worst_case_increase_vs_fixed": worst_increase,
            "recommendation": recommendation,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 5 — RENT VS BUY
    # ═══════════════════════════════════════════════════════════════════════

    def _rent_vs_buy(
        self,
        home_price: float,
        down_payment: float,
        loan_amount: float,
        rate: float,
        term: int,
        monthly: dict,
        current_rent: float,
        state: str,
    ) -> dict:
        """Multi-year rent vs buy comparison with equity build and
        appreciation."""
        # CPI shelter trend for rent escalation
        shelter_trend = get_indicator_trend("CUSR0000SAH1", months=12)
        rent_increase = _DEFAULT_RENT_INCREASE
        if shelter_trend.get("direction") == "falling":
            rent_increase = 0.03
        elif shelter_trend.get("direction") == "rising":
            rent_increase = 0.05

        # Home appreciation from Case-Shiller trend
        cs_trend = get_indicator_trend("CSUSHPINSA", months=12)
        appreciation = _DEFAULT_APPRECIATION
        if cs_trend.get("change_pct", 0) > 0:
            appreciation = max(min(cs_trend["change_pct"] / 100, 0.08), 0.02)

        closing_buy = home_price * _CLOSING_COST_BUY_PCT
        schedule = _amortisation_schedule(loan_amount, rate / 100, term)

        comparisons: dict[int, dict] = {}
        breakeven_year: Optional[int] = None

        for horizon in [3, 5, 7, 10, 15]:
            # ── Rent total ────────────────────────────────────────────────
            rent_total = 0.0
            rent = current_rent
            for yr in range(1, horizon + 1):
                rent_total += rent * 12
                rent *= (1 + rent_increase)

            # ── Buy total ─────────────────────────────────────────────────
            # Payments
            buy_payments = monthly["total"] * 12 * min(horizon, term)
            # Closing costs (buy + eventual sell)
            sell_price = home_price * ((1 + appreciation) ** horizon)
            selling_costs = sell_price * _SELLING_COST_PCT
            # Equity built
            if horizon <= len(schedule):
                equity_from_payments = loan_amount - schedule[horizon - 1]["balance"]
            else:
                equity_from_payments = loan_amount
            appreciation_gain = sell_price - home_price
            total_equity = down_payment + equity_from_payments + appreciation_gain
            # Net cost of buying
            buy_total = (
                buy_payments + closing_buy + selling_costs
                - total_equity
                - down_payment  # down payment is returned via equity
            )
            # Tax benefit (rough: mortgage interest deduction in first years)
            if horizon <= len(schedule):
                total_interest = sum(
                    s["interest_paid"] for s in schedule[:horizon]
                )
            else:
                total_interest = sum(s["interest_paid"] for s in schedule)
            tax_benefit = total_interest * 0.22  # assume 22% bracket
            buy_total -= tax_benefit

            diff = rent_total - buy_total
            winner = "BUY" if diff > 0 else "RENT"

            comparisons[horizon] = {
                "years": horizon,
                "rent_total": round(rent_total, 2),
                "buy_total": round(buy_total, 2),
                "difference": round(diff, 2),
                "winner": winner,
                "home_value": round(sell_price, 2),
                "equity": round(total_equity, 2),
            }

            if breakeven_year is None and winner == "BUY":
                breakeven_year = horizon

        # If no breakeven found in standard horizons, estimate it
        if breakeven_year is None:
            breakeven_year = 99  # means renting wins even at 15 years

        return {
            "current_rent": current_rent,
            "rent_annual_increase": f"{rent_increase:.0%}",
            "home_appreciation": f"{appreciation:.1%}",
            "breakeven_years": breakeven_year,
            "comparisons": comparisons,
            "recommendation": self._rent_buy_rec(breakeven_year, comparisons),
        }

    @staticmethod
    def _rent_buy_rec(breakeven: int, comparisons: dict) -> str:
        if breakeven <= 3:
            return (
                "Buying is favourable even on a short horizon. "
                "With your rent level and local appreciation, "
                "owning pays off quickly."
            )
        elif breakeven <= 5:
            return (
                f"Buying breaks even around year {breakeven}. "
                f"If you plan to stay 5+ years, buying is the stronger move."
            )
        elif breakeven <= 7:
            return (
                f"Breakeven is around year {breakeven}. "
                f"Only buy if you're confident you'll stay 7+ years. "
                f"Otherwise renting preserves flexibility."
            )
        elif breakeven <= 15:
            return (
                f"Breakeven is year {breakeven} — renting is cheaper in the "
                f"medium term. Consider buying only if it's a lifestyle choice "
                f"or you'll stay a very long time."
            )
        return (
            "Renting appears cheaper even at 15 years given current prices "
            "and rates. Focus on investing the difference instead."
        )

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 6 — REFINANCE
    # ═══════════════════════════════════════════════════════════════════════

    def _refinance_analysis(
        self,
        current: dict,
        market_rate: float,
        rates: dict,
    ) -> dict:
        """Compare current mortgage to refinancing at market rates."""
        old_balance = float(current.get("balance", 0) or 0)
        old_rate = float(current.get("rate", 0) or 0)
        old_payment = float(current.get("payment", 0) or 0)
        old_years_left = int(current.get("years_left", 25) or 25)

        if old_balance <= 0:
            return {"applicable": False, "note": "No current mortgage balance provided."}

        # Use the old payment if given, otherwise compute
        if old_payment <= 0:
            old_payment = _monthly_payment(old_balance, old_rate / 100, old_years_left)

        new_payment = _monthly_payment(old_balance, market_rate / 100, old_years_left)
        closing = old_balance * _CLOSING_COST_REFI_PCT
        monthly_savings = round(old_payment - new_payment, 2)

        if monthly_savings <= 0:
            return {
                "applicable": True,
                "makes_sense": False,
                "current_rate": old_rate,
                "new_rate": market_rate,
                "monthly_savings": monthly_savings,
                "note": (
                    f"Your current rate ({old_rate}%) is already at or below "
                    f"market ({market_rate}%). Refinancing doesn't save money."
                ),
            }

        breakeven_months = math.ceil(closing / monthly_savings) if monthly_savings > 0 else 999
        lifetime_savings = round(monthly_savings * old_years_left * 12 - closing, 2)

        # Rate trajectory — should they wait?
        fed_trend = get_indicator_trend("FEDFUNDS", months=6)
        wait_note = ""
        if fed_trend.get("direction") == "falling":
            projected = max(market_rate - 0.375, 3.0)
            wait_note = (
                f"Fed is cutting — rates may drop to ~{projected:.2f}% "
                f"in 6 months. Waiting could save an additional "
                f"${round(_monthly_payment(old_balance, projected / 100, old_years_left) - new_payment, 0) * -1:,.0f}/mo. "
                f"Consider: refi now + refi again later, or wait."
            )
        elif fed_trend.get("direction") == "rising":
            wait_note = "Rates are rising — refinance sooner rather than later."

        return {
            "applicable": True,
            "makes_sense": True,
            "current_rate": old_rate,
            "new_rate": market_rate,
            "old_payment": round(old_payment, 2),
            "new_payment": round(new_payment, 2),
            "monthly_savings": monthly_savings,
            "closing_costs": round(closing, 2),
            "breakeven_months": breakeven_months,
            "lifetime_savings": lifetime_savings,
            "rate_trajectory_note": wait_note,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # TOTAL OWNERSHIP COST
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _total_ownership_cost(
        loan_amount: float,
        rate: float,
        term: int,
        home_price: float,
        monthly: dict,
        down_payment: float,
    ) -> dict:
        schedule = _amortisation_schedule(loan_amount, rate / 100, term)
        total_interest = sum(s["interest_paid"] for s in schedule)
        total_payments = monthly["principal_interest"] * term * 12
        total_tax = monthly["property_tax"] * term * 12
        total_insurance = monthly["insurance"] * term * 12
        total_maintenance = monthly["maintenance"] * term * 12

        grand_total = (
            down_payment + total_payments + total_tax
            + total_insurance + total_maintenance
        )

        return {
            "down_payment": round(down_payment, 2),
            "total_principal_interest": round(total_payments, 2),
            "total_interest_only": round(total_interest, 2),
            "total_property_tax": round(total_tax, 2),
            "total_insurance": round(total_insurance, 2),
            "total_maintenance": round(total_maintenance, 2),
            "grand_total": round(grand_total, 2),
            "interest_to_principal": (
                f"For every $1 of principal, you'll pay "
                f"${total_interest / loan_amount:.2f} in interest"
                if loan_amount else "N/A"
            ),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # NARRATION
    # ═══════════════════════════════════════════════════════════════════════

    def _narrate(self, plan: dict, scenario: str) -> str:
        lines: list[str] = []
        inp = plan["inputs"]
        m = plan["monthly_breakdown"]
        aff = plan["affordability"]
        ra = plan["rate_analysis"]

        # ── Header ────────────────────────────────────────────────────────
        emoji = {"buying": "🏠", "refinancing": "🔄", "rent_vs_buy": "🏠↔️🏢"}.get(
            scenario, "🏠"
        )
        lines.append(
            f"{emoji} **Mortgage Calculator** — "
            f"{scenario.replace('_', ' ').title()}"
        )
        lines.append("")

        # ── Inputs recap ──────────────────────────────────────────────────
        lines.append(
            f"Home: {self.fmt_currency(inp['home_price'])} | "
            f"Down: {inp['down_payment_pct']:.0f}% "
            f"({self.fmt_currency(inp['down_payment'])}) | "
            f"Loan: {self.fmt_currency(inp['loan_amount'])} | "
            f"Rate: {inp['note_rate']:.3f}% | "
            f"Term: {inp['loan_term']}yr"
        )
        lines.append("")

        # ── Monthly breakdown ─────────────────────────────────────────────
        lines.append("**Monthly breakdown:**")
        lines.append(f"  P&I:           {self.fmt_currency(m['principal_interest'])}")
        lines.append(f"  Property tax:  {self.fmt_currency(m['property_tax'])}")
        lines.append(f"  Insurance:     {self.fmt_currency(m['insurance'])}")
        if m["pmi"] > 0:
            lines.append(f"  PMI:           {self.fmt_currency(m['pmi'])}  ({m['pmi_note']})")
        if m["hoa"] > 0:
            lines.append(f"  HOA:           {self.fmt_currency(m['hoa'])}")
        lines.append(f"  Maintenance:   {self.fmt_currency(m['maintenance'])}")
        lines.append(f"  ─────────────────────")
        lines.append(f"  **Total:       {self.fmt_currency(m['total'])}**/mo")
        lines.append("")

        # ── Affordability ─────────────────────────────────────────────────
        aff_emoji = {
            "COMFORTABLE": "✅", "STRETCHED": "⚠️", "OVER_EXTENDED": "🔴"
        }.get(aff["status"], "❓")
        lines.append(
            f"**Affordability:** {aff_emoji} **{aff['status']}**"
        )
        lines.append(
            f"  Front ratio (housing/income): {aff['front_ratio']:.1f}% "
            f"(guideline: ≤28%)"
        )
        lines.append(
            f"  Back ratio (housing+debts/income): {aff['back_ratio']:.1f}% "
            f"(guideline: ≤36%)"
        )
        lines.append(f"  {aff['note']}")
        if aff.get("affordability_context"):
            lines.append(f"  📊 {aff['affordability_context']}")
        lines.append("")

        # ── Rate analysis ─────────────────────────────────────────────────
        traj_emoji = {
            "FALLING": "📉", "RISING": "📈", "STABLE": "➡️"
        }.get(ra["trajectory"], "➡️")
        lines.append(f"**Rate analysis:** {traj_emoji} {ra['trajectory']}")
        lines.append(
            f"  30yr: {ra['current_30yr']:.2f}% | "
            f"15yr: {ra['current_15yr']:.2f}% | "
            f"5/1 ARM: {ra['current_5_1_arm']:.2f}%"
        )
        lines.append(f"  Fed funds: {ra['fed_funds']:.2f}% ({ra['fed_direction']})")
        lines.append(f"  6-month projection: ~{ra['projected_6m']:.2f}%")
        lines.append(f"  {ra['rate_impact']['note']}")
        lines.append(f"  💡 {ra['recommendation']}")
        lines.append("")

        # ── ARM vs Fixed ──────────────────────────────────────────────────
        arm = plan["arm_vs_fixed"]
        if arm["monthly_savings"] > 0:
            lines.append("**ARM vs Fixed:**")
            lines.append(
                f"  Fixed ({arm['fixed_rate']:.2f}%): "
                f"{self.fmt_currency(arm['fixed_payment'])}/mo"
            )
            lines.append(
                f"  5/1 ARM ({arm['arm_rate']:.2f}%): "
                f"{self.fmt_currency(arm['arm_payment'])}/mo "
                f"(save {self.fmt_currency(arm['monthly_savings'])}/mo for 5yr)"
            )
            lines.append(
                f"  Worst-case yr 6 ({arm['worst_case_rate_yr6']:.2f}%): "
                f"{self.fmt_currency(arm['worst_case_payment'])}/mo "
                f"(+{self.fmt_currency(arm['worst_case_increase_vs_fixed'])}/mo vs fixed)"
            )
            lines.append(f"  💡 {arm['recommendation']}")
            lines.append("")

        # ── Rent vs Buy ───────────────────────────────────────────────────
        rvb = plan.get("rent_vs_buy")
        if rvb:
            lines.append("**Rent vs Buy:**")
            lines.append(
                f"  Current rent: {self.fmt_currency(rvb['current_rent'])}/mo | "
                f"Annual rent increase: {rvb['rent_annual_increase']} | "
                f"Home appreciation: {rvb['home_appreciation']}"
            )
            lines.append("")
            for horizon in [5, 10, 15]:
                comp = rvb["comparisons"].get(horizon)
                if comp:
                    w_emoji = "🏠" if comp["winner"] == "BUY" else "🏢"
                    lines.append(
                        f"  {horizon}yr: Rent {self.fmt_currency(comp['rent_total'])} "
                        f"vs Buy {self.fmt_currency(comp['buy_total'])} "
                        f"→ {w_emoji} **{comp['winner']}** saves "
                        f"{self.fmt_currency(abs(comp['difference']))}"
                    )
            lines.append(
                f"\n  ⏱️ Breakeven: **year {rvb['breakeven_years']}**"
                if rvb["breakeven_years"] < 99
                else "\n  ⏱️ Renting is cheaper at all horizons analysed."
            )
            lines.append(f"  💡 {rvb['recommendation']}")
            lines.append("")

        # ── Refinance ─────────────────────────────────────────────────────
        refi = plan.get("refinance")
        if refi and refi.get("applicable"):
            lines.append("**Refinance analysis:**")
            if refi.get("makes_sense"):
                lines.append(
                    f"  Old: {refi['current_rate']:.2f}% → "
                    f"{self.fmt_currency(refi['old_payment'])}/mo"
                )
                lines.append(
                    f"  New: {refi['new_rate']:.2f}% → "
                    f"{self.fmt_currency(refi['new_payment'])}/mo"
                )
                lines.append(
                    f"  Monthly savings: {self.fmt_currency(refi['monthly_savings'])}"
                )
                lines.append(
                    f"  Closing costs: {self.fmt_currency(refi['closing_costs'])} | "
                    f"Breakeven: {refi['breakeven_months']} months"
                )
                lines.append(
                    f"  Lifetime savings: {self.fmt_currency(refi['lifetime_savings'])}"
                )
                if refi.get("rate_trajectory_note"):
                    lines.append(f"  📉 {refi['rate_trajectory_note']}")
            else:
                lines.append(f"  {refi['note']}")
            lines.append("")

        # ── Total cost of ownership ───────────────────────────────────────
        tc = plan["total_ownership_cost"]
        lines.append(f"**Total cost over {inp['loan_term']} years:**")
        lines.append(
            f"  Principal + Interest: {self.fmt_currency(tc['total_principal_interest'])}"
        )
        lines.append(
            f"  Interest alone:       {self.fmt_currency(tc['total_interest_only'])}"
        )
        lines.append(
            f"  Property tax:         {self.fmt_currency(tc['total_property_tax'])}"
        )
        lines.append(
            f"  Insurance:            {self.fmt_currency(tc['total_insurance'])}"
        )
        lines.append(
            f"  Maintenance:          {self.fmt_currency(tc['total_maintenance'])}"
        )
        lines.append(
            f"  **Grand total:        {self.fmt_currency(tc['grand_total'])}**"
        )
        lines.append(f"  💡 {tc['interest_to_principal']}")
        lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: Freddie Mac, FRED, Case-Shiller, BLS"
        )

        return "\n".join(lines)
