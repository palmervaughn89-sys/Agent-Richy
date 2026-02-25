"""Youth financial education module for Agent Richy.

Targets middle school (grades 6-8) and high school (grades 9-12) students
with real-world examples for earning, budgeting, saving, investing,
talent discovery, side-hustle building, breaking bad spending habits,
and AI-generated educational video lessons via CogVideoX.
"""

import math
from typing import Optional, List
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
    filter_investments,
)
from agent_richy.utils.video_generator import (
    is_video_generation_available,
    list_videos_for_audience,
    generate_video,
    generate_custom_video,
    show_lesson_without_video,
)

# ---------------------------------------------------------------------------
# Talent categories & monetization paths
# ---------------------------------------------------------------------------

TALENT_CATEGORIES = {
    "creative": {
        "label": "Creative / Artistic",
        "examples": ["drawing", "painting", "photography", "music", "singing",
                      "writing", "poetry", "filmmaking", "animation", "crafts"],
        "monetize_middle": [
            ("Sell art/crafts on Etsy or local markets",
             "Custom portraits, stickers, bookmarks, jewelry.  Start-up < $20.  "
             "Price items 3-5x material cost.  A $2 bookmark sells for $8-$10."),
            ("Offer art lessons to younger kids",
             "Charge $10-15/hr to teach drawing or painting in your neighborhood.  "
             "Parents love structured activities for their kids."),
            ("Create and sell digital art",
             "Design phone wallpapers, social-media templates, or printables.  "
             "Sell on Gumroad or Redbubble for passive income."),
        ],
        "monetize_high": [
            ("Freelance graphic design",
             "Learn Canva / Figma (free).  Offer logos, social posts, flyers "
             "on Fiverr ($15-$100/project).  Build a portfolio on Instagram."),
            ("YouTube / TikTok content creation",
             "Art tutorials, music covers, or creative vlogs.  Consistency > perfection.  "
             "Monetize via AdSense (1 K subs), sponsorships, or merch."),
            ("Photography / videography services",
             "Shoot events, senior portraits, product photos.  Charge $50-$200/session.  "
             "Start with your phone camera — modern phones are powerful."),
            ("Commission-based art",
             "Pet portraits, fan art, custom illustrations.  Market on Reddit, "
             "Twitter/X, Instagram.  $25-$200+ per piece."),
            ("Music production / beat selling",
             "Use free DAWs (GarageBand, LMMS).  Sell beats on BeatStars.  "
             "Producers earn $20-$500+ per beat license."),
        ],
    },
    "tech": {
        "label": "Tech / Digital",
        "examples": ["coding", "gaming", "building PCs", "web design",
                      "robotics", "3-D printing", "app ideas", "AI tools"],
        "monetize_middle": [
            ("Help neighbors with tech",
             "Set up Wi-Fi, fix printers, teach seniors smartphones.  $10-$20/hr.  "
             "This builds amazing people skills too."),
            ("Start a tech-review channel",
             "Review gadgets, apps, or games on YouTube.  Even simple screen recordings "
             "with commentary can get views.  Start building your audience now."),
            ("Build simple websites",
             "Learn basic HTML / CSS (freeCodeCamp).  Offer to build sites for local "
             "businesses or family friends for $50-$100."),
        ],
        "monetize_high": [
            ("Freelance web development",
             "HTML / CSS / JS → React.  Build sites for small businesses $200-$2,000.  "
             "Use GitHub to showcase projects.  Upwork / Fiverr for first clients."),
            ("App or game development",
             "Learn Python, Swift, or Unity.  Publish to App Store / Google Play.  "
             "Even simple utility apps can earn ad revenue."),
            ("Tech tutoring / course creation",
             "Teach coding, Photoshop, or video editing.  $20-$50/hr on Wyzant "
             "or create Udemy courses for passive income."),
            ("PC building / repair service",
             "Build custom PCs for gamers ($50-$150 labor fee).  "
             "Repair/upgrade laptops for classmates and neighbors."),
            ("AI / automation freelancing",
             "Learn to use AI tools (ChatGPT, Midjourney).  Help businesses automate "
             "social media, write content, or create images.  The future is NOW."),
        ],
    },
    "athletic": {
        "label": "Athletic / Sports",
        "examples": ["basketball", "soccer", "swimming", "dance", "martial arts",
                      "skateboarding", "fitness", "running", "gymnastics"],
        "monetize_middle": [
            ("Coach younger kids",
             "Help with drills at local parks.  $10-$15/hr.  Parents always need "
             "constructive activities for their children."),
            ("Referee or scorekeeper",
             "Local youth leagues pay $15-$30/game for refs.  Contact your city's "
             "parks and rec department."),
            ("Fitness challenge videos",
             "Film workout routines or sport tricks for TikTok / YouTube.  "
             "Build an audience now — monetize later with brand deals."),
        ],
        "monetize_high": [
            ("Personal training / coaching",
             "Get CPR certified ($30-$50).  Offer training sessions $20-$40/hr.  "
             "Specialize in a sport you excel at."),
            ("Sports content creation",
             "Highlights, tutorials, training vlogs.  Monetize through YouTube, "
             "brand sponsorships (athletic wear), or Patreon."),
            ("Referee / umpire (certified)",
             "Get certified through your state's athletic association.  "
             "Earn $25-$50/game for high-school level.  Great weekend income."),
            ("Camp counselor / sports instructor",
             "Summer camps pay $10-$18/hr.  Looks great on college apps AND "
             "builds leadership skills."),
        ],
    },
    "social": {
        "label": "Social / People Person",
        "examples": ["talking to people", "organizing events", "leadership",
                      "helping others", "public speaking", "teaching"],
        "monetize_middle": [
            ("Babysitting / pet sitting",
             "Red Cross babysitting course ($35) → charge $12-$20/hr.  "
             "Pet sitting $25-$50/day.  Build a client list through trust."),
            ("Party / event helper",
             "Help set up birthday parties, clean up events.  $10-$15/hr.  "
             "Great way to build a network and get referrals."),
            ("Tutoring",
             "Help classmates or younger students.  $10-$20/hr.  "
             "Your school may even have a paid tutoring program."),
        ],
        "monetize_high": [
            ("Social-media management",
             "Manage Instagram / TikTok for small businesses.  $100-$500/month per "
             "client.  Learn scheduling tools (Buffer, Later).  Build a case study."),
            ("Event-planning assistant",
             "Help with weddings, parties, corporate events.  $12-$20/hr.  "
             "Connect with local event planners for gig work."),
            ("Sales / retail (part-time)",
             "Commission-based sales teach negotiation and hustle.  "
             "Top teen sales people in retail earn $500-$1,200/month."),
            ("Tutoring / test prep",
             "SAT / ACT prep commands $25-$50/hr.  Start with Wyzant or Varsity "
             "Tutors.  Your high scores are your résumé."),
            ("Start a small service business",
             "Cleaning, organizing, errand running.  Charge $15-$25/hr.  "
             "Use Nextdoor or flyers to find clients.  Scale with friends."),
        ],
    },
    "hands_on": {
        "label": "Hands-On / Builder",
        "examples": ["fixing things", "woodworking", "cooking", "gardening",
                      "sewing", "mechanics", "electronics", "building stuff"],
        "monetize_middle": [
            ("Lawn care / yard work",
             "Mowing, weeding, leaf raking.  $20-$40/yard.  "
             "In summer earn $200-$600/month on weekends alone."),
            ("Baking / cooking for sale",
             "Cookies, brownies, cupcakes for neighbors.  Check local cottage-food "
             "laws.  A batch of cookies (~$5 to make) sells for $15-$20."),
            ("Small repair services",
             "Fix bikes, skateboards, or simple household items.  $5-$15 per fix.  "
             "YouTube teaches you everything you need to know."),
        ],
        "monetize_high": [
            ("Car washing / detailing",
             "Basic wash $20-$30, full detail $75-$150.  Start with a bucket, soap, "
             "microfiber cloths (~$30 startup).  VERY scalable."),
            ("Landscaping / power washing",
             "Rent or buy a power washer ($150-$300).  Charge $75-$200 per driveway.  "
             "Spring and fall are peak seasons."),
            ("Custom woodworking / crafts",
             "Cutting boards, shelves, phone stands.  Sell on Etsy or at farmers' "
             "markets.  $30-$200+ per piece.  Material cost is low."),
            ("Cooking / catering",
             "Meal-prep services for busy families.  $100-$300/week per family.  "
             "Check your state's cottage-food license requirements."),
            ("Mechanical work",
             "Oil changes, tire rotations, basic maintenance.  $20-$50 per service.  "
             "Learn from YouTube, practice on family cars first."),
        ],
    },
}

