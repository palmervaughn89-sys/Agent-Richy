"""Adult financial planning module for Agent Richy.

Covers: deep financial assessment, paycheck-to-paycheck escape plan,
bad-habit identifier, subscription audit, debt payoff strategies,
tax estimator, in-depth budget simulation, mortgage calculator,
vacation planner (multi-year), investment portfolio builder,
insurance overview, and a free-form AI advisor.
"""

import math
from typing import Optional, Dict, List
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import (
    print_header,
    print_divider,
    print_tip,
    print_warning,
    print_success,
    prompt,
    parse_yes_no,
    parse_number,
    format_currency,
    wrap_text,
    ask_llm,
    choose_one,
    choose_many,
    progress_bar,
    load_investments,
    filter_investments,
)
from agent_richy.utils.video_generator import (
    is_video_generation_available,
    list_videos_for_audience,
    generate_video,
    show_lesson_without_video,
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

# ---------------------------------------------------------------------------
# Bad financial habits (adults)
# ---------------------------------------------------------------------------
BAD_HABITS_ADULT = [
    ("Living paycheck to paycheck with no emergency fund",
     "Start with $500 mini-emergency fund in a HYSA.  Automate $25-$50/week "
     "from your checking to savings the day AFTER payday."),
    ("Only paying minimum on credit cards",
     "Minimum payments = maximum interest.  Attack the highest-rate card first "
     "(avalanche method) or smallest balance first (snowball method) for momentum."),
    ("Impulse buying / retail therapy",
     "Implement the 72-hour rule: wait 3 days before any purchase over $50.  "
     "Unsubscribe from marketing emails.  Remove saved credit cards from apps."),
    ("Eating out too often / food delivery apps",
     "Track food spending for 2 weeks — most people are shocked.  "
     "Meal-prep Sundays can cut food costs by 50-70 %.  Aim for max 2 eat-outs/week."),
    ("Subscription creep (streaming, apps, memberships)",
     "Audit every subscription TODAY.  Cancel anything you haven't used in 30 days.  "
     "Average American wastes $240/month on unused subscriptions."),
    ("No budget — 'winging it' every month",
     "A budget is a PLAN, not a punishment.  Use the 50/30/20 rule as a starting point.  "
     "Track with a free app or even a simple spreadsheet."),
    ("Taking on car debt you can't afford",
     "The 20/4/10 rule: 20 % down, 4-year loan max, payment ≤ 10 % of gross income.  "
     "Buy reliable used cars and invest the difference."),
    ("Ignoring retirement savings / no 401(k) contributions",
     "At MINIMUM contribute enough to get the full employer match — it's free money.  "
     "$500/mo from age 30 at 8 % = ~$750 K by age 60."),
    ("Lifestyle inflation (spending more as you earn more)",
     "When you get a raise, invest at least 50 % of the increase BEFORE adjusting "
     "your lifestyle.  Your future self will thank you."),
    ("Not having adequate insurance",
     "One hospital stay can bankrupt you.  Ensure you have health, auto, and "
     "(if anyone depends on you) term life insurance.  Renters insurance is ~$15/mo."),
]

# ---------------------------------------------------------------------------
# Pure utility functions
# ---------------------------------------------------------------------------

def estimate_federal_tax(gross_income: float, filing_status: str = "single") -> dict:
    """Return an estimate of federal income tax using 2024 brackets."""
    deduction = (
        STANDARD_DEDUCTION_MFJ if filing_status.lower() in ("mfj", "married", "joint")
        else STANDARD_DEDUCTION_SINGLE
    )
    taxable = max(0.0, gross_income - deduction)

    tax = 0.0
    prev_limit = 0.0
    for limit, rate in TAX_BRACKETS_SINGLE:
        if taxable <= prev_limit:
            break
        bracket_income = min(taxable, limit) - prev_limit
        tax += bracket_income * rate
        prev_limit = limit

    effective_rate = (tax / gross_income * 100) if gross_income else 0.0
    fica = min(gross_income, 168_600) * 0.0765

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
    """Monthly mortgage payment using standard amortization."""
    monthly_rate = annual_rate / 12
    n = years * 12
    if monthly_rate == 0:
        return principal / n
    return principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)


def months_to_goal(monthly_saving: float, goal: float, annual_rate: float = 0.05) -> int:
    """Months to reach a savings goal with compound interest."""
    if monthly_saving <= 0:
        return 0
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return math.ceil(goal / monthly_saving)
    n = math.log(1 + (goal * monthly_rate) / monthly_saving) / math.log(1 + monthly_rate)
    return math.ceil(n)


def debt_payoff_schedule(balance: float, apr: float, monthly_payment: float) -> List[Dict]:
    """Return month-by-month debt-payoff schedule."""
    schedule = []
    remaining = balance
    month = 0
    while remaining > 0 and month < 600:
        month += 1
        interest = remaining * (apr / 12)
        principal_paid = min(monthly_payment - interest, remaining)
        if principal_paid <= 0:
            break  # payment doesn't cover interest
        remaining -= principal_paid
        schedule.append({
            "month": month,
            "payment": monthly_payment,
            "interest": interest,
            "principal": principal_paid,
            "remaining": max(0, remaining),
        })
    return schedule


# ===================================================================
# Module class
# ===================================================================


