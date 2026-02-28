"""Side Hustle Ideas — based on skills, hours, market.
Realistic hourly rate AFTER expenses. Startup costs.
Tax warning for SE tax. Link to Tax Estimator.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# SIDE HUSTLE DATABASE
# ═══════════════════════════════════════════════════════════════════════════

# SE tax rate (Social Security + Medicare for self-employed)
_SE_TAX_RATE = 0.153   # 15.3%
_SE_TAX_DEDUCTION = 0.5  # 50% of SE tax deductible
_QUARTERLY_TAX_WARNING = (
    "⚠️ As self-employment income, you must pay estimated taxes quarterly "
    "(April 15, June 15, Sep 15, Jan 15). Failure to pay quarterly can "
    "result in penalties. Set aside {pct}% of earnings for taxes."
)

_HUSTLES: list[dict[str, Any]] = [
    # ── Online / Remote ──────────────────────────────────────────────────
    {
        "name": "Freelance Writing / Copywriting",
        "category": "online",
        "skills": ["writing", "content", "creative", "marketing", "blog"],
        "gross_hourly": (25, 75),
        "expense_pct": 0.05,
        "startup_cost": (0, 100),
        "startup_items": "Laptop, portfolio site (free with Contently/Medium)",
        "platforms": ["Upwork", "Fiverr", "Contently", "ProBlogger"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 4,
    },
    {
        "name": "Web Development / Programming",
        "category": "online",
        "skills": ["coding", "programming", "developer", "web", "software", "tech"],
        "gross_hourly": (50, 150),
        "expense_pct": 0.10,
        "startup_cost": (0, 200),
        "startup_items": "Laptop, domain, hosting",
        "platforms": ["Upwork", "Toptal", "Fiverr", "GitHub Jobs"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 2,
    },
    {
        "name": "Graphic Design",
        "category": "online",
        "skills": ["design", "creative", "art", "photoshop", "illustrator", "canva"],
        "gross_hourly": (25, 80),
        "expense_pct": 0.10,
        "startup_cost": (0, 300),
        "startup_items": "Design software (Canva free / Affinity $70)",
        "platforms": ["Fiverr", "99designs", "Dribbble", "Upwork"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 3,
    },
    {
        "name": "Online Tutoring / Teaching",
        "category": "online",
        "skills": ["teaching", "tutor", "education", "math", "science", "english", "language"],
        "gross_hourly": (20, 60),
        "expense_pct": 0.05,
        "startup_cost": (0, 50),
        "startup_items": "Webcam, quiet space, whiteboard app",
        "platforms": ["Wyzant", "Tutor.com", "Preply", "Varsity Tutors"],
        "hours_flexible": True,
        "min_hours_week": 3,
        "ramp_weeks": 2,
    },
    {
        "name": "Virtual Assistant",
        "category": "online",
        "skills": ["admin", "organized", "assistant", "office", "data entry", "email"],
        "gross_hourly": (15, 35),
        "expense_pct": 0.05,
        "startup_cost": (0, 50),
        "startup_items": "Laptop, reliable internet",
        "platforms": ["Belay", "Time Etc", "Fancy Hands", "Upwork"],
        "hours_flexible": True,
        "min_hours_week": 10,
        "ramp_weeks": 2,
    },
    {
        "name": "Social Media Management",
        "category": "online",
        "skills": ["social media", "marketing", "content", "instagram", "tiktok"],
        "gross_hourly": (20, 60),
        "expense_pct": 0.10,
        "startup_cost": (0, 100),
        "startup_items": "Phone, scheduling tools (Later free tier)",
        "platforms": ["Local businesses", "Upwork", "LinkedIn outreach"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 3,
    },

    # ── Gig Economy ──────────────────────────────────────────────────────
    {
        "name": "Rideshare (Uber/Lyft)",
        "category": "gig",
        "skills": ["driving", "car", "people"],
        "gross_hourly": (18, 30),
        "expense_pct": 0.35,
        "startup_cost": (0, 50),
        "startup_items": "Newer car (< 15 yrs), insurance, clean background",
        "platforms": ["Uber", "Lyft"],
        "hours_flexible": True,
        "min_hours_week": 10,
        "ramp_weeks": 1,
        "note": "After gas, maintenance, depreciation, real rate is $12-20/hr",
    },
    {
        "name": "Food Delivery",
        "category": "gig",
        "skills": ["driving", "car", "bike", "flexible"],
        "gross_hourly": (15, 25),
        "expense_pct": 0.30,
        "startup_cost": (0, 50),
        "startup_items": "Car/bike, insulated bag, phone mount",
        "platforms": ["DoorDash", "Uber Eats", "Grubhub", "Instacart"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 1,
        "note": "After expenses real rate is $10-18/hr. Best during lunch/dinner peaks",
    },
    {
        "name": "TaskRabbit / Handy Work",
        "category": "gig",
        "skills": ["handy", "fix", "build", "assemble", "move", "furniture", "labor"],
        "gross_hourly": (25, 60),
        "expense_pct": 0.15,
        "startup_cost": (50, 300),
        "startup_items": "Basic tool kit, transportation",
        "platforms": ["TaskRabbit", "Thumbtack", "Nextdoor"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 1,
    },

    # ── Physical / Local ─────────────────────────────────────────────────
    {
        "name": "Dog Walking / Pet Sitting",
        "category": "local",
        "skills": ["animals", "pets", "dogs", "cats", "walking"],
        "gross_hourly": (15, 30),
        "expense_pct": 0.10,
        "startup_cost": (0, 50),
        "startup_items": "Leashes, waste bags, treats",
        "platforms": ["Rover", "Wag", "Nextdoor", "Local Facebook groups"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 2,
    },
    {
        "name": "House Cleaning",
        "category": "local",
        "skills": ["cleaning", "organized", "detail", "physical"],
        "gross_hourly": (25, 50),
        "expense_pct": 0.15,
        "startup_cost": (50, 200),
        "startup_items": "Cleaning supplies, transportation",
        "platforms": ["Thumbtack", "Nextdoor", "Local Facebook groups"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 2,
    },
    {
        "name": "Lawn Care / Landscaping",
        "category": "local",
        "skills": ["outdoor", "yard", "garden", "mowing", "landscaping", "physical"],
        "gross_hourly": (20, 50),
        "expense_pct": 0.25,
        "startup_cost": (200, 1000),
        "startup_items": "Mower, trimmer, blower, transportation",
        "platforms": ["Nextdoor", "Thumbtack", "Craigslist", "Door-to-door"],
        "hours_flexible": True,
        "min_hours_week": 8,
        "ramp_weeks": 3,
    },
    {
        "name": "Photography",
        "category": "local",
        "skills": ["photography", "camera", "creative", "visual", "art"],
        "gross_hourly": (50, 150),
        "expense_pct": 0.20,
        "startup_cost": (500, 3000),
        "startup_items": "Camera, lens, editing software, portfolio",
        "platforms": ["Instagram", "Local networking", "Thumbtack", "The Knot"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 6,
    },

    # ── Selling / E-commerce ─────────────────────────────────────────────
    {
        "name": "Reselling / Thrift Flipping",
        "category": "ecommerce",
        "skills": ["shopping", "fashion", "bargain", "selling", "thrift"],
        "gross_hourly": (15, 40),
        "expense_pct": 0.40,
        "startup_cost": (50, 500),
        "startup_items": "Sourcing capital, shipping supplies, scale",
        "platforms": ["eBay", "Poshmark", "Mercari", "Facebook Marketplace"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 4,
    },
    {
        "name": "Etsy / Handmade Crafts",
        "category": "ecommerce",
        "skills": ["crafts", "handmade", "creative", "art", "jewelry", "woodwork"],
        "gross_hourly": (10, 40),
        "expense_pct": 0.35,
        "startup_cost": (50, 500),
        "startup_items": "Materials, packaging, Etsy fees ($0.20/listing + 6.5%)",
        "platforms": ["Etsy", "Shopify", "Local craft fairs"],
        "hours_flexible": True,
        "min_hours_week": 5,
        "ramp_weeks": 6,
    },
    {
        "name": "Print on Demand",
        "category": "ecommerce",
        "skills": ["design", "creative", "marketing"],
        "gross_hourly": (5, 30),
        "expense_pct": 0.05,
        "startup_cost": (0, 50),
        "startup_items": "Designs (Canva free), platform account",
        "platforms": ["Redbubble", "Merch by Amazon", "TeeSpring", "Printful"],
        "hours_flexible": True,
        "min_hours_week": 3,
        "ramp_weeks": 8,
        "note": "Passive income potential but slow ramp. Need 50+ designs for traction",
    },
]


def _match_hustles(
    skills: list[str],
    hours_available: int,
    category_pref: str | None,
) -> list[dict]:
    """Score and rank hustles by skill match and constraints."""
    scored: list[tuple[float, dict]] = []
    skills_lower = [s.lower() for s in skills] if skills else []

    for h in _HUSTLES:
        # Category filter
        if category_pref and h["category"] != category_pref:
            continue
        # Hours filter
        if hours_available and hours_available < h["min_hours_week"]:
            continue

        # Skill match score
        skill_score = 0
        if skills_lower:
            for sk in skills_lower:
                for hsk in h["skills"]:
                    if sk in hsk or hsk in sk:
                        skill_score += 1
            skill_score = skill_score / max(len(skills_lower), 1)
        else:
            skill_score = 0.5  # neutral if no skills specified

        # Earning potential factor
        mid_hourly = (h["gross_hourly"][0] + h["gross_hourly"][1]) / 2
        net_hourly = mid_hourly * (1 - h["expense_pct"])
        earn_score = min(net_hourly / 50, 1.0)

        # Startup cost penalty
        avg_startup = (h["startup_cost"][0] + h["startup_cost"][1]) / 2
        startup_penalty = max(0, 1 - avg_startup / 1000)

        total_score = skill_score * 0.5 + earn_score * 0.3 + startup_penalty * 0.2
        scored.append((total_score, h))

    scored.sort(key=lambda x: -x[0])
    return [h for _, h in scored]


class SideHustle(RichyToolBase):
    """Side hustle recommendations with realistic earnings and tax info."""

    tool_id = 36
    tool_name = "side_hustle"
    description = (
        "Side hustle ideas: skill-matched, realistic hourly rates "
        "after expenses, startup costs, SE tax warnings"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.82),
            response=self._narrate(plan),
            data_used=["skills", "hours_available", "income"],
            accuracy_score=0.80,
            sources=[
                "Bureau of Labor Statistics gig economy data 2024",
                "IRS Schedule SE / Publication 334",
                "Platform-reported earnings (Uber, DoorDash, Upwork)",
            ],
            raw_data=plan,
        )

    def analyze(self, p: dict) -> dict:
        skills = p.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        hours = int(p.get("hours_available", 10) or 10)
        income = float(p.get("income", 60_000) or 60_000)
        category = p.get("category", None)

        matches = _match_hustles(skills, hours, category)
        top = matches[:6]

        results: list[dict] = []
        for h in top:
            lo, hi = h["gross_hourly"]
            mid = (lo + hi) / 2
            net_lo = lo * (1 - h["expense_pct"])
            net_hi = hi * (1 - h["expense_pct"])
            net_mid = mid * (1 - h["expense_pct"])

            monthly_est = net_mid * hours * 4.33
            annual_est = monthly_est * 12

            # Tax set-aside (income + SE tax combined marginal estimate)
            marginal_bracket = 0.22 if income > 44_725 else 0.12
            total_tax_pct = marginal_bracket + _SE_TAX_RATE * (1 - _SE_TAX_DEDUCTION)
            tax_set_aside_pct = round(total_tax_pct * 100, 0)
            tax_set_aside_monthly = round(monthly_est * total_tax_pct, 2)

            results.append({
                "name": h["name"],
                "category": h["category"],
                "gross_hourly_range": f"${lo}-${hi}",
                "net_hourly_range": f"${net_lo:.0f}-${net_hi:.0f}",
                "net_hourly_mid": round(net_mid, 2),
                "expense_pct": h["expense_pct"],
                "startup_cost": f"${h['startup_cost'][0]}-${h['startup_cost'][1]}",
                "startup_items": h["startup_items"],
                "platforms": h["platforms"],
                "ramp_weeks": h["ramp_weeks"],
                "monthly_estimate": round(monthly_est, 2),
                "annual_estimate": round(annual_est, 2),
                "tax_set_aside_pct": tax_set_aside_pct,
                "tax_set_aside_monthly": tax_set_aside_monthly,
                "note": h.get("note"),
            })

        confidence = 0.78 + min(len(skills), 3) * 0.03
        return {
            "hustles": results,
            "hours_available": hours,
            "skills": skills,
            "income": income,
            "se_tax_rate": f"{_SE_TAX_RATE * 100:.1f}%",
            "quarterly_tax_warning": _QUARTERLY_TAX_WARNING.format(
                pct=int(results[0]["tax_set_aside_pct"]) if results else 30
            ),
            "confidence": round(confidence, 2),
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        lines.append(
            f"💼 **Side Hustle Finder** — "
            f"{plan['hours_available']} hrs/week available | "
            f"Skills: {', '.join(plan['skills']) if plan['skills'] else 'general'}"
        )
        lines.append("")

        for i, h in enumerate(plan["hustles"], 1):
            lines.append(
                f"**{i}. {h['name']}** ({h['category']})"
            )
            lines.append(
                f"  💰 Gross: {h['gross_hourly_range']}/hr → "
                f"**Net: {h['net_hourly_range']}/hr** "
                f"(after {h['expense_pct'] * 100:.0f}% expenses)"
            )
            lines.append(
                f"  📊 Estimated: {self.fmt_currency(h['monthly_estimate'])}/mo | "
                f"{self.fmt_currency(h['annual_estimate'])}/yr "
                f"@ {plan['hours_available']} hrs/week"
            )
            lines.append(f"  🚀 Startup: {h['startup_cost']} — {h['startup_items']}")
            lines.append(f"  📱 Platforms: {', '.join(h['platforms'])}")
            lines.append(f"  ⏱️ Ramp-up: ~{h['ramp_weeks']} weeks to first income")
            if h.get("note"):
                lines.append(f"  ℹ️ {h['note']}")
            lines.append("")

        # Tax warning
        lines.append(f"**🧾 TAX WARNING:**")
        lines.append(f"  {plan['quarterly_tax_warning']}")
        lines.append(
            f"  SE tax alone is {plan['se_tax_rate']} on net self-employment income."
        )
        if plan["hustles"]:
            h0 = plan["hustles"][0]
            lines.append(
                f"  Set aside ~{self.fmt_currency(h0['tax_set_aside_monthly'])}/mo "
                f"({h0['tax_set_aside_pct']:.0f}%) for taxes."
            )
        lines.append("")

        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: BLS, IRS Pub 334, platform data"
        )
        return "\n".join(lines)
