"""Response cache — instant answers for common finance questions.

Two layers:
1. Pre-written cache of 30 common Q&A pairs with fuzzy keyword matching.
2. Session-level cache of LLM responses (same question → instant replay).
"""

import re
import time
import random
import hashlib
import streamlit as st
from typing import Optional, Tuple

# ── Pre-written expert responses ─────────────────────────────────────────
# Each entry: { "keywords": [...], "response": "..." }
# Responses are written in Coach Richy's warm, specific voice.

CACHED_RESPONSES: list[dict] = [
    {
        "keywords": ["compound interest", "what is compound"],
        "response": (
            "### What Is Compound Interest? 🌱\n\n"
            "Compound interest is when you earn interest **on your interest** — it's "
            "the single most powerful force in building wealth.\n\n"
            "**Example:** Put **$5,000** in a savings account earning **5% annually**, "
            "and in 10 years you'll have **$8,144** — without adding another dime. "
            "But if you also add **$200/month**, you'll have **$39,204** in 10 years.\n\n"
            "The key? **Start early.** Someone who invests from age 25–35 (10 years) often "
            "ends up with MORE than someone who invests from 35–65 (30 years). Time beats money.\n\n"
            "**Next Step:** Want me to calculate how much YOUR savings could grow? "
            "Tell me your starting amount and how much you can save monthly."
        ),
    },
    {
        "keywords": ["start investing", "how to invest", "begin investing"],
        "response": (
            "### How to Start Investing 📈\n\n"
            "Here's the smartest order for a beginner:\n\n"
            "1. **Emergency fund first** — 3-6 months of expenses in a high-yield savings account\n"
            "2. **401(k) match** — Invest enough to get your employer's full match (that's free money)\n"
            "3. **Roth IRA** — Up to **$7,000/year** (2025 limit) of tax-free growth\n"
            "4. **Max 401(k)** — Up to **$23,500/year** (2025 limit)\n"
            "5. **Taxable brokerage** — After maxing tax-advantaged accounts\n\n"
            "For what to buy: a **total stock market index fund** (like VTI or FXAIX) is the "
            "simplest, cheapest way to own the entire market. Warren Buffett recommends this.\n\n"
            "**Next Step:** How much can you set aside monthly for investing? I'll build you a projection."
        ),
    },
    {
        "keywords": ["50/30/20", "fifty thirty twenty", "50 30 20 rule"],
        "response": (
            "### The 50/30/20 Budget Rule 📋\n\n"
            "Split your **after-tax income** into three buckets:\n\n"
            "- **50% — Needs:** Rent, groceries, utilities, insurance, minimum debt payments\n"
            "- **30% — Wants:** Dining out, entertainment, subscriptions, shopping\n"
            "- **20% — Savings:** Emergency fund, retirement, extra debt payments\n\n"
            "**Example on $4,500/month:**\n"
            "- Needs: **$2,250**\n"
            "- Wants: **$1,350**\n"
            "- Savings: **$900**\n\n"
            "If your needs are over 50%, that's a sign you're either in a high-cost area "
            "or need to reduce fixed expenses. Start by auditing subscriptions and negotiating bills.\n\n"
            "**Next Step:** Tell me your monthly take-home pay and I'll build your personal 50/30/20 breakdown."
        ),
    },
    {
        "keywords": ["emergency fund", "rainy day fund", "how much emergency"],
        "response": (
            "### Emergency Fund Guide 🛟\n\n"
            "The rule of thumb: **3-6 months of essential expenses** in a high-yield savings account.\n\n"
            "**Be specific:**\n"
            "- If your monthly essentials (rent, food, utilities, insurance) = **$3,000**\n"
            "- Your target is **$9,000 – $18,000**\n\n"
            "**Where to keep it:** A high-yield savings account (HYSA) earning 4-5% APY. "
            "Top options: Marcus, Ally, Wealthfront. Never invest your emergency fund in stocks.\n\n"
            "**Starting from zero?** Aim for $1,000 first. That covers most car repairs, "
            "medical copays, or surprise bills. Then build to 1 month, then 3, then 6.\n\n"
            "**Next Step:** What are your monthly essential expenses? I'll calculate your exact target."
        ),
    },
    {
        "keywords": ["pay off debt or invest", "debt vs invest", "debt or save"],
        "response": (
            "### Debt vs. Investing: The Priority Ladder 🪜\n\n"
            "Follow this exact order:\n\n"
            "1. **Minimum payments** on all debts (always, no exceptions)\n"
            "2. **401(k) match** — Get the free employer match first\n"
            "3. **High-interest debt** (>7% APR) — Pay aggressively (credit cards, personal loans)\n"
            "4. **Emergency fund** — Build to 3-6 months\n"
            "5. **Low-interest debt** (≤5-6%) — Student loans, car loans, these can coexist with investing\n"
            "6. **Max retirement accounts** — Roth IRA, then max 401(k)\n\n"
            "**The math:** If your credit card charges **22% APR**, paying it off is like earning "
            "22% guaranteed return. The stock market averages ~10%. Pay the card first.\n\n"
            "**Next Step:** Tell me about your debts (balances and interest rates) and I'll prioritize them."
        ),
    },
    {
        "keywords": ["roth ira", "traditional ira", "ira difference"],
        "response": (
            "### Roth IRA vs. Traditional IRA 🏦\n\n"
            "| Feature | Traditional IRA | Roth IRA |\n"
            "|---|---|---|\n"
            "| Tax break | Now (deduct contributions) | Later (withdrawals tax-free) |\n"
            "| 2025 limit | **$7,000** ($8,000 if 50+) | **$7,000** ($8,000 if 50+) |\n"
            "| Income limit | None for contributions | **$150K** single / **$236K** married |\n"
            "| Withdrawals | Taxed as income at 59½ | Tax-free at 59½ |\n"
            "| RMDs | Required at 73 | None |\n\n"
            "**Rule of thumb:** If you think your tax rate will be **higher in retirement** → Roth. "
            "If **lower** → Traditional. Most young people benefit from Roth.\n\n"
            "**Next Step:** What's your current income? I can tell you which makes more sense for you."
        ),
    },
    {
        "keywords": ["build credit", "improve credit", "credit building"],
        "response": (
            "### How to Build Credit 📊\n\n"
            "Credit scores (300-850) are built on 5 factors:\n\n"
            "1. **Payment history (35%)** — Never miss a payment. Set up autopay.\n"
            "2. **Credit utilization (30%)** — Keep balances under **30%** of your limit (under 10% is ideal)\n"
            "3. **Length of history (15%)** — Don't close your oldest card\n"
            "4. **Credit mix (10%)** — Having different types helps\n"
            "5. **New inquiries (10%)** — Don't apply for too many cards at once\n\n"
            "**Starting from scratch?** Get a secured credit card, use it for one small purchase/month, "
            "pay it off in full. You'll build credit in 6 months.\n\n"
            "**Next Step:** What's your current credit score? I can give specific improvement tips."
        ),
    },
    {
        "keywords": ["what is 401k", "401k", "four oh one k"],
        "response": (
            "### 401(k) Explained 💼\n\n"
            "A 401(k) is a retirement account through your employer:\n\n"
            "- **2025 limit:** **$23,500/year** ($31,000 if 50+)\n"
            "- **Tax advantage:** Traditional = pre-tax (reduces your taxable income now). "
            "Roth 401(k) = after-tax (withdrawals are tax-free later)\n"
            "- **Employer match:** Many employers match 3-6% of your salary. This is **free money**.\n\n"
            "**Example:** You earn $60K, employer matches 4%. You contribute 4% ($2,400/year), "
            "employer adds $2,400. That's **$4,800/year** with only $200/month from you.\n\n"
            "At 8% growth over 30 years, that $4,800/year becomes **~$587,000**.\n\n"
            "**Next Step:** Does your employer offer a 401(k) match? Tell me the details and I'll optimize."
        ),
    },
    {
        "keywords": ["how much to retire", "retirement savings", "retire"],
        "response": (
            "### How Much Do You Need to Retire? 🏖️\n\n"
            "**The 25x Rule:** Multiply your desired annual retirement spending by 25.\n\n"
            "- Want **$50K/year** in retirement? You need **$1,250,000**\n"
            "- Want **$80K/year?** You need **$2,000,000**\n"
            "- Want **$100K/year?** You need **$2,500,000**\n\n"
            "**The 4% Rule:** You can safely withdraw 4% of your portfolio per year. "
            "That's where the 25x number comes from ($1M × 4% = $40K/year).\n\n"
            "**Starting late?** If you're 35 with $0, investing **$800/month** at 8% gets you "
            "**$1.14 million** by 65. Start at 25? Only **$400/month** needed.\n\n"
            "**Next Step:** What age do you want to retire, and what lifestyle do you imagine? "
            "I'll calculate your exact target."
        ),
    },
    {
        "keywords": ["index fund", "what are index funds"],
        "response": (
            "### Index Funds Explained 📊\n\n"
            "An index fund tracks an entire market (like the S&P 500 = 500 biggest US companies). "
            "Instead of picking individual stocks, you own a tiny piece of **everything**.\n\n"
            "**Why they're the best investment for most people:**\n"
            "- **Low cost:** Expense ratios as low as 0.03% (vs. 1%+ for active funds)\n"
            "- **Diversification:** You own 500+ companies instantly\n"
            "- **Performance:** 90% of professional fund managers can't beat the index over 15 years\n\n"
            "**Top picks:**\n"
            "- **VTI** / **VTSAX** — Total US stock market\n"
            "- **VOO** / **FXAIX** — S&P 500\n"
            "- **VXUS** — International stocks\n"
            "- **BND** — Total bond market\n\n"
            "**Next Step:** Want me to suggest a portfolio allocation based on your age and risk tolerance?"
        ),
    },
    {
        "keywords": ["create budget", "make budget", "how to budget"],
        "response": (
            "### How to Create a Budget That Works 📋\n\n"
            "**Step 1:** Calculate your actual take-home pay\n"
            "**Step 2:** Track spending for one month (check bank/card statements)\n"
            "**Step 3:** Categorize into Needs, Wants, Savings\n"
            "**Step 4:** Apply the 50/30/20 rule and adjust\n\n"
            "**Pro tips:**\n"
            "- Automate savings on payday (pay yourself first)\n"
            "- Use the **envelope method** for categories you overspend\n"
            "- Review weekly for the first month, then monthly\n"
            "- Round up expenses (turns small change into savings)\n\n"
            "**Biggest budget killers:** Subscriptions you forgot about, dining out, "
            "and impulse online shopping. Start by auditing those three.\n\n"
            "**Next Step:** Tell me your monthly income and I'll draft a 50/30/20 budget right now."
        ),
    },
    {
        "keywords": ["dollar cost averaging", "dca"],
        "response": (
            "### Dollar Cost Averaging (DCA) 📉📈\n\n"
            "DCA means investing the **same amount on a schedule** regardless of market price.\n\n"
            "**Example:** Invest **$500/month** into an index fund:\n"
            "- Month 1: Price $50 → buy 10 shares\n"
            "- Month 2: Price drops to $40 → buy 12.5 shares (more for your money!)\n"
            "- Month 3: Price rises to $55 → buy 9.1 shares\n\n"
            "**Why it works:**\n"
            "- Removes emotion from investing (no panic selling, no FOMO buying)\n"
            "- You automatically buy more shares when prices are low\n"
            "- Over time, your average cost per share tends to be favorable\n\n"
            "**Lump sum vs DCA:** Studies show lump sum wins ~68% of the time, but DCA wins "
            "on **stress reduction**. If you'd otherwise keep cash on the sidelines, DCA wins.\n\n"
            "**Next Step:** How much can you invest monthly? I'll project your growth."
        ),
    },
    {
        "keywords": ["rent or buy", "should i buy a house", "renting vs buying"],
        "response": (
            "### Rent vs. Buy: The Real Math 🏠\n\n"
            "**The rule of thumb:** If you'll stay **5+ years** and the **price-to-rent ratio** "
            "in your area is under 20, buying usually wins.\n\n"
            "**Price-to-rent ratio:** Home price ÷ (annual rent). Below 15 = buy, 15-20 = toss-up, above 20 = rent.\n\n"
            "**Buying costs people forget:**\n"
            "- Property taxes (1-2% of home value/year)\n"
            "- Maintenance (1% of home value/year)\n"
            "- Insurance (~$1,500-3,000/year)\n"
            "- PMI if down payment < 20%\n"
            "- Closing costs (2-5% of price)\n\n"
            "**Example:** $350K home at 7% mortgage = **$2,329/month** (P&I only). "
            "Add tax, insurance, maintenance: ~**$3,100/month** true cost.\n\n"
            "**Next Step:** What's your budget and how long do you plan to stay? I'll run the numbers."
        ),
    },
    {
        "keywords": ["reduce taxes", "lower taxes", "tax strategy", "save on taxes"],
        "response": (
            "### How to Legally Reduce Your Taxes 🧾\n\n"
            "**Top tax-saving moves:**\n\n"
            "1. **Max pre-tax 401(k)** — $23,500 = saves $5,875+ in taxes (25% bracket)\n"
            "2. **HSA contributions** — $4,150 single / $8,300 family (triple tax advantage)\n"
            "3. **Standard deduction** — $15,000 single / $30,000 married (2025)\n"
            "4. **Capital gains harvesting** — Sell at 0% rate if income under $47,025\n"
            "5. **Tax-loss harvesting** — Offset gains with losses (save up to $3K/year)\n"
            "6. **Charitable giving** — Donate appreciated stock (skip capital gains tax)\n\n"
            "**The biggest miss:** Not contributing to pre-tax accounts. That's leaving thousands on the table.\n\n"
            "*I'm an AI coach, not a tax professional. Consult a CPA for your specific situation.*\n\n"
            "**Next Step:** What's your income and filing status? I'll estimate your tax situation."
        ),
    },
    {
        "keywords": ["what is etf", "etf vs mutual fund"],
        "response": (
            "### ETFs Explained 📊\n\n"
            "An ETF (Exchange-Traded Fund) is like a mutual fund that trades like a stock.\n\n"
            "**ETF vs Mutual Fund:**\n"
            "| Feature | ETF | Mutual Fund |\n"
            "|---|---|---|\n"
            "| Trading | Anytime market is open | Once per day at close |\n"
            "| Minimum | Price of 1 share (~$50-400) | Often $1,000-3,000 |\n"
            "| Expense ratio | Lower (0.03-0.20%) | Higher (0.10-1%+) |\n"
            "| Tax efficiency | Better | Less efficient |\n\n"
            "**For a new investor:** ETFs are usually the better choice. Start with one total "
            "market ETF like **VTI** ($280/share) and you're instantly diversified.\n\n"
            "**Next Step:** Want me to suggest specific ETFs based on your risk tolerance?"
        ),
    },
    {
        "keywords": ["start saving", "how to save money", "save more"],
        "response": (
            "### How to Start Saving Money 💰\n\n"
            "**The 3 fastest wins:**\n\n"
            "1. **Automate it** — Set up auto-transfer on payday. Even $50/month beats $0.\n"
            "2. **Open a HYSA** — Earn 4-5% instead of 0.01% at your bank. Top picks: "
            "Marcus, Ally, Wealthfront.\n"
            "3. **Cut the Big 3** — Housing, transportation, and food are 60-70% of most budgets. "
            "A $200/month savings here beats skipping lattes forever.\n\n"
            "**Psychology hack:** Name your savings account. \"Emergency Fund\" or \"Japan Trip 2026\" "
            "makes you 3x less likely to raid it than \"Savings Account 2.\"\n\n"
            "**The snowball:** Start with $50/month. Next month, $75. Then $100. "
            "By month 12, you're saving $300/month without noticing.\n\n"
            "**Next Step:** What's your monthly take-home? I'll find the savings hiding in your budget."
        ),
    },
    {
        "keywords": ["diversification", "diversify", "don't put all eggs"],
        "response": (
            "### Diversification: Don't Put All Eggs in One Basket 🥚\n\n"
            "Diversification means spreading money across different investments so one bad pick "
            "doesn't wreck your whole portfolio.\n\n"
            "**Simple diversified portfolio:**\n"
            "- **60% US stocks** (VTI) — Growth engine\n"
            "- **25% International** (VXUS) — Global exposure\n"
            "- **15% Bonds** (BND) — Stability and income\n\n"
            "**Why it matters:** In 2022, the S&P 500 dropped 19%. Bonds dropped 13%. "
            "But international value stocks were down only 5%. A diversified portfolio "
            "recovered faster than an all-S&P portfolio.\n\n"
            "**As you age:** Shift from stocks → bonds. Rule of thumb: your age in bonds "
            "(30 years old = 30% bonds), though many experts say (age - 20) is fine.\n\n"
            "**Next Step:** What's your age and risk tolerance? I'll suggest an allocation."
        ),
    },
    {
        "keywords": ["how much house", "afford house", "home affordability"],
        "response": (
            "### How Much House Can You Afford? 🏡\n\n"
            "**The 28/36 Rule:**\n"
            "- **28%:** Your mortgage payment (P&I + tax + insurance) ≤ 28% of gross income\n"
            "- **36%:** Total debt payments ≤ 36% of gross income\n\n"
            "**On $80K salary ($6,667/month):**\n"
            "- Max mortgage payment: **$1,867/month**\n"
            "- At 7% rate, 30-yr fixed: ~**$280,000** home price\n"
            "- Need 20% down to avoid PMI: **$56,000**\n\n"
            "**Hidden costs:** Budget an extra **30-40%** on top of your mortgage for taxes, "
            "insurance, HOA, and maintenance.\n\n"
            "**Next Step:** Tell me your income, debts, and savings — I'll calculate your max home price."
        ),
    },
    {
        "keywords": ["credit score", "what is credit score", "fico"],
        "response": (
            "### Credit Score Breakdown 📊\n\n"
            "Your FICO score (300-850) determines your interest rates on everything:\n\n"
            "| Score | Rating | Mortgage Rate Impact |\n"
            "|---|---|---|\n"
            "| 760+ | Excellent | Best rates |\n"
            "| 700-759 | Good | +0.25-0.5% |\n"
            "| 650-699 | Fair | +1-1.5% |\n"
            "| Below 650 | Poor | +2-3% or denied |\n\n"
            "**The cost of bad credit:** On a $300K mortgage, the difference between 6.5% and 8% "
            "is **$115,000** extra in interest over 30 years.\n\n"
            "**Quick wins to boost your score:**\n"
            "- Pay down credit card to <30% utilization\n"
            "- Set up autopay (never miss a payment)\n"
            "- Don't close old cards\n"
            "- Dispute any errors on your credit report (free at annualcreditreport.com)\n\n"
            "**Next Step:** What's your current score? I'll create a specific improvement plan."
        ),
    },
    {
        "keywords": ["negotiate raise", "raise salary", "ask for raise"],
        "response": (
            "### How to Negotiate a Raise 💼\n\n"
            "**Before the meeting:**\n"
            "- Research market rate on Glassdoor, Levels.fyi, or Payscale\n"
            "- Document your wins (revenue generated, problems solved, extra responsibilities)\n"
            "- Time it right: after a big win, during review season, or when the company is doing well\n\n"
            "**The script:** \"Based on my contributions [list 2-3 specific wins] and market data "
            "for this role, I'd like to discuss adjusting my compensation to $X.\"\n\n"
            "**If they say no:** Ask \"What would it take to get to that number?\" and get specifics.\n\n"
            "**Impact:** A $5,000 raise at age 30, invested at 8% for 35 years = **$73,000** "
            "extra in retirement. Raises compound just like interest.\n\n"
            "**Next Step:** What's your current salary and role? I'll help you research your market value."
        ),
    },
    {
        "keywords": ["inflation", "what is inflation"],
        "response": (
            "### Inflation: Why Your Money Loses Value 📉\n\n"
            "Inflation means prices rise over time, so $1 today buys less tomorrow.\n\n"
            "**Historical average:** ~3% per year. At 3%, something costing $100 today will cost "
            "$134 in 10 years and $181 in 20 years.\n\n"
            "**What it means for you:**\n"
            "- Cash in a 0.01% savings account is **losing** ~3%/year in purchasing power\n"
            "- Your investments need to beat inflation to grow wealth\n"
            "- Your salary needs to grow at least 3%/year just to stay even\n\n"
            "**Inflation-beating investments:** Stocks (~10% avg), Real estate, I-Bonds, TIPS.\n"
            "**Inflation losers:** Cash, low-yield savings, fixed-rate bonds.\n\n"
            "**Next Step:** Want to see how inflation affects your savings goal? Give me a target and timeframe."
        ),
    },
    {
        "keywords": ["bonds", "what are bonds"],
        "response": (
            "### Bonds Explained 🏛️\n\n"
            "A bond is a loan you make to a government or company. They pay you interest and return "
            "your money at maturity.\n\n"
            "**Types:** Treasury bonds (safest), corporate bonds (higher yield), municipal bonds (tax-free).\n\n"
            "**Why own bonds:**\n"
            "- Stability when stocks crash\n"
            "- Predictable income stream\n"
            "- Lower risk than stocks\n\n"
            "**Current yields (2025):** 10-year Treasury ~4.5%, corporate bonds 5-7%.\n\n"
            "**How much?** Classic rule: your age = % in bonds. Age 30 = 30% bonds. More aggressive: "
            "age - 20 = bonds (so 10% at 30).\n\n"
            "**Easiest way to buy:** Bond index fund like **BND** (Vanguard Total Bond Market).\n\n"
            "**Next Step:** Want me to suggest a stock/bond split for your age and risk level?"
        ),
    },
    {
        "keywords": ["teach kids money", "kids money", "financial literacy kids"],
        "response": (
            "### Teaching Kids About Money 🎓\n\n"
            "**By age:**\n"
            "- **Ages 3-5:** Coins are real, things cost money\n"
            "- **Ages 6-10:** Earning (chores), Saving (piggy bank → real bank), Needs vs Wants\n"
            "- **Ages 11-14:** Budgeting, compound interest, entrepreneurship\n"
            "- **Ages 15+:** Investing, credit, taxes, real-world money management\n\n"
            "**Best tools:**\n"
            "- **3-jar system:** Save, Spend, Share (give each jar a specific purpose)\n"
            "- **Match their savings:** Act as the \"Bank of Mom/Dad\" — match what they save\n"
            "- **Give them choices:** \"You can buy this toy OR save for the bigger one next month\"\n\n"
            "**Check out our Kids Education section** — it has video lessons and quizzes designed for young learners!\n\n"
            "**Next Step:** How old is your child? I'll give age-specific money activities."
        ),
    },
    {
        "keywords": ["debt snowball", "snowball method"],
        "response": (
            "### The Debt Snowball Method ⛄\n\n"
            "Pay off debts from **smallest balance to largest**, regardless of interest rate.\n\n"
            "**How it works:**\n"
            "1. List debts smallest to largest\n"
            "2. Pay minimum on everything except the smallest\n"
            "3. Throw every extra dollar at the smallest debt\n"
            "4. When it's paid off, roll that payment into the next smallest\n\n"
            "**Why it works:** Quick wins build motivation. Paying off a $500 card feels amazing and "
            "keeps you going on the $15,000 student loan.\n\n"
            "**Downside:** You pay more interest than the avalanche method (highest rate first). "
            "But 70% of people who start snowball actually finish. Completion rate matters.\n\n"
            "**Next Step:** List your debts (name, balance, rate, minimum payment) and I'll compare snowball vs avalanche for you."
        ),
    },
    {
        "keywords": ["debt avalanche", "avalanche method"],
        "response": (
            "### The Debt Avalanche Method 🏔️\n\n"
            "Pay off debts from **highest interest rate to lowest**. Mathematically optimal.\n\n"
            "**How it works:**\n"
            "1. List debts by interest rate (highest first)\n"
            "2. Pay minimum on everything except the highest-rate debt\n"
            "3. Throw every extra dollar at the highest-rate debt\n"
            "4. When it's paid off, roll that payment into the next highest rate\n\n"
            "**Why it's best:** You pay the **least total interest**. On $30K of mixed debt, "
            "avalanche can save $1,000-5,000+ vs snowball.\n\n"
            "**Downside:** If your highest-rate debt is also your biggest, it takes longer to get "
            "a \"win.\" Some people lose motivation.\n\n"
            "**Next Step:** Share your debts and I'll show you EXACTLY how much avalanche saves you."
        ),
    },
    {
        "keywords": ["financial advisor", "need advisor", "hire advisor"],
        "response": (
            "### Do You Need a Financial Advisor? 🤝\n\n"
            "**You might NOT need one if:**\n"
            "- Your finances are straightforward (W-2 income, basic investments)\n"
            "- You're willing to learn and use index funds\n"
            "- Your net worth is under $250K\n\n"
            "**You probably SHOULD get one if:**\n"
            "- Income over $200K with complex tax situations\n"
            "- Business owner, stock options, or equity compensation\n"
            "- Inheritance or windfall\n"
            "- Approaching retirement with $500K+\n\n"
            "**Type to look for:** Fee-only fiduciary (they're legally required to act in your interest). "
            "Avoid commission-based advisors. Check NAPFA.org for fee-only advisors.\n\n"
            "**Cost:** $150-300/hour or 0.5-1% of assets/year.\n\n"
            "**Next Step:** I can handle most general planning! What specific situation are you dealing with?"
        ),
    },
    {
        "keywords": ["asset allocation", "portfolio allocation"],
        "response": (
            "### Asset Allocation Guide 📊\n\n"
            "**By age (aggressive):**\n"
            "- **20s:** 90% stocks / 10% bonds\n"
            "- **30s:** 80% stocks / 20% bonds\n"
            "- **40s:** 70% stocks / 30% bonds\n"
            "- **50s:** 60% stocks / 40% bonds\n"
            "- **60s+:** 50% stocks / 50% bonds\n\n"
            "**Within stocks:** 70% US (VTI) + 30% International (VXUS).\n"
            "**Within bonds:** Total bond market (BND) or treasury bonds (VGSH for short-term).\n\n"
            "**Rebalance yearly:** Sell what's grown above target, buy what's below. "
            "This forces you to sell high and buy low.\n\n"
            "**Next Step:** Tell me your age, risk tolerance, and timeline. I'll build your allocation."
        ),
    },
    {
        "keywords": ["college savings", "529 plan", "save for college"],
        "response": (
            "### College Savings: 529 Plans 🎓\n\n"
            "A 529 plan is the best way to save for education:\n\n"
            "- **Tax-free growth** and withdrawals for education expenses\n"
            "- **No income limits** to contribute\n"
            "- **State tax deduction** in many states\n"
            "- **High limits:** $300K+ lifetime per beneficiary\n\n"
            "**How much to save:** Average 4-year public university costs ~$110K total (2025). "
            "Saving **$350/month** from birth at 7% return gets you there.\n\n"
            "**Starting late?** Even $200/month for 10 years = ~$34,000 at 7%. Every bit helps.\n\n"
            "**If they don't go to college:** You can change the beneficiary to another family member "
            "or roll up to $35,000 into a Roth IRA (new 2024 rule).\n\n"
            "**Next Step:** How old is the child and what's your monthly savings capacity?"
        ),
    },
    {
        "keywords": ["high yield savings", "hysa", "best savings account"],
        "response": (
            "### High-Yield Savings Accounts (HYSA) 🏦\n\n"
            "A HYSA earns **4-5% APY** vs. the **0.01%** your regular bank probably pays.\n\n"
            "**On $10,000:** Regular bank = $1/year. HYSA = $450/year. That's $449 you're leaving behind.\n\n"
            "**Top HYSA options (2025):**\n"
            "- **Wealthfront:** ~5.0% APY\n"
            "- **Marcus (Goldman Sachs):** ~4.4% APY\n"
            "- **Ally:** ~4.2% APY\n"
            "- **SoFi:** ~4.5% APY (with direct deposit)\n\n"
            "**Use for:** Emergency fund, short-term savings (1-3 year goals). "
            "NOT for long-term investing (stocks beat HYSA over 5+ years).\n\n"
            "**Next Step:** How much do you have in savings? Let's calculate how much you're leaving on the table."
        ),
    },
    {
        "keywords": ["stock investing basics", "stocks for beginners", "how to buy stocks"],
        "response": (
            "### Stock Investing Basics 📈\n\n"
            "**What a stock is:** You own a tiny piece of a company. If the company grows, "
            "your piece becomes worth more.\n\n"
            "**The smart beginner approach:**\n"
            "1. Open a brokerage account (Fidelity, Schwab, or Vanguard — all free)\n"
            "2. Buy a **total market index fund** (VTI or FXAIX)\n"
            "3. Set up **automatic monthly investments**\n"
            "4. **Don't check it daily** — that leads to panic selling\n\n"
            "**Historical returns:** S&P 500 averages ~10%/year over long periods. "
            "But individual years range from -37% to +52%. That's why you hold long-term.\n\n"
            "**Rule:** Only invest money you won't need for **5+ years**. Short-term money "
            "goes in a HYSA.\n\n"
            "**Next Step:** How much can you invest monthly, and what's your timeline? I'll project your growth."
        ),
    },
]


