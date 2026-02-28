"""Insurance Guide — tells users if they're over/under-insured
with benchmark data across health, auto, life, renters, disability,
and homeowners.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Optional

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# BENCHMARK DATA
# ═══════════════════════════════════════════════════════════════════════════

# ── Health (KFF Employer Health Benefits Survey 2024 + ACA) ──────────────
_KFF_ANNUAL_PREMIUMS: dict[str, dict[str, float]] = {
    "single": {
        "employer_total": 8_951,
        "employee_share": 1_401,
        "aca_benchmark":  6_300,    # ACA silver benchmark (unsubsidized)
    },
    "family": {
        "employer_total": 25_572,
        "employee_share": 6_575,
        "aca_benchmark":  17_640,
    },
}

# HSA limits 2025
_HSA_LIMITS = {
    "single": 4_300,
    "family": 8_550,
    "catch_up_55": 1_000,
}

# HDHP minimums 2025
_HDHP_MIN_DEDUCTIBLE = {"single": 1_650, "family": 3_300}
_HDHP_MAX_OOP = {"single": 8_300, "family": 16_600}

# ── Auto Insurance (NAIC / III state averages, annual) ───────────────────
_AUTO_STATE_AVG: dict[str, float] = {
    "AL": 1_780, "AK": 1_420, "AZ": 1_760, "AR": 1_530, "CA": 2_020,
    "CO": 2_020, "CT": 1_850, "DE": 1_810, "FL": 2_560, "GA": 1_960,
    "HI": 1_260, "ID": 1_250, "IL": 1_530, "IN": 1_350, "IA": 1_110,
    "KS": 1_370, "KY": 1_910, "LA": 2_720, "ME": 1_080, "MD": 1_790,
    "MA": 1_360, "MI": 2_610, "MN": 1_420, "MS": 1_720, "MO": 1_520,
    "MT": 1_560, "NE": 1_350, "NV": 2_060, "NH": 1_190, "NJ": 1_760,
    "NM": 1_560, "NY": 2_320, "NC": 1_300, "ND": 1_200, "OH": 1_210,
    "OK": 1_820, "OR": 1_530, "PA": 1_530, "RI": 1_760, "SC": 1_640,
    "SD": 1_310, "TN": 1_510, "TX": 1_840, "UT": 1_430, "VT": 1_120,
    "VA": 1_350, "WA": 1_510, "WV": 1_510, "WI": 1_120, "WY": 1_420,
    "DC": 1_720,
}
_AUTO_NATIONAL_AVG = 1_630

# ── Homeowners (III 2024 avg) ────────────────────────────────────────────
_HOMEOWNERS_NATIONAL_AVG = 2_377  # annual
_HOMEOWNERS_RULE = 0.005  # ~0.5% of home value per year

# ── Renters (III 2024 avg) ───────────────────────────────────────────────
_RENTERS_NATIONAL_AVG = 180       # annual (~$15/mo)
_RENTERS_TYPICAL_COVERAGE = 30_000

# ── Term Life by age (annual per $500K, healthy non-smoker, 20yr term) ───
_TERM_LIFE_500K: dict[str, float] = {
    "25": 230, "30": 250, "35": 270, "40": 340, "45": 520,
    "50": 830, "55": 1_400, "60": 2_400, "65": 4_200,
}

# ── Disability Statistics (CDA / SSA) ────────────────────────────────────
_DISABILITY_CHANCE_90DAY = {
    25: 0.24, 30: 0.24, 35: 0.23, 40: 0.21, 45: 0.19,
    50: 0.18, 55: 0.17, 60: 0.15,
}  # probability of a 90+ day disability before 65

_LTD_REPLACEMENT_TARGET = 0.60  # 60% of gross income

# ── Medicare (2025 Part B standard) ──────────────────────────────────────
_MEDICARE_PART_B = 185.00  # monthly
_MEDICARE_PART_D_AVG = 55.50
_MEDIGAP_AVG = 175.00

# ── Umbrella ─────────────────────────────────────────────────────────────
_UMBRELLA_1M_AVG = 380  # annual for $1M policy


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _bracket_age(age: int) -> str:
    """Round age to nearest 5 for term life table lookups."""
    rounded = max(25, min(65, 5 * round(age / 5)))
    return str(rounded)


def _state_auto_avg(state: str) -> float:
    """Return state auto insurance average (annual)."""
    return _AUTO_STATE_AVG.get(state.upper(), _AUTO_NATIONAL_AVG)


def _disability_risk(age: int) -> float:
    """Probability of a 90+-day disability before 65."""
    # Find nearest key
    keys = sorted(_DISABILITY_CHANCE_90DAY.keys())
    nearest = min(keys, key=lambda k: abs(k - age))
    return _DISABILITY_CHANCE_90DAY[nearest]


def _life_need(
    income: float,
    age: int,
    youngest_child_age: int | None,
    mortgage_balance: float,
    other_debts: float,
    college_fund_target: float,
    existing_savings: float,
) -> dict:
    """Calculate life insurance need via income-replacement method.

    Need = income * years_to_18(youngest) + mortgage + debts
         + college - savings
    """
    if youngest_child_age is not None:
        years_support = max(0, 18 - youngest_child_age)
    else:
        years_support = 10  # default: 10 years income replacement

    income_replacement = income * years_support
    total_need = (
        income_replacement
        + mortgage_balance
        + other_debts
        + college_fund_target
        - existing_savings
    )
    total_need = max(0, total_need)

    return {
        "income_replacement": round(income_replacement, 2),
        "years_support": years_support,
        "mortgage_balance": round(mortgage_balance, 2),
        "other_debts": round(other_debts, 2),
        "college_target": round(college_fund_target, 2),
        "less_savings": round(existing_savings, 2),
        "total_need": round(total_need, 2),
    }


# ═══════════════════════════════════════════════════════════════════════════
# PER-TYPE ASSESSMENTS
# ═══════════════════════════════════════════════════════════════════════════

def _assess_health(
    policy: dict | None,
    household_size: int,
    age: int,
    income: float,
) -> dict:
    """Assess health insurance coverage vs KFF benchmarks."""
    tier = "family" if household_size > 1 else "single"
    benchmarks = _KFF_ANNUAL_PREMIUMS[tier]
    benchmark_premium = benchmarks["employee_share"]

    result: dict[str, Any] = {
        "type": "health",
        "has_coverage": policy is not None,
        "benchmark_annual": benchmark_premium,
        "benchmark_tier": tier,
    }

    if policy is None:
        result["status"] = "CRITICAL_GAP"
        result["severity"] = "critical"
        result["message"] = (
            "No health insurance. Medical debt is the #1 cause of "
            "bankruptcy. Explore ACA marketplace or employer plans."
        )
        aca = benchmarks["aca_benchmark"]
        # ACA subsidy estimate
        fpl_400 = 62_400 if household_size <= 1 else 62_400 + (household_size - 1) * 18_000
        subsidy_eligible = income < fpl_400
        result["aca_benchmark"] = aca
        result["subsidy_eligible"] = subsidy_eligible
        if subsidy_eligible:
            result["message"] += (
                f" You may qualify for ACA subsidies (income under "
                f"${fpl_400:,.0f} for household of {household_size})."
            )
        result["action"] = "Enroll in health insurance immediately."
        return result

    premium_annual = float(policy.get("premium_annual", 0) or 0)
    if premium_annual == 0:
        premium_monthly = float(policy.get("premium_monthly", 0) or 0)
        premium_annual = premium_monthly * 12

    deductible = float(policy.get("deductible", 0) or 0)
    plan_type = (policy.get("plan_type", "") or "").upper()

    delta_pct = ((premium_annual - benchmark_premium) / max(benchmark_premium, 1)) * 100
    result["premium_annual"] = round(premium_annual, 2)
    result["delta_pct"] = round(delta_pct, 1)

    if delta_pct > 30:
        result["status"] = "OVER_INSURED"
        result["severity"] = "moderate"
        result["message"] = (
            f"Paying ${premium_annual:,.0f}/yr — {delta_pct:.0f}% above the "
            f"${benchmark_premium:,.0f} benchmark. Consider HDHP + HSA, "
            f"marketplace shopping, or raising deductible."
        )
    elif delta_pct < -20:
        result["status"] = "UNDER_INSURED"
        result["severity"] = "moderate"
        result["message"] = (
            f"Paying ${premium_annual:,.0f}/yr — well below benchmark. "
            f"Verify your plan has adequate coverage (deductible, OOP max, "
            f"network breadth). Cheapest isn't always best."
        )
    else:
        result["status"] = "ADEQUATE"
        result["severity"] = "low"
        result["message"] = (
            f"Health premium of ${premium_annual:,.0f}/yr is within normal "
            f"range of the ${benchmark_premium:,.0f} benchmark."
        )

    # HSA eligibility
    is_hdhp = (
        plan_type in ("HDHP", "HSA")
        or deductible >= _HDHP_MIN_DEDUCTIBLE[tier]
    )
    result["hsa_eligible"] = is_hdhp
    if is_hdhp:
        limit = _HSA_LIMITS[tier]
        if age >= 55:
            limit += _HSA_LIMITS["catch_up_55"]
        result["hsa_limit"] = limit
        result["hsa_note"] = (
            f"Your HDHP qualifies for an HSA — up to ${limit:,}/yr, "
            f"triple tax-advantaged (deductible, grows tax-free, "
            f"tax-free medical withdrawals)."
        )
    elif premium_annual > benchmark_premium * 1.1:
        result["hsa_suggestion"] = (
            "Switching to an HDHP could save on premiums AND unlock "
            f"an HSA (${_HSA_LIMITS[tier]:,}/yr tax advantage)."
        )

    return result


def _assess_auto(
    policy: dict | None,
    state: str,
    car_value: float,
    car_age: int,
) -> dict:
    """Assess auto insurance vs state averages."""
    state_avg = _state_auto_avg(state)

    result: dict[str, Any] = {
        "type": "auto",
        "has_coverage": policy is not None,
        "state_avg_annual": state_avg,
        "state": state.upper(),
    }

    if policy is None:
        result["status"] = "NO_POLICY"
        result["severity"] = "info"
        result["message"] = "No auto insurance on file. Skip if you don't own a car."
        return result

    premium_annual = float(policy.get("premium_annual", 0) or 0)
    if premium_annual == 0:
        premium_monthly = float(policy.get("premium_monthly", 0) or 0)
        premium_annual = premium_monthly * 12

    deductible = float(policy.get("deductible", 500) or 500)
    has_collision = policy.get("has_collision", True)

    delta_pct = ((premium_annual - state_avg) / max(state_avg, 1)) * 100
    result["premium_annual"] = round(premium_annual, 2)
    result["delta_pct"] = round(delta_pct, 1)

    savings_tips: list[str] = []
    potential_savings = 0.0

    if delta_pct > 20:
        result["status"] = "OVER_INSURED"
        result["severity"] = "moderate"
        result["message"] = (
            f"Paying ${premium_annual:,.0f}/yr — {delta_pct:.0f}% above the "
            f"{state.upper()} average of ${state_avg:,.0f}."
        )
        # Tips
        if deductible < 1_000:
            save_est = premium_annual * 0.10
            savings_tips.append(
                f"Raise deductible to $1,000 → save ~${save_est:,.0f}/yr"
            )
            potential_savings += save_est
        savings_tips.append(
            "Bundle auto + home/renters → typical 5-15% discount"
        )
        potential_savings += premium_annual * 0.08
        savings_tips.append("Shop annually — loyalty doesn't mean best price")
    elif delta_pct < -15:
        result["status"] = "UNDER_INSURED"
        result["severity"] = "moderate"
        result["message"] = (
            f"Paying ${premium_annual:,.0f}/yr — below the {state.upper()} "
            f"average. Verify liability limits are at least 100/300/100."
        )
    else:
        result["status"] = "ADEQUATE"
        result["severity"] = "low"
        result["message"] = (
            f"Auto premium of ${premium_annual:,.0f}/yr is close to the "
            f"{state.upper()} average of ${state_avg:,.0f}."
        )

    # Old car: drop collision?
    if car_age >= 10 and has_collision and car_value < 8_000:
        collision_save = premium_annual * 0.25
        savings_tips.append(
            f"Car is {car_age} years old (value ~${car_value:,.0f}). "
            f"Drop collision/comprehensive → save ~${collision_save:,.0f}/yr"
        )
        potential_savings += collision_save

    result["savings_tips"] = savings_tips
    result["potential_savings"] = round(potential_savings, 2)
    return result


def _assess_life(
    policy: dict | None,
    age: int,
    income: float,
    youngest_child_age: int | None,
    mortgage_balance: float,
    other_debts: float,
    college_target: float,
    savings: float,
) -> dict:
    """Assess life insurance need vs current coverage."""
    need = _life_need(
        income, age, youngest_child_age,
        mortgage_balance, other_debts, college_target, savings,
    )

    bracket = _bracket_age(age)
    benchmark_500k = _TERM_LIFE_500K.get(bracket, 500)

    result: dict[str, Any] = {
        "type": "life",
        "has_coverage": policy is not None,
        "calculated_need": need,
        "benchmark_500k_annual": benchmark_500k,
        "age_bracket": bracket,
    }

    if policy is None:
        if need["total_need"] > 0:
            result["status"] = "CRITICAL_GAP"
            result["severity"] = "critical"
            # Estimate premium for the needed amount
            ratio = need["total_need"] / 500_000
            est_premium = round(benchmark_500k * ratio, 0)
            result["message"] = (
                f"No life insurance. Your calculated need is "
                f"${need['total_need']:,.0f}. A 20-year term policy for "
                f"that amount would cost ~${est_premium:,.0f}/yr at age {age}."
            )
            result["estimated_premium"] = est_premium
            result["action"] = (
                "Get quotes for term life insurance immediately. "
                "Term is 5-10x cheaper than whole life for the same coverage."
            )
        else:
            result["status"] = "NOT_NEEDED"
            result["severity"] = "info"
            result["message"] = (
                "No dependents relying on your income and no major debts. "
                "Life insurance may not be necessary right now."
            )
        return result

    coverage = float(policy.get("coverage_amount", 0) or 0)
    premium_annual = float(policy.get("premium_annual", 0) or 0)
    if premium_annual == 0:
        premium_monthly = float(policy.get("premium_monthly", 0) or 0)
        premium_annual = premium_monthly * 12
    policy_type = (policy.get("policy_type", "term") or "term").lower()

    gap = need["total_need"] - coverage
    result["current_coverage"] = coverage
    result["premium_annual"] = round(premium_annual, 2)
    result["policy_type"] = policy_type
    result["gap"] = round(gap, 2)

    if gap > 50_000:
        result["status"] = "UNDER_INSURED"
        result["severity"] = "high"
        result["message"] = (
            f"Coverage gap of ${gap:,.0f}. You have ${coverage:,.0f} "
            f"but need ${need['total_need']:,.0f}. Consider additional "
            f"term coverage."
        )
    elif gap < -200_000:
        result["status"] = "OVER_INSURED"
        result["severity"] = "moderate"
        excess = abs(gap)
        result["message"] = (
            f"You may be over-insured by ~${excess:,.0f}. "
            f"Coverage: ${coverage:,.0f} vs need: ${need['total_need']:,.0f}. "
            f"Consider reducing to save on premiums."
        )
    else:
        result["status"] = "ADEQUATE"
        result["severity"] = "low"
        result["message"] = (
            f"Life coverage of ${coverage:,.0f} is well-aligned with "
            f"your calculated need of ${need['total_need']:,.0f}."
        )

    # Term vs whole analysis
    if policy_type == "whole":
        term_equiv = benchmark_500k * (coverage / 500_000)
        savings_if_switch = max(0, premium_annual - term_equiv)
        result["term_vs_whole"] = {
            "current_whole_premium": round(premium_annual, 2),
            "equivalent_term_premium": round(term_equiv, 2),
            "annual_savings": round(savings_if_switch, 2),
            "recommendation": (
                f"Whole life costs ${premium_annual:,.0f}/yr. Equivalent "
                f"term coverage: ~${term_equiv:,.0f}/yr → save "
                f"${savings_if_switch:,.0f}/yr. Invest the difference "
                f"in index funds for better returns."
            ) if savings_if_switch > 200 else (
                "Your whole life premium is reasonable relative to "
                "equivalent term. Keep if you value the cash-value component."
            ),
        }

    return result


def _assess_renters(policy: dict | None, is_renter: bool) -> dict:
    """Assess renters insurance."""
    result: dict[str, Any] = {
        "type": "renters",
        "has_coverage": policy is not None,
        "benchmark_annual": _RENTERS_NATIONAL_AVG,
    }

    if not is_renter:
        result["status"] = "NOT_APPLICABLE"
        result["severity"] = "info"
        result["message"] = "Not a renter — homeowners insurance applies instead."
        return result

    if policy is None:
        result["status"] = "CRITICAL_GAP"
        result["severity"] = "high"
        result["message"] = (
            f"No renters insurance! Only ~${_RENTERS_NATIONAL_AVG / 12:.0f}/mo "
            f"(${_RENTERS_NATIONAL_AVG}/yr) for ~${_RENTERS_TYPICAL_COVERAGE:,} "
            f"in personal property coverage + liability protection. "
            f"Your landlord's policy does NOT cover your belongings."
        )
        result["action"] = (
            "Get renters insurance today — Lemonade, State Farm, "
            "or your auto insurer (bundle discount)."
        )
        return result

    premium_annual = float(policy.get("premium_annual", 0) or 0)
    if premium_annual == 0:
        premium_monthly = float(policy.get("premium_monthly", 0) or 0)
        premium_annual = premium_monthly * 12

    coverage = float(policy.get("coverage_amount", _RENTERS_TYPICAL_COVERAGE) or _RENTERS_TYPICAL_COVERAGE)

    result["premium_annual"] = round(premium_annual, 2)
    result["coverage"] = coverage
    result["status"] = "ADEQUATE"
    result["severity"] = "low"
    result["message"] = (
        f"Renters insurance at ${premium_annual:,.0f}/yr for "
        f"${coverage:,.0f} coverage. ✓"
    )

    if coverage < 20_000:
        result["status"] = "UNDER_INSURED"
        result["severity"] = "moderate"
        result["message"] += (
            f" Coverage of ${coverage:,.0f} may be low — do a quick "
            f"home inventory to verify."
        )

    return result


def _assess_homeowners(
    policy: dict | None,
    is_homeowner: bool,
    home_value: float,
) -> dict:
    """Assess homeowners insurance."""
    result: dict[str, Any] = {
        "type": "homeowners",
        "has_coverage": policy is not None,
        "benchmark_annual": _HOMEOWNERS_NATIONAL_AVG,
    }

    if not is_homeowner:
        result["status"] = "NOT_APPLICABLE"
        result["severity"] = "info"
        result["message"] = "Not a homeowner — renters insurance applies instead."
        return result

    expected_premium = max(
        home_value * _HOMEOWNERS_RULE,
        _HOMEOWNERS_NATIONAL_AVG * 0.6,
    )

    if policy is None:
        result["status"] = "CRITICAL_GAP"
        result["severity"] = "critical"
        result["message"] = (
            "No homeowners insurance on a property! This is extremely risky. "
            "If you have a mortgage, your lender will force-place expensive "
            "coverage. Average cost: ~${:,.0f}/yr.".format(expected_premium)
        )
        result["action"] = "Get homeowners insurance quotes immediately."
        return result

    premium_annual = float(policy.get("premium_annual", 0) or 0)
    if premium_annual == 0:
        premium_monthly = float(policy.get("premium_monthly", 0) or 0)
        premium_annual = premium_monthly * 12

    coverage = float(policy.get("coverage_amount", home_value) or home_value)
    result["premium_annual"] = round(premium_annual, 2)
    result["coverage"] = coverage

    delta_pct = ((premium_annual - expected_premium) / max(expected_premium, 1)) * 100

    if delta_pct > 30:
        result["status"] = "OVER_INSURED"
        result["severity"] = "moderate"
        result["message"] = (
            f"Paying ${premium_annual:,.0f}/yr — {delta_pct:.0f}% above "
            f"expected (~${expected_premium:,.0f}). Raise deductible to "
            f"$2,500, bundle with auto, or shop around."
        )
        result["potential_savings"] = round(premium_annual - expected_premium, 2)
    elif coverage < home_value * 0.80:
        result["status"] = "UNDER_INSURED"
        result["severity"] = "high"
        result["message"] = (
            f"Coverage of ${coverage:,.0f} is under 80% of home value "
            f"(${home_value:,.0f}). In a total loss, your claim may be "
            f"reduced proportionally. Increase to at least "
            f"${home_value * 0.80:,.0f}."
        )
    else:
        result["status"] = "ADEQUATE"
        result["severity"] = "low"
        result["message"] = (
            f"Homeowners coverage at ${premium_annual:,.0f}/yr for "
            f"${coverage:,.0f} looks reasonable for a ${home_value:,.0f} home."
        )

    return result


def _assess_disability(
    policy: dict | None,
    age: int,
    income: float,
) -> dict:
    """Assess disability insurance (long-term)."""
    risk = _disability_risk(age)
    target_monthly = round(income / 12 * _LTD_REPLACEMENT_TARGET, 2)

    result: dict[str, Any] = {
        "type": "disability",
        "has_coverage": policy is not None,
        "disability_risk_before_65": f"{risk * 100:.0f}%",
        "target_monthly_benefit": target_monthly,
    }

    if policy is None:
        result["status"] = "CRITICAL_GAP"
        result["severity"] = "high"
        result["message"] = (
            f"No disability insurance. There's a {risk * 100:.0f}% chance "
            f"of a 90+ day disability before age 65. Your income IS your "
            f"greatest asset. Target: ${target_monthly:,.0f}/mo benefit "
            f"(60% of income)."
        )
        # Estimate cost: ~1-3% of income
        est_premium = round(income * 0.02, 0)
        result["estimated_premium"] = est_premium
        result["action"] = (
            f"Check employer LTD first (often subsidized). "
            f"Individual policy: ~${est_premium:,.0f}/yr "
            f"(~{est_premium / income * 100:.1f}% of income)."
        )
        return result

    benefit_monthly = float(policy.get("benefit_monthly", 0) or 0)
    premium_annual = float(policy.get("premium_annual", 0) or 0)
    if premium_annual == 0:
        premium_monthly = float(policy.get("premium_monthly", 0) or 0)
        premium_annual = premium_monthly * 12

    result["benefit_monthly"] = benefit_monthly
    result["premium_annual"] = round(premium_annual, 2)
    replacement_pct = (benefit_monthly / max(income / 12, 1)) * 100

    if replacement_pct < 50:
        result["status"] = "UNDER_INSURED"
        result["severity"] = "moderate"
        result["message"] = (
            f"Disability benefit of ${benefit_monthly:,.0f}/mo replaces "
            f"only {replacement_pct:.0f}% of income. Target is 60%. "
            f"Consider supplemental coverage."
        )
    elif replacement_pct > 80:
        result["status"] = "OVER_INSURED"
        result["severity"] = "low"
        result["message"] = (
            f"Disability benefit of ${benefit_monthly:,.0f}/mo replaces "
            f"{replacement_pct:.0f}% of income — above the 60% target. "
            f"This is fine but verify you're not paying excessive premiums."
        )
    else:
        result["status"] = "ADEQUATE"
        result["severity"] = "low"
        result["message"] = (
            f"Disability coverage: ${benefit_monthly:,.0f}/mo "
            f"({replacement_pct:.0f}% replacement) at "
            f"${premium_annual:,.0f}/yr. ✓"
        )

    return result


# ═══════════════════════════════════════════════════════════════════════════
# INSURANCE GUIDE TOOL
# ═══════════════════════════════════════════════════════════════════════════

class InsuranceGuide(RichyToolBase):
    """Tells users if they're over/under-insured with benchmark data.

    Assesses health, auto, life, renters/homeowners, and disability
    coverage against industry benchmarks and personal need.
    """

    tool_id = 43
    tool_name = "insurance_guide"
    description = (
        "Insurance coverage assessment: health, auto, life, disability, "
        "renters/homeowners — benchmark comparison and gap analysis"
    )
    required_profile: list[str] = []

    # ── Execute ───────────────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan),
            data_used=[
                "age", "state", "income", "household_size",
                "insurance_policies", "home_value", "mortgage_balance",
            ],
            accuracy_score=0.85,
            sources=[
                "KFF Employer Health Benefits Survey 2024",
                "NAIC / III Auto Insurance by State 2024",
                "III Homeowners / Renters Insurance 2024",
                "CDA / SSA Disability Statistics",
                "ACA Marketplace Benchmarks 2025",
                "IRS HSA Limits 2025",
            ],
            raw_data=plan,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════

    def analyze(self, user_profile: dict) -> dict:
        """Run full insurance assessment.

        Expected keys in ``user_profile``:
            age:                int
            state:              str (2-letter)
            income:             float (annual gross)
            household_size:     int
            is_homeowner:       bool
            home_value:         float
            mortgage_balance:   float
            other_debts:        float
            savings:            float
            youngest_child_age: int | None
            college_target:     float (per child)
            car_value:          float
            car_age:            int (years)
            policies:           dict[str, dict]  — keyed by type:
                "health":      {premium_annual | premium_monthly, deductible, plan_type}
                "auto":        {premium_annual | premium_monthly, deductible, has_collision}
                "life":        {premium_annual | premium_monthly, coverage_amount, policy_type}
                "renters":     {premium_annual | premium_monthly, coverage_amount}
                "homeowners":  {premium_annual | premium_monthly, coverage_amount}
                "disability":  {premium_annual | premium_monthly, benefit_monthly}
        """
        age = int(user_profile.get("age", 35) or 35)
        state = str(user_profile.get("state", "TX") or "TX").upper()
        income = float(user_profile.get("income", 60_000) or 60_000)
        household_size = int(user_profile.get("household_size", 1) or 1)
        is_homeowner = bool(user_profile.get("is_homeowner", False))
        home_value = float(user_profile.get("home_value", 0) or 0)
        mortgage_balance = float(user_profile.get("mortgage_balance", 0) or 0)
        other_debts = float(user_profile.get("other_debts", 0) or 0)
        savings = float(user_profile.get("savings", 0) or 0)
        youngest_child_age = user_profile.get("youngest_child_age")
        if youngest_child_age is not None:
            youngest_child_age = int(youngest_child_age)
        college_target = float(user_profile.get("college_target", 0) or 0)
        car_value = float(user_profile.get("car_value", 0) or 0)
        car_age = int(user_profile.get("car_age", 0) or 0)

        policies: dict = user_profile.get("policies", {}) or {}

        # ── Run each assessment ──────────────────────────────────────────
        assessments: list[dict] = []

        # Health
        assessments.append(
            _assess_health(policies.get("health"), household_size, age, income)
        )

        # Auto
        assessments.append(
            _assess_auto(policies.get("auto"), state, car_value, car_age)
        )

        # Life
        assessments.append(
            _assess_life(
                policies.get("life"), age, income,
                youngest_child_age, mortgage_balance, other_debts,
                college_target, savings,
            )
        )

        # Renters or Homeowners
        if is_homeowner:
            assessments.append(
                _assess_homeowners(policies.get("homeowners"), True, home_value)
            )
            # Add renters as N/A
            assessments.append(
                _assess_renters(None, False)
            )
        else:
            assessments.append(
                _assess_renters(policies.get("renters"), True)
            )
            assessments.append(
                _assess_homeowners(None, False, 0)
            )

        # Disability
        assessments.append(
            _assess_disability(policies.get("disability"), age, income)
        )

        # ── Aggregate ────────────────────────────────────────────────────
        total_spend = 0.0
        potential_savings = 0.0
        action_items: list[dict] = []

        severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3, "info": 4}

        for a in assessments:
            if a.get("premium_annual"):
                total_spend += a["premium_annual"]
            if a.get("potential_savings"):
                potential_savings += a["potential_savings"]
            if a.get("estimated_premium"):
                # This is a suggested cost, not a savings
                pass
            # Collect action items for gaps
            if a.get("status") in ("CRITICAL_GAP", "UNDER_INSURED"):
                action_items.append({
                    "type": a["type"],
                    "severity": a.get("severity", "moderate"),
                    "action": a.get("action", a.get("message", "")),
                })
            elif a.get("status") == "OVER_INSURED" and a.get("savings_tips"):
                action_items.append({
                    "type": a["type"],
                    "severity": "moderate",
                    "action": "; ".join(a["savings_tips"]),
                })

        # Sort actions by severity
        action_items.sort(key=lambda x: severity_order.get(x["severity"], 5))

        pct_income = (total_spend / max(income, 1)) * 100
        target_range = (5.0, 10.0)

        if pct_income < target_range[0]:
            overall_status = "POSSIBLY_UNDER_INSURED"
            overall_msg = (
                f"Total insurance spend is {pct_income:.1f}% of income — "
                f"below the 5-10% target. Check for coverage gaps."
            )
        elif pct_income > target_range[1]:
            overall_status = "POSSIBLY_OVER_INSURED"
            overall_msg = (
                f"Total insurance spend is {pct_income:.1f}% of income — "
                f"above the 5-10% target. Look for savings opportunities."
            )
        else:
            overall_status = "WELL_BALANCED"
            overall_msg = (
                f"Total insurance spend is {pct_income:.1f}% of income — "
                f"within the 5-10% target range."
            )

        # ── Umbrella suggestion ──────────────────────────────────────────
        umbrella_suggestion = None
        if income > 100_000 or home_value > 300_000:
            umbrella_suggestion = {
                "recommended": True,
                "cost": _UMBRELLA_1M_AVG,
                "note": (
                    f"With income of ${income:,.0f} and/or assets, consider "
                    f"a $1M umbrella policy (~${_UMBRELLA_1M_AVG}/yr). "
                    f"Protects against lawsuits beyond auto/home limits."
                ),
            }

        # ── Confidence ───────────────────────────────────────────────────
        policies_provided = sum(
            1 for k in ["health", "auto", "life", "renters",
                        "homeowners", "disability"]
            if policies.get(k)
        )
        confidence = min(0.72 + policies_provided * 0.04 + 0.02, 0.92)

        return {
            "total_spend": round(total_spend, 2),
            "pct_income": round(pct_income, 1),
            "target_range": f"{target_range[0]:.0f}-{target_range[1]:.0f}%",
            "overall_status": overall_status,
            "overall_message": overall_msg,
            "assessments": assessments,
            "potential_savings": round(potential_savings, 2),
            "action_items": action_items,
            "umbrella": umbrella_suggestion,
            "confidence": round(confidence, 2),
            "age": age,
            "state": state,
            "income": income,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # NARRATION
    # ═══════════════════════════════════════════════════════════════════════

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []

        # ── Header ────────────────────────────────────────────────────────
        status_emoji = {
            "WELL_BALANCED": "✅",
            "POSSIBLY_UNDER_INSURED": "⚠️",
            "POSSIBLY_OVER_INSURED": "💰",
        }
        emoji = status_emoji.get(plan.get("overall_status", ""), "🛡️")
        lines.append(
            f"{emoji} **Insurance Guide** — Age {plan['age']} | "
            f"{plan['state']} | Income {self.fmt_currency(plan['income'])}"
        )
        lines.append("")

        # ── Overall ──────────────────────────────────────────────────────
        lines.append(
            f"**Total insurance spend:** "
            f"{self.fmt_currency(plan['total_spend'])}/yr "
            f"({plan['pct_income']:.1f}% of income, target {plan['target_range']})"
        )
        lines.append(f"  {plan['overall_message']}")
        lines.append("")

        # ── Per-type assessments ─────────────────────────────────────────
        type_emoji = {
            "health": "🏥", "auto": "🚗", "life": "💀",
            "renters": "🏠", "homeowners": "🏡", "disability": "♿",
        }

        for a in plan.get("assessments", []):
            t = a.get("type", "")
            if a.get("status") == "NOT_APPLICABLE":
                continue
            te = type_emoji.get(t, "📋")
            status = a.get("status", "UNKNOWN")

            status_fmt = {
                "ADEQUATE": "✅ Adequate",
                "OVER_INSURED": "💰 Over-insured",
                "UNDER_INSURED": "⚠️ Under-insured",
                "CRITICAL_GAP": "🚨 CRITICAL GAP",
                "NO_POLICY": "— No policy",
                "NOT_NEEDED": "ℹ️ Not needed",
            }

            lines.append(
                f"  {te} **{t.replace('_', ' ').title()}** "
                f"— {status_fmt.get(status, status)}"
            )
            lines.append(f"    {a['message']}")

            # HSA note
            if a.get("hsa_note"):
                lines.append(f"    💊 {a['hsa_note']}")
            elif a.get("hsa_suggestion"):
                lines.append(f"    💡 {a['hsa_suggestion']}")

            # Term vs whole
            if a.get("term_vs_whole"):
                tvw = a["term_vs_whole"]
                lines.append(f"    📊 {tvw['recommendation']}")

            # Savings tips
            if a.get("savings_tips"):
                for tip in a["savings_tips"]:
                    lines.append(f"    💡 {tip}")

            lines.append("")

        # ── Umbrella ─────────────────────────────────────────────────────
        umb = plan.get("umbrella")
        if umb and umb.get("recommended"):
            lines.append(f"  ☂️ **Umbrella Policy:** {umb['note']}")
            lines.append("")

        # ── Potential savings ─────────────────────────────────────────────
        if plan.get("potential_savings", 0) > 0:
            lines.append(
                f"**💰 Potential savings:** "
                f"{self.fmt_currency(plan['potential_savings'])}/yr"
            )
            lines.append("")

        # ── Action items ──────────────────────────────────────────────────
        actions = plan.get("action_items", [])
        if actions:
            lines.append(f"**🎯 Action items ({len(actions)}):**")
            severity_markers = {
                "critical": "🚨",
                "high": "⚠️",
                "moderate": "💡",
                "low": "ℹ️",
            }
            for i, act in enumerate(actions, 1):
                marker = severity_markers.get(act["severity"], "•")
                lines.append(
                    f"  {i}. {marker} [{act['type'].title()}] {act['action']}"
                )
            lines.append("")

        # ── Confidence ────────────────────────────────────────────────────
        lines.append(
            f"Confidence: {plan.get('confidence', 0.85):.0%} | "
            f"Sources: KFF, NAIC/III, CDA/SSA, IRS, ACA"
        )

        return "\n".join(lines)
