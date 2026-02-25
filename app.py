"""Agent Richy — AI Financial Coach.

Home page: avatar greeting, quick onboarding (name + age), then routes to chat.
This is an AI-FIRST tool — Richy the agent IS the product.
"""

import streamlit as st
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client
from agent_richy.avatar import get_avatar_html

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Richy — AI Financial Coach",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #aaa;
        margin-bottom: 1.5rem;
    }
    .tagline {
        font-size: 1rem;
        text-align: center;
        color: #777;
        margin-top: -0.5rem;
        margin-bottom: 2rem;
    }
    .avatar-center {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    .feature-item {
        background: #16213e;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #333;
        text-align: center;
    }
    .feature-item h4 { margin: 0.5rem 0 0.3rem; color: #FFD700; }
    .feature-item p { margin: 0; color: #aaa; font-size: 0.85rem; }
    .stDeployButton { display: none; }
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
if "financial_plan" not in st.session_state:
    st.session_state.financial_plan = {}
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False


# =========================================================================
#  ONBOARDING
# =========================================================================
if not st.session_state.onboarded:
    # Centered avatar
    _, col_avatar, _ = st.columns([1, 2, 1])
    with col_avatar:
        st.markdown(
            f'<div class="avatar-center">{get_avatar_html("happy", 200)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<p class="main-header">Agent Richy</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Your Personal AI Financial Coach</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="tagline">Talk to me. I\'ll build your entire financial plan.</p>',
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        with st.form("onboarding", border=True):
            name = st.text_input("What's your name?", placeholder="Enter your name")
            age = st.number_input("How old are you?", min_value=5, max_value=120, value=25)
            submitted = st.form_submit_button("Talk to Richy 🚀", use_container_width=True)
            if submitted and name:
                profile = UserProfile(name=name, age=int(age))
                profile.user_type = "youth" if age < 18 else "adult"
                st.session_state.profile = profile
                st.session_state.onboarded = True
                st.rerun()
            elif submitted:
                st.warning("Please enter your name to continue.")

    st.markdown("---")
    st.markdown("### What Richy Can Do")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
        <div class="feature-item">
            <h4>🤖 AI Financial Advisor</h4>
            <p>Tell me your situation — I'll create a personalized plan</p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feature-item">
            <h4>📊 Auto-Built Plans</h4>
            <p>Budget, debt payoff, investing — all generated from our chat</p>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feature-item">
            <h4>📚 Learning Center</h4>
            <p>30+ lessons with quizzes for kids, teens, and adults</p>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div class="feature-item">
            <h4>💬 Just Talk</h4>
            <p>No forms. No spreadsheets. Just tell me about your money.</p>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# =========================================================================
#  POST-ONBOARDING DASHBOARD
# =========================================================================
profile = st.session_state.profile

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div class="avatar-center">{get_avatar_html("happy", 100)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**{profile.name}** · age {profile.age}")
    mode = "🎓 Youth" if profile.is_youth() else "💼 Adult"
    st.caption(mode)

    if profile.monthly_income > 0:
        surplus = profile.monthly_surplus()
        st.metric("Monthly Surplus", f"${surplus:,.0f}")

    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Main content ─────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(
        f'<div class="avatar-center">{get_avatar_html("happy", 180)}</div>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(f'<p class="main-header">Hey, {profile.name}!</p>', unsafe_allow_html=True)

    if profile.is_youth():
        st.markdown(
            "Ready to learn about money? **Start chatting with me** "
            "or explore the **Learning Center** 📚"
        )
    else:
        if st.session_state.plan_generated:
            st.markdown(
                "Your financial plan is ready! Check the **My Plan** page. "
                "Or keep chatting to refine it 💪"
            )
        else:
            st.markdown(
                "Tell me about your income, debts, and goals — "
                "I'll create your complete financial plan. "
                "**No forms. Just conversation.** 💬"
            )

st.markdown("---")

# ── Quick navigation ─────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 💬 Talk to Richy")
    st.caption("Tell me everything — I'll build your plan from our conversation.")
    st.page_link("pages/1_Chat_with_Richy.py", label="Start Chatting →", use_container_width=True)

with c2:
    st.markdown("### 📊 My Plan")
    st.caption("Your AI-generated financial plan — budget, debt, investments, goals.")
    st.page_link("pages/3_My_Plan.py", label="View Plan →", use_container_width=True)

with c3:
    st.markdown("### 📚 Learning Center")
    st.caption("30+ lessons with quizzes — for all ages.")
    st.page_link("pages/2_Learning_Center.py", label="Start Learning →", use_container_width=True)

st.markdown("---")
st.markdown(
    "> *\"Don't fill out forms. Tell me your story — "
    "I'll build the plan.\"*  \n> — Agent Richy 💰"
)
