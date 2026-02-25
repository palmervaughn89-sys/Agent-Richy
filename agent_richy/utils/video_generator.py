"""CogVideoX-powered educational video generator for Agent Richy.

Generates short AI videos to teach financial literacy concepts to
kids, middle-schoolers, and high-schoolers.  Falls back gracefully
when GPU / dependencies are not available.

Requires: pip install diffusers torch accelerate
Recommended: NVIDIA GPU with 12GB+ VRAM (RTX 3060+/4070+)
"""

import os
import time
from pathlib import Path
from typing import Optional, List, Dict

# Output directory (project-root/data/videos/)
VIDEO_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "videos"

# ---------------------------------------------------------------------------
# Pre-crafted educational video prompt library
# ---------------------------------------------------------------------------

VIDEO_PROMPTS: Dict[str, Dict] = {
    # ---------- Savings & compound interest ----------
    "savings_piggy_bank": {
        "title": "The Magic Piggy Bank",
        "audience": "kids",
        "topic": "saving",
        "prompt": (
            "A bright, colorful 3-D animated scene of a cheerful cartoon piggy bank "
            "sitting on a wooden desk.  Gold coins float in one-by-one and each time "
            "a coin drops in the piggy bank glows a little bigger and smiles wider.  "
            "A small counter in the corner ticks upward.  Warm, soft lighting, "
            "Pixar-style animation, 4K, joyful atmosphere."
        ),
        "lesson": (
            "Every dollar you save is like feeding your piggy bank — "
            "the more you feed it, the bigger and stronger it gets!"
        ),
    },
    "compound_interest_tree": {
        "title": "The Money Tree",
        "audience": "middle",
        "topic": "compound interest",
        "prompt": (
            "A time-lapse animation of a tiny green seedling planted in rich soil.  "
            "As sunlight shines, the seedling grows rapidly into a large, beautiful "
            "tree.  Instead of leaves, crisp dollar bills sprout on every branch and "
            "flutter gently in the breeze.  A clock on the side fast-forwards through "
            "years 1, 5, 10, 20.  Lush garden background, cinematic lighting, "
            "whimsical cartoon style."
        ),
        "lesson": (
            "Compound interest means your money earns money ON TOP of money.  "
            "$100 at 8 %/year becomes $215 in 10 years — without adding a dime!"
        ),
    },
    "compound_snowball": {
        "title": "The Compound Snowball",
        "audience": "middle",
        "topic": "compound interest",
        "prompt": (
            "A small snowball at the top of a snowy mountain begins to roll downhill.  "
            "As it rolls it picks up more snow and grows exponentially larger.  "
            "Coins and dollar signs appear inside the snowball as it gains speed.  "
            "The snowball reaches a cheerful village at the bottom, now enormous.  "
            "Bright winter day, playful cartoon style, dynamic camera angles."
        ),
        "lesson": (
            "Investing is like rolling a snowball downhill — the longer it rolls, "
            "the bigger it gets.  Start early and let time do the heavy lifting!"
        ),
    },
    # ---------- Earning & hustling ----------
    "lemonade_stand": {
        "title": "Your First Business",
        "audience": "kids",
        "topic": "earning",
        "prompt": (
            "A cheerful animated teenager setting up a colorful lemonade stand on a "
            "sunny suburban sidewalk.  Customers line up smiling, handing over coins.  "
            "The teenager puts half the coins in a 'SAVE' jar and half in a 'SPEND' "
            "jar on the counter.  Happy neighborhood, warm golden-hour lighting, "
            "Pixar-style characters, vibrant colors."
        ),
        "lesson": (
            "Earning your own money is the first step.  The second step?  "
            "Pay yourself first — save BEFORE you spend."
        ),
    },
    "side_hustle_montage": {
        "title": "Side Hustle Montage",
        "audience": "high",
        "topic": "earning",
        "prompt": (
            "A fast-paced montage of a teenage entrepreneur: first mowing a lawn "
            "and collecting cash, then sitting at a laptop designing a logo in Canva, "
            "then filming a TikTok video, then high-fiving a happy customer.  Each "
            "scene transitions with rising dollar amounts: $50 → $200 → $500 → $1,000. "
            "Energetic, motivational tone, modern urban setting, cinematic color grading."
        ),
        "lesson": (
            "You don't need ONE perfect job — stack multiple small hustles "
            "and watch the income add up."
        ),
    },
    # ---------- Budgeting ----------
    "budget_pie_chart": {
        "title": "Where Does Your Money Go?",
        "audience": "middle",
        "topic": "budgeting",
        "prompt": (
            "An animated pie chart on a whiteboard that assembles itself slice by "
            "slice.  Each slice is labeled (Food, Fun, Savings, Phone, Clothes) and "
            "colored differently.  A cartoon hand with a marker circles the 'Savings' "
            "slice and draws a big star next to it.  Classroom setting, clean flat "
            "design, educational infographic style."
        ),
        "lesson": (
            "A budget is just a plan for your money.  When you PLAN where every "
            "dollar goes, you stop wondering where it all went."
        ),
    },
    "needs_vs_wants": {
        "title": "Needs vs. Wants",
        "audience": "kids",
        "topic": "budgeting",
        "prompt": (
            "A split-screen animation: on the left side labeled 'NEEDS', everyday "
            "essentials float by — food, water, school supplies, a warm jacket. "
            "On the right side labeled 'WANTS', fun items float by — video games, "
            "candy, designer shoes, concert tickets.  A friendly cartoon robot slides "
            "between the two sides helping sort items.  Bright, colorful, child-friendly."
        ),
        "lesson": (
            "Needs keep you alive and safe.  Wants make life fun.  "
            "Always cover your needs FIRST, then enjoy your wants."
        ),
    },
    # ---------- Investing ----------
    "stock_market_rollercoaster": {
        "title": "The Stock Market Rollercoaster",
        "audience": "high",
        "topic": "investing",
        "prompt": (
            "An animated rollercoaster shaped like a stock market chart — it climbs "
            "steeply, dips sharply, climbs even higher, dips again, but the overall "
            "trend is upward.  Cartoon riders cheer at the top and gasp at the dips "
            "but at the end they arrive at a platform much HIGHER than where they "
            "started.  Theme park setting, exciting camera work, vivid colors."
        ),
        "lesson": (
            "The stock market goes up AND down — that's normal.  "
            "Over 10-20 years, it has ALWAYS trended upward.  Stay patient!"
        ),
    },
    "roth_ira_rocket": {
        "title": "The Roth IRA Rocket",
        "audience": "high",
        "topic": "investing",
        "prompt": (
            "A cartoon teenager loads dollar bills into a shiny rocket labeled "
            "'ROTH IRA'.  The rocket launches slowly at first, then accelerates "
            "through the atmosphere.  In space the rocket transforms into a golden "
            "treasure chest overflowing with cash.  Text overlay: 'TAX-FREE GROWTH'. "
            "Sci-fi meets cartoon style, dramatic lighting, inspirational tone."
        ),
        "lesson": (
            "A Roth IRA lets your money grow tax-free.  Start as a teen and by "
            "retirement you could have over $1 MILLION from small contributions!"
        ),
    },
    # ---------- Bad habits ----------
    "impulse_buying_trap": {
        "title": "The Impulse Buying Trap",
        "audience": "middle",
        "topic": "bad habits",
        "prompt": (
            "A cartoon character walks through a flashy mall.  Neon signs flash "
            "'SALE! BUY NOW!' and items fly off shelves into their arms.  Their "
            "wallet shrinks visibly with each purchase.  Then the scene rewinds — "
            "this time the character pauses, thinks with a thought bubble showing "
            "a savings goal, and walks past.  Their wallet stays full and starts "
            "glowing.  Bright pop-art style, humorous tone."
        ),
        "lesson": (
            "The 48-hour rule: wait 2 days before any non-essential purchase.  "
            "70 % of the time, you'll realize you didn't actually need it."
        ),
    },
    "two_paths": {
        "title": "Two Paths — Saver vs. Spender",
        "audience": "high",
        "topic": "bad habits",
        "prompt": (
            "A split-screen animation showing two teens over 10 years.  Left path: "
            "teen saves and invests $100/month, shown by a growing garden.  Right "
            "path: teen spends everything on fast fashion and takeout, shown by a "
            "pile that shrinks.  At the end, the left teen has a car and savings "
            "account, the right teen has worn-out shoes and an empty wallet.  "
            "Clean infographic style, time-lapse feel, motivational."
        ),
        "lesson": (
            "Small choices today create massive differences tomorrow.  "
            "$100/month invested at 8 % = $18,000+ in 10 years."
        ),
    },
    # ---------- Debt awareness ----------
    "debt_monster": {
        "title": "The Debt Monster",
        "audience": "high",
        "topic": "debt",
        "prompt": (
            "A small, cute blob-like creature labeled 'DEBT $100' sits on a desk.  "
            "Interest charges cause it to grow — $200, $500, $1,000 — until it "
            "becomes a towering monster filling the room.  A brave teen fights back "
            "by feeding it 'PAYMENT' coins, shrinking it slice by slice until it "
            "disappears in a poof of confetti.  Fun monster-movie style, dramatic "
            "but humorous, vibrant colors."
        ),
        "lesson": (
            "Debt + interest grows like a monster.  Attack it early and "
            "consistently with payments — don't let it grow!"
        ),
    },
    # ================================================================
    #  NEW — Expanded curriculum prompts (18 additional)
    # ================================================================
    # ---------- Elementary: Money basics ----------
    "coins_and_counting": {
        "title": "Coins, Dollars & Making Change",
        "audience": "kids",
        "topic": "money basics",
        "prompt": (
            "A bright animated table-top view showing a child's hands sorting shiny "
            "coins — pennies, nickels, dimes, and quarters — into neat stacks.  "
            "Each stack glows and a label appears: 1¢, 5¢, 10¢, 25¢.  The coins "
            "then slide together to form a glowing dollar bill.  A small cash "
            "register rings happily.  Warm pastel colors, playful classroom "
            "setting, child-friendly cartoon style."
        ),
        "lesson": (
            "Knowing your coins and counting change is a real-life superpower.  "
            "Always count your change — that's YOUR money!"
        ),
    },
    "opportunity_cost_crossroads": {
        "title": "The Crossroads of Choice",
        "audience": "kids",
        "topic": "decision making",
        "prompt": (
            "A cartoon child stands at a colorful crossroads in a park.  One path "
            "leads to a glowing toy store, the other to a sparkling basketball court "
            "where a basketball bounces invitingly.  A thought bubble appears above "
            "the child showing both options.  The child picks one path and the other "
            "fades gently with a soft 'maybe next time' sparkle.  Bright, warm, "
            "Pixar-style, gentle music implied, educational atmosphere."
        ),
        "lesson": (
            "Every choice has an opportunity cost — the thing you give up.  "
            "Think about what you'll miss BEFORE you decide."
        ),
    },
    "marshmallow_patience": {
        "title": "The Marshmallow Test: Patience Pays",
        "audience": "kids",
        "topic": "mindset",
        "prompt": (
            "A cartoon child sits at a table with one fluffy marshmallow.  A clock "
            "on the wall ticks.  The child fidgets, imagines eating it, then takes "
            "a deep breath and waits.  Confetti bursts as a second marshmallow "
            "magically appears — the child now has TWO!  The table transforms into "
            "a piggy bank overflowing with coins.  Cheerful lab-room setting, "
            "soft pastel palette, heartwarming tone."
        ),
        "lesson": (
            "Waiting for a bigger reward is hard — but it's how you build wealth.  "
            "Patience turns one marshmallow into a mountain of them."
        ),
    },
    "giving_jar": {
        "title": "The Joy of Giving",
        "audience": "kids",
        "topic": "community",
        "prompt": (
            "Three colorful glass jars sit on a child's desk, labeled SAVE, SPEND, "
            "and GIVE in bright letters.  A cartoon hand drops coins into each jar.  "
            "The GIVE jar glows warmly and the coins transform into miniature scenes "
            "of help: a bowl of soup, a wrapped present, a planted tree.  Warm golden "
            "light, cozy bedroom setting, wholesome and heartwarming cartoon style."
        ),
        "lesson": (
            "Setting aside even a little to give makes the world better — "
            "and it makes YOU feel great too."
        ),
    },
    "bank_vault_adventure": {
        "title": "Inside the Bank Vault",
        "audience": "kids",
        "topic": "banking",
        "prompt": (
            "A friendly cartoon bank teller welcomes a child through sparkling glass "
            "doors.  They walk together into an animated vault filled with gold bars "
            "and stacks of bills.  A small savings account book appears and glows — "
            "numbers tick up as 'interest' sparkles rain down.  The child smiles and "
            "gives a thumbs up.  Grand but friendly bank interior, treasure-chest "
            "ambiance, safe and welcoming, Pixar-style characters."
        ),
        "lesson": (
            "A bank is a safe place for your money — and it pays you interest "
            "just for saving.  Your money makes money while you sleep!"
        ),
    },
    # ---------- Middle school: Financial skills ----------
    "smart_shopping_detective": {
        "title": "Smart Shopping Detective",
        "audience": "middle",
        "topic": "spending",
        "prompt": (
            "An animated teen detective with a magnifying glass walks through a "
            "colorful store.  Sale signs flash 'MEGA DEAL!' and 'LIMITED TIME!'  "
            "The detective examines each sign — fake ones turn red and crumble while "
            "real deals turn green and sparkle.  The teen then checks a phone app "
            "with price comparisons.  Pop-art colors, playful spy-thriller vibe, "
            "educational and humorous, modern retail setting."
        ),
        "lesson": (
            "Stores use tricks to make you spend more.  Be a smart shopping detective — "
            "compare prices, wait before buying, and never trust 'SALE' at face value."
        ),
    },
    "checking_vs_savings": {
        "title": "Checking vs. Savings Explained",
        "audience": "middle",
        "topic": "banking",
        "prompt": (
            "A split-screen animation: on the left a blue 'CHECKING' river flows "
            "quickly — money goes in, debit card purchases splash out like rapids.  "
            "On the right, a calm green 'SAVINGS' lake collects water and slowly "
            "rises.  Small fish labeled 'INTEREST' swim in the savings lake, "
            "making it grow.  A bridge connects both.  Nature-meets-finance, "
            "soothing but educational, clean cartoon style."
        ),
        "lesson": (
            "Checking = fast-flowing spending money.  Savings = a calm lake that "
            "grows with interest.  Use both wisely!"
        ),
    },
    "teen_entrepreneur_montage": {
        "title": "Think Like an Entrepreneur",
        "audience": "middle",
        "topic": "earning",
        "prompt": (
            "A fast montage of a cartoon teen spotting problems and creating solutions: "
            "first helping an elderly neighbor with a tablet, then making custom phone "
            "cases and selling them at school, then setting up a small tutoring desk.  "
            "Dollar signs float up from each activity.  A chalkboard shows: "
            "PROBLEM → SOLUTION → PROFIT.  Energetic, colorful, motivational, "
            "diverse characters, classroom-to-street transitions."
        ),
        "lesson": (
            "Entrepreneurs solve problems for a profit.  Look around you — "
            "what problem can YOU solve for someone?"
        ),
    },
    "credit_vs_debit_battle": {
        "title": "Credit vs. Debit Card Battle",
        "audience": "middle",
        "topic": "credit",
        "prompt": (
            "Two animated cards face off in an arena: a blue DEBIT card and a red "
            "CREDIT card.  The debit card draws from a visible bank balance that "
            "decreases transparently.  The credit card shoots purchases but a growing "
            "chain of INTEREST links appears behind it.  A referee cartoon character "
            "holds up a sign: 'PAY IN FULL = WIN'.  The credit card's chain dissolves "
            "when paid.  Comic-book battle style, bright and educational."
        ),
        "lesson": (
            "Debit spends YOUR money.  Credit borrows the bank's.  "
            "If you use credit, ALWAYS pay in full to avoid the interest chain."
        ),
    },
    "inflation_shrinking_dollar": {
        "title": "The Shrinking Dollar",
        "audience": "middle",
        "topic": "economics",
        "prompt": (
            "A cartoon dollar bill sits on a table.  A clock spins through years: "
            "1990, 2000, 2010, 2020.  With each decade the dollar bill physically "
            "shrinks while price tags on everyday items — milk, movie tickets, "
            "sneakers — grow larger.  At the end an investment account is shown "
            "growing to outpace the shrinking dollar.  Infographic style, "
            "time-lapse feel, clear educational graphics, warm tone."
        ),
        "lesson": (
            "Inflation makes your dollars buy less over time.  "
            "Investing your money helps it grow faster than prices rise."
        ),
    },
    "scam_alert_shield": {
        "title": "Scam Alert: Protect Your Money",
        "audience": "middle",
        "topic": "safety",
        "prompt": (
            "A cartoon teen scrolls through a phone.  Suspicious messages pop up: "
            "'YOU WON A PRIZE!', 'Send $50 to double your money!', a fake bank email.  "
            "Each scam message is blocked by a glowing blue SHIELD that materializes "
            "around the teen.  The scam messages shatter on impact.  The teen gives "
            "a confident thumbs-up.  Cyberpunk-meets-cartoon style, bright neon colors, "
            "empowering and educational tone."
        ),
        "lesson": (
            "If someone asks you to send money to GET money, it's a scam.  Always.  "
            "Your shield: never share personal info with strangers online."
        ),
    },
    "paycheck_breakdown_animation": {
        "title": "Where Does Your Paycheck Go?",
        "audience": "middle",
        "topic": "taxes",
        "prompt": (
            "A cartoon teenager receives an animated paycheck envelope.  As it opens, "
            "the gross pay ($480) splits into colorful streams: green for take-home pay "
            "($412), yellow for federal tax, orange for state tax, and purple for FICA.  "
            "Each stream flows into a labeled bucket.  The tax buckets morph into "
            "schools, roads, and firetrucks showing what taxes fund.  Clean infographic "
            "style, friendly, educational, modern flat design."
        ),
        "lesson": (
            "Your paycheck has money taken out before you get it.  "
            "Understanding gross vs. net pay is your first real-world money lesson."
        ),
    },
    "charity_impact_ripple": {
        "title": "Your Donation Creates Ripples",
        "audience": "middle",
        "topic": "community",
        "prompt": (
            "A cartoon hand drops a single glowing coin into a calm pond.  Ripples "
            "spread outward and each ring transforms into a scene of impact: a family "
            "eating dinner, a child reading a book, a community garden blooming.  "
            "The ripples keep expanding off-screen.  The text '10% can change the world' "
            "appears in gentle gold letters.  Peaceful, watercolor-inspired style, "
            "heartwarming, soft acoustic music implied."
        ),
        "lesson": (
            "Even a small donation creates big ripples.  Research your charity, "
            "give with intention, and watch your impact spread."
        ),
    },
    # ---------- High school: Real-world preparation ----------
    "credit_score_dashboard": {
        "title": "Your Credit Score Dashboard",
        "audience": "high",
        "topic": "credit",
        "prompt": (
            "A futuristic holographic dashboard appears before a young adult.  A large "
            "credit score speedometer sits in the center — the needle rises from 580 "
            "(red zone) through 670 (yellow) to 750 (green) as good financial habits "
            "materialize: on-time payments, low credit usage, account age.  Five pie "
            "slices show the score factors.  Cyberpunk-lite aesthetic, glowing blue "
            "and green neon, clean data visualization, aspirational tone."
        ),
        "lesson": (
            "Your credit score is your financial GPA.  Build it early: "
            "pay on time, keep balances low, and be patient."
        ),
    },
    "student_loan_comparison": {
        "title": "The Student Loan Reality Check",
        "audience": "high",
        "topic": "debt",
        "prompt": (
            "Split-screen: Left shows 'Path A' — a student at a fancy private campus "
            "with a growing DEBT counter above ($55K → $110K → $220K), chains appearing "
            "on their graduation gown.  Right shows 'Path B' — a student at a community "
            "college then state university, debt counter stays small ($25K), graduation "
            "with coins raining down.  Both hold the SAME diploma at the end.  "
            "Clean cinematic style, stark contrast, motivational."
        ),
        "lesson": (
            "Same degree, vastly different debt.  The school name matters less "
            "than the financial burden you carry after graduation."
        ),
    },
    "first_car_financial_guide": {
        "title": "Your First Car: Don't Get Wrecked",
        "audience": "high",
        "topic": "major purchases",
        "prompt": (
            "A cartoon teen looks at two cars in a showroom.  Car A is shiny and new — "
            "the price tag explodes into monthly payments, insurance costs, and gas "
            "charges that pile up like bricks.  Car B is a clean 3-year-old used car — "
            "its costs stack neatly and fit within a green budget bar.  The 20/4/10 "
            "rule appears on screen.  Car dealership setting, split comparison style, "
            "clean infographic, practical tone."
        ),
        "lesson": (
            "Your first car should be reliable and affordable, not flashy.  "
            "Follow the 20/4/10 rule: 20% down, 4-year loan max, payment ≤ 10% of income."
        ),
    },
    "first_apartment_walkthrough": {
        "title": "Renting Your First Apartment",
        "audience": "high",
        "topic": "housing",
        "prompt": (
            "A young adult walks through an apartment door for the first time.  "
            "Cost labels float in each room: RENT ($900), UTILITIES ($150), RENTER'S "
            "INSURANCE ($20), FURNITURE ($500 one-time).  A budget meter at the top "
            "fills to 30% — green checkmark.  Then a second scenario shows solo rent "
            "at 45% — red warning.  A roommate walks in and the meter drops to 25% — "
            "green again.  Clean lifestyle-magazine feel, warm lighting, practical."
        ),
        "lesson": (
            "Keep housing under 30% of your income.  Roommates aren't just fun — "
            "they're a wealth-building strategy."
        ),
    },
    "insurance_shield_animation": {
        "title": "Insurance: Your Financial Shield",
        "audience": "high",
        "topic": "protection",
        "prompt": (
            "A young adult stands confidently behind a large transparent shield.  "
            "Life events fly toward them — a car accident, a hospital bill, a stolen "
            "laptop.  Each impact hits the shield and bounces off in a shower of "
            "sparks while a small 'PREMIUM: $200/mo' counter ticks.  Without the "
            "shield, a second scene shows bills piling up: $8,500, $15,000.  "
            "Superhero-inspired, dramatic but educational, clean animation style."
        ),
        "lesson": (
            "Insurance costs money every month — but NOT having insurance "
            "costs WAY more when something goes wrong."
        ),
    },
}

