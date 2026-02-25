"""My Plan — AI-generated financial dashboard.

This page shows the financial plan that Richy built from your conversation.
No data entry — everything is populated from chat.
Users can view budget, debt strategy, investment recommendations, and goals.
"""

import math
import streamlit as st
import plotly.graph_objects as go
from agent_richy.profiles import UserProfile
import streamlit.components.v1 as components
from agent_richy.avatar import get_avatar_html, get_avatar_chat_html, get_sidebar_avatar, wrap_avatar_html
from agent_richy.utils.helpers import load_investments
from agent_richy.modules.adult import (
    estimate_federal_tax, mortgage_payment, debt_payoff_schedule, months_to_goal,
)

st.set_page_config(page_title="My Plan", page_icon="📊", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .avatar-center { display:flex; justify-content:center; align-items:center; margin:0.5rem 0; }
    .plan-section {
        background: #16213e;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    .empty-plan {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
    .empty-plan h2 { color: #FFD700; }
    .highlight-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #FFD700;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Session guard ────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.warning("Please start from the **Home** page first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile: UserProfile = st.session_state.profile
plan = st.session_state.get("financial_plan", {})
plan_generated = st.session_state.get("plan_generated", False)

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    expr_side = "happy" if plan_generated else "thinking"
    components.html(wrap_avatar_html(get_sidebar_avatar(expr_side, profile.name)), height=220)
    if profile.monthly_income > 0:
        expenses = profile.monthly_expenses or {}
        total_exp = sum(expenses.values()) if expenses else 0
        surplus = profile.monthly_income - total_exp
        st.metric("Monthly Surplus", f"${surplus:,.0f}")
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Chat_with_Richy.py", label="💬 Chat with Richy")
    st.page_link("pages/2_Learning_Center.py", label="📚 Learning Center")

# ── Header ───────────────────────────────────────────────────────────────
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    expr = "happy" if plan_generated else "thinking"
    components.html(wrap_avatar_html(get_avatar_html(expr, 100)), height=180)
with header_col2:
    st.markdown(f"## 📊 {profile.name}'s Financial Plan")
    if plan_generated:
        st.caption("Built by Richy from your conversation. Keep chatting to refine it!")
    else:
        st.caption("Talk to Richy first — your plan will appear here automatically.")


# ══════════════════════════════════════════════════════════════════════════
#  EMPTY STATE — No plan yet
# ══════════════════════════════════════════════════════════════════════════
if not plan_generated and profile.monthly_income == 0:
    st.markdown("---")

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        components.html(wrap_avatar_html(get_avatar_html("thinking", 180)), height=300)
        st.markdown("""
        <div class="empty-plan">
            <h2>💬 Your plan starts with a conversation</h2>
            <p>Tell Richy about your income, expenses, debts, and goals.<br>
            He'll build your complete financial plan right here.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/1_Chat_with_Richy.py",
            label="💬 Start Talking to Richy →",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("### What your plan will include:")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown("#### 📊 Budget")
        st.caption("50/30/20 breakdown based on YOUR income")
    with p2:
        st.markdown("#### 💳 Debt Strategy")
        st.caption("Payoff timeline with avalanche/snowball")
    with p3:
        st.markdown("#### 📈 Investments")
        st.caption("Portfolio recommendations for your risk level")
    with p4:
        st.markdown("#### 🎯 Goals")
        st.caption("Timeline and savings plan for each goal")

    st.stop()


# ══════════════════════════════════════════════════════════════════════════
#  PLAN DASHBOARD — populated from chat
# ══════════════════════════════════════════════════════════════════════════

# ── Top-level metrics ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Financial Overview")

income = profile.monthly_income
expenses = profile.monthly_expenses
surplus = income - expenses if income > 0 else 0
savings_rate = (surplus / income * 100) if income > 0 else 0

mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    st.metric("Monthly Income", f"${income:,.0f}" if income > 0 else "—")
with mc2:
    st.metric("Monthly Expenses", f"${expenses:,.0f}" if expenses > 0 else "—")
with mc3:
    st.metric("Monthly Surplus", f"${surplus:,.0f}",
              delta=f"{savings_rate:.1f}% savings rate" if income > 0 else None)
with mc4:
    ef = profile.emergency_fund
    if ef > 0 and expenses > 0:
        ef_months = ef / expenses
        st.metric("Emergency Fund", f"${ef:,.0f}", delta=f"{ef_months:.1f} months")
    elif profile.savings_balance > 0:
        st.metric("Savings", f"${profile.savings_balance:,.0f}")
    else:
        st.metric("Savings", "—")


# ── Budget Section ───────────────────────────────────────────────────────
if income > 0:
    st.markdown("---")
    st.markdown("### 📊 Your Budget Plan")

    budget = plan.get("budget", {})
    needs = budget.get("needs", income * 0.50)
    wants = budget.get("wants", income * 0.30)
    save_amt = budget.get("savings", income * 0.20)

    bc1, bc2 = st.columns([1, 1])

    with bc1:
        fig = go.Figure(data=[go.Pie(
            labels=["Needs", "Wants", "Savings & Investing"],
            values=[needs, wants, save_amt],
            marker_colors=["#FF6B6B", "#FFD93D", "#6BCB77"],
            hole=0.45,
            textinfo="label+percent",
        )])
        fig.update_layout(
            title="Recommended Budget Split",
            template="plotly_dark",
            height=350,
            showlegend=True,
            margin=dict(t=40, b=20, l=20, r=20),
        )
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
                st.warning(
                    f"⚠️ You're currently saving ${actual_save:,.0f}/mo — "
                    f"${diff:,.0f}/mo short of your target."
                )
            else:
                st.success(f"✅ You're saving ${actual_save:,.0f}/mo — on target!")


# ── Debt Section ─────────────────────────────────────────────────────────
if profile.debts:
    st.markdown("---")
    st.markdown("### 💳 Debt Payoff Strategy")

    total_debt = profile.total_debt()
    st.metric("Total Debt", f"${total_debt:,.0f}")

    # Sort by rate (avalanche)
    sorted_debts = sorted(
        profile.debts.items(),
        key=lambda x: profile.debt_interest_rates.get(x[0], 0),
        reverse=True,
    )

    st.markdown("#### Avalanche Order (highest interest first — saves the most)")

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

    # Payoff projection for first debt
    if sorted_debts:
        first_name, first_bal = sorted_debts[0]
        first_rate = profile.debt_interest_rates.get(first_name, 0)
        extra_payment = surplus * 0.5 if surplus > 0 else 0  # 50% of surplus to debt
        min_pay = max(first_bal * 0.02, 25)
        total_pay = min_pay + extra_payment

        if total_pay > first_bal * (first_rate / 12) and first_rate > 0:
            schedule = debt_payoff_schedule(first_bal, first_rate, total_pay)
            if schedule:
                months_list = [s["month"] for s in schedule]
                balances = [s["remaining"] for s in schedule]
                total_interest = sum(s["interest"] for s in schedule)

                yrs = len(schedule) // 12
                mos = len(schedule) % 12

                pc1, pc2, pc3 = st.columns(3)
                with pc1:
                    st.metric("Payoff Time", f"{yrs}yr {mos}mo")
                with pc2:
                    st.metric("Total Interest", f"${total_interest:,.0f}")
                with pc3:
                    st.metric("Monthly Payment", f"${total_pay:,.0f}")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months_list, y=balances,
                    fill="tozeroy", name="Remaining Balance",
                    line=dict(color="#FF6B6B"),
                    fillcolor="rgba(255,107,107,0.3)",
                ))
                fig.update_layout(
                    title=f"Payoff Timeline — {first_name}",
                    xaxis_title="Months", yaxis_title="Balance ($)",
                    template="plotly_dark", height=350,
                )
                st.plotly_chart(fig, use_container_width=True)


# ── Investment Section ───────────────────────────────────────────────────
if income > 0 and (not profile.debts or profile.total_debt() < income * 6):
    st.markdown("---")
    st.markdown("### 📈 Investment Recommendations")

    risk_level = plan.get("risk_level", profile.risk_tolerance)
    invest_amount = max(0, surplus * 0.3) if surplus > 0 else 0

    if invest_amount <= 0:
        st.info("💡 Focus on building surplus first. Once you have extra money each month, "
                "investing projections will appear here.")
    else:
        st.markdown(f"**Risk Level:** {risk_level.title()} · **Monthly Investment:** ${invest_amount:,.0f}")

        st.markdown("""
**Richy's Recommended Portfolio:**

| Allocation | What | Why |
|---|---|---|
| **60%** | Total Market Index (VTI/VXUS) | Broad diversification, low fees |
| **20%** | Bond Index (BND/BNDX) | Stability, income |
| **10%** | Growth ETF (QQQ/VGT) | Higher growth potential |
| **10%** | REIT / Alternative | Real estate exposure |
        """)

        # Growth projection
        rate_map = {"low": 0.05, "medium": 0.07, "moderate": 0.07,
                    "high": 0.10, "very high": 0.12, "aggressive": 0.12}
        annual_rate = rate_map.get(risk_level.lower(), 0.07)
        mr = annual_rate / 12

        years_list = [1, 5, 10, 15, 20, 25, 30]
        balances_proj = []
        contributed_proj = []
        for yr in years_list:
            b = 0.0
            for _ in range(yr * 12):
                b = b * (1 + mr) + invest_amount
            balances_proj.append(b)
            contributed_proj.append(invest_amount * 12 * yr)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"{y}yr" for y in years_list], y=contributed_proj,
            name="Contributed", marker_color="#555",
        ))
        fig.add_trace(go.Bar(
            x=[f"{y}yr" for y in years_list],
            y=[b - c for b, c in zip(balances_proj, contributed_proj)],
            name="Growth", marker_color="#6BCB77",
        ))
        fig.update_layout(
            title=f"${invest_amount:,.0f}/mo at ~{annual_rate*100:.0f}% return",
            barmode="stack", template="plotly_dark", height=350,
            yaxis_title="Balance ($)",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"**30-year projection: ${balances_proj[-1]:,.0f}** "
                    f"(contributed: ${contributed_proj[-1]:,.0f})")

        st.caption("⚠️ Projections are estimates. Past performance ≠ future results.")


# ── Goals Section ────────────────────────────────────────────────────────
if profile.goals:
    st.markdown("---")
    st.markdown("### 🎯 Your Goals")

    for goal in profile.goals:
        st.markdown(f"- ✅ {goal}")


# ── Recommendations Section ──────────────────────────────────────────────
recs = plan.get("recommendations", [])
if recs:
    st.markdown("---")
    st.markdown("### 🤖 Richy's Action Plan")

    for i, rec in enumerate(recs, 1):
        st.markdown(f"**{i}.** {rec}")

    st.markdown("")
    st.page_link(
        "pages/1_Chat_with_Richy.py",
        label="💬 Refine Plan with Richy →",
        use_container_width=True,
    )

# ── Financial Health Indicators ──────────────────────────────────────────
if profile.completed_assessment:
    st.markdown("---")
    st.markdown("### 🏥 Financial Health")

    hi1, hi2, hi3, hi4 = st.columns(4)

    with hi1:
        st.markdown("**Emergency Fund**")
        ef_months = profile.months_of_emergency()
        st.progress(min(ef_months / 6, 1.0))
        st.caption(f"{ef_months:.1f} / 6 months")

    with hi2:
        st.markdown("**Savings Rate**")
        st.progress(min(savings_rate / 20, 1.0))
        st.caption(f"{savings_rate:.0f}% / 20% target")

    with hi3:
        st.markdown("**Debt-to-Income**")
        dti = profile.debt_to_income_ratio()
        st.progress(min(dti / 50, 1.0))
        color = "🟢" if dti < 20 else "🟡" if dti < 36 else "🔴"
        st.caption(f"{dti:.0f}% {color}")

    with hi4:
        st.markdown("**Credit Score**")
        if profile.credit_score:
            score_pct = min(profile.credit_score / 850, 1.0)
            st.progress(score_pct)
            if profile.credit_score >= 750:
                st.caption(f"{profile.credit_score} — Excellent ✅")
            elif profile.credit_score >= 670:
                st.caption(f"{profile.credit_score} — Good 👍")
            elif profile.credit_score >= 580:
                st.caption(f"{profile.credit_score} — Fair ⚠️")
            else:
                st.caption(f"{profile.credit_score} — Needs work 🔧")
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

        st.info("💡 Reduce taxes: max out 401(k) ($23,000/yr), contribute to HSA/IRA, "
                "track deductions.")


# ── CTA at bottom ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Need to update your plan?")
st.markdown("Just go back to the chat and tell Richy about any changes in your situation.")
st.page_link(
    "pages/1_Chat_with_Richy.py",
    label="💬 Talk to Richy →",
    use_container_width=True,
)
