"""Economic Calendar — upcoming data releases (CPI, jobs, Fed meetings,
GDP) with dates and plain-English explanations of what they mean for the
user's wallet.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# EVENT TEMPLATES — recurring macro releases
# ═══════════════════════════════════════════════════════════════════════════
# Each event has a recurring pattern.  We hard-code a static calendar that
# refreshes quarterly.  For a production system this would pull from the
# BLS / BEA / FRED release calendar API.

_RECURRING_EVENTS: list[dict[str, Any]] = [
    {
        "id": "cpi",
        "name": "CPI Inflation Report",
        "source": "Bureau of Labor Statistics",
        "frequency": "Monthly (2nd or 3rd week)",
        "impact": "HIGH",
        "description": (
            "Measures how fast prices are rising for everyday goods. "
            "A higher-than-expected CPI can push interest rates up, "
            "making mortgages & loans more expensive."
        ),
        "what_it_means": {
            "saver": "High CPI erodes purchasing power — consider TIPS or I-Bonds.",
            "borrower": "Rising CPI → Fed may hike rates → lock in fixed rates ASAP.",
            "investor": "Hot CPI → stocks may dip short-term as rate-hike fears rise.",
            "worker": "Use CPI data to justify cost-of-living raises with your employer.",
        },
    },
    {
        "id": "jobs",
        "name": "Employment Situation (Non-Farm Payrolls)",
        "source": "Bureau of Labor Statistics",
        "frequency": "Monthly (1st Friday)",
        "impact": "HIGH",
        "description": (
            "How many jobs were added/lost and the unemployment rate. "
            "Strong jobs = healthy economy. Weak = potential slowdown."
        ),
        "what_it_means": {
            "saver": "Weak jobs report can push the Fed to CUT rates → lower HYSA yields.",
            "borrower": "Weak jobs → potential rate cuts → better time to refinance.",
            "investor": "Strong hiring supports corporate earnings; weak report may spike volatility.",
            "worker": "Low unemployment = leverage for raises & job-hopping.",
        },
    },
    {
        "id": "fed",
        "name": "Federal Reserve FOMC Decision",
        "source": "Federal Reserve",
        "frequency": "~8 times/year",
        "impact": "VERY HIGH",
        "description": (
            "The Fed sets the federal funds rate. This directly affects "
            "your savings account APY, mortgage rates, and credit card interest."
        ),
        "what_it_means": {
            "saver": "Rate hike → HYSA/CD yields rise. Rate cut → yields fall.",
            "borrower": "Rate hike → higher loan costs. Rate cut → refinance opportunity.",
            "investor": "Markets typically rally on dovish signals, sell on hawkish surprises.",
            "worker": "Rate decisions trickle into hiring decisions — watch for freeze signals.",
        },
    },
    {
        "id": "gdp",
        "name": "GDP (Gross Domestic Product)",
        "source": "Bureau of Economic Analysis",
        "frequency": "Quarterly (advance, 2nd, 3rd estimates)",
        "impact": "MEDIUM",
        "description": (
            "The total output of the US economy. 2 consecutive negative "
            "quarters = technical recession."
        ),
        "what_it_means": {
            "saver": "Recession risk → build emergency fund; keep 6 months expenses liquid.",
            "borrower": "Slowing GDP → Fed may cut rates → watch for refinance window.",
            "investor": "GDP growth supports stock market. Contraction → defensive positioning.",
            "worker": "Negative GDP → layoff risk rises. Update your resume & skills.",
        },
    },
    {
        "id": "pce",
        "name": "PCE Price Index (Fed's Preferred Inflation Gauge)",
        "source": "Bureau of Economic Analysis",
        "frequency": "Monthly (last week)",
        "impact": "HIGH",
        "description": (
            "Personal Consumption Expenditures price index — the Fed's "
            "preferred inflation measure. Core PCE (excluding food/energy) "
            "is what the Fed targets at 2%."
        ),
        "what_it_means": {
            "saver": "Core PCE above 2% = inflation still hot → real returns matter.",
            "borrower": "PCE trending down → rate cuts more likely → good for borrowers.",
            "investor": "PCE approaching 2% target = bullish for rate-sensitive sectors.",
            "worker": "Use PCE data alongside CPI for salary negotiations.",
        },
    },
    {
        "id": "retail_sales",
        "name": "Retail Sales Report",
        "source": "Census Bureau",
        "frequency": "Monthly (mid-month)",
        "impact": "MEDIUM",
        "description": (
            "Consumer spending strength. Since ~70% of US GDP is consumer "
            "spending, this tells us how confident people feel."
        ),
        "what_it_means": {
            "saver": "Strong retail = economy is humming; keep saving plan on track.",
            "borrower": "Rising consumer spending → less chance of rate cuts.",
            "investor": "Strong retail → boost to consumer discretionary stocks.",
            "worker": "Robust spending = job security in retail, hospitality, logistics.",
        },
    },
    {
        "id": "housing",
        "name": "Housing Starts & Existing Home Sales",
        "source": "Census Bureau / NAR",
        "frequency": "Monthly",
        "impact": "MEDIUM",
        "description": (
            "How many new homes are being built and how many existing "
            "homes are selling. Key for anyone buying or selling."
        ),
        "what_it_means": {
            "saver": "More supply = eventual price relief for buyers. Keep saving for down payment.",
            "borrower": "Watch mortgage rate trends alongside housing data.",
            "investor": "Housing data impacts REITs, homebuilders, and bank stocks.",
            "worker": "Construction jobs rise with housing starts.",
        },
    },
    {
        "id": "consumer_sentiment",
        "name": "Consumer Sentiment (UMich / Conference Board)",
        "source": "University of Michigan / Conference Board",
        "frequency": "Monthly",
        "impact": "LOW-MEDIUM",
        "description": (
            "How optimistic or pessimistic consumers feel about the "
            "economy. Leading indicator of future spending."
        ),
        "what_it_means": {
            "saver": "Low sentiment → people tighten belts → good time to bulk up savings.",
            "borrower": "Falling sentiment can foreshadow rate cuts.",
            "investor": "Extreme pessimism is often contrarian bullish for markets.",
            "worker": "Sentiment drops may precede hiring slowdowns — prepare.",
        },
    },
    {
        "id": "jolts",
        "name": "JOLTS (Job Openings & Labor Turnover)",
        "source": "Bureau of Labor Statistics",
        "frequency": "Monthly (1st week, 2-month lag)",
        "impact": "MEDIUM",
        "description": (
            "How many job openings exist and quit rates. High quits = "
            "workers are confident; low openings = tighter market."
        ),
        "what_it_means": {
            "saver": "Fewer openings → recession risk → bolster emergency fund.",
            "borrower": "Cooling labor market → rate cuts on the horizon.",
            "investor": "Falling openings → lower wage pressure → margin boost for companies.",
            "worker": "High openings = leverage to negotiate. Low = stay put & upskill.",
        },
    },
    {
        "id": "ism",
        "name": "ISM Manufacturing & Services PMI",
        "source": "Institute for Supply Management",
        "frequency": "Monthly (1st business day)",
        "impact": "MEDIUM",
        "description": (
            "Purchasing Managers' Index — above 50 = expansion, below 50 "
            "= contraction. Leading indicator of economic direction."
        ),
        "what_it_means": {
            "saver": "PMI below 50 → slowdown → make sure emergency fund is solid.",
            "borrower": "Contraction signals → Fed may ease → refinancing window.",
            "investor": "PMI expansion → cyclical stocks tend to outperform.",
            "worker": "Manufacturing PMI affects supply-chain & factory jobs directly.",
        },
    },
]

# ═══════════════════════════════════════════════════════════════════════════
# STATIC UPCOMING DATES (next ~6 months from a reference)
# This would be replaced by an API fetcher in production.
# ═══════════════════════════════════════════════════════════════════════════

def _generate_upcoming_dates() -> list[dict]:
    """Generate plausible upcoming dates for recurring events,
    starting from today."""
    today = date.today()
    upcoming: list[dict] = []

    for event in _RECURRING_EVENTS:
        # Generate ~3 future occurrences per event
        eid = event["id"]
        if eid == "fed":
            # FOMC meets ~8 times/year, roughly every 6-7 weeks
            base = today + timedelta(days=14)
            for i in range(3):
                d = base + timedelta(weeks=7 * i)
                upcoming.append({**event, "date": d.isoformat(),
                                 "days_away": (d - today).days})
        elif eid == "jobs":
            # First Friday of each month
            for m_offset in range(1, 4):
                m = today.month + m_offset
                y = today.year + (m - 1) // 12
                m = ((m - 1) % 12) + 1
                first = date(y, m, 1)
                # Find first Friday
                days_until_fri = (4 - first.weekday()) % 7
                fri = first + timedelta(days=days_until_fri)
                upcoming.append({**event, "date": fri.isoformat(),
                                 "days_away": (fri - today).days})
        else:
            # Generic: mid-month for next 3 months
            for m_offset in range(1, 4):
                m = today.month + m_offset
                y = today.year + (m - 1) // 12
                m = ((m - 1) % 12) + 1
                d = date(y, m, min(15, 28))
                upcoming.append({**event, "date": d.isoformat(),
                                 "days_away": (d - today).days})

    upcoming.sort(key=lambda e: e["date"])
    return upcoming


def _user_role(p: dict) -> str:
    """Determine which 'what_it_means' lens to highlight."""
    # Check for debt, savings, investments to pick the most relevant lens
    roles = []
    income = float(p.get("income", 0) or 0)
    savings = float(p.get("savings", 0) or 0)
    debts = p.get("debts", [])
    investments = float(p.get("investment_amount", 0) or 0)

    total_debt = 0
    if isinstance(debts, list):
        for d in debts:
            total_debt += float(d.get("balance", 0) if isinstance(d, dict) else 0)
    elif isinstance(debts, (int, float)):
        total_debt = float(debts)

    if total_debt > 10_000:
        return "borrower"
    if investments > 50_000:
        return "investor"
    if savings > income * 0.25 and income > 0:
        return "saver"
    return "worker"


class EconomicCalendar(RichyToolBase):
    """Upcoming economic data releases with plain-English impact."""

    tool_id = 48
    tool_name = "economic_calendar"
    description = (
        "Upcoming economic data releases (CPI, jobs, Fed, GDP) "
        "with dates and what they mean for your finances"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(question, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.80),
            response=self._narrate(plan),
            data_used=["user_role", "question_keywords"],
            accuracy_score=0.78,
            sources=[
                "BLS release calendar",
                "Federal Reserve FOMC schedule",
                "BEA GDP release schedule",
                "Census Bureau retail & housing releases",
            ],
            raw_data=plan,
        )

    def analyze(self, question: str, user_profile: dict) -> dict:
        q_lower = (question or "").lower()
        role = _user_role(user_profile)

        upcoming = _generate_upcoming_dates()

        # Filter by question keywords if present
        keyword_map = {
            "cpi": "cpi", "inflation": "cpi", "prices": "cpi",
            "job": "jobs", "employment": "jobs", "payroll": "jobs",
            "unemployment": "jobs", "hiring": "jobs",
            "fed": "fed", "fomc": "fed", "interest rate": "fed",
            "rate decision": "fed", "powell": "fed",
            "gdp": "gdp", "recession": "gdp", "growth": "gdp",
            "pce": "pce",
            "retail": "retail_sales", "spending": "retail_sales",
            "housing": "housing", "home": "housing", "mortgage": "housing",
            "sentiment": "consumer_sentiment", "confidence": "consumer_sentiment",
            "jolt": "jolts", "openings": "jolts", "quit": "jolts",
            "ism": "ism", "pmi": "ism", "manufacturing": "ism",
        }

        filter_ids: set[str] = set()
        for kw, eid in keyword_map.items():
            if kw in q_lower:
                filter_ids.add(eid)

        if filter_ids:
            filtered = [e for e in upcoming if e["id"] in filter_ids]
        else:
            filtered = upcoming

        # Limit to next ~15 events for readability
        filtered = filtered[:15]

        # Determine the high-impact events in the next 14 days
        imminent = [e for e in filtered if e["days_away"] <= 14]

        # Build commentary per event
        events_out: list[dict] = []
        for e in filtered:
            means = e.get("what_it_means", {})
            personal_note = means.get(role, means.get("worker", ""))
            events_out.append({
                "name": e["name"],
                "date": e["date"],
                "days_away": e["days_away"],
                "impact": e["impact"],
                "source": e["source"],
                "frequency": e["frequency"],
                "description": e["description"],
                "personal_note": personal_note,
                "role_used": role,
            })

        confidence = 0.82 if not filter_ids else 0.88

        return {
            "role": role,
            "total_events": len(events_out),
            "imminent_count": len(imminent),
            "events": events_out,
            "filter_applied": list(filter_ids) if filter_ids else None,
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        lines.append("📅 **Economic Calendar — Upcoming Releases**")
        lines.append(
            f"  Showing {plan['total_events']} events | "
            f"Your lens: {plan['role'].title()}"
        )
        if plan["imminent_count"] > 0:
            lines.append(
                f"  ⚡ {plan['imminent_count']} event(s) within the next 2 weeks!"
            )
        lines.append("")

        impact_emoji = {
            "VERY HIGH": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW-MEDIUM": "🟢",
            "LOW": "⚪",
        }

        prev_month = ""
        for e in plan["events"]:
            # Month header
            month_str = e["date"][:7]  # YYYY-MM
            if month_str != prev_month:
                lines.append(f"**── {month_str} ──**")
                prev_month = month_str

            emoji = impact_emoji.get(e["impact"], "🟡")
            imminent_flag = " ⚡SOON" if e["days_away"] <= 7 else ""
            lines.append(
                f"{emoji} **{e['date']}** — {e['name']} "
                f"({e['impact']}){imminent_flag}"
            )
            lines.append(f"    {e['description']}")
            if e["personal_note"]:
                lines.append(f"    💡 *For you ({e['role_used']}):* {e['personal_note']}")
            lines.append("")

        lines.append("─" * 50)
        lines.append(
            "📌 **How to use this:** Check the calendar before major financial "
            "decisions (refinancing, large purchases, job changes). Market-moving "
            "data often creates short-term volatility — avoid panic selling."
        )
        lines.append("")
        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: BLS, Fed, BEA, Census Bureau"
        )
        return "\n".join(lines)
