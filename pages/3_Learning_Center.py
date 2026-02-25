"""Learning Center — Full financial literacy curriculum with lessons, quizzes, videos & challenges."""

import streamlit as st
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client, ask_llm
from agent_richy.utils.video_generator import (
    VIDEO_PROMPTS,
    get_video_path,
    get_all_generated_videos,
)
from agent_richy.lessons import (
    ELEMENTARY_LESSONS,
    MIDDLE_SCHOOL_LESSONS,
    HIGH_SCHOOL_LESSONS,
    ALL_LESSONS,
    get_lessons_for_audience,
    get_all_categories,
)
from agent_richy.modules.adult import BAD_HABITS_ADULT

st.set_page_config(page_title="Learning Center", page_icon="📚", layout="wide")

# ── Session guard ────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.warning("Please start from the **Home** page first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile: UserProfile = st.session_state.profile
client = st.session_state.get("llm_client")

# ── Progress state ───────────────────────────────────────────────────────
if "completed_lessons" not in st.session_state:
    st.session_state.completed_lessons = set()
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}  # lesson_id -> (correct, total)

# ── Determine audience ───────────────────────────────────────────────────
def _get_audience() -> str:
    if profile.is_youth():
        if profile.age and profile.age < 11:
            return "kids"
        elif profile.age and profile.age < 15:
            return "middle"
        return "high"
    return "adult"

audience = _get_audience()
lessons = get_lessons_for_audience(audience)

# ── Helper: audience badge color ─────────────────────────────────────────
AUDIENCE_COLORS = {"kids": "🟢", "middle": "🔵", "high": "🟣"}

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  HEADER                                                              ║
# ╚═══════════════════════════════════════════════════════════════════════╝
st.markdown("## 📚 Learning Center")

with st.chat_message("assistant", avatar="💰"):
    completed_count = len(st.session_state.completed_lessons)
    total_lessons = len(lessons)
    if completed_count == 0:
        greeting = (
            f"Welcome, **{profile.name}**! 🎓 You have **{total_lessons} lessons** "
            "ready to explore.  Each one has a mini-lesson, a real-world example, "
            "a video, a quiz, and an activity.  Let's level up your money skills!"
        )
    elif completed_count == total_lessons:
        greeting = "🏆 You've completed EVERY lesson!  You're a financial literacy champion!"
    else:
        greeting = (
            f"Great progress, **{profile.name}**! You've completed "
            f"**{completed_count}/{total_lessons}** lessons.  Keep it up!"
        )
    st.markdown(greeting)

# ── Progress bar ─────────────────────────────────────────────────────────
if lessons:
    progress = completed_count / total_lessons
    st.progress(progress, text=f"{completed_count}/{total_lessons} lessons completed")

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  TABS                                                                ║
# ╚═══════════════════════════════════════════════════════════════════════╝
tabs = st.tabs([
    "📖 Lesson Curriculum",
    "🎬 Video Library",
    "🚫 Bad Habits Quiz",
    "💰 Savings Challenges",
    "🛡️ Insurance Guide",
])

