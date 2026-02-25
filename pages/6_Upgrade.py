"""Upgrade — Premium vs Free tier comparison."""

import streamlit as st
from styles import inject_styles
from config import COLORS, FREE_MESSAGE_LIMIT, FREE_VIDEO_MODULES, FREE_VIDEO_LESSONS, KIDS_MODULES
from utils.session import init_session_state

st.set_page_config(page_title="Upgrade — Agent Richy", page_icon="⭐", layout="wide")
inject_styles()
init_session_state()

total_videos = sum(len(m["lessons"]) for m in KIDS_MODULES)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0 1.5rem;">
    <h1 style="margin: 0; font-size: 2.2rem;">
        <span style="color: {COLORS['gold']};">⭐</span>
        Upgrade to Premium
    </h1>
    <p style="color: {COLORS['text_secondary']}; font-size: 1.1rem; margin: 0.5rem 0 0;">
        Unlock the full power of AI-driven financial coaching
    </p>
</div>
""", unsafe_allow_html=True)

is_premium = st.session_state.get("is_premium", False)

if is_premium:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['gold']}30, {COLORS['navy_card']});
                border: 2px solid {COLORS['gold']}; border-radius: 20px; padding: 2rem;
                text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">👑</div>
        <h2 style="color: {COLORS['gold']}; margin: 0 0 0.5rem;">You're a Premium Member!</h2>
        <p style="color: {COLORS['text_secondary']}; margin: 0;">
            Enjoy unlimited access to all features.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Comparison Table ─────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

free_col, premium_col = st.columns(2)

with free_col:
    border = f"1px solid {COLORS['border']}"
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border: {border};
                border-radius: 20px; padding: 2rem; min-height: 600px;">
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 1.1rem; color: {COLORS['text_secondary']};">Free</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: {COLORS['white']};">$0</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.9rem;">forever</div>
        </div>
        <hr style="border-color: {COLORS['border']}; margin: 1rem 0;">
        <div style="font-size: 0.95rem; line-height: 2.2;">
            ✅ {FREE_MESSAGE_LIMIT} AI messages per day<br>
            ✅ Coach Richy (general advisor)<br>
            ✅ {FREE_VIDEO_MODULES} education module ({FREE_VIDEO_LESSONS} lessons)<br>
            ✅ Basic financial dashboard<br>
            ✅ Financial profile editor<br>
            ❌ Specialist agents (Budget, Debt, etc.)<br>
            ❌ Full education library ({len(KIDS_MODULES)} modules)<br>
            ❌ Advanced tax estimates<br>
            ❌ Investment portfolio builder<br>
            ❌ Debt payoff projections<br>
            ❌ Priority support
        </div>
    </div>
    """, unsafe_allow_html=True)

with premium_col:
    border = f"2px solid {COLORS['gold']}"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['gold']}10, {COLORS['navy_card']});
                border: {border}; border-radius: 20px; padding: 2rem; min-height: 600px;
                position: relative;">
        <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
                    background: {COLORS['gold']}; color: {COLORS['navy']}; font-weight: 700;
                    padding: 4px 16px; border-radius: 20px; font-size: 0.8rem;">
            RECOMMENDED
        </div>
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 1.1rem; color: {COLORS['gold']};">Premium</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: {COLORS['white']};">$10</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.9rem;">per month</div>
        </div>
        <hr style="border-color: {COLORS['gold']}40; margin: 1rem 0;">
        <div style="font-size: 0.95rem; line-height: 2.2;">
            ✅ <strong>Unlimited</strong> AI messages<br>
            ✅ <strong>All 6 specialist agents</strong><br>
            ✅ <strong>All {len(KIDS_MODULES)} education modules</strong> ({total_videos} lessons)<br>
            ✅ <strong>Full financial dashboard</strong> with charts<br>
            ✅ Financial profile editor<br>
            ✅ Budget Bot — zero-based budgeting<br>
            ✅ Debt Destroyer — avalanche/snowball plans<br>
            ✅ Investment Intel — portfolio builder<br>
            ✅ Tax estimates & projections<br>
            ✅ Savings challenges & streaks<br>
            ✅ Priority support
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CTA ──────────────────────────────────────────────────────────────────
if not is_premium:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.95rem;">
                🔒 Try Premium risk-free • Cancel anytime
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⭐ Activate Premium", use_container_width=True, type="primary"):
            st.session_state.is_premium = True
            st.balloons()
            st.success("🎉 Welcome to Premium! You now have unlimited access to all features.")
            st.rerun()

        st.caption("*This is a demo — no payment required. Toggle premium on/off below.*")

# ── Demo toggle ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔧 Demo Controls")
st.caption("For testing purposes — toggle premium mode on/off.")

current_status = "Premium ⭐" if is_premium else "Free"
st.markdown(f"**Current tier:** {current_status}")

toggle = st.toggle("Premium Mode", value=is_premium, key="premium_toggle")
if toggle != is_premium:
    st.session_state.is_premium = toggle
    st.rerun()

if is_premium:
    st.markdown(f"""
    <div style="background: {COLORS['gold']}20; border: 1px solid {COLORS['gold']}40;
                border-radius: 10px; padding: 0.8rem; margin-top: 0.5rem;">
        <strong style="color: {COLORS['gold']};">👑 Premium Active</strong>
        <span style="color: {COLORS['text_secondary']};">— All features unlocked</span>
    </div>
    """, unsafe_allow_html=True)

# ── Feature highlights ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ✨ What Premium Members Love")

features = [
    ("🤖", "6 Specialist AI Agents",
     "Get targeted advice from Budget Bot, Debt Destroyer, Invest Intel, Savings Sage, and Kid Coach."),
    ("📊", "Advanced Dashboard",
     "Interactive Plotly charts showing your budget, debt payoff projections, and investment growth."),
    ("🎓", f"Full Education Library",
     f"Access all {len(KIDS_MODULES)} modules with {total_videos} video lessons, quizzes, and achievement badges."),
    ("💬", "Unlimited AI Chat",
     "No daily limits — chat as much as you need. Your coaches learn from every conversation."),
]

for i in range(0, len(features), 2):
    cols = st.columns(2)
    for j, col in enumerate(cols):
        if i + j < len(features):
            icon, title, desc = features[i + j]
            with col:
                st.markdown(f"""
                <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 14px; padding: 1.2rem; min-height: 120px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                    <div style="font-weight: 700; color: {COLORS['white']}; margin-bottom: 0.3rem;">
                        {title}
                    </div>
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.page_link("pages/2_Chat.py", label="💬 Start Chatting", use_container_width=True)
