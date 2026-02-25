"""My Profile — financial assessment form and snapshot dashboard."""

import streamlit as st
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client, ask_llm, format_currency

st.set_page_config(page_title="My Profile", page_icon="📋", layout="wide")

# ── Session guard ────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.warning("Please start from the **Home** page first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile: UserProfile = st.session_state.profile
client = st.session_state.get("llm_client")

st.markdown("## 📋 My Financial Profile")

# ── Tabs ─────────────────────────────────────────────────────────────────
tab_assess, tab_snap = st.tabs(["📝 Financial Assessment", "📊 My Snapshot"])

# =====================================================================
# TAB 1 — Financial Assessment
# =====================================================================
with tab_assess:
    with st.chat_message("assistant", avatar="💰"):
        st.markdown(
            "Let's get a complete picture of your finances. "
            "Be honest — this is for **YOU**, not for anyone else. "
            "Everything stays in your browser session. 🔒"
        )

    if profile.is_youth():
        # Youth assessment
        st.markdown("### 🎓 Youth Financial Assessment")

        with st.form("youth_assess"):
            yc1, yc2 = st.columns(2)
            with yc1:
                name = st.text_input("Name", value=profile.name, key="ya_name")
                age = st.number_input("Age", 5, 17, value=profile.age or 14, key="ya_age")
                grade = st.selectbox("Grade level", ["middle", "high"],
                                      index=0 if profile.grade_level == "middle" else 1,
                                      key="ya_grade")
            with yc2:
                allowance = st.number_input("Monthly allowance ($)", 0.0, step=5.0,
                                             value=profile.allowance, key="ya_allow")
                has_job = st.checkbox("Do you have a job?", value=profile.has_job, key="ya_job")
                if has_job:
                    hourly = st.number_input("Hourly rate ($)", 0.0, step=0.5,
                                              value=profile.hourly_rate, key="ya_rate")
                    hours = st.number_input("Hours per week", 0.0, step=1.0,
                                             value=profile.weekly_hours, key="ya_hours")
                else:
                    hourly = 0.0
                    hours = 0.0

            savings = st.number_input("Current savings ($)", 0.0, step=10.0,
                                       value=profile.savings_balance, key="ya_savings")

            talents = st.multiselect("Your talents / interests", [
                "Creative (art, music, writing)", "Tech (coding, gaming, video)",
                "Athletic (sports, fitness)", "Social (leadership, communication)",
                "Hands-on (building, cooking, crafts)",
            ], key="ya_talents")

            submitted = st.form_submit_button("Save Assessment ✅", use_container_width=True)

            if submitted:
                profile.name = name
                profile.age = int(age)
                profile.grade_level = grade
                profile.user_type = "youth"
                profile.allowance = allowance
                profile.has_job = has_job
                profile.hourly_rate = hourly
                profile.weekly_hours = hours
                profile.savings_balance = savings
                profile.talents = talents
                profile.completed_assessment = True
                st.success("Assessment saved! Check the **My Snapshot** tab for your summary. ✅")
                st.rerun()

    else:
        # Adult assessment
        st.markdown("### 💼 Full Financial Assessment")

        with st.form("adult_assess"):
            st.markdown("#### 💵 Income")
            ic1, ic2 = st.columns(2)
            with ic1:
                income = st.number_input("Monthly take-home income ($)", 0.0, step=100.0,
                                          value=profile.monthly_income, key="aa_income")
            with ic2:
                other_income = st.number_input("Other monthly income (side gig, rental, etc.)", 0.0,
                                                step=50.0, key="aa_other")

            st.markdown("#### 🏦 Savings & Emergency Fund")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                savings_bal = st.number_input("Total savings balance ($)", 0.0, step=100.0,
                                               value=profile.savings_balance, key="aa_savings")
            with sc2:
                ef = st.number_input("Emergency fund ($)", 0.0, step=100.0,
                                      value=profile.emergency_fund, key="aa_ef")
            with sc3:
                credit = st.number_input("Credit score (0 if unsure)", 0, 850,
                                          value=profile.credit_score or 0, key="aa_credit")

            st.markdown("#### 💸 Monthly Expenses")
            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1:
                e_rent = st.number_input("Rent / mortgage", 0.0, step=50.0, key="aa_rent")
                e_groc = st.number_input("Groceries", 0.0, step=25.0, key="aa_groc")
                e_child = st.number_input("Childcare", 0.0, step=50.0, key="aa_child")
            with ec2:
                e_car = st.number_input("Car payment", 0.0, step=50.0, key="aa_car")
                e_util = st.number_input("Utilities", 0.0, step=25.0, key="aa_util")
                e_ins = st.number_input("Insurance premiums", 0.0, step=25.0, key="aa_ins")
            with ec3:
                e_dine = st.number_input("Dining out / delivery", 0.0, step=25.0, key="aa_dine")
                e_gas = st.number_input("Gas / transportation", 0.0, step=25.0, key="aa_gas")
                e_phone = st.number_input("Phone / internet", 0.0, step=10.0, key="aa_phone")
            with ec4:
                e_subs = st.number_input("Subscriptions", 0.0, step=10.0, key="aa_subs")
                e_shop = st.number_input("Shopping / clothing", 0.0, step=25.0, key="aa_shop")
                e_misc = st.number_input("Miscellaneous", 0.0, step=25.0, key="aa_misc")

            total_exp = (e_rent + e_groc + e_child + e_car + e_util + e_ins +
                         e_dine + e_gas + e_phone + e_subs + e_shop + e_misc)

            st.markdown("#### 💳 Debts")
            has_debt = st.checkbox("I have debts", key="aa_has_debt")
            debts_input = {}
            rates_input = {}
            if has_debt:
                num_debts = st.number_input("Number of debts", 1, 10, 1, key="aa_ndebts")
                for i in range(int(num_debts)):
                    dc1, dc2, dc3 = st.columns(3)
                    with dc1:
                        dname = st.text_input("Debt name", f"Debt {i+1}", key=f"aa_dn_{i}")
                    with dc2:
                        dbal = st.number_input("Balance ($)", 0.0, step=100.0, key=f"aa_db_{i}")
                    with dc3:
                        drate = st.number_input("APR (%)", 0.0, 50.0, step=0.5, key=f"aa_dr_{i}")
                    if dbal > 0:
                        debts_input[dname] = dbal
                        rates_input[dname] = drate / 100

            submitted = st.form_submit_button("Save Assessment ✅", use_container_width=True)

            if submitted:
                profile.monthly_income = income + other_income
                profile.monthly_expenses = total_exp
                profile.savings_balance = savings_bal
                profile.emergency_fund = ef
                profile.credit_score = int(credit) if credit > 0 else None
                profile.debts = debts_input
                profile.debt_interest_rates = rates_input
                profile.debt_balance = sum(debts_input.values())

                surplus = profile.monthly_income - profile.monthly_expenses
                if surplus <= profile.monthly_income * 0.05 and ef < total_exp:
                    profile.paycheck_to_paycheck = True

                profile.completed_assessment = True
                st.success("Assessment saved! ✅")
                st.rerun()


