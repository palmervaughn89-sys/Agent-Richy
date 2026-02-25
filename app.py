"""Agent Richy — AI-Powered Financial Coach.

Premium fintech coaching platform with multi-agent AI system,
professional onboarding, and kids financial education.
"""

import streamlit as st
from agent_richy.profiles import UserProfile
from styles import inject_styles
from config import (
    COLORS, AGENTS, AGE_RANGES, EXPERIENCE_LEVELS,
    EMPLOYMENT_STATUS, INCOME_RANGES, FINANCIAL_GOALS,
)
from utils.session import init_session_state, get_profile
from components.progress_tracker import render_onboarding_progress
from components.agent_card import render_agent_card

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Richy — AI Financial Coach",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()
init_session_state()


# =========================================================================
#  ONBOARDING FLOW (4 steps)
# =========================================================================
if not st.session_state.onboarded:

    step = st.session_state.onboarding_step

    # ── Step 0 — Welcome Screen ──────────────────────────────────────────
    if step == 0 or step == 1 and not st.session_state.get("onboarding_started"):

        st.markdown("")  # spacer
        _, center, _ = st.columns([1, 3, 1])
        with center:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 0.5rem;">💰</div>
                <h1 class="hero-title">Agent Richy</h1>
                <p class="hero-subtitle">Your AI-Powered Financial Coach — Smarter Money Starts Here</p>
            </div>
            """, unsafe_allow_html=True)

        # Feature showcase
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">🤖</div>
                <h4>Personal AI Coaches</h4>
                <p>6 specialized agents for every financial need — budgeting, investing, debt, savings, and more</p>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">🎓</div>
                <h4>Kids Financial Education</h4>
                <p>Teach your children about money with fun video lessons, quizzes, and progress tracking</p>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">📊</div>
                <h4>Smart Insights</h4>
                <p>Real calculations and actionable plans — not generic advice. Numbers that matter.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
            if st.button("Get Started  →", use_container_width=True, key="start_btn"):
                st.session_state.onboarding_step = 1
                st.session_state.onboarding_started = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.stop()

    # ── Progress indicator ────────────────────────────────────────────────
    render_onboarding_progress(step, 4)

    _, form_col, _ = st.columns([1, 2, 1])

    # ── Step 1 — Tell us about yourself ──────────────────────────────────
    if step == 1:
        with form_col:
            st.markdown("### 👋 Tell us about yourself")
            st.caption("Let's personalize your experience.")

            with st.form("onboard_step1", border=True):
                name = st.text_input(
                    "What's your name?",
                    placeholder="Enter your name",
                    value=st.session_state.get("ob_name", ""),
                )
                age_range = st.selectbox("Age range", AGE_RANGES)
                exp_level = st.selectbox("Financial experience", EXPERIENCE_LEVELS)
                employment = st.selectbox("Employment status", EMPLOYMENT_STATUS)
                income_range = st.selectbox("Approximate annual income", INCOME_RANGES)

                submitted = st.form_submit_button("Next →", use_container_width=True)
                if submitted and name:
                    # Parse age from range
                    age_map = {"Under 13": 10, "13-17": 15, "18-24": 21,
                               "25-34": 30, "35-44": 40, "45-54": 50,
                               "55-64": 60, "65+": 70}
                    age = age_map.get(age_range, 30)

                    st.session_state.ob_name = name
                    st.session_state.ob_age = age
                    st.session_state.ob_age_range = age_range
                    st.session_state.ob_experience = exp_level
                    st.session_state.ob_employment = employment
                    st.session_state.ob_income_range = income_range
                    st.session_state.onboarding_step = 2
                    st.rerun()
                elif submitted:
                    st.warning("Please enter your name to continue.")

    # ── Step 2 — Financial Goals ─────────────────────────────────────────
    elif step == 2:
        with form_col:
            st.markdown("### 🎯 What are your financial goals?")
            st.caption("Select all that apply, then pick your top 3 priorities.")

            with st.form("onboard_step2", border=True):
                selected_goals = st.multiselect(
                    "Select your goals",
                    FINANCIAL_GOALS,
                    default=st.session_state.get("ob_goals", []),
                )
                other_goal = st.text_input(
                    "Other goal (optional)",
                    placeholder="e.g., Start a business",
                )

                st.markdown("**Rank your top 3 priorities** (drag to reorder or select)")
                if selected_goals:
                    top_goals = selected_goals[:3]
                    st.info(f"Top priorities: {', '.join(top_goals)}")

                col_back, col_next = st.columns(2)
                with col_back:
                    back = st.form_submit_button("← Back", use_container_width=True)
                with col_next:
                    submitted = st.form_submit_button("Next →", use_container_width=True)

                if back:
                    st.session_state.onboarding_step = 1
                    st.rerun()
                if submitted:
                    goals = selected_goals[:]
                    if other_goal:
                        goals.append(other_goal)
                    st.session_state.ob_goals = goals
                    st.session_state.onboarding_step = 3
                    st.rerun()

    # ── Step 3 — Financial Snapshot (optional) ───────────────────────────
    elif step == 3:
        with form_col:
            st.markdown("### 💼 Your financial snapshot")
            st.caption(
                "This helps us personalize your advice. All data stays private and "
                "is only used in this session."
            )

            with st.form("onboard_step3", border=True):
                monthly_income = st.number_input(
                    "Monthly income ($)", min_value=0, value=0, step=100,
                )
                monthly_expenses = st.number_input(
                    "Monthly expenses ($)", min_value=0, value=0, step=100,
                )
                total_debt = st.number_input(
                    "Total debt ($)", min_value=0, value=0, step=500,
                )
                current_savings = st.number_input(
                    "Current savings ($)", min_value=0, value=0, step=100,
                )

                col_back, col_skip, col_next = st.columns(3)
                with col_back:
                    back = st.form_submit_button("← Back", use_container_width=True)
                with col_skip:
                    skip = st.form_submit_button("Skip for now", use_container_width=True)
                with col_next:
                    submitted = st.form_submit_button("Next →", use_container_width=True)

                if back:
                    st.session_state.onboarding_step = 2
                    st.rerun()
                if skip or submitted:
                    if submitted and monthly_income > 0:
                        st.session_state.ob_income = monthly_income
                        st.session_state.ob_expenses = monthly_expenses
                        st.session_state.ob_debt = total_debt
                        st.session_state.ob_savings = current_savings
                    st.session_state.onboarding_step = 4
                    st.rerun()

    # ── Step 4 — Meet Your Coaches ───────────────────────────────────────
    elif step == 4:
        with form_col:
            st.markdown("### 🤖 Meet your AI coaches")
            st.caption("Each coach specializes in a different area. Pick who to chat with first!")

        # Show agent cards in 2 rows of 3
        agents_list = list(AGENTS.items())
        row1 = agents_list[:3]
        row2 = agents_list[3:]

        r1_cols = st.columns(3)
        for idx, (key, agent) in enumerate(row1):
            with r1_cols[idx]:
                st.markdown(f"""
                <div class="agent-card" style="border-left: 3px solid {agent['color']};">
                    <span class="agent-icon">{agent['icon']}</span>
                    <h4 style="color: {agent['color']} !important;">{agent['name']}</h4>
                    <p>{agent['tagline']}</p>
                </div>
                """, unsafe_allow_html=True)

        r2_cols = st.columns(3)
        for idx, (key, agent) in enumerate(row2):
            with r2_cols[idx]:
                st.markdown(f"""
                <div class="agent-card" style="border-left: 3px solid {agent['color']};">
                    <span class="agent-icon">{agent['icon']}</span>
                    <h4 style="color: {agent['color']} !important;">{agent['name']}</h4>
                    <p>{agent['tagline']}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")

        _, btn_col2, _ = st.columns([1, 2, 1])
        with btn_col2:
            # Back button
            if st.button("← Back", key="step4_back", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()

            st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
            if st.button("Start My Journey  🚀", key="complete_onboarding",
                         use_container_width=True):
                # Build profile from onboarding data
                name = st.session_state.get("ob_name", "Friend")
                age = st.session_state.get("ob_age", 30)
                profile = UserProfile(name=name, age=age)
                profile.user_type = "youth" if age < 18 else "adult"
                profile.goals = st.session_state.get("ob_goals", [])

                if st.session_state.get("ob_income", 0) > 0:
                    profile.monthly_income = float(st.session_state.ob_income)
                    profile.monthly_expenses = float(st.session_state.get("ob_expenses", 0))
                    profile.debt_balance = float(st.session_state.get("ob_debt", 0))
                    profile.savings_balance = float(st.session_state.get("ob_savings", 0))
                    if profile.monthly_income > 0 and profile.monthly_expenses > 0:
                        profile.completed_assessment = True

                st.session_state.profile = profile
                st.session_state.onboarded = True

                # Route to best agent based on top goal
                goals = profile.goals
                if goals:
                    first_goal = goals[0].lower()
                    if "debt" in first_goal:
                        st.session_state.active_agent = "debt_destroyer"
                    elif "invest" in first_goal:
                        st.session_state.active_agent = "invest_intel"
                    elif "budget" in first_goal or "emergency" in first_goal:
                        st.session_state.active_agent = "budget_bot"
                    elif "kid" in first_goal or "child" in first_goal:
                        st.session_state.active_agent = "kid_coach"
                    elif "save" in first_goal or "retire" in first_goal:
                        st.session_state.active_agent = "savings_sage"

                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# =========================================================================
#  POST-ONBOARDING — Redirect to Dashboard
# =========================================================================
profile = get_profile()

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">💰</div>
        <div style="font-weight: 700; font-size: 1.1rem; color: {COLORS['gold']};">Agent Richy</div>
        <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">AI Financial Coach</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"**{profile.name}** · age {profile.age}")
    mode = "🎓 Youth" if profile.is_youth() else "💼 Adult"
    premium = " · ⭐ Premium" if st.session_state.get("is_premium") else ""
    st.caption(f"{mode}{premium}")

    if profile.monthly_income > 0:
        surplus = profile.monthly_surplus()
        st.metric("Monthly Surplus", f"${surplus:,.0f}")

    st.markdown("---")

    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard", use_container_width=True)
    st.page_link("pages/2_Chat.py", label="💬 Chat with Agents", use_container_width=True)
    st.page_link("pages/3_Kids_Education.py", label="🎓 Kids Education", use_container_width=True)
    st.page_link("pages/4_My_Plan.py", label="📋 My Plan", use_container_width=True)
    st.page_link("pages/5_Financial_Profile.py", label="👤 Financial Profile", use_container_width=True)
    st.page_link("pages/6_Upgrade.py", label="⭐ Upgrade to Premium", use_container_width=True)

    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Main — personalized welcome + quick navigation ──────────────────────
st.markdown(f"""
<div style="text-align: center; padding: 1rem 0 0.5rem;">
    <h1 class="hero-title" style="font-size: 2.4rem;">Welcome back, {profile.name}!</h1>
    <p class="hero-subtitle" style="font-size: 1rem;">Your AI financial coaching dashboard is ready.</p>
</div>
""", unsafe_allow_html=True)

# Quick summary metrics
if profile.monthly_income > 0:
    from components.metric_card import render_metric_row
    surplus = profile.monthly_surplus()
    sr = profile.savings_rate()
    metrics = [
        {"label": "Monthly Income", "value": f"${profile.monthly_income:,.0f}", "icon": "💵"},
        {"label": "Monthly Expenses", "value": f"${profile.monthly_expenses:,.0f}", "icon": "🧾"},
        {"label": "Surplus", "value": f"${surplus:,.0f}",
         "delta": f"{sr:.0f}% savings rate" if sr > 0 else "",
         "delta_positive": surplus > 0, "icon": "📈"},
        {"label": "Total Debt", "value": f"${profile.total_debt():,.0f}", "icon": "💳"},
    ]
    render_metric_row(metrics)

st.markdown("---")

# Quick navigation cards
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="feature-card">
        <div class="icon">💬</div>
        <h4>Chat with AI Coaches</h4>
        <p>6 specialist agents ready to help with budgets, investing, debt, and more</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Chat.py", label="Start Chatting →", use_container_width=True)

with c2:
    st.markdown(f"""
    <div class="feature-card">
        <div class="icon">📊</div>
        <h4>Your Dashboard</h4>
        <p>Financial overview, charts, and health indicators</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Dashboard.py", label="View Dashboard →", use_container_width=True)

with c3:
    if profile.is_youth():
        st.markdown(f"""
        <div class="feature-card">
            <div class="icon">🎓</div>
            <h4>Learning Center</h4>
            <p>Video lessons, quizzes, and challenges to master money</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_Kids_Education.py", label="Start Learning →",
                     use_container_width=True)
    else:
        st.markdown(f"""
        <div class="feature-card">
            <div class="icon">📋</div>
            <h4>My Financial Plan</h4>
            <p>Budget, debt payoff, investments, goals — built by AI</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/4_My_Plan.py", label="View Plan →", use_container_width=True)

st.markdown("---")
st.caption(
    "Agent Richy is an AI-powered financial education tool. "
    "Not a licensed financial advisor. Consult professionals for personalized advice."
)
