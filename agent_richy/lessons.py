"""Comprehensive financial literacy curriculum for Agent Richy.

Lessons drawn from best practices across leading youth financial
education programs: Junior Achievement, Biz Kid$, NGPF (Next Gen
Personal Finance), CFPB Money As You Grow, Khan Academy, EverFi,
Jump$tart Coalition, Council for Economic Education, and more.

Every example is original.  Every lesson has:
  - title, audience, category, icon
  - lesson_text (the core concept)
  - example (a relatable, concrete story)
  - key_takeaway (one sentence to remember)
  - activity (an actionable exercise)
  - video_key (maps to VIDEO_PROMPTS in video_generator.py)
  - quiz (list of {"q", "choices", "answer_index"} dicts)
"""

from typing import List, Dict, Any

# ─── ELEMENTARY (ages 5-10) ──────────────────────────────────────────────
ELEMENTARY_LESSONS: List[Dict[str, Any]] = [
    {
        "id": "e01_needs_vs_wants",
        "title": "Needs vs. Wants",
        "audience": "kids",
        "category": "Spending Basics",
        "icon": "🛒",
        "lesson_text": (
            "A NEED is something you must have to survive and stay safe — "
            "food, water, shelter, clothing, and medicine.  A WANT is something "
            "nice to have but you can live without — toys, candy, video games, "
            "or the latest sneakers."
        ),
        "example": (
            "Maya gets $20 for her birthday.  She sees a new stuffed animal for $18 "
            "AND she needs a new notebook for school that costs $4.  If she buys the "
            "stuffed animal, she can't afford the notebook.  She decides: notebook "
            "first ($4), then saves the rest.  By next month she has enough for the "
            "stuffed animal AND still has her notebook!"
        ),
        "key_takeaway": "Cover your needs first, then enjoy your wants with what's left.",
        "activity": (
            "Draw two columns on paper: NEEDS and WANTS.  Cut out pictures from a "
            "magazine or print them and sort each item into the right column.  "
            "Challenge: Can you find 5 items that are tricky to sort?"
        ),
        "video_key": "needs_vs_wants",
        "quiz": [
            {"q": "Which of these is a NEED?", "choices": ["Video game", "Winter jacket", "Candy bar", "Toy car"], "answer_index": 1},
            {"q": "You have $10.  Lunch costs $6 and a toy costs $8.  What should you buy?", "choices": ["The toy", "Both", "Lunch first", "Neither"], "answer_index": 2},
            {"q": "True or False: Wants are bad and you should never buy them.", "choices": ["True", "False"], "answer_index": 1},
        ],
    },
    {
        "id": "e02_earning_money",
        "title": "How People Earn Money",
        "audience": "kids",
        "category": "Earning",
        "icon": "💵",
        "lesson_text": (
            "People earn money by working — doing a job or providing a service "
            "that others need.  Some people work for a company and get a paycheck.  "
            "Others start their own business.  Even kids can earn money by doing "
            "chores, helping neighbors, or selling things they make."
        ),
        "example": (
            "Eight-year-old Jordan notices that his neighbor's dog needs walking "
            "every afternoon.  He offers to walk the dog for $5 each time.  After "
            "walking the dog 3 times a week for a month, Jordan has earned $60!  "
            "He puts $30 in his savings jar and uses $30 for a book he wanted."
        ),
        "key_takeaway": "Money doesn't appear — it's earned by providing value to others.",
        "activity": (
            "Make a list of 5 things you could do to earn money this week.  "
            "Ask a parent which ones are realistic.  Pick ONE and try it!"
        ),
        "video_key": "lemonade_stand",
        "quiz": [
            {"q": "How do most people earn money?", "choices": ["Finding it", "Working", "Wishing for it", "Asking on TV"], "answer_index": 1},
            {"q": "Jordan earns $5 per dog walk, 3 times a week.  How much in 2 weeks?", "choices": ["$15", "$25", "$30", "$60"], "answer_index": 2},
            {"q": "Which is an example of earning money?", "choices": ["Getting a gift card", "Mowing a lawn for pay", "Borrowing from a friend", "Finding a dollar"], "answer_index": 1},
        ],
    },
    {
        "id": "e03_saving_basics",
        "title": "The Power of Saving",
        "audience": "kids",
        "category": "Saving",
        "icon": "🐷",
        "lesson_text": (
            "Saving means keeping some of your money instead of spending it "
            "all right away.  When you save, you can buy bigger things later, "
            "handle surprises, and feel safe knowing you have money when you need it.  "
            "Even saving a little bit each week adds up over time."
        ),
        "example": (
            "Lily wants a $40 art set.  She gets $5 a week for chores.  "
            "If she spends it all on candy, she'll never get the art set.  "
            "But if she saves just $4 each week and spends $1 on a treat, "
            "she can buy the art set in 10 weeks AND still enjoy a small "
            "treat every week!"
        ),
        "key_takeaway": "Saving a little bit regularly is how you reach big goals.",
        "activity": (
            "Get three jars or envelopes.  Label them SAVE, SPEND, and GIVE.  "
            "Every time you get money, split it: 50% Save, 40% Spend, 10% Give."
        ),
        "video_key": "savings_piggy_bank",
        "quiz": [
            {"q": "Lily saves $4/week.  How many weeks to save $40?", "choices": ["5 weeks", "8 weeks", "10 weeks", "20 weeks"], "answer_index": 2},
            {"q": "Why is saving important?", "choices": ["So you never have fun", "To buy bigger things later", "Because spending is wrong", "Adults said so"], "answer_index": 1},
            {"q": "What is a good savings split for kids?", "choices": ["Spend everything", "Save 50%, Spend 40%, Give 10%", "Save 1%, Spend 99%", "Give everything away"], "answer_index": 1},
        ],
    },
    {
        "id": "e04_coins_and_dollars",
        "title": "Coins, Dollars & Making Change",
        "audience": "kids",
        "category": "Money Basics",
        "icon": "🪙",
        "lesson_text": (
            "Money comes in coins and bills.  In the U.S.: a penny = 1¢, "
            "nickel = 5¢, dime = 10¢, quarter = 25¢.  Bills come in $1, $5, "
            "$10, $20, $50, and $100.  Knowing how to count money and make "
            "change is a real-life superpower."
        ),
        "example": (
            "At a yard sale, Sam buys a book for $3.75.  He pays with a $5 bill.  "
            "The seller gives him back: 1 quarter (25¢) + 1 dollar bill = $1.25 in "
            "change.  Sam counts it carefully to make sure it's right.  $5.00 – $3.75 = $1.25.  ✓"
        ),
        "key_takeaway": "Always count your change — that's YOUR money.",
        "activity": (
            "Gather coins from around the house.  Practice making these amounts: "
            "$0.47, $0.83, $1.36.  See how many different combinations work!"
        ),
        "video_key": "coins_and_counting",
        "quiz": [
            {"q": "How many nickels make a dollar?", "choices": ["10", "15", "20", "25"], "answer_index": 2},
            {"q": "You buy something for $7.50 and pay with $10.  What's your change?", "choices": ["$1.50", "$2.00", "$2.50", "$3.50"], "answer_index": 2},
            {"q": "Which coin is worth the most?", "choices": ["Penny", "Nickel", "Dime", "Quarter"], "answer_index": 3},
        ],
    },
    {
        "id": "e05_opportunity_cost",
        "title": "Choices: You Can't Have Everything",
        "audience": "kids",
        "category": "Decision Making",
        "icon": "🤔",
        "lesson_text": (
            "Every time you choose to spend money on one thing, you're giving up "
            "the chance to spend it on something else.  This is called opportunity "
            "cost — the thing you DIDN'T choose.  Good money decisions come from "
            "thinking about what you'll miss before you buy."
        ),
        "example": (
            "Aiden has $15.  He can buy a new Minecraft add-on ($15) OR save it "
            "toward a basketball ($30 — he already has $15 saved).  If he buys "
            "the add-on, the opportunity cost is the basketball he could have had "
            "TODAY.  He thinks about it and decides the basketball will bring him "
            "more fun for longer."
        ),
        "key_takeaway": "Before you buy, ask: 'What am I giving up by choosing this?'",
        "activity": (
            "Next time you want to buy something, write down TWO other things "
            "you could use that money for.  Rank all three by which would make "
            "you happiest for the longest time."
        ),
        "video_key": "opportunity_cost_crossroads",
        "quiz": [
            {"q": "What is opportunity cost?", "choices": ["A hidden fee", "What you give up when you choose", "The price tag", "A type of tax"], "answer_index": 1},
            {"q": "You spend $20 on a t-shirt.  The opportunity cost might be:", "choices": ["Getting the shirt dirty", "A $20 book you wanted", "Nothing", "The store closing"], "answer_index": 1},
        ],
    },
    {
        "id": "e06_patience_delayed_gratification",
        "title": "The Marshmallow Test: Patience Pays",
        "audience": "kids",
        "category": "Mindset",
        "icon": "⏰",
        "lesson_text": (
            "Delayed gratification means waiting for a BIGGER reward instead of "
            "taking a SMALLER one right now.  Scientists found that kids who could "
            "wait for two marshmallows instead of eating one immediately tended to "
            "do better in school and life.  The same skill helps with money!"
        ),
        "example": (
            "Zoe sees a gumball machine every day at the store.  Each gumball "
            "costs 25¢.  She used to buy one every day ($1.75/week).  Then she "
            "decided to skip the gumball and save the quarters.  After 8 weeks "
            "she had $14 — enough for the art supplies she'd been dreaming about."
        ),
        "key_takeaway": "Waiting + saving = getting something WAY better later.",
        "activity": (
            "Try a '7-Day Wait' challenge: when you want to buy something this week, "
            "write it down but DON'T buy it.  After 7 days, check: do you still want it?"
        ),
        "video_key": "marshmallow_patience",
        "quiz": [
            {"q": "What is delayed gratification?", "choices": ["Buying right away", "Waiting for a bigger reward later", "Never buying anything", "Asking for more"], "answer_index": 1},
            {"q": "Zoe saves 25¢/day for 8 weeks (56 days).  How much does she save?", "choices": ["$7.00", "$10.00", "$14.00", "$20.00"], "answer_index": 2},
        ],
    },
    {
        "id": "e07_sharing_and_giving",
        "title": "The Joy of Giving",
        "audience": "kids",
        "category": "Community",
        "icon": "🎁",
        "lesson_text": (
            "Part of being good with money is sharing with others.  Giving doesn't "
            "have to be a lot — even a little bit helps.  You can donate to a food "
            "bank, help a friend, or save up to buy a gift for someone you love.  "
            "Giving makes the world better AND makes YOU feel good."
        ),
        "example": (
            "Emma's class is collecting canned food for families in need.  Emma "
            "uses $3 from her 'Give' jar to buy 4 cans of soup at the store.  "
            "Her small donation helps feed a family dinner.  Emma learns that "
            "even small amounts make a real difference."
        ),
        "key_takeaway": "Set aside a little to give — it helps others and builds character.",
        "activity": (
            "This week, find ONE way to give: donate a toy you've outgrown, "
            "help a neighbor for free, or put $1 in a donation jar."
        ),
        "video_key": "giving_jar",
        "quiz": [
            {"q": "Why is giving part of money skills?", "choices": ["It's not", "It helps others and builds character", "You have to", "To get a tax break"], "answer_index": 1},
            {"q": "How much of your money should go to giving?", "choices": ["0%", "About 10%", "50%", "All of it"], "answer_index": 1},
        ],
    },
    {
        "id": "e08_what_is_a_bank",
        "title": "Where Do People Keep Their Money?",
        "audience": "kids",
        "category": "Banking",
        "icon": "🏦",
        "lesson_text": (
            "A bank is a safe place to keep your money.  When you put money in "
            "a savings account, the bank actually pays YOU a little extra money "
            "called INTEREST — like a 'thank you' for letting them hold it.  "
            "Your money is insured (protected) up to $250,000 by the government."
        ),
        "example": (
            "Noah opens his first savings account with $50 from his birthday.  "
            "The bank pays 4% interest per year.  After one year, the bank adds "
            "$2.00 to his account — free money just for saving!  Noah didn't have "
            "to do anything except NOT spend it."
        ),
        "key_takeaway": "Banks keep your money safe AND pay you interest for saving.",
        "activity": (
            "Ask a parent to help you open a savings account (many kids' accounts "
            "have no fees and no minimum).  Track your balance monthly and watch "
            "the interest grow!"
        ),
        "video_key": "bank_vault_adventure",
        "quiz": [
            {"q": "What is interest?", "choices": ["A fee you pay the bank", "Money the bank pays you for saving", "A type of tax", "A bank rule"], "answer_index": 1},
            {"q": "Noah puts $50 in the bank at 4% interest.  After 1 year he has:", "choices": ["$50", "$54", "$52", "$100"], "answer_index": 2},
            {"q": "Up to how much does the government insure in your bank account?", "choices": ["$1,000", "$10,000", "$100,000", "$250,000"], "answer_index": 3},
        ],
    },
]

