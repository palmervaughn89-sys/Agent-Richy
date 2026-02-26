"""Dashboard — Professional financial overview with charts and metrics."""

import streamlit as st
import plotly.graph_objects as go
from styles import inject_styles
from config import COLORS, PLOTLY_LAYOUT, PLOTLY_COLORS, AGENTS
from utils.session import init_session_state, get_profile
from utils.calculations import (
    compound_growth, debt_payoff_schedule, savings_rate_pct,
    emergency_fund_months,
)
from components.metric_card import render_metric_row

st.set_page_config(page_title="Dashboard — Agent Richy", page_icon="📊", layout="wide")
inject_styles()
init_session_state()

# ── Session guard ────────────────────────────────────────────────────────
if not st.session_state.get("onboarded"):
    st.warning("Please complete onboarding first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile = get_profile()
plan = st.session_state.get("financial_plan", {})

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2rem;">💰</div>
        <div style="font-weight: 700; color: {COLORS['gold']};">Agent Richy</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**{profile.name}** · {profile.age}yr")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/2_Chat.py", label="💬 Chat", use_container_width=True)
    st.page_link("pages/3_Kids_Education.py", label="🎓 Kids", use_container_width=True)
    st.page_link("pages/4_My_Plan.py", label="📋 Plan", use_container_width=True)
    st.page_link("pages/5_Financial_Profile.py", label="👤 Profile", use_container_width=True)
    st.page_link("pages/6_Upgrade.py", label="⭐ Premium", use_container_width=True)

# ── Header ───────────────────────────────────────────────────────────────
st.markdown(f"## 📊 {profile.name}'s Financial Dashboard")
st.caption("Real-time overview of your financial health. Keep chatting with agents to update your data.")

# ══════════════════════════════════════════════════════════════════════════
#  TOP SECTION — Key Metrics
# ══════════════════════════════════════════════════════════════════════════
income = profile.monthly_income
expenses = profile.monthly_expenses
surplus = income - expenses if income > 0 else 0
sr = savings_rate_pct(income, expenses)
ef_months = emergency_fund_months(
    profile.emergency_fund or profile.savings_balance, expenses
)
total_debt = profile.total_debt()

metrics = []
metrics.append({
    "label": "Net Worth (Est.)",
    "value": f"${(profile.savings_balance + profile.emergency_fund - total_debt):,.0f}"
             if income > 0 else "—",
    "icon": "💎",
    "delta": "",
    "delta_positive": True,
})
metrics.append({
    "label": "Monthly Savings Rate",
    "value": f"{sr:.1f}%" if income > 0 else "—",
    "icon": "📈",
    "delta": "Target: 20%",
    "delta_positive": sr >= 20,
})
metrics.append({
    "label": "Debt-to-Income",
    "value": f"{profile.debt_to_income_ratio():.0f}%"
             if income > 0 and total_debt > 0 else "0%",
    "icon": "⚖️",
    "delta": "< 36% is healthy",
    "delta_positive": profile.debt_to_income_ratio() < 36,
})
metrics.append({
    "label": "Emergency Fund",
    "value": f"{ef_months:.1f} months" if ef_months > 0 else "—",
    "icon": "🛡️",
    "delta": "Target: 6 months",
    "delta_positive": ef_months >= 3,
})

render_metric_row(metrics)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════
#  MIDDLE SECTION — Charts
# ══════════════════════════════════════════════════════════════════════════
if income > 0:
    chart1, chart2 = st.columns(2)

    # ── Spending Breakdown (Donut) ────────────────────────────────────────
    with chart1:
        st.markdown("### 📊 Budget Breakdown")
        budget = plan.get("budget", {})
        needs = budget.get("needs", income * 0.50)
        wants = budget.get("wants", income * 0.30)
        save_amt = budget.get("savings", income * 0.20)

        fig = go.Figure(data=[go.Pie(
            labels=["Needs", "Wants", "Savings & Investing"],
            values=[needs, wants, save_amt],
            marker_colors=[COLORS["blue"], COLORS["gold"], COLORS["green"]],
            hole=0.55,
            textinfo="label+percent",
            textfont=dict(color="white", size=13),
        )])
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Income vs Expenses (Bar) ─────────────────────────────────────────
    with chart2:
        st.markdown("### 💵 Income vs Expenses")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=["Income", "Expenses", "Surplus"],
            y=[income, expenses, max(0, surplus)],
            marker_color=[COLORS["green"], COLORS["red"], COLORS["blue"]],
            text=[f"${income:,.0f}", f"${expenses:,.0f}", f"${max(0,surplus):,.0f}"],
            textposition="outside",
            textfont=dict(color="white"),
        ))
        fig2.update_layout(
            **PLOTLY_LAYOUT,
            height=350,
            showlegend=False,
            yaxis=dict(title="$/month", gridcolor=COLORS["border"]),
            xaxis=dict(gridcolor=COLORS["border"]),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    chart3, chart4 = st.columns(2)

    # ── Debt Payoff Projection ───────────────────────────────────────────
    with chart3:
        if profile.debts and surplus > 0:
            st.markdown("### 💳 Debt Payoff Projection")
            # Use highest-interest debt
            sorted_debts = sorted(
                profile.debts.items(),
                key=lambda x: profile.debt_interest_rates.get(x[0], 0),
                reverse=True,
            )
            first_name, first_bal = sorted_debts[0]
            first_rate = profile.debt_interest_rates.get(first_name, 0.18)
            min_pay = max(first_bal * 0.02, 25)
            total_pay = min_pay + (surplus * 0.5)

            if total_pay > first_bal * (first_rate / 12) and first_rate > 0:
                schedule = debt_payoff_schedule(first_bal, first_rate, total_pay)
                if schedule:
                    months_list = [s["month"] for s in schedule]
                    balances = [s["remaining"] for s in schedule]
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(
                        x=months_list, y=balances,
                        fill="tozeroy", name="Remaining Balance",
                        line=dict(color=COLORS["red"]),
                        fillcolor=f"rgba(239,68,68,0.2)",
                    ))
                    fig3.update_layout(
                        **PLOTLY_LAYOUT,
                        height=350,
                        xaxis_title="Months",
                        yaxis_title="Balance ($)",
                        yaxis=dict(gridcolor=COLORS["border"]),
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                    total_months = len(schedule)
                    st.caption(
                        f"**{first_name}** — payoff in {total_months // 12}yr "
                        f"{total_months % 12}mo at ${total_pay:,.0f}/mo"
                    )
            else:
                st.info("Increase your payments to start reducing the balance.")
        else:
            st.markdown("### 💳 Debt Status")
            if not profile.debts:
                st.success("🎉 No debt recorded — keep it that way!")
            else:
                st.info("Build surplus through budgeting to start debt payoff projections.")

    # ── Savings Growth Projection ────────────────────────────────────────
    with chart4:
        st.markdown("### 📈 Savings Growth Projection")
        invest_amt = max(0, surplus * 0.3) if surplus > 0 else 100
        rate_map = {"low": 0.05, "medium": 0.07, "moderate": 0.07,
                    "high": 0.10, "very high": 0.12}
        annual_rate = rate_map.get(profile.risk_tolerance.lower(), 0.07)

        years = [1, 5, 10, 15, 20, 25, 30]
        balances = [compound_growth(invest_amt, annual_rate, y) for y in years]
        contributed = [invest_amt * 12 * y for y in years]

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=[f"{y}yr" for y in years],
            y=contributed,
            name="Contributed",
            marker_color=COLORS["text_muted"],
        ))
        fig4.add_trace(go.Bar(
            x=[f"{y}yr" for y in years],
            y=[b - c for b, c in zip(balances, contributed)],
            name="Growth",
            marker_color=COLORS["green"],
        ))
        fig4.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            height=350,
            yaxis_title="Balance ($)",
            yaxis=dict(gridcolor=COLORS["border"]),
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.caption(f"${invest_amt:,.0f}/mo at ~{annual_rate*100:.0f}% → **${balances[-1]:,.0f}** in 30yr")