EARNING_IDEAS = {
    "middle": [
        ("Lawn mowing / yard work",
         "Charge $20-$40 per yard.  In a summer month you could earn $200-$600 "
         "just on weekends.  Track your clients in a simple notebook."),
        ("Pet sitting / dog walking",
         "Apps like Rover or flyers in your neighborhood.  $15-$25 per walk, "
         "$25-$50 per day of pet sitting."),
        ("Tutoring younger kids",
         "Help kids in your neighborhood with reading or math for $10-$20/hr.  "
         "Your school or library may post tutoring requests."),
        ("Selling crafts or art online",
         "Use Etsy to sell handmade items.  Start-up cost is minimal; "
         "focus on a niche like custom bookmarks or stickers."),
        ("Helping with tech for neighbors",
         "Set up Wi-Fi, teach seniors to use smartphones, or fix basic "
         "computer issues.  Charge $10-$20/hour."),
    ],
    "high": [
        ("Part-time job (retail / food service)",
         "Federal minimum wage is $7.25/hr; many states pay $12-$15+.  "
         "Work 10-15 hrs/week = $500-$900/month.  Build résumé skills too."),
        ("Freelance graphic design / video editing",
         "Learn free tools (Canva, DaVinci Resolve).  Sell services on Fiverr "
         "starting at $5-$50 per project.  Build a portfolio on Instagram."),
        ("Social-media content creation",
         "YouTube AdSense, TikTok Creator Fund, or brand sponsorships.  "
         "Pick a niche you love — consistency is more important than perfection."),
        ("Online reselling (sneakers, vintage clothes)",
         "Buy low on Facebook Marketplace or thrift stores, sell higher on "
         "eBay or StockX.  Study what's trending to maximize margins."),
        ("Car washing / detailing",
         "Start with a bucket, soap, and microfiber cloths.  Charge $20-$30 "
         "for a basic wash, $75-$150 for a full detail.  Very scalable."),
        ("Tutoring in school subjects",
         "High-school subjects like Calculus, Chemistry, and SAT prep command "
         "$25-$50/hr.  Market yourself through school counselors or Wyzant."),
    ],
}

INVESTING_INTRO = {
    "middle": (
        "Investing 101 for Middle Schoolers\n"
        "------------------------------------\n"
        "Think of investing like planting a seed.  You put in a little money now,\n"
        "and over time it GROWS — even while you sleep!\n\n"
        "Key ideas to know:\n"
        "1. COMPOUND INTEREST: Earn interest on top of interest.  $100 at 8 %/year\n"
        "   becomes $215 in 10 years — without adding a single dollar!\n"
        "2. INDEX FUNDS: Instead of picking one company, you buy a tiny piece of\n"
        "   HUNDREDS of companies at once.  Less risky, less stressful.\n"
        "3. START EARLY: The earlier you invest, the more time your money has to\n"
        "   grow.  Even $25/month starting at age 12 can become thousands by 18!\n\n"
        "Great first step: Ask a parent about opening a custodial account (like\n"
        "a Fidelity Youth Account or Greenlight) so you can start learning with\n"
        "real money in a safe environment."
    ),
    "high": (
        "Investing 101 for High Schoolers\n"
        "-----------------------------------\n"
        "You already know the basics — now let's level up.\n\n"
        "Key vehicles to understand:\n"
        "1. STOCKS: Ownership in a company.  Higher potential reward, higher risk.\n"
        "   Study a company before buying.  Look at revenue growth, not just hype.\n"
        "2. ETFs / INDEX FUNDS: Diversified baskets of stocks or bonds.  SPY (S&P 500)\n"
        "   has averaged ~10 %/year historically.  Great for long-term holding.\n"
        "3. ROTH IRA: If you have earned income (job), you can contribute up to\n"
        "   $7,000/year.  That money grows TAX-FREE.  This is the #1 wealth-building\n"
        "   tool available to teenagers with jobs!\n"
        "4. DOLLAR-COST AVERAGING (DCA): Invest a fixed amount every month\n"
        "   regardless of price.  Removes emotion from investing.\n\n"
        "Action step: Open a Roth IRA through Fidelity or Schwab (parent co-signer\n"
        "needed under 18).  Start with as little as $1 in an S&P 500 index fund."
    ),
}

