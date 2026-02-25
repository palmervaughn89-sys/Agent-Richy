"""Animated HTML5 Financial Education Shorts — TikTok-style lessons.

Generates self-contained HTML/CSS/JS animated "videos" that play
directly in the browser via Streamlit's components.html().
No GPU required — pure CSS/JS animations.

Each "video" is a 15-25 second animated sequence with:
- CSS keyframe animations & SVG graphics
- JavaScript scene-sequencing engine
- Animated counters, charts, particles
- Dark theme with gold accents
- TikTok vertical (9:16) format
"""

from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
#  LESSON DEFINITIONS — compact scene configs for all 30 videos
# ═══════════════════════════════════════════════════════════════════════

ANIMATED_SHORTS: Dict[str, dict] = {
    # ── KIDS (Elementary) ────────────────────────────────────────────
    "savings_piggy_bank": {
        "title": "The Magic Piggy Bank",
        "audience": "kids",
        "topic": "saving",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        "scenes": [
            {"t": "title", "icon": "🐷", "text": "The Magic\nPiggy Bank", "sub": "Feed it & watch it grow!"},
            {"t": "rain", "icons": ["🪙", "💰", "✨", "🪙", "💵"], "label": "Coins going in..."},
            {"t": "counter", "label": "Your Savings", "start": 0, "end": 52, "prefix": "$", "color": "#FFD700"},
            {"t": "bars", "title": "Piggy Bank Growth", "items": [
                ("Week 1", 5, "#FFD700"), ("Month 1", 20, "#FFA500"),
                ("Month 6", 55, "#FF6B6B"), ("Year 1", 100, "#4CAF50")]},
            {"t": "lesson", "icon": "🌟", "text": "Every dollar you save makes your piggy bank bigger & stronger!"},
        ],
    },
    "lemonade_stand": {
        "title": "Your First Business",
        "audience": "kids",
        "topic": "earning",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2d1b4e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🍋", "text": "Your First\nBusiness", "sub": "Earn • Save • Spend"},
            {"t": "stack", "title": "Steps to Start", "items": [
                ("🍋 Setup: Lemonade Stand", "#FFD700"),
                ("👥 Customers Line Up", "#4CAF50"),
                ("💵 You Earn $25!", "#FF6B6B"),
                ("🐷 Save Half = $12.50", "#2196F3")]},
            {"t": "split", "left_icon": "🐷", "left_label": "SAVE",
             "left_items": ["$12.50", "For your future", "Grows over time"],
             "right_icon": "🎮", "right_label": "SPEND",
             "right_items": ["$12.50", "For fun stuff", "Enjoy today"]},
            {"t": "lesson", "icon": "💡", "text": "Pay yourself first — save BEFORE you spend!"},
        ],
    },
    "needs_vs_wants": {
        "title": "Needs vs. Wants",
        "audience": "kids",
        "topic": "budgeting",
        "bg": "linear-gradient(180deg, #0f3460 0%, #1a1a2e 50%, #16213e 100%)",
        "scenes": [
            {"t": "title", "icon": "🤔", "text": "Needs vs.\nWants", "sub": "Know the difference!"},
            {"t": "split", "left_icon": "✅", "left_label": "NEEDS",
             "left_items": ["🍎 Food", "🏠 Home", "📚 School", "🧥 Clothes"],
             "right_icon": "🎯", "right_label": "WANTS",
             "right_items": ["🎮 Games", "🍭 Candy", "👟 Jordans", "🎵 Concert"]},
            {"t": "stack", "title": "The Rule", "items": [
                ("1️⃣  Cover NEEDS first", "#4CAF50"),
                ("2️⃣  Save some money", "#2196F3"),
                ("3️⃣  THEN enjoy wants!", "#FFD700")]},
            {"t": "lesson", "icon": "🧠", "text": "Needs keep you safe. Wants make life fun. Needs FIRST!"},
        ],
    },
    "coins_and_counting": {
        "title": "Coins & Counting",
        "audience": "kids",
        "topic": "money basics",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #162d2e 50%, #0f3460 100%)",
        "scenes": [
            {"t": "title", "icon": "🪙", "text": "Coins, Dollars\n& Making Change", "sub": "Money math superpower!"},
            {"t": "stack", "title": "Know Your Coins", "items": [
                ("1¢  Penny — copper shiny", "#CD7F32"),
                ("5¢  Nickel — chunky & silver", "#C0C0C0"),
                ("10¢ Dime — tiny but mighty", "#FFD700"),
                ("25¢ Quarter — the big one!", "#4CAF50")]},
            {"t": "counter", "label": "4 Quarters =", "start": 0, "end": 100, "prefix": "$1.", "suffix": "0", "color": "#4CAF50"},
            {"t": "lesson", "icon": "💪", "text": "Count your change — that's YOUR money!"},
        ],
    },
    "opportunity_cost_crossroads": {
        "title": "The Crossroads of Choice",
        "audience": "kids",
        "topic": "decision making",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e1a3e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🔀", "text": "The Crossroads\nof Choice", "sub": "Every choice has a cost"},
            {"t": "split", "left_icon": "🎮", "left_label": "PATH A",
             "left_items": ["Buy the game", "$40 spent", "Fun today!"],
             "right_icon": "🏀", "right_label": "PATH B",
             "right_items": ["Buy basketball", "$40 spent", "Play for years!"]},
            {"t": "stack", "title": "Opportunity Cost", "items": [
                ("Choosing A means giving up B", "#FF6B6B"),
                ("Choosing B means giving up A", "#2196F3"),
                ("Think: which lasts longer?", "#FFD700")]},
            {"t": "lesson", "icon": "🤔", "text": "Think about what you'll miss BEFORE you decide!"},
        ],
    },
    "marshmallow_patience": {
        "title": "The Marshmallow Test",
        "audience": "kids",
        "topic": "mindset",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #3e2a1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🍡", "text": "The Marshmallow\nTest", "sub": "Patience pays off!"},
            {"t": "split", "left_icon": "😋", "left_label": "EAT NOW",
             "left_items": ["1 marshmallow", "Instant joy", "Gone forever"],
             "right_icon": "😊", "right_label": "WAIT 15 MIN",
             "right_items": ["2 marshmallows!", "Double reward", "Self-control wins"]},
            {"t": "counter", "label": "Patience Reward", "start": 1, "end": 2, "prefix": "", "suffix": "x reward", "color": "#FF6B6B"},
            {"t": "lesson", "icon": "🏆", "text": "Waiting for a bigger reward is how you build wealth!"},
        ],
    },
    "giving_jar": {
        "title": "The Joy of Giving",
        "audience": "kids",
        "topic": "community",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #1a2e1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🫙", "text": "Save • Spend\n• Give", "sub": "Three jars, one plan!"},
            {"t": "bars", "title": "Fill Your Jars", "items": [
                ("🐷 SAVE", 40, "#4CAF50"), ("🎮 SPEND", 40, "#2196F3"),
                ("❤️ GIVE", 20, "#FF6B6B")]},
            {"t": "stack", "title": "Giving Creates", "items": [
                ("🍲 Meals for families", "#FFA500"),
                ("🎁 Gifts for kids", "#FF6B6B"),
                ("🌳 Trees planted", "#4CAF50")]},
            {"t": "lesson", "icon": "💛", "text": "Even a little giving makes the world better — and YOU feel great!"},
        ],
    },
    "bank_vault_adventure": {
        "title": "Inside the Bank",
        "audience": "kids",
        "topic": "banking",
        "bg": "linear-gradient(180deg, #0f3460 0%, #1a1a2e 50%, #16213e 100%)",
        "scenes": [
            {"t": "title", "icon": "🏦", "text": "Inside the\nBank Vault", "sub": "Your money, safe & growing"},
            {"t": "rain", "icons": ["🪙", "💵", "🏦", "✨", "💰"], "label": "Deposit your savings"},
            {"t": "counter", "label": "Interest Earned", "start": 100, "end": 105, "prefix": "$", "suffix": "", "color": "#4CAF50"},
            {"t": "stack", "title": "Bank Benefits", "items": [
                ("🔒 Safe from theft", "#4CAF50"),
                ("💸 Earns interest", "#FFD700"),
                ("💳 Easy access", "#2196F3"),
                ("📱 Track online", "#FF6B6B")]},
            {"t": "lesson", "icon": "🌙", "text": "Banks pay you interest — your money makes money while you sleep!"},
        ],
    },

    # ── MIDDLE SCHOOL ────────────────────────────────────────────────
    "compound_interest_tree": {
        "title": "The Money Tree",
        "audience": "middle",
        "topic": "compound interest",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #1a3e1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🌳", "text": "The Money\nTree", "sub": "Compound interest is magic"},
            {"t": "bars", "title": "$100 Growing at 8%/yr", "items": [
                ("Year 1", 15, "#66BB6A"), ("Year 5", 30, "#4CAF50"),
                ("Year 10", 50, "#388E3C"), ("Year 20", 100, "#1B5E20")]},
            {"t": "counter", "label": "$100 After 20 Years", "start": 100, "end": 466, "prefix": "$", "color": "#4CAF50"},
            {"t": "lesson", "icon": "🌱", "text": "Money earns money ON TOP of money. $100 → $466 without adding a dime!"},
        ],
    },
    "compound_snowball": {
        "title": "The Compound Snowball",
        "audience": "middle",
        "topic": "compound interest",
        "bg": "linear-gradient(180deg, #16213e 0%, #1a2a4e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "⛷️", "text": "The Compound\nSnowball", "sub": "Small start → huge finish"},
            {"t": "counter", "label": "$50/month at 8%", "start": 0, "end": 18000, "prefix": "$", "color": "#87CEEB"},
            {"t": "bars", "title": "Your Snowball Growing", "items": [
                ("You Put In", 60, "#2196F3"), ("Interest Added", 40, "#FFD700")]},
            {"t": "lesson", "icon": "❄️", "text": "Start early! $50/month invested = $18,000+ in 10 years!"},
        ],
    },
    "budget_pie_chart": {
        "title": "Where Does Your Money Go?",
        "audience": "middle",
        "topic": "budgeting",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e1a3e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🥧", "text": "Where Does Your\nMoney Go?", "sub": "The 50/30/20 rule"},
            {"t": "pie", "title": "The 50/30/20 Budget", "slices": [
                ("Needs", 50, "#4CAF50"), ("Wants", 30, "#FF9800"), ("Savings", 20, "#2196F3")]},
            {"t": "stack", "title": "What's in Each?", "items": [
                ("50% NEEDS: rent, food, bills", "#4CAF50"),
                ("30% WANTS: fun, dining, shopping", "#FF9800"),
                ("20% SAVE: future you!", "#2196F3")]},
            {"t": "lesson", "icon": "📊", "text": "A budget = a PLAN for your money. Plan it, don't wonder where it went!"},
        ],
    },
    "impulse_buying_trap": {
        "title": "The Impulse Trap",
        "audience": "middle",
        "topic": "bad habits",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #3e1a1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🛒", "text": "The Impulse\nBuying Trap", "sub": "Don't fall for it!"},
            {"t": "split", "left_icon": "❌", "left_label": "IMPULSE BUY",
             "left_items": ["See it → Buy it", "Wallet = empty", "Regret in 2 days"],
             "right_icon": "✅", "right_label": "48-HOUR RULE",
             "right_items": ["See it → Wait 48h", "Still want it?", "70% say NO"]},
            {"t": "counter", "label": "Impulse Saves/Year", "start": 0, "end": 1200, "prefix": "$", "color": "#FF6B6B"},
            {"t": "lesson", "icon": "⏰", "text": "Wait 48 hours before any non-essential purchase. You'll save $1,000+/year!"},
        ],
    },
    "smart_shopping_detective": {
        "title": "Smart Shopping Detective",
        "audience": "middle",
        "topic": "spending",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #1a2e3e 50%, #0f3460 100%)",
        "scenes": [
            {"t": "title", "icon": "🔍", "text": "Smart Shopping\nDetective", "sub": "Don't believe every 'SALE'!"},
            {"t": "stack", "title": "Store Tricks to Spot", "items": [
                ("🚨 'SALE' signs everywhere", "#FF6B6B"),
                ("⏰ 'LIMITED TIME' pressure", "#FFA500"),
                ("🤑 Inflated 'was' prices", "#FF9800"),
                ("🛒 Items near checkout", "#E91E63")]},
            {"t": "stack", "title": "Your Detective Tools", "items": [
                ("🔍 Compare prices first", "#4CAF50"),
                ("📱 Use price-check apps", "#2196F3"),
                ("⏰ Wait 48 hours", "#FFD700")]},
            {"t": "lesson", "icon": "🕵️", "text": "Be a detective — compare prices, wait before buying, ignore 'SALE' hype!"},
        ],
    },
    "checking_vs_savings": {
        "title": "Checking vs. Savings",
        "audience": "middle",
        "topic": "banking",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #1a2e3e 100%)",
        "scenes": [
            {"t": "title", "icon": "🏦", "text": "Checking vs.\nSavings", "sub": "River vs. Lake"},
            {"t": "split", "left_icon": "🌊", "left_label": "CHECKING",
             "left_items": ["Fast-flowing", "Daily spending", "Debit card", "~0% interest"],
             "right_icon": "🏔️", "right_label": "SAVINGS",
             "right_items": ["Calm lake", "Grows slowly", "Emergency $", "4-5% APY"]},
            {"t": "bars", "title": "Interest Comparison", "items": [
                ("Checking: 0.01%", 1, "#FF6B6B"), ("Savings: 4.5%", 90, "#4CAF50")]},
            {"t": "lesson", "icon": "💧", "text": "Checking = spending money. Savings = growing money. Use BOTH!"},
        ],
    },
    "teen_entrepreneur_montage": {
        "title": "Think Like an Entrepreneur",
        "audience": "middle",
        "topic": "earning",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #3e2e1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "💡", "text": "Think Like an\nEntrepreneur", "sub": "Problem → Solution → Profit"},
            {"t": "stack", "title": "The Formula", "items": [
                ("🔍 Find a PROBLEM", "#FF6B6B"),
                ("💡 Create a SOLUTION", "#FFD700"),
                ("💰 Earn PROFIT", "#4CAF50")]},
            {"t": "bars", "title": "Teen Hustle Ideas", "items": [
                ("Tutoring: $25/hr", 50, "#4CAF50"), ("Design: $30/hr", 60, "#2196F3"),
                ("Lawn Care: $40/job", 80, "#FFD700"), ("Social Media: $50/post", 100, "#FF6B6B")]},
            {"t": "lesson", "icon": "🚀", "text": "Entrepreneurs solve problems for profit. What problem can YOU solve?"},
        ],
    },
    "credit_vs_debit_battle": {
        "title": "Credit vs. Debit",
        "audience": "middle",
        "topic": "credit",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e1a2e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "💳", "text": "Credit vs.\nDebit Card", "sub": "Know the difference!"},
            {"t": "split", "left_icon": "🔵", "left_label": "DEBIT",
             "left_items": ["YOUR money", "From checking", "No interest", "Spend what you have"],
             "right_icon": "🔴", "right_label": "CREDIT",
             "right_items": ["BANK'S money", "Must repay", "22% interest!", "Can grow debt"]},
            {"t": "counter", "label": "Credit Card Interest on $1,000", "start": 1000, "end": 1220, "prefix": "$", "color": "#FF6B6B"},
            {"t": "lesson", "icon": "⚡", "text": "If you use credit, ALWAYS pay in full to avoid the interest trap!"},
        ],
    },
    "inflation_shrinking_dollar": {
        "title": "The Shrinking Dollar",
        "audience": "middle",
        "topic": "economics",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #3e3e1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "📉", "text": "The Shrinking\nDollar", "sub": "Inflation is real"},
            {"t": "bars", "title": "$1 Buying Power Over Time", "items": [
                ("1990: $1.00", 100, "#4CAF50"), ("2000: $0.78", 78, "#FFD700"),
                ("2010: $0.64", 64, "#FFA500"), ("2024: $0.49", 49, "#FF6B6B")]},
            {"t": "counter", "label": "Movie Ticket 1990→2024", "start": 4, "end": 12, "prefix": "$", "color": "#FF6B6B"},
            {"t": "lesson", "icon": "📈", "text": "Inflation makes $ buy less over time. Investing beats inflation!"},
        ],
    },
    "scam_alert_shield": {
        "title": "Scam Alert!",
        "audience": "middle",
        "topic": "safety",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #1a1a3e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🛡️", "text": "Scam Alert:\nProtect Your $", "sub": "Don't fall for it!"},
            {"t": "stack", "title": "Common Scam Lines", "items": [
                ("🚫 'You won a prize!'", "#FF6B6B"),
                ("🚫 'Send $50 to get $500!'", "#E91E63"),
                ("🚫 'Click this link now!'", "#F44336"),
                ("🚫 'Give me your password'", "#D32F2F")]},
            {"t": "stack", "title": "Your Shield", "items": [
                ("✅ Never share passwords", "#4CAF50"),
                ("✅ If it's too good = SCAM", "#2196F3"),
                ("✅ Tell a trusted adult", "#FFD700")]},
            {"t": "lesson", "icon": "🛡️", "text": "Send money to GET money? ALWAYS a scam. Protect yourself!"},
        ],
    },
    "paycheck_breakdown_animation": {
        "title": "Your Paycheck Explained",
        "audience": "middle",
        "topic": "taxes",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #1a3e2e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "💵", "text": "Where Does Your\nPaycheck Go?", "sub": "Gross vs. Net pay"},
            {"t": "bars", "title": "From $480 Gross Pay", "items": [
                ("Take Home: $412", 86, "#4CAF50"), ("Federal Tax: $36", 7, "#FF9800"),
                ("State Tax: $14", 3, "#FF6B6B"), ("FICA/SS: $18", 4, "#9C27B0")]},
            {"t": "stack", "title": "Taxes Fund", "items": [
                ("🏫 Schools & teachers", "#2196F3"),
                ("🚗 Roads & bridges", "#FFA500"),
                ("🚒 Fire & police", "#FF6B6B"),
                ("🏥 Hospitals", "#4CAF50")]},
            {"t": "lesson", "icon": "📝", "text": "Gross ≠ Net. Understand what's taken out BEFORE you spend!"},
        ],
    },
    "charity_impact_ripple": {
        "title": "Your Donation Ripples",
        "audience": "middle",
        "topic": "community",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #1a2e3e 50%, #0f3460 100%)",
        "scenes": [
            {"t": "title", "icon": "🌊", "text": "Your Donation\nCreates Ripples", "sub": "Small acts, big impact"},
            {"t": "rain", "icons": ["❤️", "🪙", "🌊", "✨", "🌍"], "label": "One coin drops..."},
            {"t": "stack", "title": "Ripple Effects", "items": [
                ("🍲 A family eats dinner", "#FFA500"),
                ("📚 A child gets books", "#2196F3"),
                ("🌳 A garden blooms", "#4CAF50"),
                ("💛 A community thrives", "#FFD700")]},
            {"t": "lesson", "icon": "🌟", "text": "Even small donations create big ripples. Give with intention!"},
        ],
    },

    # ── HIGH SCHOOL ──────────────────────────────────────────────────
    "stock_market_rollercoaster": {
        "title": "Stock Market Rollercoaster",
        "audience": "high",
        "topic": "investing",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #0f3460 50%, #1a3e2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🎢", "text": "The Stock Market\nRollercoaster", "sub": "Scary ride, amazing destination"},
            {"t": "chart", "title": "S&P 500 Over Time", "points": [
                10, 15, 12, 20, 17, 25, 20, 35, 30, 45, 38, 55, 50, 70, 65, 85, 80, 100]},
            {"t": "split", "left_icon": "😬", "left_label": "SHORT TERM",
             "left_items": ["-30% crash", "Panic selling", "Lose money"],
             "right_icon": "🤑", "right_label": "LONG TERM",
             "right_items": ["+10%/yr avg", "Stay invested", "Build wealth"]},
            {"t": "lesson", "icon": "🎢", "text": "Markets go up AND down. Over 10-20 years = always UP. Stay patient!"},
        ],
    },
    "roth_ira_rocket": {
        "title": "The Roth IRA Rocket",
        "audience": "high",
        "topic": "investing",
        "bg": "linear-gradient(180deg, #0a0a2e 0%, #16213e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🚀", "text": "The Roth IRA\nRocket", "sub": "Tax-free growth to the moon"},
            {"t": "counter", "label": "$500/mo from age 18→65", "start": 0, "end": 1700000, "prefix": "$", "color": "#FFD700"},
            {"t": "bars", "title": "Roth IRA Power", "items": [
                ("You Invest: $282K", 30, "#2196F3"), ("Growth: $1.4M+", 100, "#4CAF50")]},
            {"t": "stack", "title": "Why Roth IRA?", "items": [
                ("✅ Tax-FREE growth", "#4CAF50"),
                ("✅ $7,000/yr max (2024)", "#2196F3"),
                ("✅ Withdraw tax-free in retirement", "#FFD700"),
                ("✅ Start as a TEEN!", "#FF6B6B")]},
            {"t": "lesson", "icon": "🌙", "text": "Start a Roth IRA as a teen → $1M+ by retirement. Tax FREE!"},
        ],
    },
    "two_paths": {
        "title": "Two Paths: Saver vs. Spender",
        "audience": "high",
        "topic": "bad habits",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e1a1a 50%, #1a2e1a 100%)",
        "scenes": [
            {"t": "title", "icon": "🔀", "text": "Two Paths\n10 Years Later", "sub": "Same income, different choices"},
            {"t": "split", "left_icon": "🌱", "left_label": "SAVER",
             "left_items": ["Saves $100/mo", "Invests at 8%", "$18,295 →", "Car + freedom"],
             "right_icon": "🔥", "right_label": "SPENDER",
             "right_items": ["Spends $100/mo", "Fast food & stuff", "$0 saved", "Broke & stressed"]},
            {"t": "counter", "label": "$100/mo × 10 Years at 8%", "start": 0, "end": 18295, "prefix": "$", "color": "#4CAF50"},
            {"t": "lesson", "icon": "🔀", "text": "Small choices today = massive differences tomorrow. Choose wisely!"},
        ],
    },
    "debt_monster": {
        "title": "The Debt Monster",
        "audience": "high",
        "topic": "debt",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #3e1a1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "👾", "text": "The Debt\nMonster", "sub": "Kill it before it grows!"},
            {"t": "bars", "title": "Debt + Interest Growth", "items": [
                ("Start: $1,000", 20, "#FFD700"), ("Year 1: $1,220", 30, "#FFA500"),
                ("Year 3: $1,816", 50, "#FF6B6B"), ("Year 5: $2,700", 80, "#E91E63"),
                ("Year 10: $7,305", 100, "#D32F2F")]},
            {"t": "counter", "label": "$1,000 at 22% for 10yr", "start": 1000, "end": 7305, "prefix": "$", "color": "#FF6B6B"},
            {"t": "lesson", "icon": "⚔️", "text": "Debt grows like a monster. Attack it early — don't let it grow!"},
        ],
    },
    "side_hustle_montage": {
        "title": "Side Hustle Montage",
        "audience": "high",
        "topic": "earning",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e2e1a 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "💪", "text": "Side Hustle\nMontage", "sub": "Stack those income streams!"},
            {"t": "bars", "title": "Monthly Hustle Income", "items": [
                ("🌿 Lawn Care: $400", 40, "#4CAF50"), ("🎨 Freelance: $600", 60, "#2196F3"),
                ("📱 Social Media: $300", 30, "#E91E63"), ("📚 Tutoring: $500", 50, "#FFD700")]},
            {"t": "counter", "label": "Stacked Monthly Income", "start": 0, "end": 1800, "prefix": "$", "color": "#FFD700"},
            {"t": "lesson", "icon": "🔥", "text": "Don't need ONE perfect job — stack multiple hustles!"},
        ],
    },
    "credit_score_dashboard": {
        "title": "Your Credit Score",
        "audience": "high",
        "topic": "credit",
        "bg": "linear-gradient(180deg, #0a0a2e 0%, #16213e 50%, #0f3460 100%)",
        "scenes": [
            {"t": "title", "icon": "📊", "text": "Your Credit\nScore Dashboard", "sub": "Your financial GPA"},
            {"t": "gauge", "label": "Credit Score", "value": 750, "min": 300, "max": 850,
             "zones": [("Poor", 580, "#FF6B6B"), ("Fair", 670, "#FFA500"), ("Good", 740, "#FFD700"), ("Excellent", 850, "#4CAF50")]},
            {"t": "pie", "title": "Score Factors", "slices": [
                ("Payment History", 35, "#4CAF50"), ("Amounts Owed", 30, "#2196F3"),
                ("Length", 15, "#FFD700"), ("New Credit", 10, "#FF9800"), ("Mix", 10, "#E91E63")]},
            {"t": "lesson", "icon": "💪", "text": "Build it early: pay on time, keep balances low, be patient!"},
        ],
    },
    "student_loan_comparison": {
        "title": "Student Loan Reality",
        "audience": "high",
        "topic": "debt",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e1a2e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🎓", "text": "Student Loan\nReality Check", "sub": "Same degree, different debt"},
            {"t": "split", "left_icon": "🏛️", "left_label": "PRIVATE $55K/yr",
             "left_items": ["4 years = $220K", "Monthly: $2,500", "10 years to repay", "Total: $300K+"],
             "right_icon": "🏫", "right_label": "STATE $12K/yr",
             "right_items": ["4 years = $48K", "Monthly: $500", "10 years to repay", "Total: $60K"]},
            {"t": "counter", "label": "You SAVE choosing state", "start": 0, "end": 240000, "prefix": "$", "color": "#4CAF50"},
            {"t": "lesson", "icon": "🎓", "text": "Same diploma, WAY less debt. The school name matters less than debt!"},
        ],
    },
    "first_car_financial_guide": {
        "title": "Your First Car",
        "audience": "high",
        "topic": "major purchases",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🚗", "text": "Your First Car:\nDon't Get Wrecked", "sub": "The 20/4/10 rule"},
            {"t": "split", "left_icon": "✨", "left_label": "NEW $35K",
             "left_items": ["$700/mo payment", "$200/mo insurance", "Loses 20% yr 1", "Stress!"],
             "right_icon": "🔧", "right_label": "USED $12K",
             "right_items": ["$250/mo payment", "$120/mo insurance", "Already depreciated", "Smart!"]},
            {"t": "stack", "title": "The 20/4/10 Rule", "items": [
                ("20% down payment", "#FFD700"),
                ("4-year loan maximum", "#2196F3"),
                ("10% of income max for car costs", "#4CAF50")]},
            {"t": "lesson", "icon": "🚗", "text": "First car = reliable & affordable. Not flashy. Follow 20/4/10!"},
        ],
    },
    "first_apartment_walkthrough": {
        "title": "Renting Your First Place",
        "audience": "high",
        "topic": "housing",
        "bg": "linear-gradient(180deg, #1a1a2e 0%, #2e1a3e 50%, #1a1a2e 100%)",
        "scenes": [
            {"t": "title", "icon": "🏠", "text": "Renting Your\nFirst Apartment", "sub": "The 30% rule"},
            {"t": "stack", "title": "Monthly Costs", "items": [
                ("🏠 Rent: $900", "#FF6B6B"),
                ("💡 Utilities: $150", "#FFA500"),
                ("🛡️ Renters Insurance: $20", "#2196F3"),
                ("🍳 Furnishing: $40/mo", "#4CAF50")]},
            {"t": "bars", "title": "Income % on Housing", "items": [
                ("Solo: 45% ❌", 90, "#FF6B6B"),
                ("Roommate: 25% ✅", 50, "#4CAF50")]},
            {"t": "lesson", "icon": "🏠", "text": "Keep housing under 30% of income. Roommates = wealth strategy!"},
        ],
    },
    "insurance_shield_animation": {
        "title": "Insurance Shield",
        "audience": "high",
        "topic": "protection",
        "bg": "linear-gradient(180deg, #0a0a2e 0%, #1a1a2e 50%, #16213e 100%)",
        "scenes": [
            {"t": "title", "icon": "🛡️", "text": "Insurance:\nYour Financial Shield", "sub": "Protection costs less than disaster"},
            {"t": "split", "left_icon": "🛡️", "left_label": "WITH INSURANCE",
             "left_items": ["Pay $200/mo", "Car wreck → $500", "ER visit → $250", "Protected!"],
             "right_icon": "💥", "right_label": "WITHOUT",
             "right_items": ["Save $200/mo", "Car wreck → $15,000", "ER visit → $8,500", "Bankrupt 😰"]},
            {"t": "bars", "title": "Annual Cost Comparison", "items": [
                ("Insurance: $2,400/yr", 15, "#4CAF50"),
                ("One ER visit: $8,500", 55, "#FF6B6B"),
                ("Car accident: $15,000", 100, "#D32F2F")]},
            {"t": "lesson", "icon": "🛡️", "text": "Insurance costs monthly — NOT having it costs WAY more when things go wrong!"},
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════
#  HTML/CSS/JS ANIMATION ENGINE
# ═══════════════════════════════════════════════════════════════════════

_BASE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; }
.vc {
    width: 360px; height: 640px;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    color: #fff;
}
.scene {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    padding: 24px 20px;
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}
.scene.active {
    opacity: 1;
    transform: translateY(0);
}
.scene.exit {
    opacity: 0;
    transform: translateY(-30px);
}
/* Title scene */
.sc-title .icon { font-size: 64px; margin-bottom: 12px; animation: iconPulse 2s ease-in-out infinite; }
.sc-title .main-text {
    font-size: 32px; font-weight: 800; text-align: center; line-height: 1.2;
    background: linear-gradient(135deg, #FFD700, #FFA500);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    white-space: pre-line;
}
.sc-title .sub-text {
    font-size: 14px; color: #aaa; margin-top: 8px; text-align: center;
    animation: fadeSlideUp 0.8s ease 0.4s both;
}
@keyframes iconPulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.15)} }
@keyframes fadeSlideUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn { from{opacity:0} to{opacity:1} }
@keyframes slideRight { from{width:0} to{width:var(--tw)} }
@keyframes countUp { from{opacity:0;transform:scale(0.8)} to{opacity:1;transform:scale(1)} }
@keyframes rainFall {
    0% { transform: translateY(-100px) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(700px) rotate(360deg); opacity: 0; }
}
@keyframes growIn { from{transform:scaleY(0);opacity:0} to{transform:scaleY(1);opacity:1} }
@keyframes popIn { 0%{transform:scale(0);opacity:0} 60%{transform:scale(1.1);opacity:1} 100%{transform:scale(1);opacity:1} }
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
@keyframes drawLine { from{stroke-dashoffset:1000} to{stroke-dashoffset:0} }
@keyframes gaugeGrow { from{stroke-dashoffset:var(--circ)} to{stroke-dashoffset:var(--offset)} }

