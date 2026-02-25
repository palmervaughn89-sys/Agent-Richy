"""Adult financial planning module for Agent Richy.

Covers: tax helper, in-depth budget simulation, mortgage calculator,
insurance overview, vacation planning, and goal-setting.
"""

import math
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
# Tax brackets (2024, Single filer – simplified illustration)
# ---------------------------------------------------------------------------
TAX_BRACKETS_SINGLE = [
    (11_600,  0.10),
    (47_150,  0.12),
    (100_525, 0.22),
    (191_950, 0.24),
    (243_725, 0.32),
    (609_350, 0.35),
    (float("inf"), 0.37),
]

STANDARD_DEDUCTION_SINGLE = 14_600
STANDARD_DEDUCTION_MFJ = 29_200


def estimate_federal_tax(gross_income: float, filing_status: str = "single") -> dict:
    """Return an estimate of federal income tax using 2024 brackets."""
    deduction = (
        STANDARD_DEDUCTION_MFJ if filing_status.lower() in ("mfj", "married", "joint")
        else STANDARD_DEDUCTION_SINGLE
    )
    taxable = max(0.0, gross_income - deduction)

    tax = 0.0
    prev_limit = 0.0
    effective_rates = []
    for limit, rate in TAX_BRACKETS_SINGLE:
        if taxable <= prev_limit:
            break
        bracket_income = min(taxable, limit) - prev_limit
        bracket_tax = bracket_income * rate
        tax += bracket_tax
        effective_rates.append((rate, bracket_income, bracket_tax))
        prev_limit = limit

    effective_rate = (tax / gross_income * 100) if gross_income else 0.0
    fica = min(gross_income, 168_600) * 0.0765  # Social Security + Medicare

    return {
        "gross_income": gross_income,
        "standard_deduction": deduction,
        "taxable_income": taxable,
        "federal_tax": tax,
        "fica_tax": fica,
        "total_tax": tax + fica,
        "effective_rate": effective_rate,
        "take_home": gross_income - tax - fica,
    }


def mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Calculate monthly mortgage payment using standard amortization formula."""
    monthly_rate = annual_rate / 12
    n = years * 12
    if monthly_rate == 0:
        return principal / n
    payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    return payment


def months_to_goal(monthly_saving: float, goal: float, annual_rate: float = 0.05) -> int:
    """Return the number of months to reach a savings goal with compound interest."""
    if monthly_saving <= 0:
        return 0
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return math.ceil(goal / monthly_saving)
    n = math.log(1 + (goal * monthly_rate) / monthly_saving) / math.log(1 + monthly_rate)
    return math.ceil(n)


class AdultModule:
    """Interactive financial planning tools for adult users."""

    def __init__(self, profile: UserProfile, llm_client=None):
        self.profile = profile
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Top-level menu
    # ------------------------------------------------------------------

    def run(self) -> None:
        print_header(f"Welcome, {self.profile.name}! I'm Agent Richy 💰")
        print(wrap_text(
            "I'm your personal financial planning assistant. Whether you need "
            "help with taxes, budgeting, or planning big life goals like buying "
            "a home or retiring early — I'm here to guide you every step of the way."
        ))

        while True:
            print_divider()
            print("\nWhat would you like to work on?")
            print("  1. Tax estimator")
            print("  2. Budget simulation")
            print("  3. Goal planner (vacation, home, retirement, etc.)")
            print("  4. Mortgage calculator")
            print("  5. Insurance overview")
            print("  6. Ask Richy anything")
            print("  7. Exit")
            choice = prompt("Choose an option (1-7):").strip()

            if choice == "1":
                self._tax_helper()
            elif choice == "2":
                self._budget_simulation()
            elif choice == "3":
                self._goal_planner()
            elif choice == "4":
                self._mortgage_calculator()
            elif choice == "5":
                self._insurance_overview()
            elif choice == "6":
                self._free_question()
            elif choice == "7":
                print("\nStay disciplined, stay focused. Your financial future is bright! 🌟")
                break
            else:
                print("Please enter a number between 1 and 7.")

    # ------------------------------------------------------------------
    # Tax helper
    # ------------------------------------------------------------------

    def _tax_helper(self) -> None:
        print_header("Tax Estimator 🧾")
        print(wrap_text(
            "This tool gives you a rough federal tax estimate based on 2024 "
            "tax brackets. Always consult a CPA for your actual return."
        ))

        income_str = prompt("What is your GROSS annual income (before taxes)?:")
        income = parse_number(income_str)
        if not income:
            print("Could not parse that. Please enter a number like 65000.")
            return

        filing = prompt("Filing status? (single / married):").lower()
        filing = "married" if "married" in filing or "joint" in filing else "single"

        result = estimate_federal_tax(income, filing)

        print("\n" + "=" * 60)
        print("  FEDERAL TAX ESTIMATE (2024)")
        print("=" * 60)
        print(f"  Gross Income:          {format_currency(result['gross_income'])}")
        print(f"  Standard Deduction:    {format_currency(result['standard_deduction'])}")
        print(f"  Taxable Income:        {format_currency(result['taxable_income'])}")
        print(f"  Federal Income Tax:    {format_currency(result['federal_tax'])}")
        print(f"  FICA (SS + Medicare):  {format_currency(result['fica_tax'])}")
        print(f"  Total Tax:             {format_currency(result['total_tax'])}")
        print(f"  Effective Rate:        {result['effective_rate']:.1f}%")
        print(f"  Est. Take-Home/Year:   {format_currency(result['take_home'])}")
        print(f"  Est. Take-Home/Month:  {format_currency(result['take_home'] / 12)}")
        print("=" * 60)

        # Quick deduction tips
        print("\n💡 Ways to Reduce Your Tax Bill:")
        tips = [
            "Contribute to a 401(k) — up to $23,000/year reduces taxable income.",
            "Fund a Traditional IRA — up to $7,000/year is deductible if eligible.",
            "Use an HSA if you have a high-deductible health plan — triple tax advantage.",
            "Track charitable donations for itemized deductions.",
            "If you're self-employed, deduct home office, internet, and business expenses.",
        ]
        for tip in tips:
            print(f"  • {wrap_text(tip)}")

        llm_tip = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy, a financial advisor. "
                "Give one specific, actionable tax tip in 2 sentences based on the user's income."
            ),
            user_message=f"Gross income: {income}, filing status: {filing}",
        )
        if llm_tip:
            print(f"\n🤖 Richy's personalized tip: {llm_tip}")

    # ------------------------------------------------------------------
    # Budget simulation
    # ------------------------------------------------------------------

    def _budget_simulation(self) -> None:
        print_header("Budget Simulation 📊")
        print(wrap_text(
            "Let's build a detailed picture of your finances. "
            "I'll ask about income, fixed costs, variable spending, "
            "and then show you where you stand and how to improve."
        ))

        income_str = prompt("What is your monthly take-home income (after taxes)?:")
        income = parse_number(income_str) or 0.0
        self.profile.monthly_income = income

        print("\n--- Fixed Monthly Expenses ---")
        fixed_categories = [
            "rent / mortgage",
            "car payment",
            "student loans",
            "insurance premiums (health, auto, life)",
            "utilities (electric, gas, water)",
            "internet / phone",
            "subscriptions (streaming, gym, etc.)",
        ]
        fixed = {}
        for cat in fixed_categories:
            val = parse_number(prompt(f"  {cat}:")) or 0.0
            fixed[cat] = val

        print("\n--- Variable Monthly Expenses ---")
        variable_categories = [
            "groceries",
            "dining out / food delivery",
            "gas / transportation",
            "clothing / shopping",
            "entertainment / hobbies",
            "personal care",
            "miscellaneous",
        ]
        variable = {}
        for cat in variable_categories:
            val = parse_number(prompt(f"  {cat}:")) or 0.0
            variable[cat] = val

        total_fixed = sum(fixed.values())
        total_variable = sum(variable.values())
        total_exp = total_fixed + total_variable
        surplus = income - total_exp
        self.profile.monthly_expenses = total_exp

        print("\n" + "=" * 60)
        print("  YOUR MONTHLY BUDGET")
        print("=" * 60)
        print(f"  Take-Home Income:      {format_currency(income)}")
        print(f"  Total Fixed Expenses:  {format_currency(total_fixed)}")
        print(f"  Total Variable Exp.:   {format_currency(total_variable)}")
        print(f"  Total Expenses:        {format_currency(total_exp)}")
        print(f"  Monthly Surplus:       {format_currency(surplus)}")
        if income > 0:
            print(f"  Savings Rate:          {(max(0, surplus) / income * 100):.1f}%")
        print("=" * 60)

        # 50/30/20 analysis
        if income > 0:
            needs_pct = total_fixed / income * 100
            wants_pct = total_variable / income * 100
            savings_pct = max(0, surplus / income * 100)
            print("\n📐 50/30/20 Rule Analysis:")
            print(f"  Needs (fixed):   {needs_pct:.1f}%  (target ≤ 50%)")
            print(f"  Wants (variable): {wants_pct:.1f}%  (target ≤ 30%)")
            print(f"  Savings/Debt:    {savings_pct:.1f}%  (target ≥ 20%)")

        if surplus < 0:
            print(wrap_text(
                "\n⚠️  You're spending more than you earn! "
                "Look for the largest variable expenses to cut first. "
                "Even a 10% reduction can make a significant difference."
            ))
        elif surplus < income * 0.1:
            print(wrap_text(
                "\nYou have a thin surplus. Try to build an emergency fund of "
                "3-6 months of expenses before focusing on investing."
            ))
        else:
            print(wrap_text(
                f"\n✅ You have a surplus of {format_currency(surplus)}/month. "
                "Prioritize: 1) Emergency fund, 2) High-interest debt, 3) Retirement accounts, "
                "4) Additional investments."
            ))

        # Top expense by category
        all_expenses = {**fixed, **variable}
        top_exp = sorted(all_expenses.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_exp:
            print("\n🔍 Your top 3 expenses:")
            for cat, val in top_exp:
                print(f"  • {cat.title()}: {format_currency(val)}")

    # ------------------------------------------------------------------
    # Goal planner
    # ------------------------------------------------------------------

    def _goal_planner(self) -> None:
        print_header("Goal Planner 🎯")
        print(wrap_text(
            "Let's plan for your big financial goals. I'll help you figure out "
            "exactly what you need to save each month to get there."
        ))

        goals = [
            ("Emergency fund", 3),
            ("Vacation", 2),
            ("New car (down payment)", 3),
            ("Home down payment", 3),
            ("Child's education fund", 2),
            ("Early retirement / FIRE", 3),
            ("Other custom goal", 1),
        ]
        print("Which goal would you like to plan for?")
        for i, (g, _) in enumerate(goals, 1):
            print(f"  {i}. {g}")

        choice = prompt("Choose a number:").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(goals)):
            print("Invalid choice.")
            return

        idx = int(choice) - 1
        goal_name, _ = goals[idx]

        if goal_name == "Other custom goal":
            goal_name = prompt("What is your goal?:")

        target_str = prompt(f"How much money do you need for {goal_name}? ($):")
        target = parse_number(target_str)
        if not target:
            print("Please enter a valid dollar amount.")
            return

        current_str = prompt("How much have you already saved toward this goal? ($):")
        current = parse_number(current_str) or 0.0
        remaining = max(0.0, target - current)

        rate_str = prompt("Expected annual return on savings (e.g. 5 for 5%; use 2 for savings account):")
        rate = (parse_number(rate_str) or 5.0) / 100

        monthly_str = prompt("How much can you set aside per month for this goal? ($):")
        monthly = parse_number(monthly_str) or 0.0

        months = months_to_goal(monthly, remaining, rate) if monthly > 0 else 0

        print("\n" + "=" * 60)
        print(f"  GOAL: {goal_name.upper()}")
        print("=" * 60)
        print(f"  Target Amount:       {format_currency(target)}")
        print(f"  Already Saved:       {format_currency(current)}")
        print(f"  Still Needed:        {format_currency(remaining)}")
        if monthly > 0:
            print(f"  Monthly Contribution: {format_currency(monthly)}")
            print(f"  Expected Rate:        {rate * 100:.1f}%/year")
            years = months // 12
            extra_months = months % 12
            print(f"  Time to Goal:         {years} yr {extra_months} mo  ({months} months)")
        else:
            print("  Set a monthly amount to see your timeline!")
        print("=" * 60)

        # Specific tips per goal type
        tips_map = {
            "Emergency fund": (
                "Keep your emergency fund in a High-Yield Savings Account (HYSA) — "
                "currently paying 4-5% APY. Don't invest it in stocks."
            ),
            "Vacation": (
                "Open a dedicated savings account just for vacation. "
                "Use travel rewards credit cards (paid in full each month) to earn "
                "free flights and hotel stays."
            ),
            "Home down payment": (
                "A 20% down payment avoids PMI (Private Mortgage Insurance), "
                "saving you thousands. Consider an FHSA or first-time homebuyer programs "
                "in your state for extra assistance."
            ),
            "Early retirement / FIRE": (
                "FIRE = Financial Independence, Retire Early. Aim for 25x your "
                "annual expenses (the '4% rule'). Max out 401(k), Roth IRA, and "
                "HSA before taxable brokerage accounts."
            ),
        }
        tip = tips_map.get(goal_name)
        if tip:
            print(f"\n💡 Richy's Tip: {wrap_text(tip)}")

        if self.profile.monthly_income > 0 and monthly > 0:
            pct = monthly / self.profile.monthly_income * 100
            print(wrap_text(
                f"\nThis goal will use {pct:.1f}% of your monthly take-home pay. "
                + ("That's very manageable!" if pct < 15 else
                   "That's significant — make sure your budget can handle it.")
            ))

    # ------------------------------------------------------------------
    # Mortgage calculator
    # ------------------------------------------------------------------

    def _mortgage_calculator(self) -> None:
        print_header("Mortgage Calculator 🏠")

        price_str = prompt("What is the home purchase price? ($):")
        price = parse_number(price_str)
        if not price:
            return

        down_str = prompt("Down payment amount or percentage? (e.g. 20000 or 20%):")
        down_raw = down_str.strip()
        if "%" in down_raw:
            pct = parse_number(down_raw) or 20.0
            down = price * pct / 100
        else:
            down = parse_number(down_raw) or price * 0.20

        principal = price - down

        rate_str = prompt("Annual interest rate? (e.g. 6.5 for 6.5%):")
        annual_rate = (parse_number(rate_str) or 6.5) / 100

        years_str = prompt("Loan term in years? (15 or 30):")
        years = int(parse_number(years_str) or 30)

        pmi = 0.0
        if down / price < 0.20:
            pmi = principal * 0.008 / 12  # ~0.8% per year

        monthly = mortgage_payment(principal, annual_rate, years)
        total_paid = monthly * years * 12
        total_interest = total_paid - principal

        prop_tax_monthly = price * 0.012 / 12  # ~1.2% property tax
        insurance_monthly = price * 0.005 / 12  # ~0.5% homeowners insurance
        total_monthly = monthly + prop_tax_monthly + insurance_monthly + pmi

        print("\n" + "=" * 60)
        print("  MORTGAGE SUMMARY")
        print("=" * 60)
        print(f"  Home Price:             {format_currency(price)}")
        print(f"  Down Payment:           {format_currency(down)} ({down/price*100:.1f}%)")
        print(f"  Loan Amount:            {format_currency(principal)}")
        print(f"  Interest Rate:          {annual_rate*100:.2f}%")
        print(f"  Loan Term:              {years} years")
        print_divider()
        print(f"  Monthly P&I Payment:    {format_currency(monthly)}")
        print(f"  Est. Property Tax/Mo:   {format_currency(prop_tax_monthly)}")
        print(f"  Est. Insurance/Mo:      {format_currency(insurance_monthly)}")
        if pmi > 0:
            print(f"  PMI (until 20% equity): {format_currency(pmi)}")
        print(f"  Total Monthly Cost:     {format_currency(total_monthly)}")
        print_divider()
        print(f"  Total Interest Paid:    {format_currency(total_interest)}")
        print(f"  Total Amount Paid:      {format_currency(total_paid)}")
        print("=" * 60)

        if self.profile.monthly_income > 0:
            dti = total_monthly / self.profile.monthly_income * 100
            print(f"\n  Debt-to-Income Ratio:   {dti:.1f}%")
            if dti > 43:
                print(wrap_text(
                    "  ⚠️  Your DTI exceeds 43% — lenders may not approve this loan. "
                    "Consider a less expensive home or a larger down payment."
                ))
            elif dti > 28:
                print(wrap_text(
                    "  ⚠️  Your housing cost exceeds 28% of income (traditional guideline). "
                    "You may qualify but it could strain your budget."
                ))
            else:
                print("  ✅ Your housing cost is within healthy guidelines.")

    # ------------------------------------------------------------------
    # Insurance overview
    # ------------------------------------------------------------------

    def _insurance_overview(self) -> None:
        print_header("Insurance Guide 🛡️")
        print(wrap_text(
            "Insurance protects you from financial catastrophe. "
            "Here's a breakdown of the key types and what you need to know."
        ))

        types = [
            (
                "Health Insurance",
                "The most critical. If you have an employer plan, contribute enough to "
                "get the full match. Also consider a High-Deductible Health Plan (HDHP) "
                "paired with an HSA for triple tax savings. "
                "Key metrics: premium, deductible, out-of-pocket max.",
            ),
            (
                "Life Insurance",
                "If anyone depends on your income, you need life insurance. "
                "Term life (10-30 year policies) is almost always best for most people. "
                "Rule of thumb: 10-12x your annual income in coverage. "
                "Avoid whole life/universal life unless you've maxed all tax-advantaged accounts.",
            ),
            (
                "Disability Insurance",
                "Often overlooked — but your ability to earn income IS your biggest asset. "
                "Long-term disability insurance replaces 60-70% of your income if you can't work. "
                "Many employers offer this; supplement if the coverage is low.",
            ),
            (
                "Auto Insurance",
                "Required by law. Carry enough liability coverage to protect your assets "
                "(at least $100k/$300k). Raise your deductible to lower premiums if you have "
                "a solid emergency fund.",
            ),
            (
                "Homeowners / Renters Insurance",
                "Homeowners covers your dwelling and belongings. "
                "Renters insurance is incredibly cheap (~$15/mo) and covers your personal "
                "property and liability — every renter should have it.",
            ),
            (
                "Umbrella Insurance",
                "Extra liability coverage beyond your auto and home policies. "
                "$1M in umbrella coverage typically costs ~$200/year. "
                "Essential if you have significant assets or a high-earning career.",
            ),
        ]

        for title, detail in types:
            print(f"\n🔹 {title}")
            print(wrap_text(f"   {detail}"))

        print(wrap_text(
            "\n💡 General Rule: Never skip health, life (if dependents), "
            "disability, and auto insurance. The rest depends on your situation."
        ))

    # ------------------------------------------------------------------
    # Free question
    # ------------------------------------------------------------------

    def _free_question(self) -> None:
        print_header("Ask Richy Anything 🤔")
        question = prompt("What financial question is on your mind?:")
        if not question:
            return

        context = ""
        if self.profile.monthly_income:
            context = (
                f"User's monthly take-home: {format_currency(self.profile.monthly_income)}. "
                f"Monthly expenses: {format_currency(self.profile.monthly_expenses)}. "
            )

        system_prompt = (
            "You are Agent Richy, a knowledgeable and friendly financial advisor for adults. "
            "Provide clear, actionable advice. Use concrete numbers when helpful. "
            "Keep answers under 200 words. Encourage the user."
        )
        user_msg = f"{context}\nQuestion: {question}"
        response = ask_llm(self.llm_client, system_prompt, user_msg)
        if response:
            print(f"\n💬 Richy says:\n{wrap_text(response)}")
        else:
            print(wrap_text(
                "\nHere's a foundational piece of financial wisdom: "
                "Before investing, make sure you have (1) an emergency fund of 3-6 months "
                "of expenses, (2) no high-interest debt, and (3) are contributing enough "
                "to your 401(k) to get the full employer match. "
                "Those three steps alone put you ahead of most people."
            ))
