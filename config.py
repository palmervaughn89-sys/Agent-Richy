"""Configuration and constants for Agent Richy."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ── LLM Settings ─────────────────────────────────────────────────────────
PRIMARY_LLM = "openai"          # "openai" | "google"
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1000
GOOGLE_MODEL = "gemini-1.5-flash"

# ── Brand Colors ─────────────────────────────────────────────────────────
COLORS = {
    "navy":         "#0A1628",
    "navy_light":   "#0F2035",
    "navy_card":    "#111D32",
    "blue":         "#2563EB",
    "blue_light":   "#3B82F6",
    "blue_hover":   "#1D4ED8",
    "gold":         "#F59E0B",
    "gold_light":   "#FBBF24",
    "gold_dim":     "#D97706",
    "white":        "#FFFFFF",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted":   "#64748B",
    "green":        "#10B981",
    "green_light":  "#34D399",
    "red":          "#EF4444",
    "red_light":    "#F87171",
    "border":       "#1E293B",
    "border_light": "#334155",
    "surface":      "#0F172A",
    "surface_alt":  "#1E293B",
    "gray":         "#94A3B8",
    "gray_dark":    "#64748B",
}

# ── Plotly Theme ─────────────────────────────────────────────────────────
PLOTLY_COLORS = [
    COLORS["blue"],
    COLORS["gold"],
    COLORS["green"],
    COLORS["red"],
    "#8B5CF6",   # purple
    "#EC4899",   # pink
    "#06B6D4",   # cyan
    "#F97316",   # orange
]

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text_primary"]),
    margin=dict(t=40, b=20, l=20, r=20),
)

# ── Free Tier Limits ─────────────────────────────────────────────────────
FREE_MESSAGE_LIMIT = 10
FREE_VIDEO_MODULES = 1       # Only Module 1
FREE_VIDEO_LESSONS = 2       # First 2 videos in Module 1

# ── Agent Definitions ────────────────────────────────────────────────────
AGENTS = {
    "coach_richy": {
        "name": "Coach Richy",
        "icon": "💰",
        "color": COLORS["gold"],
        "specialty": "General Financial Coaching",
        "tagline": "Your smart friend who happens to be a financial planner",
        "sample_q": "Help me build a complete financial plan",
        "avatar": "https://api.dicebear.com/7.x/personas/svg?seed=CoachRichy&backgroundColor=F59E0B",
    },
    "budget_bot": {
        "name": "Budget Bot",
        "icon": "📊",
        "color": COLORS["blue"],
        "specialty": "Budgeting & Expense Tracking",
        "tagline": "Analytical, detail-oriented — loves crunching your numbers",
        "sample_q": "Analyze my spending and build a budget",
        "avatar": "https://api.dicebear.com/7.x/personas/svg?seed=BudgetBot&backgroundColor=2563EB",
    },
    "invest_intel": {
        "name": "Invest Intel",
        "icon": "📈",
        "color": COLORS["green"],
        "specialty": "Investing & Portfolio Strategy",
        "tagline": "Confident, strategic, data-driven market insights",
        "sample_q": "How should I invest $500/month?",
        "avatar": "https://api.dicebear.com/7.x/personas/svg?seed=InvestIntel&backgroundColor=10B981",
    },
    "debt_destroyer": {
        "name": "Debt Destroyer",
        "icon": "💳",
        "color": COLORS["red"],
        "specialty": "Debt Payoff Strategies",
        "tagline": "Motivational, action-oriented debt elimination",
        "sample_q": "I have $20K in credit card debt — help!",
        "avatar": "https://api.dicebear.com/7.x/personas/svg?seed=DebtDestroyer&backgroundColor=EF4444",
    },
    "savings_sage": {
        "name": "Savings Sage",
        "icon": "🏦",
        "color": "#8B5CF6",
        "specialty": "Savings & Emergency Funds",
        "tagline": "Patient, goal-oriented savings strategist",
        "sample_q": "How do I build a 6-month emergency fund?",
        "avatar": "https://api.dicebear.com/7.x/personas/svg?seed=SavingsSage&backgroundColor=8B5CF6",
    },
    "kid_coach": {
        "name": "Kid Coach",
        "icon": "🎓",
        "color": "#06B6D4",
        "specialty": "Youth Financial Education",
        "tagline": "Fun, educational — makes money lessons exciting",
        "sample_q": "How can I start earning money as a kid?",
        "avatar": "https://api.dicebear.com/7.x/personas/svg?seed=KidCoach&backgroundColor=06B6D4",
    },
}

# ── Kids Education Modules ───────────────────────────────────────────────
KIDS_MODULES = [
    {
        "id": "module_1",
        "title": "What is Money?",
        "icon": "💵",
        "color": COLORS["gold"],
        "description": "Learn where money comes from, how it works, and why it matters.",
        "lessons": [
            {
                "id": "m1_l1",
                "title": "The History of Money",
                "video_url": "https://www.youtube.com/embed/YCN2aTlocOw",
                "duration": "4:32",
                "description": "From bartering to Bitcoin — discover how money evolved over thousands of years.",
                "objectives": ["Understand why money was invented", "Learn about different forms of money", "Know the difference between currency and value"],
                "quiz": [
                    {"q": "What did people do before money existed?", "choices": ["Traded goods directly (barter)", "Used credit cards", "Didn't buy anything", "Used the internet"], "answer": 0},
                    {"q": "Why was money invented?", "choices": ["To make people rich", "To make trading easier", "Because gold is shiny", "For fun"], "answer": 1},
                ],
            },
            {
                "id": "m1_l2",
                "title": "Coins, Bills & Digital Money",
                "video_url": "https://www.youtube.com/embed/aF8_AYWKYGA",
                "duration": "5:15",
                "description": "Different types of money you use every day — from piggy banks to payment apps.",
                "objectives": ["Identify coins and bills", "Understand digital payments", "Know that money has to be earned"],
                "quiz": [
                    {"q": "Which of these is a form of money?", "choices": ["All of the below", "Coins", "Dollar bills", "Money in a bank app"], "answer": 0},
                    {"q": "Where does money come from?", "choices": ["Trees", "People earn it by working", "It appears magically", "The store gives it to you"], "answer": 1},
                ],
            },
            {
                "id": "m1_l3",
                "title": "Needs vs. Wants",
                "video_url": "https://www.youtube.com/embed/E0F0MU_87b4",
                "duration": "3:48",
                "description": "The most important money lesson — knowing the difference between needs and wants.",
                "objectives": ["Distinguish needs from wants", "Make smarter spending choices", "Prioritize essential spending"],
                "quiz": [
                    {"q": "Which is a NEED?", "choices": ["Food and water", "A new video game", "Designer sneakers", "A skateboard"], "answer": 0},
                    {"q": "What should you buy first?", "choices": ["Needs", "Wants", "Whatever is on sale", "Whatever your friends buy"], "answer": 0},
                    {"q": "Is a phone a need or a want?", "choices": ["It depends on the situation", "Always a need", "Always a want", "It's free"], "answer": 0},
                ],
            },
            {
                "id": "m1_l4",
                "title": "How Banks Work",
                "video_url": "https://www.youtube.com/embed/8N_tupPBtWQ",
                "duration": "4:55",
                "description": "Your money's safe home — learn how banks keep your money and help it grow.",
                "objectives": ["Understand what a bank does", "Learn about savings accounts", "Know your money is safe in a bank"],
                "quiz": [
                    {"q": "What does a bank do with your money?", "choices": ["Keeps it safe and lends some to others", "Spends it on themselves", "Throws it away", "Sends it to another country"], "answer": 0},
                    {"q": "What is interest?", "choices": ["Money the bank pays you for keeping your money there", "A fee for having an account", "Extra money you owe the bank", "A type of tax"], "answer": 0},
                ],
            },
        ],
    },
    {
        "id": "module_2",
        "title": "Saving & Spending",
        "icon": "🐷",
        "color": COLORS["blue"],
        "description": "Build your savings muscle and learn to spend wisely.",
        "lessons": [
            {
                "id": "m2_l1",
                "title": "Pay Yourself First",
                "video_url": "https://www.youtube.com/embed/jm0L5YhSS3g",
                "duration": "4:12",
                "description": "The #1 savings rule — save before you spend!",
                "objectives": ["Learn the 'pay yourself first' rule", "Set up automatic savings", "Create a savings habit"],
                "quiz": [
                    {"q": "What does 'pay yourself first' mean?", "choices": ["Save money before spending on anything else", "Pay your bills first", "Buy yourself a gift", "Don't pay anyone"], "answer": 0},
                    {"q": "When should you save money?", "choices": ["As soon as you get it", "After buying everything you want", "Only on holidays", "Never"], "answer": 0},
                ],
            },
            {
                "id": "m2_l2",
                "title": "Setting Savings Goals",
                "video_url": "https://www.youtube.com/embed/KjOAtcLvnyA",
                "duration": "5:30",
                "description": "Want something special? Learn to save for it step by step.",
                "objectives": ["Set SMART savings goals", "Calculate how long it takes to save", "Stay motivated while saving"],
                "quiz": [
                    {"q": "What makes a good savings goal?", "choices": ["Specific amount and deadline", "Just 'save more money'", "As much as possible", "Whatever your parents say"], "answer": 0},
                    {"q": "You want to buy a $60 game. You save $10/week. How many weeks?", "choices": ["6 weeks", "60 weeks", "10 weeks", "1 week"], "answer": 0},
                ],
            },
            {
                "id": "m2_l3",
                "title": "Smart Spending Decisions",
                "video_url": "https://www.youtube.com/embed/TXA2jdEaqJs",
                "duration": "4:45",
                "description": "Learn to think before you spend — and keep more money in your pocket.",
                "objectives": ["Use the 24-hour rule", "Compare prices before buying", "Avoid impulse purchases"],
                "quiz": [
                    {"q": "What is the 24-hour rule?", "choices": ["Wait 24 hours before buying something you want", "You can only shop for 24 hours", "Return items within 24 hours", "Spend for only 24 minutes"], "answer": 0},
                    {"q": "What should you do before buying something?", "choices": ["Compare prices and think about it", "Buy it immediately", "Buy the most expensive version", "Ask a stranger"], "answer": 0},
                ],
            },
            {
                "id": "m2_l4",
                "title": "The Power of Compound Interest",
                "video_url": "https://www.youtube.com/embed/MjAHcCpEmMM",
                "duration": "5:10",
                "description": "How your money can grow while you sleep — the magic of compound interest!",
                "objectives": ["Understand compound interest", "See how time makes money grow", "Start saving early"],
                "quiz": [
                    {"q": "What is compound interest?", "choices": ["Earning interest on your interest", "A type of bank fee", "Extra money you pay the bank", "Interest that disappears"], "answer": 0},
                    {"q": "Who earns more: someone who starts saving at 15 or at 25?", "choices": ["The person who starts at 15", "The person who starts at 25", "They earn the same", "Neither earns anything"], "answer": 0},
                ],
            },
        ],
    },
    {
        "id": "module_3",
        "title": "Earning & Growing Money",
        "icon": "🌱",
        "color": COLORS["green"],
        "description": "Discover ways to earn money and make it grow over time.",
        "lessons": [
            {
                "id": "m3_l1",
                "title": "Ways Kids Can Earn Money",
                "video_url": "https://www.youtube.com/embed/346CwLMNVCg",
                "duration": "6:20",
                "description": "From lemonade stands to lawn care — real ways kids make real money.",
                "objectives": ["Identify age-appropriate earning opportunities", "Understand work ethic", "Start your first mini-business"],
                "quiz": [
                    {"q": "Which is a good way for kids to earn money?", "choices": ["All of the below", "Do chores for neighbors", "Sell crafts or baked goods", "Tutor younger kids"], "answer": 0},
                    {"q": "What's the most important quality for earning money?", "choices": ["Being reliable and working hard", "Being lucky", "Having rich parents", "Being the oldest kid"], "answer": 0},
                ],
            },
            {
                "id": "m3_l2",
                "title": "Entrepreneurship for Young People",
                "video_url": "https://www.youtube.com/embed/PyIcVsbPbQ0",
                "duration": "5:45",
                "description": "Think like a business owner — even as a kid you can start something amazing.",
                "objectives": ["Understand what an entrepreneur does", "Generate business ideas", "Learn basic business planning"],
                "quiz": [
                    {"q": "What is an entrepreneur?", "choices": ["Someone who starts a business", "Someone who works for the government", "A type of teacher", "A bank employee"], "answer": 0},
                    {"q": "What's the first step to starting a business?", "choices": ["Find a problem you can solve", "Borrow a lot of money", "Quit school", "Copy someone else's business exactly"], "answer": 0},
                ],
            },
            {
                "id": "m3_l3",
                "title": "What is Investing?",
                "video_url": "https://www.youtube.com/embed/WEDIj9JBTC8",
                "duration": "5:00",
                "description": "Making your money work for YOU — intro to stocks, bonds, and more.",
                "objectives": ["Understand what investing means", "Learn about stocks and bonds", "Know that investing involves risk and reward"],
                "quiz": [
                    {"q": "What is investing?", "choices": ["Using money to make more money over time", "Putting money under your mattress", "Spending money on things you want", "Giving money away"], "answer": 0},
                    {"q": "What is a stock?", "choices": ["Owning a tiny piece of a company", "A type of soup", "Money in a savings account", "A loan from the bank"], "answer": 0},
                ],
            },
            {
                "id": "m3_l4",
                "title": "Good Debt vs. Bad Debt",
                "video_url": "https://www.youtube.com/embed/WnO1T7bnFGU",
                "duration": "4:30",
                "description": "Not all borrowing is bad — learn the difference between smart and dangerous debt.",
                "objectives": ["Distinguish good debt from bad debt", "Understand interest on loans", "Make smart borrowing decisions"],
                "quiz": [
                    {"q": "Which is an example of 'good debt'?", "choices": ["A student loan for education", "Credit card debt for designer clothes", "Borrowing to buy the latest phone", "A loan for a vacation"], "answer": 0},
                    {"q": "What makes debt 'bad'?", "choices": ["High interest on things that lose value", "Any borrowing at all", "Lending money to a friend", "Having a savings account"], "answer": 0},
                ],
            },
        ],
    },
    {
        "id": "module_4",
        "title": "Smart Money Habits",
        "icon": "🧠",
        "color": "#8B5CF6",
        "description": "Build lifelong habits that make you wealthy and wise with money.",
        "lessons": [
            {
                "id": "m4_l1",
                "title": "The 50/30/20 Budget Rule",
                "video_url": "https://www.youtube.com/embed/HQzoZfc3GwQ",
                "duration": "4:50",
                "description": "The simplest budget rule that works for any income level.",
                "objectives": ["Understand the 50/30/20 rule", "Categorize spending", "Create a simple budget"],
                "quiz": [
                    {"q": "In the 50/30/20 rule, what does 50% go to?", "choices": ["Needs (food, housing, bills)", "Wants (fun stuff)", "Savings", "Investments"], "answer": 0},
                    {"q": "If you earn $100, how much should you save?", "choices": ["$20", "$50", "$30", "$10"], "answer": 0},
                ],
            },
            {
                "id": "m4_l2",
                "title": "Avoiding Money Traps",
                "video_url": "https://www.youtube.com/embed/A8LdSIqzoE4",
                "duration": "5:20",
                "description": "Scams, FOMO spending, and sneaky fees — protect your money!",
                "objectives": ["Recognize common money traps", "Avoid peer pressure spending", "Protect yourself from scams"],
                "quiz": [
                    {"q": "What is FOMO spending?", "choices": ["Buying things because you're afraid of missing out", "Spending money overseas", "A type of investment", "Saving for the future"], "answer": 0},
                    {"q": "If someone offers you 'free money,' what should you do?", "choices": ["Be suspicious — it's probably a scam", "Give them your bank account info", "Send them money first", "Tell all your friends about it"], "answer": 0},
                ],
            },
            {
                "id": "m4_l3",
                "title": "Building a Money Routine",
                "video_url": "https://www.youtube.com/embed/Gs8K-R9PEnw",
                "duration": "4:15",
                "description": "Create daily and weekly money habits that build real wealth over time.",
                "objectives": ["Create a daily money check-in", "Track spending weekly", "Build consistency with money management"],
                "quiz": [
                    {"q": "How often should you check your money?", "choices": ["At least once a week", "Once a year", "Only when you're broke", "Never — it's stressful"], "answer": 0},
                    {"q": "What's the best money habit?", "choices": ["Saving consistently, even small amounts", "Spending everything and hoping for the best", "Only thinking about money when you need something", "Avoiding all money topics"], "answer": 0},
                ],
            },
            {
                "id": "m4_l4",
                "title": "Your Financial Future",
                "video_url": "https://www.youtube.com/embed/fJV-dvf_2HA",
                "duration": "5:30",
                "description": "Plan ahead — where do you want to be in 5, 10, and 20 years?",
                "objectives": ["Think about long-term financial goals", "Understand the power of starting early", "Create a personal money vision"],
                "quiz": [
                    {"q": "Why should you think about your financial future now?", "choices": ["Starting early gives you more time to grow wealth", "You should only think about today", "Thinking about the future is scary", "Money doesn't matter"], "answer": 0},
                    {"q": "What's the biggest advantage young people have?", "choices": ["Time — money can grow for decades", "More allowance", "Parents pay for everything", "No bills to pay"], "answer": 0},
                ],
            },
        ],
    },
]

# ── Onboarding Options ───────────────────────────────────────────────────
AGE_RANGES = [
    "Under 13",
    "13-17",
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65+",
]

EXPERIENCE_LEVELS = [
    "Beginner — I'm just starting to learn about money",
    "Intermediate — I know the basics but want to improve",
    "Advanced — I'm experienced and want expert strategies",
]

EMPLOYMENT_STATUS = [
    "Employed (Full-time)",
    "Employed (Part-time)",
    "Self-employed / Freelancer",
    "Student",
    "Unemployed / Between jobs",
    "Retired",
    "Homemaker",
]

INCOME_RANGES = [
    "Under $25,000",
    "$25,000 - $49,999",
    "$50,000 - $74,999",
    "$75,000 - $99,999",
    "$100,000 - $149,999",
    "$150,000 - $249,999",
    "$250,000+",
    "Prefer not to say",
]

FINANCIAL_GOALS = [
    "Build Emergency Fund",
    "Pay Off Debt",
    "Start Investing",
    "Save for Retirement",
    "Teach Kids About Money",
    "Buy a Home",
    "Build Passive Income",
    "Improve Credit Score",
    "Create a Budget",
    "Plan for College",
]
