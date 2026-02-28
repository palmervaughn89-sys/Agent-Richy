"""Retirement Planner — on-track assessment with specific actions
to close any gap, SS optimisation, and Vanguard benchmarks.

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
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

_TAX_YEAR = 2025

# ── 401(k) / IRA limits 2025 ─────────────────────────────────────────────
_401K_LIMIT = 23_500
_401K_CATCH_UP_50 = 7_500
_401K_CATCH_UP_60_63 = 11_250   # SECURE 2.0 super catch-up
_IRA_LIMIT = 7_000
_IRA_CATCH_UP_50 = 1_000
_ROTH_IRA_LIMIT = 7_000
_ROTH_CATCH_UP_50 = 1_000

# ── Life expectancy (SSA 2023 Period Life Table, rounded) ─────────────────
_LIFE_EXPECTANCY: dict[str, float] = {
    "male": 84.0,
    "female": 87.0,
    "average": 85.5,
}

# ── Social Security bend points 2025 & replacement rates ─────────────────
# PIA formula: 90% of first $1,174 AIME + 32% up to $7,078 + 15% above
_SS_BEND_1 = 1_174
_SS_BEND_2 = 7_078
_SS_RATES = (0.90, 0.32, 0.15)

# Age factors for claiming (FRA = 67)
_SS_FRA = 67
_SS_CLAIMING: dict[int, dict] = {
    62: {"factor": 0.70, "label": "Age 62 (30% reduction)"},
    63: {"factor": 0.75, "label": "Age 63 (25% reduction)"},
    64: {"factor": 0.80, "label": "Age 64 (20% reduction)"},
    65: {"factor": 0.867, "label": "Age 65 (13.3% reduction)"},
    66: {"factor": 0.933, "label": "Age 66 (6.7% reduction)"},
    67: {"factor": 1.00, "label": "Age 67 (full benefit)"},
    68: {"factor": 1.08, "label": "Age 68 (+8%)"},
    69: {"factor": 1.16, "label": "Age 69 (+16%)"},
    70: {"factor": 1.24, "label": "Age 70 (+24%)"},
}

# ── Vanguard "How America Saves" 2024 benchmarks ─────────────────────────
# Average & median 401(k) balance by age from Vanguard's report
_VANGUARD_BENCHMARKS: dict[str, dict[str, float]] = {
    "25-34": {"average": 37_557,  "median": 14_933},
    "35-44": {"average": 101_234, "median": 40_243},
    "45-54": {"average": 179_200, "median": 71_898},
    "55-64": {"average": 256_244, "median": 89_716},
    "65+":   {"average": 280_000, "median": 87_725},
}

# ── Historical average returns (nominal) by asset class ───────────────────
_RETURNS: dict[str, float] = {
    "stocks":  0.103,   # S&P 500 long-term average
    "bonds":   0.051,
    "cash":    0.033,
    "balanced": 0.077,  # 60/40
}

# ── Age-based allocation glide path (stock %) ────────────────────────────
def _stock_pct_for_age(age: int) -> float:
    """Target-date fund style glide path."""
    if age <= 30:
        return 0.90
    elif age <= 40:
        return 0.85
    elif age <= 50:
        return 0.75
    elif age <= 55:
        return 0.65
    elif age <= 60:
        return 0.55
    elif age <= 65:
        return 0.45
    else:
        return 0.35

def _blended_return(age: int) -> float:
    """Expected nominal return based on age-appropriate allocation."""
    s = _stock_pct_for_age(age)
    return s * _RETURNS["stocks"] + (1 - s) * _RETURNS["bonds"]

# ── Inflation assumption ─────────────────────────────────────────────────
def _inflation_rate() -> float:
    """Pull breakeven inflation from data layer or use 2.5% fallback."""
    t10yie = get_latest_indicator("T10YIE")
    return t10yie.get("value", 2.5) / 100


# ═══════════════════════════════════════════════════════════════════════════
# SOCIAL SECURITY ESTIMATOR
# ═══════════════════════════════════════════════════════════════════════════

def _estimate_ss_pia(annual_income: float, years_worked: int = 35) -> float:
    """Estimate Primary Insurance Amount (monthly) from income.

    Simplified: AIME ≈ top-35-year average monthly earnings.
    """
    # Cap at SS wage base for each year
    ss_wage_base = 176_100
    capped = min(annual_income, ss_wage_base)
    aime = capped / 12  # approximate AIME

    # PIA bend-point formula
    if aime <= _SS_BEND_1:
        pia = aime * _SS_RATES[0]
    elif aime <= _SS_BEND_2:
        pia = _SS_BEND_1 * _SS_RATES[0] + (aime - _SS_BEND_1) * _SS_RATES[1]
    else:
        pia = (
            _SS_BEND_1 * _SS_RATES[0]
            + (_SS_BEND_2 - _SS_BEND_1) * _SS_RATES[1]
            + (aime - _SS_BEND_2) * _SS_RATES[2]
        )
    return round(pia, 2)


def _ss_optimization(pia: float) -> dict:
    """Compare SS benefits at ages 62, 67, 70 with breakeven analysis."""
    results: dict[int, dict] = {}
    life_exp = _LIFE_EXPECTANCY["average"]

    for claim_age, info in _SS_CLAIMING.items():
        if claim_age not in (62, 67, 70):
            continue
        monthly = round(pia * info["factor"], 2)
        annual = monthly * 12
        years_collecting = max(life_exp - claim_age, 0)
        lifetime = round(annual * years_collecting, 2)
        results[claim_age] = {
            "claim_age": claim_age,
            "monthly": monthly,
            "annual": round(annual, 2),
            "years_collecting": round(years_collecting, 1),
            "lifetime_total": lifetime,
            "label": info["label"],
        }

    # Breakeven: 62 vs 67
    b62 = results[62]["annual"]
    b67 = results[67]["annual"]
    if b67 > b62:
        # Total received diverges: 67 catches up to 62 after N years
        head_start = b62 * 5  # 5 years of early benefits
        annual_diff = b67 - b62
        breakeven_67 = 67 + (head_start / annual_diff) if annual_diff > 0 else 99
    else:
        breakeven_67 = 99.0

    # Breakeven: 67 vs 70
    b70 = results[70]["annual"]
    if b70 > b67:
        head_start = b67 * 3
        annual_diff = b70 - b67
        breakeven_70 = 70 + (head_start / annual_diff) if annual_diff > 0 else 99
    else:
        breakeven_70 = 99.0

    # Recommendation
    if life_exp >= breakeven_70 + 2:
        rec = (
            "Wait until 70 if you can. With average life expectancy, "
            "the 24% bonus beats early claiming by "
            f"${results[70]['lifetime_total'] - results[62]['lifetime_total']:,.0f} "
            f"in lifetime benefits."
        )
    elif life_exp >= breakeven_67 + 2:
        rec = (
            "Claim at FRA (67) for the best balance of monthly income "
            "and lifetime value."
        )
    else:
        rec = "Consider claiming at 62 if you need the income or have health concerns."

    return {
        "at_62": results[62],
        "at_67": results[67],
        "at_70": results[70],
        "breakeven_62_vs_67": round(breakeven_67, 1),
        "breakeven_67_vs_70": round(breakeven_70, 1),
        "recommendation": rec,
    }


# ═══════════════════════════════════════════════════════════════════════════
# RETIREMENT PLANNER TOOL
# ═══════════════════════════════════════════════════════════════════════════

class RetirementPlanner(RichyToolBase):
    """On-track retirement assessment with gap-closing actions,
    SS optimisation, and Vanguard peer benchmarks.
    """

    tool_id = 15
    tool_name = "retirement_planner"
    description = (
        "Retirement on-track assessment, nest-egg projections, "
        "SS optimisation, and gap-closing strategies"
    )
    required_profile: list[str] = []

    # ── Router entry ──────────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.82),
            response=self._narrate(plan),
            data_used=[
                "income", "age", "savings", "contributions",
                "employer_match", "SS", "pension",
            ],
            accuracy_score=0.84,
            sources=[
                "IRS Rev Proc 2024-40 (contribution limits)",
                "SSA 2023 Period Life Table",
                "SSA PIA bend points (2025)",
                "Vanguard 'How America Saves' 2024",
                "S&P 500 historical returns",
                "FRED: T10YIE, SP500, DGS10",
            ],
            raw_data=plan,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════

    def analyze(self, user_profile: dict) -> dict:
        """Full retirement planning pipeline.

        Keys in ``user_profile``:
            current_age, target_retirement_age,
            savings: {401k, ira, roth, taxable, other},
            monthly_contributions: {401k, ira, roth},
            employer_match: {pct, max_pct},
            income, expected_ss (float monthly or "estimate"),
            pension (annual), desired_retirement_income (or "maintain"),
            state, gender (optional, for life expectancy)
        """
        # ── Extract inputs ────────────────────────────────────────────────
        age = int(user_profile.get("current_age", 35) or 35)
        retire_age = int(user_profile.get("target_retirement_age", 67) or 67)
        income = float(user_profile.get("income", 75_000) or 75_000)
        gender = (user_profile.get("gender", "average") or "average").lower()
        state = (user_profile.get("state", "") or "").upper()

        savings_raw = user_profile.get("savings", {}) or {}
        bal_401k = float(savings_raw.get("401k", 0) or 0)
        bal_ira = float(savings_raw.get("ira", 0) or 0)
        bal_roth = float(savings_raw.get("roth", 0) or 0)
        bal_taxable = float(savings_raw.get("taxable", 0) or 0)
        bal_other = float(savings_raw.get("other", 0) or 0)
        total_savings = bal_401k + bal_ira + bal_roth + bal_taxable + bal_other

        contribs_raw = user_profile.get("monthly_contributions", {}) or {}
        mc_401k = float(contribs_raw.get("401k", 0) or 0)
        mc_ira = float(contribs_raw.get("ira", 0) or 0)
        mc_roth = float(contribs_raw.get("roth", 0) or 0)
        monthly_total = mc_401k + mc_ira + mc_roth

        match_raw = user_profile.get("employer_match", {}) or {}
        match_pct = float(match_raw.get("pct", 0) or 0) / 100
        match_max_pct = float(match_raw.get("max_pct", 0) or 0) / 100

        pension_annual = float(user_profile.get("pension", 0) or 0)

        # SS
        expected_ss_raw = user_profile.get("expected_ss", "estimate")
        if isinstance(expected_ss_raw, (int, float)) and expected_ss_raw > 0:
            ss_pia = float(expected_ss_raw)
        else:
            ss_pia = _estimate_ss_pia(income)

        # Desired retirement income
        desired_raw = user_profile.get("desired_retirement_income", "maintain")
        if isinstance(desired_raw, (int, float)) and desired_raw > 0:
            desired_income = float(desired_raw)
        else:
            desired_income = income * 0.80  # 80% replacement

        inflation = _inflation_rate()
        years_to_retire = max(retire_age - age, 0)
        life_exp = _LIFE_EXPECTANCY.get(gender, _LIFE_EXPECTANCY["average"])
        years_in_retirement = max(life_exp - retire_age, 0)

        # ── 1. Income need (inflation-adjusted) ──────────────────────────
        inflation_factor = (1 + inflation) ** years_to_retire
        income_needed = desired_income * inflation_factor

        # ── 2. SS at FRA (monthly → annual) ──────────────────────────────
        ss_annual = ss_pia * 12 * inflation_factor  # rough COLA match

        # ── 3. Gap analysis ───────────────────────────────────────────────
        guaranteed_income = ss_annual + pension_annual * inflation_factor
        annual_gap = max(income_needed - guaranteed_income, 0)

        # ── 4. Nest egg target ────────────────────────────────────────────
        # Use CAPE-adjusted withdrawal rate
        cape_adj = self._cape_adjusted_wr()
        nest_egg_target = annual_gap / cape_adj if cape_adj > 0 else annual_gap * 25

        # ── 5. Project savings forward ────────────────────────────────────
        projections = self._project_savings(
            age=age,
            retire_age=retire_age,
            current_savings=total_savings,
            monthly_contrib=monthly_total,
            employer_match_annual=self._calc_match(
                mc_401k * 12, income, match_pct, match_max_pct,
            ),
        )
        projected_at_retirement = projections[-1]["savings"] if projections else total_savings

        # ── 6. On-track assessment ────────────────────────────────────────
        surplus_or_gap = projected_at_retirement - nest_egg_target
        if surplus_or_gap >= 0:
            status = "green"
            probability = min(0.95, 0.80 + (surplus_or_gap / nest_egg_target) * 0.15) if nest_egg_target > 0 else 0.95
        elif surplus_or_gap > -nest_egg_target * 0.20:
            status = "yellow"
            probability = 0.55 + (1 + surplus_or_gap / nest_egg_target) * 0.20 if nest_egg_target > 0 else 0.50
        else:
            status = "red"
            probability = max(0.10, 0.50 + (surplus_or_gap / nest_egg_target) * 0.40) if nest_egg_target > 0 else 0.10

        on_track = {
            "status": status,
            "projected_nest_egg": round(projected_at_retirement, 2),
            "target_nest_egg": round(nest_egg_target, 2),
            "surplus_or_gap": round(surplus_or_gap, 2),
            "probability": round(probability, 2),
        }

        # ── 7. Benchmarks ────────────────────────────────────────────────
        benchmarks = self._benchmark(age, total_savings)

        # ── 8. Recommendations ───────────────────────────────────────────
        recommendations = self._recommendations(
            age=age,
            retire_age=retire_age,
            income=income,
            mc_401k=mc_401k,
            mc_ira=mc_ira,
            mc_roth=mc_roth,
            bal_401k=bal_401k,
            match_pct=match_pct,
            match_max_pct=match_max_pct,
            surplus_or_gap=surplus_or_gap,
            nest_egg_target=nest_egg_target,
            inflation=inflation,
        )

        # ── 9. SS optimisation ───────────────────────────────────────────
        ss_opt = _ss_optimization(ss_pia)

        # ── Income sources at retirement ──────────────────────────────────
        savings_draw = round(projected_at_retirement * cape_adj, 2)
        total_retirement_income = ss_annual + pension_annual * inflation_factor + savings_draw
        income_gap = max(income_needed - total_retirement_income, 0)

        income_sources = {
            "social_security": round(ss_annual, 2),
            "pension": round(pension_annual * inflation_factor, 2),
            "savings_draw": savings_draw,
            "total": round(total_retirement_income, 2),
            "needed": round(income_needed, 2),
            "gap": round(income_gap, 2),
            "withdrawal_rate": round(cape_adj * 100, 2),
        }

        # ── Target summary ───────────────────────────────────────────────
        target = {
            "income_needed": round(income_needed, 2),
            "nest_egg_target": round(nest_egg_target, 2),
            "withdrawal_rate": f"{cape_adj * 100:.1f}%",
            "inflation_assumption": f"{inflation * 100:.1f}%",
            "years_to_retire": years_to_retire,
            "years_in_retirement": round(years_in_retirement, 1),
            "life_expectancy": life_exp,
        }

        # ── Confidence ────────────────────────────────────────────────────
        filled = sum(1 for v in [
            income, age, total_savings, monthly_total, pension_annual,
        ] if v)
        confidence = min(0.70 + filled * 0.04, 0.92)

        return {
            "target": target,
            "income_sources": income_sources,
            "on_track": on_track,
            "benchmarks": benchmarks,
            "recommendations": recommendations,
            "projections": projections,
            "ss_optimization": ss_opt,
            "confidence": round(confidence, 2),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    # ── CAPE-adjusted withdrawal rate ─────────────────────────────────────

    @staticmethod
    def _cape_adjusted_wr() -> float:
        """Adjust the 4% rule based on current CAPE.

        CAPE > 30 → lower WR (3.3%), CAPE < 20 → higher WR (4.5%).
        """
        # Manual CAPE (no FRED series available)
        cape = 34.5  # as of Feb 2026
        if cape > 30:
            return 0.033
        elif cape > 25:
            return 0.035
        elif cape > 20:
            return 0.040
        else:
            return 0.045

    # ── Employer match calculation ────────────────────────────────────────

    @staticmethod
    def _calc_match(
        annual_401k: float,
        income: float,
        match_pct: float,
        match_max_pct: float,
    ) -> float:
        """Calculate annual employer match."""
        if match_pct <= 0 or match_max_pct <= 0:
            return 0.0
        employee_pct = annual_401k / income if income > 0 else 0
        matched_pct = min(employee_pct, match_max_pct)
        return round(matched_pct * income * match_pct, 2)

    # ── Savings projection ────────────────────────────────────────────────

    @staticmethod
    def _project_savings(
        *,
        age: int,
        retire_age: int,
        current_savings: float,
        monthly_contrib: float,
        employer_match_annual: float,
    ) -> list[dict]:
        """Year-by-year projection to retirement."""
        projections: list[dict] = []
        balance = current_savings

        for yr_age in range(age, retire_age + 1):
            ret = _blended_return(yr_age)
            annual_contrib = monthly_contrib * 12
            annual_match = employer_match_annual
            growth = balance * ret
            balance += annual_contrib + annual_match + growth

            projections.append({
                "age": yr_age,
                "savings": round(balance, 2),
                "contributions": round(annual_contrib, 2),
                "employer_match": round(annual_match, 2),
                "growth": round(growth, 2),
                "return_rate": round(ret * 100, 1),
            })

        return projections

    # ── Benchmarks ────────────────────────────────────────────────────────

    @staticmethod
    def _benchmark(age: int, total_savings: float) -> dict:
        """Compare to Vanguard averages by age bracket."""
        if age < 35:
            bracket = "25-34"
        elif age < 45:
            bracket = "35-44"
        elif age < 55:
            bracket = "45-54"
        elif age < 65:
            bracket = "55-64"
        else:
            bracket = "65+"

        bench = _VANGUARD_BENCHMARKS[bracket]
        avg = bench["average"]
        med = bench["median"]

        # Estimate percentile (rough)
        if total_savings >= avg * 2:
            percentile = 90
        elif total_savings >= avg:
            percentile = 75
        elif total_savings >= med:
            percentile = 50 + int((total_savings - med) / max(avg - med, 1) * 25)
        elif total_savings >= med * 0.5:
            percentile = 25 + int((total_savings - med * 0.5) / max(med * 0.5, 1) * 25)
        else:
            percentile = max(5, int(total_savings / max(med * 0.5, 1) * 25))

        return {
            "age_bracket": bracket,
            "your_savings": round(total_savings, 2),
            "average": avg,
            "median": med,
            "estimated_percentile": min(percentile, 99),
            "source": "Vanguard 'How America Saves' 2024",
        }

    # ── Recommendations ───────────────────────────────────────────────────

    @staticmethod
    def _recommendations(
        *,
        age: int,
        retire_age: int,
        income: float,
        mc_401k: float,
        mc_ira: float,
        mc_roth: float,
        bal_401k: float,
        match_pct: float,
        match_max_pct: float,
        surplus_or_gap: float,
        nest_egg_target: float,
        inflation: float,
    ) -> list[dict]:
        """Generate prioritised gap-closing actions."""
        recs: list[dict] = []
        years_left = max(retire_age - age, 1)
        annual_401k = mc_401k * 12

        # ── 1. Capture full employer match ────────────────────────────────
        if match_pct > 0 and match_max_pct > 0:
            needed_for_match = match_max_pct * income
            if annual_401k < needed_for_match:
                extra = needed_for_match - annual_401k
                match_value = extra * match_pct
                recs.append({
                    "action": "Capture full employer match",
                    "impact": round(match_value, 2),
                    "impact_label": f"+${match_value:,.0f}/year free money",
                    "detail": (
                        f"Increase 401(k) contributions by ${extra:,.0f}/year "
                        f"(${extra / 12:,.0f}/mo) to capture the full "
                        f"{match_pct * 100:.0f}% match on {match_max_pct * 100:.0f}% "
                        f"of salary. That's ${match_value:,.0f}/year in free money."
                    ),
                    "priority": "critical",
                })

        # ── 2. Max out tax-advantaged accounts ────────────────────────────
        limit_401k = _401K_LIMIT
        if 60 <= age <= 63:
            limit_401k += _401K_CATCH_UP_60_63
        elif age >= 50:
            limit_401k += _401K_CATCH_UP_50

        gap_401k = limit_401k - annual_401k
        if gap_401k > 500:
            growth_est = gap_401k * years_left * 0.07  # rough compound
            recs.append({
                "action": "Max out 401(k)",
                "impact": round(gap_401k, 2),
                "impact_label": f"+${gap_401k:,.0f}/year → ~${growth_est:,.0f} at retirement",
                "detail": (
                    f"You have ${gap_401k:,.0f} of room in your 401(k) "
                    f"(limit: ${limit_401k:,.0f}). Maxing it adds "
                    f"~${growth_est:,.0f} to your nest egg over {years_left} years."
                ),
                "priority": "high",
            })

        limit_ira = _IRA_LIMIT + (_IRA_CATCH_UP_50 if age >= 50 else 0)
        annual_ira = mc_ira * 12
        gap_ira = limit_ira - annual_ira
        if gap_ira > 100:
            growth_est = gap_ira * years_left * 0.06
            recs.append({
                "action": "Max IRA contributions",
                "impact": round(gap_ira, 2),
                "impact_label": f"+${gap_ira:,.0f}/year",
                "detail": (
                    f"Contribute ${gap_ira:,.0f}/year to your IRA (Traditional "
                    f"or Roth depending on income). Over {years_left} years, "
                    f"that's ~${growth_est:,.0f} more."
                ),
                "priority": "high",
            })

        # ── 3. Increase savings rate 1%/year ──────────────────────────────
        current_rate = (mc_401k + mc_ira + mc_roth) * 12 / income * 100 if income > 0 else 0
        if current_rate < 15:
            target_rate = min(current_rate + 1, 15)
            extra_annual = income * 0.01
            cumulative = extra_annual * years_left * 1.5  # rough compound
            recs.append({
                "action": "Increase savings rate by 1%/year",
                "impact": round(extra_annual, 2),
                "impact_label": f"+${extra_annual:,.0f}/year (currently {current_rate:.1f}%)",
                "detail": (
                    f"Your savings rate is {current_rate:.1f}% — bump it 1% "
                    f"per year toward 15%. Just ${extra_annual / 12:,.0f}/mo more "
                    f"next year adds ~${cumulative:,.0f} by retirement."
                ),
                "priority": "medium",
            })

        # ── 4. Roth conversions (if in low bracket now) ───────────────────
        if income < 90_000 and bal_401k > 50_000:
            recs.append({
                "action": "Consider Roth conversions",
                "impact": 0,
                "impact_label": "Tax diversification",
                "detail": (
                    f"Your income ({f'${income:,.0f}'}) may be lower now than "
                    f"in retirement. Converting some Traditional 401(k)/IRA "
                    f"to Roth at today's lower bracket saves future taxes. "
                    f"Convert enough to fill your current bracket without "
                    f"jumping to the next one."
                ),
                "priority": "medium",
            })

        # ── 5. Delay retirement (impact of each extra year) ───────────────
        if surplus_or_gap < 0:
            # Each extra year: one more year of growth + contributions + one less year of withdrawals
            monthly_total = mc_401k + mc_ira + mc_roth
            extra_year_value = round(
                monthly_total * 12  # contributions
                + nest_egg_target * 0.07  # growth on target
                + nest_egg_target * 0.033,  # one less year of withdrawal
                2,
            )
            years_needed = math.ceil(abs(surplus_or_gap) / extra_year_value) if extra_year_value > 0 else 5
            recs.append({
                "action": f"Delay retirement by {min(years_needed, 5)} year(s)",
                "impact": round(extra_year_value * min(years_needed, 5), 2),
                "impact_label": f"Each year adds ~${extra_year_value:,.0f}",
                "detail": (
                    f"Each year you delay: +${monthly_total * 12:,.0f} contributions, "
                    f"+~${nest_egg_target * 0.07:,.0f} growth, and one fewer year "
                    f"of withdrawals. {min(years_needed, 5)} extra year(s) could "
                    f"close your gap."
                ),
                "priority": "low" if years_needed <= 2 else "medium",
            })

        # ── 6. HSA as stealth retirement account ──────────────────────────
        if age < 65:
            recs.append({
                "action": "Max HSA (stealth retirement account)",
                "impact": 4_300 if age < 55 else 5_300,
                "impact_label": f"+${4_300 if age < 55 else 5_300:,}/year triple-tax-free",
                "detail": (
                    "HSA contributions are tax-deductible, grow tax-free, "
                    "and withdraw tax-free for medical expenses. After 65, "
                    "it works like a Traditional IRA for any purpose. "
                    "Invest it, don't spend it."
                ),
                "priority": "medium",
            })

        return recs

    # ═══════════════════════════════════════════════════════════════════════
    # NARRATION
    # ═══════════════════════════════════════════════════════════════════════

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []

        # ── Header ────────────────────────────────────────────────────────
        ot = plan["on_track"]
        emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(ot["status"], "⚪")
        lines.append(
            f"🏦 **Retirement Planner** — {emoji} **{ot['status'].upper()}**"
        )
        lines.append("")

        # ── Target ────────────────────────────────────────────────────────
        t = plan["target"]
        lines.append("**Your retirement target:**")
        lines.append(f"  Income needed (inflation-adj): {self.fmt_currency(t['income_needed'])}/year")
        lines.append(f"  Nest egg target:               {self.fmt_currency(t['nest_egg_target'])}")
        lines.append(f"  Withdrawal rate:               {t['withdrawal_rate']} (CAPE-adjusted)")
        lines.append(f"  Years to retire:               {t['years_to_retire']}")
        lines.append(f"  Retirement duration:           ~{t['years_in_retirement']:.0f} years (to age {t['life_expectancy']:.0f})")
        lines.append("")

        # ── On-track ─────────────────────────────────────────────────────
        lines.append("**On-track assessment:**")
        lines.append(f"  Projected nest egg: {self.fmt_currency(ot['projected_nest_egg'])}")
        lines.append(f"  Target:             {self.fmt_currency(ot['target_nest_egg'])}")
        if ot["surplus_or_gap"] >= 0:
            lines.append(f"  ✅ Surplus:          {self.fmt_currency(ot['surplus_or_gap'])}")
        else:
            lines.append(f"  ⚠️ Gap:              ({self.fmt_currency(abs(ot['surplus_or_gap']))})")
        lines.append(f"  Success probability: ~{ot['probability']:.0%}")
        lines.append("")

        # ── Income sources at retirement ──────────────────────────────────
        inc = plan["income_sources"]
        lines.append("**Retirement income sources:**")
        lines.append(f"  Social Security:   {self.fmt_currency(inc['social_security'])}/year")
        if inc["pension"] > 0:
            lines.append(f"  Pension:           {self.fmt_currency(inc['pension'])}/year")
        lines.append(f"  Savings draw ({inc['withdrawal_rate']}%): {self.fmt_currency(inc['savings_draw'])}/year")
        lines.append(f"  **Total:           {self.fmt_currency(inc['total'])}/year**")
        if inc["gap"] > 0:
            lines.append(f"  Gap:               ({self.fmt_currency(inc['gap'])})/year")
        lines.append("")

        # ── Benchmarks ────────────────────────────────────────────────────
        b = plan["benchmarks"]
        lines.append(f"**Peer comparison ({b['age_bracket']} age group):**")
        lines.append(f"  Your savings:  {self.fmt_currency(b['your_savings'])}")
        lines.append(f"  Average:       {self.fmt_currency(b['average'])}")
        lines.append(f"  Median:        {self.fmt_currency(b['median'])}")
        pct = b["estimated_percentile"]
        pct_emoji = "🏆" if pct >= 75 else "👍" if pct >= 50 else "📈"
        lines.append(f"  {pct_emoji} You're at roughly the {pct}th percentile")
        lines.append("")

        # ── SS optimisation ───────────────────────────────────────────────
        ss = plan["ss_optimization"]
        lines.append("**Social Security claiming strategy:**")
        for key in ("at_62", "at_67", "at_70"):
            info = ss[key]
            lines.append(
                f"  {info['label']}: {self.fmt_currency(info['monthly'])}/mo "
                f"({self.fmt_currency(info['annual'])}/yr, "
                f"lifetime ~{self.fmt_currency(info['lifetime_total'])})"
            )
        lines.append(f"  Breakeven 62→67: age {ss['breakeven_62_vs_67']:.0f}")
        lines.append(f"  Breakeven 67→70: age {ss['breakeven_67_vs_70']:.0f}")
        lines.append(f"  💡 {ss['recommendation']}")
        lines.append("")

        # ── Recommendations ───────────────────────────────────────────────
        recs = plan.get("recommendations", [])
        if recs:
            lines.append("**🔧 Actions to strengthen your plan:**")
            for i, r in enumerate(recs, 1):
                pri = {
                    "critical": "🔴", "high": "🟠",
                    "medium": "🟡", "low": "⚪",
                }.get(r.get("priority", "low"), "⚪")
                lines.append(f"  {pri} {i}. **{r['action']}** ({r['impact_label']})")
                lines.append(f"     {r['detail']}")
                lines.append("")

        # ── Projection milestones ─────────────────────────────────────────
        proj = plan.get("projections", [])
        if proj and len(proj) > 5:
            lines.append("**Projection milestones:**")
            # Show every 5 years + last
            milestone_ages = set()
            for p in proj:
                if p["age"] % 5 == 0 or p["age"] == proj[-1]["age"]:
                    milestone_ages.add(p["age"])
            for p in proj:
                if p["age"] in milestone_ages:
                    lines.append(
                        f"  Age {p['age']:>3d}: {self.fmt_currency(p['savings']):>14s}  "
                        f"(+{self.fmt_currency(p['contributions'])} contrib, "
                        f"+{self.fmt_currency(p['growth'])} growth)"
                    )
            lines.append("")

        # ── Confidence ────────────────────────────────────────────────────
        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: IRS limits, SSA tables, Vanguard benchmarks, "
            f"FRED indicators"
        )

        return "\n".join(lines)
