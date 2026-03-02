"""Coach Richy — Main AI financial coach agent."""

from agents.base_agent import BaseAgent


class CoachRichy(BaseAgent):
    """The primary financial coach. Warm, encouraging, routes to specialists."""

    def __init__(self):
        super().__init__(
            name="Coach Richy",
            icon="💰",
            specialty="General Financial Coaching",
        )

    def get_system_prompt(self, user_profile: dict, financial_plan: dict) -> str:
        """Build Coach Richy's system prompt."""
        from models.profile import FinancialProfile

        # Build a temporary profile to use _build_known_data
        p = FinancialProfile(**{k: v for k, v in user_profile.items()
                               if k in FinancialProfile.model_fields})
        known_str = self._build_known_data(p)

        plan_str = ""
        if financial_plan:
            plan_str = f"\nExisting plan sections: {', '.join(financial_plan.keys())}"

        is_youth = user_profile.get("user_type") == "youth"

        if is_youth:
            persona = (
                "You are Coach Richy, a fun, encouraging AI financial coach for young people. "
                "You make money topics exciting and relatable. Use simple language, emojis, "
                "and real examples teens can connect with. You're like a cool older sibling "
                "who's great with money."
            )
            discovery = (
                "Ask about: allowance, any jobs/hustles, savings, what they want to buy/save for, "
                "their interests and talents. Be enthusiastic about their potential."
            )
        else:
            persona = (
                "You are Coach Richy, a warm, knowledgeable AI financial advisor. "
                "You speak in plain English — like a smart friend who happens to be a financial planner. "
                "Many users struggle paycheck-to-paycheck. Give clear, actionable advice "
                "with real numbers. Be encouraging but honest. Never judge. "
                "You're the user's primary coach who understands their full financial picture."
            )
            discovery = (
                "Gather: monthly take-home income, major expenses (rent, car, utilities, food, "
                "subscriptions), debts (type, balance, interest rate, minimum payment), "
                "savings balance, emergency fund, credit score, financial goals. "
                "Ask naturally — not like a form. Space questions across messages."
            )

        return f"""{persona}

CURRENT KNOWLEDGE ABOUT USER:
{known_str}{plan_str}

YOUR JOB:
1. Have a natural, empathetic conversation to understand their financial situation
2. {discovery}
3. When you have enough info (income, expenses, debts, goals), proactively offer to build their plan
4. Give specific, actionable advice with dollar amounts
5. After building a plan, help them refine it
6. If the topic is specialized (deep investing, complex debt strategy), suggest they also talk to a specialist:
   - Budget Bot for detailed spending analysis
   - Invest Intel for portfolio strategy
   - Debt Destroyer for payoff plans
   - Savings Sage for savings goals

{self._format_base_rules()}
"""

    def _offline_response(self, user_input: str, profile) -> str:
        """Generate helpful offline response with keyword matching."""
        import re
        q = user_input.lower()
        numbers = re.findall(r'\$?([\d,]+)', q)

        if profile.is_youth():
            if not any(q):
                return (
                    f"Hey **{profile.name}**! 🎉 I'm Richy, your money coach!\n\n"
                    "Let's talk about your money situation — it's totally casual.\n\n"
                    "**Tell me:**\n"
                    "- Do you get an allowance? Have a job or side hustle?\n"
                    "- Are you saving for anything specific?\n"
                    "- What are you into? (hobbies, skills, interests)\n\n"
                    "Just tell me whatever — I'll figure out the best plan for you! 💪"
                )

        if any(w in q for w in ["income", "make", "earn", "salary", "paid", "paycheck"]):
            if numbers:
                amt = float(numbers[0].replace(",", ""))
                profile.monthly_income = amt
                profile.completed_assessment = True
                return (
                    f"Got it — **${amt:,.0f}/month** take-home income. 📝\n\n"
                    "Now tell me about your **main expenses**:\n"
                    "- Rent/mortgage?\n- Car payment?\n"
                    "- Utilities, groceries, subscriptions?\n\n"
                    "Just give me rough numbers — I'll build your budget!"
                )
            return "What's your **monthly take-home pay**? (After taxes)\n\nJust give me the number and I'll start building your plan."

        if any(w in q for w in ["budget", "50/30/20", "spending plan"]):
            if profile.monthly_income > 0:
                needs = profile.monthly_income * 0.50
                wants = profile.monthly_income * 0.30
                save = profile.monthly_income * 0.20
                return (
                    f"### Your 50/30/20 Budget on ${profile.monthly_income:,.0f}/mo\n\n"
                    f"- **50% Needs:** ${needs:,.0f} (rent, food, utilities)\n"
                    f"- **30% Wants:** ${wants:,.0f} (dining, entertainment)\n"
                    f"- **20% Savings:** ${save:,.0f} (emergency fund, investing)\n\n"
                    "**Next Step:** Tell me your actual expenses so I can show where you stand vs. this target."
                )
            return "I'd love to build your budget! First, tell me your **monthly take-home income**."

        if any(w in q for w in ["invest", "stock", "401k", "roth"]):
            return (
                "### Investing Priority Ladder\n\n"
                "1. **Employer 401(k) match** — free money, take it ALL\n"
                "2. **3-6 month emergency fund** in HYSA (4-5% APY)\n"
                "3. **Roth IRA** — $7,000/year max, tax-free growth\n"
                "4. **Index funds** — VTI, VOO, VXUS for diversification\n\n"
                "$500/mo invested at 8% for 30 years = **~$750,000** 📈\n\n"
                "**Next Step:** Tell me about your current situation so I can give you specific numbers.\n\n"
                "*I'm an AI coach, not a licensed financial advisor.*"
            )

        if any(w in q for w in ["debt", "owe", "credit card", "loan"]):
            return (
                "Let me help you tackle that debt! 💪\n\n"
                "**Tell me about each debt:**\n"
                "- Type (credit card, student loan, car, medical)\n"
                "- Balance ($)\n- Interest rate (%)\n- Minimum payment ($)\n\n"
                "I'll compare **avalanche** (highest interest first) vs **snowball** "
                "(smallest balance first) strategies for you.\n\n"
                "**Next Step:** List your debts and I'll build your payoff plan."
            )

        if any(w in q for w in ["save", "emergency", "fund"]):
            return (
                "### Emergency Fund Priorities\n\n"
                "1. **Phase 1:** $1,000 starter fund (do this FIRST)\n"
                "2. **Phase 2:** 3 months of expenses\n"
                "3. **Phase 3:** 6 months for full security\n\n"
                "Put it in a **High-Yield Savings Account** (4-5% APY).\n"
                "Automate transfers on payday — even $25/week adds up!\n\n"
                "**Next Step:** What's your current savings balance?"
            )

        return (
            f"Hey **{profile.name}**! 💰\n\n"
            "I'm here to help with anything money-related. Tell me about:\n"
            "- Your **income** (monthly take-home)\n"
            "- Your **biggest expenses**\n"
            "- Any **debts** you're dealing with\n"
            "- Your **financial goals**\n\n"
            "The more I know, the better plan I can build! "
            "Set up an `OPENAI_API_KEY` for full AI-powered conversations. 🔑"
        )

    def get_opening_message(self, profile) -> str:
        """Generate the opening conversation message."""
        if profile.is_youth():
            return (
                f"Hey **{profile.name}**! 🎉 I'm Coach Richy, your personal money coach!\n\n"
                "Let's talk about your money situation — no boring forms, just conversation.\n\n"
                "**Start by telling me:**\n"
                "- Do you get an allowance or have a job?\n"
                "- Are you saving for anything cool?\n"
                "- What are your interests and hobbies?\n\n"
                "I'll help you build a plan that actually works for you! 💪"
            )
        return (
            f"Hey **{profile.name}**! 💰 I'm Coach Richy, your AI financial advisor.\n\n"
            "Let's build your financial plan through conversation — "
            "no spreadsheets, no judgment.\n\n"
            "**Start by telling me about:**\n"
            "- Your monthly take-home pay\n"
            "- Your biggest expenses (rent, car, food)\n"
            "- Any debts you're carrying\n"
            "- What you're trying to achieve financially\n\n"
            "Share as much or as little as you want — I'll ask follow-up questions "
            "and build your personalized plan as we go! 🚀"
        )