class AdultModule:
    """Interactive financial planning tools for adult users."""

    def __init__(self, profile: UserProfile, llm_client=None):
        self.profile = profile
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------

    def run(self) -> None:
        print_header(f"Welcome, {self.profile.name}!  I'm Agent Richy 💰")
        print(wrap_text(
            "I'm your personal financial planning assistant.  Whether you need "
            "help with taxes, budgeting, crushing debt, planning a vacation, or "
            "building real wealth — I'm here to guide you every step of the way.  "
            "Let's take control of your money. 💪"
        ))

        if not self.profile.completed_assessment:
            do_assess = parse_yes_no(prompt(
                "Want to do a full financial assessment first? "
                "It helps me give personalized advice. (yes/no):"
            ))
            if do_assess:
                self._financial_assessment()

        while True:
            print_divider()
            print("\n🏠 MAIN MENU")
            print("   1.  📋 Full financial assessment")
            print("   2.  📊 Budget simulation (50/30/20)")
            print("   3.  🚨 Paycheck-to-paycheck escape plan")
            print("   4.  🚫 Bad financial habits check")
            print("   5.  📺 Subscription audit")
            print("   6.  💳 Debt destroyer (snowball / avalanche)")
            print("   7.  🧾 Tax estimator")
            print("   8.  🏠 Mortgage calculator")
            print("   9.  🏖️  Vacation planner (multi-year)")
            print("  10.  🎯 Goal planner")
            print("  11.  📈 Investment portfolio builder")
            print("  12.  🛡️  Insurance guide")
            print("  13.  🎬 Video lessons (AI-generated)")
            print("  14.  🤖 Ask Richy anything")
            print("  15.  📋 My financial snapshot")
            print("  16.  Exit")
            choice = prompt("Choose an option (1-16):").strip()

            actions = {
                "1": self._financial_assessment,
                "2": self._budget_simulation,
                "3": self._paycheck_escape_plan,
                "4": self._bad_habits_check,
                "5": self._subscription_audit,
                "6": self._debt_destroyer,
                "7": self._tax_helper,
                "8": self._mortgage_calculator,
                "9": self._vacation_planner,
                "10": self._goal_planner,
                "11": self._investment_builder,
                "12": self._insurance_overview,
                "13": self._video_lessons,
                "14": self._free_question,
                "15": self._financial_snapshot,
            }
            if choice == "16":
                print("\nStay disciplined, stay focused.  Your financial future is bright! 🌟")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Please enter a number between 1 and 16.")

    # ------------------------------------------------------------------
    # 1 — Full financial assessment
    # ------------------------------------------------------------------

    def _financial_assessment(self) -> None:
        print_header("Full Financial Assessment 📋")
        print(wrap_text(
            "Let's get a complete picture of your finances.  I'll ask about income, "
            "expenses, debts, savings, and habits so I can give you the best advice "
            "possible.  Be honest — this is for YOU, not for anyone else."
        ))

        # Name / age
        name = prompt("What's your name?:")
        if name:
            self.profile.name = name
        age = parse_number(prompt("How old are you?:"))
        if age:
            self.profile.age = int(age)

        # Income
        print_header("Income 💵")
        income = parse_number(prompt("Monthly take-home income (after taxes)?:")) or 0.0
        self.profile.monthly_income = income

        other_income = parse_number(prompt("Any other monthly income? (side gig, rental, etc.):")) or 0.0
        self.profile.monthly_income += other_income

        # Savings & emergency fund
        print_header("Savings & Emergency Fund 🏦")
        self.profile.savings_balance = parse_number(prompt("Total savings balance?:")) or 0.0
        self.profile.emergency_fund = parse_number(prompt("How much is specifically set aside as an emergency fund?:")) or 0.0

        # Credit score
        score_str = prompt("Do you know your credit score? (Enter number, or 0 if unsure):")
        score = parse_number(score_str)
        if score and score > 300:
            self.profile.credit_score = int(score)

        # Debts
        print_header("Debts 💳")
        has_debt = parse_yes_no(prompt("Do you have any debts? (yes/no):"))
        if has_debt:
            debt_types = [
                "Credit cards", "Student loans", "Car loan",
                "Personal loan", "Medical debt", "Other",
            ]
            print("What types of debt do you have?")
            chosen = choose_many("Select all that apply:", debt_types)
            for idx in chosen:
                dtype = debt_types[idx]
                bal = parse_number(prompt(f"  {dtype} — total balance?:")) or 0.0
                rate = parse_number(prompt(f"  {dtype} — interest rate (APR %)?:")) or 0.0
                mpay = parse_number(prompt(f"  {dtype} — minimum monthly payment?:")) or 0.0
                self.profile.debts[dtype] = bal
                self.profile.debt_interest_rates[dtype] = rate / 100
            self.profile.debt_balance = sum(self.profile.debts.values())

        # Monthly expenses overview
        print_header("Monthly Expenses 💸")
        print("Give rough monthly estimates:\n")
        expense_cats = [
            "Rent / mortgage", "Car payment", "Groceries",
            "Utilities (electric, gas, water, internet)",
            "Insurance premiums", "Dining out / food delivery",
            "Gas / transportation", "Subscriptions (streaming, gym, etc.)",
            "Clothing / shopping", "Entertainment / hobbies",
            "Childcare / child expenses", "Miscellaneous",
        ]
        total_exp = 0.0
        for cat in expense_cats:
            val = parse_number(prompt(f"  {cat}:")) or 0.0
            total_exp += val
        self.profile.monthly_expenses = total_exp

        # Paycheck-to-paycheck check
        surplus = self.profile.monthly_income - self.profile.monthly_expenses
        if surplus <= self.profile.monthly_income * 0.05 and self.profile.emergency_fund < self.profile.monthly_expenses * 1:
            self.profile.paycheck_to_paycheck = True

        self.profile.completed_assessment = True

        # Print summary
        print_header("Your Financial Summary 📊")
        print(f"  Monthly Income:     {format_currency(self.profile.monthly_income)}")
        print(f"  Monthly Expenses:   {format_currency(self.profile.monthly_expenses)}")
        print(f"  Monthly Surplus:    {format_currency(surplus)}")
        if self.profile.monthly_income > 0:
            print(f"  Savings Rate:       {max(0, surplus / self.profile.monthly_income * 100):.1f} %")
        print_divider()
        print(f"  Total Savings:      {format_currency(self.profile.savings_balance)}")
        print(f"  Emergency Fund:     {format_currency(self.profile.emergency_fund)}")
        efm = self.profile.months_of_emergency()
        ef_bar = progress_bar(efm, 6)
        print(f"  Emergency Coverage: {efm:.1f} months {ef_bar}")
        if self.profile.credit_score:
            print(f"  Credit Score:       {self.profile.credit_score}")
        print_divider()
        if self.profile.debts:
            print(f"  Total Debt:         {format_currency(self.profile.total_debt())}")
            for label, bal in self.profile.debts.items():
                rate_pct = self.profile.debt_interest_rates.get(label, 0) * 100
                print(f"    • {label}: {format_currency(bal)} @ {rate_pct:.1f} %")

        # Priority recommendations
        print_header("Richy's Priority Recommendations 🎯")
        priorities = []
        if efm < 1:
            priorities.append("🚨 URGENT: Build a $1,000 mini emergency fund ASAP")
        elif efm < 3:
            priorities.append("⚠️  Build emergency fund to 3 months of expenses")
        elif efm < 6:
            priorities.append("📈 Continue building emergency fund to 6 months")

        high_rate_debt = {k: v for k, v in self.profile.debt_interest_rates.items() if v > 0.10}
        if high_rate_debt:
            worst = max(high_rate_debt, key=high_rate_debt.get)
            priorities.append(f"🔥 Attack high-interest debt: {worst} @ {high_rate_debt[worst]*100:.0f} %")

        if self.profile.paycheck_to_paycheck:
            priorities.append("💡 You're living paycheck-to-paycheck — try the escape plan (menu #3)")

        if surplus > 0 and not self.profile.debts:
            priorities.append("📈 Start investing!  Even $100/month in an index fund builds wealth")

        if not priorities:
            priorities.append("✅ You're in great shape!  Focus on growing investments and enjoying life.")

        for i, p in enumerate(priorities, 1):
            print(f"  {i}. {p}")

        # LLM personalized advice
        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy, a financial advisor for adults who are often "
                "struggling paycheck to paycheck.  Based on the user's financial data, "
                "give 3 specific, actionable recommendations in priority order.  "
                "Be empathetic, practical, and motivating.  Use real numbers.  Under 200 words."
            ),
            user_message=(
                f"Income: {format_currency(self.profile.monthly_income)}/mo, "
                f"Expenses: {format_currency(self.profile.monthly_expenses)}/mo, "
                f"Surplus: {format_currency(surplus)}/mo, "
                f"Savings: {format_currency(self.profile.savings_balance)}, "
                f"Emergency fund: {format_currency(self.profile.emergency_fund)} ({efm:.1f} months), "
                f"Debt: {self.profile.debts or 'None'}, "
                f"Age: {self.profile.age}"
            ),
        )
        if resp:
            print(f"\n🤖 Richy's Personalized Advice:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 2 — Budget simulation
    # ------------------------------------------------------------------

    def _budget_simulation(self) -> None:
        print_header("Budget Simulation 📊")
        print(wrap_text(
            "Let's build a detailed picture of your finances.  "
            "I'll ask about income, fixed costs, variable spending, "
            "and show you where you stand and how to improve."
        ))

        income = self.profile.monthly_income
        if income == 0:
            income = parse_number(prompt("Monthly take-home income (after taxes)?:")) or 0.0
            self.profile.monthly_income = income

        print("\n--- Fixed Monthly Expenses ---")
        fixed_cats = [
            "rent / mortgage", "car payment", "student loans",
            "insurance premiums (health, auto, life)",
            "utilities (electric, gas, water)",
            "internet / phone", "subscriptions (streaming, gym, etc.)",
        ]
        fixed = {}
        for cat in fixed_cats:
            fixed[cat] = parse_number(prompt(f"  {cat}:")) or 0.0

        print("\n--- Variable Monthly Expenses ---")
        var_cats = [
            "groceries", "dining out / food delivery",
            "gas / transportation", "clothing / shopping",
            "entertainment / hobbies", "personal care", "miscellaneous",
        ]
        variable = {}
        for cat in var_cats:
            variable[cat] = parse_number(prompt(f"  {cat}:")) or 0.0

        total_fixed = sum(fixed.values())
        total_var = sum(variable.values())
        total_exp = total_fixed + total_var
        surplus = income - total_exp
        self.profile.monthly_expenses = total_exp

        print("\n" + "=" * 60)
        print("  YOUR MONTHLY BUDGET")
        print("=" * 60)
        print(f"  Take-Home Income:      {format_currency(income)}")
        print(f"  Total Fixed Expenses:  {format_currency(total_fixed)}")
        print(f"  Total Variable Exp.:   {format_currency(total_var)}")
        print(f"  Total Expenses:        {format_currency(total_exp)}")
        print(f"  Monthly Surplus:       {format_currency(surplus)}")
        if income > 0:
            print(f"  Savings Rate:          {max(0, surplus / income * 100):.1f} %")
        print("=" * 60)

        # 50/30/20 analysis
        if income > 0:
            needs_pct = total_fixed / income * 100
            wants_pct = total_var / income * 100
            save_pct = max(0, surplus / income * 100)
            print("\n📐 50/30/20 Rule Analysis:")
            print(f"  Needs (fixed):    {needs_pct:.1f} %  (target ≤ 50 %)  {'✅' if needs_pct <= 50 else '⚠️'}")
            print(f"  Wants (variable): {wants_pct:.1f} %  (target ≤ 30 %)  {'✅' if wants_pct <= 30 else '⚠️'}")
            print(f"  Savings/Debt:     {save_pct:.1f} %  (target ≥ 20 %)  {'✅' if save_pct >= 20 else '⚠️'}")

        if surplus < 0:
            print_warning(
                "You're spending more than you earn!  "
                "Look for the largest variable expenses to cut first."
            )
        elif surplus < income * 0.1:
            print(wrap_text(
                "\nThin surplus — build an emergency fund of 3-6 months expenses "
                "before investing."
            ))
        else:
            print_success(
                f"Surplus of {format_currency(surplus)}/month!  "
                "Prioritize: 1) Emergency fund, 2) High-interest debt, "
                "3) Retirement accounts, 4) Investments."
            )

        # Top 3 expenses
        all_exp = {**fixed, **variable}
        top3 = sorted(all_exp.items(), key=lambda x: x[1], reverse=True)[:3]
        if top3 and top3[0][1] > 0:
            print("\n🔍 Your top 3 expenses:")
            for cat, val in top3:
                print(f"  • {cat.title()}: {format_currency(val)}")
                print(f"    → Cut by 20 % = save {format_currency(val * 0.20)}/month = {format_currency(val * 0.20 * 12)}/year")

        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy.  Analyze this adult's budget and give 3 specific, "
                "actionable tips with dollar amounts.  Be empathetic and practical.  Under 150 words."
            ),
            user_message=f"Income: {income}, Fixed: {fixed}, Variable: {variable}, Surplus: {surplus}",
        )
        if resp:
            print(f"\n🤖 Richy's Budget Tips:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 3 — Paycheck-to-paycheck escape plan
    # ------------------------------------------------------------------

    def _paycheck_escape_plan(self) -> None:
        print_header("Paycheck-to-Paycheck Escape Plan 🚨")
        print(wrap_text(
            "78 % of Americans live paycheck to paycheck.  If that's you, "
            "NO SHAME — but let's get you OUT of that cycle.  Here's your plan:"
        ))

        income = self.profile.monthly_income
        if income == 0:
            income = parse_number(prompt("Monthly take-home income?:")) or 0.0
            self.profile.monthly_income = income

        expenses = self.profile.monthly_expenses
        if expenses == 0:
            expenses = parse_number(prompt("Total monthly expenses?:")) or 0.0
            self.profile.monthly_expenses = expenses

        surplus = income - expenses
        ef = self.profile.emergency_fund

        print_header("Phase 1: Stop the Bleeding 🩹")
        print(wrap_text(
            "Before anything else, we need to find SOME money to start saving.  "
            "Even $50/month changes the game."
        ))

        cuts = []
        print("\nLet's find quick wins.  Do any of these apply?")
        quick_wins = [
            ("Cancel unused subscriptions", 30, "Average person wastes $30-$50/mo on these"),
            ("Cook at home 2 more nights/week", 80, "Take-out averages $15-$25/meal for a family"),
            ("Switch to a cheaper phone plan", 30, "Mint Mobile, Visible: $25-$30/mo vs $80+ for major carriers"),
            ("Brown-bag lunch 3 days/week", 60, "Lunch out = $10-$15. Home = $3-$5. Savings = $30-$60/mo"),
            ("Drop premium streaming (keep 1-2 max)", 25, "Netflix + Hulu + Disney + HBO = $60+/mo"),
            ("Negotiate car insurance rate", 40, "Call and ask for discounts. Shop around annually."),
        ]
        total_potential = 0.0
        for desc, savings_amt, detail in quick_wins:
            ans = parse_yes_no(prompt(f"  {desc}? (yes/no):"))
            if ans:
                cuts.append((desc, savings_amt))
                total_potential += savings_amt
                print(f"    → Potential savings: {format_currency(savings_amt)}/mo — {detail}")

        if total_potential > 0:
            print(f"\n🎯 Total potential monthly savings: {format_currency(total_potential)}")
            print(f"   That's {format_currency(total_potential * 12)} per YEAR!")
        else:
            print(wrap_text("\nEven if those don't apply, small changes add up.  Let's keep going."))

        print_header("Phase 2: Build a $1,000 Starter Emergency Fund 🏦")
        target = 1000.0
        already = min(ef, target)
        remaining = target - already
        print(f"  Current emergency fund: {format_currency(ef)}")
        print(f"  Target:                 {format_currency(target)}")
        print(f"  Still needed:           {format_currency(max(0, remaining))}")
        print(f"  Progress: {progress_bar(already, target)}")

        if total_potential > 0 and remaining > 0:
            months_needed = math.ceil(remaining / total_potential) if total_potential > 0 else 0
            print(f"\n  With your cuts, you'd hit $1,000 in ~{months_needed} months!")
        elif remaining <= 0:
            print_success("You already have your starter emergency fund!")

        print_header("Phase 3: Attack Debt 💳")
        if self.profile.debts:
            print("Your debts (sorted by interest rate, highest first):")
            sorted_debts = sorted(
                self.profile.debt_interest_rates.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for label, rate in sorted_debts:
                bal = self.profile.debts.get(label, 0)
                print(f"  • {label}: {format_currency(bal)} @ {rate*100:.1f} %")
            print(wrap_text(
                "\nUse the Debt Destroyer tool (menu #6) for a detailed payoff plan."
            ))
        else:
            print_success("No debt reported!  Skip to Phase 4.")

        print_header("Phase 4: Build Real Emergency Fund (3-6 months) 🛡️")
        target_ef = expenses * 3
        print(f"  3-month target: {format_currency(target_ef)}")
        print(f"  6-month target: {format_currency(expenses * 6)}")
        print(f"  Current:        {format_currency(ef)}")
        print(f"  Progress (3 mo): {progress_bar(ef, target_ef)}")

        print_header("Phase 5: Invest & Build Wealth 📈")
        print(wrap_text(
            "Once you have your emergency fund and no high-interest debt, "
            "START INVESTING.  The #1 move: contribute enough to your 401(k) "
            "to get the FULL employer match (that's 100 % return on your money).  "
            "Then consider a Roth IRA ($7,000/year max).  Then a taxable brokerage."
        ))

        if income > 0:
            invest_15 = income * 0.15
            print(f"\n  If you invest 15 % of income ({format_currency(invest_15)}/mo):")
            balance = 0.0
            mr = 0.08 / 12
            for _ in range(360):  # 30 years
                balance = balance * (1 + mr) + invest_15
            print(f"  In 30 years at 8 %: {format_currency(balance)}")

        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy.  The user is living paycheck to paycheck.  "
                f"Income: {format_currency(income)}/mo, expenses: {format_currency(expenses)}/mo, "
                f"emergency fund: {format_currency(ef)}, debt: {self.profile.debts or 'none'}.  "
                "Give a compassionate, specific 90-day action plan with weekly milestones.  "
                "Focus on quick wins.  Under 250 words."
            ),
            user_message="Help me escape the paycheck-to-paycheck cycle.",
        )
        if resp:
            print(f"\n🤖 Richy's 90-Day Escape Plan:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 4 — Bad habits check
    # ------------------------------------------------------------------

    def _bad_habits_check(self) -> None:
        print_header("Bad Financial Habits Check 🚫")
        print(wrap_text(
            "Let's see if any common money traps are holding you back.  "
            "Be honest — awareness is the first step to change."
        ))

        score = 0
        identified = []
        for i, (habit, fix) in enumerate(BAD_HABITS_ADULT, 1):
            ans = parse_yes_no(prompt(f"{i}. {habit}\n   Is this you? (yes/no):"))
            if ans:
                score += 1
                identified.append((habit, fix))
                print(f"   ✏️  Fix: {wrap_text(fix)}")
            else:
                print("   ✅ Not you — great!")

        total = len(BAD_HABITS_ADULT)
        print_header("Results 📊")
        print(f"  Bad habits found: {score}/{total}")
        print(f"  Financial health: {progress_bar(total - score, total)}")

        if score == 0:
            print_success("Zero bad habits — you're doing amazing!")
        elif score <= 3:
            print(wrap_text("\nFew areas to improve.  Fix ONE per month."))
        elif score <= 6:
            print(wrap_text(
                "\nSeveral habits to address.  Start with the one costing you "
                "the most money.  Small changes compound over time."
            ))
        else:
            print(wrap_text(
                "\nSubstantial work ahead — but recognizing these habits is powerful.  "
                "Most people never even think about this.  Let's build an action plan."
            ))

        self.profile.bad_habits = [h.split("(")[0].strip() for h, _ in identified]

        if identified:
            # Calculate estimated cost of bad habits
            print("\n💸 Estimated annual cost of your habits:")
            costs = {
                "Living paycheck": 0,
                "Only paying minimum": 2400,
                "Impulse buying": 3600,
                "Eating out": 4800,
                "Subscription creep": 2880,
                "No budget": 1200,
                "car debt": 3000,
                "Ignoring retirement": 6000,
                "Lifestyle inflation": 4000,
                "Not having adequate": 0,
            }
            total_cost = 0.0
            for habit, _ in identified:
                for key, cost in costs.items():
                    if key.lower() in habit.lower():
                        total_cost += cost
                        break
            if total_cost > 0:
                print(f"  Estimated: {format_currency(total_cost)}/year")
                print(f"  Over 10 years: {format_currency(total_cost * 10)}")
                print(f"  Over 10 years if invested: {format_currency(total_cost * 10 * 1.5)} (est. with returns)")

            resp = ask_llm(
                self.llm_client,
                system_prompt=(
                    "You are Agent Richy.  The user identified these bad habits: "
                    f"{', '.join(self.profile.bad_habits)}.  Create a 30-day challenge "
                    "to fix their costliest habit.  Be specific with daily actions.  "
                    "Empathetic and motivating.  Under 200 words."
                ),
                user_message=f"Income: {format_currency(self.profile.monthly_income)}, Age: {self.profile.age}",
            )
            if resp:
                print(f"\n🤖 Richy's 30-Day Fix:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 5 — Subscription audit
    # ------------------------------------------------------------------

    def _subscription_audit(self) -> None:
        print_header("Subscription Audit 📺")
        print(wrap_text(
            "The average American spends $219/month on subscriptions — and wastes "
            "about $133/month on ones they don't really use.  Let's audit yours."
        ))

        common_subs = [
            ("Netflix", 15.49), ("Hulu", 17.99), ("Disney+", 13.99),
            ("HBO Max", 16.99), ("Spotify/Apple Music", 10.99),
            ("Amazon Prime", 14.99), ("YouTube Premium", 13.99),
            ("Gym membership", 40.00), ("Cloud storage (iCloud/Google)", 2.99),
            ("News apps (NYT/WSJ)", 10.00), ("Gaming (Xbox/PS+)", 16.99),
            ("Meal-kit delivery", 60.00),
        ]

        print("\nCommon subscriptions — mark what you pay for:\n")
        subs = {}
        total = 0.0
        for name, typical in common_subs:
            ans = parse_yes_no(prompt(f"  {name} (~${typical:.2f}/mo)? (yes/no):"))
            if ans:
                actual = parse_number(prompt(f"    How much do you pay/month? (Enter for ~${typical:.2f}):")) or typical
                subs[name] = actual
                total += actual

        # Custom subs
        print("\nAny other subscriptions?")
        while True:
            extra = prompt("  Name (or Enter to finish):")
            if not extra:
                break
            cost = parse_number(prompt(f"  Monthly cost for {extra}?:")) or 0.0
            subs[extra] = cost
            total += cost

        self.profile.subscriptions = subs

        print_header("Subscription Summary 📊")
        for name, cost in sorted(subs.items(), key=lambda x: x[1], reverse=True):
            print(f"  {name:<30} {format_currency(cost):>10}/mo")
        print_divider()
        print(f"  {'TOTAL':<30} {format_currency(total):>10}/mo")
        print(f"  {'ANNUAL':<30} {format_currency(total * 12):>10}/yr")

        if self.profile.monthly_income > 0:
            pct = total / self.profile.monthly_income * 100
            print(f"\n  That's {pct:.1f} % of your monthly income.")

        # Which to keep/cut
        print_header("Keep, Downgrade, or Cancel? ✂️")
        savings_from_cuts = 0.0
        for name, cost in subs.items():
            action = prompt(f"  {name} ({format_currency(cost)}/mo) — Keep / Downgrade / Cancel?:").lower()
            if "cancel" in action:
                savings_from_cuts += cost
                print(f"    → Saves {format_currency(cost)}/mo = {format_currency(cost * 12)}/yr")
            elif "downgrade" in action:
                new_cost = parse_number(prompt(f"    New monthly cost after downgrade?:")) or cost * 0.5
                savings_from_cuts += (cost - new_cost)
                print(f"    → Saves {format_currency(cost - new_cost)}/mo")

        if savings_from_cuts > 0:
            print_header("Your Savings from This Audit 🎯")
            print(f"  Monthly savings: {format_currency(savings_from_cuts)}")
            print(f"  Annual savings:  {format_currency(savings_from_cuts * 12)}")
            # Investment projection
            balance = 0.0
            mr = 0.08 / 12
            for _ in range(120):
                balance = balance * (1 + mr) + savings_from_cuts
            print(f"  If invested (8 %, 10 yrs): {format_currency(balance)}")

    # ------------------------------------------------------------------
    # 6 — Debt destroyer
    # ------------------------------------------------------------------

    def _debt_destroyer(self) -> None:
        print_header("Debt Destroyer 💳🔥")
        print(wrap_text(
            "Let's build a strategy to crush your debt.  Two proven methods:\n"
            "  • AVALANCHE: Pay highest-interest first (saves the most money)\n"
            "  • SNOWBALL: Pay smallest balance first (quickest wins for motivation)"
        ))

        # Gather debts if not already assessed
        if not self.profile.debts:
            print("\nLet's list your debts:")
            while True:
                name = prompt("  Debt name (or Enter when done):")
                if not name:
                    break
                bal = parse_number(prompt(f"  {name} — balance?:")) or 0.0
                rate = (parse_number(prompt(f"  {name} — APR %?:")) or 0.0) / 100
                mpay = parse_number(prompt(f"  {name} — minimum monthly payment?:")) or 0.0
                self.profile.debts[name] = bal
                self.profile.debt_interest_rates[name] = rate

        if not self.profile.debts:
            print_success("No debts to crush — you're debt-free! 🎉")
            return

        total_debt = sum(self.profile.debts.values())
        print(f"\n  Total Debt: {format_currency(total_debt)}")

        extra = parse_number(prompt(
            "How much EXTRA can you throw at debt each month "
            "(beyond minimums)?:"
        )) or 0.0

        # Choose method
        method_idx = choose_one("Which method?", ["Avalanche (highest rate first)", "Snowball (smallest balance first)"])
        method = "avalanche" if method_idx == 0 else "snowball"

        # Sort debts
        if method == "avalanche":
            order = sorted(self.profile.debts.keys(),
                           key=lambda k: self.profile.debt_interest_rates.get(k, 0),
                           reverse=True)
        else:
            order = sorted(self.profile.debts.keys(),
                           key=lambda k: self.profile.debts[k])

        print_header(f"{'Avalanche' if method == 'avalanche' else 'Snowball'} Payoff Order 📋")
        for i, name in enumerate(order, 1):
            bal = self.profile.debts[name]
            rate = self.profile.debt_interest_rates.get(name, 0) * 100
            print(f"  {i}. {name}: {format_currency(bal)} @ {rate:.1f} %")

        # Simulate payoff for the top debt
        top = order[0]
        bal = self.profile.debts[top]
        rate = self.profile.debt_interest_rates.get(top, 0)
        min_pay = max(bal * 0.02, 25)  # rough minimum
        total_pay = min_pay + extra

        if total_pay <= bal * (rate / 12):
            print_warning(f"Your payment of {format_currency(total_pay)} doesn't cover "
                          f"monthly interest!  You need to pay more.")
        else:
            schedule = debt_payoff_schedule(bal, rate, total_pay)
            if schedule:
                total_months = len(schedule)
                total_interest = sum(s["interest"] for s in schedule)
                print(f"\n  Paying {format_currency(total_pay)}/mo on {top}:")
                print(f"    Paid off in:      {total_months} months ({total_months // 12} yr {total_months % 12} mo)")
                print(f"    Total interest:   {format_currency(total_interest)}")
                print(f"    Total paid:       {format_currency(total_pay * total_months)}")

                # Show a few milestones
                print(f"\n    {'Month':>6}  {'Balance':>12}  {'Int. Paid':>12}")
                for s in schedule:
                    if s["month"] <= 3 or s["month"] % 6 == 0 or s["month"] == total_months:
                        print(f"    {s['month']:>6}  {format_currency(s['remaining']):>12}  "
                              f"{format_currency(s['interest']):>12}")

        # Compare with just minimums
        if extra > 0:
            schedule_min = debt_payoff_schedule(bal, rate, min_pay)
            if schedule_min:
                interest_min = sum(s["interest"] for s in schedule_min)
                print(f"\n  Without extra payments (just {format_currency(min_pay)}/mo):")
                print(f"    Months:   {len(schedule_min)}")
                print(f"    Interest: {format_currency(interest_min)}")
                if schedule:
                    saved = interest_min - total_interest
                    print(f"\n  🎯 Your extra {format_currency(extra)}/mo saves you "
                          f"{format_currency(saved)} in interest!")

        print_tip(
            "Every extra dollar toward debt is a guaranteed return equal to "
            "your interest rate.  There is no investment that guarantees 20-25 %."
        )

    # ------------------------------------------------------------------
    # 7 — Tax helper
    # ------------------------------------------------------------------

    def _tax_helper(self) -> None:
        print_header("Tax Estimator 🧾")
        print(wrap_text(
            "Rough federal tax estimate based on 2024 brackets.  "
            "Always consult a CPA for your actual return."
        ))

        income = parse_number(prompt("GROSS annual income (before taxes)?:"))
        if not income:
            print("Could not parse.  Enter a number like 65000.")
            return

        filing = prompt("Filing status? (single / married):").lower()
        filing = "married" if "married" in filing or "joint" in filing else "single"

        result = estimate_federal_tax(income, filing)

        print("\n" + "=" * 60)
        print("  FEDERAL TAX ESTIMATE (2024)")
        print("=" * 60)
        for label, key in [
            ("Gross Income", "gross_income"), ("Standard Deduction", "standard_deduction"),
            ("Taxable Income", "taxable_income"), ("Federal Income Tax", "federal_tax"),
            ("FICA (SS + Medicare)", "fica_tax"), ("Total Tax", "total_tax"),
        ]:
            print(f"  {label + ':':<25} {format_currency(result[key])}")
        print(f"  {'Effective Rate:':<25} {result['effective_rate']:.1f} %")
        print(f"  {'Take-Home/Year:':<25} {format_currency(result['take_home'])}")
        print(f"  {'Take-Home/Month:':<25} {format_currency(result['take_home'] / 12)}")
        print("=" * 60)

        print("\n💡 Ways to Reduce Your Tax Bill:")
        tips = [
            "Contribute to a 401(k) — up to $23,000/yr reduces taxable income.",
            "Fund a Traditional IRA — up to $7,000/yr is deductible.",
            "Use an HSA if eligible — triple tax advantage.",
            "Track charitable donations for itemized deductions.",
            "Self-employed?  Deduct home office, internet, business expenses.",
        ]
        for t in tips:
            print(f"  • {t}")

        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy.  Give one specific, actionable tax tip in 2 sentences "
                "based on the user's income."
            ),
            user_message=f"Gross income: {income}, filing: {filing}",
        )
        if resp:
            print(f"\n🤖 Richy's personalized tip: {resp}")

    # ------------------------------------------------------------------
    # 8 — Mortgage calculator
    # ------------------------------------------------------------------

    def _mortgage_calculator(self) -> None:
        print_header("Mortgage Calculator 🏠")

        price = parse_number(prompt("Home purchase price?:"))
        if not price:
            return

        down_str = prompt("Down payment amount or percent? (e.g. 60000 or 20 %):").strip()
        if "%" in down_str:
            pct = parse_number(down_str) or 20.0
            down = price * pct / 100
        else:
            down = parse_number(down_str) or price * 0.20

        principal = price - down
        annual_rate = (parse_number(prompt("Annual interest rate? (e.g. 6.5):")) or 6.5) / 100
        years = int(parse_number(prompt("Loan term? (15 or 30):")) or 30)

        pmi = 0.0
        if down / price < 0.20:
            pmi = principal * 0.008 / 12

        monthly = mortgage_payment(principal, annual_rate, years)
        total_paid = monthly * years * 12
        total_interest = total_paid - principal
        prop_tax = price * 0.012 / 12
        insurance = price * 0.005 / 12
        total_monthly = monthly + prop_tax + insurance + pmi

        print("\n" + "=" * 60)
        print("  MORTGAGE SUMMARY")
        print("=" * 60)
        print(f"  Home Price:             {format_currency(price)}")
        print(f"  Down Payment:           {format_currency(down)} ({down/price*100:.1f} %)")
        print(f"  Loan Amount:            {format_currency(principal)}")
        print(f"  Interest Rate:          {annual_rate*100:.2f} %")
        print(f"  Loan Term:              {years} years")
        print_divider()
        print(f"  Monthly P&I:            {format_currency(monthly)}")
        print(f"  Est. Property Tax/Mo:   {format_currency(prop_tax)}")
        print(f"  Est. Insurance/Mo:      {format_currency(insurance)}")
        if pmi > 0:
            print(f"  PMI (until 20 % equity):{format_currency(pmi)}")
        print(f"  Total Monthly Cost:     {format_currency(total_monthly)}")
        print_divider()
        print(f"  Total Interest Paid:    {format_currency(total_interest)}")
        print(f"  Total Amount Paid:      {format_currency(total_paid)}")
        print("=" * 60)

        if self.profile.monthly_income > 0:
            dti = total_monthly / self.profile.monthly_income * 100
            print(f"\n  Debt-to-Income Ratio: {dti:.1f} %")
            if dti > 43:
                print_warning("DTI > 43 % — lenders may not approve.")
            elif dti > 28:
                print_warning("Housing > 28 % of income.  Could strain budget.")
            else:
                print_success("Housing cost within healthy guidelines.")

    # ------------------------------------------------------------------
    # 9 — Vacation planner
    # ------------------------------------------------------------------

    def _vacation_planner(self) -> None:
        print_header("Vacation Planner 🏖️")
        print(wrap_text(
            "Let's plan your dream vacation with a real savings strategy — "
            "even if it's 1, 2, or 5 years away.  No credit card debt needed!"
        ))

        dest = prompt("Where do you want to go?:")
        travelers = parse_number(prompt("How many people traveling?:")) or 1
        when_months = parse_number(prompt("How many months from now?:")) or 12

        print_header("Let's Estimate Costs ✈️")
        print("Enter estimates (or $0 if not applicable):\n")
        costs = {}
        for cat in ["Flights / transportation", "Hotel / lodging",
                     "Food & dining", "Activities / excursions",
                     "Shopping / souvenirs", "Travel insurance",
                     "Misc / buffer (10-20 % recommended)"]:
            costs[cat] = parse_number(prompt(f"  {cat}:")) or 0.0

        total = sum(costs.values())
        self.profile.vacation_target = total
        self.profile.vacation_deadline_months = int(when_months)

        print_header("Vacation Budget Summary 📋")
        for cat, val in costs.items():
            if val > 0:
                print(f"  {cat:<35} {format_currency(val):>10}")
        print_divider()
        print(f"  {'TOTAL':<35} {format_currency(total):>10}")
        print(f"  {'Per person':<35} {format_currency(total / travelers):>10}")

        # Savings plan
        monthly_needed = total / when_months if when_months > 0 else total
        weekly_needed = monthly_needed / 4.33

        print_header("Your Savings Plan 🗓️")
        print(f"  Goal:           {format_currency(total)}")
        print(f"  Deadline:       {int(when_months)} months")
        print(f"  Save/month:     {format_currency(monthly_needed)}")
        print(f"  Save/week:      {format_currency(weekly_needed)}")

        already = parse_number(prompt("How much have you already saved for this trip?:")) or 0.0
        self.profile.vacation_fund = already
        remaining = max(0, total - already)
        monthly_actual = remaining / when_months if when_months > 0 else remaining

        print(f"\n  Already saved:  {format_currency(already)}")
        print(f"  Still needed:   {format_currency(remaining)}")
        print(f"  Adjusted: save  {format_currency(monthly_actual)}/month")
        print(f"  Progress:       {progress_bar(already, total)}")

        if self.profile.monthly_income > 0:
            pct = monthly_actual / self.profile.monthly_income * 100
            print(f"\n  That's {pct:.1f} % of your monthly income.")
            if pct > 20:
                print_warning(
                    "That's a big chunk.  Consider extending the timeline or reducing costs."
                )
            else:
                print_success("Very doable!  Set up an auto-transfer to a dedicated savings account.")

        # Multi-year savings schedule
        print("\n📅 Month-by-Month Progress:")
        print(f"  {'Month':>6}  {'Saved':>12}  {'Remaining':>12}  {'Progress':>15}")
        saved = already
        for m in range(1, int(when_months) + 1):
            saved += monthly_actual
            rem = max(0, total - saved)
            if m <= 6 or m % 3 == 0 or m == int(when_months):
                print(f"  {m:>6}  {format_currency(saved):>12}  {format_currency(rem):>12}  "
                      f"{progress_bar(saved, total):>15}")

        print_tip(
            "Open a SEPARATE savings account labeled 'Vacation Fund'.  "
            "Automate transfers on payday so you never 'forget' to save."
        )

        # LLM money-saving travel tips
        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy, a travel & savings expert.  The user is planning "
                f"a trip to {dest} for {int(travelers)} people in {int(when_months)} months.  "
                f"Budget: {format_currency(total)}.  "
                "Give 5 specific money-saving travel tips for their destination.  "
                "Be practical and enthusiastic.  Under 200 words."
            ),
            user_message=f"Destination: {dest}, budget: {total}",
        )
        if resp:
            print(f"\n🤖 Richy's Travel-Saving Tips:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 10 — Goal planner
    # ------------------------------------------------------------------

    def _goal_planner(self) -> None:
        print_header("Goal Planner 🎯")
        print(wrap_text(
            "Let's plan for your big financial goals.  I'll figure out "
            "exactly what you need to save each month."
        ))

        goals = [
            "Emergency fund", "Vacation", "New car (down payment)",
            "Home down payment", "Child's education fund",
            "Early retirement / FIRE", "Wedding", "Start a business",
            "Other custom goal",
        ]
        idx = choose_one("Which goal?", goals)
        if idx is None:
            return
        goal_name = goals[idx]
        if goal_name == "Other custom goal":
            goal_name = prompt("What is your goal?:")

        target = parse_number(prompt(f"How much do you need for {goal_name}? ($):"))
        if not target:
            return
        current = parse_number(prompt("Already saved toward this?:")) or 0.0
        remaining = max(0, target - current)
        rate = (parse_number(prompt("Expected annual return? (5 = savings, 8 = invested):")) or 5.0) / 100
        monthly = parse_number(prompt("Monthly contribution?:")) or 0.0

        months = months_to_goal(monthly, remaining, rate) if monthly > 0 else 0

        print("\n" + "=" * 60)
        print(f"  GOAL: {goal_name.upper()}")
        print("=" * 60)
        print(f"  Target:           {format_currency(target)}")
        print(f"  Already Saved:    {format_currency(current)}")
        print(f"  Still Needed:     {format_currency(remaining)}")
        print(f"  Progress:         {progress_bar(current, target)}")
        if monthly > 0:
            print(f"  Monthly Amount:   {format_currency(monthly)}")
            print(f"  Expected Rate:    {rate*100:.1f} %/yr")
            yrs = months // 12
            mos = months % 12
            print(f"  Time to Goal:     {yrs} yr {mos} mo  ({months} months)")
        print("=" * 60)

        tips_map = {
            "Emergency fund": "Keep in a HYSA (4-5 % APY).  Don't invest it in stocks.",
            "Vacation": "Open a dedicated savings account.  Use travel rewards cards (paid in full).",
            "Home down payment": "20 % down avoids PMI.  Check first-time buyer programs in your state.",
            "Early retirement / FIRE": "FIRE = 25x annual expenses.  Max 401(k), Roth IRA, HSA first.",
            "Wedding": "Average US wedding costs $30K.  Budget ruthlessly.  Negotiate everything.",
            "Start a business": "Start lean.  Validate idea before investing heavily.  Keep your day job initially.",
        }
        tip = tips_map.get(goal_name)
        if tip:
            print_tip(tip)

        if self.profile.monthly_income > 0 and monthly > 0:
            pct = monthly / self.profile.monthly_income * 100
            label = "Very manageable!" if pct < 15 else "Significant — make sure the budget works."
            print(f"\n  Uses {pct:.1f} % of take-home pay.  {label}")

    # ------------------------------------------------------------------
    # 11 — Investment portfolio builder
    # ------------------------------------------------------------------

    def _investment_builder(self) -> None:
        print_header("Investment Portfolio Builder 📈")
        print(wrap_text(
            "Let's build a personalized investment portfolio based on your "
            "risk tolerance, interests, and goals.  I'll pull from real "
            "investment options to give you a starting point."
        ))

        # Risk tolerance
        risk_options = ["Conservative (low risk, stable)", "Moderate (balanced)",
                        "Aggressive (high growth, more volatility)",
                        "Very aggressive (maximum growth, crypto-included)"]
        risk_idx = choose_one("What's your risk tolerance?", risk_options)
        risk_map = {0: "low", 1: "medium", 2: "high", 3: "very high"}
        risk = risk_map.get(risk_idx, "medium")
        self.profile.risk_tolerance = risk

        # Themes
        theme_options = [
            "Technology / AI", "Clean energy / ESG", "Healthcare",
            "Real estate", "Crypto / blockchain", "Dividend income",
            "Broad market / diversified",
        ]
        theme_idxs = choose_many("What themes interest you?", theme_options)
        theme_map = {
            0: "AI", 1: "clean energy", 2: "healthcare",
            3: "real estate", 4: "crypto", 5: "income",
            6: "diversification",
        }
        themes = [theme_map[i] for i in theme_idxs]
        self.profile.themes = themes

        esg = parse_yes_no(prompt("Prefer ESG / socially responsible investing? (yes/no):"))
        self.profile.esg_preference = bool(esg)

        # Monthly investment amount
        invest_amount = parse_number(prompt("How much can you invest per month?:")) or 0.0

        # Build portfolio from real data
        print_header("Your Recommended Portfolio 📊")

        data = load_investments()
        all_instruments = []
        for category in data.values():
            all_instruments.extend(category)

        # Score each instrument
        scored = []
        for inst in all_instruments:
            score = 0
            # Risk match
            if inst.get("risk") == risk:
                score += 3
            elif risk == "very high" and inst.get("risk") in ("high", "very high"):
                score += 2
            elif risk == "medium" and inst.get("risk") in ("low", "medium"):
                score += 2
            elif risk == "low" and inst.get("risk") == "low":
                score += 3

            # Theme match
            inst_themes = [t.lower() for t in inst.get("themes", [])]
            for t in themes:
                if any(t.lower() in it for it in inst_themes):
                    score += 2

            # ESG
            if esg:
                esg_rank = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "N/A": 0}
                if esg_rank.get(inst.get("esg_score", "N/A"), 0) >= 4:
                    score += 2

            scored.append((score, inst))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_picks = scored[:8]

        if not top_picks:
            print("No matching investments found.")
            return

        # Allocation suggestion
        total_alloc = 0
        allocations = []

        # Core holdings (60%)
        print("🏗️  CORE HOLDINGS (60 % of portfolio):")
        core = [s for s in top_picks if s[1].get("type") in ("etf", "fund")][:3]
        core_pct = 60 // max(len(core), 1)
        for _, inst in core:
            pct = core_pct
            amt = invest_amount * pct / 100
            total_alloc += pct
            allocations.append((inst, pct))
            print(f"  • {inst['ticker']} — {inst['name']}")
            print(f"    {inst['description']}")
            print(f"    Risk: {inst['risk']}  |  Type: {inst['type']}  |  Allocation: {pct} % ({format_currency(amt)}/mo)")
            print()

        # Growth holdings (30%)
        print("🚀 GROWTH HOLDINGS (30 % of portfolio):")
        growth = [s for s in top_picks if s[1].get("type") == "stock"][:3]
        growth_pct = 30 // max(len(growth), 1)
        for _, inst in growth:
            pct = growth_pct
            amt = invest_amount * pct / 100
            total_alloc += pct
            allocations.append((inst, pct))
            print(f"  • {inst['ticker']} — {inst['name']}")
            print(f"    {inst['description']}")
            print(f"    Risk: {inst['risk']}  |  Allocation: {pct} % ({format_currency(amt)}/mo)")
            print()

        # Alternative holdings (10%)
        remaining_pct = 100 - total_alloc
        alt = [s for s in top_picks if s[1].get("type") in ("commodity", "crypto")][:2]
        if alt and remaining_pct > 0:
            print("🔮 ALTERNATIVE HOLDINGS (10 % of portfolio):")
            alt_pct = remaining_pct // max(len(alt), 1)
            for _, inst in alt:
                amt = invest_amount * alt_pct / 100
                allocations.append((inst, alt_pct))
                print(f"  • {inst['ticker']} — {inst['name']}")
                print(f"    {inst['description']}")
                print(f"    Risk: {inst['risk']}  |  Allocation: {alt_pct} % ({format_currency(amt)}/mo)")
                print()

        # Projection
        if invest_amount > 0:
            print_header("Growth Projection 📈")
            balance = 0.0
            rate_map = {"low": 0.05, "medium": 0.08, "high": 0.10, "very high": 0.12}
            annual = rate_map.get(risk, 0.08)
            mr = annual / 12
            print(f"  Investing {format_currency(invest_amount)}/mo at ~{annual*100:.0f} % avg return:\n")
            print(f"  {'Year':>6}  {'Balance':>14}  {'Contributed':>14}")
            for yr in [1, 2, 3, 5, 10, 15, 20, 25, 30]:
                b = 0.0
                for _ in range(yr * 12):
                    b = b * (1 + mr) + invest_amount
                c = invest_amount * 12 * yr
                print(f"  {yr:>6}  {format_currency(b):>14}  {format_currency(c):>14}")

        print_warning(
            "This is educational, not financial advice.  Past performance doesn't "
            "guarantee future returns.  Consider consulting a licensed advisor."
        )

        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy.  Based on the user's portfolio preferences "
                f"(risk: {risk}, themes: {themes}, ESG: {esg}), give 3 specific tips "
                "for getting started with investing.  Include platform recommendations "
                "(Fidelity, Schwab, Vanguard).  Under 150 words."
            ),
            user_message=f"Monthly investment: {format_currency(invest_amount)}, Age: {self.profile.age}",
        )
        if resp:
            print(f"\n🤖 Richy's Investing Tips:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 12 — Insurance overview
    # ------------------------------------------------------------------

    def _insurance_overview(self) -> None:
        print_header("Insurance Guide 🛡️")
        print(wrap_text(
            "Insurance protects you from financial catastrophe.  "
            "Here's what you need to know."
        ))

        types = [
            ("Health Insurance",
             "The most critical.  Get the full employer match.  Consider HDHP + HSA "
             "for triple tax savings.  Key metrics: premium, deductible, OOP max."),
            ("Life Insurance",
             "If anyone depends on your income → get term life.  10-12x annual income.  "
             "Avoid whole life/universal unless you've maxed all tax-advantaged accounts."),
            ("Disability Insurance",
             "Your earning ability IS your biggest asset.  LTD replaces 60-70 % of income.  "
             "Many employers offer it; supplement if coverage is low."),
            ("Auto Insurance",
             "Required by law.  At least $100K/$300K liability.  Raise deductible to "
             "lower premiums if you have a solid emergency fund."),
            ("Homeowners / Renters",
             "Renters insurance is ~$15/mo and covers personal property + liability.  "
             "Every renter should have it."),
            ("Umbrella Insurance",
             "$1M umbrella coverage costs ~$200/year.  Essential with significant assets."),
        ]

        for title, detail in types:
            print(f"\n🔹 {title}")
            print(wrap_text(f"   {detail}"))

        print_tip(
            "Never skip: health, auto, disability.  "
            "Add life (if dependents) and renters/homeowners.  Umbrella if you have assets."
        )

    # ------------------------------------------------------------------
    # 13 — Video lessons
    # ------------------------------------------------------------------

    def _video_lessons(self) -> None:
        print_header("Video Lessons 🎬 — Powered by CogVideoX AI")

        videos = list_videos_for_audience("high")  # adults get all videos
        if not videos:
            print("No video lessons available.")
            return

        can_gen = is_video_generation_available()
        if can_gen:
            print(wrap_text("CogVideoX available — I can generate AI videos!"))
        else:
            print(wrap_text(
                "Video generation requires GPU + 'diffusers'.  "
                "Showing storyboards + lessons instead."
            ))

        by_topic = {}
        for v in videos:
            by_topic.setdefault(v["topic"], []).append(v)

        flat = []
        num = 1
        for topic, items in by_topic.items():
            print(f"\n  📂 {topic.upper()}")
            for v in items:
                print(f"     {num}. {v['title']}")
                flat.append(v)
                num += 1

        choice = prompt("Pick a number (or Enter to skip):").strip()
        if not choice.isdigit():
            return
        pick = int(choice) - 1
        if not (0 <= pick < len(flat)):
            return

        v = flat[pick]
        if can_gen:
            go = parse_yes_no(prompt(f"Generate '{v['title']}'? (yes/no):"))
            if go:
                path = generate_video(v["key"])
                if path:
                    print_success(f"Saved: {path}")
            else:
                show_lesson_without_video(v["key"])
        else:
            show_lesson_without_video(v["key"])

        print(f"\n📚 Lesson: {v['lesson']}")

    # ------------------------------------------------------------------
    # 14 — Ask Richy anything
    # ------------------------------------------------------------------

    def _free_question(self) -> None:
        print_header("Ask Richy Anything 🤖")
        question = prompt("What financial question is on your mind?:")
        if not question:
            return

        ctx = []
        if self.profile.monthly_income:
            ctx.append(f"Monthly take-home: {format_currency(self.profile.monthly_income)}")
            ctx.append(f"Monthly expenses: {format_currency(self.profile.monthly_expenses)}")
        if self.profile.debts:
            ctx.append(f"Debts: {self.profile.debts}")
        if self.profile.savings_balance:
            ctx.append(f"Savings: {format_currency(self.profile.savings_balance)}")
        if self.profile.bad_habits:
            ctx.append(f"Working on: {', '.join(self.profile.bad_habits)}")
        if self.profile.age:
            ctx.append(f"Age: {self.profile.age}")

        system = (
            "You are Agent Richy, a knowledgeable, empathetic financial advisor "
            "for adults who are often struggling.  Give clear, actionable advice "
            "with concrete numbers.  Be encouraging but honest.  Under 200 words.\n"
            "User context: " + "; ".join(ctx)
        )
        resp = ask_llm(self.llm_client, system, question)
        if resp:
            print(f"\n💬 Richy says:\n{wrap_text(resp)}")
        else:
            print(wrap_text(
                "\nFoundational wisdom: Before investing, ensure you have "
                "(1) an emergency fund of 3-6 months expenses, "
                "(2) no high-interest debt, and "
                "(3) enough 401(k) contribution to get the full employer match.  "
                "Those three steps put you ahead of most people."
            ))

        if parse_yes_no(prompt("Another question? (yes/no):") or "no"):
            self._free_question()

    # ------------------------------------------------------------------
    # 15 — Financial snapshot
    # ------------------------------------------------------------------

    def _financial_snapshot(self) -> None:
        print_header(f"{self.profile.name}'s Financial Snapshot 📋")

        surplus = self.profile.monthly_surplus()
        print(f"  Name:             {self.profile.name}")
        print(f"  Age:              {self.profile.age or 'Not set'}")
        print_divider()
        print(f"  Monthly Income:   {format_currency(self.profile.monthly_income)}")
        print(f"  Monthly Expenses: {format_currency(self.profile.monthly_expenses)}")
        print(f"  Monthly Surplus:  {format_currency(surplus)}")
        if self.profile.monthly_income > 0:
            print(f"  Savings Rate:     {self.profile.savings_rate():.1f} %")
        print_divider()
        print(f"  Total Savings:    {format_currency(self.profile.savings_balance)}")
        print(f"  Emergency Fund:   {format_currency(self.profile.emergency_fund)} "
              f"({self.profile.months_of_emergency():.1f} months)")
        if self.profile.credit_score:
            print(f"  Credit Score:     {self.profile.credit_score}")
        print_divider()
        if self.profile.debts:
            print(f"  Total Debt:       {format_currency(self.profile.total_debt())}")
            for label, bal in self.profile.debts.items():
                rate = self.profile.debt_interest_rates.get(label, 0) * 100
                print(f"    • {label}: {format_currency(bal)} @ {rate:.1f} %")
        else:
            print("  Debt:             None 🎉")
        if self.profile.subscriptions:
            print(f"  Subscriptions:    {format_currency(self.profile.total_subscriptions())}/mo")
        if self.profile.bad_habits:
            print(f"  Working On:       {', '.join(self.profile.bad_habits)}")
        if self.profile.vacation_target > 0:
            print(f"  Vacation Goal:    {format_currency(self.profile.vacation_target)} "
                  f"(saved: {format_currency(self.profile.vacation_fund)})")
        print_divider()

        # Net worth estimate
        assets = self.profile.savings_balance + self.profile.emergency_fund
        liabilities = self.profile.total_debt()
        net = assets - liabilities
        print(f"\n  Estimated Net Worth: {format_currency(net)}")
        if net < 0:
            print(wrap_text("  (Negative net worth is common — focus on debt reduction.)"))
