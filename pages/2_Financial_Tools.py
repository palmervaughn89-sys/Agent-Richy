"""Financial Tools — calculators, simulators, and planners."""

import math
import streamlit as st
import plotly.graph_objects as go
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import (
    get_openai_client, ask_llm, load_investments, format_currency,
)
from agent_richy.modules.adult import (
    estimate_federal_tax, mortgage_payment, debt_payoff_schedule, months_to_goal,
)

st.set_page_config(page_title="Financial Tools", page_icon="💰", layout="wide")

# ── Session guard ────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.warning("Please start from the **Home** page first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile: UserProfile = st.session_state.profile
client = st.session_state.get("llm_client")

st.markdown("## 💰 Financial Tools")

with st.chat_message("assistant", avatar="💰"):
    st.markdown("Pick a tool below — I'll crunch the numbers for you! 🔢")

# ── Tabs ─────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Budget", "💳 Debt Payoff", "🧾 Tax Estimator",
    "🏠 Mortgage", "🏖️ Vacation", "🎯 Goals", "📈 Investments",
])

# =====================================================================
# TAB 1 — Budget Simulator
# =====================================================================
with tabs[0]:
    st.markdown("### 📊 Budget Simulator (50/30/20 Rule)")
    st.caption("Enter your numbers to see where your money goes and how to improve.")

    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly take-home income ($)", min_value=0.0,
                                  value=float(profile.monthly_income) if profile.monthly_income else 4000.0,
                                  step=100.0, key="budget_income")
    with col2:
        st.markdown("**Guidelines**")
        st.markdown("- **50%** Needs — rent, food, insurance")
        st.markdown("- **30%** Wants — fun, dining, shopping")
        st.markdown("- **20%** Save & invest")

    st.markdown("#### Fixed Expenses (Needs)")
    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        rent = st.number_input("Rent / mortgage", 0.0, step=50.0, key="b_rent")
    with bc2:
        utilities = st.number_input("Utilities", 0.0, step=25.0, key="b_util")
    with bc3:
        insurance = st.number_input("Insurance", 0.0, step=25.0, key="b_ins")
    with bc4:
        transport = st.number_input("Transportation", 0.0, step=25.0, key="b_trans")

    bc5, bc6, bc7, bc8 = st.columns(4)
    with bc5:
        groceries = st.number_input("Groceries", 0.0, step=25.0, key="b_groc")
    with bc6:
        phone = st.number_input("Phone / internet", 0.0, step=10.0, key="b_phone")
    with bc7:
        loan_pay = st.number_input("Loan payments", 0.0, step=25.0, key="b_loan")
    with bc8:
        childcare = st.number_input("Childcare", 0.0, step=50.0, key="b_child")

    total_needs = rent + utilities + insurance + transport + groceries + phone + loan_pay + childcare

    st.markdown("#### Variable Expenses (Wants)")
    wc1, wc2, wc3, wc4 = st.columns(4)
    with wc1:
        dining = st.number_input("Dining out / delivery", 0.0, step=25.0, key="b_dine")
    with wc2:
        shopping = st.number_input("Shopping / clothing", 0.0, step=25.0, key="b_shop")
    with wc3:
        entertain = st.number_input("Entertainment", 0.0, step=25.0, key="b_ent")
    with wc4:
        subs = st.number_input("Subscriptions", 0.0, step=10.0, key="b_subs")

    total_wants = dining + shopping + entertain + subs
    total_exp = total_needs + total_wants
    surplus = income - total_exp

    if income > 0:
        st.markdown("---")
        st.markdown("### Results")

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("Total Expenses", f"${total_exp:,.0f}")
        with mc2:
            st.metric("Monthly Surplus", f"${surplus:,.0f}",
                       delta="Positive ✅" if surplus >= 0 else "Overspending ⚠️")
        with mc3:
            sr = max(0, surplus / income * 100)
            st.metric("Savings Rate", f"{sr:.1f}%",
                       delta="On track" if sr >= 20 else "Under 20%")
        with mc4:
            needs_pct = total_needs / income * 100
            st.metric("Needs %", f"{needs_pct:.0f}%",
                       delta="OK" if needs_pct <= 50 else "Over 50%")

        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=["Needs", "Wants", "Savings/Surplus"],
            values=[total_needs, total_wants, max(0, surplus)],
            marker_colors=["#FF6B6B", "#FFD93D", "#6BCB77"],
            hole=0.4,
            textinfo="label+percent",
        )])
        fig.update_layout(
            title="Your Budget Breakdown",
            template="plotly_dark",
            height=400,
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        # 50/30/20 comparison
        needs_pct = total_needs / income * 100
        wants_pct = total_wants / income * 100
        save_pct = max(0, surplus / income * 100)

        st.markdown("#### 50/30/20 Analysis")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            st.progress(min(needs_pct / 50, 1.0))
            icon = "✅" if needs_pct <= 50 else "⚠️"
            st.markdown(f"**Needs:** {needs_pct:.0f}% / 50% {icon}")
        with ac2:
            st.progress(min(wants_pct / 30, 1.0))
            icon = "✅" if wants_pct <= 30 else "⚠️"
            st.markdown(f"**Wants:** {wants_pct:.0f}% / 30% {icon}")
        with ac3:
            st.progress(min(save_pct / 20, 1.0))
            icon = "✅" if save_pct >= 20 else "⚠️"
            st.markdown(f"**Savings:** {save_pct:.0f}% / 20% {icon}")

        if surplus < 0:
            st.error(f"⚠️ You're overspending by ${abs(surplus):,.0f}/month. "
                     "Look at your top expenses to find cuts.")

        # Update profile
        profile.monthly_income = income
        profile.monthly_expenses = total_exp


# =====================================================================
# TAB 2 — Debt Payoff
# =====================================================================
with tabs[1]:
    st.markdown("### 💳 Debt Destroyer")
    st.caption("See exactly when you'll be debt-free with snowball or avalanche strategy.")

    method = st.radio("Payoff strategy", ["Avalanche (highest rate first)", "Snowball (smallest balance first)"],
                      horizontal=True, key="debt_method")

    num_debts = st.number_input("How many debts?", min_value=1, max_value=10, value=1, key="n_debts")

    debts_data = []
    for i in range(int(num_debts)):
        st.markdown(f"**Debt {i+1}**")
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            name = st.text_input("Name", value=f"Debt {i+1}", key=f"dname_{i}")
        with dc2:
            bal = st.number_input("Balance ($)", 0.0, step=100.0, key=f"dbal_{i}")
        with dc3:
            apr = st.number_input("APR (%)", 0.0, 50.0, step=0.5, key=f"dapr_{i}")
        if bal > 0:
            debts_data.append({"name": name, "balance": bal, "apr": apr / 100})

    extra = st.number_input("Extra monthly payment beyond minimums ($)",
                             0.0, step=50.0, key="debt_extra")

    if debts_data and st.button("Calculate Payoff Plan 🔥", key="calc_debt"):
        # Sort by method
        if "Avalanche" in method:
            debts_data.sort(key=lambda d: d["apr"], reverse=True)
        else:
            debts_data.sort(key=lambda d: d["balance"])

        st.markdown("#### Payoff Order")
        for i, d in enumerate(debts_data, 1):
            st.markdown(f"{i}. **{d['name']}**: ${d['balance']:,.0f} @ {d['apr']*100:.1f}%")

        # Simulate first debt payoff
        d = debts_data[0]
        min_pay = max(d["balance"] * 0.02, 25)
        total_pay = min_pay + extra

        if total_pay <= d["balance"] * (d["apr"] / 12):
            st.error("⚠️ Your payment doesn't cover monthly interest! Increase your payment.")
        else:
            schedule = debt_payoff_schedule(d["balance"], d["apr"], total_pay)
            if schedule:
                total_months = len(schedule)
                total_interest = sum(s["interest"] for s in schedule)
                yrs = total_months // 12
                mos = total_months % 12

                rc1, rc2, rc3 = st.columns(3)
                with rc1:
                    st.metric("Payoff Time", f"{yrs}yr {mos}mo")
                with rc2:
                    st.metric("Total Interest", f"${total_interest:,.0f}")
                with rc3:
                    st.metric("Monthly Payment", f"${total_pay:,.0f}")

                # Chart
                months_list = [s["month"] for s in schedule]
                balances = [s["remaining"] for s in schedule]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months_list, y=balances,
                    fill="tozeroy", name="Remaining Balance",
                    line=dict(color="#FF6B6B"),
                    fillcolor="rgba(255,107,107,0.3)",
                ))
                fig.update_layout(
                    title=f"Payoff Timeline — {d['name']}",
                    xaxis_title="Months", yaxis_title="Balance ($)",
                    template="plotly_dark", height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

                # Compare with minimums only
                if extra > 0:
                    schedule_min = debt_payoff_schedule(d["balance"], d["apr"], min_pay)
                    if schedule_min:
                        int_min = sum(s["interest"] for s in schedule_min)
                        saved = int_min - total_interest
                        st.success(
                            f"💰 Your extra ${extra:,.0f}/mo saves **${saved:,.0f}** in interest "
                            f"and cuts **{len(schedule_min) - total_months} months** off your payoff!"
                        )

        # Store debts on profile
        for d in debts_data:
            profile.debts[d["name"]] = d["balance"]
            profile.debt_interest_rates[d["name"]] = d["apr"]


# =====================================================================
# TAB 3 — Tax Estimator
# =====================================================================
with tabs[2]:
    st.markdown("### 🧾 Federal Tax Estimator (2024)")
    st.caption("Rough estimate — always consult a CPA for your actual return.")

    tc1, tc2 = st.columns(2)
    with tc1:
        gross = st.number_input("Gross annual income ($)", 0.0, step=1000.0,
                                 value=65000.0, key="tax_gross")
    with tc2:
        filing = st.selectbox("Filing status", ["Single", "Married Filing Jointly"],
                               key="tax_filing")

    if gross > 0:
        status = "married" if "Married" in filing else "single"
        result = estimate_federal_tax(gross, status)

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.metric("Take-Home (Annual)", f"${result['take_home']:,.0f}")
        with rc2:
            st.metric("Take-Home (Monthly)", f"${result['take_home']/12:,.0f}")
        with rc3:
            st.metric("Effective Rate", f"{result['effective_rate']:.1f}%")

        st.markdown("#### Breakdown")
        st.markdown(f"""
| Item | Amount |
|---|---|
| Gross Income | ${result['gross_income']:,.0f} |
| Standard Deduction | -${result['standard_deduction']:,.0f} |
| Taxable Income | ${result['taxable_income']:,.0f} |
| Federal Income Tax | ${result['federal_tax']:,.0f} |
| FICA (SS + Medicare) | ${result['fica_tax']:,.0f} |
| **Total Tax** | **${result['total_tax']:,.0f}** |
| **Take-Home** | **${result['take_home']:,.0f}** |
        """)

        st.markdown("#### 💡 Ways to Reduce Your Tax Bill")
        st.markdown("""
- **401(k):** Contribute up to $23,000/yr to reduce taxable income
- **Traditional IRA:** Up to $7,000/yr deductible
- **HSA:** Triple tax advantage if you have a high-deductible health plan
- **Charitable donations:** Deductible if you itemize
- **Self-employed?** Deduct home office, business expenses, and self-employment tax
        """)


# =====================================================================
# TAB 4 — Mortgage Calculator
# =====================================================================
with tabs[3]:
    st.markdown("### 🏠 Mortgage Calculator")

    mc1, mc2 = st.columns(2)
    with mc1:
        home_price = st.number_input("Home price ($)", 0.0, step=10000.0,
                                      value=350000.0, key="mort_price")
        down_pct = st.slider("Down payment (%)", 0, 50, 20, key="mort_down")
        down = home_price * down_pct / 100
        st.caption(f"Down payment: ${down:,.0f}")
    with mc2:
        rate = st.number_input("Interest rate (%)", 0.0, 15.0, 6.5, 0.1, key="mort_rate")
        term = st.selectbox("Loan term", [30, 15, 20], key="mort_term")

    if home_price > 0:
        principal = home_price - down
        monthly = mortgage_payment(principal, rate / 100, term)
        total_paid = monthly * term * 12
        total_interest = total_paid - principal

        # PMI if < 20% down
        pmi = principal * 0.008 / 12 if down_pct < 20 else 0.0
        prop_tax = home_price * 0.012 / 12
        home_ins = home_price * 0.005 / 12
        total_monthly = monthly + prop_tax + home_ins + pmi

        st.markdown("---")
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric("Monthly P&I", f"${monthly:,.0f}")
        with rc2:
            st.metric("Total Monthly*", f"${total_monthly:,.0f}")
        with rc3:
            st.metric("Total Interest", f"${total_interest:,.0f}")
        with rc4:
            if profile.monthly_income > 0:
                dti = total_monthly / profile.monthly_income * 100
                st.metric("Housing DTI", f"{dti:.0f}%",
                           delta="OK" if dti <= 28 else "High")

        st.caption("*Includes estimated property tax, insurance, and PMI if applicable")

        st.markdown("#### Cost Breakdown")
        st.markdown(f"""
| Item | Monthly | Annual |
|---|---|---|
| Principal & Interest | ${monthly:,.0f} | ${monthly*12:,.0f} |
| Property Tax (est.) | ${prop_tax:,.0f} | ${prop_tax*12:,.0f} |
| Home Insurance (est.) | ${home_ins:,.0f} | ${home_ins*12:,.0f} |
| PMI | ${pmi:,.0f} | ${pmi*12:,.0f} |
| **Total** | **${total_monthly:,.0f}** | **${total_monthly*12:,.0f}** |
        """)

        if down_pct < 20:
            st.warning("⚠️ With less than 20% down, you'll pay PMI until you reach 20% equity.")


# =====================================================================
# TAB 5 — Vacation Planner
# =====================================================================
with tabs[4]:
    st.markdown("### 🏖️ Vacation Planner")
    st.caption("Plan your dream trip with a real savings timeline — no credit card debt needed!")

    vc1, vc2, vc3 = st.columns(3)
    with vc1:
        dest = st.text_input("Destination", "Hawaii", key="vac_dest")
    with vc2:
        travelers = st.number_input("Number of travelers", 1, 10, 2, key="vac_trav")
    with vc3:
        months_away = st.number_input("Months from now", 1, 60, 12, key="vac_months")

    st.markdown("#### Estimated Costs")
    vcc1, vcc2, vcc3 = st.columns(3)
    with vcc1:
        flights = st.number_input("Flights / transportation", 0.0, step=100.0, key="v_flights")
        food = st.number_input("Food & dining", 0.0, step=100.0, key="v_food")
    with vcc2:
        hotel = st.number_input("Hotel / lodging", 0.0, step=100.0, key="v_hotel")
        activities = st.number_input("Activities / excursions", 0.0, step=50.0, key="v_act")
    with vcc3:
        shopping_v = st.number_input("Shopping / souvenirs", 0.0, step=50.0, key="v_shop")
        buffer = st.number_input("Buffer (10-20%)", 0.0, step=50.0, key="v_buffer")

    total_vac = flights + hotel + food + activities + shopping_v + buffer
    already_saved = st.number_input("Already saved for this trip ($)", 0.0, step=100.0, key="v_saved")

    if total_vac > 0:
        remaining = max(0, total_vac - already_saved)
        monthly_save = remaining / months_away if months_away > 0 else remaining
        weekly_save = monthly_save / 4.33

        st.markdown("---")
        rr1, rr2, rr3, rr4 = st.columns(4)
        with rr1:
            st.metric("Total Cost", f"${total_vac:,.0f}")
        with rr2:
            st.metric("Per Person", f"${total_vac/travelers:,.0f}")
        with rr3:
            st.metric("Save / Month", f"${monthly_save:,.0f}")
        with rr4:
            st.metric("Save / Week", f"${weekly_save:,.0f}")

        pct_done = already_saved / total_vac
        st.progress(min(pct_done, 1.0))
        st.caption(f"{pct_done*100:.0f}% saved — ${remaining:,.0f} to go")

        # Timeline chart
        months_list = list(range(int(months_away) + 1))
        savings_line = [min(already_saved + monthly_save * m, total_vac) for m in months_list]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months_list, y=savings_line,
            fill="tozeroy", name="Savings",
            line=dict(color="#6BCB77"),
            fillcolor="rgba(107,203,119,0.3)",
        ))
        fig.add_hline(y=total_vac, line_dash="dash", line_color="#FFD700",
                       annotation_text=f"Goal: ${total_vac:,.0f}")
        fig.update_layout(
            title=f"Savings Timeline for {dest}",
            xaxis_title="Months", yaxis_title="Saved ($)",
            template="plotly_dark", height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        profile.vacation_target = total_vac
        profile.vacation_fund = already_saved
        profile.vacation_deadline_months = int(months_away)

        st.info("💡 **Tip:** Open a separate savings account labeled 'Vacation Fund' "
                "and automate transfers on payday!")


# =====================================================================
# TAB 6 — Goal Planner
# =====================================================================
with tabs[5]:
    st.markdown("### 🎯 Goal Planner")
    st.caption("See exactly how long it takes to hit any savings goal with compound growth.")

    gc1, gc2 = st.columns(2)
    with gc1:
        goal_name = st.selectbox("Goal type", [
            "Emergency fund", "New car", "Home down payment",
            "Child education", "Wedding", "Start a business",
            "Early retirement", "Custom goal",
        ], key="goal_type")
        if goal_name == "Custom goal":
            goal_name = st.text_input("Goal name", key="goal_custom")
        target = st.number_input("Target amount ($)", 0.0, step=1000.0,
                                  value=10000.0, key="goal_target")
    with gc2:
        current = st.number_input("Already saved ($)", 0.0, step=100.0, key="goal_current")
        monthly_c = st.number_input("Monthly contribution ($)", 0.0, step=50.0,
                                     value=200.0, key="goal_monthly")
        ann_rate = st.slider("Expected annual return (%)", 0.0, 15.0, 7.0, 0.5,
                              key="goal_rate")

    if target > 0 and monthly_c > 0:
        remaining = max(0, target - current)
        months = months_to_goal(monthly_c, remaining, ann_rate / 100) if monthly_c > 0 else 0
        yrs = months // 12
        mos = months % 12

        st.markdown("---")
        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            st.metric("Time to Goal", f"{yrs}yr {mos}mo")
        with gc2:
            total_contributed = current + monthly_c * months
            st.metric("Total Contributed", f"${total_contributed:,.0f}")
        with gc3:
            growth = target - total_contributed
            st.metric("Growth from Returns", f"${max(0,growth):,.0f}")

        st.progress(min(current / target, 1.0))
        st.caption(f"{current/target*100:.0f}% complete")

        # Growth chart
        mr = ann_rate / 100 / 12
        balances = []
        b = current
        for m in range(months + 1):
            balances.append(b)
            b = b * (1 + mr) + monthly_c

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(balances))), y=balances,
            fill="tozeroy", name="Balance",
            line=dict(color="#6BCB77"),
            fillcolor="rgba(107,203,119,0.2)",
        ))
        contributions = [current + monthly_c * m for m in range(months + 1)]
        fig.add_trace(go.Scatter(
            x=list(range(len(contributions))), y=contributions,
            name="Contributions Only", line=dict(color="#888", dash="dash"),
        ))
        fig.add_hline(y=target, line_dash="dash", line_color="#FFD700",
                       annotation_text=f"Goal: ${target:,.0f}")
        fig.update_layout(
            title=f"Path to {goal_name}",
            xaxis_title="Months", yaxis_title="Balance ($)",
            template="plotly_dark", height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# TAB 7 — Investment Portfolio Builder
# =====================================================================
with tabs[6]:
    st.markdown("### 📈 Investment Portfolio Builder")
    st.caption("Get personalized investment ideas based on your risk tolerance and interests.")

    ic1, ic2 = st.columns(2)
    with ic1:
        risk = st.select_slider("Risk tolerance", options=["low", "medium", "high", "very high"],
                                 value="medium", key="inv_risk")
        invest_monthly = st.number_input("Monthly investment amount ($)", 0.0,
                                          step=50.0, value=500.0, key="inv_amount")
    with ic2:
        themes = st.multiselect("Investment themes", [
            "AI", "clean energy", "healthcare", "real estate",
            "crypto", "income", "diversification",
        ], default=["diversification"], key="inv_themes")
        esg = st.checkbox("Prefer ESG / socially responsible", key="inv_esg")

    if st.button("Build My Portfolio 🏗️", key="build_port"):
        data = load_investments()
        all_instruments = []
        for category in data.values():
            all_instruments.extend(category)

        # Score instruments
        scored = []
        for inst in all_instruments:
            score = 0
            inst_risk = inst.get("risk", "")
            if inst_risk == risk:
                score += 3
            elif risk == "very high" and inst_risk in ("high", "very high"):
                score += 2
            elif risk == "medium" and inst_risk in ("low", "medium"):
                score += 2

            inst_themes = [t.lower() for t in inst.get("themes", [])]
            for t in themes:
                if any(t.lower() in it for it in inst_themes):
                    score += 2

            if esg:
                esg_rank = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "N/A": 0}
                if esg_rank.get(inst.get("esg_score", "N/A"), 0) >= 4:
                    score += 2

            scored.append((score, inst))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_picks = scored[:8]

        if not top_picks:
            st.warning("No matching investments found. Try different filters.")
        else:
            # Core / Growth / Alternative split
            core = [s for s in top_picks if s[1].get("type") in ("etf", "fund")][:3]
            growth = [s for s in top_picks if s[1].get("type") == "stock"][:3]
            alt = [s for s in top_picks if s[1].get("type") in ("commodity", "crypto")][:2]

            st.markdown("#### 🏗️ Core Holdings (60%)")
            if core:
                for _, inst in core:
                    alloc = 60 // len(core)
                    amt = invest_monthly * alloc / 100
                    st.markdown(
                        f"**{inst['ticker']}** — {inst['name']}  \n"
                        f"{inst['description']}  \n"
                        f"Risk: `{inst['risk']}` | Type: `{inst['type']}` | "
                        f"Allocation: **{alloc}%** (${amt:,.0f}/mo)"
                    )

            st.markdown("#### 🚀 Growth Holdings (30%)")
            if growth:
                for _, inst in growth:
                    alloc = 30 // len(growth)
                    amt = invest_monthly * alloc / 100
                    st.markdown(
                        f"**{inst['ticker']}** — {inst['name']}  \n"
                        f"{inst['description']}  \n"
                        f"Risk: `{inst['risk']}` | Allocation: **{alloc}%** (${amt:,.0f}/mo)"
                    )

            st.markdown("#### 🔮 Alternative Holdings (10%)")
            if alt:
                for _, inst in alt:
                    alloc = 10 // len(alt)
                    amt = invest_monthly * alloc / 100
                    st.markdown(
                        f"**{inst['ticker']}** — {inst['name']}  \n"
                        f"{inst['description']}  \n"
                        f"Risk: `{inst['risk']}` | Allocation: **{alloc}%** (${amt:,.0f}/mo)"
                    )

            # Growth projection
            if invest_monthly > 0:
                st.markdown("#### 📈 Growth Projection")
                rate_map = {"low": 0.05, "medium": 0.08, "high": 0.10, "very high": 0.12}
                annual = rate_map.get(risk, 0.08)
                mr = annual / 12

                years_list = [1, 3, 5, 10, 15, 20, 25, 30]
                balances_proj = []
                contributed_proj = []
                for yr in years_list:
                    b = 0.0
                    for _ in range(yr * 12):
                        b = b * (1 + mr) + invest_monthly
                    balances_proj.append(b)
                    contributed_proj.append(invest_monthly * 12 * yr)

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
                    title=f"${invest_monthly:,.0f}/mo at ~{annual*100:.0f}% annual return",
                    barmode="stack", template="plotly_dark", height=400,
                    yaxis_title="Balance ($)",
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(f"**30-year balance: ${balances_proj[-1]:,.0f}** "
                            f"(contributed ${contributed_proj[-1]:,.0f})")

            st.warning("⚠️ This is educational, not financial advice. "
                       "Past performance doesn't guarantee future returns.")

        profile.risk_tolerance = risk
        profile.themes = themes
        profile.esg_preference = esg
