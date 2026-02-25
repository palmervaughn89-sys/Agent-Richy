"""Learning Center — Financial literacy curriculum with animated video lessons, quizzes & challenges."""

import streamlit as st
import streamlit.components.v1 as components
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client, ask_llm
from agent_richy.avatar import get_avatar_html, get_avatar_with_speech
from agent_richy.animated_lessons import (
    ANIMATED_SHORTS,
    render_animated_short,
    get_shorts_for_audience,
)
from agent_richy.utils.video_generator import VIDEO_PROMPTS
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

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .avatar-center { display:flex; justify-content:center; align-items:center; margin:0.5rem 0; }
    .video-card {
        background: linear-gradient(135deg, #16213e, #0f3460);
        border-radius: 16px; padding: 16px; border: 1px solid rgba(255,215,0,0.15);
        text-align: center; transition: transform 0.2s, box-shadow 0.2s;
    }
    .video-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255,215,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

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
    st.session_state.quiz_scores = {}

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

AUDIENCE_COLORS = {"kids": "🟢", "middle": "🔵", "high": "🟣"}

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  HEADER                                                              ║
# ╚═══════════════════════════════════════════════════════════════════════╝
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    st.markdown(
        f'<div class="avatar-center">{get_avatar_html("happy", 120)}</div>',
        unsafe_allow_html=True,
    )
with header_col2:
    st.markdown("## 📚 Learning Center")
    completed_count = len(st.session_state.completed_lessons)
    total_lessons = len(lessons)
    if completed_count == 0:
        st.caption(f"Welcome! You have {total_lessons} lessons to explore.")
    elif completed_count == total_lessons:
        st.caption("🏆 You've completed every lesson! Champion!")
    else:
        st.caption(f"Progress: {completed_count}/{total_lessons} lessons completed")

# ── Progress bar ─────────────────────────────────────────────────────────
if lessons:
    progress = completed_count / total_lessons
    st.progress(progress, text=f"{completed_count}/{total_lessons} lessons completed")

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  TABS                                                                ║
# ╚═══════════════════════════════════════════════════════════════════════╝
tabs = st.tabs([
    "📖 Lessons",
    "🎬 Video Shorts",
    "🚫 Bad Habits Quiz",
    "💰 Savings Challenges",
    "🛡️ Insurance Guide",
])

# =====================================================================
# TAB 1 — LESSON CURRICULUM
# =====================================================================
with tabs[0]:
    st.markdown("### 📖 Financial Literacy Curriculum")
    st.caption(
        "Inspired by Junior Achievement, Biz Kid$, NGPF, Khan Academy, "
        "CFPB, EverFi, Jump$tart — all with original examples."
    )

    filter_cols = st.columns([2, 2, 2])
    with filter_cols[0]:
        grade_options = ["All Levels"]
        if any(l["audience"] == "kids" for l in lessons):
            grade_options.append("🟢 Elementary (Ages 5-10)")
        if any(l["audience"] == "middle" for l in lessons):
            grade_options.append("🔵 Middle School (Ages 11-14)")
        if any(l["audience"] == "high" for l in lessons):
            grade_options.append("🟣 High School (Ages 15-17)")
        grade_filter = st.selectbox("Grade Level", grade_options)

    with filter_cols[1]:
        categories = ["All Categories"] + sorted(set(l["category"] for l in lessons))
        cat_filter = st.selectbox("Category", categories)

    with filter_cols[2]:
        status_filter = st.selectbox("Status", ["All", "Not Started", "Completed"])

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
            st.markdown("#### 📖 The Lesson")
            st.markdown(lesson["lesson_text"])

            st.markdown("---")
            st.markdown("#### 💡 Real-World Example")
            st.info(lesson["example"])

            st.success(f"🔑 **Key Takeaway:** {lesson['key_takeaway']}")

            # Animated Video Short
            vkey = lesson.get("video_key", "")
            if vkey and vkey in ANIMATED_SHORTS:
                st.markdown("---")
                st.markdown("#### 🎬 Video Lesson")
                html = render_animated_short(vkey)
                if html:
                    components.html(html, height=680, scrolling=False)

            # Quiz
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
                        "Check Answers ✔️", use_container_width=True,
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
                            st.error(f"Q{qi + 1}: ❌ {user_ans} → Correct: **{correct_ans}**")

                    st.session_state.quiz_scores[lid] = (correct, len(quiz))
                    pct = correct / len(quiz)
                    if pct == 1.0:
                        st.balloons()
                        st.success(f"🏆 Perfect: {correct}/{len(quiz)}!")
                    elif pct >= 0.6:
                        st.info(f"Score: {correct}/{len(quiz)} — Good, review the misses!")
                    else:
                        st.warning(f"Score: {correct}/{len(quiz)} — Re-read and try again!")

            # Activity
            st.markdown("---")
            st.markdown("#### 🎯 Activity")
            st.markdown(lesson["activity"])

            # Mark complete
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
        st.info("No lessons match your filters. Try adjusting above.")


# =====================================================================
# TAB 2 — ANIMATED VIDEO SHORTS
# =====================================================================
with tabs[1]:
    st.markdown("### 🎬 TikTok-Style Video Lessons")
    st.caption(
        "Short, animated educational videos — swipe through to learn financial concepts fast! "
        "Each plays automatically with smooth animations."
    )

    # Get videos for this audience
    available_keys = get_shorts_for_audience(audience)
    total_videos = len(available_keys)
    st.success(f"🎥 **{total_videos} animated video lessons** ready to watch!")

    # Group by topic
    by_topic: dict = {}
    for key in available_keys:
        meta = ANIMATED_SHORTS.get(key, {})
        topic = meta.get("topic", "other").title()
        by_topic.setdefault(topic, []).append((key, meta))

    # Topic filter
    topics = ["All Topics"] + sorted(by_topic.keys())
    selected_topic = st.selectbox("Filter by Topic", topics)

    if selected_topic != "All Topics":
        by_topic = {k: v for k, v in by_topic.items() if k == selected_topic}

    for topic, items in sorted(by_topic.items()):
        st.markdown(f"#### {topic}")

        cols = st.columns(min(len(items), 3))
        for i, (key, meta) in enumerate(items):
            with cols[i % len(cols)]:
                aud_badge = AUDIENCE_COLORS.get(meta.get("audience", ""), "⚪")
                with st.container(border=True):
                    st.markdown(f"**{meta.get('title', key)}** {aud_badge}")
                    st.caption(f"Topic: {meta.get('topic', '').title()}")

                    # Play button expander
                    with st.expander("▶️ Watch Video"):
                        html = render_animated_short(key)
                        if html:
                            components.html(html, height=680, scrolling=False)

                    # Show lesson text
                    prompt_meta = VIDEO_PROMPTS.get(key, {})
                    if prompt_meta:
                        st.markdown(f"📖 {prompt_meta.get('lesson', '')}")


# =====================================================================
# TAB 3 — BAD HABITS QUIZ
# =====================================================================
with tabs[2]:
    st.markdown("### 🚫 Bad Financial Habits Check")
    st.caption("Be honest — awareness is the first step to change!")

    if profile.is_youth():
        habits = [
            ("Spending all my money as soon as I get it",
             "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings. Pay yourself first!"),
            ("Buying things just because friends have them",
             "FOMO spending is real. Ask: 'Will I use this in 30 days?' If not, skip it."),
            ("Never tracking where my money goes",
             "Use a notebook or free app. You can't fix what you don't measure."),
            ("Impulse buying on Amazon / online shopping",
             "The 72-hour rule: wait 3 days before buying anything non-essential."),
            ("Not saving for bigger goals",
             "Even $5/week = $260/year. Set a goal, visualize it, automate savings."),
            ("Lending money to friends and not getting it back",
             "It's OK to say no. Keep loans small and don't lend what you can't lose."),
            ("Comparing my stuff to what influencers have",
             "Most influencer lifestyles are sponsored. Build real wealth, not fake image."),
            ("Not knowing the difference between needs and wants",
             "Before ANY purchase: 'Can I survive without this?' If yes, it's a want."),
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
        submitted = st.form_submit_button("Check Results 📊", use_container_width=True)

    if submitted:
        score = sum(1 for v in st.session_state.quiz_answers.values() if v)
        total = len(habits)
        good = total - score

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

        for i, (habit, fix) in enumerate(habits):
            if st.session_state.quiz_answers.get(i, False):
                with st.expander(f"🔧 Fix: {habit[:60]}...", expanded=True):
                    st.success(fix)

        profile.bad_habits = [h.split("(")[0].strip()
                              for i, (h, _) in enumerate(habits)
                              if st.session_state.quiz_answers.get(i, False)]

        if score == 0:
            st.balloons()
            st.success("🎉 Zero bad habits — you're crushing it!")


# =====================================================================
# TAB 4 — SAVINGS CHALLENGES
# =====================================================================
with tabs[3]:
    st.markdown("### 💰 Savings Challenges")
    st.caption("Pick a challenge and build your savings muscle!")

    challenges = [
        {
            "name": "52-Week Challenge", "icon": "📅",
            "desc": "Save $1 in week 1, $2 in week 2 … $52 in week 52.",
            "total": "$1,378/year",
            "detail": "Week 1: $1 | Week 2: $2 | … Week 52: $52\n\n"
                      "**Total: $1,378!**\n\n💡 Reverse it: start at $52 when motivated.",
        },
        {
            "name": "No-Spend Weekend", "icon": "🚫",
            "desc": "One weekend per month — zero non-essential spending.",
            "total": "$100-$300/month",
            "detail": "Rules: no dining out, no shopping, no paid entertainment.\n"
                      "Cook at home, enjoy parks, game nights.\n"
                      "Transfer what you WOULD have spent to savings.",
        },
        {
            "name": "Round-Up Challenge", "icon": "🔄",
            "desc": "Round every purchase up and save the difference.",
            "total": "$30-$50/month",
            "detail": "Coffee $4.35 → $5.00, save $0.65\nGas $42.18 → $43.00, save $0.82\n\n"
                      "Most banking apps automate this! Check: Acorns, Chime.",
        },
        {
            "name": "100 Envelope Challenge", "icon": "✉️",
            "desc": "Number 100 envelopes 1-100. Pick one randomly each day.",
            "total": "$5,050 in 100 days",
            "detail": "Label 100 envelopes 1-100. Each day, randomly pick one and save that amount.\n\n"
                      "💡 Digital: use a random number generator and transfer to savings.",
        },
        {
            "name": "Subscription Detox", "icon": "📺",
            "desc": "Cancel ALL subscriptions for 30 days. Only reactivate what you miss.",
            "total": "$50-$200/month",
            "detail": "1. List every subscription\n2. Cancel ALL\n"
                      "3. After 30 days, only re-subscribe to genuinely missed ones.\n\n"
                      "Average savings: $600-$2,400/year!",
        },
        {
            "name": "Spare Change Jar", "icon": "🫙",
            "desc": "Empty pocket change into a jar every night.",
            "total": "$20-$60/month",
            "detail": "Classic and effective — especially for kids.\n"
                      "Monthly count and deposit to savings.\n"
                      "Challenge: guess the amount before counting!",
        },
    ]

    cols = st.columns(min(len(challenges), 3))
    for i, ch in enumerate(challenges):
        with cols[i % len(cols)]:
            with st.container(border=True):
                st.markdown(f"### {ch['icon']} {ch['name']}")
                st.markdown(ch["desc"])
                st.markdown(f"**Potential:** {ch['total']}")
                with st.expander("Details"):
                    st.markdown(ch["detail"])


# =====================================================================
# TAB 5 — INSURANCE GUIDE
# =====================================================================
with tabs[4]:
    st.markdown("### 🛡️ Insurance Guide")
    st.caption("Insurance protects what you build.")

    insurance_types = [
        ("🏥 Health Insurance", "critical",
         "One ER visit = $3,000-$30,000 without it.\n\n"
         "**Key terms:** Premium, deductible, copay, out-of-pocket max.\n\n"
         "Stay on parent's plan until age **26**. After: employer or ACA marketplace."),
        ("🚗 Auto Insurance", "required by law",
         "Required in 49/50 states. At minimum: $100K/$300K liability.\n\n"
         "Lower it with: good grades discount, defensive driving, higher deductible ($1,000).\n\n"
         "Shop around annually — rates vary 30-50%."),
        ("🏠 Renters Insurance", "essential & cheap",
         "~$15-$25/month. Covers personal property + liability.\n\n"
         "If your stuff was stolen/destroyed, could you replace it? **Every renter should have it.**"),
        ("💀 Life Insurance", "if dependents rely on your income",
         "Get **term life** (not whole). 10-12x annual income.\n\n"
         "25yr-old: $500K ≈ $20/mo. Only needed if someone depends on your income."),
        ("🦽 Disability Insurance", "your biggest asset: ability to earn",
         "Replaces 60-70% of income if you can't work.\n\n"
         "1 in 4 workers disabled before retirement. Check employer benefits!"),
        ("☂️ Umbrella Insurance", "if significant assets",
         "$1M coverage ≈ $200/year. Essential once net worth exceeds auto/home liability."),
    ]

    for title, priority, detail in insurance_types:
        with st.expander(f"{title} — *{priority}*"):
            st.markdown(detail)

    st.info(
        "**Never skip:** Health, Auto, Disability\n\n"
        "**Add when applicable:** Renters/Homeowners, Life, Umbrella"
    )
