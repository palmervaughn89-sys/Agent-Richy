"""Financial Profile — View & edit financial data."""

import streamlit as st
from styles import inject_styles
from config import COLORS
from utils.session import init_session_state, get_profile

st.set_page_config(page_title="Financial Profile — Agent Richy", page_icon="👤", layout="wide")
inject_styles()
init_session_state()

if not st.session_state.get("onboarded"):
    st.warning("Please complete onboarding first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile = get_profile()

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align: center; padding: 1rem 0 1.5rem;">
    <h1 style="margin: 0;">
        <span style="color: {COLORS['gold']};">👤</span>
        Financial Profile
    </h1>
    <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0 0;">
        Review and update your financial information. Changes are saved automatically.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Personal Info ────────────────────────────────────────────────────────
st.markdown("### 📝 Personal Information")
pi1, pi2, pi3 = st.columns(3)
with pi1:
    new_name = st.text_input("Name", value=profile.name, key="prof_name")
    if new_name != profile.name:
        profile.name = new_name
with pi2:
    new_age = st.number_input("Age", value=profile.age, min_value=5, max_value=120, key="prof_age")
    if new_age != profile.age:
        profile.age = new_age
with pi3:
    emp_options = ["employed", "self-employed", "unemployed", "student", "retired"]
    current_emp = getattr(profile, "employment_status", "employed")
    if current_emp not in emp_options:
        current_emp = "employed"
    emp = st.selectbox("Employment Status", emp_options,
                       index=emp_options.index(current_emp), key="prof_emp")
    profile.employment_status = emp

# ── Income & Expenses ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💰 Income & Expenses")

ie1, ie2 = st.columns(2)
with ie1:
    new_income = st.number_input(
        "Monthly Income ($)",
        value=float(profile.monthly_income),
        min_value=0.0, step=100.0, format="%.0f",
        key="prof_income",
    )
    profile.monthly_income = new_income

with ie2:
    new_expenses = st.number_input(
        "Monthly Expenses ($)",
        value=float(profile.monthly_expenses),
        min_value=0.0, step=100.0, format="%.0f",
        key="prof_expenses",
    )
    profile.monthly_expenses = new_expenses

if profile.monthly_income > 0:
    surplus = profile.monthly_income - profile.monthly_expenses
    rate = (surplus / profile.monthly_income * 100) if profile.monthly_income > 0 else 0
    sc1, sc2 = st.columns(2)
    with sc1:
        color = COLORS["green"] if surplus >= 0 else COLORS["red"]
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border-left: 3px solid {color};
                    padding: 0.8rem 1rem; border-radius: 0 10px 10px 0;">
            <strong>Monthly Surplus:</strong> ${surplus:,.0f}
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border-left: 3px solid {COLORS['blue']};
                    padding: 0.8rem 1rem; border-radius: 0 10px 10px 0;">
            <strong>Savings Rate:</strong> {rate:.1f}%
        </div>
        """, unsafe_allow_html=True)

# ── Savings ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🏦 Savings")

sv1, sv2 = st.columns(2)
with sv1:
    new_savings = st.number_input(
        "Total Savings ($)",
        value=float(getattr(profile, "savings_balance", 0)),
        min_value=0.0, step=500.0, format="%.0f",
        key="prof_savings",
    )
    profile.savings_balance = new_savings
with sv2:
    new_ef = st.number_input(
        "Emergency Fund ($)",
        value=float(getattr(profile, "emergency_fund", 0)),
        min_value=0.0, step=500.0, format="%.0f",
        key="prof_ef",
    )
    profile.emergency_fund = new_ef

# ── Debts ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💳 Debts")

if profile.debts:
    for name, balance in list(profile.debts.items()):
        rate = profile.debt_interest_rates.get(name, 0)
        dc1, dc2, dc3, dc4 = st.columns([2, 1.5, 1.5, 0.5])
        with dc1:
            st.text_input("Debt name", value=name, key=f"dname_{name}", disabled=True)
        with dc2:
            new_bal = st.number_input(
                "Balance", value=float(balance), min_value=0.0, step=100.0,
                format="%.0f", key=f"dbal_{name}",
            )
            profile.debts[name] = new_bal
        with dc3:
            new_rate = st.number_input(
                "APR %", value=float(rate * 100), min_value=0.0, max_value=100.0,
                step=0.1, format="%.1f", key=f"drate_{name}",
            )
            profile.debt_interest_rates[name] = new_rate / 100
        with dc4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"ddel_{name}"):
                del profile.debts[name]
                profile.debt_interest_rates.pop(name, None)
                st.rerun()
else:
    st.info("No debts recorded. Tell your coach about debts in chat, or add them below.")

# Add new debt
with st.expander("➕ Add a debt"):
    nd1, nd2, nd3 = st.columns(3)
    with nd1:
        new_debt_name = st.text_input("Name (e.g., Credit Card)", key="new_debt_name")
    with nd2:
        new_debt_bal = st.number_input("Balance ($)", min_value=0.0, step=100.0,
                                       format="%.0f", key="new_debt_bal")
    with nd3:
        new_debt_rate = st.number_input("APR %", min_value=0.0, max_value=100.0,
                                        step=0.1, format="%.1f", key="new_debt_rate")
    if st.button("Add Debt", key="add_debt_btn"):
        if new_debt_name and new_debt_bal > 0:
            profile.debts[new_debt_name] = new_debt_bal
            profile.debt_interest_rates[new_debt_name] = new_debt_rate / 100
            st.success(f"Added {new_debt_name}!")
            st.rerun()
        else:
            st.warning("Please enter a name and balance.")

# ── Goals ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎯 Goals")

if profile.goals:
    for i, goal in enumerate(profile.goals):
        gc1, gc2 = st.columns([5, 0.5])
        with gc1:
            st.markdown(f"""
            <div style="background: {COLORS['navy_card']}; border-left: 3px solid {COLORS['gold']};
                        padding: 0.6rem 1rem; border-radius: 0 10px 10px 0;">
                {goal}
            </div>
            """, unsafe_allow_html=True)
        with gc2:
            if st.button("🗑️", key=f"gdel_{i}"):
                profile.goals.pop(i)
                st.rerun()
else:
    st.info("No goals set yet. Share your goals in chat or add them below.")

new_goal = st.text_input("Add a goal", placeholder="e.g., Save $10,000 emergency fund", key="new_goal")
if st.button("Add Goal", key="add_goal_btn"):
    if new_goal:
        profile.goals.append(new_goal)
        st.success(f"Added: {new_goal}")
        st.rerun()

# ── Credit Score ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Credit Score")

cs = getattr(profile, "credit_score", None) or 0
new_cs = st.number_input(
    "Credit Score (300–850)", value=int(cs),
    min_value=0, max_value=850, step=10, key="prof_cs",
)
if new_cs > 0:
    profile.credit_score = new_cs
    pct = min(new_cs / 850, 1.0)
    st.progress(pct)
    if new_cs >= 750:
        st.success(f"Excellent ({new_cs})")
    elif new_cs >= 670:
        st.info(f"Good ({new_cs})")
    elif new_cs >= 580:
        st.warning(f"Fair ({new_cs})")
    else:
        st.error(f"Needs improvement ({new_cs})")

# ── Risk Tolerance ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ⚖️ Investment Risk Tolerance")

risk_options = ["low", "moderate", "high", "aggressive"]
current_risk = getattr(profile, "risk_tolerance", "moderate")
if current_risk not in risk_options:
    current_risk = "moderate"
risk = st.select_slider(
    "How much risk are you comfortable with?",
    options=risk_options,
    value=current_risk,
    key="prof_risk",
)
profile.risk_tolerance = risk

risk_desc = {
    "low": "Conservative — bonds, savings, low-volatility. Best for short-term goals.",
    "moderate": "Balanced — mix of stocks and bonds. Good for 5+ year goals.",
    "high": "Growth-focused — mostly stocks. Best for 10+ year horizons.",
    "aggressive": "Maximum growth — heavy equities, some crypto/alternatives. Long-term only.",
}
st.caption(risk_desc.get(risk, ""))

# ── Summary Footer ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="background: {COLORS['navy_card']}; border-radius: 16px; padding: 1.5rem;
            text-align: center; border: 1px solid {COLORS['border']};">
    <p style="color: {COLORS['text_secondary']}; margin: 0;">
        Your profile updates are saved in this session. Chat with your coach to get
        personalized advice based on your data.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/2_Chat.py", label="💬 Chat with Coaches", use_container_width=True)
with col2:
    st.page_link("pages/4_My_Plan.py", label="📋 View My Plan", use_container_width=True)
