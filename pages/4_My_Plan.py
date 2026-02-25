"""My Plan — AI-generated financial plan dashboard."""

import math
import streamlit as st
import plotly.graph_objects as go
from styles import inject_styles
from config import COLORS, PLOTLY_LAYOUT
from utils.session import init_session_state, get_profile
from utils.calculations import (
    debt_payoff_schedule, compound_growth, estimate_federal_tax,
    savings_rate_pct, debt_to_income, emergency_fund_months,
)
from components.metric_card import render_metric_card, render_metric_row

st.set_page_config(page_title="My Plan — Agent Richy", page_icon="📋", layout="wide")
inject_styles()
init_session_state()

if not st.session_state.get("onboarded"):
    st.warning("Please complete onboarding first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile = get_profile()
plan = st.session_state.get("financial_plan", {})
plan_generated = st.session_state.get("plan_generated", False)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align: center; padding: 1rem 0 0.5rem;">
    <h1 style="margin: 0;">
        <span style="color: {COLORS['gold']};">📋</span>
        {profile.name}'s Financial Plan
    </h1>
    <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0 0;">
        {"Built from your conversations — keep chatting to refine it!" if plan_generated
         else "Chat with your coaches to populate this plan."}
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  EMPTY STATE
# ══════════════════════════════════════════════════════════════════════════
income = profile.monthly_income
expenses = profile.monthly_expenses
surplus = income - expenses if income > 0 else 0

if not plan_generated and income == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['border']};
                    border-radius: 20px; padding: 3rem 2rem; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">💬</div>
            <h2 style="color: {COLORS['gold']}; margin: 0 0 0.5rem;">Your plan starts with a conversation</h2>
            <p style="color: {COLORS['text_secondary']}; margin: 0 0 1.5rem; line-height: 1.6;">
                Tell your coaches about your income, expenses, debts, and goals.<br>
                They'll build your complete financial plan right here.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Chat.py", label="💬 Start Chatting →", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### What your plan will include:")
    p1, p2, p3, p4 = st.columns(4)
    cards = [
        ("📊", "Budget", "50/30/20 breakdown based on YOUR income"),
        ("💳", "Debt Strategy", "Payoff timeline with avalanche/snowball"),
        ("📈", "Investments", "Portfolio recommendations for your risk level"),
        ("🎯", "Goals", "Timeline and savings plan for each goal"),
    ]
    for col_obj, (icon, title, desc) in zip([p1, p2, p3, p4], cards):
        with col_obj:
            st.markdown(f"""
            <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['border']};
                        border-radius: 14px; padding: 1.2rem; text-align: center; min-height: 140px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-weight: 700; color: {COLORS['white']}; margin-bottom: 0.3rem;">{title}</div>
                <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════
#  PLAN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════

# ── Top metrics ──────────────────────────────────────────────────────────
sr = savings_rate_pct(income, expenses) if income > 0 else 0
dti = debt_to_income(profile.total_debt(), income) if income > 0 and hasattr(profile, 'total_debt') else 0
ef_months = emergency_fund_months(profile.emergency_fund, expenses) if expenses > 0 else 0

metrics = [
    {"label": "Monthly Income", "value": f"${income:,.0f}" if income else "—",
     "icon": "💰", "color": COLORS["green"]},
    {"label": "Monthly Expenses", "value": f"${expenses:,.0f}" if expenses else "—",
     "icon": "💸", "color": COLORS["red"]},
    {"label": "Monthly Surplus", "value": f"${surplus:,.0f}",
     "icon": "📊", "color": COLORS["blue"],
     "delta": f"{sr:.0f}% savings rate" if income > 0 else None},
    {"label": "Emergency Fund", "value": f"${profile.emergency_fund:,.0f}" if profile.emergency_fund else "—",
     "icon": "🛡️", "color": COLORS["gold"],
     "delta": f"{ef_months:.1f} months" if ef_months > 0 else None},
]
render_metric_row(metrics)

# ── Budget Section ───────────────────────────────────────────────────────
if income > 0:
    st.markdown("---")
    st.markdown(f"### 📊 Budget Plan")

    budget = plan.get("budget", {})
    needs = budget.get("needs", income * 0.50)
    wants = budget.get("wants", income * 0.30)
    save_amt = budget.get("savings", income * 0.20)

    bc1, bc2 = st.columns([1, 1])
    with bc1:
        fig = go.Figure(data=[go.Pie(
            labels=["Needs", "Wants", "Savings & Investing"],
            values=[needs, wants, save_amt],
            marker_colors=[COLORS["red"], COLORS["gold"], COLORS["green"]],
            hole=0.5,
            textinfo="label+percent",
            textfont=dict(color="white", size=13),
        )])
        layout = {**PLOTLY_LAYOUT, "height": 360, "title": "Recommended 50/30/20 Split"}
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    with bc2:
        st.markdown(f"""
| Category | Amount | % of Income |
|---|---|---|
| **Needs** (rent, food, bills) | ${needs:,.0f} | {needs/income*100:.0f}% |
| **Wants** (fun, dining, shopping) | ${wants:,.0f} | {wants/income*100:.0f}% |
| **Savings & Investing** | ${save_amt:,.0f} | {save_amt/income*100:.0f}% |
| **Total** | **${income:,.0f}** | **100%** |
        """)

        if expenses > 0:
            actual_save = income - expenses
            if actual_save < save_amt:
                diff = save_amt - actual_save
                st.warning(f"⚠️ Currently saving ${actual_save:,.0f}/mo — ${diff:,.0f}/mo short of target.")
            else:
                st.success(f"✅ Saving ${actual_save:,.0f}/mo — on target!")


# ── Debt Section ─────────────────────────────────────────────────────────
if profile.debts:
    st.markdown("---")
    st.markdown(f"### 💳 Debt Payoff Strategy")

    total_debt = profile.total_debt()
    st.metric("Total Debt", f"${total_debt:,.0f}")

    sorted_debts = sorted(
        profile.debts.items(),
        key=lambda x: profile.debt_interest_rates.get(x[0], 0),
        reverse=True,
    )

    st.markdown("#### Avalanche Order (highest interest first)")
    for i, (name, balance) in enumerate(sorted_debts, 1):
        rate = profile.debt_interest_rates.get(name, 0)
        min_pay = max(balance * 0.02, 25)
        dc1, dc2, dc3, dc4 = st.columns(4)
        with dc1:
            st.markdown(f"**{i}. {name}**")
        with dc2:
            st.markdown(f"${balance:,.0f}")
        with dc3:
            st.markdown(f"{rate*100:.1f}% APR")
        with dc4:
            st.markdown(f"Min: ${min_pay:,.0f}/mo")

    # Payoff projection
    if sorted_debts and surplus > 0:
        first_name, first_bal = sorted_debts[0]
        first_rate = profile.debt_interest_rates.get(first_name, 0)
        extra_payment = surplus * 0.5
        min_pay = max(first_bal * 0.02, 25)
        total_pay = min_pay + extra_payment

        if first_rate > 0 and total_pay > first_bal * (first_rate / 12):
            schedule = debt_payoff_schedule(first_bal, first_rate, total_pay)
            if schedule:
                months_list = [s["month"] for s in schedule]
                balances = [s["remaining"] for s in schedule]
                total_interest = sum(s["interest"] for s in schedule)
                yrs = len(schedule) // 12
                mos = len(schedule) % 12

                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("Payoff Time", f"{yrs}yr {mos}mo")
                with mc2:
                    st.metric("Total Interest", f"${total_interest:,.0f}")
                with mc3:
                    st.metric("Monthly Payment", f"${total_pay:,.0f}")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months_list, y=balances,
                    fill="tozeroy", name="Remaining Balance",
                    line=dict(color=COLORS["red"]),
                    fillcolor=f"{COLORS['red']}40",
                ))
                layout = {
                    **PLOTLY_LAYOUT, "height": 350,
                    "title": f"Payoff Timeline — {first_name}",
                    "xaxis_title": "Months", "yaxis_title": "Balance ($)",
                }
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True)


# ── Investment Section ───────────────────────────────────────────────────
if income > 0 and (not profile.debts or profile.total_debt() < income * 6):
    st.markdown("---")
    st.markdown("### 📈 Investment Recommendations")

    risk_level = plan.get("risk_level", getattr(profile, "risk_tolerance", "moderate"))
    invest_amount = max(0, surplus * 0.3) if surplus > 0 else 0

    if invest_amount <= 0:
        st.info("💡 Build surplus first. Investment projections will appear once you have extra monthly income.")
    else:
        st.markdown(f"**Risk Level:** {risk_level.title()} · **Monthly Investment:** ${invest_amount:,.0f}")

        st.markdown("""
| Allocation | What | Why |
|---|---|---|
| **60%** | Total Market Index (VTI/VXUS) | Broad diversification, low fees |
| **20%** | Bond Index (BND/BNDX) | Stability, income |
| **10%** | Growth ETF (QQQ/VGT) | Higher growth potential |
| **10%** | REIT / Alternative | Real estate exposure |
        """)

        rate_map = {"low": 0.05, "medium": 0.07, "moderate": 0.07,
                    "high": 0.10, "very high": 0.12, "aggressive": 0.12}
        annual_rate = rate_map.get(risk_level.lower(), 0.07)
        mr = annual_rate / 12

        years_list = [1, 5, 10, 15, 20, 25, 30]
        balances_proj = []
        contributed_proj = []
        for yr in years_list:
            b = compound_growth(invest_amount, annual_rate, yr * 12)
            balances_proj.append(b)
            contributed_proj.append(invest_amount * 12 * yr)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"{y}yr" for y in years_list], y=contributed_proj,
            name="Contributed", marker_color=COLORS["gray"],
        ))
        fig.add_trace(go.Bar(
            x=[f"{y}yr" for y in years_list],
            y=[b - c for b, c in zip(balances_proj, contributed_proj)],
            name="Growth", marker_color=COLORS["green"],
        ))
        layout = {
            **PLOTLY_LAYOUT, "height": 350, "barmode": "stack",
            "title": f"${invest_amount:,.0f}/mo at ~{annual_rate*100:.0f}% return",
            "yaxis_title": "Balance ($)",
        }
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"**30-year projection: ${balances_proj[-1]:,.0f}** "
                    f"(contributed: ${contributed_proj[-1]:,.0f})")
        st.caption("⚠️ Projections are estimates. Past performance ≠ future results.")


# ── Goals ────────────────────────────────────────────────────────────────
if profile.goals:
    st.markdown("---")
    st.markdown("### 🎯 Your Goals")
    for goal in profile.goals:
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border-left: 3px solid {COLORS['gold']};
                    padding: 0.8rem 1rem; border-radius: 0 10px 10px 0; margin-bottom: 0.5rem;">
            ✅ {goal}
        </div>
        """, unsafe_allow_html=True)


