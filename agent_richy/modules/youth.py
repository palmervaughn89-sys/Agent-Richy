"""Youth financial education module for Agent Richy.

Targets middle school (grades 6-8) and high school (grades 9-12) students
with real-world examples for earning, budgeting, saving, and investing.
"""

from typing import Optional
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import (
    print_header,
    print_divider,
    prompt,
    parse_yes_no,
    parse_number,
    format_currency,
    wrap_text,
    ask_llm,
)

# ---------------------------------------------------------------------------
# Real-world earning opportunities keyed by grade level
# ---------------------------------------------------------------------------

EARNING_IDEAS = {
    "middle": [
        ("Lawn mowing / yard work",
         "Charge $20-40 per yard. In a summer month you could earn $200-600 "
         "just on weekends. Track your clients in a simple notebook."),
        ("Pet sitting / dog walking",
         "Apps like Rover or flyers in your neighborhood. $15-25 per walk, "
         "$25-50 per day of pet sitting."),
        ("Tutoring younger kids",
         "Help kids in your neighborhood with reading or math for $10-20/hr. "
         "Your school or library may post tutoring requests."),
        ("Selling crafts or art online",
         "Use Etsy to sell handmade items. Start-up cost is minimal; "
         "focus on a niche like custom bookmarks or stickers."),
        ("Helping with tech for neighbors",
         "Set up Wi-Fi, teach seniors to use smartphones, or fix basic "
         "computer issues. Charge $10-20/hour."),
    ],
    "high": [
        ("Part-time job (retail / food service)",
         "Federal minimum wage is $7.25/hr; many states pay $12-15+. "
         "Work 10-15 hrs/week = $500-900/month. Build resume skills too."),
        ("Freelance graphic design / video editing",
         "Learn free tools (Canva, DaVinci Resolve). Sell services on Fiverr "
         "starting at $5-$50 per project. Build a portfolio on Instagram."),
        ("Social media content creation",
         "YouTube AdSense, TikTok Creator Fund, or brand sponsorships. "
         "Pick a niche you love — consistency is more important than perfection."),
        ("Online reselling (sneakers, vintage clothes)",
         "Buy low on Facebook Marketplace or thrift stores, sell higher on "
         "eBay or StockX. Study what's trending to maximize margins."),
        ("Car washing / detailing",
         "Start with a bucket, soap, and microfiber cloths. Charge $20-30 "
         "for a basic wash, $75-150 for a full detail. Very scalable."),
        ("Tutoring in school subjects",
         "High-school subjects like Calculus, Chemistry, and SAT prep command "
         "$25-50/hr. Market yourself through school counselors or Wyzant."),
    ],
}

BUDGETING_TEMPLATE = """
Simple Budget Template
----------------------
Monthly Income (after tax): {income}

Fixed Expenses:
  - School supplies / fees:   {school}
  - Phone bill (if any):      {phone}
  - Subscriptions:            {subs}

Variable Expenses:
  - Food / eating out:        {food}
  - Entertainment:            {ent}
  - Clothing:                 {clothing}
  - Transportation:           {transport}

Total Expenses:               {total_exp}
Remaining (Savings):          {savings}

Savings Goal Tip: Aim to save at least 20% of every paycheck!
"""