# ─── MIDDLE SCHOOL (ages 11-14) ─────────────────────────────────────────
MIDDLE_SCHOOL_LESSONS: List[Dict[str, Any]] = [
    {
        "id": "m01_budgeting_basics",
        "title": "Your First Real Budget",
        "audience": "middle",
        "category": "Budgeting",
        "icon": "📊",
        "lesson_text": (
            "A budget is a plan that shows how much money comes in, how much goes "
            "out, and where it goes.  The simplest budget for teens: 50% Needs, "
            "30% Wants, 20% Savings.  Tracking your money is how you stop wondering "
            "'where did it all go?'"
        ),
        "example": (
            "Kai earns $200/month from mowing lawns.  His budget:\n"
            "• Needs (50%): $100 → Phone bill ($35), school supplies ($15), saving for new cleats ($50)\n"
            "• Wants (30%): $60 → Snacks with friends ($25), Spotify ($6), games ($29)\n"
            "• Savings (20%): $40 → Straight to savings account\n"
            "By writing this down, Kai knows exactly what he can and can't afford."
        ),
        "key_takeaway": "A budget isn't a punishment — it's a PLAN that gives you control.",
        "activity": (
            "Track every dollar you spend for 7 days in a notebook or free app.  "
            "At the end, categorize each expense as Need, Want, or Saving.  "
            "What surprises you?"
        ),
        "video_key": "budget_pie_chart",
        "quiz": [
            {"q": "In the 50/30/20 rule, what % goes to savings?", "choices": ["50%", "30%", "20%", "10%"], "answer_index": 2},
            {"q": "Kai earns $200/mo.  How much for Wants?", "choices": ["$100", "$60", "$40", "$20"], "answer_index": 1},
            {"q": "What's the first step in budgeting?", "choices": ["Stop spending", "Track where money goes", "Get a credit card", "Ask for a raise"], "answer_index": 1},
        ],
    },
    {
        "id": "m02_compound_interest",
        "title": "The 8th Wonder: Compound Interest",
        "audience": "middle",
        "category": "Saving & Investing",
        "icon": "📈",
        "lesson_text": (
            "Compound interest means you earn interest on your interest.  "
            "Year 1: you earn interest on your deposit.  Year 2: you earn interest "
            "on your deposit PLUS last year's interest.  This creates exponential "
            "growth — the longer you wait, the faster it grows."
        ),
        "example": (
            "Twins Mia and Max each get $1,000 at age 13.  Mia invests it at "
            "8% annual return and never touches it.  Max spends his $1,000 on "
            "stuff that year.\n\n"
            "By age 23: Mia has $2,159 (her money more than doubled!)\n"
            "By age 33: Mia has $4,661\n"
            "By age 43: Mia has $10,063\n"
            "By age 63: Mia has $46,902 — from just $1,000!\n\n"
            "Max has $0 from that $1,000."
        ),
        "key_takeaway": "Time is the #1 ingredient in building wealth.  Start now.",
        "activity": (
            "Use a compound interest calculator online.  Enter $500 at 8% for "
            "10, 20, 30, and 40 years.  Notice how the growth EXPLODES after "
            "year 20.  That's compounding!"
        ),
        "video_key": "compound_interest_tree",
        "quiz": [
            {"q": "$1,000 at 8% interest for 10 years becomes approximately:", "choices": ["$1,080", "$1,800", "$2,159", "$10,000"], "answer_index": 2},
            {"q": "Compound interest means you earn interest on:", "choices": ["Only your original deposit", "Your deposit + previous interest", "A loan", "Nothing"], "answer_index": 1},
            {"q": "Why is starting early so powerful?", "choices": ["Banks charge less fees", "You get more interest on more interest over time", "Jobs pay more", "It doesn't matter"], "answer_index": 1},
        ],
    },
    {
        "id": "m03_smart_shopping",
        "title": "Smart Shopping: Don't Fall for Tricks",
        "audience": "middle",
        "category": "Spending",
        "icon": "🛍️",
        "lesson_text": (
            "Stores use psychology to make you spend more: sale signs ('50% OFF!'), "
            "product placement at eye level, 'limited time' pressure, and grouping "
            "cheap add-ons near checkout.  Being aware of these tricks makes you "
            "a smarter shopper.  Comparison shopping (checking multiple stores / "
            "websites) can save 20-40%."
        ),
        "example": (
            "Jayden wants wireless earbuds.  Store A has them for $49.99 with a "
            "sign: 'SALE — Was $79.99!'  But when Jayden checks online, the exact "
            "same earbuds are $39.99 on Amazon and $35.99 refurbished on eBay.  "
            "He saved $14 — that's 28% — just by comparing prices for 5 minutes."
        ),
        "key_takeaway": "Never pay the first price you see — compare, wait, and think.",
        "activity": (
            "Pick something you want to buy.  Check the price in 3 different places "
            "(store, Amazon, eBay, etc.).  Calculate how much you'd save buying from "
            "the cheapest option."
        ),
        "video_key": "smart_shopping_detective",
        "quiz": [
            {"q": "A store says 'Was $80, Now $50!'  What should you do?", "choices": ["Buy immediately", "Check if $50 is actually a good price elsewhere", "Buy two", "Ignore it"], "answer_index": 1},
            {"q": "Comparison shopping means:", "choices": ["Buying the most expensive item", "Checking the same item at multiple stores", "Only buying on sale", "Buying in bulk"], "answer_index": 1},
        ],
    },
    {
        "id": "m04_how_banks_work",
        "title": "Checking vs. Savings Accounts",
        "audience": "middle",
        "category": "Banking",
        "icon": "🏦",
        "lesson_text": (
            "CHECKING account = for everyday spending.  Comes with a debit card "
            "and/or checks.  Earns little or no interest.  Easy to access.\n\n"
            "SAVINGS account = for money you want to grow.  Earns higher interest "
            "(currently 4-5% at online banks).  Harder to access on purpose — "
            "it's meant to stay and grow.\n\n"
            "Smart move: use BOTH.  Keep spending money in checking, savings goals "
            "in savings."
        ),
        "example": (
            "Priya, age 13, opens a teen checking account and a savings account.  "
            "Her lawn-mowing money ($120/mo) goes to checking.  She auto-transfers "
            "$30/mo to savings.  By year-end, her savings has $360 + $9 interest = $369.  "
            "Her checking stays low, so she's never tempted to overspend."
        ),
        "key_takeaway": "Checking = spending money.  Savings = growing money.  Use both.",
        "activity": (
            "Ask a parent to help you compare 3 banks' teen savings account rates.  "
            "Look at: interest rate (APY), minimum balance, and monthly fees."
        ),
        "video_key": "checking_vs_savings",
        "quiz": [
            {"q": "Which account earns more interest?", "choices": ["Checking", "Savings", "They're the same", "Neither"], "answer_index": 1},
            {"q": "A savings account at 4% APY on $500 earns about ____ in one year:", "choices": ["$4", "$20", "$50", "$200"], "answer_index": 1},
            {"q": "Why keep spending money in checking, not savings?", "choices": ["Savings is riskier", "It prevents you from spending your savings", "Checking earns more", "No reason"], "answer_index": 1},
        ],
    },
    {
        "id": "m05_entrepreneurship_basics",
        "title": "Think Like an Entrepreneur",
        "audience": "middle",
        "category": "Earning",
        "icon": "🚀",
        "lesson_text": (
            "An entrepreneur spots a problem and creates a solution people will "
            "pay for.  The basics: 1) Find a need, 2) Create a product or service, "
            "3) Set a fair price, 4) Tell people about it, 5) Deliver quality.  "
            "You don't need to be an adult to start — many successful businesses "
            "began as a teenager's side project."
        ),
        "example": (
            "Thirteen-year-old Marcus notices his neighbors struggle to set up "
            "new tech gadgets.  He creates 'TeenTech Help' — $20/visit to set up "
            "phones, smart TVs, and Wi-Fi.  He makes flyers, asks happy customers "
            "for reviews, and soon gets 3 clients a week = $240/month.  His costs "
            "are nearly zero, so almost everything is profit."
        ),
        "key_takeaway": "Find a problem, solve it, and people will pay you.",
        "activity": (
            "Write down 3 problems people around you have.  For each one, brainstorm "
            "a product or service that solves it.  Pick the best idea and make a "
            "simple one-page business plan: What? Who? How much? How will people find you?"
        ),
        "video_key": "teen_entrepreneur_montage",
        "quiz": [
            {"q": "What's the first step of entrepreneurship?", "choices": ["Make flyers", "Find a need or problem to solve", "Set up a website", "Get a business loan"], "answer_index": 1},
            {"q": "Marcus earns $20/visit, 3 visits/week.  Monthly revenue?", "choices": ["$60", "$120", "$180", "$240"], "answer_index": 3},
        ],
    },
    {
        "id": "m06_credit_debit_cards",
        "title": "Credit Cards vs. Debit Cards Explained",
        "audience": "middle",
        "category": "Credit & Debt",
        "icon": "💳",
        "lesson_text": (
            "DEBIT card = spends YOUR money directly from your bank account.  "
            "When it's gone, it's gone.  No debt.\n\n"
            "CREDIT card = borrows the BANK'S money.  You get a bill each month.  "
            "If you don't pay in full, you owe INTEREST — typically 20-29% APR.  "
            "That $100 purchase could cost you $120+ if you only pay minimums.\n\n"
            "Rule: Never charge more than you can pay in full each month."
        ),
        "example": (
            "Diego sees a $200 gaming console.  With a debit card, he checks: "
            "'Do I have $200 in my account?  Yes — I'll buy it.'  If he used a "
            "credit card at 25% APR and only paid $10/month, he'd pay $254 total "
            "and it would take over 2 YEARS to pay off a single purchase."
        ),
        "key_takeaway": "Debit = your money.  Credit = borrowed money with interest.",
        "activity": (
            "Calculate this: If you owe $500 on a credit card at 22% APR and pay "
            "$25/month, how long to pay it off?  (Answer: 24 months, total $596).  "
            "Use an online credit card payoff calculator."
        ),
        "video_key": "credit_vs_debit_battle",
        "quiz": [
            {"q": "A debit card takes money from:", "choices": ["The bank's account", "Your bank account", "Your credit score", "Your parents"], "answer_index": 1},
            {"q": "Average credit card APR is about:", "choices": ["5%", "10%", "22-25%", "50%"], "answer_index": 2},
            {"q": "The safest rule with a credit card is:", "choices": ["Pay the minimum", "Pay in full every month", "Only use it for emergencies", "Max it out for rewards"], "answer_index": 1},
        ],
    },
    {
        "id": "m07_inflation",
        "title": "Why Does Everything Cost More?",
        "audience": "middle",
        "category": "Economics",
        "icon": "📉",
        "lesson_text": (
            "Inflation means the prices of things go up over time.  A movie "
            "ticket cost $4 in 1990 and costs about $11 today.  A gallon of "
            "gas cost $1.16 in 1990 and costs about $3.50 today.  On average, "
            "prices rise about 3% per year.  This means money sitting under your "
            "mattress LOSES value — $100 today buys more than $100 will in 10 years."
        ),
        "example": (
            "Grandma tells Ava that her first car cost $3,000 in 1980.  That same "
            "model today costs $28,000.  But Grandma's salary was $15,000/year back then.  "
            "The car was 20% of her salary.  The average salary today is ~$60,000, "
            "and the car is 47% of that.  Some things inflated FASTER than income!"
        ),
        "key_takeaway": "Inflation makes cash worth less over time — that's why investing matters.",
        "activity": (
            "Ask a grandparent or older relative what 3 items cost when they were "
            "your age.  Look up the same items today.  Calculate the increase."
        ),
        "video_key": "inflation_shrinking_dollar",
        "quiz": [
            {"q": "Historical average inflation is about ___ per year:", "choices": ["1%", "3%", "10%", "20%"], "answer_index": 1},
            {"q": "If prices rise 3%/year, $100 today is worth about ____ in 10 years:", "choices": ["$100", "$97", "$74", "$50"], "answer_index": 2},
            {"q": "Why is inflation a reason to invest?", "choices": ["You lose money investing", "Cash loses buying power, investments can outpace inflation", "Banks are unsafe", "It isn't"], "answer_index": 1},
        ],
    },
    {
        "id": "m08_scams_identity_theft",
        "title": "Scams, Fraud & Protecting Your Money",
        "audience": "middle",
        "category": "Safety",
        "icon": "🔒",
        "lesson_text": (
            "Scammers use tricks to steal your money or identity.  Common scams:\n"
            "• 'You won a prize!' — but you have to pay a fee first\n"
            "• Phishing emails/texts that look like your bank\n"
            "• Social media 'money flipping' schemes\n"
            "• Someone asking for your Social Security number or passwords\n\n"
            "Rule: If it sounds too good to be true, it IS.  Never share personal "
            "info online with strangers."
        ),
        "example": (
            "Riley gets a DM on Instagram: 'Send me $50 and I'll turn it into $500 "
            "with my investment method!'  It has screenshots of 'proof.'  "
            "Riley asks his dad, who explains this is a common Venmo/CashApp scam.  "
            "The 'proof' is easily faked.  Riley blocks the account and reports it."
        ),
        "key_takeaway": "If someone asks you to send money to GET money, it's a scam.  Always.",
        "activity": (
            "Search for 'common scams targeting teens' and list 5 different types.  "
            "Share what you find with friends so everyone stays safe."
        ),
        "video_key": "scam_alert_shield",
        "quiz": [
            {"q": "Someone online says 'Send me $100, I'll send back $1,000.'  This is:", "choices": ["A great investment", "A scam", "Normal banking", "A guaranteed return"], "answer_index": 1},
            {"q": "You should never share your ____ with strangers online:", "choices": ["Favorite color", "Social Security number", "School name", "Hobby"], "answer_index": 1},
        ],
    },
    {
        "id": "m09_taxes_basics",
        "title": "What Are Taxes & Why Do We Pay Them?",
        "audience": "middle",
        "category": "Taxes",
        "icon": "🧾",
        "lesson_text": (
            "Taxes are money the government collects to pay for public services: "
            "schools, roads, firefighters, police, parks, and the military.  "
            "When you get a job, your paycheck has money taken out BEFORE you "
            "receive it — that's called withholding.  The main types: income tax "
            "(federal & state), sales tax (on purchases), and payroll tax (Social "
            "Security & Medicare)."
        ),
        "example": (
            "Aaliyah gets her first paycheck from her summer job.  She worked "
            "40 hours at $12/hour = $480 gross pay.  But her check is only $412.  "
            "Where's the $68?  Federal tax: $34, State tax: $14, FICA: $20.  "
            "She learns that 'gross' pay and 'net' (take-home) pay are different!"
        ),
        "key_takeaway": "Taxes fund public services.  Your take-home pay is LESS than your hourly rate × hours.",
        "activity": (
            "Look at a sample pay stub online (search 'sample pay stub').  "
            "Identify: gross pay, federal tax, state tax, FICA, and net pay.  "
            "What percentage went to taxes?"
        ),
        "video_key": "paycheck_breakdown_animation",
        "quiz": [
            {"q": "Taxes pay for:", "choices": ["Just the president's salary", "Schools, roads, firefighters & more", "Internet subscriptions", "Only the military"], "answer_index": 1},
            {"q": "Aaliyah earns $480 gross.  Her take-home (net) is $412.  Tax rate?", "choices": ["About 5%", "About 14%", "About 25%", "About 50%"], "answer_index": 1},
            {"q": "'Gross pay' means:", "choices": ["Your actual paycheck amount", "Total pay BEFORE taxes", "Money that's dirty", "Your hourly rate"], "answer_index": 1},
        ],
    },
    {
        "id": "m10_charitable_giving_impact",
        "title": "Using Money to Change the World",
        "audience": "middle",
        "category": "Community",
        "icon": "🌍",
        "lesson_text": (
            "Giving back is a core money skill.  It doesn't have to be huge — "
            "$5 to a food bank, $10 to an animal shelter, or volunteering your "
            "time.  When you donate to a registered charity, adults can even "
            "deduct it from their taxes.  Smart giving: research charities on "
            "sites like Charity Navigator to make sure your money is used well."
        ),
        "example": (
            "A middle school class raises $300 with a bake sale.  They research "
            "three charities on Charity Navigator: one uses 92% of donations on "
            "programs, another uses only 55% (the rest goes to 'overhead').  "
            "They choose the 92% charity, knowing $276 of their $300 will help "
            "feed families directly."
        ),
        "key_takeaway": "Give with impact — research where your donation actually goes.",
        "activity": (
            "Pick a cause you care about.  Look up 3 charities on charitynavigator.org.  "
            "Compare their efficiency ratings.  Which would you donate to and why?"
        ),
        "video_key": "charity_impact_ripple",
        "quiz": [
            {"q": "A charity uses 90% of donations on programs.  Is that good?", "choices": ["No", "Yes — that's excellent", "Doesn't matter", "Only if it's 100%"], "answer_index": 1},
            {"q": "Where can you check if a charity uses money wisely?", "choices": ["Instagram", "Charity Navigator", "The CEO's Twitter", "You can't check"], "answer_index": 1},
        ],
    },
]