# Group prompts by audience for easy menu building
PROMPTS_BY_AUDIENCE = {
    "kids": [k for k, v in VIDEO_PROMPTS.items() if v["audience"] == "kids"],
    "middle": [k for k, v in VIDEO_PROMPTS.items() if v["audience"] == "middle"],
    "high": [k for k, v in VIDEO_PROMPTS.items() if v["audience"] == "high"],
}

PROMPTS_BY_TOPIC = {}
for _k, _v in VIDEO_PROMPTS.items():
    PROMPTS_BY_TOPIC.setdefault(_v["topic"], []).append(_k)


# ---------------------------------------------------------------------------
# CogVideoX pipeline (lazy-loaded, optional)
# ---------------------------------------------------------------------------

_pipeline = None
_COGVIDEO_AVAILABLE: Optional[bool] = None


def _check_cogvideo_available() -> bool:
    """Return True if CogVideoX dependencies are installed."""
    global _COGVIDEO_AVAILABLE
    if _COGVIDEO_AVAILABLE is not None:
        return _COGVIDEO_AVAILABLE
    try:
        import torch                     # noqa: F401
        from diffusers import CogVideoXPipeline  # noqa: F401
        _COGVIDEO_AVAILABLE = True
    except ImportError:
        _COGVIDEO_AVAILABLE = False
    return _COGVIDEO_AVAILABLE