/* Bars */
.bar-container { width: 100%; margin: 6px 0; }
.bar-label { font-size: 12px; color: #ccc; margin-bottom: 3px; }
.bar-outer { width:100%; height:22px; background:rgba(255,255,255,0.1); border-radius:11px; overflow:hidden; }
.bar-inner {
    height: 100%; border-radius: 11px;
    animation: slideRight 1.2s ease-out forwards;
    display:flex; align-items:center; padding-left:8px;
    font-size:11px; font-weight:700; color:#000;
}
/* Stack items */
.stack-item {
    width: 100%; padding: 10px 14px; margin: 5px 0;
    border-radius: 10px; font-size: 13px; font-weight: 600;
    opacity: 0; animation: popIn 0.5s ease forwards;
    border-left: 4px solid;
    background: rgba(255,255,255,0.05);
}
/* Split */
.split-wrap { display:flex; gap:10px; width:100%; }
.split-side {
    flex:1; background:rgba(255,255,255,0.05); border-radius:12px;
    padding:14px 10px; text-align:center;
    opacity:0; animation: fadeSlideUp 0.6s ease forwards;
}
.split-side .s-icon { font-size:36px; margin-bottom:6px; }
.split-side .s-label { font-size:14px; font-weight:800; margin-bottom:8px; letter-spacing:1px; }
.split-side .s-item { font-size:12px; color:#ccc; margin:4px 0; }
/* Counter */
.counter-wrap { text-align:center; }
.counter-label { font-size:13px; color:#aaa; margin-bottom:6px; }
.counter-value {
    font-size:56px; font-weight:900;
    background: linear-gradient(90deg, var(--cc), #fff, var(--cc));
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
}
/* Rain */
.rain-icon {
    position: absolute; font-size: 28px;
    animation: rainFall linear infinite;
    pointer-events: none;
}
.rain-label { position: absolute; bottom: 40px; font-size: 14px; color: #ccc; text-align:center; width:100%; }
/* Lesson */
.sc-lesson {
    background: rgba(0,0,0,0.3); border-radius: 16px;
    padding: 20px; text-align: center; border: 1px solid rgba(255,215,0,0.3);
}
.sc-lesson .l-icon { font-size: 48px; margin-bottom: 10px; }
.sc-lesson .l-text {
    font-size: 16px; line-height: 1.5; font-weight: 600;
    color: #FFD700;
}
/* Progress dots */
.prog-dots {
    position:absolute; bottom:12px; left:0; right:0;
    display:flex; justify-content:center; gap:6px;
}
.prog-dot {
    width:8px; height:8px; border-radius:50%;
    background:rgba(255,255,255,0.2);
    transition: background 0.3s;
}
.prog-dot.active { background:#FFD700; }
/* Pie */
.pie-container { width:160px; height:160px; position:relative; }
/* Chart */
.chart-container { width:100%; height:160px; position:relative; }
.chart-container svg { width:100%; height:100%; }
/* Gauge */
.gauge-container { width:200px; height:120px; position:relative; }
.gauge-label { position:absolute; bottom:-8px; width:100%; text-align:center; font-size:28px; font-weight:900; color:#FFD700; }
/* Branding */
.brand {
    position:absolute; top:12px; left:16px;
    font-size:11px; font-weight:700; color:#FFD700;
    letter-spacing:1px; opacity:0.7;
}
.topic-badge {
    position:absolute; top:12px; right:16px;
    font-size:10px; font-weight:700; color:#000;
    background:#FFD700; padding:2px 8px; border-radius:10px;
}
.replay-btn {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    background:rgba(255,215,0,0.9); color:#000; border:none;
    padding:12px 28px; border-radius:25px; font-size:16px; font-weight:700;
    cursor:pointer; opacity:0; transition:opacity 0.4s;
    z-index:100;
}
.replay-btn.show { opacity:1; }
.replay-btn:hover { background:#FFD700; transform:translate(-50%,-50%) scale(1.05); }
"""

_BASE_JS = """
let scenes, dots, replayBtn, sceneIdx=0, timers=[];
function init(){
    scenes=document.querySelectorAll('.scene');
    dots=document.querySelectorAll('.prog-dot');
    replayBtn=document.getElementById('replay');
    if(replayBtn) replayBtn.addEventListener('click', restart);
    play();
}
function play(){
    timers.forEach(t=>clearTimeout(t));
    timers=[];
    sceneIdx=0;
    showScene(0);
    const durations = JSON.parse(document.getElementById('durations').textContent);
    let delay=0;
    for(let i=0;i<durations.length;i++){
        delay+=durations[i]*1000;
        if(i<durations.length-1){
            ((idx,d)=>{timers.push(setTimeout(()=>showScene(idx+1),d));})(i,delay);
        } else {
            timers.push(setTimeout(()=>{if(replayBtn)replayBtn.classList.add('show');},delay));
        }
    }
}
function showScene(idx){
    sceneIdx=idx;
    scenes.forEach((s,i)=>{
        s.classList.remove('active','exit');
        if(i<idx) s.classList.add('exit');
        else if(i===idx) s.classList.add('active');
    });
    dots.forEach((d,i)=>d.classList.toggle('active',i===idx));
    // Trigger counter animations in active scene
    const active=scenes[idx];
    const cv=active.querySelector('.counter-value');
    if(cv && !cv.dataset.started){
        cv.dataset.started='1';
        animateCounter(cv, parseFloat(cv.dataset.from), parseFloat(cv.dataset.to),
                       cv.dataset.prefix||'', cv.dataset.suffix||'', 2000, cv.dataset.decimals||0);
    }
}
function animateCounter(el, from, to, pfx, sfx, dur, dec){
    const start=performance.now();
    function step(now){
        const p=Math.min((now-start)/dur,1);
        const ease=1-Math.pow(1-p,3); // easeOutCubic
        const val=from+(to-from)*ease;
        el.textContent=pfx+(dec>0?val.toFixed(dec):Math.round(val).toLocaleString())+sfx;
        if(p<1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}
function restart(){
    if(replayBtn)replayBtn.classList.remove('show');
    scenes.forEach(s=>{s.classList.remove('active','exit');s.style.transition='none';});
    // Reset counters
    document.querySelectorAll('.counter-value').forEach(c=>delete c.dataset.started);
    // Reset bar animations
    document.querySelectorAll('.bar-inner').forEach(b=>{b.style.animation='none';b.offsetHeight;b.style.animation='';});
    document.querySelectorAll('.stack-item').forEach(s=>{s.style.animation='none';s.offsetHeight;s.style.animation='';});
    document.querySelectorAll('.split-side').forEach(s=>{s.style.animation='none';s.offsetHeight;s.style.animation='';});
    setTimeout(()=>{scenes.forEach(s=>s.style.transition='');play();},50);
}
window.addEventListener('DOMContentLoaded',init);
"""


def _render_title_scene(scene: dict) -> str:
    """Render a title scene."""
    text = scene.get("text", "")
    sub = scene.get("sub", "")
    icon = scene.get("icon", "")
    return f"""
    <div class="sc-title" style="display:flex;flex-direction:column;align-items:center;">
        <div class="icon">{icon}</div>
        <div class="main-text">{text}</div>
        <div class="sub-text">{sub}</div>
    </div>"""


def _render_counter_scene(scene: dict) -> str:
    """Render an animated counter scene."""
    label = scene.get("label", "")
    start = scene.get("start", 0)
    end = scene.get("end", 100)
    prefix = scene.get("prefix", "")
    suffix = scene.get("suffix", "")
    color = scene.get("color", "#FFD700")
    dec = scene.get("decimals", 0)
    return f"""
    <div class="counter-wrap" style="--cc:{color}">
        <div class="counter-label">{label}</div>
        <div class="counter-value" data-from="{start}" data-to="{end}"
             data-prefix="{prefix}" data-suffix="{suffix}" data-decimals="{dec}">{prefix}{start}{suffix}</div>
    </div>"""


def _render_bars_scene(scene: dict) -> str:
    """Render animated horizontal bar chart."""
    title = scene.get("title", "")
    items = scene.get("items", [])
    html = f'<div style="width:100%;"><div style="font-size:15px;font-weight:700;margin-bottom:10px;text-align:center;">{title}</div>'
    for i, (label, pct, color) in enumerate(items):
        delay = 0.2 + i * 0.3
        html += f"""
        <div class="bar-container" style="animation:fadeIn 0.4s ease {delay}s both;">
            <div class="bar-label">{label}</div>
            <div class="bar-outer">
                <div class="bar-inner" style="--tw:{pct}%;background:{color};animation-delay:{delay}s;"></div>
            </div>
        </div>"""
    html += "</div>"
    return html


def _render_stack_scene(scene: dict) -> str:
    """Render items appearing one by one."""
    title = scene.get("title", "")
    items = scene.get("items", [])
    html = f'<div style="width:100%;"><div style="font-size:15px;font-weight:700;margin-bottom:10px;text-align:center;">{title}</div>'
    for i, (text, color) in enumerate(items):
        delay = 0.2 + i * 0.35
        html += f"""
        <div class="stack-item" style="border-color:{color};animation-delay:{delay}s;
             background:linear-gradient(90deg,{color}15,transparent);">
            {text}
        </div>"""
    html += "</div>"
    return html


def _render_split_scene(scene: dict) -> str:
    """Render a two-side comparison."""
    left_icon = scene.get("left_icon", "")
    left_label = scene.get("left_label", "A")
    left_items = scene.get("left_items", [])
    right_icon = scene.get("right_icon", "")
    right_label = scene.get("right_label", "B")
    right_items = scene.get("right_items", [])

    def side_html(icon, label, items, delay, color):
        items_html = "".join(f'<div class="s-item">{it}</div>' for it in items)
        return f"""
        <div class="split-side" style="animation-delay:{delay}s;border:1px solid {color}33;">
            <div class="s-icon">{icon}</div>
            <div class="s-label" style="color:{color}">{label}</div>
            {items_html}
        </div>"""

    return f"""
    <div class="split-wrap">
        {side_html(left_icon, left_label, left_items, 0.2, "#4CAF50")}
        {side_html(right_icon, right_label, right_items, 0.5, "#FF6B6B")}
    </div>"""


def _render_rain_scene(scene: dict) -> str:
    """Render emoji falling from the sky."""
    icons = scene.get("icons", ["💰"])
    label = scene.get("label", "")
    html = ""
    import random
    random.seed(42)  # deterministic for caching
    for i in range(15):
        icon = icons[i % len(icons)]
        left = random.randint(5, 90)
        dur = random.uniform(2, 4)
        delay = random.uniform(0, 3)
        size = random.randint(20, 40)
        html += f'<div class="rain-icon" style="left:{left}%;font-size:{size}px;animation-duration:{dur}s;animation-delay:{delay}s;">{icon}</div>'
    if label:
        html += f'<div class="rain-label">{label}</div>'
    return html


def _render_lesson_scene(scene: dict) -> str:
    """Render the final lesson/takeaway."""
    icon = scene.get("icon", "🌟")
    text = scene.get("text", "")
    return f"""
    <div class="sc-lesson" style="animation:fadeIn 0.8s ease both;">
        <div class="l-icon" style="animation:iconPulse 1.5s ease-in-out infinite;">{icon}</div>
        <div class="l-text">{text}</div>
    </div>"""


def _render_pie_scene(scene: dict) -> str:
    """Render an animated SVG pie chart."""
    title = scene.get("title", "")
    slices = scene.get("slices", [])
    radius = 70
    cx, cy = 80, 80
    total = sum(pct for _, pct, _ in slices)

    html = f'<div style="text-align:center;width:100%;"><div style="font-size:15px;font-weight:700;margin-bottom:8px;">{title}</div>'
    html += f'<svg width="160" height="160" viewBox="0 0 160 160" style="margin:0 auto;display:block;">'

    start_angle = -90
    for i, (label, pct, color) in enumerate(slices):
        angle = (pct / total) * 360
        end_angle = start_angle + angle
        large = 1 if angle > 180 else 0
        import math
        x1 = cx + radius * math.cos(math.radians(start_angle))
        y1 = cy + radius * math.sin(math.radians(start_angle))
        x2 = cx + radius * math.cos(math.radians(end_angle))
        y2 = cy + radius * math.sin(math.radians(end_angle))
        delay = 0.3 + i * 0.3
        html += f"""
        <path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{radius},{radius} 0 {large},1 {x2:.1f},{y2:.1f} Z"
              fill="{color}" opacity="0" style="animation:fadeIn 0.5s ease {delay}s forwards;">
            <title>{label}: {pct}%</title>
        </path>"""
        # Label
        mid_angle = start_angle + angle / 2
        lx = cx + (radius * 0.6) * math.cos(math.radians(mid_angle))
        ly = cy + (radius * 0.6) * math.sin(math.radians(mid_angle))
        html += f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="9" fill="#fff" font-weight="700" opacity="0" style="animation:fadeIn 0.4s ease {delay+0.3}s forwards;">{pct}%</text>'
        start_angle = end_angle

    html += "</svg>"
    # Legend
    html += '<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:8px;">'
    for label, pct, color in slices:
        html += f'<div style="font-size:10px;color:#ccc;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin-right:4px;"></span>{label}</div>'
    html += "</div></div>"
    return html


def _render_chart_scene(scene: dict) -> str:
    """Render an animated line chart (stock market style)."""
    title = scene.get("title", "")
    points = scene.get("points", [])
    if not points:
        return ""

    w, h = 300, 140
    pad = 15
    max_val = max(points)
    min_val = min(points)
    rng = max_val - min_val or 1
    n = len(points)
    step_x = (w - 2 * pad) / max(1, n - 1)

    coords = []
    for i, v in enumerate(points):
        x = pad + i * step_x
        y = h - pad - ((v - min_val) / rng) * (h - 2 * pad)
        coords.append(f"{x:.1f},{y:.1f}")

    polyline = " ".join(coords)
    path_len = 1000  # approximation for dasharray

    # Gradient fill path
    fill_coords = f"{pad},{h - pad} " + polyline + f" {pad + (n-1)*step_x},{h-pad}"

    html = f"""
    <div style="width:100%;text-align:center;">
        <div style="font-size:15px;font-weight:700;margin-bottom:8px;">{title}</div>
        <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;margin:0 auto;">
            <defs>
                <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#4CAF50" stop-opacity="0.4"/>
                    <stop offset="100%" stop-color="#4CAF50" stop-opacity="0"/>
                </linearGradient>
            </defs>
            <polygon points="{fill_coords}" fill="url(#cg)" opacity="0" style="animation:fadeIn 1s ease 0.5s forwards;"/>
            <polyline points="{polyline}" fill="none" stroke="#4CAF50" stroke-width="2.5"
                      stroke-dasharray="{path_len}" stroke-dashoffset="{path_len}"
                      style="animation:drawLine 2.5s ease forwards;" stroke-linejoin="round"/>
            <!-- End dot -->
            <circle cx="{coords[-1].split(',')[0]}" cy="{coords[-1].split(',')[1]}" r="4" fill="#FFD700" opacity="0"
                    style="animation:popIn 0.4s ease 2.5s forwards;"/>
            <!-- Trend arrow -->
            <text x="{w-pad}" y="{pad+10}" text-anchor="end" font-size="18" fill="#4CAF50" opacity="0"
                  style="animation:fadeIn 0.5s ease 2.5s forwards;">📈</text>
        </svg>
    </div>"""
    return html


def _render_gauge_scene(scene: dict) -> str:
    """Render an animated gauge/speedometer."""
    label = scene.get("label", "")
    value = scene.get("value", 750)
    min_v = scene.get("min", 300)
    max_v = scene.get("max", 850)
    zones = scene.get("zones", [])

    # Semi-circle gauge
    r = 80
    cx, cy = 100, 95
    circumference = 3.14159 * r  # half circle
    pct = (value - min_v) / (max_v - min_v)
    offset = circumference * (1 - pct)

    # Determine color
    color = "#FFD700"
    for zname, zmax, zcolor in zones:
        if value <= zmax:
            color = zcolor
            break

    html = f"""
    <div style="text-align:center;width:100%;">
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">{label}</div>
        <svg width="200" height="120" viewBox="0 0 200 120" style="display:block;margin:0 auto;">
            <path d="M 20 95 A {r} {r} 0 0 1 180 95" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="14" stroke-linecap="round"/>
            <path d="M 20 95 A {r} {r} 0 0 1 180 95" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"
                  stroke-dasharray="{circumference}" stroke-dashoffset="{circumference}"
                  style="--circ:{circumference};--offset:{offset};animation:gaugeGrow 2s ease forwards;"/>"""
    # Zone labels
    for i, (zname, zmax, zcolor) in enumerate(zones):
        zp = (zmax - min_v) / (max_v - min_v)
        import math
        angle = 180 * (1 - zp)
        tx = cx + (r + 16) * math.cos(math.radians(angle))
        ty = cy - (r + 16) * math.sin(math.radians(angle))
        html += f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="middle" font-size="7" fill="{zcolor}">{zname}</text>'

    html += f"""
            <text x="100" y="95" text-anchor="middle" font-size="32" font-weight="900" fill="{color}"
                  opacity="0" style="animation:fadeIn 0.5s ease 1.5s forwards;">{value}</text>
        </svg>
    </div>"""
    return html


# Scene renderer dispatch
_RENDERERS = {
    "title": _render_title_scene,
    "counter": _render_counter_scene,
    "bars": _render_bars_scene,
    "stack": _render_stack_scene,
    "split": _render_split_scene,
    "rain": _render_rain_scene,
    "lesson": _render_lesson_scene,
    "pie": _render_pie_scene,
    "chart": _render_chart_scene,
    "gauge": _render_gauge_scene,
}


def render_animated_short(key: str) -> Optional[str]:
    """Render a complete animated HTML5 short for the given key.

    Returns self-contained HTML string, or None if key not found.
    Embed in Streamlit with: st.components.v1.html(html, height=680)
    """
    lesson = ANIMATED_SHORTS.get(key)
    if not lesson:
        return None

    scenes = lesson.get("scenes", [])
    bg = lesson.get("bg", "linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)")
    title = lesson.get("title", "")
    topic = lesson.get("topic", "")
    audience = lesson.get("audience", "")

    # Default duration per scene type
    default_dur = {"title": 3, "counter": 4, "bars": 4, "stack": 4,
                   "split": 5, "rain": 4, "lesson": 5, "pie": 5, "chart": 5, "gauge": 5}
    durations = [s.get("duration", default_dur.get(s["t"], 4)) for s in scenes]

    # Build scene HTML
    scenes_html = ""
    for i, scene in enumerate(scenes):
        renderer = _RENDERERS.get(scene["t"])
        if not renderer:
            continue
        inner = renderer(scene)
        scenes_html += f'<div class="scene" data-idx="{i}">{inner}</div>\n'

    # Progress dots
    dots_html = "".join(f'<div class="prog-dot"></div>' for _ in scenes)

    aud_label = {"kids": "Elementary", "middle": "Middle School", "high": "High School"}.get(audience, audience.title())

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{_BASE_CSS}</style></head>
<body>
<div class="vc" style="background:{bg};">
    <div class="brand">AGENT RICHY</div>
    <div class="topic-badge">{aud_label} • {topic.title()}</div>
    {scenes_html}
    <div class="prog-dots">{dots_html}</div>
    <button id="replay" class="replay-btn">▶ Replay</button>
</div>
<script id="durations" type="application/json">{durations}</script>
<script>{_BASE_JS}</script>
</body></html>"""


def get_all_animated_shorts() -> Dict[str, dict]:
    """Return complete dict of animated short metadata."""
    return {k: {"title": v["title"], "audience": v["audience"], "topic": v["topic"]}
            for k, v in ANIMATED_SHORTS.items()}


def get_shorts_for_audience(audience: str) -> List[str]:
    """Return list of keys for a given audience (inclusive — kids ⊂ middle ⊂ high)."""
    include = {"kids": ["kids"], "middle": ["kids", "middle"],
               "high": ["kids", "middle", "high"], "adult": ["kids", "middle", "high"]}
    allowed = include.get(audience, ["kids", "middle", "high"])
    return [k for k, v in ANIMATED_SHORTS.items() if v["audience"] in allowed]