# ─── HIGH SCHOOL (ages 15-17) ──────────────────────────────────────────
HIGH_SCHOOL_LESSONS: List[Dict[str, Any]] = [
    {
        "id": "h01_credit_scores",
        "title": "Credit Scores: Your Financial GPA",
        "audience": "high",
        "category": "Credit",
        "icon": "📊",
        "lesson_text": (
            "Your credit score (300–850) tells lenders how likely you are to "
            "repay.  It affects apartment applications, car loans, mortgages, "
            "insurance rates, and even some jobs.  The five factors:\n"
            "• Payment history (35%) — Pay on time, every time\n"
            "• Credit utilization (30%) — Keep usage under 30% of your limit\n"
            "• Length of history (15%) — Start early with a secured card\n"
            "• Credit mix (10%) — Different types of credit\n"
            "• New inquiries (10%) — Don't apply for many cards at once"
        ),
        "example": (
            "At 18, Sofia gets a secured credit card with a $500 limit.  She "
            "uses it for one small purchase ($30 gas) each month and pays in FULL.  "
            "After 12 months her score is 715.  Her roommate Bella "
            "maxed out a $1,000 card and paid late twice — her score is 580.  "
            "When they apply for an apartment, Sofia gets approved; Bella needs "
            "a co-signer and a larger deposit."
        ),
        "key_takeaway": "Build credit early with small charges paid in full and on time.",
        "activity": (
            "If you're 18+, check your free credit report at annualcreditreport.com.  "
            "If under 18, ask a parent to show you theirs and explain each section."
        ),
        "video_key": "credit_score_dashboard",
        "quiz": [
            {"q": "What's the biggest factor in your credit score?", "choices": ["Income", "Payment history (35%)", "Age", "Bank balance"], "answer_index": 1},
            {"q": "Good credit utilization means using:", "choices": ["0% of your limit", "Under 30% of your limit", "100% of your limit", "As much as possible"], "answer_index": 1},
            {"q": "A 'good' credit score starts at about:", "choices": ["300", "500", "670", "800"], "answer_index": 2},
        ],
    },
    {
        "id": "h02_investing_basics",
        "title": "Investing 101: Stocks, Bonds & ETFs",
        "audience": "high",
        "category": "Investing",
        "icon": "📈",
        "lesson_text": (
            "STOCKS = buying a tiny piece of a company.  If the company grows, "
            "so does your investment.  Higher risk, higher potential reward.\n\n"
            "BONDS = lending money to a company or government.  They pay you "
            "interest.  Lower risk, lower return.\n\n"
            "ETFs (Exchange-Traded Funds) = a basket of many stocks or bonds "
            "bundled together.  Less risky than individual stocks because you're "
            "diversified.  Example: an S&P 500 ETF owns pieces of 500 companies.\n\n"
            "Historical averages: stocks ~10%/yr, bonds ~4-5%/yr, savings ~3-5%/yr."
        ),
        "example": (
            "Tyler, 16, opens a custodial Roth IRA with his parents.  He invests "
            "$100/month in a total stock market ETF (like VTI).  At 10% average "
            "annual return:\n"
            "• Age 26: $20,655 (contributed $12,000)\n"
            "• Age 36: $75,937 (contributed $24,000)\n"
            "• Age 66: $1,396,690 (contributed $60,000)\n"
            "His $60K of contributions became $1.4 MILLION — tax-free in a Roth!"
        ),
        "key_takeaway": "Start investing even small amounts — time is your greatest advantage.",
        "activity": (
            "Look up these ETFs and their 10-year returns: VTI (total stock market), "
            "VOO (S&P 500), BND (bonds).  Which grew more?  Why?"
        ),
        "video_key": "stock_market_rollercoaster",
        "quiz": [
            {"q": "An ETF is:", "choices": ["A single stock", "A basket of multiple investments", "A type of bank account", "A government bond"], "answer_index": 1},
            {"q": "Average annual stock market return is about:", "choices": ["3%", "5%", "10%", "25%"], "answer_index": 2},
            {"q": "Why is diversification important?", "choices": ["Guarantees profit", "Reduces risk by spreading across many investments", "It isn't important", "Saves on taxes"], "answer_index": 1},
        ],
    },
    {
        "id": "h03_roth_ira_teens",
        "title": "The Roth IRA: A Teen's Secret Weapon",
        "audience": "high",
        "category": "Investing",
        "icon": "🚀",
        "lesson_text": (
            "A Roth IRA is a retirement investment account where your money "
            "grows TAX-FREE.  You put in money you've already paid taxes on, "
            "and when you take it out in retirement, you owe $0 in taxes.\n\n"
            "2024 limit: $7,000/year (or your earned income, whichever is less).  "
            "You MUST have a job to contribute.  Under 18, a parent opens a "
            "'custodial Roth IRA' for you.\n\n"
            "Starting at 15 gives you 50 YEARS of tax-free compounding."
        ),
        "example": (
            "Zara, 15, babysits and earns $3,000/year.  She puts $2,000 into a "
            "Roth IRA each year for just 5 years ($10,000 total), then STOPS.  "
            "At 8% growth, her $10,000 becomes:\n"
            "• Age 25: $21,589\n"
            "• Age 35: $46,610\n"
            "• Age 45: $100,627\n"
            "• Age 65: $469,016\n"
            "ALL tax-free.  $10K became $469K just by starting early."
        ),
        "key_takeaway": "If you have earned income, a Roth IRA is the #1 move you can make as a teen.",
        "activity": (
            "Search 'custodial Roth IRA for teens' at Fidelity or Schwab.  "
            "Ask a parent to help you open one if you have any earned income."
        ),
        "video_key": "roth_ira_rocket",
        "quiz": [
            {"q": "In a Roth IRA, you pay taxes:", "choices": ["When you take money out", "Never", "When you put money in", "Every year"], "answer_index": 2},
            {"q": "Can a 15-year-old have a Roth IRA?", "choices": ["No", "Yes, if they have earned income (custodial account)", "Only at 18", "Only at 21"], "answer_index": 1},
            {"q": "2024 Roth IRA contribution limit:", "choices": ["$1,000", "$3,000", "$7,000", "$23,000"], "answer_index": 2},
        ],
    },
    {
        "id": "h04_student_loans",
        "title": "The Student Loan Reality Check",
        "audience": "high",
        "category": "Debt",
        "icon": "🎓",
        "lesson_text": (
            "Average student loan debt: $37,338.  Average monthly payment: $393.  "
            "Average time to repay: 20 years.  Average interest rate: 5-7%.\n\n"
            "Strategies to minimize debt:\n"
            "1. Community college first (save $20K-$40K)\n"
            "2. In-state public university (vs. out-of-state or private)\n"
            "3. Apply for EVERY scholarship and grant (free money)\n"
            "4. Work part-time during school\n"
            "5. Only borrow what you truly NEED, not the max offered"
        ),
        "example": (
            "Two paths for the same degree:\n\n"
            "Path A (expensive): Private university, $55K/year × 4 = $220K debt\n"
            "→ Monthly payment: $2,328 for 10 years  →  Total paid: $279,401\n\n"
            "Path B (smart): Community college 2 years ($3K/yr) + state university "
            "2 years ($12K/yr) + $5K in scholarships = $25K debt\n"
            "→ Monthly payment: $265 for 10 years  →  Total paid: $31,725\n\n"
            "Same degree.  $247,676 difference."
        ),
        "key_takeaway": "The school name on your degree matters less than the debt you carry after.",
        "activity": (
            "Look up the total 4-year cost of 3 schools you're interested in.  "
            "Calculate how much you'd need to borrow.  Use studentaid.gov's "
            "repayment calculator to see your monthly payment."
        ),
        "video_key": "student_loan_comparison",
        "quiz": [
            {"q": "Average student loan debt in the U.S.:", "choices": ["$10,000", "$37,338", "$100,000", "$250,000"], "answer_index": 1},
            {"q": "Which strategy saves the most on college costs?", "choices": ["Borrowing the maximum", "Community college + state university", "Only private schools", "Not going to college"], "answer_index": 1},
        ],
    },
    {
        "id": "h05_side_hustles",
        "title": "Building Income Streams as a Teen",
        "audience": "high",
        "category": "Earning",
        "icon": "💼",
        "lesson_text": (
            "Wealthy people have multiple income streams.  As a teen, you can "
            "start stacking them:\n\n"
            "• SERVICE: Dog walking, tutoring, lawn care, car washing ($15-30/hr)\n"
            "• DIGITAL: Freelance design, social media management, video editing ($20-50/hr)\n"
            "• PRODUCT: Reselling on eBay/Mercari, handmade goods on Etsy\n"
            "• CONTENT: YouTube, TikTok, blogging (builds over time)\n"
            "• PASSIVE: Once established — digital downloads, print-on-demand\n\n"
            "Start with one, master it, add another."
        ),
        "example": (
            "Isaiah, 17, stacks three hustles:\n"
            "1. Lawn care on weekends: $120/week\n"
            "2. Graphic design on Fiverr: $200/month\n"
            "3. Reselling sneakers on eBay: $150/month average\n\n"
            "Total: $830/month.  He saves 50% ($415) and invests it.  "
            "By graduation he has $5,000+ saved and real business experience "
            "for his resume."
        ),
        "key_takeaway": "Don't wait for permission — start earning now and stack your hustles.",
        "activity": (
            "Pick ONE side hustle from the list above.  This week: 1) Research it "
            "for 30 minutes, 2) Set up what you need, 3) Get your FIRST customer.  "
            "Even $1 earned makes you an entrepreneur."
        ),
        "video_key": "side_hustle_montage",
        "quiz": [
            {"q": "Isaiah earns $120/week from lawns + $200/mo design + $150/mo reselling.  Monthly total?", "choices": ["$470", "$830", "$600", "$1,200"], "answer_index": 1},
            {"q": "What's the best time to start a side hustle?", "choices": ["After college", "After getting a 'real' job", "Now — while you have few expenses", "Never — too risky"], "answer_index": 2},
        ],
    },
    {
        "id": "h06_car_buying",
        "title": "Your First Car: Don't Get Wrecked Financially",
        "audience": "high",
        "category": "Major Purchases",
        "icon": "🚗",
        "lesson_text": (
            "A car is most teens' first BIG purchase.  Rules:\n"
            "• The 20/4/10 rule: 20% down, 4-year loan max, payment ≤ 10% of gross income\n"
            "• Buy used (2-3 years old) — new cars lose 20% value in Year 1\n"
            "• Budget for: insurance ($150-300/mo for teens), gas ($100-200/mo), "
            "maintenance ($100/mo average)\n"
            "• Total car costs often = car payment + insurance + gas + maintenance\n"
            "• A $25,000 car really costs $35,000+ over 5 years with all expenses"
        ),
        "example": (
            "Olivia makes $2,000/month.  She's choosing between:\n\n"
            "Car A: New, $28,000, $520/mo payment + $280 insurance = $800/mo (40% of income!)\n"
            "Car B: Used 3yr-old, $14,000, $280/mo payment + $190 insurance = $470/mo (23.5%)\n\n"
            "Car B fits within the 20/4/10 rule.  Car A would leave her broke every month."
        ),
        "key_takeaway": "Your first car should be reliable and affordable — not impressive.",
        "activity": (
            "Search for a car you'd like on AutoTrader.  Calculate TOTAL monthly cost: "
            "payment + insurance (get a parent's quote) + gas ($150) + maintenance ($75).  "
            "Is it under 20% of your expected income?"
        ),
        "video_key": "first_car_financial_guide",
        "quiz": [
            {"q": "The 20/4/10 rule means:", "choices": ["20 MPG, 4 doors, 10 years old", "20% down, 4-year loan, payment ≤ 10% of income", "20K price, 4% interest, $10 gas", "20% tip, 4WD, 10 colors"], "answer_index": 1},
            {"q": "A new car loses about ___ of its value in Year 1:", "choices": ["5%", "20%", "50%", "0%"], "answer_index": 1},
        ],
    },
    {
        "id": "h07_taxes_w2_filing",
        "title": "Your First Paycheck & Filing Taxes",
        "audience": "high",
        "category": "Taxes",
        "icon": "📝",
        "lesson_text": (
            "When you get a job, you'll fill out a W-4 form (tells your employer "
            "how much tax to withhold).  At year-end you'll get a W-2 form showing "
            "total earnings and taxes paid.  If you earned under $13,850 (2023 standard "
            "deduction), you likely owe ZERO federal income tax and can get a REFUND "
            "of what was withheld.\n\n"
            "File for free using IRS Free File (incomes under $79K)."
        ),
        "example": (
            "Ethan worked part-time and earned $8,000 last year.  His employer "
            "withheld $640 in federal taxes.  But since $8,000 < $13,850 standard "
            "deduction, Ethan owes NOTHING.  He files his tax return and gets his "
            "entire $640 BACK as a refund.  That's money in his pocket he almost "
            "left on the table."
        ),
        "key_takeaway": "If you earn under ~$14K as a student, file anyway — you often get money BACK.",
        "activity": (
            "If you had a job last year, get your W-2 from your employer.  "
            "Use IRS Free File to file your return.  See if you get a refund!"
        ),
        "video_key": "paycheck_breakdown_animation",
        "quiz": [
            {"q": "A W-2 form shows:", "choices": ["Your credit score", "Your earnings and taxes withheld", "Your bank balance", "Your GPA"], "answer_index": 1},
            {"q": "If you earned $8,000, you likely owe ____ in federal income tax:", "choices": ["$640", "$800", "$0 (under standard deduction)", "$1,200"], "answer_index": 2},
        ],
    },
    {
        "id": "h08_apartment_renting",
        "title": "Renting Your First Apartment",
        "audience": "high",
        "category": "Housing",
        "icon": "🏠",
        "lesson_text": (
            "The 30% rule: housing should cost no more than 30% of your gross "
            "(before-tax) income.  If you make $3,000/mo gross, max rent = $900.\n\n"
            "Costs beyond rent:\n"
            "• Security deposit (usually 1 month's rent)\n"
            "• Utilities ($100-$200/mo)\n"
            "• Renter's insurance ($15-$25/mo)\n"
            "• Furniture and move-in costs ($500-$2,000 one-time)\n\n"
            "Roommates can cut your cost 30-50%."
        ),
        "example": (
            "Fresh out of high school, Jade earns $2,800/month.  30% = $840 max rent.  "
            "She has two options:\n"
            "• Studio apartment: $1,100/mo (39% of income — too much!)\n"
            "• Split 2-bedroom with a roommate: $750/mo each (27% — perfect!)\n"
            "By choosing a roommate, Jade saves $350/mo = $4,200/year to invest."
        ),
        "key_takeaway": "Keep housing under 30% of income.  Roommates are a wealth-building strategy.",
        "activity": (
            "Search apartments in a city you'd like to live in on Apartments.com.  "
            "Find the average 1-bedroom rent.  What annual salary would you need "
            "for rent to be ≤ 30% of gross income?"
        ),
        "video_key": "first_apartment_walkthrough",
        "quiz": [
            {"q": "Housing should cost no more than __% of gross income:", "choices": ["10%", "30%", "50%", "80%"], "answer_index": 1},
            {"q": "Jade earns $2,800/mo.  Max rent should be:", "choices": ["$600", "$840", "$1,100", "$1,400"], "answer_index": 1},
        ],
    },
    {
        "id": "h09_time_value_of_money",
        "title": "Time Value of Money: Why $1 Today > $1 Tomorrow",
        "audience": "high",
        "category": "Core Concepts",
        "icon": "⏳",
        "lesson_text": (
            "A dollar today is worth MORE than a dollar in the future because "
            "today's dollar can be invested and earn returns.  This is the Time "
            "Value of Money (TVM) — the foundation of all finance.\n\n"
            "The Rule of 72: divide 72 by your interest rate to find how many "
            "years it takes your money to DOUBLE.  At 8% → 72 ÷ 8 = 9 years.  "
            "At 10% → 72 ÷ 10 = 7.2 years."
        ),
        "example": (
            "Two friends each have $5,000:\n"
            "• Friend A invests it at 10% per year\n"
            "• Friend B puts it under his mattress\n\n"
            "After 7 years (Rule of 72): A has ~$10,000.  B still has $5,000.\n"
            "After 14 years: A has ~$20,000.  B still has $5,000.\n"
            "After 21 years: A has ~$40,000.  B has $5,000 that buys "
            "LESS due to inflation."
        ),
        "key_takeaway": "The Rule of 72: 72 ÷ return rate = years to double your money.",
        "activity": (
            "Use the Rule of 72 to calculate: at 6% return, how long to double?  "
            "At 12%?  At 3%?  Then verify with a calculator."
        ),
        "video_key": "compound_snowball",
        "quiz": [
            {"q": "Rule of 72: At 8%, your money doubles in:", "choices": ["4 years", "8 years", "9 years", "12 years"], "answer_index": 2},
            {"q": "Why is $100 today worth more than $100 in 5 years?", "choices": ["Inflation is a myth", "Today's $100 can be invested and grow", "Money changes color", "It's the same value"], "answer_index": 1},
        ],
    },
    {
        "id": "h10_avoiding_debt_traps",
        "title": "Debt Traps: Predatory Lending & Buy Now Pay Later",
        "audience": "high",
        "category": "Debt",
        "icon": "⚠️",
        "lesson_text": (
            "Predatory lenders target young people with:\n"
            "• Payday loans: 400%+ APR (a $500 loan can cost $625 in 2 weeks)\n"
            "• Buy Now Pay Later (BNPL): Seems free but late fees add up; "
            "makes you spend 20-30% more than you would otherwise\n"
            "• Rent-to-own stores: A $500 TV ends up costing $1,500+\n"
            "• Car title loans: Risk losing your car at 300%+ interest\n\n"
            "These products target people who feel desperate.  Build an "
            "emergency fund to NEVER need them."
        ),
        "example": (
            "Kai needs $500 for a car repair.  Option A: Payday loan — $500 at "
            "400% APR = owes $575 in 2 weeks.  If he can't pay, rolls over: "
            "owes $660 in 4 weeks.  Can spiral into $1,000+ of debt.\n\n"
            "Option B: He asks his employer for a $500 advance, repaid over "
            "4 paychecks.  Zero interest.  Problem solved.\n\n"
            "Always look for alternatives BEFORE predatory lending."
        ),
        "key_takeaway": "If a lender targets people who 'need money fast,' the terms are probably terrible.",
        "activity": (
            "Look up the APR of: a credit card, a payday loan, a BNPL late fee, "
            "and a car title loan.  Make a comparison chart.  Which is safest?"
        ),
        "video_key": "debt_monster",
        "quiz": [
            {"q": "Typical payday loan APR:", "choices": ["10%", "25%", "100%", "400%+"], "answer_index": 3},
            {"q": "BNPL (Buy Now Pay Later) makes people spend:", "choices": ["Less", "The same", "20-30% more", "Only on needs"], "answer_index": 2},
        ],
    },
    {
        "id": "h11_insurance_basics",
        "title": "Insurance: Protecting What You Build",
        "audience": "high",
        "category": "Protection",
        "icon": "🛡️",
        "lesson_text": (
            "Insurance is paying a small amount regularly (premium) so that if "
            "something bad happens, you don't go bankrupt.  Key types for young adults:\n\n"
            "• Health insurance: Most expensive bill you'll ever face without it.  "
            "One ER visit = $3,000-$30,000.  Stay on parents' plan until 26.\n"
            "• Auto insurance: Required by law.  $150-$300/mo for teens.\n"
            "• Renter's insurance: $15-$25/mo.  Covers your stuff if stolen/damaged.\n\n"
            "Key terms: premium (monthly cost), deductible (what you pay first), "
            "copay (your share), out-of-pocket max (your ceiling)."
        ),
        "example": (
            "Without insurance: Alex breaks his arm playing basketball.  "
            "ER visit + X-ray + cast = $8,500 bill.  He has to set up a payment "
            "plan for 3 years.\n\n"
            "With insurance ($200/mo premium, $2,000 deductible): Alex pays $2,000, "
            "insurance covers $6,500.  Annual premiums: $2,400.  But $2,400/year is "
            "way better than one surprise $8,500 bill."
        ),
        "key_takeaway": "Insurance costs money — not having insurance costs MORE money.",
        "activity": (
            "Ask a parent about their health insurance: What's the premium?  "
            "Deductible?  Out-of-pocket max?  At what age does it stop covering you?"
        ),
        "video_key": "insurance_shield_animation",
        "quiz": [
            {"q": "You can stay on a parent's health insurance until age:", "choices": ["18", "21", "26", "30"], "answer_index": 2},
            {"q": "A 'deductible' is:", "choices": ["Your monthly premium", "What you pay before insurance kicks in", "A tax deduction", "The total bill"], "answer_index": 1},
        ],
    },
    {
        "id": "h12_impulse_control",
        "title": "The Psychology of Spending",
        "audience": "high",
        "category": "Mindset",
        "icon": "🧠",
        "lesson_text": (
            "Companies spend BILLIONS to make you buy impulsively:\n"
            "• Social media ads targeted by your browsing history\n"
            "• 'Limited time!' and 'Only 3 left!' create false urgency\n"
            "• Influencers make products seem essential\n"
            "• Free shipping thresholds make you add unnecessary items\n"
            "• 'Dopamine hits' from buying feel good for ~20 minutes, then fade\n\n"
            "Defense: Unfollow shopping accounts, remove saved cards from apps, "
            "use a 72-hour rule, and set a monthly 'fun money' limit."
        ),
        "example": (
            "Nadia used to spend $200+/month on impulse online orders.  "
            "She tried three changes:\n"
            "1. Deleted Instagram shopping app, removed saved cards from Amazon\n"
            "2. Added items to cart but waited 72 hours before buying\n"
            "3. Set a $75/month 'fun money' limit\n\n"
            "Result: She now spends $60/month on things she ACTUALLY wants "
            "and saves the extra $140/month ($1,680/year)."
        ),
        "key_takeaway": "Every dollar you don't waste is a dollar working FOR you.",
        "activity": (
            "This week: add something to your online cart but DON'T buy it.  "
            "After 72 hours, honestly ask: Do I still want this?  How many "
            "hours of work does this cost me?"
        ),
        "video_key": "impulse_buying_trap",
        "quiz": [
            {"q": "The '72-hour rule' means:", "choices": ["Shop for 72 hours", "Wait 72 hours before buying", "Return items in 72 hours", "Buy within 72 hours for a discount"], "answer_index": 1},
            {"q": "Nadia saved __/year by controlling impulse spending:", "choices": ["$200", "$840", "$1,680", "$3,000"], "answer_index": 2},
        ],
    },
]