BAD_SPENDING_HABITS_YOUTH = [
    ("Impulse buying (buying stuff you don't need on the spot)",
     "The 48-hour rule: Wait 48 hours before any non-essential purchase.  "
     "You'll find 70 % of the time you don't actually want it anymore."),
    ("Spending ALL your money (never saving anything)",
     "Pay yourself FIRST.  As soon as you get money, put 20 % in savings "
     "BEFORE spending anything.  Automate it if possible."),
    ("Buying things to impress friends",
     "Real wealth is invisible.  The richest people you know probably "
     "don't wear designer everything.  Invest in yourself, not appearances."),
    ("Eating out / ordering food constantly",
     "Track how much you spend on food for a week — it'll shock you.  "
     "Pack lunches, cook simple meals.  Save $100-$300/month easily."),
    ("In-app purchases / gaming micro-transactions",
     "Set a strict monthly 'fun money' limit ($10-$20).  Once it's gone, "
     "it's gone.  Those $0.99 purchases add up to hundreds per year."),
    ("Not tracking where money goes",
     "Download a free budget app or use Notes on your phone.  Track "
     "EVERY dollar for 30 days.  Awareness is the first step to control."),
    ("Lending money you can't afford to lose",
     "It's okay to say no.  If you lend money, consider it a gift.  "
     "Never lend what you need for your own bills or savings."),
]

SAVINGS_CHALLENGES = [
    {
        "name": "52-Week Savings Challenge",
        "desc": (
            "Week 1 → save $1.  Week 2 → save $2 … Week 52 → save $52.  "
            "Total at the end: $1,378!"
        ),
        "total": 1378.0,
    },
    {
        "name": "100-Envelope Challenge (student edition)",
        "desc": (
            "Label 20 envelopes $1-$20.  Each week pick one randomly, "
            "put that amount in savings.  After 20 weeks: $210 saved!"
        ),
        "total": 210.0,
    },
    {
        "name": "No-Spend Weekend Challenge",
        "desc": (
            "Pick one weekend/month: zero non-essential spending.  "
            "Find free activities (parks, home movie night, cooking).  "
            "Save what you would've spent."
        ),
        "total": 0,
    },
    {
        "name": "Round-Up Savings",
        "desc": (
            "Every purchase, round up to the nearest dollar and save the "
            "difference.  Buy something for $3.40 → save $0.60.  "
            "Average savings: $30-$50/month on autopilot."
        ),
        "total": 0,
    },
]

# ===================================================================
# Module class
# ===================================================================


