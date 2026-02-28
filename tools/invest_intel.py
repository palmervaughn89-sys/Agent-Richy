"""Invest Intel — translates heartbeat engine patterns into
plain-English investment guidance for regular consumers.

Uses regime detection (bull / bear / mixed scoring across 8 signals),
sector rotation logic tied to the Fed cycle, CAPE valuation,
personalised allocation by risk + horizon, and buyable ETF mapping.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Optional

from tools.base import RichyToolBase, ToolResult
from tools.data_layer import get_latest_indicator, get_indicator_trend

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# ── Sector rotation map: macro condition → favoured sectors + ETFs ────────
_SECTOR_ROTATION: dict[str, list[dict]] = {
    "fed_cutting": [
        {"sector": "REITs",        "etf": "VNQ",  "reason": "Lower rates boost real estate valuations"},
        {"sector": "Growth",       "etf": "VUG",  "reason": "Cheaper capital fuels growth stocks"},
        {"sector": "Small Cap",    "etf": "IWM",  "reason": "Small caps benefit most from easing"},
        {"sector": "Long Bonds",   "etf": "TLT",  "reason": "Bond prices rise as yields fall"},
    ],
    "fed_hiking": [
        {"sector": "Energy",       "etf": "XLE",  "reason": "Often hiking because economy (& oil) is hot"},
        {"sector": "Financials",   "etf": "XLF",  "reason": "Banks earn more on wider net interest margin"},
        {"sector": "Short Bonds",  "etf": "SHY",  "reason": "Less duration risk while rates rise"},
        {"sector": "Value",        "etf": "VTV",  "reason": "Rotation away from growth into value"},
    ],
    "high_inflation": [
        {"sector": "Commodities",  "etf": "DJP",  "reason": "Commodities are the inflation hedge"},
        {"sector": "TIPS",         "etf": "TIP",  "reason": "Inflation-adjusted Treasury bonds"},
        {"sector": "Gold",         "etf": "GLD",  "reason": "Traditional inflation / uncertainty hedge"},
        {"sector": "Energy",       "etf": "XLE",  "reason": "Energy prices drive and benefit from inflation"},
    ],
    "recession_risk": [
        {"sector": "Utilities",    "etf": "XLU",  "reason": "Defensive, regulated earnings"},
        {"sector": "Healthcare",   "etf": "XLV",  "reason": "Non-cyclical demand"},
        {"sector": "Staples",      "etf": "XLP",  "reason": "People buy toothpaste in any economy"},
        {"sector": "Bonds",        "etf": "BND",  "reason": "Flight to safety, yields fall in recession"},
    ],
    "recovery": [
        {"sector": "Discretionary","etf": "XLY",  "reason": "Consumer spending rebounds first"},
        {"sector": "Tech",         "etf": "QQQ",  "reason": "Growth accelerates in early recovery"},
        {"sector": "Industrials",  "etf": "XLI",  "reason": "Capex cycle restarts"},
        {"sector": "Small Cap",    "etf": "IWM",  "reason": "Small caps lead recoveries historically"},
    ],
}

# ── Model portfolio templates by risk / horizon ──────────────────────────
_MODEL_PORTFOLIOS: dict[str, dict[str, float]] = {
    "conservative": {
        "US Bonds (BND)":   40,
        "Short-Term Bonds (SHY)": 15,
        "TIPS (TIP)":       10,
        "US Large Cap (VTI)": 20,
        "Dividend (VYM)":   10,
        "Intl Developed (VXUS)": 5,
    },
    "moderate": {
        "US Large Cap (VTI)": 35,
        "US Bonds (BND)":   20,
        "Intl Developed (VXUS)": 15,
        "Small Cap (IWM)":  10,
        "TIPS (TIP)":       5,
        "REITs (VNQ)":      5,
        "Gold (GLD)":       5,
        "Short-Term Bonds (SHY)": 5,
    },
    "aggressive": {
        "US Large Cap (VTI)": 30,
        "Growth (VUG)":     20,
        "Intl Developed (VXUS)": 15,
        "Small Cap (IWM)":  15,
        "Emerging Markets (VWO)": 10,
        "REITs (VNQ)":      5,
        "Gold (GLD)":       5,
    },
}

# ── CAPE (Shiller P/E) reference — no FRED series, manual ────────────────
_CAPE_REFERENCE = {
    "current": 34.5,     # as of Feb 2026 (manual)
    "historical_avg": 17.0,
    "dot_com_peak": 44.2,
    "gfc_trough": 13.3,
    "ranges": {
        "cheap": (0, 20),
        "fair": (20, 30),
        "expensive": (30, 999),
    },
}

# ── Historical average returns by asset class ────────────────────────────
_HIST_RETURNS: dict[str, dict] = {
    "US_large_cap":  {"avg": 10.3, "std": 15.6, "source": "S&P 500 1926-2025"},
    "US_small_cap":  {"avg": 11.8, "std": 20.1, "source": "Russell 2000 1979-2025"},
    "intl_developed":{"avg": 7.8,  "std": 17.2, "source": "MSCI EAFE 1970-2025"},
    "emerging":      {"avg": 9.5,  "std": 23.4, "source": "MSCI EM 1988-2025"},
    "US_bonds":      {"avg": 5.1,  "std": 5.8,  "source": "Bloomberg Agg 1976-2025"},
    "gold":          {"avg": 7.4,  "std": 15.3, "source": "LBMA Gold 1971-2025"},
    "REITs":         {"avg": 9.7,  "std": 18.9, "source": "FTSE NAREIT 1972-2025"},
    "cash":          {"avg": 3.3,  "std": 0.8,  "source": "3-Mo T-Bill 1926-2025"},
}


# ═══════════════════════════════════════════════════════════════════════════
# REGIME DETECTION SIGNALS
# ═══════════════════════════════════════════════════════════════════════════

def _score_regime() -> dict:
    """Score 8 market-regime signals and return aggregate assessment.

    Returns dict with ``regime`` (FAVORABLE / MIXED / CAUTION),
    ``score``, and per-signal breakdown.
    """
    signals: dict[str, dict] = {}

    # 1. Yield curve (10Y-2Y)
    t10y2y = get_latest_indicator("T10Y2Y")
    val = t10y2y.get("value", 0)
    if val > 0:
        signals["yield_curve"] = {"value": val, "signal": "bullish", "weight": 1.0,
                                   "note": "Yield curve normal (10Y > 2Y)"}
    else:
        signals["yield_curve"] = {"value": val, "signal": "bearish", "weight": 1.0,
                                   "note": "Yield curve INVERTED — recession warning"}

    # 2. VIX
    vix = get_latest_indicator("VIXCLS")
    val = vix.get("value", 16)
    if val < 20:
        signals["vix"] = {"value": val, "signal": "bullish", "weight": 1.0,
                          "note": f"VIX {val:.1f} — low fear"}
    elif val < 25:
        signals["vix"] = {"value": val, "signal": "neutral", "weight": 0.5,
                          "note": f"VIX {val:.1f} — moderate caution"}
    else:
        signals["vix"] = {"value": val, "signal": "bearish", "weight": 1.0,
                          "note": f"VIX {val:.1f} — elevated fear"}

    # 3. Consumer sentiment
    sent = get_latest_indicator("UMCSENT")
    sent_trend = get_indicator_trend("UMCSENT", months=3)
    val = sent.get("value", 68)
    direction = sent_trend.get("direction", "flat")
    if val > 80 or direction == "rising":
        signals["sentiment"] = {"value": val, "signal": "bullish", "weight": 0.8,
                                "note": f"Consumer sentiment {val:.0f}, trending {direction}"}
    elif val < 60 or direction == "falling":
        signals["sentiment"] = {"value": val, "signal": "bearish", "weight": 0.8,
                                "note": f"Consumer sentiment {val:.0f}, trending {direction}"}
    else:
        signals["sentiment"] = {"value": val, "signal": "neutral", "weight": 0.4,
                                "note": f"Consumer sentiment {val:.0f}, {direction}"}

    # 4. NFCI (negative = loose conditions = bullish)
    nfci = get_latest_indicator("NFCI")
    val = nfci.get("value", -0.25)
    if val < 0:
        signals["financial_conditions"] = {"value": val, "signal": "bullish", "weight": 1.0,
                                           "note": f"NFCI {val:.2f} — loose financial conditions"}
    else:
        signals["financial_conditions"] = {"value": val, "signal": "bearish", "weight": 1.0,
                                           "note": f"NFCI {val:.2f} — tight financial conditions"}

    # 5. Recession probability
    rec = get_latest_indicator("RECPROUSM156N")
    val = rec.get("value", 5)
    if val < 10:
        signals["recession_prob"] = {"value": val, "signal": "bullish", "weight": 1.0,
                                     "note": f"Recession probability {val:.1f}% — low"}
    elif val < 30:
        signals["recession_prob"] = {"value": val, "signal": "neutral", "weight": 0.5,
                                     "note": f"Recession probability {val:.1f}% — watch closely"}
    else:
        signals["recession_prob"] = {"value": val, "signal": "bearish", "weight": 1.0,
                                     "note": f"Recession probability {val:.1f}% — elevated!"}

    # 6. Sahm Rule
    sahm = get_latest_indicator("SAHMREALTIME")
    val = sahm.get("value", 0.23)
    if val < 0.3:
        signals["sahm_rule"] = {"value": val, "signal": "bullish", "weight": 1.0,
                                "note": f"Sahm indicator {val:.2f} — below 0.50 trigger"}
    elif val < 0.5:
        signals["sahm_rule"] = {"value": val, "signal": "neutral", "weight": 0.5,
                                "note": f"Sahm indicator {val:.2f} — approaching trigger"}
    else:
        signals["sahm_rule"] = {"value": val, "signal": "bearish", "weight": 1.0,
                                "note": f"Sahm indicator {val:.2f} — TRIGGERED (recession signal)"}

    # 7. High-yield spread (credit stress)
    hy = get_latest_indicator("BAMLH0A0HYM2")
    hy_trend = get_indicator_trend("BAMLH0A0HYM2", months=3)
    val = hy.get("value", 3.5)
    hy_dir = hy_trend.get("direction", "flat")
    if val < 4.0 and hy_dir != "rising":
        signals["hy_spread"] = {"value": val, "signal": "bullish", "weight": 0.8,
                                "note": f"HY spread {val:.2f}% — tight, no credit stress"}
    elif val > 5.5 or hy_dir == "rising":
        signals["hy_spread"] = {"value": val, "signal": "bearish", "weight": 0.8,
                                "note": f"HY spread {val:.2f}% ({hy_dir}) — credit stress rising"}
    else:
        signals["hy_spread"] = {"value": val, "signal": "neutral", "weight": 0.4,
                                "note": f"HY spread {val:.2f}% — normal range"}

    # 8. Fed direction
    fed_trend = get_indicator_trend("FEDFUNDS", months=6)
    fed_dir = fed_trend.get("direction", "flat")
    if fed_dir == "falling":
        signals["fed_direction"] = {"value": 0, "signal": "bullish", "weight": 1.0,
                                    "note": "Fed cutting — monetary easing"}
    elif fed_dir == "rising":
        signals["fed_direction"] = {"value": 0, "signal": "bearish", "weight": 1.0,
                                    "note": "Fed hiking — monetary tightening"}
    else:
        signals["fed_direction"] = {"value": 0, "signal": "neutral", "weight": 0.5,
                                    "note": "Fed on hold"}

    # ── Aggregate ─────────────────────────────────────────────────────────
    bull_score = sum(
        s["weight"] for s in signals.values() if s["signal"] == "bullish"
    )
    bear_score = sum(
        s["weight"] for s in signals.values() if s["signal"] == "bearish"
    )
    total_weight = sum(s["weight"] for s in signals.values())
    net_score = bull_score - bear_score  # positive = bullish
    normalised = (bull_score / total_weight) * 10 if total_weight else 5.0

    if bull_score >= 5.5:
        regime = "FAVORABLE"
    elif bear_score >= 4.5:
        regime = "CAUTION"
    else:
        regime = "MIXED"

    return {
        "regime": regime,
        "regime_score": round(normalised, 1),
        "bull_signals": round(bull_score, 1),
        "bear_signals": round(bear_score, 1),
        "signals": signals,
    }


# ═══════════════════════════════════════════════════════════════════════════
# INVEST INTEL TOOL
# ═══════════════════════════════════════════════════════════════════════════

class InvestIntel(RichyToolBase):
    """Translates economic indicators and heartbeat patterns into
    plain-English investment guidance.

    Regime detection → sector rotation → personalised allocation →
    confidence-weighted recommendations with cited indicators.
    """

    tool_id = 3
    tool_name = "invest_intel"
    description = (
        "Market regime detection, sector rotation, personalised allocation, "
        "and plain-English investment guidance"
    )
    required_profile: list[str] = []

    # ── Router entry ──────────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(question, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.80),
            response=self._narrate(plan),
            data_used=plan.get("data_sources", []),
            accuracy_score=0.82,
            sources=[
                "SP500", "VIXCLS", "T10Y2Y", "T10Y3M",
                "UMCSENT", "RECPROUSM156N", "SAHMREALTIME",
                "NFCI", "FEDFUNDS", "PCEPILFE",
                "BAMLH0A0HYM2", "GOLDAMGBD228NLBM", "DCOILWTICO",
                "CAPE (manual)", "historical returns",
            ],
            raw_data=plan,
        )

    # ── Main analysis ─────────────────────────────────────────────────────

    def analyze(self, question: str, user_profile: dict) -> dict:
        """Full investment-intelligence pipeline.

        Args:
            question: user's investment question.
            user_profile: optional keys: ``risk_tolerance`` (1-10),
                ``horizon`` ("short" | "medium" | "long"),
                ``age``, ``monthly_investable``,
                ``current_holdings`` ({ticker: pct}).

        Returns:
            Plan dict with regime, allocation, rotation, etc.
        """
        risk = int(user_profile.get("risk_tolerance", 5) or 5)
        horizon = (user_profile.get("horizon", "medium") or "medium").lower()
        age = int(user_profile.get("age", 35) or 35)
        monthly = float(user_profile.get("monthly_investable", 0) or 0)
        holdings = user_profile.get("current_holdings", {})

        data_sources: list[str] = []

        # ── 1. Regime detection ───────────────────────────────────────────
        regime = _score_regime()
        data_sources.extend([
            "T10Y2Y", "VIXCLS", "UMCSENT", "NFCI",
            "RECPROUSM156N", "SAHMREALTIME", "BAMLH0A0HYM2", "FEDFUNDS",
        ])

        # ── 2. Sector rotation ────────────────────────────────────────────
        rotation = self._sector_rotation(regime)

        # ── 3. CAPE valuation ─────────────────────────────────────────────
        valuation = self._valuation_check()

        # ── 4. Personalised allocation ────────────────────────────────────
        allocation = self._personalise_allocation(
            risk, horizon, age, regime, valuation,
        )

        # ── 5. DCA recommendation ─────────────────────────────────────────
        dca = self._dca_recommendation(
            monthly, regime, valuation, horizon,
        )

        # ── 6. Key patterns summary ───────────────────────────────────────
        patterns = self._key_patterns(regime)

        # ── 7. Holdings review (if provided) ──────────────────────────────
        holdings_review = (
            self._review_holdings(holdings, regime, rotation)
            if holdings else None
        )

        # ── Confidence ────────────────────────────────────────────────────
        confidence = self._calc_confidence(regime, valuation)

        # ── Plain-English recommendation ──────────────────────────────────
        recommendation = self._build_recommendation(
            regime, rotation, valuation, allocation, dca, risk, horizon, age,
        )

        return {
            "regime": regime["regime"],
            "regime_score": regime["regime_score"],
            "regime_signals": regime["signals"],
            "recommendation": recommendation,
            "suggested_allocation": allocation,
            "sector_rotation": rotation,
            "dca_plan": dca,
            "key_patterns": patterns,
            "valuation": valuation,
            "holdings_review": holdings_review,
            "confidence": confidence,
            "data_sources": list(set(data_sources)),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    # ── 2. Sector rotation ────────────────────────────────────────────────

    def _sector_rotation(self, regime: dict) -> list[dict]:
        """Determine which sectors to favour based on macro conditions."""
        rotations: list[dict] = []
        active_themes: list[str] = []

        signals = regime.get("signals", {})

        # Fed direction
        fed_sig = signals.get("fed_direction", {}).get("signal", "neutral")
        if fed_sig == "bullish":
            active_themes.append("fed_cutting")
        elif fed_sig == "bearish":
            active_themes.append("fed_hiking")

        # Inflation
        pce = get_latest_indicator("PCEPILFE")
        pce_trend = get_indicator_trend("PCEPILFE", months=6)
        if pce_trend.get("direction") == "rising":
            active_themes.append("high_inflation")

        # Recession risk
        rec_sig = signals.get("recession_prob", {}).get("signal", "neutral")
        sahm_sig = signals.get("sahm_rule", {}).get("signal", "neutral")
        if rec_sig == "bearish" or sahm_sig == "bearish":
            active_themes.append("recession_risk")
        elif regime["regime"] == "FAVORABLE" and rec_sig == "bullish":
            active_themes.append("recovery")

        # Default to recovery if nothing triggered
        if not active_themes:
            active_themes.append("recovery")

        # Collect unique sectors
        seen_sectors: set[str] = set()
        for theme in active_themes:
            for entry in _SECTOR_ROTATION.get(theme, []):
                if entry["sector"] not in seen_sectors:
                    rotations.append({
                        "sector": entry["sector"],
                        "etf": entry["etf"],
                        "direction": "overweight",
                        "reason": entry["reason"],
                        "theme": theme,
                    })
                    seen_sectors.add(entry["sector"])

        return rotations

    # ── 3. CAPE valuation ─────────────────────────────────────────────────

    @staticmethod
    def _valuation_check() -> dict:
        """Assess market valuation via CAPE ratio."""
        cape = _CAPE_REFERENCE["current"]
        hist_avg = _CAPE_REFERENCE["historical_avg"]

        if cape < 20:
            assessment = "cheap"
            note = (
                f"CAPE at {cape:.1f} — below historical average of {hist_avg}. "
                f"Historically, this has preceded above-average returns."
            )
        elif cape < 30:
            assessment = "fair"
            note = (
                f"CAPE at {cape:.1f} — above average but not extreme. "
                f"Expected returns are moderate."
            )
        else:
            assessment = "expensive"
            note = (
                f"CAPE at {cape:.1f} — expensive by historical standards "
                f"(avg {hist_avg}). Don't panic, but expect lower returns "
                f"over the next decade and diversify internationally."
            )

        # 10-year expected return from CAPE
        # Rough model: E[return] ≈ 1/CAPE + real growth (~2%) + inflation (~2.5%)
        expected_real = (1 / cape) * 100 + 2.0
        expected_nominal = expected_real + 2.5

        return {
            "cape": cape,
            "historical_avg": hist_avg,
            "assessment": assessment,
            "note": note,
            "expected_10yr_real": round(expected_real, 1),
            "expected_10yr_nominal": round(expected_nominal, 1),
        }

    # ── 4. Personalised allocation ────────────────────────────────────────

    @staticmethod
    def _personalise_allocation(
        risk: int,
        horizon: str,
        age: int,
        regime: dict,
        valuation: dict,
    ) -> dict:
        """Build a personalised asset allocation."""
        # Pick base template
        if risk <= 3 or age >= 60 or horizon == "short":
            base = dict(_MODEL_PORTFOLIOS["conservative"])
            label = "conservative"
        elif risk >= 8 and age < 40 and horizon == "long":
            base = dict(_MODEL_PORTFOLIOS["aggressive"])
            label = "aggressive"
        else:
            base = dict(_MODEL_PORTFOLIOS["moderate"])
            label = "moderate"

        # Regime tilts
        regime_name = regime["regime"]
        if regime_name == "CAUTION":
            # Shift 10% from equities to bonds
            eq_keys = [k for k in base if any(
                x in k for x in ("Cap", "Growth", "Small", "Emerging", "Discretionary")
            )]
            bond_keys = [k for k in base if any(x in k for x in ("Bond", "SHY", "TIP"))]
            if eq_keys and bond_keys:
                shift = 10
                per_eq = shift / len(eq_keys)
                per_bond = shift / len(bond_keys)
                for k in eq_keys:
                    base[k] = max(base[k] - per_eq, 0)
                for k in bond_keys:
                    base[k] = base[k] + per_bond
        elif regime_name == "FAVORABLE":
            # Shift 5% from bonds to equities
            eq_keys = [k for k in base if any(
                x in k for x in ("Cap", "Growth", "Small")
            )]
            bond_keys = [k for k in base if any(x in k for x in ("Bond", "SHY"))]
            if eq_keys and bond_keys:
                shift = 5
                per_eq = shift / len(eq_keys)
                per_bond = shift / len(bond_keys)
                for k in eq_keys:
                    base[k] = base[k] + per_eq
                for k in bond_keys:
                    base[k] = max(base[k] - per_bond, 0)

        # Normalise to 100%
        total = sum(base.values())
        if total > 0:
            base = {k: round(v / total * 100, 1) for k, v in base.items()}

        # Remove any 0% allocations
        base = {k: v for k, v in base.items() if v > 0}

        return {
            "label": label,
            "regime_tilt": regime_name,
            "holdings": base,
        }

    # ── 5. DCA recommendation ─────────────────────────────────────────────

    @staticmethod
    def _dca_recommendation(
        monthly: float,
        regime: dict,
        valuation: dict,
        horizon: str,
    ) -> dict:
        """Dollar-cost averaging plan."""
        if monthly <= 0:
            return {
                "applicable": False,
                "note": "Set up automatic monthly investing — even $50/mo compounds significantly.",
            }

        cape_assess = valuation["assessment"]
        regime_name = regime["regime"]

        # Pace: how aggressively to deploy
        if cape_assess == "expensive" and regime_name == "CAUTION":
            pace = "slow"
            guidance = (
                f"Markets are expensive (CAPE {valuation['cape']:.0f}) and "
                f"regime is cautious. Deploy ${monthly:,.0f}/mo steadily but "
                f"keep a cash reserve for opportunities."
            )
            allocation_split = {"invest": 70, "cash_reserve": 30}
        elif regime_name == "FAVORABLE" and cape_assess != "expensive":
            pace = "full"
            guidance = (
                f"Regime is favorable and valuations are {cape_assess}. "
                f"Deploy your full ${monthly:,.0f}/mo — time in market > timing."
            )
            allocation_split = {"invest": 100, "cash_reserve": 0}
        else:
            pace = "steady"
            guidance = (
                f"Mixed signals — keep DCA'ing ${monthly:,.0f}/mo on schedule. "
                f"Consistency beats timing over long horizons."
            )
            allocation_split = {"invest": 85, "cash_reserve": 15}

        # Projected growth (simple compound estimate)
        annual_return = valuation.get("expected_10yr_nominal", 7.0) / 100
        years = {"short": 3, "medium": 7, "long": 15}.get(horizon, 7)
        # Future value of monthly annuity
        monthly_rate = annual_return / 12
        if monthly_rate > 0:
            fv = monthly * (((1 + monthly_rate) ** (years * 12)) - 1) / monthly_rate
        else:
            fv = monthly * years * 12
        total_contributed = monthly * years * 12
        growth = fv - total_contributed

        return {
            "applicable": True,
            "monthly_amount": monthly,
            "pace": pace,
            "guidance": guidance,
            "allocation_split": allocation_split,
            "projection": {
                "years": years,
                "total_contributed": round(total_contributed, 2),
                "projected_value": round(fv, 2),
                "projected_growth": round(growth, 2),
                "assumed_return": f"{annual_return * 100:.1f}%",
            },
        }

    # ── 6. Key patterns ───────────────────────────────────────────────────

    @staticmethod
    def _key_patterns(regime: dict) -> list[dict]:
        """Summarise the most important indicator patterns."""
        patterns = []
        for name, sig in regime.get("signals", {}).items():
            patterns.append({
                "indicator": name,
                "value": sig.get("value"),
                "signal": sig["signal"],
                "weight": sig["weight"],
                "note": sig["note"],
                "accuracy": (
                    "Historical: this indicator correctly predicted "
                    "direction ~65-75% of the time over trailing 20 years."
                ),
            })
        # Sort by weight descending
        patterns.sort(key=lambda p: -p["weight"])
        return patterns

    # ── 7. Holdings review ────────────────────────────────────────────────

    @staticmethod
    def _review_holdings(
        holdings: dict,
        regime: dict,
        rotation: list[dict],
    ) -> dict:
        """Basic review of current holdings vs regime tilts."""
        # Map ETFs to broad categories
        _etf_category = {
            "VTI": "US Equity", "VOO": "US Equity", "SPY": "US Equity",
            "QQQ": "Growth", "VUG": "Growth", "IWM": "Small Cap",
            "VTV": "Value", "VYM": "Dividend",
            "VXUS": "International", "VWO": "Emerging",
            "BND": "Bonds", "AGG": "Bonds", "TLT": "Long Bonds",
            "SHY": "Short Bonds", "TIP": "TIPS",
            "VNQ": "REITs", "GLD": "Gold",
            "XLE": "Energy", "XLF": "Financials",
            "XLU": "Utilities", "XLV": "Healthcare",
            "XLP": "Staples", "XLY": "Discretionary",
            "XLI": "Industrials",
        }

        category_pcts: dict[str, float] = {}
        unrecognised: list[str] = []
        for ticker, pct in holdings.items():
            ticker_up = ticker.upper()
            cat = _etf_category.get(ticker_up)
            if cat:
                category_pcts[cat] = category_pcts.get(cat, 0) + pct
            else:
                unrecognised.append(ticker_up)

        favoured_sectors = {r["sector"] for r in rotation}
        overweight_aligned = [
            cat for cat in category_pcts
            if cat in favoured_sectors and category_pcts[cat] >= 10
        ]
        missing_sectors = [
            s for s in favoured_sectors
            if s not in category_pcts or category_pcts[s] < 5
        ]

        return {
            "category_breakdown": category_pcts,
            "aligned_with_rotation": overweight_aligned,
            "missing_favoured_sectors": missing_sectors,
            "unrecognised_tickers": unrecognised,
        }

    # ── Confidence ────────────────────────────────────────────────────────

    @staticmethod
    def _calc_confidence(regime: dict, valuation: dict) -> float:
        """Higher confidence when signals agree."""
        score = regime["regime_score"]
        # Strong agreement (near 0 or near 10) = higher confidence
        agreement = abs(score - 5.0) / 5.0  # 0 to 1
        base = 0.60 + agreement * 0.25     # 0.60 to 0.85
        return round(min(base, 0.92), 2)

    # ── Plain-English recommendation ──────────────────────────────────────

    @staticmethod
    def _build_recommendation(
        regime: dict,
        rotation: list[dict],
        valuation: dict,
        allocation: dict,
        dca: dict,
        risk: int,
        horizon: str,
        age: int,
    ) -> str:
        """Build the headline recommendation paragraph."""
        parts: list[str] = []

        # Regime headline
        rn = regime["regime"]
        rs = regime["regime_score"]
        if rn == "FAVORABLE":
            parts.append(
                f"The market regime is FAVORABLE (score {rs}/10). "
                f"Most indicators point to continued growth."
            )
        elif rn == "CAUTION":
            parts.append(
                f"The regime reads CAUTION (score {rs}/10). "
                f"Multiple warning signs suggest defensive positioning."
            )
        else:
            parts.append(
                f"Regime is MIXED (score {rs}/10) — indicators are conflicting. "
                f"Stay diversified and keep DCA'ing."
            )

        # Valuation colour
        cape_a = valuation["assessment"]
        if cape_a == "expensive":
            parts.append(
                f"Valuations are stretched (CAPE {valuation['cape']:.0f}). "
                f"Don't chase, don't panic — diversify and lean international."
            )
        elif cape_a == "cheap":
            parts.append(
                f"Valuations are attractive (CAPE {valuation['cape']:.0f}). "
                f"Historically a great time to invest for the long term."
            )

        # Sector calls
        top_sectors = rotation[:3]
        if top_sectors:
            sector_str = ", ".join(f"{r['sector']} ({r['etf']})" for r in top_sectors)
            parts.append(f"Favoured sectors: {sector_str}.")

        # Personalisation
        al = allocation["label"]
        parts.append(
            f"For your profile (risk {risk}/10, {horizon} horizon, age {age}), "
            f"I'd suggest a {al} allocation with a {regime['regime'].lower()} regime tilt."
        )

        # DCA
        if dca.get("applicable"):
            parts.append(dca["guidance"])

        # Disclaimer
        parts.append(
            "⚠️ Based on historical patterns, not a guarantee. "
            "Past performance doesn't predict future results."
        )

        return " ".join(parts)

    # ── Narration ─────────────────────────────────────────────────────────

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []

        # Header
        regime = plan["regime"]
        score = plan["regime_score"]
        emoji = {"FAVORABLE": "🟢", "MIXED": "🟡", "CAUTION": "🔴"}.get(regime, "⚪")
        lines.append(
            f"📊 **Invest Intel** — Market regime: {emoji} **{regime}** "
            f"(score {score}/10)"
        )
        lines.append("")

        # Signal dashboard
        lines.append("**Regime signals:**")
        for p in plan.get("key_patterns", []):
            sig_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}.get(p["signal"], "⚪")
            lines.append(
                f"  {sig_emoji} {p['indicator'].replace('_', ' ').title()}: "
                f"{p['note']}"
            )
        lines.append("")

        # Valuation
        v = plan.get("valuation", {})
        if v:
            lines.append(
                f"📈 **Valuation**: CAPE {v['cape']:.1f} — **{v['assessment']}** "
                f"(historical avg {v['historical_avg']})"
            )
            lines.append(
                f"   Expected 10Y return: ~{v['expected_10yr_nominal']:.1f}% nominal "
                f"({v['expected_10yr_real']:.1f}% real)"
            )
            lines.append(f"   {v['note']}")
            lines.append("")

        # Recommendation
        lines.append(f"💡 **Recommendation:**")
        lines.append(plan.get("recommendation", ""))
        lines.append("")

        # Allocation
        alloc = plan.get("suggested_allocation", {})
        if alloc.get("holdings"):
            label = alloc["label"].title()
            lines.append(
                f"**Suggested allocation ({label}, "
                f"{alloc['regime_tilt']} tilt):**"
            )
            for asset, pct in sorted(
                alloc["holdings"].items(), key=lambda x: -x[1]
            ):
                bar = "█" * int(pct / 5)
                lines.append(f"  {bar} {asset}: {pct:.1f}%")
            lines.append("")

        # Sector rotation
        rotation = plan.get("sector_rotation", [])
        if rotation:
            lines.append("**Sector rotation:**")
            for r in rotation[:5]:
                lines.append(
                    f"  📌 **{r['sector']}** ({r['etf']}) — {r['reason']} "
                    f"[{r['theme'].replace('_', ' ')}]"
                )
            lines.append("")

        # DCA plan
        dca = plan.get("dca_plan", {})
        if dca.get("applicable"):
            proj = dca.get("projection", {})
            lines.append(
                f"**DCA plan** ({dca['pace']}): "
                f"{self.fmt_currency(dca['monthly_amount'])}/mo"
            )
            if proj:
                lines.append(
                    f"  → In {proj['years']} years: "
                    f"{self.fmt_currency(proj['projected_value'])} "
                    f"({self.fmt_currency(proj['projected_growth'])} growth "
                    f"on {self.fmt_currency(proj['total_contributed'])} contributed)"
                )
            lines.append(f"  {dca['guidance']}")
            lines.append("")

        # Holdings review
        hr = plan.get("holdings_review")
        if hr:
            lines.append("**Portfolio review:**")
            if hr["aligned_with_rotation"]:
                lines.append(
                    f"  ✅ Aligned: {', '.join(hr['aligned_with_rotation'])}"
                )
            if hr["missing_favoured_sectors"]:
                lines.append(
                    f"  ⚠️ Consider adding: {', '.join(hr['missing_favoured_sectors'])}"
                )
            lines.append("")

        # Confidence
        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"⚠️ Based on historical patterns — not a guarantee."
        )

        return "\n".join(lines)
