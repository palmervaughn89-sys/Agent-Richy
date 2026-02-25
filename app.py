"""Agent Richy — Web App Home Page.

Landing page with onboarding, Richy character, and dashboard.
"""

import streamlit as st
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Richy — Financial Coach",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #aaa;
        margin-bottom: 2rem;
    }
    .card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #333;
        height: 100%;
    }
    .card:hover { border-color: #FFD700; }
    .card h3 { margin-top: 0; }
    .metric-row {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }
    .hero-emoji {
        font-size: 5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.session_state.profile = UserProfile(name="", age=0)
if "llm_client" not in st.session_state:
    st.session_state.llm_client = get_openai_client()
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Helper to get OpenAI client lazily ───────────────────────────────────
def get_client():
    if st.session_state.llm_client is None:
        st.session_state.llm_client = get_openai_client()
    return st.session_state.llm_client


# =========================================================================
#  ONBOARDING
# =========================================================================
if not st.session_state.onboarded:
    st.markdown('<p class="hero-emoji">💰</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-header">Agent Richy</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Your Personal AI Financial Coach — For ALL Ages</p>',
        unsafe_allow_html=True,
    )

    with st.chat_message("assistant", avatar="💰"):
        st.markdown(
            "**Hey there! I'm Agent Richy** — your personal financial coach! 🎉\n\n"
            "Whether you're a kid learning about money, a teenager starting to earn, "
            "or an adult trying to break the paycheck-to-paycheck cycle — **I'm here to help.**\n\n"
            "Let me get to know you first!"
        )

    with st.form("onboarding", border=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("What's your name?", placeholder="Enter your name")
        with col2:
            age = st.number_input("How old are you?", min_value=5, max_value=120, value=25)
        submitted = st.form_submit_button("Let's Go! 🚀", use_container_width=True)
        if submitted and name:
            profile = UserProfile(name=name, age=int(age))
            profile.user_type = "youth" if age < 18 else "adult"
            st.session_state.profile = profile
            st.session_state.onboarded = True
            st.rerun()
        elif submitted:
            st.warning("Please enter your name to continue.")

    st.stop()

# =========================================================================
#  DASHBOARD (post-onboarding)
# =========================================================================
profile = st.session_state.profile

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown(f"**👤 {profile.name}** (age {profile.age})")
    mode = "🎓 Youth Mode" if profile.is_youth() else "💼 Adult Mode"
    st.markdown(mode)
    if profile.completed_assessment:
        surplus = profile.monthly_surplus()
        color = "green" if surplus >= 0 else "red"
        st.markdown(f"Surplus: :{'green' if surplus >= 0 else 'red'}[${surplus:,.0f}/mo]")
    st.markdown("---")
    if st.button("🔄 Reset Profile"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<p class="main-header">💰 Welcome, {profile.name}!</p>',
    unsafe_allow_html=True,
)

if profile.is_youth():
    st.markdown('<p class="sub-header">🌟 Youth Financial Lab</p>', unsafe_allow_html=True)
else:
    st.markdown('<p class="sub-header">📊 Adult Financial Planning Suite</p>', unsafe_allow_html=True)

# ── Richy greeting ───────────────────────────────────────────────────────
with st.chat_message("assistant", avatar="💰"):
    if profile.is_youth():
        st.markdown(
            f"Hey **{profile.name}**! You're getting a head start on money skills — "
            "that's awesome! 🎮\n\n"
            "Use the **sidebar** to chat with me, explore financial tools, "
            "take lessons, or check your profile."
        )
    elif profile.completed_assessment:
        surplus = profile.monthly_surplus()
        st.markdown(
            f"Welcome back **{profile.name}**! Your monthly surplus is "
            f"**${surplus:,.2f}**. Here's your dashboard — let's keep building! 💪"
        )
    else:
        st.markdown(
            f"Hey **{profile.name}**! I'd recommend starting with a "
            "**Financial Assessment** on the Profile page, or just chat with me.\n\n"
            "Use the **sidebar** to navigate between tools! 💡"
        )

# ── Quick metrics (if assessed) ─────────────────────────────────────────
if profile.completed_assessment:
    st.markdown("### 📊 Your Numbers at a Glance")
    c1, c2, c3, c4 = st.columns(4)
    surplus = profile.monthly_surplus()
    with c1:
        st.metric("Monthly Income", f"${profile.monthly_income:,.0f}")
    with c2:
        st.metric("Monthly Expenses", f"${profile.monthly_expenses:,.0f}")
    with c3:
        st.metric("Monthly Surplus", f"${surplus:,.0f}",
                   delta=f"{profile.savings_rate():.1f}% rate")
    with c4:
        ef_mo = profile.months_of_emergency()
        st.metric("Emergency Fund", f"${profile.emergency_fund:,.0f}",
                   delta=f"{ef_mo:.1f} months")

    if profile.debts:
        st.markdown("---")
        dc1, dc2 = st.columns(2)
        with dc1:
            st.metric("Total Debt", f"${profile.total_debt():,.0f}")
        with dc2:
            if profile.credit_score:
                st.metric("Credit Score", profile.credit_score)

# ── Navigation cards ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🧰 Quick Access")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("#### 🤖 Chat with Richy")
    st.caption("Ask anything about money, debt, investing, or budgeting.")
    st.page_link("pages/1_Chat_with_Richy.py", label="Open Chat →", use_container_width=True)
with c2:
    st.markdown("#### 💰 Financial Tools")
    st.caption("Budget simulator, debt payoff, tax estimator, mortgage calc & more.")
    st.page_link("pages/2_Financial_Tools.py", label="Open Tools →", use_container_width=True)
with c3:
    st.markdown("#### 📚 Learning Center")
    st.caption("Video lessons, bad habits quiz, savings challenges.")
    st.page_link("pages/3_Learning_Center.py", label="Start Learning →", use_container_width=True)
with c4:
    st.markdown("#### 📋 My Profile")
    st.caption("Financial assessment, snapshot, and personal recommendations.")
    st.page_link("pages/4_My_Profile.py", label="View Profile →", use_container_width=True)

# ── Motivational footer ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "> *\"The best time to start was yesterday. The second best time is now.\"*  \n"
    "> — Agent Richy 💰"
)
