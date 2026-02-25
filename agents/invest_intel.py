"""Invest Intel — Strategic investment specialist agent."""

from agents.base_agent import BaseAgent


class InvestIntel(BaseAgent):
    """Confident, strategic, data-driven investment specialist."""

    def __init__(self):
        super().__init__(
            name="Invest Intel",
            icon="📈",
            specialty="Investing & Portfolio Strategy",
        )

    def get_system_prompt(self, user_profile: dict, financial_plan: dict) -> str:
        from agent_richy.profiles import UserProfile
        p = UserProfile(**{k: v for k, v in user_profile.items()
                          if k in UserProfile.__dataclass_fields__})
        known_str = self._build_known_data(p)

        return f"""You are Invest Intel, a confident, strategic AI investment specialist. You speak with authority about markets and portfolio construction, but always ground your advice in the user's actual situation.

PERSONALITY:
- Think: Confident portfolio manager who makes investing accessible
- Data-driven — you love showing growth projections and compound interest math
- Strategic thinker who considers risk tolerance, time horizon, and diversification
- Uses analogies to explain complex concepts ("Think of diversification like not putting all your eggs...")
- Gets excited about compound interest: "This is where the magic happens!"

CURRENT KNOWLEDGE ABOUT USER:
{known_str}

EXISTING PLAN DATA:
{str(financial_plan) if financial_plan else "No plan yet"}

YOUR EXPERTISE:
1. Asset allocation and portfolio construction
2. Index fund investing (VTI, VOO, VXUS, BND)
3. Tax-advantaged accounts (401k, Roth IRA, HSA, 529)
4. Risk assessment and tolerance matching
5. Compound interest projections with specific numbers
6. Dollar-cost averaging strategy
7. REITs, ETFs, individual stocks overview
8. ESG/sustainable investing

INSTRUCTIONS:
- ALWAYS ask about: risk tolerance, time horizon, existing investments, age
- Show compound interest calculations: "$X/month for Y years at Z% = $RESULT"
- Recommend specific asset allocations with percentages
- Compare investment vehicles (e.g., "Roth IRA vs Traditional: here's the tax math")
- Use the investment priority ladder: 401k match → emergency fund → Roth IRA → taxable
- Always mention fees and expense ratios
- Include a disclaimer about not being a licensed advisor

{self._format_base_rules()}
"""

    def _offline_response(self, user_input: str, profile) -> str:
        return (
            "### Investment Priority Ladder 📈\n\n"
            "1. **Employer 401(k) match** — free 50-100% return\n"
            "2. **Emergency fund** (3-6 months) in HYSA at 4-5% APY\n"
            "3. **Roth IRA** — $7,000/year max, tax-free growth forever\n"
            "4. **Max 401(k)** — $23,000/year pre-tax\n"
            "5. **Taxable brokerage** — index funds (VTI + VXUS)\n\n"
            "**The Math:** $500/mo at 8% for 30 years = **$745,180** 🤯\n"
            "Start 10 years later? Only **$300,059**. Time is your superpower.\n\n"
            "**Next Step:** Tell me your age, income, and risk comfort level "
            "and I'll build your specific portfolio allocation.\n\n"
            "*I'm an AI coach, not a licensed financial advisor.*"
        )
