"""Configuration and constants for Agent Richy v2 Backend."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ── LLM Settings ─────────────────────────────────────────────────────────
PRIMARY_LLM = "openai"
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1000
GOOGLE_MODEL = "gemini-1.5-flash"

# ── Brand Colors ─────────────────────────────────────────────────────────
COLORS = {
    "navy": "#0A1628",
    "navy_light": "#0F2035",
    "navy_card": "#111D32",
    "blue": "#2563EB",
    "blue_light": "#3B82F6",
    "blue_hover": "#1D4ED8",
    "gold": "#F59E0B",
    "gold_light": "#FBBF24",
    "gold_dim": "#D97706",
    "white": "#FFFFFF",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "green": "#10B981",
    "green_light": "#34D399",
    "red": "#EF4444",
    "red_light": "#F87171",
    "border": "#1E293B",
    "border_light": "#334155",
    "surface": "#0F172A",
    "surface_alt": "#1E293B",
    "gray": "#94A3B8",
    "gray_dark": "#64748B",
}

# ── Free Tier Limits ─────────────────────────────────────────────────────
FREE_MESSAGE_LIMIT = 10
FREE_VIDEO_MODULES = 1
FREE_VIDEO_LESSONS = 2

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

# ── Onboarding Options ───────────────────────────────────────────────────
AGE_RANGES = ["Under 13", "13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

EXPERIENCE_LEVELS = [
    "Beginner — I'm just starting to learn about money",
    "Intermediate — I know the basics but want to improve",
    "Advanced — I'm experienced and want expert strategies",
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