INVESTING_INTRO = {
    "middle": """
Investing 101 for Middle Schoolers
------------------------------------
Think of investing like planting a seed. You put in a little money now,
and over time it GROWS — even while you sleep!

Key ideas to know:
1. COMPOUND INTEREST: Earn interest on top of interest. $100 at 8%/year
   becomes $215 in 10 years — without adding a single dollar!
2. INDEX FUNDS: Instead of picking one company, you buy a tiny piece of
   HUNDREDS of companies at once. Less risky, less stressful.
3. START EARLY: The earlier you invest, the more time your money has to
   grow. Even $25/month starting at age 12 can become thousands by 18!

Great first step: Ask a parent about opening a custodial account (like
a Fidelity Youth Account or Greenlight) so you can start learning with
real money in a safe environment.
""",
    "high": """
Investing 101 for High Schoolers
-----------------------------------
You already know the basics — now let's level up.

Key vehicles to understand:
1. STOCKS: Ownership in a company. Higher potential reward, higher risk.
   Study a company before buying. Look at revenue growth, not just hype.
2. ETFs / INDEX FUNDS: Diversified baskets of stocks or bonds. SPY (S&P 500)
   has averaged ~10%/year historically. Great for long-term holding.
3. ROTH IRA: If you have earned income (job), you can contribute up to
   $7,000/year. That money grows TAX-FREE. This is the #1 wealth-building
   tool available to teenagers with jobs!
4. DOLLAR-COST AVERAGING (DCA): Invest a fixed amount every month
   regardless of price. Removes emotion from investing.

Action step: Open a Roth IRA through Fidelity or Schwab (parent co-signer
needed under 18). Start with as little as $1 in an S&P 500 index fund.
""",
}