# =====================================================================
# TAB 2 — Financial Snapshot
# =====================================================================
with tab_snap:
    if not profile.completed_assessment:
        st.info("Complete the **Financial Assessment** tab first to see your snapshot.")
        st.stop()

    with st.chat_message("assistant", avatar="💰"):
        surplus = profile.monthly_surplus()
        if profile.is_youth():
            monthly = profile.youth_monthly_income()
            st.markdown(
                f"Here's your financial snapshot, **{profile.name}**! "
                f"You're earning about **${monthly:,.0f}/month** — that's a great start! 🌟"
            )
        elif surplus > 0:
            st.markdown(
                f"Looking good, **{profile.name}**! You have a monthly surplus of "
                f"**${surplus:,.0f}**. Let's make every dollar count! 💪"
            )
        else:
            st.markdown(
                f"Let's work on this together, **{profile.name}**. "
                "Awareness is the first step to change! 🎯"
            )

    # ── Youth Snapshot ────────────────────────────────────────────────
    if profile.is_youth():
        st.markdown("### 🎓 Youth Financial Dashboard")

        mc1, mc2, mc3 = st.columns(3)
        monthly_inc = profile.youth_monthly_income()
        with mc1:
            st.metric("Monthly Income", f"${monthly_inc:,.0f}")
        with mc2:
            st.metric("Savings", f"${profile.savings_balance:,.0f}")
        with mc3:
            st.metric("Grade Level", (profile.grade_level or "N/A").title())

        if profile.talents:
            st.markdown(f"**Talents:** {', '.join(profile.talents)}")
        if profile.side_hustles:
            st.markdown(f"**Side Hustles:** {', '.join(profile.side_hustles)}")

        st.markdown("---")
        st.markdown("### 📊 Recommendations")
        recs = []
        if profile.savings_balance < 100:
            recs.append("🎯 Set a first savings goal: $100!")
        if not profile.has_job and profile.age and profile.age >= 14:
            recs.append("💼 You're old enough for a part-time job — explore options!")
        if not profile.talents:
            recs.append("🌟 Discover your talents — they could become earning opportunities!")
        recs.append("📚 Keep learning about money — you're already ahead!")
        for r in recs:
            st.markdown(f"- {r}")

    # ── Adult Snapshot ────────────────────────────────────────────────
    else:
        st.markdown("### 💼 Adult Financial Dashboard")

        surplus = profile.monthly_surplus()
        sr = profile.savings_rate()
        ef_months = profile.months_of_emergency()

        # Top metrics
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("Monthly Income", f"${profile.monthly_income:,.0f}")
        with mc2:
            st.metric("Monthly Expenses", f"${profile.monthly_expenses:,.0f}")
        with mc3:
            st.metric("Monthly Surplus", f"${surplus:,.0f}",
                       delta=f"{sr:.1f}% savings rate")
        with mc4:
            st.metric("Emergency Fund", f"${profile.emergency_fund:,.0f}",
                       delta=f"{ef_months:.1f} months")

        st.markdown("---")

        # Debt & net worth
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            total_debt = profile.total_debt()
            st.metric("Total Debt", f"${total_debt:,.0f}")
            if profile.debts:
                for label, bal in profile.debts.items():
                    rate = profile.debt_interest_rates.get(label, 0) * 100
                    st.caption(f"• {label}: ${bal:,.0f} @ {rate:.1f}%")
        with dc2:
            if profile.credit_score:
                st.metric("Credit Score", profile.credit_score)
                if profile.credit_score >= 750:
                    st.caption("Excellent ✅")
                elif profile.credit_score >= 670:
                    st.caption("Good 👍")
                elif profile.credit_score >= 580:
                    st.caption("Fair ⚠️")
                else:
                    st.caption("Needs improvement 🔧")
        with dc3:
            assets = profile.savings_balance + profile.emergency_fund
            net_worth = assets - total_debt
            st.metric("Net Worth (est.)", f"${net_worth:,.0f}")
            if net_worth < 0:
                st.caption("Negative net worth is common — focus on debt reduction")

        st.markdown("---")

        # Health indicators
        st.markdown("### 🏥 Financial Health Indicators")
        hi1, hi2, hi3, hi4 = st.columns(4)

        with hi1:
            st.markdown("**Emergency Fund**")
            ef_target = 6
            st.progress(min(ef_months / ef_target, 1.0))
            st.caption(f"{ef_months:.1f} / {ef_target} months")

        with hi2:
            st.markdown("**Savings Rate**")
            sr_target = 20
            st.progress(min(sr / sr_target, 1.0))
            st.caption(f"{sr:.1f}% / {sr_target}% target")

        with hi3:
            st.markdown("**Debt-to-Income**")
            dti = profile.debt_to_income_ratio()
            st.progress(min(dti / 50, 1.0))
            color = "🟢" if dti < 20 else "🟡" if dti < 36 else "🔴"
            st.caption(f"{dti:.0f}% {color}")

        with hi4:
            st.markdown("**Paycheck Status**")
            if profile.paycheck_to_paycheck:
                st.error("Living paycheck to paycheck ⚠️")
            else:
                st.success("Financial breathing room ✅")

        # Subscriptions
        if profile.subscriptions:
            st.markdown("---")
            st.markdown(f"**Active Subscriptions:** ${profile.total_subscriptions():,.0f}/mo")

        # Bad habits
        if profile.bad_habits:
            st.markdown(f"**Working On:** {', '.join(profile.bad_habits)}")

        # Vacation goal
        if profile.vacation_target > 0:
            st.markdown("---")
            st.markdown("### 🏖️ Vacation Goal")
            st.progress(min(profile.vacation_fund / profile.vacation_target, 1.0))
            st.caption(
                f"${profile.vacation_fund:,.0f} / ${profile.vacation_target:,.0f} saved "
                f"({profile.vacation_deadline_months} months to go)"
            )

        # AI recommendations
        st.markdown("---")
        st.markdown("### 🎯 Richy's Recommendations")

        priorities = []
        if ef_months < 1:
            priorities.append("🚨 **URGENT:** Build a $1,000 mini emergency fund ASAP")
        elif ef_months < 3:
            priorities.append("⚠️ Build emergency fund to 3 months of expenses")
        elif ef_months < 6:
            priorities.append("📈 Continue building emergency fund to 6 months")

        high_rate = {k: v for k, v in profile.debt_interest_rates.items() if v > 0.10}
        if high_rate:
            worst = max(high_rate, key=high_rate.get)
            priorities.append(
                f"🔥 Attack high-interest debt: **{worst}** @ {high_rate[worst]*100:.0f}%"
            )

        if profile.paycheck_to_paycheck:
            priorities.append("💡 Try the **Paycheck Escape Plan** — chat with Richy about it!")

        if sr < 20:
            priorities.append(f"💰 Increase savings rate from {sr:.0f}% to 20%")

        if surplus > 0 and not profile.debts:
            priorities.append("📈 Start investing — even $100/month in an index fund builds wealth")

        if not priorities:
            priorities.append("✅ You're in great shape! Focus on growing investments")

        for p in priorities:
            st.markdown(f"- {p}")

        # LLM advice
        resp = ask_llm(
            client,
            system_prompt=(
                "You are Agent Richy. Based on this user's finances, give 3 specific, "
                "actionable recommendations with dollar amounts. Empathetic and practical. "
                "Under 200 words."
            ),
            user_message=(
                f"Income: ${profile.monthly_income:,.0f}/mo, "
                f"Expenses: ${profile.monthly_expenses:,.0f}/mo, "
                f"Surplus: ${surplus:,.0f}/mo, "
                f"EF: ${profile.emergency_fund:,.0f} ({ef_months:.1f} months), "
                f"Debt: {profile.debts or 'None'}, Age: {profile.age}"
            ),
        )
        if resp:
            st.markdown("### 🤖 Personalized AI Advice")
            with st.chat_message("assistant", avatar="💰"):
                st.markdown(resp)