# ── Recommendations ──────────────────────────────────────────────────────
recs = plan.get("recommendations", [])
if recs:
    st.markdown("---")
    st.markdown("### 🤖 Action Plan")
    for i, rec in enumerate(recs, 1):
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border-left: 3px solid {COLORS['blue']};
                    padding: 0.8rem 1rem; border-radius: 0 10px 10px 0; margin-bottom: 0.5rem;">
            <strong>{i}.</strong> {rec}
        </div>
        """, unsafe_allow_html=True)


# ── Financial Health ─────────────────────────────────────────────────────
if income > 0:
    st.markdown("---")
    st.markdown("### 🏥 Financial Health")
    hi1, hi2, hi3, hi4 = st.columns(4)

    with hi1:
        st.markdown("**Emergency Fund**")
        st.progress(min(ef_months / 6, 1.0))
        st.caption(f"{ef_months:.1f} / 6 months")

    with hi2:
        st.markdown("**Savings Rate**")
        st.progress(min(sr / 20, 1.0))
        st.caption(f"{sr:.0f}% / 20% target")

    with hi3:
        st.markdown("**Debt-to-Income**")
        dti_val = debt_to_income(profile.total_debt(), income) if hasattr(profile, 'total_debt') else 0
        st.progress(min(dti_val / 50, 1.0))
        color = "🟢" if dti_val < 20 else "🟡" if dti_val < 36 else "🔴"
        st.caption(f"{dti_val:.0f}% {color}")

    with hi4:
        st.markdown("**Credit Score**")
        cs = getattr(profile, "credit_score", None)
        if cs:
            st.progress(min(cs / 850, 1.0))
            if cs >= 750:
                st.caption(f"{cs} — Excellent ✅")
            elif cs >= 670:
                st.caption(f"{cs} — Good 👍")
            else:
                st.caption(f"{cs} — Needs work ⚠️")
        else:
            st.caption("Not provided yet")


# ── Tax Estimate ─────────────────────────────────────────────────────────
if income > 0:
    st.markdown("---")
    st.markdown("### 🧾 Tax Estimate")
    annual_income = income * 12
    result = estimate_federal_tax(annual_income, "single")

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.metric("Annual Gross", f"${annual_income:,.0f}")
    with tc2:
        st.metric("Take-Home (Monthly)", f"${result['take_home']/12:,.0f}")
    with tc3:
        st.metric("Effective Tax Rate", f"{result['effective_rate']:.1f}%")

    with st.expander("See tax breakdown"):
        st.markdown(f"""
| Item | Amount |
|---|---|
| Gross Income | ${result['gross_income']:,.0f} |
| Standard Deduction | -${result['standard_deduction']:,.0f} |
| Taxable Income | ${result['taxable_income']:,.0f} |
| Federal Tax | ${result['federal_tax']:,.0f} |
| FICA | ${result['fica_tax']:,.0f} |
| **Total Tax** | **${result['total_tax']:,.0f}** |
| **Take-Home** | **${result['take_home']:,.0f}** |
        """)


# ── Bottom CTA ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="background: {COLORS['navy_card']}; border-radius: 16px; padding: 1.5rem;
            text-align: center; border: 1px solid {COLORS['border']};">
    <h3 style="color: {COLORS['white']}; margin: 0 0 0.5rem;">Need to update your plan?</h3>
    <p style="color: {COLORS['text_secondary']}; margin: 0 0 1rem;">
        Go back to chat and tell your coach about any changes in your situation.
    </p>
</div>
""", unsafe_allow_html=True)
st.page_link("pages/2_Chat.py", label="💬 Talk to Your Coaches →", use_container_width=True)