def _get_pipeline():
    """Lazy-load the CogVideoX pipeline (downloads model on first use).

    Memory strategy based on available VRAM:
    - 16GB+: Full model on GPU (fastest)
    - 12-16GB: Model CPU offload (moderate speed, fits in VRAM)
    - <12GB / no GPU: Sequential CPU offload (slow but works)
    """
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    if not _check_cogvideo_available():
        return None

    import torch
    from diffusers import CogVideoXPipeline

    model_id = os.environ.get("COGVIDEO_MODEL", "THUDM/CogVideoX-2b")
    has_cuda = torch.cuda.is_available()
    dtype = torch.float16 if has_cuda else torch.float32

    # Detect VRAM
    vram_gb = 0
    if has_cuda:
        vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
        gpu_name = torch.cuda.get_device_name(0)
        print(f"  🖥️  GPU detected: {gpu_name} ({vram_gb:.1f} GB VRAM)")
    else:
        print("  ⚠️  No CUDA GPU detected — generation will be very slow on CPU.")

    print(f"  ⏳ Loading CogVideoX model ({model_id}) — this may take a few minutes on first run...")
    start = time.time()

    _pipeline = CogVideoXPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
    )

    # Memory-efficient attention (xformers or SDPA)
    try:
        _pipeline.enable_xformers_memory_efficient_attention()
        print("  ✅ xformers memory-efficient attention enabled")
    except Exception:
        try:
            # PyTorch 2.0+ native SDPA — already default in newer diffusers
            pass
        except Exception:
            pass

    # VAE slicing + tiling for lower VRAM usage
    try:
        _pipeline.vae.enable_slicing()
        _pipeline.vae.enable_tiling()
    except Exception:
        pass

    # Place model based on available VRAM
    if has_cuda and vram_gb >= 16:
        _pipeline = _pipeline.to("cuda")
        print("  ✅ Full model loaded on GPU (fastest mode)")
    elif has_cuda and vram_gb >= 10:
        _pipeline.enable_model_cpu_offload()
        print("  ✅ Model CPU offload enabled (balanced speed/memory)")
    elif has_cuda:
        _pipeline.enable_sequential_cpu_offload()
        print("  ✅ Sequential CPU offload enabled (low VRAM mode)")
    # else: stays on CPU

    elapsed = time.time() - start
    print(f"  ✅ Model loaded in {elapsed:.1f}s")
    return _pipeline


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_video_generation_available() -> bool:
    """Check whether video generation can run on this machine."""
    return _check_cogvideo_available()


