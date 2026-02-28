"""Tax Estimator — real tax calculation using actual IRS brackets,
standard/itemized deduction logic, credits, SE tax, state tax,
capital gains, and optimisation recommendations.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# IRS REFERENCE DATA — TAX YEAR 2025
# (Revenue Procedure 2024-40, published Nov 2024)
# ═══════════════════════════════════════════════════════════════════════════

_TAX_YEAR = 2025

# ── Federal marginal brackets ────────────────────────────────────────────
# Each list entry: (upper_bound, rate).  upper_bound = math.inf for last.
_BRACKETS: dict[str, list[tuple[float, float]]] = {
    "single": [
        (11_925,  0.10),
        (48_475,  0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (626_350, 0.35),
        (math.inf, 0.37),
    ],
    "married_filing_jointly": [
        (23_850,  0.10),
        (96_950,  0.12),
        (206_700, 0.22),
        (394_600, 0.24),
        (501_050, 0.32),
        (751_600, 0.35),
        (math.inf, 0.37),
    ],
    "married_filing_separately": [
        (11_925,  0.10),
        (48_475,  0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (375_800, 0.35),
        (math.inf, 0.37),
    ],
    "head_of_household": [
        (17_000,  0.10),
        (64_850,  0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_500, 0.32),
        (626_350, 0.35),
        (math.inf, 0.37),
    ],
}

# ── Standard deduction ───────────────────────────────────────────────────
_STANDARD_DEDUCTION: dict[str, float] = {
    "single":                    15_000,
    "married_filing_jointly":    30_000,
    "married_filing_separately": 15_000,
    "head_of_household":         22_500,
}

# ── Child Tax Credit ─────────────────────────────────────────────────────
_CTC_PER_CHILD = 2_000           # children under 17
_CTC_REFUNDABLE_MAX = 1_700      # ACTC refundable portion (2025)
_CTC_PHASE_OUT_SINGLE = 200_000
_CTC_PHASE_OUT_JOINT = 400_000
_CTC_PHASE_OUT_RATE = 50          # $50 reduction per $1,000 over threshold

# ── Other dependent credit ───────────────────────────────────────────────
_ODC_PER_DEPENDENT = 500          # dependents 17+ or non-qualifying

# ── EITC 2025 (estimated from Rev Proc 2024-40) ─────────────────────────
_EITC: dict[int, dict] = {
    # children: {max_credit, phase_out_start_single, phase_out_start_joint,
    #            phase_out_end_single, phase_out_end_joint}
    0: {"max": 649, "po_start_s": 10_330, "po_start_j": 17_250,
        "po_end_s": 19_104, "po_end_j": 26_214},
    1: {"max": 3_733, "po_start_s": 21_560, "po_start_j": 28_480,
        "po_end_s": 49_084, "po_end_j": 56_004},
    2: {"max": 6_164, "po_start_s": 21_560, "po_start_j": 28_480,
        "po_end_s": 55_768, "po_end_j": 62_688},
    3: {"max": 6_935, "po_start_s": 21_560, "po_start_j": 28_480,
        "po_end_s": 59_899, "po_end_j": 66_819},
}

# ── Social Security / Self-Employment ────────────────────────────────────
_SS_WAGE_BASE = 176_100           # 2025 SS wage base
_SS_RATE = 0.062
_MEDICARE_RATE = 0.0145
_SE_TAX_RATE = 0.153              # 12.4% SS + 2.9% Medicare
_SE_DEDUCTIBLE_FACTOR = 0.9235    # taxable portion of SE income
_ADDITIONAL_MEDICARE_THRESHOLD_S = 200_000
_ADDITIONAL_MEDICARE_THRESHOLD_J = 250_000
_ADDITIONAL_MEDICARE_RATE = 0.009  # 0.9%

# ── Net Investment Income Tax ─────────────────────────────────────────────
_NIIT_RATE = 0.038
_NIIT_THRESHOLD_S = 200_000
_NIIT_THRESHOLD_J = 250_000

# ── Capital gains brackets 2025 ──────────────────────────────────────────
_LTCG_BRACKETS: dict[str, list[tuple[float, float]]] = {
    "single": [
        (48_350,   0.00),
        (533_400,  0.15),
        (math.inf, 0.20),
    ],
    "married_filing_jointly": [
        (96_700,   0.00),
        (600_050,  0.15),
        (math.inf, 0.20),
    ],
    "married_filing_separately": [
        (48_350,   0.00),
        (300_000,  0.15),
        (math.inf, 0.20),
    ],
    "head_of_household": [
        (64_750,   0.00),
        (566_700,  0.15),
        (math.inf, 0.20),
    ],
}

# ── SALT cap ──────────────────────────────────────────────────────────────
_SALT_CAP = 10_000

# ── Education credits ────────────────────────────────────────────────────
_AOTC_MAX = 2_500
_AOTC_REFUNDABLE_PCT = 0.40
_LLC_MAX = 2_000

# ── HSA limits 2025 ──────────────────────────────────────────────────────
_HSA_LIMIT_SELF = 4_300
_HSA_LIMIT_FAMILY = 8_550
_HSA_CATCH_UP = 1_000  # age 55+

# ── 401(k) / IRA limits 2025 ─────────────────────────────────────────────
_401K_LIMIT = 23_500
_401K_CATCH_UP_50 = 7_500
_401K_CATCH_UP_60_63 = 11_250  # new SECURE 2.0 super catch-up
_IRA_LIMIT = 7_000
_IRA_CATCH_UP_50 = 1_000

# ── State income tax rates (flat or top marginal for progressive) ────────
# Simplified: flat-rate states + top marginal for progressive.
_STATE_TAX: dict[str, dict] = {
    "AL": {"rate": 5.0, "type": "progressive"},
    "AK": {"rate": 0.0, "type": "none"},
    "AZ": {"rate": 2.5, "type": "flat"},
    "AR": {"rate": 3.9, "type": "progressive"},
    "CA": {"rate": 13.3, "type": "progressive"},
    "CO": {"rate": 4.4, "type": "flat"},
    "CT": {"rate": 6.99, "type": "progressive"},
    "DE": {"rate": 6.6, "type": "progressive"},
    "FL": {"rate": 0.0, "type": "none"},
    "GA": {"rate": 5.39, "type": "flat"},
    "HI": {"rate": 11.0, "type": "progressive"},
    "ID": {"rate": 5.695, "type": "flat"},
    "IL": {"rate": 4.95, "type": "flat"},
    "IN": {"rate": 3.05, "type": "flat"},
    "IA": {"rate": 3.8, "type": "flat"},
    "KS": {"rate": 5.7, "type": "progressive"},
    "KY": {"rate": 4.0, "type": "flat"},
    "LA": {"rate": 4.25, "type": "progressive"},
    "ME": {"rate": 7.15, "type": "progressive"},
    "MD": {"rate": 5.75, "type": "progressive"},
    "MA": {"rate": 5.0, "type": "flat"},
    "MI": {"rate": 4.25, "type": "flat"},
    "MN": {"rate": 9.85, "type": "progressive"},
    "MS": {"rate": 4.7, "type": "flat"},
    "MO": {"rate": 4.8, "type": "progressive"},
    "MT": {"rate": 5.9, "type": "progressive"},
    "NE": {"rate": 5.84, "type": "progressive"},
    "NV": {"rate": 0.0, "type": "none"},
    "NH": {"rate": 0.0, "type": "none"},   # no wage tax (interest/div tax ended 2025)
    "NJ": {"rate": 10.75, "type": "progressive"},
    "NM": {"rate": 5.9, "type": "progressive"},
    "NY": {"rate": 10.9, "type": "progressive"},
    "NC": {"rate": 4.5, "type": "flat"},
    "ND": {"rate": 2.5, "type": "progressive"},
    "OH": {"rate": 3.5, "type": "progressive"},
    "OK": {"rate": 4.75, "type": "progressive"},
    "OR": {"rate": 9.9, "type": "progressive"},
    "PA": {"rate": 3.07, "type": "flat"},
    "RI": {"rate": 5.99, "type": "progressive"},
    "SC": {"rate": 6.4, "type": "progressive"},
    "SD": {"rate": 0.0, "type": "none"},
    "TN": {"rate": 0.0, "type": "none"},
    "TX": {"rate": 0.0, "type": "none"},
    "UT": {"rate": 4.55, "type": "flat"},
    "VT": {"rate": 8.75, "type": "progressive"},
    "VA": {"rate": 5.75, "type": "progressive"},
    "WA": {"rate": 0.0, "type": "none"},   # 7% cap gains tax excluded here (special)
    "WV": {"rate": 5.12, "type": "progressive"},
    "WI": {"rate": 7.65, "type": "progressive"},
    "WY": {"rate": 0.0, "type": "none"},
    "DC": {"rate": 10.75, "type": "progressive"},
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER — apply marginal brackets
# ═══════════════════════════════════════════════════════════════════════════

def _apply_brackets(
    taxable: float,
    brackets: list[tuple[float, float]],
) -> tuple[float, list[dict]]:
    """Apply marginal brackets and return (total_tax, breakdown).

    ``brackets`` is a list of (upper_bound, rate), sorted ascending.
    """
    tax = 0.0
    breakdown: list[dict] = []
    prev = 0.0
    for upper, rate in brackets:
        if taxable <= 0:
            break
        span = min(taxable, upper) - prev
        if span <= 0:
            prev = upper
            continue
        layer_tax = span * rate
        tax += layer_tax
        breakdown.append({
            "bracket": f"{rate:.0%}",
            "range": f"${prev:,.0f} – ${min(taxable, upper):,.0f}",
            "income_in_bracket": round(span, 2),
            "tax": round(layer_tax, 2),
        })
        prev = upper
        if taxable <= upper:
            break
    return round(tax, 2), breakdown


def _calc_ltcg_tax(
    ltcg: float,
    ordinary_taxable: float,
    filing: str,
) -> float:
    """Calculate long-term capital gains tax using preferential rates."""
    if ltcg <= 0:
        return 0.0
    brackets = _LTCG_BRACKETS.get(filing, _LTCG_BRACKETS["single"])
    tax = 0.0
    # The LTCG brackets are based on total taxable income (ordinary + LTCG).
    # The 0% bracket "fills up" with ordinary income first.
    base = ordinary_taxable
    remaining = ltcg
    for upper, rate in brackets:
        if remaining <= 0:
            break
        room = max(upper - base, 0)
        if room <= 0:
            base = upper
            continue
        layer = min(remaining, room)
        tax += layer * rate
        remaining -= layer
        base = upper
    return round(tax, 2)


# ═══════════════════════════════════════════════════════════════════════════
# TAX ESTIMATOR TOOL
# ═══════════════════════════════════════════════════════════════════════════

class TaxEstimator(RichyToolBase):
    """Federal + state tax calculator with optimisation recommendations.

    Uses actual 2025 IRS brackets, standard/itemized logic, credits,
    SE tax, NIIT, capital gains, and state tax.
    """

    tool_id = 38
    tool_name = "tax_estimator"
    description = (
        "Federal & state tax estimate with brackets, credits, "
        "deductions, refund forecast, and optimisation strategies"
    )
    required_profile: list[str] = []

    # ── Router entry ──────────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        result = self.estimate(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=result.get("confidence", 0.88),
            response=self._narrate(result),
            data_used=["income", "filing_status", "state", "dependents",
                        "pre_tax_contributions", "itemized_deductions",
                        "other_income", "estimated_taxes_paid"],
            accuracy_score=0.90,
            sources=[
                f"IRS Rev Proc 2024-40 (TY {_TAX_YEAR})",
                "IRS Publication 17",
                "IRS Publication 505",
                "State tax tables",
            ],
            raw_data=result,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN ESTIMATE
    # ═══════════════════════════════════════════════════════════════════════

    def estimate(self, user_profile: dict) -> dict:
        """Full tax estimate pipeline.

        Keys in ``user_profile``:
            gross_income:  float
            filing_status: str  (single | married_filing_jointly |
                                 married_filing_separately | head_of_household)
            state:         str  (two-letter code)
            w2_or_1099:    str  ("w2" | "1099" | "both")
            dependents:    list[dict]  [{age: int}, ...]
            pre_tax:       dict  {401k, ira, hsa}
            itemized:      dict  {mortgage_interest, salt, charitable, medical}
            other_income:  dict  {cap_gains_short, cap_gains_long,
                                  dividends_qualified, rental, side_hustle}
            estimated_taxes_paid: float
            age:           int
        """
        # ── Extract inputs with safe defaults ─────────────────────────────
        gross = float(user_profile.get("gross_income", 0) or 0)
        filing = (
            user_profile.get("filing_status", "single") or "single"
        ).lower().replace(" ", "_")
        state = (user_profile.get("state", "") or "").upper().strip()
        w2_or_1099 = (
            user_profile.get("w2_or_1099", "w2") or "w2"
        ).lower()
        dependents = user_profile.get("dependents", []) or []
        pre_tax = user_profile.get("pre_tax", {}) or {}
        itemized = user_profile.get("itemized", {}) or {}
        other_income = user_profile.get("other_income", {}) or {}
        est_paid = float(user_profile.get("estimated_taxes_paid", 0) or 0)
        age = int(user_profile.get("age", 35) or 35)

        # Pre-tax contributions
        contrib_401k = float(pre_tax.get("401k", 0) or 0)
        contrib_ira = float(pre_tax.get("ira", 0) or 0)
        contrib_hsa = float(pre_tax.get("hsa", 0) or 0)

        # Other income
        cg_short = float(other_income.get("cap_gains_short", 0) or 0)
        cg_long = float(other_income.get("cap_gains_long", 0) or 0)
        div_qual = float(other_income.get("dividends_qualified", 0) or 0)
        rental = float(other_income.get("rental", 0) or 0)
        side_hustle = float(other_income.get("side_hustle", 0) or 0)

        # Itemized components
        mortgage_int = float(itemized.get("mortgage_interest", 0) or 0)
        salt_raw = float(itemized.get("salt", 0) or 0)
        charitable = float(itemized.get("charitable", 0) or 0)
        medical_raw = float(itemized.get("medical", 0) or 0)

        # ── 1. Gross → AGI ────────────────────────────────────────────────
        # Determine SE income
        se_income = 0.0
        if w2_or_1099 == "1099":
            se_income = gross
        elif w2_or_1099 == "both":
            se_income = side_hustle  # only side hustle is 1099

        total_se_income = se_income + side_hustle if w2_or_1099 != "both" else se_income
        if w2_or_1099 == "1099":
            total_se_income = gross + side_hustle  # all income is SE

        # Half of SE tax is above-the-line deduction
        se_taxable_base = total_se_income * _SE_DEDUCTIBLE_FACTOR
        half_se_tax = (se_taxable_base * _SE_TAX_RATE) / 2 if total_se_income > 0 else 0.0

        total_gross = gross + cg_short + cg_long + div_qual + rental + side_hustle

        agi = (
            total_gross
            - contrib_401k
            - contrib_ira
            - contrib_hsa
            - half_se_tax
        )
        agi = max(agi, 0)

        # ── 2. AGI → Taxable income ──────────────────────────────────────
        standard = _STANDARD_DEDUCTION.get(filing, 15_000)

        # Itemized total with SALT cap
        salt_capped = min(salt_raw, _SALT_CAP)
        # Medical: only amount exceeding 7.5% of AGI
        medical_deductible = max(medical_raw - agi * 0.075, 0)
        itemized_total = mortgage_int + salt_capped + charitable + medical_deductible

        if itemized_total > standard:
            deduction_method = "itemized"
            deduction_amount = itemized_total
        else:
            deduction_method = "standard"
            deduction_amount = standard

        # Ordinary taxable (excludes LTCG and qualified dividends)
        ordinary_taxable = max(agi - cg_long - div_qual - deduction_amount, 0)

        # ── 3. Apply marginal brackets ────────────────────────────────────
        brackets = _BRACKETS.get(filing, _BRACKETS["single"])
        federal_ordinary_tax, bracket_breakdown = _apply_brackets(
            ordinary_taxable, brackets,
        )

        # Determine marginal bracket
        marginal_bracket = 0.10
        for upper, rate in brackets:
            if ordinary_taxable <= upper:
                marginal_bracket = rate
                break

        # ── 4. Capital gains tax ──────────────────────────────────────────
        # Short-term: taxed as ordinary (already included in ordinary_taxable
        # via cg_short being part of total_gross → AGI)
        # Long-term + qualified dividends: preferential rate
        ltcg_total = cg_long + div_qual
        ltcg_tax = _calc_ltcg_tax(ltcg_total, ordinary_taxable, filing)

        # ── 5. NIIT (3.8% on investment income above threshold) ──────────
        niit_thresh = (
            _NIIT_THRESHOLD_J
            if filing == "married_filing_jointly"
            else _NIIT_THRESHOLD_S
        )
        investment_income = cg_short + cg_long + div_qual + rental
        niit = 0.0
        if agi > niit_thresh and investment_income > 0:
            niit = min(investment_income, agi - niit_thresh) * _NIIT_RATE
        niit = round(niit, 2)

        # ── 6. Credits ────────────────────────────────────────────────────
        credits_list: list[dict] = []
        total_nonrefundable = 0.0
        total_refundable = 0.0

        # Child Tax Credit
        children_under_17 = [d for d in dependents if d.get("age", 0) < 17]
        other_dependents = [d for d in dependents if d.get("age", 0) >= 17]

        if children_under_17:
            ctc_phase_thresh = (
                _CTC_PHASE_OUT_JOINT
                if filing == "married_filing_jointly"
                else _CTC_PHASE_OUT_SINGLE
            )
            raw_ctc = len(children_under_17) * _CTC_PER_CHILD
            if agi > ctc_phase_thresh:
                reduction = math.ceil((agi - ctc_phase_thresh) / 1_000) * _CTC_PHASE_OUT_RATE
                raw_ctc = max(raw_ctc - reduction, 0)

            nonrefundable_ctc = min(raw_ctc, federal_ordinary_tax + ltcg_tax)
            refundable_ctc = min(
                raw_ctc - nonrefundable_ctc,
                len(children_under_17) * _CTC_REFUNDABLE_MAX,
            )
            total_ctc = nonrefundable_ctc + refundable_ctc
            if total_ctc > 0:
                credits_list.append({
                    "credit": "Child Tax Credit",
                    "amount": round(total_ctc, 2),
                    "refundable": refundable_ctc > 0,
                    "children": len(children_under_17),
                })
                total_nonrefundable += nonrefundable_ctc
                total_refundable += refundable_ctc

        # Other Dependent Credit
        if other_dependents:
            odc = len(other_dependents) * _ODC_PER_DEPENDENT
            credits_list.append({
                "credit": "Other Dependent Credit",
                "amount": round(odc, 2),
                "refundable": False,
                "dependents": len(other_dependents),
            })
            total_nonrefundable += odc

        # EITC
        eitc_children = min(len(children_under_17), 3)
        eitc_info = _EITC.get(eitc_children)
        if eitc_info and filing != "married_filing_separately":
            is_joint = filing == "married_filing_jointly"
            po_start = eitc_info["po_start_j"] if is_joint else eitc_info["po_start_s"]
            po_end = eitc_info["po_end_j"] if is_joint else eitc_info["po_end_s"]
            if agi <= po_end:
                if agi <= po_start:
                    eitc_amt = eitc_info["max"]
                else:
                    phase_pct = (agi - po_start) / (po_end - po_start)
                    eitc_amt = eitc_info["max"] * (1 - phase_pct)
                eitc_amt = max(round(eitc_amt, 2), 0)
                if eitc_amt > 0:
                    credits_list.append({
                        "credit": "Earned Income Tax Credit",
                        "amount": eitc_amt,
                        "refundable": True,
                    })
                    total_refundable += eitc_amt

        total_credits = total_nonrefundable + total_refundable

        # ── 7. Self-employment tax ────────────────────────────────────────
        se_tax = 0.0
        se_details: dict = {}
        if total_se_income > 0:
            se_base = total_se_income * _SE_DEDUCTIBLE_FACTOR
            ss_portion = min(se_base, _SS_WAGE_BASE) * _SS_RATE * 2  # employee + employer
            medicare_portion = se_base * _MEDICARE_RATE * 2
            # Additional Medicare
            add_med_thresh = (
                _ADDITIONAL_MEDICARE_THRESHOLD_J
                if filing == "married_filing_jointly"
                else _ADDITIONAL_MEDICARE_THRESHOLD_S
            )
            add_medicare = 0.0
            if total_se_income > add_med_thresh:
                add_medicare = (total_se_income - add_med_thresh) * _ADDITIONAL_MEDICARE_RATE
            se_tax = round(ss_portion + medicare_portion + add_medicare, 2)
            se_details = {
                "se_income": round(total_se_income, 2),
                "taxable_base": round(se_base, 2),
                "ss_tax": round(ss_portion, 2),
                "medicare_tax": round(medicare_portion, 2),
                "additional_medicare": round(add_medicare, 2),
                "half_deducted": round(half_se_tax, 2),
            }

        # ── 8. State tax ─────────────────────────────────────────────────
        state_info = _STATE_TAX.get(state, {"rate": 0.0, "type": "unknown"})
        state_rate = state_info["rate"] / 100
        state_tax = round(max(agi - deduction_amount, 0) * state_rate, 2)
        state_name = state if state else "N/A"

        # ── 9. Totals ────────────────────────────────────────────────────
        federal_before_credits = federal_ordinary_tax + ltcg_tax + niit
        federal_after_credits = max(federal_before_credits - total_nonrefundable, 0)
        total_federal = federal_after_credits - total_refundable  # can go negative
        total_tax = total_federal + se_tax + state_tax
        effective_rate = (total_tax / total_gross * 100) if total_gross > 0 else 0.0

        # ── 10. Refund or owe ─────────────────────────────────────────────
        difference = est_paid - total_tax
        refund_or_owe = {
            "taxes_paid": round(est_paid, 2),
            "total_owed": round(total_tax, 2),
            "difference": round(difference, 2),
            "status": "REFUND" if difference >= 0 else "OWE",
        }

        # ── 11. Optimisations ─────────────────────────────────────────────
        optimizations = self._find_optimizations(
            gross=gross,
            agi=agi,
            filing=filing,
            marginal_bracket=marginal_bracket,
            contrib_401k=contrib_401k,
            contrib_ira=contrib_ira,
            contrib_hsa=contrib_hsa,
            itemized_total=itemized_total,
            standard=standard,
            charitable=charitable,
            cg_long=cg_long,
            cg_short=cg_short,
            deduction_method=deduction_method,
            age=age,
            state=state,
        )

        # ── Confidence ────────────────────────────────────────────────────
        # Higher if more inputs provided
        filled_fields = sum(1 for v in [
            gross, filing, state, dependents, contrib_401k, contrib_ira,
            contrib_hsa, mortgage_int, salt_raw, charitable, cg_long,
        ] if v)
        confidence = min(0.70 + filled_fields * 0.025, 0.95)

        return {
            "tax_year": _TAX_YEAR,
            "summary": {
                "gross_income": round(total_gross, 2),
                "agi": round(agi, 2),
                "deduction_method": deduction_method,
                "deduction_amount": round(deduction_amount, 2),
                "taxable_income_ordinary": round(ordinary_taxable, 2),
                "federal_ordinary_tax": round(federal_ordinary_tax, 2),
                "ltcg_tax": round(ltcg_tax, 2),
                "niit": niit,
                "federal_before_credits": round(federal_before_credits, 2),
                "total_credits": round(total_credits, 2),
                "federal_after_credits": round(total_federal, 2),
                "se_tax": se_tax,
                "state_tax": state_tax,
                "state": state_name,
                "total_tax": round(total_tax, 2),
                "effective_rate": round(effective_rate, 2),
                "marginal_bracket": f"{marginal_bracket:.0%}",
            },
            "bracket_breakdown": bracket_breakdown,
            "credits": credits_list,
            "se_details": se_details if se_details else None,
            "refund_or_owe": refund_or_owe,
            "optimizations": optimizations,
            "confidence": round(confidence, 2),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # OPTIMISATION ENGINE
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _find_optimizations(
        *,
        gross: float,
        agi: float,
        filing: str,
        marginal_bracket: float,
        contrib_401k: float,
        contrib_ira: float,
        contrib_hsa: float,
        itemized_total: float,
        standard: float,
        charitable: float,
        cg_long: float,
        cg_short: float,
        deduction_method: str,
        age: int,
        state: str,
    ) -> list[dict]:
        """Identify actionable tax-saving strategies."""
        opts: list[dict] = []

        # ── 401(k) gap ───────────────────────────────────────────────────
        limit_401k = _401K_LIMIT
        if 60 <= age <= 63:
            limit_401k += _401K_CATCH_UP_60_63
        elif age >= 50:
            limit_401k += _401K_CATCH_UP_50

        gap_401k = limit_401k - contrib_401k
        if gap_401k > 500:
            savings = round(gap_401k * marginal_bracket, 2)
            opts.append({
                "strategy": "Max out 401(k)",
                "gap": round(gap_401k, 2),
                "savings": savings,
                "action": (
                    f"Contribute an additional ${gap_401k:,.0f} to your 401(k). "
                    f"At your {marginal_bracket:.0%} bracket, that saves "
                    f"~${savings:,.0f} in federal tax."
                ),
                "deadline": f"Dec 31, {_TAX_YEAR}",
                "priority": "high",
            })

        # ── IRA gap ───────────────────────────────────────────────────────
        limit_ira = _IRA_LIMIT + (_IRA_CATCH_UP_50 if age >= 50 else 0)
        gap_ira = limit_ira - contrib_ira
        if gap_ira > 100:
            savings = round(gap_ira * marginal_bracket, 2)
            opts.append({
                "strategy": "Fund Traditional IRA",
                "gap": round(gap_ira, 2),
                "savings": savings,
                "action": (
                    f"Contribute ${gap_ira:,.0f} to a Traditional IRA for a "
                    f"~${savings:,.0f} deduction. (Income limits may apply — "
                    f"consider backdoor Roth if over limits.)"
                ),
                "deadline": f"Apr 15, {_TAX_YEAR + 1}",
                "priority": "medium",
            })

        # ── HSA opportunity ───────────────────────────────────────────────
        hsa_limit = _HSA_LIMIT_SELF  # simplified; family coverage higher
        if filing == "married_filing_jointly":
            hsa_limit = _HSA_LIMIT_FAMILY
        if age >= 55:
            hsa_limit += _HSA_CATCH_UP
        gap_hsa = hsa_limit - contrib_hsa
        if gap_hsa > 100:
            savings = round(gap_hsa * (marginal_bracket + 0.0765), 2)  # also avoids FICA
            opts.append({
                "strategy": "Max HSA contributions",
                "gap": round(gap_hsa, 2),
                "savings": savings,
                "action": (
                    f"Contribute ${gap_hsa:,.0f} more to your HSA. Triple tax "
                    f"benefit: deductible now, grows tax-free, tax-free for "
                    f"medical expenses. Saves ~${savings:,.0f} (income tax + FICA)."
                ),
                "deadline": f"Apr 15, {_TAX_YEAR + 1}",
                "priority": "high",
            })

        # ── Roth conversion opportunity ───────────────────────────────────
        # If in a low bracket (10% or 12%), Roth conversion may be smart
        if marginal_bracket <= 0.12 and agi < 50_000:
            # Fill up to top of 12% bracket
            bracket_12_top = {
                "single": 48_475,
                "married_filing_jointly": 96_950,
                "head_of_household": 64_850,
            }.get(filing, 48_475)
            room = max(bracket_12_top - agi, 0)
            if room > 1_000:
                tax_cost = round(room * marginal_bracket, 2)
                opts.append({
                    "strategy": "Roth conversion",
                    "gap": round(room, 2),
                    "savings": 0,  # not a "savings" but a future tax benefit
                    "tax_cost_now": tax_cost,
                    "action": (
                        f"Convert up to ${room:,.0f} from Traditional IRA to "
                        f"Roth at only {marginal_bracket:.0%}. You'd pay "
                        f"~${tax_cost:,.0f} now but never pay tax on that "
                        f"money (or its growth) again."
                    ),
                    "deadline": f"Dec 31, {_TAX_YEAR}",
                    "priority": "medium",
                })

        # ── Charitable bunching ───────────────────────────────────────────
        if deduction_method == "standard" and charitable > 0:
            # If they could bunch 2 years of giving into 1 year, would they
            # exceed the standard deduction?
            bunched = itemized_total + charitable  # double charitable
            if bunched > standard:
                extra_deduction = bunched - standard
                savings = round(extra_deduction * marginal_bracket, 2)
                opts.append({
                    "strategy": "Charitable bunching",
                    "savings": savings,
                    "action": (
                        f"You're using the standard deduction, but if you "
                        f"bunch 2 years of charitable giving into one year "
                        f"(${charitable * 2:,.0f}), your itemized deductions "
                        f"(${bunched:,.0f}) would exceed the standard "
                        f"(${standard:,.0f}), saving ~${savings:,.0f}. "
                        f"Consider a Donor Advised Fund for flexibility."
                    ),
                    "deadline": f"Dec 31, {_TAX_YEAR}",
                    "priority": "medium",
                })

        # ── Tax-loss harvesting ───────────────────────────────────────────
        if cg_short > 0 or cg_long > 0:
            total_gains = cg_short + cg_long
            potential_savings = round(
                min(total_gains, 3_000) * marginal_bracket + max(
                    0, cg_long * 0.15  # offset LTCG
                ),
                2,
            )
            opts.append({
                "strategy": "Tax-loss harvesting",
                "savings": potential_savings,
                "action": (
                    f"Review your portfolio for losing positions. "
                    f"Realised losses offset your ${total_gains:,.0f} in "
                    f"gains dollar-for-dollar, plus you can deduct up to "
                    f"$3,000/year of excess losses against ordinary income. "
                    f"Avoid wash-sale rule (30-day window)."
                ),
                "deadline": f"Dec 31, {_TAX_YEAR}",
                "priority": "high" if total_gains > 5_000 else "medium",
            })

        # ── State relocation (only if high-tax state) ─────────────────────
        state_info = _STATE_TAX.get(state, {"rate": 0, "type": "none"})
        if state_info["rate"] > 7.0 and gross > 100_000:
            savings = round(gross * state_info["rate"] / 100, 2)
            opts.append({
                "strategy": "State tax savings (if relocating)",
                "savings": savings,
                "action": (
                    f"{state} has a {state_info['rate']}% top rate. "
                    f"If remote work allows, relocating to a no-income-tax "
                    f"state (FL, TX, TN, NV, WA, WY, SD) could save "
                    f"~${savings:,.0f}/year. Not practical for everyone, "
                    f"but worth considering."
                ),
                "deadline": "Ongoing",
                "priority": "low",
            })

        # Sort by savings descending
        opts.sort(key=lambda o: -(o.get("savings", 0)))
        return opts

    # ═══════════════════════════════════════════════════════════════════════
    # NARRATION
    # ═══════════════════════════════════════════════════════════════════════

    def _narrate(self, result: dict) -> str:
        lines: list[str] = []
        s = result["summary"]
        # Parse marginal bracket string (e.g. "22%") to float for comparison
        marginal_pct = float(s["marginal_bracket"].replace("%", ""))

        # ── Header ────────────────────────────────────────────────────────
        lines.append(
            f"🧾 **Tax Estimator** — Tax Year {result['tax_year']}"
        )
        lines.append("")

        # ── Income → AGI → Taxable ────────────────────────────────────────
        lines.append("**Income summary:**")
        lines.append(f"  Gross income:      {self.fmt_currency(s['gross_income'])}")
        lines.append(f"  Adjusted Gross:    {self.fmt_currency(s['agi'])}")
        lines.append(
            f"  Deduction:         {self.fmt_currency(s['deduction_amount'])} "
            f"({s['deduction_method']})"
        )
        lines.append(f"  Taxable (ordinary):{self.fmt_currency(s['taxable_income_ordinary'])}")
        lines.append("")

        # ── Bracket breakdown ─────────────────────────────────────────────
        lines.append("**Federal bracket breakdown:**")
        for b in result["bracket_breakdown"]:
            bar = "█" * max(int(b["tax"] / max(s["federal_ordinary_tax"], 1) * 20), 1)
            lines.append(
                f"  {bar} {b['bracket']:>4s}  "
                f"{self.fmt_currency(b['income_in_bracket']):>12s}  →  "
                f"{self.fmt_currency(b['tax'])}"
            )
        lines.append(
            f"  Federal ordinary tax: {self.fmt_currency(s['federal_ordinary_tax'])}"
        )
        lines.append("")

        # Effective vs marginal
        if s["effective_rate"] < marginal_pct - 5:
            lines.append(
                f"💡 You're in the **{s['marginal_bracket']}** bracket, but your "
                f"effective rate is only **{s['effective_rate']:.1f}%**."
            )
        else:
            lines.append(
                f"💡 Marginal bracket: **{s['marginal_bracket']}** | "
                f"Effective rate: **{s['effective_rate']:.1f}%** "
                f"(includes SE & state tax)."
            )
        lines.append("")

        # ── Capital gains / NIIT ──────────────────────────────────────────
        if s["ltcg_tax"] > 0 or s["niit"] > 0:
            lines.append("**Investment taxes:**")
            if s["ltcg_tax"] > 0:
                lines.append(
                    f"  Long-term cap gains / qualified dividends tax: "
                    f"{self.fmt_currency(s['ltcg_tax'])}"
                )
            if s["niit"] > 0:
                lines.append(
                    f"  Net Investment Income Tax (3.8%): "
                    f"{self.fmt_currency(s['niit'])}"
                )
            lines.append("")

        # ── SE tax ────────────────────────────────────────────────────────
        se = result.get("se_details")
        if se:
            lines.append("**Self-employment tax:**")
            lines.append(f"  SE income:         {self.fmt_currency(se['se_income'])}")
            lines.append(f"  SS portion:        {self.fmt_currency(se['ss_tax'])}")
            lines.append(f"  Medicare portion:  {self.fmt_currency(se['medicare_tax'])}")
            if se["additional_medicare"] > 0:
                lines.append(
                    f"  Add'l Medicare:    {self.fmt_currency(se['additional_medicare'])}"
                )
            lines.append(f"  Half deducted:     ({self.fmt_currency(se['half_deducted'])})")
            lines.append(f"  Total SE tax:      {self.fmt_currency(s['se_tax'])}")
            lines.append("")

        # ── Credits ───────────────────────────────────────────────────────
        credits = result.get("credits", [])
        if credits:
            lines.append("**Credits:**")
            for c in credits:
                ref = " (refundable)" if c.get("refundable") else ""
                lines.append(
                    f"  ✅ {c['credit']}: {self.fmt_currency(c['amount'])}{ref}"
                )
            lines.append(
                f"  Total credits: {self.fmt_currency(s['total_credits'])}"
            )
            lines.append("")

        # ── State tax ─────────────────────────────────────────────────────
        if s["state_tax"] > 0:
            lines.append(
                f"**State tax ({s['state']}):** "
                f"{self.fmt_currency(s['state_tax'])}"
            )
            lines.append("")

        # ── Bottom line ───────────────────────────────────────────────────
        lines.append("━" * 40)
        lines.append(
            f"  **Total tax:       {self.fmt_currency(s['total_tax'])}**"
        )
        lines.append(
            f"  Effective rate:    **{s['effective_rate']:.1f}%**"
        )
        lines.append("━" * 40)
        lines.append("")

        # ── Refund / owe ──────────────────────────────────────────────────
        ro = result["refund_or_owe"]
        if ro["taxes_paid"] > 0:
            if ro["status"] == "REFUND":
                lines.append(
                    f"💰 **REFUND: {self.fmt_currency(ro['difference'])}** "
                    f"(you paid {self.fmt_currency(ro['taxes_paid'])}, "
                    f"owe {self.fmt_currency(ro['total_owed'])})"
                )
            else:
                lines.append(
                    f"⚠️ **YOU OWE: {self.fmt_currency(abs(ro['difference']))}** "
                    f"(paid {self.fmt_currency(ro['taxes_paid'])}, "
                    f"owe {self.fmt_currency(ro['total_owed'])})"
                )
            lines.append("")

        # ── Optimisations ─────────────────────────────────────────────────
        opts = result.get("optimizations", [])
        if opts:
            lines.append("**🔧 Tax-saving strategies:**")
            for i, o in enumerate(opts, 1):
                sav = o.get("savings", 0)
                sav_str = f" → save ~{self.fmt_currency(sav)}" if sav else ""
                pri = {"high": "🔴", "medium": "🟡", "low": "⚪"}.get(
                    o.get("priority", "low"), "⚪"
                )
                lines.append(f"  {pri} {i}. **{o['strategy']}**{sav_str}")
                lines.append(f"     {o['action']}")
                if o.get("deadline"):
                    lines.append(f"     ⏰ Deadline: {o['deadline']}")
                lines.append("")

        # ── Confidence ────────────────────────────────────────────────────
        lines.append(
            f"Confidence: {result['confidence']:.0%} | "
            f"Source: IRS Rev Proc 2024-40 (TY {_TAX_YEAR})"
        )

        return "\n".join(lines)
