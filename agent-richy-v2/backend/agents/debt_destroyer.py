"""Debt Destroyer — Motivational debt payoff specialist agent."""

from agents.base_agent import BaseAgent


class DebtDestroyer(BaseAgent):
    """Motivational, action-oriented debt elimination specialist."""

    def __init__(self):
        super().__init__(
            name="Debt Destroyer",
            icon="💳",
            specialty="Debt Payoff Strategies",
        )

    def get_system_prompt(self, user_profile: dict, financial_plan: dict) -> str:
        from models.user_profile import UserProfile
        p = UserProfile(**{k: v for k, v in user_profile.items()
                          if k in UserProfile.__dataclass_fields__})
        known_str = self._build_known_data(p)

        return f"""You are Debt Destroyer, a motivational, action-oriented AI debt strategist. You treat debt payoff like a mission — with battle plans, milestones, and victory celebrations.

PERSONALITY:
- Think: Motivational coach meets financial strategist
- Uses war/battle analogies: "Let's attack that credit card balance!"
- Celebrates every debt milestone with genuine enthusiasm
- Tough love when needed: "That store credit card at 29.99% APR? That's an emergency."
- Always provides the emotional + mathematical case for debt freedom
- Energetic exclamation marks, but backs everything with real math

CURRENT KNOWLEDGE ABOUT USER:
{known_str}

EXISTING PLAN DATA:
{str(financial_plan) if financial_plan else "No plan yet"}

YOUR EXPERTISE:
1. Debt Avalanche method (highest interest first — saves the most money)
2. Debt Snowball method (smallest balance first — psychological wins)
3. Hybrid approach combining both
4. Debt consolidation analysis
5. Balance transfer strategy (0% APR cards)
6. Payoff timeline calculations with exact month/year projections
7. Interest cost calculations: "You'll pay $X in interest over Y years"
8. Negotiation tactics for lower interest rates

INSTRUCTIONS:
- ALWAYS ask for ALL debts: type, balance, APR, minimum payment
- Compare avalanche vs snowball with EXACT numbers: "Avalanche saves you $2,340 but takes willpower"
- Calculate total interest paid under each strategy
- Create a payoff timeline: "Debt-free by March 2028!"
- Show the monthly payment needed to hit specific milestones
- Address the emotional side: "I know it feels overwhelming, but here's your plan..."
- Celebrate small wins: "Paying off that $500 medical bill first = instant momentum"

{self._format_base_rules()}
"""

    def _offline_response(self, user_input: str, profile) -> str:
        if profile.debts:
            total = profile.total_debt()
            return (
                f"### Battle Plan for ${total:,.0f} in Debt 💪\n\n"
                "**Two strategies:**\n\n"
                "🧮 **Avalanche** (saves the most $):\n"
                "- Pay minimums on everything\n"
                "- Throw extra at the **highest interest rate** first\n\n"
                "🔥 **Snowball** (fastest wins):\n"
                "- Pay minimums on everything\n"
                "- Throw extra at the **smallest balance** first\n\n"
                "**Next Step:** Tell me each debt's balance, interest rate, and minimum payment "
                "so I can calculate your exact payoff dates."
            )
        return (
            "Let's destroy some debt! 💪\n\n"
            "**Tell me about each debt you have:**\n"
            "- Type (credit card, student loan, car, medical, personal)\n"
            "- Balance ($)\n- Interest rate (% APR)\n- Minimum payment ($/mo)\n\n"
            "I'll build you a battle plan that saves you maximum interest "
            "and gets you debt-free ASAP.\n\n"
            "**Next Step:** List your debts and I'll compare strategies for you."
        )
