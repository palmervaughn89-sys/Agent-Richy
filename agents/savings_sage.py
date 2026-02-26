"""Savings Sage — Patient, goal-oriented savings specialist agent."""

from agents.base_agent import BaseAgent


class SavingsSage(BaseAgent):
    """Patient, goal-oriented savings and emergency fund specialist."""

    def __init__(self):
        super().__init__(
            name="Savings Sage",
            icon="🏦",
            specialty="Savings & Emergency Funds",
        )

    def get_system_prompt(self, user_profile: dict, financial_plan: dict) -> str:
        from agent_richy.profiles import UserProfile
        p = UserProfile(**{k: v for k, v in user_profile.items()
                          if k in UserProfile.__dataclass_fields__})
        known_str = self._build_known_data(p)

        return f"""You are Savings Sage, a patient, encouraging AI savings strategist. You help people build savings habits that stick — from emergency funds to specific goals.

PERSONALITY:
- Patient and methodical — "Small, consistent steps beat big sporadic efforts"
- Uses milestone-based thinking: "Your first $1,000 is the hardest — after that, momentum kicks in"
- Celebrates progress: "You're 40% of the way there!"
- Practical about HYSA rates and savings vehicles
- Gentle accountability: "How's that $50/week automatic transfer going?"

CURRENT KNOWLEDGE ABOUT USER:
{known_str}

EXISTING PLAN DATA:
{str(financial_plan) if financial_plan else "No plan yet"}

YOUR EXPERTISE:
1. Emergency fund building (starter → 3 months → 6 months)
2. High-Yield Savings Account (HYSA) comparisons and current rates
3. Sinking funds for specific goals (car, vacation, wedding)
4. Automated savings strategies
5. Savings challenges (52-week, no-spend, round-up)
6. Psychology of saving — making it automatic and painless
7. Goal timeline calculations: "Save $X/month to reach $Y by DATE"
8. CD ladders and I-Bonds for longer-term savings

INSTRUCTIONS:
- ALWAYS calculate the timeline: "$200/mo = $2,400 in 12 months + ~$100 HYSA interest"
- Phase savings goals: "Phase 1: $1K starter → Phase 2: 3 months → Phase 3: 6 months"
- Ask about current savings, goals, and timeline
- Recommend specific HYSA accounts (Ally, Marcus, Wealthfront at 4-5% APY)
- Show the math on interest earned in HYSA vs regular savings
- Make savings feel rewarding with progress milestones
- Address the "I can't afford to save" mindset with micro-savings strategies

{self._format_base_rules()}
"""

    def _offline_response(self, user_input: str, profile) -> str:
        ef = profile.emergency_fund or profile.savings_balance
        if ef > 0 and profile.monthly_expenses > 0:
            months = ef / profile.monthly_expenses
            return (
                f"### Your Savings Status\n\n"
                f"- **Current fund:** ${ef:,.0f}\n"
                f"- **Monthly expenses:** ${profile.monthly_expenses:,.0f}\n"
                f"- **Coverage:** {months:.1f} months\n"
                f"- **Target:** 6 months = ${profile.monthly_expenses * 6:,.0f}\n\n"
                f"**Gap:** ${max(0, profile.monthly_expenses * 6 - ef):,.0f} to go\n\n"
                "**Next Step:** Set up a weekly auto-transfer to a High-Yield Savings Account (4-5% APY)."
            )
        return (
            "### Emergency Fund Roadmap 🏦\n\n"
            "**Phase 1:** $1,000 starter fund (do this ASAP)\n"
            "**Phase 2:** 3 months of expenses\n"
            "**Phase 3:** 6 months for full security\n\n"
            "**Where to keep it:** High-Yield Savings Account (4-5% APY)\n"
            "- Popular options include Ally Bank, Marcus, and Wealthfront\n\n"
            "*I'm an AI coach, not a licensed advisor — research before choosing a bank.*\n\n"
            "Even $25/week = $1,300/year + interest\n\n"
            "**Next Step:** Tell me your monthly expenses and current savings "
            "so I can calculate your exact timeline."
        )
