"""Video lesson data for Agent Richy's Money School.

Each module contains lessons with video URLs, quizzes, and metadata.
To add real videos: replace PLACEHOLDER_URL_X values with YouTube or MP4 URLs.
Set video_type to "youtube" for YouTube links or "mp4" for direct file links.
"""

# ── Badge definitions ────────────────────────────────────────────────────
MODULE_BADGES = {
    "mod_1": {"name": "Money Master", "icon": "💰"},
    "mod_2": {"name": "Super Saver", "icon": "🐷"},
    "mod_3": {"name": "Growth Guru", "icon": "🌱"},
    "mod_4": {"name": "Money Genius", "icon": "🧠"},
}
MEGA_BADGE = {"name": "Financial Superstar", "icon": "🏆"}

# ── Video modules & lessons ─────────────────────────────────────────────
VIDEO_MODULES = [
    {
        "module_id": "mod_1",
        "title": "What is Money?",
        "description": "Learn what money is, where it comes from, and why we use it!",
        "icon": "💰",
        "age_range": "5-10",
        "show_filename": "show_001_where_did_money_come_from.mp4",
        "lessons": [
            {
                "lesson_id": "mod1_les1",
                "title": "The Story of Money",
                "description": "From trading seashells to dollar bills — how money was invented!",
                "video_url": "PLACEHOLDER_URL_1",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",            # "youtube" or "mp4"
                "video_filename": "lesson_mod1_01_the_story_of_money.mp4",
                "duration_seconds": 120,
                "thumbnail_emoji": "🏛️",
                "quiz": [
                    {
                        "question": "What did people use before money was invented?",
                        "options": ["Credit cards", "They traded things they had", "Nothing", "Coins"],
                        "correct_index": 1,
                        "explanation": "Before money, people would trade things they had (like food or tools) for things they needed. This is called bartering!"
                    },
                    {
                        "question": "Why do we use money instead of trading?",
                        "options": ["Because it's shiny", "It's easier to carry and everyone agrees on its value", "Because the government says so", "We don't use money"],
                        "correct_index": 1,
                        "explanation": "Money makes trading easier because everyone agrees on what it's worth. Imagine trying to trade a cow for a haircut!"
                    }
                ]
            },
            {
                "lesson_id": "mod1_les2",
                "title": "Coins and Bills — Know Your Money",
                "description": "Learn about all the different coins and bills and what they're worth!",
                "video_url": "PLACEHOLDER_URL_2",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod1_02_coins_and_bills.mp4",
                "duration_seconds": 90,
                "thumbnail_emoji": "🪙",
                "quiz": [
                    {
                        "question": "How many pennies make one dollar?",
                        "options": ["10", "50", "100", "25"],
                        "correct_index": 2,
                        "explanation": "There are 100 pennies in one dollar! Each penny is worth 1 cent."
                    }
                ]
            },
            {
                "lesson_id": "mod1_les3",
                "title": "Earning Money",
                "description": "How do people earn money? From lemonade stands to real jobs!",
                "video_url": "PLACEHOLDER_URL_3",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod1_03_earning_money.mp4",
                "duration_seconds": 110,
                "thumbnail_emoji": "🍋",
                "quiz": [
                    {
                        "question": "Which of these is a way kids can earn money?",
                        "options": ["Doing chores", "Helping neighbors", "Selling lemonade", "All of the above!"],
                        "correct_index": 3,
                        "explanation": "All of these are great ways for kids to earn money! When you work hard and help others, you can earn money for it."
                    }
                ]
            }
        ]
    },
    {
        "module_id": "mod_2",
        "title": "Saving & Spending Wisely",
        "description": "Learn the difference between needs and wants, and how to save like a pro!",
        "icon": "🐷",
        "age_range": "5-10",
        "show_filename": "show_002_the_super_saver_challenge.mp4",
        "lessons": [
            {
                "lesson_id": "mod2_les1",
                "title": "Needs vs Wants",
                "description": "Is ice cream a need or a want? Let's figure it out!",
                "video_url": "PLACEHOLDER_URL_4",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod2_01_needs_vs_wants.mp4",
                "duration_seconds": 100,
                "thumbnail_emoji": "🤔",
                "quiz": [
                    {
                        "question": "Which of these is a NEED?",
                        "options": ["A new toy", "Food and water", "A video game", "Candy"],
                        "correct_index": 1,
                        "explanation": "Food and water are things we need to survive! Toys and games are wants — nice to have but not necessary."
                    }
                ]
            },
            {
                "lesson_id": "mod2_les2",
                "title": "The Magic of Saving",
                "description": "Why putting money aside today makes tomorrow even better!",
                "video_url": "PLACEHOLDER_URL_5",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod2_02_the_magic_of_saving.mp4",
                "duration_seconds": 120,
                "thumbnail_emoji": "✨",
                "quiz": [
                    {
                        "question": "If you save $1 every week, how much will you have in 10 weeks?",
                        "options": ["$1", "$5", "$10", "$100"],
                        "correct_index": 2,
                        "explanation": "$1 x 10 weeks = $10! Saving a little bit regularly adds up over time. That's the magic of saving!"
                    }
                ]
            },
            {
                "lesson_id": "mod2_les3",
                "title": "Setting a Savings Goal",
                "description": "Pick something you want and make a plan to save for it!",
                "video_url": "PLACEHOLDER_URL_6",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod2_03_setting_a_savings_goal.mp4",
                "duration_seconds": 100,
                "thumbnail_emoji": "🎯",
                "quiz": [
                    {
                        "question": "What's the FIRST step to saving for something you want?",
                        "options": ["Ask your parents to buy it", "Figure out how much it costs", "Give up", "Spend all your money now"],
                        "correct_index": 1,
                        "explanation": "The first step is knowing how much your goal costs. Then you can make a plan for how long it will take to save up!"
                    }
                ]
            }
        ]
    },
    {
        "module_id": "mod_3",
        "title": "Growing Your Money",
        "description": "Discover how money can grow all by itself — like planting a money tree!",
        "icon": "🌱",
        "age_range": "8-12",
        "show_filename": "show_003_the_magic_money_tree.mp4",
        "lessons": [
            {
                "lesson_id": "mod3_les1",
                "title": "What is a Bank?",
                "description": "Where does your money go when you put it in a bank?",
                "video_url": "PLACEHOLDER_URL_7",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod3_01_what_is_a_bank.mp4",
                "duration_seconds": 110,
                "thumbnail_emoji": "🏦",
                "quiz": [
                    {
                        "question": "What happens to your money when you put it in a bank?",
                        "options": ["It disappears", "The bank keeps it safe and it can earn interest", "Someone else spends it", "Nothing"],
                        "correct_index": 1,
                        "explanation": "Banks keep your money safe AND pay you a little extra called interest. It's like a thank you for letting them hold your money!"
                    }
                ]
            },
            {
                "lesson_id": "mod3_les2",
                "title": "The Money Tree — What is Interest?",
                "description": "How your money grows a little bit every day, just like a plant!",
                "video_url": "PLACEHOLDER_URL_8",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod3_02_the_money_tree.mp4",
                "duration_seconds": 130,
                "thumbnail_emoji": "🌳",
                "quiz": [
                    {
                        "question": "If you put $100 in a bank and earn 5% interest in a year, how much do you have?",
                        "options": ["$100", "$105", "$150", "$200"],
                        "correct_index": 1,
                        "explanation": "$100 + 5% = $105! Your money grew by $5 just by sitting in the bank. The longer you leave it, the more it grows!"
                    }
                ]
            },
            {
                "lesson_id": "mod3_les3",
                "title": "What is Investing?",
                "description": "How grown-ups use money to make even MORE money!",
                "video_url": "PLACEHOLDER_URL_9",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod3_03_what_is_investing.mp4",
                "duration_seconds": 140,
                "thumbnail_emoji": "📈",
                "quiz": [
                    {
                        "question": "What does it mean to invest?",
                        "options": ["Spending all your money", "Using money to try to make more money over time", "Hiding money under your bed", "Giving money away"],
                        "correct_index": 1,
                        "explanation": "Investing means putting your money into something (like a company or a savings account) that you hope will grow and give you more money back over time!"
                    }
                ]
            }
        ]
    },
    {
        "module_id": "mod_4",
        "title": "Smart Money Habits",
        "description": "Build habits that will make you great with money for your whole life!",
        "icon": "🧠",
        "age_range": "8-12",
        "show_filename": "show_004_agent_richys_money_rules.mp4",
        "lessons": [
            {
                "lesson_id": "mod4_les1",
                "title": "The 3 Jars: Save, Spend, Share",
                "description": "A simple system that makes managing money easy and fun!",
                "video_url": "PLACEHOLDER_URL_10",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod4_01_the_three_jars.mp4",
                "duration_seconds": 120,
                "thumbnail_emoji": "🫙",
                "quiz": [
                    {
                        "question": "In the 3-jar system, what are the three jars for?",
                        "options": ["Breakfast, lunch, dinner", "Save, Spend, Share", "Me, myself, and I", "Today, tomorrow, next week"],
                        "correct_index": 1,
                        "explanation": "The 3 jars help you split your money: one jar for saving, one for spending on things you need or want, and one for sharing with others!"
                    }
                ]
            },
            {
                "lesson_id": "mod4_les2",
                "title": "Being a Smart Shopper",
                "description": "How to spot good deals and avoid spending traps!",
                "video_url": "PLACEHOLDER_URL_11",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod4_02_being_a_smart_shopper.mp4",
                "duration_seconds": 110,
                "thumbnail_emoji": "🛒",
                "quiz": [
                    {
                        "question": "You really want a toy that costs $20, but you only have $15. What should you do?",
                        "options": ["Take it anyway", "Save up the extra $5 first", "Borrow money and never pay it back", "Cry until someone buys it"],
                        "correct_index": 1,
                        "explanation": "The smart move is to save up until you have enough! Patience is a superpower when it comes to money."
                    }
                ]
            },
            {
                "lesson_id": "mod4_les3",
                "title": "Giving Back — Why Sharing Matters",
                "description": "How using your money to help others makes the world better!",
                "video_url": "PLACEHOLDER_URL_12",  # ← Replace with real YouTube/MP4 URL
                "video_type": "youtube",
                "video_filename": "lesson_mod4_03_giving_back.mp4",
                "duration_seconds": 100,
                "thumbnail_emoji": "❤️",
                "quiz": [
                    {
                        "question": "Why is it good to share some of your money with others?",
                        "options": ["It's not good", "It helps people who need it and makes your community stronger", "Because you have to", "So people like you"],
                        "correct_index": 1,
                        "explanation": "Sharing helps people who need it and makes our communities stronger. Plus, it feels really good to help others!"
                    }
                ]
            }
        ]
    }
]


def get_all_lesson_ids() -> list[str]:
    """Return a flat list of every lesson_id across all modules."""
    return [
        lesson["lesson_id"]
        for module in VIDEO_MODULES
        for lesson in module["lessons"]
    ]


def get_total_lessons() -> int:
    """Return the total number of lessons across all modules."""
    return sum(len(m["lessons"]) for m in VIDEO_MODULES)


def get_module_by_id(module_id: str) -> dict | None:
    """Look up a module by its module_id."""
    for m in VIDEO_MODULES:
        if m["module_id"] == module_id:
            return m
    return None


def get_lesson_by_id(lesson_id: str) -> tuple[dict | None, dict | None]:
    """Look up a lesson by its lesson_id. Returns (module, lesson) or (None, None)."""
    for m in VIDEO_MODULES:
        for les in m["lessons"]:
            if les["lesson_id"] == lesson_id:
                return m, les
    return None, None


def format_duration(seconds: int) -> str:
    """Convert seconds to a human-friendly string like '2:00'."""
    mins, secs = divmod(seconds, 60)
    return f"{mins}:{secs:02d}"