else:
    # No financial data yet
    st.markdown("---")
    _, ctr, _ = st.columns([1, 2, 1])
    with ctr:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 0; color: {COLORS['text_muted']};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h3>Your dashboard will fill up as you share your financial info</h3>
            <p>Start chatting with an AI coach to see your metrics, charts, and projections here.</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Chat.py", label="💬 Start Chatting →", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
#  BOTTOM SECTION — Quick Actions & Goals
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

qa1, qa2, qa3 = st.columns(3)
with qa1:
    st.markdown(f"""
    <div class="agent-card" style="border-left: 3px solid {COLORS['gold']};">
        <span class="agent-icon">💬</span>
        <h4 style="color: {COLORS['gold']} !important;">Chat with a Coach</h4>
        <p>Get personalized advice from specialist AI agents</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Chat.py", label="Open Chat →", use_container_width=True)

with qa2:
    st.markdown(f"""
    <div class="agent-card" style="border-left: 3px solid {COLORS['blue']};">
        <span class="agent-icon">🎓</span>
        <h4 style="color: {COLORS['blue']} !important;">Kids Corner</h4>
        <p>Video lessons and quizzes for financial literacy</p>
    </div>
    """, unsafe_allow_html=True)
    completed_vids = len(st.session_state.get("completed_videos", set()))
    if completed_vids > 0:
        st.caption(f"✅ {completed_vids} lessons completed")
    st.page_link("pages/3_Kids_Education.py", label="Learn →", use_container_width=True)

with qa3:
    st.markdown(f"""
    <div class="agent-card" style="border-left: 3px solid {COLORS['green']};">
        <span class="agent-icon">🎯</span>
        <h4 style="color: {COLORS['green']} !important;">My Goals</h4>
        <p>Track progress on your financial goals</p>
    </div>
    """, unsafe_allow_html=True)
    if profile.goals:
        for g in profile.goals[:3]:
            st.caption(f"• {g}")
    st.page_link("pages/4_My_Plan.py", label="View Plan →", use_container_width=True)

# ── Financial Health Indicators ──────────────────────────────────────────
if profile.completed_assessment:
    st.markdown("---")
    st.markdown("### 🏥 Financial Health")

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown("**Emergency Fund**")
        ef = emergency_fund_months(
            profile.emergency_fund or profile.savings_balance, expenses
        )
        st.progress(min(ef / 6, 1.0))
        st.caption(f"{ef:.1f} / 6 months")

    with h2:
        st.markdown("**Savings Rate**")
        st.progress(min(sr / 20, 1.0))
        st.caption(f"{sr:.0f}% / 20% target")

    with h3:
        st.markdown("**Debt-to-Income**")
        dti = profile.debt_to_income_ratio()
        st.progress(min(dti / 50, 1.0))
        color = "🟢" if dti < 20 else "🟡" if dti < 36 else "🔴"
        st.caption(f"{dti:.0f}% {color}")

    with h4:
        st.markdown("**Credit Score**")
        if profile.credit_score:
            st.progress(min(profile.credit_score / 850, 1.0))
            label = ("Excellent ✅" if profile.credit_score >= 750
                     else "Good 👍" if profile.credit_score >= 670
                     else "Fair ⚠️" if profile.credit_score >= 580
                     else "Needs Work 🔧")
            st.caption(f"{profile.credit_score} — {label}")
        else:
            st.caption("Not provided")

st.markdown("---")
st.caption("Last updated: this session • Dashboard auto-updates as you chat with agents")