# =====================================================================
# TAB 1 — LESSON CURRICULUM (main tab)
# =====================================================================
with tabs[0]:
    st.markdown("### 📖 Financial Literacy Curriculum")
    st.caption(
        "Lessons inspired by the best youth financial education programs: "
        "Junior Achievement, Biz Kid$, NGPF, Khan Academy, CFPB Money As You Grow, "
        "EverFi, Jump$tart Coalition, and more — all with original examples."
    )

    # ── Filters ──────────────────────────────────────────────────────
    filter_cols = st.columns([2, 2, 2])
    with filter_cols[0]:
        # Grade level filter
        grade_options = ["All Levels"]
        if any(l["audience"] == "kids" for l in lessons):
            grade_options.append("🟢 Elementary (Ages 5-10)")
        if any(l["audience"] == "middle" for l in lessons):
            grade_options.append("🔵 Middle School (Ages 11-14)")
        if any(l["audience"] == "high" for l in lessons):
            grade_options.append("🟣 High School (Ages 15-17)")
        grade_filter = st.selectbox("Grade Level", grade_options)

    with filter_cols[1]:
        # Category filter
        categories = ["All Categories"] + sorted(set(l["category"] for l in lessons))
        cat_filter = st.selectbox("Category", categories)

    with filter_cols[2]:
        # Status filter
        status_filter = st.selectbox("Status", ["All", "Not Started", "Completed"])

    # ── Apply filters ────────────────────────────────────────────────
    filtered = lessons[:]
    if "Elementary" in grade_filter:
        filtered = [l for l in filtered if l["audience"] == "kids"]
    elif "Middle" in grade_filter:
        filtered = [l for l in filtered if l["audience"] == "middle"]
    elif "High" in grade_filter:
        filtered = [l for l in filtered if l["audience"] == "high"]

    if cat_filter != "All Categories":
        filtered = [l for l in filtered if l["category"] == cat_filter]

    if status_filter == "Completed":
        filtered = [l for l in filtered if l["id"] in st.session_state.completed_lessons]
    elif status_filter == "Not Started":
        filtered = [l for l in filtered if l["id"] not in st.session_state.completed_lessons]

    st.caption(f"Showing {len(filtered)} of {len(lessons)} lessons")

    # ── Render each lesson ───────────────────────────────────────────
    generated_videos = get_all_generated_videos()

    for lesson in filtered:
        lid = lesson["id"]
        is_completed = lid in st.session_state.completed_lessons
        badge = AUDIENCE_COLORS.get(lesson["audience"], "⚪")
        status_emoji = "✅" if is_completed else "📝"

        with st.expander(
            f"{status_emoji} {lesson['icon']} **{lesson['title']}** — "
            f"{badge} {lesson['audience'].title()} · {lesson['category']}",
            expanded=False,
        ):
            # ── Lesson Text section ──────────────────────────────────
            st.markdown("#### 📖 The Lesson")
            st.markdown(lesson["lesson_text"])

            # ── Example section ──────────────────────────────────────
            st.markdown("---")
            st.markdown("#### 💡 Real-World Example")
            st.info(lesson["example"])

            # ── Key Takeaway ─────────────────────────────────────────
            st.success(f"🔑 **Key Takeaway:** {lesson['key_takeaway']}")

            # ── Video section ────────────────────────────────────────
            vkey = lesson.get("video_key", "")
            if vkey and vkey in VIDEO_PROMPTS:
                st.markdown("---")
                st.markdown("#### 🎬 Video Lesson")
                vpath = get_video_path(vkey)
                if vpath:
                    st.video(vpath)
                else:
                    prompt_data = VIDEO_PROMPTS[vkey]
                    st.warning(
                        "🎬 Video not generated yet.  Run locally: "
                        "`python generate_videos.py --key " + vkey + "`"
                    )
                    with st.popover("🎨 See Video Storyboard"):
                        st.markdown(f"**{prompt_data['title']}**")
                        st.caption(prompt_data["prompt"])
                        st.markdown(f"**Lesson:** {prompt_data['lesson']}")

            # ── Quiz section ─────────────────────────────────────────
            quiz = lesson.get("quiz", [])
            if quiz:
                st.markdown("---")
                st.markdown("#### 🧪 Quick Quiz")

                form_key = f"quiz_{lid}"
                with st.form(form_key):
                    answers = []
                    for qi, q in enumerate(quiz):
                        choice = st.radio(
                            q["q"],
                            q["choices"],
                            index=None,
                            key=f"{form_key}_q{qi}",
                        )
                        answers.append(choice)

                    quiz_submitted = st.form_submit_button(
                        "Check Answers ✔️",
                        use_container_width=True,
                    )

                if quiz_submitted:
                    correct = 0
                    for qi, q in enumerate(quiz):
                        user_ans = answers[qi]
                        correct_ans = q["choices"][q["answer_index"]]
                        if user_ans == correct_ans:
                            correct += 1
                            st.success(f"Q{qi + 1}: ✅ Correct!")
                        elif user_ans is None:
                            st.warning(f"Q{qi + 1}: ⚠️ No answer selected.")
                        else:
                            st.error(f"Q{qi + 1}: ❌ Your answer: {user_ans}  →  Correct: **{correct_ans}**")

                    st.session_state.quiz_scores[lid] = (correct, len(quiz))
                    pct = correct / len(quiz)
                    if pct == 1.0:
                        st.balloons()
                        st.success(f"🏆 Perfect score: {correct}/{len(quiz)}!")
                    elif pct >= 0.6:
                        st.info(f"📊 Score: {correct}/{len(quiz)} — Good job, review the ones you missed!")
                    else:
                        st.warning(f"📊 Score: {correct}/{len(quiz)} — Re-read the lesson and try again!")

            # ── Activity section ─────────────────────────────────────
            st.markdown("---")
            st.markdown("#### 🎯 Activity")
            st.markdown(lesson["activity"])

            # ── Mark complete button ─────────────────────────────────
            st.markdown("---")
            comp_cols = st.columns([3, 1])
            with comp_cols[1]:
                if is_completed:
                    st.success("✅ Completed")
                    if st.button("Undo", key=f"undo_{lid}"):
                        st.session_state.completed_lessons.discard(lid)
                        st.rerun()
                else:
                    if st.button("Mark Complete ✅", key=f"complete_{lid}", use_container_width=True):
                        st.session_state.completed_lessons.add(lid)
                        st.rerun()

    if not filtered:
        st.info("No lessons match your current filters.  Try adjusting the filters above.")


