"""Kid Coach — age-appropriate financial guidance for kids 4-17
and their parents.

Four age tiers with tailored lesson plans, allowance benchmarks,
savings projections, and parent action items.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# ── Average weekly allowance by age (RoosterMoney / BusyKid surveys) ─────
_AVG_ALLOWANCE: dict[int, float] = {
    4:  2.50,   5:  3.00,   6:  3.50,   7:  4.00,
    8:  5.00,   9:  5.50,  10:  6.50,  11:  7.50,
    12:  9.00,  13: 10.00,  14: 11.50,  15: 13.00,
    16: 15.00,  17: 17.00,
}

# ── Federal youth employment ─────────────────────────────────────────────
_FEDERAL_MIN_WAGE = 7.25
_TEEN_EMPLOYMENT_RATE = 0.336      # BLS 2024: 33.6% of 16-19 employed
_MIN_WORKING_AGE_FEDERAL = 14     # with restrictions
_MIN_WORKING_AGE_FULL = 16        # broader hours

# ── UGMA / UTMA / Kiddie Tax (2025) ──────────────────────────────────────
_UGMA_GIFT_ANNUAL = 18_000         # annual exclusion per donor
_KIDDIE_TAX_UNEARNED_STD = 1_300   # child's standard deduction on unearned
_KIDDIE_TAX_THRESHOLD = 2_600      # above this → parent's marginal rate
_CHILD_STANDARD_DEDUCTION_EARNED = 14_600  # or earned income + $450

# ── Roth IRA for minors ──────────────────────────────────────────────────
_ROTH_LIMIT = 7_000
_ROTH_NOTE = (
    "Teens with earned income can open a Custodial Roth IRA. "
    "Contributions up to their earned income (max $7,000). "
    "Tax-free growth for 50+ years is incredibly powerful."
)

# ── College cost preview (College Board 2024-25) ─────────────────────────
_COLLEGE_COSTS: dict[str, dict] = {
    "public_in_state":  {"tuition": 11_610, "room_board": 12_600, "total": 24_210},
    "public_out_state": {"tuition": 23_940, "room_board": 12_600, "total": 36_540},
    "private":          {"tuition": 43_350, "room_board": 14_400, "total": 57_750},
}
_COLLEGE_INFLATION = 0.04  # ~4% annual increase

# ── Car cost reality check ───────────────────────────────────────────────
_FIRST_CAR: dict[str, float] = {
    "purchase_used":       8_500,
    "insurance_annual":    2_400,   # teen driver surcharge
    "gas_monthly":         120,
    "maintenance_annual":  800,
    "total_first_year":    14_140,
    "monthly_cost":        round(14_140 / 12, 2),
}

# ── Compound interest teaching examples ──────────────────────────────────
_COMPOUND_EXAMPLES: list[dict] = [
    {
        "label": "Save $5/week from age 10",
        "weekly": 5, "start_age": 10, "end_age": 18,
        "rate": 0.045, "result": None,  # calculated
    },
    {
        "label": "Save $10/week from age 13",
        "weekly": 10, "start_age": 13, "end_age": 18,
        "rate": 0.045, "result": None,
    },
    {
        "label": "$1,000 in a Roth IRA at 16, untouched to 65",
        "lump": 1_000, "start_age": 16, "end_age": 65,
        "rate": 0.10, "result": None,   # ~$117K
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# TIER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

def _tier_4_7(age: int, allowance: float, has_savings: bool) -> dict:
    """Ages 4-7: Three-jar system, simple goals, visual trackers."""
    avg = _AVG_ALLOWANCE.get(age, 3.50)
    suggested = round(avg, 2)

    # Savings projection: save 1/3 of allowance weekly for a year
    save_weekly = suggested / 3
    annual_savings = save_weekly * 52

    lesson_plan = [
        {
            "lesson": "🏦 Three-Jar System",
            "description": (
                "Get three clear jars labeled SPEND, SAVE, GIVE. "
                "Every time you get money, split it into thirds."
            ),
            "activity": (
                f"Put ${suggested / 3:.2f} in each jar every week. "
                "Watch the SAVE jar grow!"
            ),
        },
        {
            "lesson": "🎯 Goal Setting",
            "description": (
                "Pick something you want that costs $10-$30. "
                "Draw a picture of it and tape it to your SAVE jar."
            ),
            "activity": (
                "Color in a bar chart each week as you get closer. "
                f"At ${save_weekly:.2f}/week, a $20 toy takes "
                f"~{math.ceil(20 / save_weekly)} weeks!"
            ),
        },
        {
            "lesson": "💰 Coins & Bills",
            "description": (
                "Learn what each coin is worth. Play store with "
                "real or play money — practice making change."
            ),
            "activity": "Sort a jar of coins and count the total together.",
        },
        {
            "lesson": "🤝 Giving Back",
            "description": (
                "The GIVE jar helps others. Pick a cause your child "
                "cares about — animals, friends, a toy drive."
            ),
            "activity": "Let them hand the donation personally so it feels real.",
        },
    ]

    parent_tips = [
        "Use clear jars so they can SEE the money grow — visual > digital at this age.",
        f"${suggested:.2f}/week is age-appropriate. Tie some to small chores for work→money connection.",
        "Grocery shopping is a goldmine: 'We have $5 for snacks — what should we pick?'",
        "Avoid bailing out impulse buys — let small mistakes happen now when stakes are low.",
        "Praise saving decisions: 'You waited and now you can afford it! That was so smart.'",
    ]

    next_milestone = {
        "age": 8,
        "milestone": "Open their first savings account (many banks allow at 8 with a parent).",
        "preview": "At 8, they'll learn the 50/30/20 rule and start tracking spending.",
    }

    return {
        "age_group": "4-7 (Little Learners)",
        "tier": "little_learners",
        "allowance_recommendation": {
            "suggested_weekly": suggested,
            "average_for_age": avg,
            "structure": "Split into three jars: Spend / Save / Give",
        },
        "lesson_plan": lesson_plan,
        "savings_projection": {
            "weekly_savings": round(save_weekly, 2),
            "annual_total": round(annual_savings, 2),
            "note": f"Saving just ${save_weekly:.2f}/week = ${annual_savings:.2f} by year end!",
        },
        "parent_tips": parent_tips,
        "next_milestone": next_milestone,
    }


def _tier_8_12(age: int, allowance: float, has_savings: bool) -> dict:
    """Ages 8-12: 50/30/20 budget, compound interest intro, parent match."""
    avg = _AVG_ALLOWANCE.get(age, 6.50)
    suggested = round(avg, 2)

    # 50/30/20 breakdown
    needs = round(suggested * 0.50, 2)
    wants = round(suggested * 0.30, 2)
    savings = round(suggested * 0.20, 2)

    # Compound interest demo: save $savings/week for years until 18
    years = 18 - age
    weekly_save = savings
    annual_save = weekly_save * 52
    rate = 0.045  # HYSA rate
    # Future value of annuity
    total_saved = 0.0
    for y in range(years):
        total_saved = (total_saved + annual_save) * (1 + rate)
    interest_earned = total_saved - (annual_save * years)

    lesson_plan = [
        {
            "lesson": "📊 The 50/30/20 Rule (Kid Version)",
            "description": (
                f"From your ${suggested:.2f}/week:\n"
                f"  • 50% NEEDS (${needs:.2f}) — school supplies, lunch extras\n"
                f"  • 30% WANTS (${wants:.2f}) — games, treats, fun stuff\n"
                f"  • 20% SAVINGS (${savings:.2f}) — future goals"
            ),
            "activity": (
                "Track spending for 2 weeks in a notebook or app. "
                "Categorize each purchase."
            ),
        },
        {
            "lesson": "📈 Compound Interest (Money Making Money)",
            "description": (
                "When you put money in a savings account, the bank pays YOU "
                "for keeping it there. Then you earn interest on your interest!"
            ),
            "activity": (
                f"If you save ${weekly_save:.2f}/week in a savings account "
                f"earning 4.5%, in {years} years you'll have "
                f"${total_saved:,.2f} — that's ${interest_earned:,.2f} "
                f"the bank paid YOU just for saving!"
            ),
        },
        {
            "lesson": "🎯 SMART Goals",
            "description": (
                "Specific, Measurable, Achievable, Relevant, Time-bound. "
                "Example: 'Save $50 for a video game by my birthday.'"
            ),
            "activity": "Write down 3 savings goals with dollar amounts and deadlines.",
        },
        {
            "lesson": "🏷️ Needs vs Wants",
            "description": (
                "A NEED is something you must have (food, clothes for school). "
                "A WANT is something nice to have (new headphones, candy)."
            ),
            "activity": "Cut out magazine/online pictures — sort into Needs vs Wants columns.",
        },
        {
            "lesson": "🛒 Comparison Shopping",
            "description": (
                "Before buying, check 2-3 places. Same toy can cost "
                "very different amounts!"
            ),
            "activity": "Pick an item you want — look up the price in 3 stores or websites.",
        },
    ]

    parent_tips = [
        f"${suggested:.2f}/week is the average for age {age}. Consider tying part to responsibilities.",
        "**Parent savings match**: Match what they save 1:1 — it teaches investing concepts and motivates saving.",
        "Open a real savings account in their name. Seeing a bank balance builds financial identity.",
        "Let them make purchasing mistakes under $20. The lesson sticks better than a lecture.",
        "Start showing them grocery receipts — 'Our family spent $X on food this week.'",
        "Consider apps like Greenlight or FamZoo for digital allowance tracking.",
    ]

    next_milestone = {
        "age": 13,
        "milestone": "Set up a checking account, explore real earning opportunities.",
        "preview": "At 13, they can start lawn care, babysitting, or online gigs.",
    }

    return {
        "age_group": "8-12 (Money Managers)",
        "tier": "money_managers",
        "allowance_recommendation": {
            "suggested_weekly": suggested,
            "average_for_age": avg,
            "structure": f"50/30/20: ${needs:.2f} needs / ${wants:.2f} wants / ${savings:.2f} savings",
        },
        "lesson_plan": lesson_plan,
        "savings_projection": {
            "weekly_savings": round(weekly_save, 2),
            "annual_total": round(annual_save, 2),
            "projected_at_18": round(total_saved, 2),
            "interest_earned": round(interest_earned, 2),
            "note": (
                f"${weekly_save:.2f}/week × {years} years + 4.5% interest = "
                f"${total_saved:,.2f}. The earlier they start, the more "
                f"compound interest works for them!"
            ),
        },
        "parent_match_suggestion": {
            "match_rate": "1:1",
            "explanation": (
                f"If they save ${savings:.2f}/week and you match it, "
                f"that doubles to ${savings * 2:.2f}/week — "
                f"${savings * 2 * 52:,.2f}/year. Teaches them about "
                f"employer matching in 401(k) later."
            ),
        },
        "parent_tips": parent_tips,
        "next_milestone": next_milestone,
    }


def _tier_13_15(age: int, allowance: float, has_savings: bool, has_earnings: bool) -> dict:
    """Ages 13-15: Bank accounts, earning, investing concepts, TVM."""
    avg = _AVG_ALLOWANCE.get(age, 11.50)
    suggested = round(avg, 2)

    # Earning opportunities
    earning_ideas = [
        {"gig": "Lawn mowing / yard work",     "est_hourly": "$15-25", "note": "Neighborhood demand is high spring-fall"},
        {"gig": "Babysitting",                  "est_hourly": "$12-20", "note": "Red Cross babysitting cert adds credibility"},
        {"gig": "Pet sitting / dog walking",    "est_hourly": "$10-20", "note": "Rover allows 18+ but local clients work"},
        {"gig": "Tutoring younger kids",        "est_hourly": "$15-25", "note": "Math and reading are most in demand"},
        {"gig": "Car washing / detailing",      "est_hourly": "$15-30", "note": "Mobile detailing has high margins"},
        {"gig": "Social media help for local biz","est_hourly": "$10-20", "note": "Small businesses need content creators"},
        {"gig": "Reselling (thrift flips)",     "est_hourly": "Varies", "note": "Buy low at thrift stores, sell on Mercari/eBay"},
    ]

    # Time-value-of-money projection
    # If they earn $100/month from gigs and save 50%:
    monthly_save = 50
    years_to_18 = 18 - age
    rate = 0.045
    total = 0.0
    for y in range(years_to_18):
        total = (total + monthly_save * 12) * (1 + rate)
    contributed = monthly_save * 12 * years_to_18
    growth = total - contributed

    # Long-term Roth projection: $1,000 at 15, untouched to 65
    roth_years = 65 - age
    roth_1k = 1_000 * (1.10 ** roth_years)

    lesson_plan = [
        {
            "lesson": "🏦 Bank Account Setup",
            "description": (
                "Open a student checking and savings account. "
                "Most banks offer fee-free accounts for teens with a parent co-signer."
            ),
            "activity": (
                "Compare 3 banks/credit unions: look at fees, interest rate, "
                "app quality, and ATM access. YOU pick the best one."
            ),
        },
        {
            "lesson": "💼 Earning Your Own Money",
            "description": (
                f"At {age}, you can earn real money! Average teen workers make "
                f"${_FEDERAL_MIN_WAGE}-$15/hour depending on location."
            ),
            "activity": "Pick 2 earning ideas from the list and try one this month.",
            "earning_ideas": earning_ideas,
        },
        {
            "lesson": "⏳ Time Value of Money",
            "description": (
                "$1 today is worth more than $1 tomorrow because you can "
                "invest it and earn returns. Starting at your age gives you "
                "a MASSIVE advantage."
            ),
            "activity": (
                f"$1,000 invested at age {age} at 10% average stock returns "
                f"grows to ${roth_1k:,.0f} by age 65 — without adding "
                f"another penny. That's the power of time."
            ),
        },
        {
            "lesson": "📊 Intro to Investing",
            "description": (
                "Stocks = owning a tiny piece of a company. "
                "When the company does well, your piece grows. "
                "An index fund owns hundreds of companies at once — way safer."
            ),
            "activity": (
                "Pick 3 companies you use (Apple, Nike, Netflix). "
                "Look up their stock price. Check again in a month."
            ),
        },
        {
            "lesson": "🧮 Opportunity Cost",
            "description": (
                "Every dollar spent is a dollar that can't be saved or invested. "
                "That $60 game could be $600 in 10 years if invested."
            ),
            "activity": (
                "Before your next purchase over $20, calculate what it "
                "would be worth in 10 years at 10% growth."
            ),
        },
    ]

    parent_tips = [
        "Help them open a real bank account — this is a milestone that builds financial identity.",
        f"Encourage earning: {_TEEN_EMPLOYMENT_RATE * 100:.0f}% of 16-19 year olds work. Starting at {age} builds ahead.",
        "**Custodial Roth IRA**: If they have earned income, open one NOW. Time is their superpower.",
        f"${roth_1k:,.0f} — that's what $1,000 invested at age {age} becomes by 65 at 10% returns. Show them.",
        "Let them negotiate prices (yard work, babysitting). Sales skills = life skills.",
        "UGMA/UTMA account: You can gift up to $18,000/year tax-free for their investments.",
    ]

    next_milestone = {
        "age": 16,
        "milestone": "First real job (W-2), learn about taxes, open a Roth IRA if earned income.",
        "preview": "At 16, they'll learn tax basics, car costs, and start serious retirement investing.",
    }

    return {
        "age_group": "13-15 (Young Entrepreneurs)",
        "tier": "young_entrepreneurs",
        "allowance_recommendation": {
            "suggested_weekly": suggested,
            "average_for_age": avg,
            "structure": (
                "Transition from pure allowance to earning-based. "
                "Base allowance + earning opportunities."
            ),
        },
        "earning_opportunities": earning_ideas,
        "lesson_plan": lesson_plan,
        "savings_projection": {
            "monthly_savings": monthly_save,
            "projected_at_18": round(total, 2),
            "total_contributed": round(contributed, 2),
            "interest_earned": round(growth, 2),
            "roth_example": {
                "invested_at_age": age,
                "amount": 1_000,
                "value_at_65": round(roth_1k, 2),
                "growth_multiple": f"{roth_1k / 1_000:.0f}x",
            },
            "note": (
                f"Saving $50/month from gigs: ${total:,.2f} by 18. "
                f"Plus: $1,000 in a Roth at {age} → ${roth_1k:,.0f} at 65!"
            ),
        },
        "parent_tips": parent_tips,
        "next_milestone": next_milestone,
    }


def _tier_16_17(age: int, allowance: float, has_earnings: bool, income: float) -> dict:
    """Ages 16-17: First job, taxes, Roth IRA, car costs, college preview."""
    avg = _AVG_ALLOWANCE.get(age, 16.00)

    # First-job tax basics
    # Teens earning under standard deduction owe $0 federal
    std_deduction = _CHILD_STANDARD_DEDUCTION_EARNED
    fica_rate = 0.0765
    tax_example_income = 8_000  # typical part-time annual
    fica_tax = round(tax_example_income * fica_rate, 2)

    # Roth IRA projection: max $7,000 at 16, let it grow
    roth_years = 65 - age
    roth_max = min(income, _ROTH_LIMIT) if income > 0 else _ROTH_LIMIT
    roth_future = roth_max * (1.10 ** roth_years)

    # College cost projection
    years_to_college = 18 - age
    college_costs_adj: dict[str, dict] = {}
    for ctype, data in _COLLEGE_COSTS.items():
        factor = (1 + _COLLEGE_INFLATION) ** years_to_college
        annual = round(data["total"] * factor, 2)
        four_year = round(annual * 4, 2)
        college_costs_adj[ctype] = {
            "annual": annual,
            "four_year": four_year,
            "label": ctype.replace("_", " ").title(),
        }

    lesson_plan = [
        {
            "lesson": "💼 First Job Guide",
            "description": (
                f"At {age}, you can work more hours and earn real income. "
                f"Avg teen earns $8-15/hour. Federal minimum: ${_FEDERAL_MIN_WAGE:.2f}."
            ),
            "activity": (
                "Fill out a W-4 (you'll likely claim exempt if earning "
                f"under ${std_deduction:,.0f}). Set up direct deposit "
                "with 10% auto-transferred to savings."
            ),
        },
        {
            "lesson": "🧾 Tax Basics for Teens",
            "description": (
                f"If you earn under ${std_deduction:,.0f}, you owe $0 in federal "
                f"income tax. But you still pay FICA (Social Security + Medicare): "
                f"7.65% of every paycheck.\n\n"
                f"Example: Earn ${tax_example_income:,.0f}/year → "
                f"FICA tax = ${fica_tax:,.2f} (~${fica_tax / 12:,.0f}/month)"
            ),
            "activity": "Read your first pay stub. Find gross pay, FICA, net pay.",
        },
        {
            "lesson": "🏦 Custodial Roth IRA",
            "description": _ROTH_NOTE,
            "activity": (
                f"If you earn ${income:,.0f} this year, you can contribute up to "
                f"${roth_max:,.0f} to a Roth IRA.\n"
                f"That ${roth_max:,.0f} could become ${roth_future:,.0f} by age 65 "
                f"at 10% average returns — tax-free!"
            ),
        },
        {
            "lesson": "🚗 Car Cost Reality Check",
            "description": (
                "A car isn't just the purchase price. Here's the real first-year cost:"
            ),
            "breakdown": _FIRST_CAR,
            "activity": (
                f"Total first-year cost: ~${_FIRST_CAR['total_first_year']:,.0f} "
                f"(${_FIRST_CAR['monthly_cost']:,.0f}/month). "
                f"At ${_FEDERAL_MIN_WAGE:.2f}/hr, that's "
                f"~{_FIRST_CAR['total_first_year'] / _FEDERAL_MIN_WAGE:.0f} "
                f"hours of work. Worth it? Maybe — but go in eyes open."
            ),
        },
        {
            "lesson": "🎓 College Cost Preview",
            "description": "Here's what 4 years of college will cost when you get there:",
            "college_costs": college_costs_adj,
            "activity": (
                "Explore scholarships NOW. Every $1,000 in scholarships = "
                "$1,000 less in student loans. Start with local community "
                "scholarships — less competition."
            ),
        },
        {
            "lesson": "💳 Credit Score Preview",
            "description": (
                "At 18, your credit journey begins. A good score (700+) "
                "saves you tens of thousands on car loans, apartments, "
                "and eventually a mortgage. Start with an authorized user "
                "on a parent's card NOW."
            ),
            "activity": (
                "Ask a parent to add you as an authorized user on their "
                "oldest credit card. You get their history on your report."
            ),
        },
    ]

    parent_tips = [
        f"**Open a Custodial Roth IRA immediately** if they have earned income. ${roth_max:,.0f} now → ${roth_future:,.0f} at 65.",
        "Match their Roth contributions — they earn $3,000, you gift $3,000 for the Roth. Life-changing.",
        "Add them as an authorized user on your oldest credit card (good history only!).",
        "Discuss car costs BEFORE they get their license. Set expectations on who pays what.",
        "Start the college financial conversation early: 'Here's our budget. Here's what scholarships could cover.'",
        f"Teens earning under ${std_deduction:,.0f} pay no federal income tax — but file anyway for the record.",
        "Teach them to negotiate pay. Moving from $10→$12/hour at 20hrs/week = $2,080 more per year.",
    ]

    next_milestone = {
        "age": 18,
        "milestone": "Financial independence transition: own bank accounts, credit card, budgeting for college/work.",
        "preview": "At 18, they graduate to the adult financial toolkit. The foundation you built here matters enormously.",
    }

    return {
        "age_group": "16-17 (Future Adults)",
        "tier": "future_adults",
        "allowance_recommendation": {
            "suggested_weekly": round(avg, 2),
            "average_for_age": avg,
            "structure": (
                "Shift to earned income. Allowance should phase out as "
                "they earn from a job. Redirect to covering their own expenses."
            ),
        },
        "first_job": {
            "min_wage": _FEDERAL_MIN_WAGE,
            "teen_employment_rate": f"{_TEEN_EMPLOYMENT_RATE * 100:.0f}%",
            "tax_basics": {
                "standard_deduction": std_deduction,
                "fica_rate": f"{fica_rate * 100:.1f}%",
                "example_income": tax_example_income,
                "example_fica": fica_tax,
                "note": f"Earn under ${std_deduction:,} = $0 federal income tax. FICA still applies.",
            },
        },
        "roth_ira": {
            "eligible": has_earnings or income > 0,
            "max_contribution": roth_max,
            "projected_value_at_65": round(roth_future, 2),
            "years_of_growth": roth_years,
            "note": _ROTH_NOTE,
        },
        "car_costs": _FIRST_CAR,
        "college_preview": college_costs_adj,
        "lesson_plan": lesson_plan,
        "savings_projection": {
            "roth_example": {
                "invested_at_age": age,
                "amount": roth_max,
                "value_at_65": round(roth_future, 2),
                "growth_multiple": f"{roth_future / max(roth_max, 1):.0f}x",
            },
        },
        "parent_tips": parent_tips,
        "next_milestone": next_milestone,
    }


# ═══════════════════════════════════════════════════════════════════════════
# KID COACH TOOL
# ═══════════════════════════════════════════════════════════════════════════

class KidCoach(RichyToolBase):
    """Age-appropriate financial guidance for kids 4-17 and their parents.

    Routes to one of four age tiers, each with tailored lessons,
    allowance benchmarks, savings projections, and parent actions.
    """

    tool_id = 6
    tool_name = "kid_coach"
    description = (
        "Youth financial education: allowance advice, savings plans, "
        "earning ideas, investing intro, and parent action items — "
        "adaptive for ages 4-17"
    )
    required_profile: list[str] = []

    # ── Router entry ──────────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.88),
            response=self._narrate(plan),
            data_used=[
                "child_age", "allowance", "has_savings_account",
                "has_earnings", "topic",
            ],
            accuracy_score=0.87,
            sources=[
                "RoosterMoney / BusyKid allowance surveys",
                "BLS teen employment statistics 2024",
                "IRS Publication 929 (Kiddie Tax)",
                "College Board Trends in College Pricing 2024-25",
                "Vanguard compound growth projections",
            ],
            raw_data=plan,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════

    def analyze(self, user_profile: dict) -> dict:
        """Route to the appropriate age tier and build guidance.

        Keys in ``user_profile``:
            child_age:          int (4-17)
            parent_income_tier: str ("low" | "middle" | "high") — optional
            current_allowance:  float (weekly) — optional
            has_savings_account: bool
            has_earnings:       bool
            topic:              str — optional focus area
            income:             float — teen's annual earned income (16-17)
        """
        age = int(user_profile.get("child_age", 10) or 10)
        age = max(4, min(age, 17))
        allowance = float(user_profile.get("current_allowance", 0) or 0)
        has_savings = bool(user_profile.get("has_savings_account", False))
        has_earnings = bool(user_profile.get("has_earnings", False))
        teen_income = float(user_profile.get("income", 0) or 0)
        topic = (user_profile.get("topic", "") or "").lower()

        # Route to tier
        if age <= 7:
            tier_data = _tier_4_7(age, allowance, has_savings)
        elif age <= 12:
            tier_data = _tier_8_12(age, allowance, has_savings)
        elif age <= 15:
            tier_data = _tier_13_15(age, allowance, has_savings, has_earnings)
        else:
            tier_data = _tier_16_17(age, allowance, has_earnings, teen_income)

        # UGMA / UTMA info
        tier_data["ugma_utma"] = {
            "annual_gift_exclusion": _UGMA_GIFT_ANNUAL,
            "kiddie_tax_threshold": _KIDDIE_TAX_THRESHOLD,
            "note": (
                f"Parents can gift up to ${_UGMA_GIFT_ANNUAL:,}/year per child "
                f"without gift tax via UGMA/UTMA. First ${_KIDDIE_TAX_UNEARNED_STD:,} "
                f"of unearned income is tax-free; ${_KIDDIE_TAX_UNEARNED_STD:,}-"
                f"${_KIDDIE_TAX_THRESHOLD:,} taxed at child's rate; above "
                f"${_KIDDIE_TAX_THRESHOLD:,} at parent's rate."
            ),
        }

        # Confidence
        filled = sum(1 for v in [age, allowance, has_savings, has_earnings] if v)
        confidence = min(0.78 + filled * 0.04, 0.92)
        tier_data["confidence"] = round(confidence, 2)
        tier_data["child_age"] = age

        return tier_data

    # ═══════════════════════════════════════════════════════════════════════
    # NARRATION
    # ═══════════════════════════════════════════════════════════════════════

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        age = plan.get("child_age", 10)
        tier = plan.get("tier", "")

        # ── Header ────────────────────────────────────────────────────────
        emoji_map = {
            "little_learners": "🧒",
            "money_managers": "📊",
            "young_entrepreneurs": "💼",
            "future_adults": "🎓",
        }
        emoji = emoji_map.get(tier, "👦")
        lines.append(
            f"{emoji} **Kid Coach** — Age {age} | "
            f"**{plan.get('age_group', '')}**"
        )
        lines.append("")

        # ── Allowance ─────────────────────────────────────────────────────
        ar = plan.get("allowance_recommendation", {})
        if ar:
            lines.append("**Allowance recommendation:**")
            lines.append(f"  Suggested: ${ar.get('suggested_weekly', 0):.2f}/week")
            lines.append(f"  Average for age {age}: ${ar.get('average_for_age', 0):.2f}/week")
            lines.append(f"  Structure: {ar.get('structure', '')}")
            lines.append("")

        # ── Lesson plan ───────────────────────────────────────────────────
        lessons = plan.get("lesson_plan", [])
        if lessons:
            lines.append(f"**Lesson plan ({len(lessons)} lessons):**")
            for i, les in enumerate(lessons, 1):
                lines.append(f"  {les.get('lesson', f'Lesson {i}')}")
                lines.append(f"    {les['description']}")
                if les.get("activity"):
                    lines.append(f"    ✏️ Activity: {les['activity']}")

                # Earning ideas (13-15 tier)
                if les.get("earning_ideas"):
                    lines.append("    💰 Earning ideas:")
                    for idea in les["earning_ideas"][:5]:
                        lines.append(
                            f"      • {idea['gig']} ({idea['est_hourly']}/hr)"
                        )

                # Car costs (16-17 tier)
                if les.get("breakdown"):
                    bd = les["breakdown"]
                    lines.append(
                        f"    🚗 Purchase: ${bd.get('purchase_used', 0):,.0f} | "
                        f"Insurance: ${bd.get('insurance_annual', 0):,.0f}/yr | "
                        f"Gas: ${bd.get('gas_monthly', 0):,.0f}/mo | "
                        f"Total yr 1: ${bd.get('total_first_year', 0):,.0f}"
                    )

                # College costs (16-17 tier)
                if les.get("college_costs"):
                    lines.append("    🎓 4-year college costs (projected):")
                    for ctype, data in les["college_costs"].items():
                        lines.append(
                            f"      {data['label']}: "
                            f"{self.fmt_currency(data['four_year'])}"
                        )

                lines.append("")

        # ── Savings projection ────────────────────────────────────────────
        sp = plan.get("savings_projection", {})
        if sp.get("note"):
            lines.append("**Savings projection:**")
            lines.append(f"  {sp['note']}")
            if sp.get("roth_example"):
                re = sp["roth_example"]
                lines.append(
                    f"  🏦 Roth IRA: ${re['amount']:,.0f} at age {re['invested_at_age']} "
                    f"→ {self.fmt_currency(re['value_at_65'])} at 65 "
                    f"({re['growth_multiple']} growth!)"
                )
            lines.append("")

        # ── Parent match (8-12) ───────────────────────────────────────────
        pm = plan.get("parent_match_suggestion", {})
        if pm:
            lines.append("**Parent savings match:**")
            lines.append(f"  {pm['explanation']}")
            lines.append("")

        # ── Roth IRA (16-17) ──────────────────────────────────────────────
        roth = plan.get("roth_ira", {})
        if roth and roth.get("eligible"):
            lines.append("**🏦 Roth IRA opportunity:**")
            lines.append(
                f"  Max contribution: {self.fmt_currency(roth['max_contribution'])}"
            )
            lines.append(
                f"  Projected at 65: {self.fmt_currency(roth['projected_value_at_65'])} "
                f"({roth['years_of_growth']} years of tax-free growth)"
            )
            lines.append(f"  {roth['note']}")
            lines.append("")

        # ── Parent tips ───────────────────────────────────────────────────
        tips = plan.get("parent_tips", [])
        if tips:
            lines.append("**👨‍👩‍👧 Tips for parents:**")
            for tip in tips:
                lines.append(f"  • {tip}")
            lines.append("")

        # ── UGMA/UTMA ────────────────────────────────────────────────────
        ugma = plan.get("ugma_utma", {})
        if ugma.get("note"):
            lines.append(f"**📋 UGMA/UTMA:** {ugma['note']}")
            lines.append("")

        # ── Next milestone ────────────────────────────────────────────────
        nm = plan.get("next_milestone", {})
        if nm:
            lines.append(
                f"**🎯 Next milestone (age {nm['age']}):** "
                f"{nm['milestone']}"
            )
            lines.append(f"  {nm['preview']}")
            lines.append("")

        # ── Confidence ────────────────────────────────────────────────────
        lines.append(
            f"Confidence: {plan.get('confidence', 0.85):.0%} | "
            f"Sources: BLS, IRS Pub 929, College Board, "
            f"RoosterMoney surveys"
        )

        return "\n".join(lines)