# ── Matching engine ──────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, strip punctuation."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def _similarity_score(query: str, keywords: list[str]) -> float:
    """Compute a keyword-match confidence score (0-100)."""
    q = _normalize(query)
    if not q:
        return 0.0
    score = 0.0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in q:
            # Exact substring match
            score += 50
            # Bonus if it's the majority of the query
            if len(kw_lower) / len(q) > 0.4:
                score += 30
    return min(score, 100.0)


def find_cached_response(query: str) -> Tuple[Optional[str], float]:
    """Look for a high-confidence cached response.

    Returns:
        (response_text, confidence) or (None, 0) if no match.
    """
    best_response = None
    best_score = 0.0

    for entry in CACHED_RESPONSES:
        score = _similarity_score(query, entry["keywords"])
        if score > best_score:
            best_score = score
            best_response = entry["response"]

    return (best_response, best_score) if best_score >= 50 else (None, 0.0)


# ── Session-level LLM response cache ────────────────────────────────────

def _cache_key(text: str) -> str:
    """Create a stable cache key from user text."""
    normalized = _normalize(text)
    return hashlib.md5(normalized.encode()).hexdigest()


def get_session_cached(query: str) -> Optional[str]:
    """Check session cache for a previous identical question."""
    cache = st.session_state.get("_response_cache", {})
    key = _cache_key(query)
    return cache.get(key)


def set_session_cache(query: str, response: str) -> None:
    """Store a response in the session cache."""
    if "_response_cache" not in st.session_state:
        st.session_state["_response_cache"] = {}
    st.session_state["_response_cache"][_cache_key(query)] = response


def fake_thinking_delay() -> None:
    """Add a small random delay so cached responses feel natural."""
    time.sleep(random.uniform(0.4, 1.2))