class YouthModule:
    """Interactive financial education for middle and high school students."""

    def __init__(self, profile: UserProfile, llm_client=None):
        self.profile = profile
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Top-level menu
    # ------------------------------------------------------------------

    def run(self) -> None:
        print_header(f"Welcome, {self.profile.name}! I'm Agent Richy 💰")
        print(wrap_text(
            "I'm here to help you start your financial journey. "
            "Whether it's earning your first dollar, budgeting like a pro, "
            "or learning to invest, I've got you covered. Let's go!"
        ))

        while True:
            print_divider()
            print("\nWhat would you like to explore?")
            print("  1. Ways to earn money")
            print("  2. How to budget your money")
            print("  3. Saving & investing basics")
            print("  4. Ask Richy anything (financial topic)")
            print("  5. Exit")
            choice = prompt("Choose an option (1-5):").strip()

            if choice == "1":
                self._earning_ideas()
            elif choice == "2":
                self._budgeting_workshop()
            elif choice == "3":
                self._investing_intro()
            elif choice == "4":
                self._free_question()
            elif choice == "5":
                print("\nKeep grinding and keep learning. Your future self will thank you! 🚀")
                break
            else:
                print("Please enter a number between 1 and 5.")

    # ------------------------------------------------------------------
    # Sub-sections
    # ------------------------------------------------------------------

    def _earning_ideas(self) -> None:
        print_header("Ways to Earn Money 💼")
        level = self.profile.grade_level or "high"
        ideas = EARNING_IDEAS.get(level, EARNING_IDEAS["high"])

        print(f"Here are {len(ideas)} real-world ways to start earning:\n")
        for i, (title, detail) in enumerate(ideas, 1):
            print(f"  {i}. {title}")

        choice = prompt("Pick a number to learn more, or press Enter to go back:").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(ideas):
                title, detail = ideas[idx]
                print(f"\n📌 {title}")
                print_divider()
                print(wrap_text(detail))

                llm_response = ask_llm(
                    self.llm_client,
                    system_prompt=(
                        "You are Agent Richy, an enthusiastic financial coach for students. "
                        "Give a short motivating tip (2-3 sentences) about this earning opportunity."
                    ),
                    user_message=f"Earning idea: {title}\nDetail: {detail}",
                )
                if llm_response:
                    print(f"\n💡 Richy's Tip: {llm_response}")

    def _budgeting_workshop(self) -> None:
        print_header("Budget Workshop 📊")
        print(wrap_text(
            "A budget is just a plan for your money. Let's build yours. "
            "Don't worry — we keep it simple!"
        ))

        income_str = prompt("How much money do you earn or receive per month? (Enter $0 if none yet):")
        income = parse_number(income_str) or 0.0

        if income == 0:
            print(wrap_text(
                "\nNo income yet? That's totally okay! This exercise will show you what "
                "to aim for once you start earning. Let's use $200/month as an example."
            ))
            income = 200.0

        categories = [
            ("school supplies / fees", 0.0),
            ("phone bill", 0.0),
            ("food / eating out", 0.0),
            ("entertainment (movies, games, etc.)", 0.0),
            ("clothing", 0.0),
            ("transportation (bus, gas, etc.)", 0.0),
        ]
        expenses = {}
        print(f"\nYour monthly income: {format_currency(income)}")
        print("Now let's list your monthly expenses. Enter $0 if you don't have that expense.\n")

        for label, _ in categories:
            val_str = prompt(f"How much do you spend on {label}?:")
            expenses[label] = parse_number(val_str) or 0.0

        total_exp = sum(expenses.values())
        savings = income - total_exp

        print("\n" + "=" * 60)
        print("YOUR MONTHLY BUDGET SNAPSHOT")
        print("=" * 60)
        print(f"  Income:       {format_currency(income)}")
        print(f"  Total Expenses: {format_currency(total_exp)}")
        print(f"  Left to Save:   {format_currency(savings)}")
        print("=" * 60)

        savings_pct = (savings / income * 100) if income else 0
        if savings < 0:
            print(wrap_text(
                "\n⚠️  You're spending more than you earn! "
                "Let's look at where you can cut back. "
                "Try reducing entertainment or eating out by even 20% — that adds up fast!"
            ))
        elif savings_pct < 10:
            print(wrap_text(
                f"\nYou're saving {savings_pct:.1f}% of your income. "
                "The goal is at least 20%. See if you can trim any variable expenses."
            ))
        else:
            print(wrap_text(
                f"\n🎉 Great job! You're saving {savings_pct:.1f}% of your income. "
                "Keep building that habit. Now think about where to PUT those savings."
            ))

        if savings > 0:
            print(wrap_text(
                f"\nWith {format_currency(savings)}/month in savings, in 1 year you'll have "
                f"{format_currency(savings * 12)}. If you invest that at 8%/year, "
                "it keeps growing long after you stop adding money!"
            ))

    def _investing_intro(self) -> None:
        level = self.profile.grade_level or "high"
        content = INVESTING_INTRO.get(level, INVESTING_INTRO["high"])
        print_header("Investing Basics 📈")
        print(content)

        print("Want to see how compound interest works? Let's run the numbers!")
        amount_str = prompt("How much could you save per month? (e.g. 50):")
        amount = parse_number(amount_str) or 50.0

        print_divider()
        print(f"If you invest {format_currency(amount)}/month at 8% annual return:\n")
        balance = 0.0
        annual = amount * 12
        monthly_rate = 0.08 / 12
        print(f"  {'Year':<8} {'Balance':>12}")
        print(f"  {'-'*8} {'-'*12}")
        for year in range(1, 11):
            for _ in range(12):
                balance = balance * (1 + monthly_rate) + amount
            print(f"  {year:<8} {format_currency(balance):>12}")

        print(wrap_text(
            f"\nThat's the power of compound interest! "
            f"After 10 years of investing {format_currency(amount)}/month "
            f"you'd have roughly {format_currency(balance)} — "
            f"even though you only put in {format_currency(amount * 12 * 10)}."
        ))

    def _free_question(self) -> None:
        print_header("Ask Richy Anything 🤔")
        question = prompt("What financial question is on your mind?:")
        if not question:
            return

        system_prompt = (
            "You are Agent Richy, a friendly and knowledgeable financial coach "
            "for middle and high school students. Answer clearly and concisely "
            "using real-world examples. Keep answers under 150 words. "
            "Use an encouraging, motivating tone."
        )
        response = ask_llm(self.llm_client, system_prompt, question)
        if response:
            print(f"\n💬 Richy says:\n{wrap_text(response)}")
        else:
            print(wrap_text(
                "\nGreat question! Here's a quick tip: the most important financial "
                "habit you can build right now is simply TRACKING where your money goes. "
                "Use a free app like Mint or just a notes app on your phone. "
                "Awareness is the first step to control."
            ))