class YouthModule:
    """Interactive financial education for middle- and high-school students."""

    def __init__(self, profile: UserProfile, llm_client=None):
        self.profile = profile
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------

    def run(self) -> None:
        print_header(f"Welcome, {self.profile.name}!  I'm Agent Richy 💰")
        print(wrap_text(
            "I'm here to help you start your financial journey.  "
            "Whether it's discovering your talents, earning your first dollar, "
            "budgeting like a pro, or learning to invest — I've got you covered.  "
            "Let's build your future! 🚀"
        ))

        if not self.profile.completed_assessment:
            do_assess = parse_yes_no(prompt(
                "Want to do a quick intro so I can give you personalized advice? (yes/no):"
            ))
            if do_assess:
                self._onboarding_assessment()

        while True:
            print_divider()
            level_label = (self.profile.grade_level or "student").title()
            print(f"\n🏠 MAIN MENU — {level_label} Level")
            print("   1. 🌟 Discover & monetize your talents")
            print("   2. 💼 Ways to earn money")
            print("   3. 🔨 Side-hustle builder")
            print("   4. 📊 Budget workshop")
            print("   5. 🏦 Savings challenges")
            print("   6. 📈 Investing basics")
            print("   7. 🚫 Bad spending-habits quiz")
            print("   8. 🎓 Real-world money scenarios")
            print("   9. 🎬 Video lessons (AI-generated)")
            print("  10. 🤖 Ask Richy anything")
            print("  11. 📋 My financial snapshot")
            print("  12. Exit")
            choice = prompt("Choose an option (1-12):").strip()

            actions = {
                "1": self._talent_discovery,
                "2": self._earning_ideas,
                "3": self._side_hustle_builder,
                "4": self._budgeting_workshop,
                "5": self._savings_challenges,
                "6": self._investing_intro,
                "7": self._bad_habits_quiz,
                "8": self._real_world_scenarios,
                "9": self._video_lessons,
                "10": self._free_question,
                "11": self._financial_snapshot,
            }
            if choice == "12":
                print("\nKeep grinding and keep learning.  Your future self will thank you! 🚀")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Please enter a number between 1 and 12.")

    # ------------------------------------------------------------------
    # Onboarding
    # ------------------------------------------------------------------

    def _onboarding_assessment(self) -> None:
        print_header("Let's Get to Know You! 🎤")

        name = prompt("What's your name?:")
        if name:
            self.profile.name = name

        age_str = prompt("How old are you?:")
        age = parse_number(age_str)
        if age:
            self.profile.age = int(age)
            self.profile.grade_level = "middle" if age <= 14 else "high"

        print(wrap_text(
            "\nEveryone has talents — things they're naturally good at or love doing.  "
            "Let me help you figure out what yours are!"
        ))
        talent_cats = list(TALENT_CATEGORIES.keys())
        talent_labels = [
            TALENT_CATEGORIES[k]["label"] + " — " +
            ", ".join(TALENT_CATEGORIES[k]["examples"][:4])
            for k in talent_cats
        ]
        chosen = choose_many("Which of these sound like you? (pick all that apply):", talent_labels)
        for idx in chosen:
            self.profile.talents.append(talent_cats[idx])

        interests_raw = prompt("List specific skills or hobbies you're proud of (comma-separated):")
        if interests_raw:
            self.profile.interests = [s.strip() for s in interests_raw.split(",") if s.strip()]

        has_job = parse_yes_no(prompt("Do you currently have a job or regular income? (yes/no):"))
        if has_job:
            self.profile.has_job = True
            self.profile.job_description = prompt("What do you do?:")
            self.profile.hourly_rate = parse_number(prompt("How much per hour?:")) or 0.0
            self.profile.weekly_hours = parse_number(prompt("Hours per week?:")) or 0.0
        else:
            self.profile.allowance = parse_number(
                prompt("Do you get an allowance?  How much/month? ($0 if none):")
            ) or 0.0

        self.profile.completed_assessment = True
        monthly = self.profile.youth_monthly_income()

        print_header("Assessment Complete! 🎯")
        print(f"  Name:            {self.profile.name}")
        print(f"  Age:             {self.profile.age}")
        print(f"  Level:           {self.profile.grade_level}")
        print(f"  Talents:         {', '.join(self.profile.talents) or 'TBD'}")
        print(f"  Interests:       {', '.join(self.profile.interests) or 'TBD'}")
        print(f"  Has Job:         {'Yes — ' + self.profile.job_description if self.profile.has_job else 'Not yet'}")
        print(f"  Est. Monthly $:  {format_currency(monthly)}")
        print_divider()

        if monthly == 0:
            print(wrap_text(
                "\nNo income yet?  That's totally fine — that's exactly what we're "
                "here to fix!  Let's explore your talents and find ways to earn. 💪"
            ))
        else:
            print(wrap_text(
                f"\nYou're already earning {format_currency(monthly)}/month — "
                "let's make sure you keep and grow as much of it as possible!"
            ))

    # ------------------------------------------------------------------
    # 1 — Talent discovery & monetization
    # ------------------------------------------------------------------

    def _talent_discovery(self) -> None:
        print_header("Discover & Monetize Your Talents 🌟")

        if not self.profile.talents:
            print(wrap_text(
                "Let's figure out your talents first!  Everyone is good at something — "
                "and I bet you're good at MORE than you think."
            ))
            talent_cats = list(TALENT_CATEGORIES.keys())
            labels = [
                TALENT_CATEGORIES[k]["label"] + " — " +
                ", ".join(TALENT_CATEGORIES[k]["examples"][:4])
                for k in talent_cats
            ]
            chosen = choose_many("Which of these sound like you?:", labels)
            for idx in chosen:
                self.profile.talents.append(talent_cats[idx])

        if not self.profile.talents:
            # LLM-powered discovery
            print(wrap_text(
                "\nNo worries — let me ask a few questions to uncover your hidden strengths."
            ))
            questions = [
                "What do you do for fun when you have free time?",
                "What subject in school do you enjoy the most?",
                "If you could teach someone something, what would it be?",
                "What do your friends or family say you're good at?",
            ]
            answers = [prompt(q + ":") for q in questions]

            resp = ask_llm(
                self.llm_client,
                system_prompt=(
                    "You are Agent Richy, a career / talent coach for teens.  Based on "
                    "the student's answers, identify 2-3 talent categories from: creative, "
                    "tech, athletic, social, hands_on.  Explain how each connects.  "
                    "Be enthusiastic and specific.  Under 150 words."
                ),
                user_message="\n".join(f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)),
            )
            if resp:
                print(f"\n🤖 Richy says:\n{wrap_text(resp)}")
            else:
                print(wrap_text(
                    "\nBased on what you've told me, you've got tons of potential!  "
                    "Try exploring the Creative and Social categories — most people "
                    "who enjoy spending time with friends or creating things thrive there."
                ))
            return

        level = self.profile.grade_level or "high"
        key = f"monetize_{level}"
        for talent in self.profile.talents:
            cat = TALENT_CATEGORIES.get(talent)
            if not cat:
                continue
            ideas = cat.get(key, cat.get("monetize_high", []))
            print(f"\n🔥 Monetizing Your {cat['label']} Talent:")
            print_divider()
            for i, (title, detail) in enumerate(ideas, 1):
                print(f"\n  {i}. {title}")
                print(f"     {wrap_text(detail)}")

        if self.profile.interests:
            resp = ask_llm(
                self.llm_client,
                system_prompt=(
                    "You are Agent Richy, a teen career coach.  The student has talents: "
                    f"{', '.join(self.profile.talents)} and interests: "
                    f"{', '.join(self.profile.interests)}.  "
                    "Give 3 SPECIFIC creative ways they can monetize their unique "
                    "combination.  Include estimated earnings.  Under 200 words."
                ),
                user_message=f"Age: {self.profile.age}, Grade: {self.profile.grade_level}",
            )
            if resp:
                print(f"\n🤖 Richy's Personalized Ideas:\n{wrap_text(resp)}")

        print_tip(
            "The #1 thing that separates earners from dreamers? Taking action.  "
            "Pick ONE idea above and start THIS WEEK."
        )

    # ------------------------------------------------------------------
    # 2 — Ways to earn money
    # ------------------------------------------------------------------

    def _earning_ideas(self) -> None:
        print_header("Ways to Earn Money 💼")
        level = self.profile.grade_level or "high"
        ideas = EARNING_IDEAS.get(level, EARNING_IDEAS["high"])

        for i, (title, _) in enumerate(ideas, 1):
            print(f"  {i}. {title}")

        choice = prompt("Pick a number to learn more, or Enter to go back:").strip()
        if not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(ideas)):
            return

        title, detail = ideas[idx]
        print(f"\n📌 {title}")
        print_divider()
        print(wrap_text(detail))

        print("\n💵 Let's estimate what you could earn:")
        hrs = parse_number(prompt("How many hours/week could you do this?:")) or 5.0
        rate = parse_number(prompt("Estimated hourly rate? ($):")) or 12.0
        weekly = hrs * rate
        monthly = weekly * 4.33
        yearly = monthly * 12
        print(f"\n  Weekly:  {format_currency(weekly)}")
        print(f"  Monthly: {format_currency(monthly)}")
        print(f"  Yearly:  {format_currency(yearly)}")
        print(f"  If you save 30 %: {format_currency(yearly * 0.30)}/year in savings!")

        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy, an enthusiastic financial coach for students.  "
                "Give a motivating tip (2-3 sentences) about this earning opportunity.  "
                "Include a specific first step they should take TODAY."
            ),
            user_message=f"Earning idea: {title}\nDetail: {detail}",
        )
        if resp:
            print(f"\n💡 Richy's Tip: {resp}")

    # ------------------------------------------------------------------
    # 3 — Side-hustle builder
    # ------------------------------------------------------------------

    def _side_hustle_builder(self) -> None:
        print_header("Side-Hustle Builder 🔨")
        print(wrap_text(
            "Let's build a real side-hustle plan — step by step.  "
            "This isn't just about earning money; it's about building skills "
            "that will pay you for the REST of your life."
        ))

        hustle_types = [
            "Service-based (mowing, tutoring, dog walking)",
            "Product-based (crafts, baked goods, reselling)",
            "Digital / online (content creation, freelancing, digital products)",
            "Skill-based (teaching, coaching, consulting)",
        ]
        idx = choose_one("Step 1 — What type of hustle interests you?", hustle_types)
        if idx is None:
            return
        hustle_key = ["service", "product", "digital", "skill"][idx]
        budget = parse_number(prompt("Step 2 — How much can you invest to start? (even $0 is fine!):")) or 0.0
        hours = parse_number(prompt("Step 3 — Hours/week you can dedicate?:")) or 5.0

        plans = {
            "service": {
                "ideas": [
                    "Lawn care / cleaning — $0 startup if you use family equipment",
                    "Babysitting — get Red Cross certified ($35), charge $15-$20/hr",
                    "Grocery delivery / errands — gas money only, $10-$20 per run",
                ],
                "steps": [
                    "Make a Canva flyer (free) with services & prices",
                    "Post on Nextdoor, neighborhood Facebook groups, bulletin boards",
                    "Tell 10 people you know — word of mouth is #1",
                    "Set up Venmo/Cash App for payments",
                    "Track every dollar in a spreadsheet",
                ],
            },
            "product": {
                "ideas": [
                    "Baked goods — $10-$20 startup → sell for $15-$25/batch",
                    "Thrift-store flipping — buy $5-$20, sell 3-5x on eBay",
                    "Handmade crafts — jewelry, stickers, candles ($10-$30 materials)",
                ],
                "steps": [
                    "Research what sells (Etsy bestsellers, eBay completed listings)",
                    "Make 3-5 samples and photograph them well (natural lighting!)",
                    "List on Etsy ($0.20/listing) or Facebook Marketplace (free)",
                    "Price at MINIMUM 3x material cost — your time has value!",
                    "Reinvest first profits into more inventory",
                ],
            },
            "digital": {
                "ideas": [
                    "TikTok / YouTube content — $0 startup, use your phone",
                    "Canva design services — free tool, charge $15-$50/design",
                    "Social-media management — $0 startup, $100-$500/month/client",
                ],
                "steps": [
                    "Pick ONE platform (TikTok for quick growth, YouTube for long-term)",
                    "Post consistently — 3-5 times/week minimum",
                    "Study your niche (TikTok Creative Center is free research)",
                    "Build a portfolio of 5-10 samples before approaching clients",
                    "Use free tools: Canva, CapCut, DaVinci Resolve, Audacity",
                ],
            },
            "skill": {
                "ideas": [
                    "Tutoring — $0 startup, $15-$50/hr depending on subject",
                    "Music lessons — $0 if you own an instrument, $20-$40/hr",
                    "Sports coaching — $0, charge $15-$30/hr private lessons",
                ],
                "steps": [
                    "List your top 3 skills others struggle with",
                    "Create a simple lesson plan or teaching outline",
                    "Offer 2-3 FREE sessions to build testimonials",
                    "Post on Wyzant, Tutor.com, or community boards",
                    "Ask satisfied clients for reviews and referrals",
                ],
            },
        }
        plan = plans[hustle_key]

        print_header("Your Custom Side-Hustle Plan 📝")
        print("🎯 Low-budget ideas:")
        for idea in plan["ideas"]:
            print(f"  • {idea}")
        print(f"\n📅 Your {int(hours)}-hr/week action plan:")
        for i, step in enumerate(plan["steps"], 1):
            print(f"  Week {i}: {step}")

        conservative = hours * 10
        moderate = hours * 18
        ambitious = hours * 30
        print("\n💵 Income Projection:")
        print(f"  Conservative: {format_currency(conservative)}/wk = {format_currency(conservative * 4.33)}/mo")
        print(f"  Moderate:     {format_currency(moderate)}/wk = {format_currency(moderate * 4.33)}/mo")
        print(f"  Ambitious:    {format_currency(ambitious)}/wk = {format_currency(ambitious * 4.33)}/mo")

        if self.profile.talents or self.profile.interests:
            resp = ask_llm(
                self.llm_client,
                system_prompt=(
                    "You are Agent Richy, a teen business coach.  Create a week-by-week "
                    f"4-week launch plan for a {hustle_key}-based hustle.  Budget: "
                    f"${budget:.0f}, {hours:.0f} hrs/week.  Talents: "
                    f"{', '.join(self.profile.talents or ['general'])}.  Interests: "
                    f"{', '.join(self.profile.interests or ['general'])}.  "
                    "Be specific with dollar amounts.  Under 200 words."
                ),
                user_message=f"Grade: {self.profile.grade_level}, Age: {self.profile.age}",
            )
            if resp:
                print(f"\n🤖 Richy's 4-Week Launch Plan:\n{wrap_text(resp)}")

        self.profile.side_hustles.append(hustle_key)
        print_tip(
            "The hardest part is starting.  Don't wait for perfect — start messy, "
            "learn fast, and improve.  Take ONE action today! ⚡"
        )

    # ------------------------------------------------------------------
    # 4 — Budget workshop
    # ------------------------------------------------------------------

    def _budgeting_workshop(self) -> None:
        print_header("Budget Workshop 📊")
        income = self.profile.youth_monthly_income()
        if income == 0:
            income = parse_number(prompt(
                "How much money do you earn or receive per month? ($0 if none):"
            )) or 0.0
        if income == 0:
            print(wrap_text(
                "\nNo income yet?  That's okay!  Let's use $200/month as an example."
            ))
            income = 200.0
        else:
            print(f"\nYour estimated monthly income: {format_currency(income)}")

        categories = [
            "school supplies / fees", "phone bill", "food / eating out",
            "entertainment (movies, games)", "clothing",
            "transportation (bus, gas)", "subscriptions (streaming, apps)",
            "gifts / social spending",
        ]
        expenses = {}
        print("\nEnter monthly expenses ($0 if you don't have that expense):\n")
        for cat in categories:
            expenses[cat] = parse_number(prompt(f"  {cat}:")) or 0.0

        total_exp = sum(expenses.values())
        savings = income - total_exp
        savings_pct = (savings / income * 100) if income else 0

        print("\n" + "=" * 60)
        print("  YOUR MONTHLY BUDGET SNAPSHOT")
        print("=" * 60)
        print(f"  Income:          {format_currency(income)}")
        for cat, val in expenses.items():
            if val > 0:
                print(f"  {cat.title()[:25]:<27} {format_currency(val):>10}  ({val/income*100:.0f}%)")
        print_divider()
        print(f"  Total Expenses:  {format_currency(total_exp)}")
        print(f"  Left to Save:    {format_currency(savings)}")
        print(f"  Savings Goal (20 %): {progress_bar(max(0, savings), income * 0.20)}")
        print("=" * 60)

        if savings < 0:
            print_warning("You're spending more than you earn!")
            top = sorted(expenses.items(), key=lambda x: x[1], reverse=True)
            if top and top[0][1] > 0:
                print(f"  Biggest expense: {top[0][0].title()} — {format_currency(top[0][1])}")
                print(f"  Cut by 25 % → save {format_currency(top[0][1] * 0.25)}/month")
        elif savings_pct < 10:
            print(wrap_text(
                f"\nYou're saving {savings_pct:.1f} % — aim for at least 20 %.  "
                "Trim variable expenses where you can."
            ))
        else:
            print_success(f"Great job!  Saving {savings_pct:.1f} % of income!")

        if savings > 0:
            print(f"\n  • In 6 months: {format_currency(savings * 6)}")
            print(f"  • In 1 year:   {format_currency(savings * 12)}")
            balance = 0.0
            mr = 0.08 / 12
            for _ in range(120):
                balance = balance * (1 + mr) + savings
            print(f"  • In 10 yrs (8 % return): {format_currency(balance)}")

        resp = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are Agent Richy, a teen finance coach.  Analyze this budget, "
                "give 3 specific tips.  Be encouraging.  Under 150 words."
            ),
            user_message=f"Income: {income}, Expenses: {expenses}, Savings: {savings}",
        )
        if resp:
            print(f"\n🤖 Richy's Budget Tips:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 5 — Savings challenges
    # ------------------------------------------------------------------

    def _savings_challenges(self) -> None:
        print_header("Savings Challenges 🏦")
        for i, ch in enumerate(SAVINGS_CHALLENGES, 1):
            print(f"\n  {i}. {ch['name']}")
            print(f"     {wrap_text(ch['desc'])}")
            if ch["total"] > 0:
                print(f"     Total saved: {format_currency(ch['total'])}")

        choice = prompt("Want to start one?  Pick a number (or Enter to skip):").strip()
        if not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(SAVINGS_CHALLENGES)):
            return

        ch = SAVINGS_CHALLENGES[idx]
        print_header(f"Starting: {ch['name']} 🎯")
        print(wrap_text(ch["desc"]))

        if "52" in ch["name"]:
            print(f"\n  {'Week':<8} {'Save':>8} {'Cumulative':>12}")
            print(f"  {'-'*8} {'-'*8} {'-'*12}")
            cum = 0.0
            for w in range(1, 53):
                cum += w
                if w <= 12 or w % 4 == 0 or w >= 49:
                    print(f"  {w:<8} {format_currency(w):>8} {format_currency(cum):>12}")
                elif w == 13:
                    print(f"  {'...':<8}")

        print_tip("Set a weekly phone reminder.  Consistency beats everything.  You've GOT this!")

    # ------------------------------------------------------------------
    # 6 — Investing basics
    # ------------------------------------------------------------------

    def _investing_intro(self) -> None:
        level = self.profile.grade_level or "high"
        print_header("Investing Basics 📈")
        print(INVESTING_INTRO.get(level, INVESTING_INTRO["high"]))

        amount = parse_number(prompt("How much could you save per month? (e.g. 50):")) or 50.0
        annual = (parse_number(prompt("Expected annual return? (8 = market avg, 5 = safe):")) or 8.0) / 100

        print_divider()
        print(f"If you invest {format_currency(amount)}/mo at {annual*100:.0f} %:\n")
        balance = 0.0
        mr = annual / 12
        print(f"  {'Year':<8} {'Balance':>12} {'Contributed':>12} {'Interest':>14}")
        print(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*14}")
        for yr in range(1, 21):
            for _ in range(12):
                balance = balance * (1 + mr) + amount
            contrib = amount * 12 * yr
            interest = balance - contrib
            if yr <= 10 or yr % 5 == 0:
                print(f"  {yr:<8} {format_currency(balance):>12} "
                      f"{format_currency(contrib):>12} {format_currency(interest):>14}")

        total_in = amount * 240
        print(wrap_text(
            f"\nAfter 20 yrs of {format_currency(amount)}/mo you'd have ~"
            f"{format_currency(balance)} — you only put in {format_currency(total_in)}.  "
            f"That's {format_currency(balance - total_in)} in FREE MONEY!"
        ))

        if level == "high":
            print_header("Beginner Investment Options 🔍")
            picks = filter_investments(risk="medium", asset_type="etfs")
            for inv in (picks or [])[:4]:
                print(f"  • {inv['ticker']} — {inv['name']}")
                print(f"    {inv['description']}")
                print(f"    Risk: {inv['risk']}  |  Dividend: {inv['dividend_yield']} %\n")
            print_tip("Start with broad index funds (SPY, QQQ).  "
                      "Don't pick individual stocks until you've studied for 6+ months.")

    # ------------------------------------------------------------------
    # 7 — Bad habits quiz
    # ------------------------------------------------------------------

    def _bad_habits_quiz(self) -> None:
        print_header("Bad Spending-Habits Check 🚫")
        print(wrap_text(
            "Let's see if any sneaky habits are eating your money.  "
            "Be honest — no judgment.  Awareness is step 1!"
        ))

        score = 0
        identified = []
        for i, (habit, fix) in enumerate(BAD_SPENDING_HABITS_YOUTH, 1):
            ans = parse_yes_no(prompt(f"{i}. {habit}\n   Is this you? (yes/no):"))
            if ans:
                score += 1
                identified.append((habit, fix))
                print(f"   ✏️  Fix: {wrap_text(fix)}")
            else:
                print("   ✅ Great — keep it up!")

        total = len(BAD_SPENDING_HABITS_YOUTH)
        print_header("Your Results 📊")
        print(f"  Bad habits found: {score}/{total}")
        print(f"  Financial health: {progress_bar(total - score, total)}")

        if score == 0:
            print_success("ZERO bad habits — you're ahead of most adults!")
        elif score <= 2:
            print(wrap_text(
                "\nNot bad!  Focus on fixing ONE habit at a time.  "
                "It takes ~30 days to break a habit."
            ))
        elif score <= 4:
            print(wrap_text(
                "\nSome work to do — but recognizing them is HUGE.  "
                "Tackle the costliest habit first."
            ))
        else:
            print(wrap_text(
                "\nSerious work ahead — but that's WHY you're here!  "
                "You're young and every habit is fixable."
            ))
            print("\n🎯 Top 3 priorities:")
            for i, (h, f) in enumerate(identified[:3], 1):
                print(f"  {i}. {h.split('(')[0].strip()}\n     Fix: {f}")

        self.profile.bad_habits = [h.split("(")[0].strip() for h, _ in identified]

        if identified:
            resp = ask_llm(
                self.llm_client,
                system_prompt=(
                    "You are Agent Richy.  The student's bad habits: "
                    f"{', '.join(self.profile.bad_habits)}.  "
                    "Create a 30-day challenge to fix their worst habit.  "
                    "Include daily/weekly actions.  Under 150 words."
                ),
                user_message=f"Age: {self.profile.age}, Grade: {self.profile.grade_level}",
            )
            if resp:
                print(f"\n🤖 Richy's 30-Day Challenge:\n{wrap_text(resp)}")

    # ------------------------------------------------------------------
    # 8 — Real-world money scenarios
    # ------------------------------------------------------------------

    def _real_world_scenarios(self) -> None:
        print_header("Real-World Money Scenarios 🎓")
        level = self.profile.grade_level or "high"

        scenarios = {
            "middle": [
                {
                    "title": "The Birthday Money Dilemma",
                    "setup": (
                        "You got $200 for your birthday.  Friends want you to buy the "
                        "new video game ($70).  You also want new shoes ($120).  "
                        "Your savings account has $50."
                    ),
                    "options": [
                        "Buy game AND shoes ($190 spent)",
                        "Buy the game, save the rest ($130 saved)",
                        "Buy the shoes, save the rest ($80 saved)",
                        "Save all $200",
                    ],
                    "analysis": [
                        "Fun but only $10 left.  No emergency fund.",
                        "Social fun + $130 saved.  Good balance.",
                        "Shoes last longer than a game.  $80 saved.",
                        "Max savings — but missing fun is okay sometimes.",
                    ],
                    "best": 1,
                    "lesson": "The 'best' answer is making a CONSCIOUS choice, not impulse buying.",
                },
                {
                    "title": "The First Paycheck",
                    "setup": (
                        "You earned $150 mowing lawns.  Promised a friend you'd go to "
                        "movies ($25).  Phone screen cracked (repair $80).  "
                        "Also saving for a $300 bike."
                    ),
                    "options": [
                        "Movies + phone repair ($105 spent, $45 saved)",
                        "Phone repair + save rest ($80 spent, $70 toward bike)",
                        "Movies + save toward bike ($25 spent, $125 saved)",
                        "Save everything ($150 toward bike)",
                    ],
                    "analysis": [
                        "Fix a need + keep a promise.  Solid choice.",
                        "Prioritize need + goal.  Very disciplined.",
                        "Keep promise but cracked phone hurts side-hustle photos.",
                        "Max savings but breaking a promise isn't ideal.",
                    ],
                    "best": 0,
                    "lesson": "Needs first, then commitments, then savings.  That's budgeting.",
                },
            ],
            "high": [
                {
                    "title": "The Part-Time Job Decision",
                    "setup": (
                        "Two offers:\n"
                        "  A: Fast food — $14/hr, 20 hrs/wk, flexible\n"
                        "  B: Social-media intern — $10/hr, 15 hrs/wk, résumé builder\n"
                        "You need $800/month for expenses."
                    ),
                    "options": [
                        "Job A — more money ($1,213/mo)",
                        "Job B — career skills ($650/mo)",
                        "Ask Job B for more hours",
                        "Take both if schedules allow",
                    ],
                    "analysis": [
                        "Meets needs + surplus.  But limited growth.",
                        "Great future value but doesn't cover expenses.",
                        "Smart negotiation!  Skills + enough money.",
                        "Maximum income + growth if you can handle it.",
                    ],
                    "best": 2,
                    "lesson": "Always negotiate.  Choose skill-building over pure hourly pay.",
                },
                {
                    "title": "The $1,000 Investment Choice",
                    "setup": (
                        "You saved $1,000 from your summer job.  No debt.  Options:\n"
                        "  A: Savings account (4.5 % APY)\n"
                        "  B: S&P 500 index fund (~10 %/yr historical)\n"
                        "  C: Crypto (could 2x or lose 50 %)\n"
                        "  D: Laptop for your side hustle"
                    ),
                    "options": ["Savings account", "S&P 500 index fund", "Crypto", "Laptop"],
                    "analysis": [
                        "Safe, guaranteed.  Good for < 2-year goals.",
                        "Best for long-term (5+ yrs).  #1 wealth builder.",
                        "Very high risk.  Only invest what you can lose.",
                        "If the laptop earns MORE money, it's an investment in YOU.",
                    ],
                    "best": 1,
                    "lesson": "Index funds beat almost everything long-term.  "
                              "But investing in yourself has the highest ROI.",
                },
            ],
        }

        available = scenarios.get(level, scenarios["high"])
        for i, s in enumerate(available, 1):
            print(f"  {i}. {s['title']}")
        idx_str = prompt("Pick a scenario:")
        if not idx_str.isdigit():
            return
        idx = int(idx_str) - 1
        if not (0 <= idx < len(available)):
            return

        s = available[idx]
        print_header(s["title"])
        print(wrap_text(s["setup"]))
        for i, opt in enumerate(s["options"], 1):
            print(f"  {i}. {opt}")
        pick_str = prompt("What would you choose?:")
        if pick_str.isdigit():
            pick = int(pick_str) - 1
            if 0 <= pick < len(s["options"]):
                print(f"\n📊 Analysis: {wrap_text(s['analysis'][pick])}")
                if pick == s["best"]:
                    print_success("That's the pro move! 🎯")
                else:
                    print(f"\n  💡 Pro pick: Option {s['best']+1} ({s['options'][s['best']]})")
                print(f"\n📚 Lesson: {wrap_text(s['lesson'])}")

    # ------------------------------------------------------------------
    # 9 — AI-generated video lessons (CogVideoX)
    # ------------------------------------------------------------------

    def _video_lessons(self) -> None:
        print_header("Video Lessons 🎬 — Powered by CogVideoX AI")

        audience = self.profile.grade_level or "high"
        videos = list_videos_for_audience(audience)

        if not videos:
            print("No video lessons available for your level.")
            return

        can_generate = is_video_generation_available()
        if can_generate:
            print(wrap_text(
                "CogVideoX is available!  I can generate short AI videos that teach "
                "financial concepts in a fun, visual way.  Each video comes with a "
                "lesson you can learn from."
            ))
        else:
            print(wrap_text(
                "Video generation requires a GPU + the 'diffusers' library.  "
                "For now I'll show you the visual story-board and lesson for each topic.  "
                "Install with:  pip install diffusers torch accelerate"
            ))

        # Group by topic for nicer display
        by_topic = {}
        for v in videos:
            by_topic.setdefault(v["topic"], []).append(v)

        print("\nAvailable lessons:\n")
        flat = []
        num = 1
        for topic, items in by_topic.items():
            print(f"  📂 {topic.upper()}")
            for v in items:
                print(f"     {num}. {v['title']}")
                flat.append(v)
                num += 1

        print(f"\n  {num}. ✨ Create a CUSTOM video lesson")

        choice = prompt("Pick a number (or Enter to go back):").strip()
        if not choice.isdigit():
            return
        pick = int(choice) - 1

        # Custom video
        if pick == len(flat):
            self._custom_video_lesson(can_generate)
            return

        if not (0 <= pick < len(flat)):
            return

        v = flat[pick]
        print_header(f"🎬 {v['title']}")
        print(f"  Topic:    {v['topic'].title()}")
        print(f"  Audience: {v['audience'].title()}")

        if can_generate:
            go = parse_yes_no(prompt("Generate the video? (yes/no):"))
            if go:
                path = generate_video(v["key"])
                if path:
                    print_success(f"Video saved to: {path}")
            else:
                show_lesson_without_video(v["key"])
        else:
            show_lesson_without_video(v["key"])

        print(f"\n📚 Key Lesson: {v['lesson']}")

        # Follow-up quiz
        print_divider()
        print("Quick check — did you get the lesson?")
        answer = prompt(f"In your own words, what does '{v['topic']}' mean?:")
        if answer:
            resp = ask_llm(
                self.llm_client,
                system_prompt=(
                    "You are Agent Richy.  A student just watched a lesson on "
                    f"'{v['topic']}' ({v['title']}).  The key lesson was: {v['lesson']}  "
                    "The student's answer is below.  Evaluate whether they understood, "
                    "give encouraging feedback, and add one extra tip.  Under 100 words."
                ),
                user_message=answer,
            )
            if resp:
                print(f"\n🤖 Richy says: {wrap_text(resp)}")
            else:
                print_success("Great effort!  The more you learn, the richer you get (in every way)!")

    def _custom_video_lesson(self, can_generate: bool) -> None:
        """Let the student describe a financial topic and generate a custom video."""
        print_header("Create Your Own Video Lesson ✨")
        print(wrap_text(
            "Describe a financial concept you'd like to see as a short animated video.  "
            "I'll craft a visual prompt and (if CogVideoX is available) generate it!"
        ))

        topic = prompt("What financial topic should the video teach?:")
        if not topic:
            return

        # Use LLM to craft a CogVideoX-friendly prompt
        llm_prompt = ask_llm(
            self.llm_client,
            system_prompt=(
                "You are an expert at writing text-to-video prompts for CogVideoX.  "
                "The user wants an educational video about a financial topic for young "
                "students.  Write a vivid, detailed visual description in 2-3 sentences.  "
                "Use colorful, animated, Pixar-style imagery.  Include camera direction.  "
                "Do NOT include text overlays, only describe visual action."
            ),
            user_message=f"Financial topic: {topic}",
        )

        if llm_prompt:
            print(f"\n🎨 Video description:\n{wrap_text(llm_prompt)}")
            if can_generate:
                go = parse_yes_no(prompt("Generate this video? (yes/no):"))
                if go:
                    safe_name = topic.lower().replace(" ", "_")[:30]
                    path = generate_custom_video(llm_prompt, filename=f"custom_{safe_name}")
                    if path:
                        print_success(f"Video saved to: {path}")
            else:
                print(wrap_text(
                    "\n(Video generation unavailable — but imagine this playing as a "
                    "short animated clip!  Install CogVideoX to generate for real.)"
                ))
        else:
            print(wrap_text(
                f"\nPicture this: a colorful animated scene that teaches about "
                f"'{topic}' using fun characters and real-world examples.  "
                "When CogVideoX and the LLM are both available, I can create "
                "this for you automatically!"
            ))

    # ------------------------------------------------------------------
    # 10 — Ask Richy anything
    # ------------------------------------------------------------------

    def _free_question(self) -> None:
        print_header("Ask Richy Anything 🤖")
        question = prompt("What financial question is on your mind?:")
        if not question:
            return

        ctx = [f"Student: {self.profile.name}"]
        if self.profile.age:
            ctx.append(f"Age: {self.profile.age}")
        if self.profile.grade_level:
            ctx.append(f"Grade: {self.profile.grade_level}")
        if self.profile.talents:
            ctx.append(f"Talents: {', '.join(self.profile.talents)}")
        if self.profile.interests:
            ctx.append(f"Interests: {', '.join(self.profile.interests)}")
        income = self.profile.youth_monthly_income()
        if income > 0:
            ctx.append(f"Monthly income: {format_currency(income)}")
        if self.profile.bad_habits:
            ctx.append(f"Working on: {', '.join(self.profile.bad_habits)}")

        system = (
            "You are Agent Richy, a friendly, motivating financial coach for teens.  "
            "Give practical, real-world advice with numbers and action steps.  "
            "Keep under 200 words.  Context:\n" + "\n".join(ctx)
        )
        resp = ask_llm(self.llm_client, system, question)
        if resp:
            print(f"\n💬 Richy says:\n{wrap_text(resp)}")
        else:
            print(wrap_text(
                "\nQuick tip: track every dollar for 30 days.  Awareness is step 1.  "
                "Step 2: pay yourself first — save BEFORE you spend.  "
                "Even $10/week = $520/year!"
            ))

        if parse_yes_no(prompt("Another question? (yes/no):") or "no"):
            self._free_question()

    # ------------------------------------------------------------------
    # 11 — Financial snapshot
    # ------------------------------------------------------------------

    def _financial_snapshot(self) -> None:
        print_header(f"{self.profile.name}'s Financial Snapshot 📋")
        income = self.profile.youth_monthly_income()

        print(f"  Name:             {self.profile.name}")
        print(f"  Age:              {self.profile.age or 'Not set'}")
        print(f"  Grade Level:      {self.profile.grade_level or 'Not set'}")
        print(f"  Talents:          {', '.join(self.profile.talents) or 'Not discovered yet'}")
        print(f"  Interests:        {', '.join(self.profile.interests) or 'Not set'}")
        print_divider()
        if self.profile.has_job:
            print(f"  Job:              {self.profile.job_description}")
            print(f"  Rate / Hours:     {format_currency(self.profile.hourly_rate)}/hr × {self.profile.weekly_hours} hrs/wk")
        if self.profile.allowance > 0:
            print(f"  Allowance:        {format_currency(self.profile.allowance)}/mo")
        print(f"  Est. Monthly $:   {format_currency(income)}")
        print(f"  Est. Yearly $:    {format_currency(income * 12)}")
        if self.profile.side_hustles:
            print(f"  Side Hustles:     {', '.join(self.profile.side_hustles)}")
        if self.profile.bad_habits:
            print(f"  Working On:       {', '.join(self.profile.bad_habits)}")
        print_divider()

        if income > 0:
            save = income * 0.20
            print(f"\n  💰 If you save 20 %/month ({format_currency(save)}):")
            print(f"     1 year:   {format_currency(save * 12)}")
            balance = 0.0
            mr = 0.08 / 12
            for _ in range(120):
                balance = balance * (1 + mr) + save
            print(f"     10 yrs (8 % return): {format_currency(balance)}")
        else:
            print("\n  No income yet — try 'Discover Your Talents' or 'Ways to Earn'!")