# =====================================================================
# TAB 2 — VIDEO LIBRARY
# =====================================================================
with tabs[1]:
    st.markdown("### 🎬 Video Lesson Library")
    st.caption("All educational video content in one place.  Powered by CogVideoX AI generation.")

    generated_videos = get_all_generated_videos()
    total_prompts = len(VIDEO_PROMPTS)

    # Status bar
    if generated_videos:
        st.success(f"🎥 {len(generated_videos)}/{total_prompts} videos generated and ready to play!")
    else:
        st.info(
            "🎬 No videos generated yet.  To create videos, run on your local GPU:\n\n"
            "```bash\n"
            "pip install -r requirements-gpu.txt\n"
            "python generate_videos.py\n"
            "```"
        )

    # Group by topic
    by_topic: dict = {}
    for key, meta in VIDEO_PROMPTS.items():
        by_topic.setdefault(meta["topic"].title(), []).append((key, meta))

    for topic, items in sorted(by_topic.items()):
        st.markdown(f"#### {topic}")
        cols = st.columns(min(len(items), 3))
        for i, (key, meta) in enumerate(items):
            with cols[i % len(cols)]:
                aud_badge = AUDIENCE_COLORS.get(meta["audience"], "⚪")
                with st.container(border=True):
                    st.markdown(f"**{meta['title']}** {aud_badge}")
                    video_path = get_video_path(key)
                    if video_path:
                        st.video(video_path)
                    else:
                        st.caption("📽️ Not yet generated")

                    st.markdown(f"📖 {meta['lesson']}")

                    with st.popover("🎨 Storyboard"):
                        st.caption(meta["prompt"])

    if not by_topic:
        st.info("No video prompts available.")


