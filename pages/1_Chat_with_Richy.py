"""Chat with Richy — THE core AI experience.

Richy is a visible animated character who:
1. Asks about your financial situation conversationally
2. Extracts financial data from the conversation
3. Builds your complete financial plan
4. Shows appropriate expressions based on context

No forms. No data entry. Just conversation → plan.
"""

import json
import re
import streamlit as st
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client, format_currency
from agent_richy.avatar import (
    get_avatar_html, get_avatar_chat_html, get_thinking_html,
    detect_expression, get_avatar_with_speech, get_sidebar_avatar,
)

st.set_page_config(page_title="Chat with Richy", page_icon="💬", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .avatar-center { display:flex; justify-content:center; align-items:center; margin:0.5rem 0; }
    .avatar-msg-row { display:flex; align-items:flex-start; gap:12px; margin-bottom:0.5rem; }
    .plan-badge {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #1a1a2e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .extraction-note {
        background: #16213e;
        border-left: 3px solid #FFD700;
        padding: 8px 12px;
        border-radius: 0 8px 8px 0;
        font-size: 0.8rem;
        color: #aaa;
        margin-top: 4px;
    }
    .richy-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px 16px;
        background: linear-gradient(135deg, rgba(255,215,0,0.05), rgba(255,165,0,0.03));
        border: 1px solid rgba(255,215,0,0.12);
        border-radius: 16px;
        margin-bottom: 12px;
    }
    .richy-header-text h2 { margin:0; }
    .richy-header-text p { margin:0; color:#aaa; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state guards ─────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.warning("Please start from the **Home** page to set up your profile first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "llm_client" not in st.session_state:
    st.session_state.llm_client = get_openai_client()
if "financial_plan" not in st.session_state:
    st.session_state.financial_plan = {}
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False
if "last_expression" not in st.session_state:
    st.session_state.last_expression = "happy"
if "extraction_log" not in st.session_state:
    st.session_state.extraction_log = []

profile: UserProfile = st.session_state.profile
client = st.session_state.llm_client
has_ai = client is not None


# ══════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT — The brain of Richy
# ══════════════════════════════════════════════════════════════════════════

def _build_system_prompt() -> str:
    """Build context-aware system prompt for Richy."""

    # Gather known data
    known = []
    if profile.name:
        known.append(f"Name: {profile.name}")
    if profile.age:
        known.append(f"Age: {profile.age}")
    if profile.monthly_income:
        known.append(f"Monthly income: ${profile.monthly_income:,.0f}")
    if profile.monthly_expenses:
        known.append(f"Monthly expenses: ${profile.monthly_expenses:,.0f}")
    if profile.savings_balance:
        known.append(f"Savings: ${profile.savings_balance:,.0f}")
    if profile.emergency_fund:
        known.append(f"Emergency fund: ${profile.emergency_fund:,.0f}")
    if profile.debts:
        for name, bal in profile.debts.items():
            rate = profile.debt_interest_rates.get(name, 0)
            known.append(f"Debt - {name}: ${bal:,.0f} @ {rate*100:.1f}%")
    if profile.credit_score:
        known.append(f"Credit score: {profile.credit_score}")
    if profile.goals:
        known.append(f"Goals: {', '.join(profile.goals)}")

    plan = st.session_state.financial_plan
    if plan:
        known.append(f"Plan already generated with sections: {', '.join(plan.keys())}")

    known_str = "; ".join(known) if known else "Nothing yet — need to ask questions"

    if profile.is_youth():
        persona = (
            "You are Agent Richy, a fun, encouraging AI financial coach for young people. "
            "You make money topics exciting and relatable. Use simple language, emojis, "
            "and real examples teens can connect with. "
        )
        discovery = (
            "Ask about: allowance, any jobs/hustles, savings, what they want to buy/save for, "
            "their interests and talents. Be enthusiastic about their potential."
        )
    else:
        persona = (
            "You are Agent Richy, a knowledgeable, empathetic AI financial advisor. "
            "Many users struggle paycheck-to-paycheck. Give clear, actionable advice "
            "with real numbers. Be encouraging but honest. Never judge."
        )
        discovery = (
            "Gather: monthly take-home income, major expenses (rent, car, utilities, food, "
            "subscriptions), debts (type, balance, interest rate, minimum payment), "
            "savings balance, emergency fund, credit score, financial goals. "
            "Ask naturally — not like a form. Space questions across messages."
        )

    return f"""{persona}

CURRENT KNOWLEDGE ABOUT USER:
{known_str}

YOUR JOB:
1. Have a natural conversation to understand their financial situation
2. {discovery}
3. When you have enough info (income, expenses, debts, goals), proactively offer to build their plan
4. Give specific, actionable advice with dollar amounts
5. After building a plan, help them refine it

IMPORTANT RULES:
- Keep responses under 300 words
- Use bullet points and formatting for clarity
- Show math when relevant
- After gathering key financial data, include a JSON block at the END of your response
  wrapped in ```json ... ``` with any data you've learned. Use this format:
  {{"monthly_income": 5000, "monthly_expenses": 3500, "savings": 2000,
    "emergency_fund": 500, "credit_score": 680,
    "debts": {{"credit_card": {{"balance": 5000, "rate": 0.22, "min_payment": 150}}}},
    "goals": ["emergency fund", "pay off credit card"],
    "budget": {{"needs": 2500, "wants": 600, "savings": 400}},
    "recommendations": ["Build $1000 emergency fund first", "Attack credit card with avalanche method"],
    "risk_level": "moderate"}}
  Only include fields you actually learned. Don't guess. Don't include the JSON block
  until you have real data from the user.
- If the user shares financial data, ALWAYS include the json extraction block
- Be conversational first, data extraction second
"""


# ══════════════════════════════════════════════════════════════════════════
#  DATA EXTRACTION — Parse AI responses for financial data
# ══════════════════════════════════════════════════════════════════════════

def _extract_financial_data(response: str) -> dict | None:
    """Extract JSON financial data from Richy's response if present."""
    # Look for ```json ... ``` blocks
    pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            return data
        except json.JSONDecodeError:
            pass
    return None


def _strip_json_block(response: str) -> str:
    """Remove the JSON extraction block from displayed response."""
    return re.sub(r"\s*```json\s*\{.*?\}\s*```\s*", "", response, flags=re.DOTALL).strip()


def _apply_extracted_data(data: dict):
    """Apply extracted financial data to profile and plan."""
    changes = []

    if "monthly_income" in data and data["monthly_income"]:
        profile.monthly_income = float(data["monthly_income"])
        changes.append(f"Income: ${profile.monthly_income:,.0f}/mo")

    if "monthly_expenses" in data and data["monthly_expenses"]:
        profile.monthly_expenses = float(data["monthly_expenses"])
        changes.append(f"Expenses: ${profile.monthly_expenses:,.0f}/mo")

    if "savings" in data and data["savings"]:
        profile.savings_balance = float(data["savings"])
        changes.append(f"Savings: ${profile.savings_balance:,.0f}")

    if "emergency_fund" in data and data["emergency_fund"]:
        profile.emergency_fund = float(data["emergency_fund"])
        changes.append(f"Emergency fund: ${profile.emergency_fund:,.0f}")

    if "credit_score" in data and data["credit_score"]:
        profile.credit_score = int(data["credit_score"])
        changes.append(f"Credit score: {profile.credit_score}")

    if "debts" in data and isinstance(data["debts"], dict):
        for name, info in data["debts"].items():
            if isinstance(info, dict):
                profile.debts[name] = float(info.get("balance", 0))
                profile.debt_interest_rates[name] = float(info.get("rate", 0))
                changes.append(f"Debt: {name} ${info.get('balance', 0):,.0f}")
            elif isinstance(info, (int, float)):
                profile.debts[name] = float(info)
                changes.append(f"Debt: {name} ${info:,.0f}")

    if "goals" in data and isinstance(data["goals"], list):
        profile.goals = data["goals"]
        changes.append(f"Goals: {', '.join(data['goals'])}")

    # Store plan components
    plan = st.session_state.financial_plan

    if "budget" in data:
        plan["budget"] = data["budget"]
        changes.append("Budget plan updated")

    if "recommendations" in data:
        plan["recommendations"] = data["recommendations"]
        changes.append("Recommendations updated")

    if "risk_level" in data:
        plan["risk_level"] = data["risk_level"]
        profile.risk_tolerance = data["risk_level"]

    # Mark assessment complete if we have key data
    if profile.monthly_income > 0 and profile.monthly_expenses > 0:
        profile.completed_assessment = True

    # Mark plan as generated if we have recommendations
    if plan.get("recommendations"):
        st.session_state.plan_generated = True

    if changes:
        st.session_state.extraction_log.append(changes)

    return changes


# ══════════════════════════════════════════════════════════════════════════
#  OFFLINE RESPONSES
# ══════════════════════════════════════════════════════════════════════════

def _offline_opening() -> str:
    """Generate the opening conversation in offline mode."""
    if profile.is_youth():
        return (
            f"Hey **{profile.name}**! 🎉 I'm Richy, your money coach!\n\n"
            "Let's talk about your money situation — it's totally casual.\n\n"
            "**Tell me:**\n"
            "- Do you get an allowance? Have a job or side hustle?\n"
            "- Are you saving for anything specific?\n"
            "- What are you into? (hobbies, skills, interests)\n\n"
            "Just tell me whatever — I'll figure out the best plan for you! 💪"
        )
    return (
        f"Hey **{profile.name}**! 💰 I'm Richy, your AI financial coach.\n\n"
        "Let's build your financial plan together — just through conversation. "
        "No forms, no spreadsheets.\n\n"
        "**Start by telling me about:**\n"
        "- Your monthly take-home pay\n"
        "- Your biggest expenses (rent, car, food)\n"
        "- Any debts you're carrying\n"
        "- What you're trying to achieve financially\n\n"
        "Share as much or as little as you want. I'll ask follow-up questions "
        "and build your plan as we go! 🚀"
    )


def _offline_response(question: str) -> str:
    """Generate helpful offline responses based on keywords."""
    q = question.lower()

    # Try to extract numbers from user message for offline data gathering
    numbers = re.findall(r'\$?([\d,]+)', q)

    if any(w in q for w in ["income", "make", "earn", "salary", "paid", "paycheck"]):
        if numbers:
            amt = float(numbers[0].replace(",", ""))
            profile.monthly_income = amt
            profile.completed_assessment = True
            return (
                f"Got it — **${amt:,.0f}/month** take-home income. 📝\n\n"
                "Now tell me about your **main expenses**:\n"
                "- Rent/mortgage?\n"
                "- Car payment?\n"
                "- Utilities, groceries, subscriptions?\n\n"
                "Just give me rough numbers — I'll build your budget!"
            )
        return (
            "What's your **monthly take-home pay**? (After taxes)\n\n"
            "Just give me the number, like '$4,500' and I'll start building your plan."
        )

    if any(w in q for w in ["expense", "spend", "rent", "bill", "cost"]):
        if numbers:
            amt = float(numbers[0].replace(",", ""))
            profile.monthly_expenses = max(profile.monthly_expenses, amt)
            return (
                f"Noted — I'm adding that to your expenses. 📝\n\n"
                "What else do you spend on each month? "
                "Tell me everything — rent, car, food, subscriptions, fun money..."
            )
        return (
            "**Walk me through your monthly spending:**\n"
            "- 🏠 Rent/mortgage: $?\n"
            "- 🚗 Car + insurance: $?\n"
            "- 🛒 Groceries: $?\n"
            "- 📱 Phone/internet: $?\n"
            "- 🎬 Entertainment/dining: $?\n\n"
            "Approximate is fine!"
        )

    if any(w in q for w in ["debt", "owe", "credit card", "loan", "student"]):
        return (
            "Let me help you tackle that debt! 💪\n\n"
            "**Tell me about each debt:**\n"
            "- Type (credit card, student loan, car, medical)\n"
            "- Balance ($)\n"
            "- Interest rate (%)\n"
            "- Minimum payment ($)\n\n"
            "I'll create a payoff strategy that saves you the most money."
        )

    if any(w in q for w in ["budget", "50/30/20", "spending plan"]):
        if profile.monthly_income > 0:
            needs = profile.monthly_income * 0.50
            wants = profile.monthly_income * 0.30
            save = profile.monthly_income * 0.20
            plan = st.session_state.financial_plan
            plan["budget"] = {"needs": needs, "wants": wants, "savings": save}
            plan["recommendations"] = [
                f"Limit needs (rent, food, bills) to ${needs:,.0f}/mo",
                f"Cap wants (fun, dining, shopping) at ${wants:,.0f}/mo",
                f"Save/invest at least ${save:,.0f}/mo",
                "Automate savings on payday",
            ]
            st.session_state.plan_generated = True
            return (
                f"**Here's your 50/30/20 budget on ${profile.monthly_income:,.0f}/mo:**\n\n"
                f"- **50% Needs:** ${needs:,.0f} (rent, food, utilities, insurance)\n"
                f"- **30% Wants:** ${wants:,.0f} (dining, entertainment, shopping)\n"
                f"- **20% Savings:** ${save:,.0f} (emergency fund, investing, debt)\n\n"
                "Check the **My Plan** page to see your full plan! 📊\n\n"
                "Want me to help you fit your actual expenses into these buckets?"
            )
        return (
            "I'd love to build your budget! First, tell me your "
            "**monthly take-home income** and I'll create your plan."
        )

    if any(w in q for w in ["invest", "stock", "401k", "roth", "index"]):
        return (
            "**Smart thinking! Here's the investing priority ladder:**\n\n"
            "1. **Employer 401(k) match** — free money, take it ALL\n"
            "2. **3-6 month emergency fund** in HYSA (4-5% APY)\n"
            "3. **Roth IRA** — $7,000/year max, tax-free growth\n"
            "4. **Index funds** — VTI, VOO, VXUS for diversification\n\n"
            "$500/mo invested at 8% for 30 years = **~$750,000** 📈\n\n"
            "Tell me about your situation and I'll give you specific recommendations!"
        )

    if any(w in q for w in ["save", "emergency", "fund"]):
        return (
            "**Emergency fund priority levels:**\n\n"
            "1. Phase 1: **$1,000** starter fund (do this FIRST)\n"
            "2. Phase 2: **3 months** of expenses\n"
            "3. Phase 3: **6 months** for full security\n\n"
            "Put it in a **High-Yield Savings Account** (4-5% APY).\n"
            "Automate transfers on payday — even $25/week builds up! 🏦\n\n"
            "What's your current savings situation?"
        )

    if any(w in q for w in ["help", "plan", "start", "where do i"]):
        return _offline_opening()

    # Default
    return (
        "I'd love to help with that! 💡\n\n"
        "To give you the best advice, tell me about:\n"
        "- Your **income** (monthly take-home)\n"
        "- Your **biggest expenses**\n"
        "- Any **debts** you're dealing with\n"
        "- Your **financial goals**\n\n"
        "The more I know, the better plan I can build! "
        "Set up an `OPENAI_API_KEY` for full AI-powered conversations. 🔑"
    )


# ══════════════════════════════════════════════════════════════════════════
#  PAGE LAYOUT
# ══════════════════════════════════════════════════════════════════════════

# ── Header with avatar ───────────────────────────────────────────────────
expression = st.session_state.last_expression

# Sidebar avatar (persistent)
with st.sidebar:
    st.markdown(
        get_sidebar_avatar(expression, profile.name or "Friend"),
        unsafe_allow_html=True,
    )
    if profile.monthly_income > 0:
        surplus = profile.monthly_surplus()
        st.metric("Monthly Surplus", f"${surplus:,.0f}")
    if st.session_state.plan_generated:
        st.success("✅ Plan ready!")
        st.page_link("pages/3_My_Plan.py", label="📊 View My Plan", use_container_width=True)
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/2_Learning_Center.py", label="📚 Learning Center", use_container_width=True)

# Main header with large avatar
st.markdown(
    f"""<div class="richy-header">
        <div>{get_avatar_html(expression, 140)}</div>
        <div class="richy-header-text">
            <h2>💬 Chat with Agent Richy</h2>
            <p>{'AI-powered — tell me about your finances and I\'ll build your plan!' if has_ai else 'Offline mode — set OPENAI_API_KEY for full AI chat. I can still help!'}</p>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

# ── Plan status indicator ────────────────────────────────────────────────
if st.session_state.plan_generated:
    st.markdown(
        '<div class="plan-badge">✅ Plan Generated — Check the My Plan page!</div>',
        unsafe_allow_html=True,
    )
elif profile.monthly_income > 0:
    st.markdown(
        '<div class="plan-badge">📝 Gathering info — keep chatting!</div>',
        unsafe_allow_html=True,
    )

# ── Opening message if no history ────────────────────────────────────────
if not st.session_state.chat_history:
    with st.chat_message("assistant", avatar="💰"):
        opening = _offline_opening()
        st.markdown(opening)

    st.session_state.chat_history.append({"role": "assistant", "content": opening})

    # Suggestion buttons
    if profile.is_youth():
        suggestions = [
            "I get $30/week allowance and work part-time",
            "I want to save for a car",
            "How can I start making money?",
            "I have $200 saved, what should I do with it?",
        ]
    else:
        suggestions = [
            "I make $4,500/month and I'm living paycheck to paycheck",
            "I have $15,000 in credit card debt",
            "Help me build a budget for my family",
            "I want to start investing but don't know where to begin",
            "I make $6,000/month with $2,000 rent — build my plan",
        ]

    cols = st.columns(min(len(suggestions), 3))
    for i, q in enumerate(suggestions):
        with cols[i % len(cols)]:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.rerun()

# ── Display chat history ─────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.chat_history):
    if i == 0 and msg["role"] == "assistant":
        continue  # Skip opening (already shown above on first load)
    avatar = "💰" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        # Strip JSON blocks from display
        display_text = _strip_json_block(msg["content"]) if msg["role"] == "assistant" else msg["content"]
        st.markdown(display_text)

# ── Chat input ───────────────────────────────────────────────────────────
user_input = st.chat_input("Tell Richy about your finances...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="💰"):
        if has_ai:
            try:
                system_prompt = _build_system_prompt()
                messages = [{"role": "system", "content": system_prompt}]
                # Recent history for context (last 20 messages for financial continuity)
                for msg in st.session_state.chat_history[-20:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                with st.spinner(""):
                    # Show thinking avatar
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown(
                        get_thinking_html(60),
                        unsafe_allow_html=True,
                    )

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000,
                        stream=True,
                    )

                    thinking_placeholder.empty()

                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            # Only show non-JSON parts during streaming
                            display = _strip_json_block(full_response)
                            placeholder.markdown(display + "▌")

                    # Final display
                    display = _strip_json_block(full_response)
                    placeholder.markdown(display)

                # Extract financial data
                extracted = _extract_financial_data(full_response)
                if extracted:
                    changes = _apply_extracted_data(extracted)
                    if changes:
                        st.markdown(
                            f'<div class="extraction-note">📊 Updated your plan: '
                            f'{", ".join(changes[:3])}'
                            f'{"..." if len(changes) > 3 else ""}</div>',
                            unsafe_allow_html=True,
                        )

                # Update expression
                st.session_state.last_expression = detect_expression(full_response)

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                fallback = _offline_response(user_input)
                st.markdown(fallback)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": fallback}
                )
        else:
            # Offline mode
            fallback = _offline_response(user_input)
            st.markdown(fallback)
            st.session_state.last_expression = detect_expression(fallback)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": fallback}
            )

    st.rerun()