def list_videos_for_audience(audience: str) -> List[Dict]:
    """Return list of video prompt metadata for the given audience."""
    keys = PROMPTS_BY_AUDIENCE.get(audience, [])
    # Also include any audience below (kids ⊂ middle ⊂ high)
    if audience == "high":
        keys = list(set(keys + PROMPTS_BY_AUDIENCE.get("middle", [])
                        + PROMPTS_BY_AUDIENCE.get("kids", [])))
    elif audience == "middle":
        keys = list(set(keys + PROMPTS_BY_AUDIENCE.get("kids", [])))
    return [{"key": k, **VIDEO_PROMPTS[k]} for k in keys]


def generate_video(
    prompt_key: str,
    *,
    num_frames: int = 49,
    guidance_scale: float = 6.0,
    num_inference_steps: int = 50,
    output_dir: Optional[str] = None,
) -> Optional[str]:
    """Generate a video from a pre-built prompt key.

    Returns the file path of the saved .mp4, or None on failure.
    """
    if prompt_key not in VIDEO_PROMPTS:
        print(f"  ❌ Unknown video key: {prompt_key}")
        return None

    meta = VIDEO_PROMPTS[prompt_key]
    pipe = _get_pipeline()
    if pipe is None:
        print("  ❌ CogVideoX is not available on this system.")
        print("     Install with:  pip install diffusers torch accelerate")
        return None

    out_dir = Path(output_dir) if output_dir else VIDEO_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{prompt_key}.mp4"

    print(f"  🎬 Generating: {meta['title']}")
    print(f"     Prompt: {meta['prompt'][:100]}…")
    print(f"     Frames: {num_frames} | Steps: {num_inference_steps} | Guidance: {guidance_scale}")

    try:
        import torch
        start = time.time()

        # Generate with autocast for mixed precision on GPU
        gen_kwargs = dict(
            prompt=meta["prompt"],
            num_frames=num_frames,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        )
        if torch.cuda.is_available():
            with torch.autocast("cuda"):
                video_frames = pipe(**gen_kwargs).frames[0]
        else:
            video_frames = pipe(**gen_kwargs).frames[0]

        from diffusers.utils import export_to_video
        export_to_video(video_frames, str(out_path), fps=8)

        elapsed = time.time() - start
        print(f"  ✅ Saved to {out_path} ({elapsed:.1f}s)")

        # Free VRAM between generations
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return str(out_path)
    except Exception as e:
        print(f"  ❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_custom_video(
    custom_prompt: str,
    filename: str = "custom_video",
    *,
    num_frames: int = 49,
    guidance_scale: float = 6.0,
    num_inference_steps: int = 50,
    output_dir: Optional[str] = None,
) -> Optional[str]:
    """Generate a video from a free-form prompt string."""
    pipe = _get_pipeline()
    if pipe is None:
        print("  ❌ CogVideoX is not available on this system.")
        print("     Install with:  pip install diffusers torch accelerate")
        return None

    out_dir = Path(output_dir) if output_dir else VIDEO_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{filename}.mp4"

    print(f"  🎬 Generating custom video …")
    print(f"     Prompt: {custom_prompt[:100]}…")

    try:
        import torch
        start = time.time()

        gen_kwargs = dict(
            prompt=custom_prompt,
            num_frames=num_frames,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        )
        if torch.cuda.is_available():
            with torch.autocast("cuda"):
                video_frames = pipe(**gen_kwargs).frames[0]
        else:
            video_frames = pipe(**gen_kwargs).frames[0]

        from diffusers.utils import export_to_video
        export_to_video(video_frames, str(out_path), fps=8)

        elapsed = time.time() - start
        print(f"  ✅ Saved to {out_path} ({elapsed:.1f}s)")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return str(out_path)
    except Exception as e:
        print(f"  ❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def show_lesson_without_video(prompt_key: str) -> None:
    """Print the lesson text for a video even when generation isn't possible."""
    meta = VIDEO_PROMPTS.get(prompt_key)
    if not meta:
        return
    print(f"\n  🎬 {meta['title']}")
    print(f"     Topic: {meta['topic'].title()}")
    print(f"\n  📖 Visual description:")
    # Pretty-print the prompt as a description
    words = meta["prompt"].split(". ")
    for sentence in words:
        s = sentence.strip().rstrip(".")
        if s:
            print(f"     • {s}.")
    print(f"\n  📚 Lesson: {meta['lesson']}")


def get_video_path(prompt_key: str) -> Optional[str]:
    """Return the path to a generated video if it exists on disk."""
    path = VIDEO_DIR / f"{prompt_key}.mp4"
    return str(path) if path.exists() else None


def get_all_generated_videos() -> Dict[str, str]:
    """Return {prompt_key: file_path} for all existing generated videos."""
    result = {}
    if VIDEO_DIR.exists():
        for mp4 in VIDEO_DIR.glob("*.mp4"):
            key = mp4.stem
            if key in VIDEO_PROMPTS:
                result[key] = str(mp4)
    return result


def generate_all_videos(
    audience: Optional[str] = None,
    *,
    num_frames: int = 49,
    guidance_scale: float = 6.0,
    num_inference_steps: int = 50,
    skip_existing: bool = True,
) -> List[str]:
    """Generate all (or audience-filtered) videos. Returns list of saved paths.

    Args:
        audience: Optional filter — 'kids', 'middle', 'high', or None for all.
        skip_existing: Skip videos that already have an .mp4 on disk.
    """
    keys = list(VIDEO_PROMPTS.keys())
    if audience:
        keys = [k for k in keys if VIDEO_PROMPTS[k]["audience"] == audience]

    total = len(keys)
    generated = []
    skipped = 0

    print(f"\n{'='*60}")
    print(f"  Agent Richy — Video Generation Batch")
    print(f"  Videos to process: {total}")
    print(f"  Skip existing: {skip_existing}")
    print(f"{'='*60}\n")

    for i, key in enumerate(keys, 1):
        meta = VIDEO_PROMPTS[key]
        existing = get_video_path(key)

        if skip_existing and existing:
            print(f"  [{i}/{total}] ⏭️  Skipping '{meta['title']}' (already exists)")
            skipped += 1
            generated.append(existing)
            continue

        print(f"\n  [{i}/{total}] 🎬 Generating '{meta['title']}' ({meta['audience']})...")
        path = generate_video(
            key,
            num_frames=num_frames,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        )
        if path:
            generated.append(path)

    print(f"\n{'='*60}")
    print(f"  ✅ Done!  Generated: {len(generated) - skipped} | Skipped: {skipped} | Failed: {total - len(generated)}")
    print(f"  📁 Videos saved in: {VIDEO_DIR}")
    print(f"{'='*60}\n")

    return generated