# =====================================================================
# TAB 3 — BAD HABITS QUIZ
# =====================================================================
with tabs[2]:
    st.markdown("### 🚫 Bad Financial Habits Check")
    st.caption("Be honest — awareness is the first step to change!")

    if profile.is_youth():
        habits = [
            ("Spending all my money as soon as I get it",
             "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.  Pay yourself first!"),
            ("Buying things just because friends have them",
             "FOMO spending is real.  Ask: 'Will I use this in 30 days?'  If not, skip it."),
            ("Never tracking where my money goes",
             "Use a notebook or free app.  You can't fix what you don't measure."),
            ("Impulse buying on Amazon / online shopping",
             "The 72-hour rule: wait 3 days before buying anything non-essential.  You'll skip most."),
            ("Not saving for bigger goals",
             "Even $5/week = $260/year.  Set a goal, visualize it, and automate savings."),
            ("Lending money to friends and not getting it back",
             "It's OK to say no.  If you lend, keep it small and don't lend what you can't afford to lose."),
            ("Comparing my stuff to what influencers have",
             "Most influencer lifestyles are sponsored/rented.  Your goal: build real wealth, not fake image."),
            ("Not knowing the difference between needs and wants",
             "Before ANY purchase, ask: 'Can I survive without this?'  If yes, it's a want — not a need."),
        ]
    else:
        habits = BAD_HABITS_ADULT

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    with st.form("habits_quiz"):
        for i, (habit, fix) in enumerate(habits):
            st.session_state.quiz_answers[i] = st.checkbox(
                habit, key=f"habit_{i}", value=st.session_state.quiz_answers.get(i, False)
            )

        submitted = st.form_submit_button("Check My Results 📊", use_container_width=True)

    if submitted:
        score = sum(1 for v in st.session_state.quiz_answers.values() if v)
        total = len(habits)
        good = total - score

        st.markdown("---")
        st.markdown("### Results")

        rc1, rc2 = st.columns(2)
        with rc1:
            st.metric("Bad Habits Found", f"{score}/{total}")
        with rc2:
            pct = good / total
            if pct >= 0.8:
                st.metric("Financial Health", "Excellent 🌟")
            elif pct >= 0.6:
                st.metric("Financial Health", "Good 👍")
            elif pct >= 0.4:
                st.metric("Financial Health", "Needs Work ⚠️")
            else:
                st.metric("Financial Health", "Time to Change 🔥")

        st.progress(good / total)

        # Show fixes for identified habits
        identified = []
        for i, (habit, fix) in enumerate(habits):
            if st.session_state.quiz_answers.get(i, False):
                identified.append(habit)
                with st.expander(f"🔧 Fix: {habit[:60]}...", expanded=True):
                    st.success(fix)

        profile.bad_habits = [h.split("(")[0].strip() for h in identified]

        if score == 0:
            st.balloons()
            st.success("🎉 Zero bad habits found — you're crushing it!")
        elif identified:
            resp = ask_llm(
                client,
                system_prompt=(
                    "You are Agent Richy.  Create a motivating 30-day challenge to fix "
                    f"this financial habit: {identified[0]}.  "
                    "Include weekly milestones.  Be specific and encouraging.  Under 200 words."
                ),
                user_message=f"Age: {profile.age}, Income: ${profile.monthly_income:,.0f}/mo",
            )
            if resp:
                st.markdown("### 🤖 Richy's 30-Day Challenge")
                with st.chat_message("assistant", avatar="💰"):
                    st.markdown(resp)


# =====================================================================
# TAB 4 — SAVINGS CHALLENGES
# =====================================================================
with tabs[3]:
    st.markdown("### 💰 Savings Challenges")
    st.caption("Pick a challenge and start building your savings muscle!")

    challenges = [
        {
            "name": "52-Week Challenge",
            "icon": "📅",
            "desc": "Save $1 in week 1, $2 in week 2 … $52 in week 52.",
            "total": "$1,378 in one year",
            "detail": (
                "Week 1: $1 | Week 2: $2 | Week 3: $3 … Week 52: $52\n\n"
                "**Total saved: $1,378!**\n\n"
                "💡 **Pro tip:** Reverse it!  Start at $52 when motivated, "
                "finish with $1 when energy dips."
            ),
        },
        {
            "name": "No-Spend Weekend",
            "icon": "🚫",
            "desc": "One weekend per month with zero non-essential spending.",
            "total": "$100-$300/month saved",
            "detail": (
                "Pick one weekend per month.  Rules:\n"
                "- No dining out, no shopping, no paid entertainment\n"
                "- Cook at home, enjoy free activities (parks, hikes, game nights)\n"
                "- Transfer what you WOULD have spent to savings\n\n"
                "Average savings: $100-$300 per no-spend weekend!"
            ),
        },
        {
            "name": "Round-Up Challenge",
            "icon": "🔄",
            "desc": "Round every purchase up to the nearest dollar and save the difference.",
            "total": "$30-$50/month",
            "detail": (
                "Every purchase, round up to the next dollar:\n"
                "- Coffee $4.35 → $5.00, save $0.65\n"
                "- Gas $42.18 → $43.00, save $0.82\n\n"
                "Most banking apps automate this!  "
                "Check: Acorns, Chime, Bank of America's Keep the Change."
            ),
        },
        {
            "name": "100 Envelope Challenge",
            "icon": "✉️",
            "desc": "Number 100 envelopes 1-100.  Pick one randomly each day.",
            "total": "$5,050 in 100 days",
            "detail": (
                "Label 100 envelopes 1-100.\n"
                "Each day, randomly pick one and save that dollar amount.\n\n"
                "After 100 days: **$5,050 saved!**\n\n"
                "💡 Digital: use a random number generator and transfer to savings."
            ),
        },
        {
            "name": "Subscription Detox (30 Days)",
            "icon": "📺",
            "desc": "Cancel ALL subscriptions for 30 days.  Reactivate only what you truly miss.",
            "total": "$50-$200/month",
            "detail": (
                "Steps:\n"
                "1. List every subscription\n"
                "2. Cancel ALL of them (most reactivate easily)\n"
                "3. After 30 days, only re-subscribe to ones you genuinely missed\n\n"
                "Average savings: $50-$200/month = $600-$2,400/year!"
            ),
        },
        {
            "name": "Spare Change Jar",
            "icon": "🫙",
            "desc": "Empty pocket change into a jar every night.  Count it monthly.",
            "total": "$20-$60/month",
            "detail": (
                "Classic and effective — especially for kids.\n"
                "- Every night, empty coins from pockets / bags into a jar\n"
                "- At month-end, count and deposit to savings\n"
                "- Challenge: guess how much is in the jar before counting!\n\n"
                "Great way to make saving a daily habit."
            ),
        },
    ]

    cols = st.columns(min(len(challenges), 3))
    for i, ch in enumerate(challenges):
        with cols[i % len(cols)]:
            with st.container(border=True):
                st.markdown(f"### {ch['icon']} {ch['name']}")
                st.markdown(ch["desc"])
                st.markdown(f"**Potential:** {ch['total']}")
                with st.expander("See details"):
                    st.markdown(ch["detail"])