# ─── COMBINED: all lessons for easy access ───────────────────────────────
ALL_LESSONS: List[Dict[str, Any]] = ELEMENTARY_LESSONS + MIDDLE_SCHOOL_LESSONS + HIGH_SCHOOL_LESSONS

# Helper: get lessons by audience
def get_lessons_for_audience(audience: str) -> List[Dict[str, Any]]:
    """Return lessons appropriate for the given audience.

    kids: elementary only
    middle: elementary + middle
    high: all three tiers
    adult: all
    """
    if audience == "kids":
        return ELEMENTARY_LESSONS
    elif audience == "middle":
        return ELEMENTARY_LESSONS + MIDDLE_SCHOOL_LESSONS
    elif audience in ("high", "adult"):
        return ALL_LESSONS
    return ALL_LESSONS

def get_lesson_by_id(lesson_id: str) -> Dict[str, Any]:
    """Fetch a single lesson by its ID."""
    for lesson in ALL_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    return {}

def get_lessons_by_category(category: str) -> List[Dict[str, Any]]:
    """Return all lessons in a category."""
    return [l for l in ALL_LESSONS if l["category"].lower() == category.lower()]

def get_all_categories() -> List[str]:
    """Return unique category names."""
    seen = []
    for l in ALL_LESSONS:
        if l["category"] not in seen:
            seen.append(l["category"])
    return seen
