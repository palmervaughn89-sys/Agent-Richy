"""
Question Router for the Richy Financial Engine.

Takes a user's natural language question and routes it to the correct
tool, optionally invoking multiple tools for compound questions.

Inherits from ``tools.base.RichyToolBase``.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# TOOL REGISTRY — every user-facing tool Richy can invoke
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ToolSpec:
    """Metadata for one routable tool."""

    tool_id: int
    name: str
    description: str
    keywords: list[str]
    agent: str                         # which agent class handles this
    calculator: Optional[str] = None   # key into CALCULATOR_REGISTRY (if any)
    required_profile: list[str] = field(default_factory=list)
    data_sources: list[str] = field(default_factory=list)


TOOL_CATALOG: list[ToolSpec] = [
    # ── 01  Coach Richy (general fallback) ────────────────────────────────
    ToolSpec(
        tool_id=1,
        name="coach_richy_general",
        description="General financial coaching and Q&A",
        keywords=[],  # catch-all — no keywords needed
        agent="coach_richy",
        data_sources=["GPT-4o / Gemini", "knowledge_base", "response_cache"],
    ),

    # ── 02  Budget Bot ────────────────────────────────────────────────────
    ToolSpec(
        tool_id=2,
        name="budget_analysis",
        description="Budget creation, 50/30/20 analysis, spending review",
        keywords=[
            "budget", "spending", "monthly", "afford", "expenses",
            "50/30/20", "spending plan", "allocate", "needs wants savings",
            "overspend", "track spending", "expense", "cut cost",
        ],
        agent="budget_bot",
        calculator="budget_50_30_20",
        required_profile=["income"],
        data_sources=["income", "monthly_expenses", "budget_50_30_20 calculator"],
    ),

    # ── 03  Invest Intel ──────────────────────────────────────────────────
    ToolSpec(
        tool_id=3,
        name="invest_intel",
        description="Investment strategy, portfolio allocation, compound growth",
        keywords=[
            "invest", "stock", "buy shares", "portfolio", "etf",
            "index fund", "roth ira", "401k", "diversif", "asset allocation",
            "bonds", "dividend", "mutual fund", "brokerage",
            "dca", "dollar cost", "s&p", "market cap",
        ],
        agent="invest_intel",
        calculator="compound_interest",
        required_profile=["income", "risk_tolerance"],
        data_sources=[
            "risk_tolerance", "income", "age",
            "data/investments.json", "compound_interest calculator",
        ],
    ),

    # ── 04  Debt Destroyer ────────────────────────────────────────────────
    ToolSpec(
        tool_id=4,
        name="debt_destroyer",
        description="Debt payoff strategy (avalanche, snowball, hybrid), refi, BT, rate forecast",
        keywords=[
            "debt", "pay off", "credit card", "loan payoff", "owe",
            "balance", "consolidat", "payoff", "interest rate",
            "student loan", "car loan", "personal loan",
            "minimum payment", "snowball", "avalanche",
            "balance transfer", "refinanc", "payoff plan",
            "debt free", "freedom date",
        ],
        agent="debt_destroyer",
        calculator="debt_payoff",
        required_profile=["debts"],
        data_sources=[
            "FEDFUNDS", "DPRIME", "TERMCBCCALLNS",
            "MORTGAGE30US", "RIFLPBCIANM60NM", "TDSP",
            "debt_payoff calculator", "snowball_vs_avalanche calculator",
        ],
    ),

    # ── 05  Savings Sage ──────────────────────────────────────────────────
    ToolSpec(
        tool_id=5,
        name="savings_sage",
        description="Savings strategy, emergency fund, HYSA, CD ladders, I-Bonds",
        keywords=[
            "save", "savings", "hysa", "cd", "i-bond", "emergency",
            "sinking fund", "save money", "high yield", "rainy day",
            "financial cushion", "savings account",
        ],
        agent="savings_sage",
        calculator="emergency_fund_status",
        required_profile=["income"],
        data_sources=[
            "monthly_expenses", "savings_balance",
            "emergency_fund_status calculator", "savings_goal_timeline calculator",
        ],
    ),

    # ── 06  Kid Coach ─────────────────────────────────────────────────────
    ToolSpec(
        tool_id=6,
        name="kid_coach",
        description="Youth financial education, allowance advice, age-adaptive",
        keywords=[
            "kid", "child", "allowance", "teach money", "teen",
            "teenager", "young", "my son", "my daughter",
            "financial literacy kids", "youth",
        ],
        agent="kid_coach",
        data_sources=["age", "lessons.py curriculum", "animated_lessons.py"],
    ),

    # ── 12  Net Worth ─────────────────────────────────────────────────────
    ToolSpec(
        tool_id=12,
        name="net_worth",
        description="Net worth calculation (assets minus liabilities)",
        keywords=[
            "net worth", "assets", "wealth", "what am i worth",
            "assets minus liabilities", "financial snapshot",
            "total assets", "liabilities",
        ],
        agent="coach_richy",
        calculator="net_worth_calculator",
        data_sources=["assets", "liabilities", "net_worth_calculator"],
    ),

    # ── 13  Credit Score ──────────────────────────────────────────────────
    ToolSpec(
        tool_id=13,
        name="credit_score",
        description="Credit score explanation, improvement tips, FICO factors",
        keywords=[
            "credit score", "fico", "credit report", "credit check",
            "credit bureau", "credit history", "credit utilization",
            "improve credit", "build credit",
        ],
        agent="coach_richy",
        data_sources=[
            "credit_score", "debt_balances",
            "knowledge_base/credit_scores.md",
        ],
    ),

    # ── 15  Retirement ────────────────────────────────────────────────────
    ToolSpec(
        tool_id=15,
        name="retirement_planner",
        description="Retirement planning: 401k, IRA, Social Security, pension",
        keywords=[
            "retire", "retirement", "401k", "ira", "roth",
            "social security", "pension", "fire",
            "retire early", "nest egg",
        ],
        agent="invest_intel",
        calculator="compound_interest",
        required_profile=["income", "age"],
        data_sources=[
            "income", "age", "has_401k", "has_ira",
            "compound_interest calculator",
            "knowledge_base/retirement_planning.md",
        ],
    ),

    # ── 16  Grocery / Shopping ────────────────────────────────────────────
    ToolSpec(
        tool_id=16,
        name="smart_grocery",
        description="Grocery optimisation: cheapest store, trip cost, seasonal, swaps",
        keywords=[
            "grocery", "food", "shopping list", "store", "cheapest",
            "meal plan", "food budget", "supermarket", "walmart",
            "costco", "aldi", "kroger", "target", "trader joe",
            "whole foods", "grocery bill", "groceries",
            "unit price", "per pound", "sale", "coupon",
        ],
        agent="smart_grocery",
        required_profile=["zip_code"],
        data_sources=[
            "CUSR0000SAF11", "CUSR0000SETB01",
            "stores_nearby", "USDA food plans",
            "store reference prices",
        ],
    ),

    # ── 23  Discount / Deals ──────────────────────────────────────────────
    ToolSpec(
        tool_id=23,
        name="discount_predictions",
        description="When to buy, sale predictions, coupon strategy",
        keywords=[
            "discount", "sale", "deal", "coupon", "when to buy",
            "price drop", "black friday", "best time to buy",
            "clearance",
        ],
        agent="budget_bot",
        data_sources=["stores_nearby", "historical pricing patterns"],
    ),

    # ── 34  Subscription Audit ────────────────────────────────────────────
    ToolSpec(
        tool_id=34,
        name="subscription_audit",
        description="Review and cut subscriptions, calculate savings",
        keywords=[
            "subscribe", "subscription", "cancel",
            "streaming", "netflix", "spotify", "monthly service",
            "recurring charge",
        ],
        agent="budget_bot",
        required_profile=["monthly_expenses"],
        data_sources=["monthly_expenses", "subscriptions list"],
    ),

    # ── 35  Bill Negotiation ──────────────────────────────────────────────
    ToolSpec(
        tool_id=35,
        name="bill_negotiation",
        description="Negotiate bills, lower monthly costs",
        keywords=[
            "negotiate", "bill", "lower my", "reduce bill",
            "haggle", "call provider", "cancel threat",
            "retention offer",
        ],
        agent="budget_bot",
        data_sources=["monthly_expenses", "knowledge_base/budgeting_methods.md"],
    ),

    # ── 36  Side Hustle ───────────────────────────────────────────────────
    ToolSpec(
        tool_id=36,
        name="side_hustle",
        description="Extra income ideas, gig economy, freelancing",
        keywords=[
            "side hustle", "extra money", "gig", "freelance",
            "extra income", "part time", "hustle",
            "uber", "doordash", "fiverr", "etsy",
        ],
        agent="coach_richy",
        data_sources=[
            "age", "income",
            "knowledge_base/side_hustles.md",
        ],
    ),

    # ── 37  Auto / Vehicle ────────────────────────────────────────────────
    ToolSpec(
        tool_id=37,
        name="auto_advisor",
        description="Car buying, leasing, auto loans, vehicle costs",
        keywords=[
            "car", "auto", "vehicle", "buy car", "lease",
            "car loan", "auto insurance", "car payment",
            "trade in", "used car", "new car",
        ],
        agent="coach_richy",
        required_profile=["income"],
        data_sources=["income", "monthly_expenses", "car_owner"],
    ),

    # ── 38  Tax Estimator ─────────────────────────────────────────────────
    ToolSpec(
        tool_id=38,
        name="tax_estimator",
        description="Federal tax estimate, brackets, deductions, refund forecast",
        keywords=[
            "tax", "deduction", "bracket", "refund", "owe",
            "w2", "1099", "filing", "standard deduction",
            "itemize", "capital gains", "withholding",
        ],
        agent="coach_richy",
        required_profile=["income", "filing_status"],
        data_sources=[
            "income", "filing_status", "dependents",
            "estimate_federal_tax()",
            "knowledge_base/tax_planning.md",
        ],
    ),

    # ── 39  Mortgage / Housing ────────────────────────────────────────────
    ToolSpec(
        tool_id=39,
        name="mortgage_calculator",
        description="Mortgage payment, rent vs buy, refinance, home affordability",
        keywords=[
            "house", "mortgage", "buy home", "rent vs buy", "refinance",
            "home loan", "down payment", "property", "real estate",
            "pmi", "home equity",
        ],
        agent="coach_richy",
        required_profile=["income"],
        data_sources=[
            "income", "monthly_expenses", "home_owner",
            "mortgage_payment()",
            "knowledge_base/real_estate.md",
        ],
    ),

    # ── 41  College / Education ───────────────────────────────────────────
    ToolSpec(
        tool_id=41,
        name="college_planner",
        description="College savings, 529 plans, student loans, tuition",
        keywords=[
            "college", "tuition", "529", "student loan",
            "university", "scholarship", "financial aid",
            "education savings",
        ],
        agent="savings_sage",
        calculator="savings_goal_timeline",
        data_sources=[
            "age", "income", "dependents",
            "savings_goal_timeline calculator",
            "knowledge_base/kids_finance.md",
        ],
    ),

    # ── 43  Insurance ─────────────────────────────────────────────────────
    ToolSpec(
        tool_id=43,
        name="insurance_guide",
        description="Health, life, auto, disability, renters/homeowners insurance",
        keywords=[
            "insurance", "health plan", "premium", "coverage",
            "life insurance", "disability", "renters insurance",
            "homeowners", "umbrella", "hdhp", "hsa",
        ],
        agent="coach_richy",
        data_sources=[
            "income", "age", "home_owner", "car_owner", "dependents",
            "knowledge_base/insurance_essentials.md",
        ],
    ),

    # ── 46  Market / Economy ──────────────────────────────────────────────
    ToolSpec(
        tool_id=46,
        name="market_outlook",
        description="Market commentary, recession indicators, inflation impact",
        keywords=[
            "market", "economy", "recession", "inflation",
            "bear market", "bull market", "fed", "interest rate hike",
            "gdp", "unemployment",
        ],
        agent="invest_intel",
        data_sources=["knowledge_base/investing_basics.md"],
    ),

    # ── 47  Interest Rate Lookup ──────────────────────────────────────────
    ToolSpec(
        tool_id=47,
        name="rate_lookup",
        description="Interest rate comparisons: APR, APY, HYSA rates, CD rates",
        keywords=[
            "rate", "interest rate", "apr", "apy",
            "fed rate", "prime rate", "cd rate",
            "hysa rate", "mortgage rate",
        ],
        agent="savings_sage",
        data_sources=["knowledge_base/emergency_funds.md"],
    ),
]

# Build a fast id→spec lookup
_CATALOG_BY_ID: dict[int, ToolSpec] = {t.tool_id: t for t in TOOL_CATALOG}

# Compound routing map: keyword triggers two tools simultaneously
_COMPOUND_KEYWORDS: dict[str, str] = {
    "discount_grocery": "tool_16_23",  # grocery + discount predictions
}


# ═══════════════════════════════════════════════════════════════════════════
# MULTI-INTENT DETECTOR
# ═══════════════════════════════════════════════════════════════════════════

# Pairs of tool IDs that commonly co-occur in a single question
_COMBO_SIGNALS: list[tuple[list[str], list[int]]] = [
    # "Should I pay off debt or invest?"
    (["pay off.*invest", "invest.*debt", "debt or invest", "invest or pay"],
     [4, 3]),
    # "Should I rent or buy a house?"
    (["rent or buy", "buy or rent", "rent vs buy", "renting vs buying"],
     [39, 2]),
    # "Should I save or invest?"
    (["save or invest", "invest or save", "savings vs invest"],
     [5, 3]),
    # "Pay debt or build emergency fund?"
    (["debt or emergency", "emergency or debt", "pay off.*emergency",
      "emergency.*pay off"],
     [4, 5]),
    # "Budget and debt plan"
    (["budget.*debt", "debt.*budget"],
     [2, 4]),
    # "Tax implications of investing"
    (["tax.*invest", "invest.*tax", "capital gains"],
     [38, 3]),
    # "Retirement vs pay off mortgage"
    (["retire.*mortgage", "mortgage.*retire", "401k.*house", "house.*401k"],
     [15, 39]),
    # "Side hustle for debt payoff"
    (["side hustle.*debt", "extra income.*pay off", "gig.*debt"],
     [36, 4]),
    # "Insurance and mortgage costs"
    (["insurance.*mortgage", "mortgage.*insurance", "home insurance.*buy"],
     [43, 39]),
    # "College savings vs investing"
    (["college.*invest", "529.*stock", "tuition.*save or invest"],
     [41, 3]),
]


def detect_multi_intent(question: str) -> Optional[list[int]]:
    """Check if a question needs answers from multiple tools.

    Returns a list of tool_ids if a compound intent is detected,
    or ``None`` for single-intent questions.
    """
    q = question.lower()
    for patterns, tool_ids in _COMBO_SIGNALS:
        for pat in patterns:
            if re.search(pat, q):
                return tool_ids
    return None


# ═══════════════════════════════════════════════════════════════════════════
# SINGLE-INTENT SCORER
# ═══════════════════════════════════════════════════════════════════════════

def _score_tool(spec: ToolSpec, question_lower: str) -> float:
    """Score a tool against a question. Higher = better match.

    Scoring:
      - Each keyword match adds ``len(keyword)`` points
        (longer phrases score higher to reward specificity).
      - Exact phrase matches get a 1.5x multiplier.
    """
    score = 0.0
    for kw in spec.keywords:
        if kw in question_lower:
            # Exact substring match
            score += len(kw) * 1.5
        elif any(w in question_lower for w in kw.split()):
            # Partial word match (e.g. "investing" matches "invest")
            score += len(kw) * 0.5
    return score


def rank_tools(question: str, top_k: int = 3) -> list[tuple[ToolSpec, float]]:
    """Return the top-k tool specs with their raw scores."""
    q = question.lower()
    scored = [(spec, _score_tool(spec, q)) for spec in TOOL_CATALOG if spec.keywords]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# ═══════════════════════════════════════════════════════════════════════════
# TOOL ROUTER
# ═══════════════════════════════════════════════════════════════════════════

class ToolRouter(RichyToolBase):
    """Routes a natural-language question to the correct Richy tool.

    Usage::

        router = ToolRouter()
        result = router.route(
            "Should I pay off my credit card or invest?",
            user_profile={...},
        )
        # result is a dict (or list of dicts for multi-intent)
    """

    tool_id = 0
    tool_name = "tool_router"
    description = "Meta-tool that routes questions to the right financial tool"

    # ── Lazy-loaded tool instances ────────────────────────────────────────

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tool_instances: dict[int, RichyToolBase] = {}

    # ── Primary entry point ───────────────────────────────────────────────

    def route(self, question: str, user_profile: dict) -> dict | list[dict]:
        """Route a question to the right tool(s) and execute.

        Returns:
            A single result dict for simple questions, or a list of
            result dicts for compound questions.
        """
        # 1. Check for multi-intent first
        multi = detect_multi_intent(question)
        if multi:
            return self._handle_multi(question, user_profile, multi)

        # 2. Single-intent ranking
        ranked = rank_tools(question, top_k=3)

        if not ranked or ranked[0][1] == 0:
            # No keyword matches → fall back to Coach Richy (tool_01)
            return self._dispatch(1, question, user_profile, confidence=0.2)

        best_spec, best_score = ranked[0]
        confidence = min(best_score / 30.0, 1.0)  # normalise to 0-1

        return self._dispatch(
            best_spec.tool_id, question, user_profile, confidence=confidence,
        )

    # ── Multi-intent handler ──────────────────────────────────────────────

    def _handle_multi(
        self,
        question: str,
        user_profile: dict,
        tool_ids: list[int],
    ) -> list[dict]:
        """Execute multiple tools and combine results."""
        results: list[dict] = []
        for tid in tool_ids:
            r = self._dispatch(tid, question, user_profile, confidence=0.85)
            results.append(r)
        return results

    # ── Dispatch to a concrete tool ───────────────────────────────────────

    def _dispatch(
        self,
        tool_id: int,
        question: str,
        user_profile: dict,
        confidence: float = 0.5,
    ) -> dict:
        """Instantiate (or reuse) the tool for *tool_id* and call it."""
        spec = _CATALOG_BY_ID.get(tool_id)
        if spec is None:
            # Unknown ID → fallback
            spec = _CATALOG_BY_ID[1]
            tool_id = 1

        # Build a lightweight tool instance on the fly
        tool = self._resolve_tool(spec)
        result = tool.run(question, user_profile)

        # Override confidence with the router's calculated value
        result["confidence"] = round(confidence, 4)
        return result

    def _resolve_tool(self, spec: ToolSpec) -> RichyToolBase:
        """Return an instance of the right tool class for a ToolSpec.

        Uses ``_CalculatorTool`` for specs with a calculator key,
        ``_AgentTool`` for LLM-backed agents, and falls back to
        ``_PassthroughTool`` otherwise.
        """
        if spec.tool_id in self._tool_instances:
            return self._tool_instances[spec.tool_id]

        if spec.calculator:
            tool = _CalculatorTool(spec)
        elif spec.agent:
            tool = _AgentTool(spec)
        else:
            tool = _PassthroughTool(spec)

        self._tool_instances[spec.tool_id] = tool
        return tool

    # ── Required abstract method (not used directly) ─────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        """ToolRouter delegates to ``route()`` instead of ``execute()``."""
        result = self.route(question, user_profile)
        if isinstance(result, list):
            combined = "; ".join(r.get("response", "") for r in result)
            return ToolResult(
                tool_id=0,
                tool_name="tool_router",
                confidence=0.9,
                response=combined,
                data_used=[],
                sources=[],
            )
        return ToolResult(**{k: v for k, v in result.items()
                            if k in ToolResult.__dataclass_fields__})


# ═══════════════════════════════════════════════════════════════════════════
# CONCRETE TOOL WRAPPERS (auto-generated from ToolSpec)
# ═══════════════════════════════════════════════════════════════════════════

class _CalculatorTool(RichyToolBase):
    """Wraps a financial calculator function as a RichyToolBase."""

    def __init__(self, spec: ToolSpec):
        self.tool_id = spec.tool_id
        self.tool_name = spec.name
        self.description = spec.description
        self.required_profile = spec.required_profile
        self._spec = spec
        self._calc_fn = self._load_calculator(spec.calculator)

    @staticmethod
    def _load_calculator(calc_name: str | None):
        """Import the calculator function lazily."""
        if not calc_name:
            return None
        try:
            from utils.financial_calculators import CALCULATOR_REGISTRY
            return CALCULATOR_REGISTRY.get(calc_name)
        except ImportError:
            logger.warning("Could not import financial_calculators")
            return None

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        from utils.intent_detection import extract_numbers, detect_intent

        numbers = extract_numbers(question)
        calc_name = self._spec.calculator

        raw: dict = {}
        response_text = ""
        data_used: list[str] = []

        # ── Try to run the matching calculator ────────────────────────────
        if self._calc_fn and calc_name:
            try:
                raw = self._auto_fill_and_run(
                    calc_name, numbers, question, user_profile,
                )
                data_used = list(raw.keys())[:10]
                response_text = self._narrate(calc_name, raw)
            except Exception as exc:
                logger.warning("Calculator %s failed: %s", calc_name, exc)
                response_text = (
                    f"I tried to calculate that but need a bit more info. "
                    f"Could you provide specific numbers (amounts, rates, timeframe)?"
                )

        if not response_text:
            response_text = (
                f"I can help with {self._spec.description}. "
                f"Give me some numbers and I'll crunch them for you!"
            )

        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=0.8 if raw else 0.4,
            response=response_text,
            data_used=data_used,
            accuracy_score=0.95 if raw else 0.0,
            sources=self._spec.data_sources,
            raw_data=raw,
        )

    # ── Calculator auto-fill logic ────────────────────────────────────────

    def _auto_fill_and_run(
        self,
        calc_name: str,
        numbers: list[float],
        question: str,
        profile: dict,
    ) -> dict:
        """Map extracted numbers + profile data to calculator kwargs."""
        fn = self._calc_fn
        if fn is None:
            return {}

        income = profile.get("income", 0)
        monthly_expenses = profile.get("monthly_expenses", {})
        total_expenses = (
            sum(monthly_expenses.values())
            if isinstance(monthly_expenses, dict) else float(monthly_expenses or 0)
        )

        if calc_name == "compound_interest":
            principal = numbers[0] if numbers else 0
            rate = self._extract_pct(question, default=8.0)
            years = int(numbers[1]) if len(numbers) > 1 and numbers[1] < 100 else 30
            monthly = numbers[2] if len(numbers) > 2 else 0
            return fn(principal, rate, years, monthly)

        if calc_name == "debt_payoff":
            debts = profile.get("debt_balances", {})
            if debts:
                first_name = next(iter(debts))
                balance = debts[first_name]
                apr = 20.0  # sensible default
                payment = numbers[0] if numbers else balance * 0.03
                return fn(balance, apr, payment)
            if len(numbers) >= 2:
                balance = max(numbers)
                payment = min(n for n in numbers if 0 < n < balance)
                rate = self._extract_pct(question, default=20.0)
                return fn(balance, rate, payment)

        if calc_name == "debt_snowball_vs_avalanche":
            debts = profile.get("debt_balances", {})
            if debts:
                debt_list = [
                    {"name": k, "balance": v, "apr": 20.0, "min_payment": v * 0.03}
                    for k, v in debts.items()
                ]
                return fn(debt_list)

        if calc_name == "emergency_fund_status":
            expenses = total_expenses or (numbers[0] if numbers else 3000)
            savings = profile.get("savings_balance",
                                  numbers[1] if len(numbers) > 1 else 0)
            return fn(expenses, savings)

        if calc_name == "budget_50_30_20":
            inc = income or (numbers[0] if numbers else 5000)
            return fn(inc)

        if calc_name == "savings_goal_timeline":
            goal = numbers[0] if numbers else 10000
            current = profile.get("savings_balance", 0)
            monthly = numbers[1] if len(numbers) > 1 else income * 0.2 if income else 500
            return fn(goal, current, monthly)

        if calc_name == "net_worth_calculator":
            assets = {"savings": profile.get("savings_balance", 0)}
            liabilities = profile.get("debt_balances", {})
            return fn(assets, liabilities)

        return {}

    @staticmethod
    def _extract_pct(text: str, default: float = 8.0) -> float:
        """Pull a percentage number from text (e.g. '7%' → 7.0)."""
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        return float(m.group(1)) if m else default

    # ── Human-readable narration ──────────────────────────────────────────

    @staticmethod
    def _narrate(calc_name: str, raw: dict) -> str:
        """Turn raw calculator output into a readable sentence."""
        if "error" in raw:
            return raw["error"]

        if calc_name == "compound_interest":
            return (
                f"If you start with ${raw.get('total_contributed', 0):,.0f} in contributions, "
                f"you'll have **${raw['final_amount']:,.0f}** — "
                f"that's ${raw['total_interest']:,.0f} in pure interest!"
            )
        if calc_name == "debt_payoff":
            return (
                f"You'll be debt-free in **{raw['months_to_payoff']} months** "
                f"({raw['years_to_payoff']} years). Total interest paid: "
                f"${raw['total_interest']:,.0f}."
            )
        if calc_name == "debt_snowball_vs_avalanche":
            rec = raw.get("recommendation", "avalanche")
            saved = raw.get("interest_saved_with_avalanche", 0)
            return (
                f"Recommendation: **{rec.title()}** method. "
                f"Avalanche saves ${saved:,.0f} in interest vs snowball."
            )
        if calc_name == "emergency_fund_status":
            return (
                f"You have **{raw['months_covered']} months** of expenses covered. "
                f"Status: {raw['status'].replace('_', ' ').title()}. {raw['message']}"
            )
        if calc_name == "budget_50_30_20":
            rec = raw.get("recommended", {})
            return (
                f"On your income, the 50/30/20 split is: "
                f"Needs ${rec.get('needs', 0):,.0f} / "
                f"Wants ${rec.get('wants', 0):,.0f} / "
                f"Savings ${rec.get('savings', 0):,.0f}."
            )
        if calc_name == "savings_goal_timeline":
            if raw.get("already_reached"):
                return "You've already reached your savings goal! 🎉"
            return (
                f"At your current pace you'll hit your goal in "
                f"**{raw['months_to_goal']} months** ({raw['years_to_goal']} years)."
            )
        if calc_name == "net_worth_calculator":
            return (
                f"Your estimated net worth is **${raw['net_worth']:,.0f}** "
                f"(assets ${raw['total_assets']:,.0f} − liabilities "
                f"${raw['total_liabilities']:,.0f})."
            )
        return str(raw)


class _AgentTool(RichyToolBase):
    """Wraps an LLM agent (coach_richy, budget_bot, etc.) as a tool."""

    def __init__(self, spec: ToolSpec):
        self.tool_id = spec.tool_id
        self.tool_name = spec.name
        self.description = spec.description
        self.required_profile = spec.required_profile
        self._spec = spec

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        # Attempt to use the enriched-context pipeline
        try:
            from utils.intent_detection import build_enriched_context
            ctx = build_enriched_context(question)

            response = ctx.get("cached_response") or ctx.get("enriched_prompt")
            calc_result = ctx.get("calculator_result")

            data_used = []
            if calc_result:
                data_used = list(calc_result.keys())[:10]
            if ctx.get("knowledge_context"):
                data_used.append("knowledge_base_rag")

            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=ctx.get("intent", {}).get("confidence", 0.6),
                response=response or f"Ask {self._spec.agent} about: {question}",
                data_used=data_used,
                accuracy_score=0.85 if calc_result else 0.7,
                sources=self._spec.data_sources,
                raw_data=calc_result or {},
            )
        except ImportError:
            logger.warning("intent_detection not available; returning stub")
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=0.5,
                response=(
                    f"I'd route this to **{self._spec.agent}** for a detailed answer. "
                    f"({self._spec.description})"
                ),
                data_used=[],
                accuracy_score=0.0,
                sources=self._spec.data_sources,
            )


class _PassthroughTool(RichyToolBase):
    """Fallback tool that returns descriptive metadata without computation."""

    def __init__(self, spec: ToolSpec):
        self.tool_id = spec.tool_id
        self.tool_name = spec.name
        self.description = spec.description
        self.required_profile = spec.required_profile
        self._spec = spec

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=0.3,
            response=(
                f"This question is best handled by **{self._spec.agent}**. "
                f"Topic: {self._spec.description}."
            ),
            data_used=[],
            accuracy_score=0.0,
            sources=self._spec.data_sources,
        )


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

_default_router: ToolRouter | None = None


def get_router() -> ToolRouter:
    """Return a module-level singleton ``ToolRouter``."""
    global _default_router
    if _default_router is None:
        _default_router = ToolRouter()
    return _default_router


def route_question(question: str, user_profile: dict) -> dict | list[dict]:
    """One-call shortcut: route a question and get the result(s)."""
    return get_router().route(question, user_profile)