# =====================================================================
# TAB 5 — INSURANCE GUIDE
# =====================================================================
with tabs[4]:
    st.markdown("### 🛡️ Insurance Guide")
    st.caption("Insurance protects what you build.  Here's what you need to know.")

    insurance_types = [
        ("🏥 Health Insurance", "critical",
         "The most important insurance.  One ER visit = $3,000-$30,000 without it.\n\n"
         "**Key terms:** Premium (monthly cost), deductible (what you pay first), "
         "copay (your share per visit), out-of-pocket max (your yearly ceiling).\n\n"
         "Stay on a parent's plan until age **26**.  After that: employer plan or ACA marketplace."),
        ("🚗 Auto Insurance", "required by law",
         "Required in 49/50 states.  At minimum: $100K/$300K liability.\n\n"
         "**Teen drivers:** $150-$300/month.  Lower it with: good grades discount, "
         "defensive driving course, higher deductible ($1,000 if you have savings).\n\n"
         "Shop around annually — rates vary 30-50% between providers."),
        ("🏠 Renters Insurance", "essential & cheap",
         "~$15-$25/month.  Covers personal property + liability.\n\n"
         "If your laptop, phone, clothes, and furniture were stolen or destroyed, "
         "could you replace them?  That's what renter's insurance does.\n\n"
         "**Every renter should have it.**"),
        ("💀 Life Insurance", "if anyone depends on your income",
         "Get **term life** (not whole life).  10-12x annual income.\n\n"
         "A healthy 25-year-old: $500K coverage ≈ $20/month.\n"
         "A healthy 35-year-old: $500K coverage ≈ $30/month.\n\n"
         "Buy it young when it's cheapest.  Only needed if someone relies on your income."),
        ("🦽 Disability Insurance", "your biggest asset is your ability to earn",
         "Long-term disability replaces 60-70% of your income if you can't work.\n\n"
         "1 in 4 workers will be disabled before retirement age.  "
         "Many employers offer it — check your benefits!"),
        ("☂️ Umbrella Insurance", "if you have significant assets",
         "$1M umbrella coverage ≈ $200/year.\n\n"
         "Covers beyond auto/home liability limits.  Essential once your "
         "net worth exceeds your auto/home liability coverage."),
    ]

    for title, priority, detail in insurance_types:
        with st.expander(f"{title} — *{priority}*", expanded=False):
            st.markdown(detail)

    st.info(
        "**Never skip:** Health, Auto, Disability  \n"
        "**Add when applicable:** Renters/Homeowners, Life (if dependents), Umbrella (if assets)"
    )
