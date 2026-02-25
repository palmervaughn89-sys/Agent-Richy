"""Chat with Richy — AI-powered conversational financial advisor."""

import streamlit as st
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import get_openai_client, format_currency

st.set_page_config(page_title="Chat with Richy", page_icon="🤖", layout="wide")

# ── Session state guards ─────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.warning("Please start from the **Home** page to set up your profile first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "llm_client" not in st.session_state:
    st.session_state.llm_client = get_openai_client()

profile: UserProfile = st.session_state.profile

# ── Build system prompt with user context ────────────────────────────────
def _build_system_prompt() -> str:
    ctx_parts = [
        f"Name: {profile.name}",
        f"Age: {profile.age}",
        f"Type: {'youth' if profile.is_youth() else 'adult'}",
    ]
    if profile.monthly_income:
        ctx_parts.append(f"Monthly income: ${profile.monthly_income:,.0f}")
        ctx_parts.append(f"Monthly expenses: ${profile.monthly_expenses:,.0f}")
        surplus = profile.monthly_surplus()
        ctx_parts.append(f"Monthly surplus: ${surplus:,.0f}")
    if profile.savings_balance:
        ctx_parts.append(f"Savings: ${profile.savings_balance:,.0f}")
    if profile.emergency_fund:
        ctx_parts.append(f"Emergency fund: ${profile.emergency_fund:,.0f} ({profile.months_of_emergency():.1f} months)")
    if profile.debts:
        debt_strs = [f"{k}: ${v:,.0f}" for k, v in profile.debts.items()]
        ctx_parts.append(f"Debts: {', '.join(debt_strs)}")
    if profile.credit_score:
        ctx_parts.append(f"Credit score: {profile.credit_score}")
    if profile.bad_habits:
        ctx_parts.append(f"Working on habits: {', '.join(profile.bad_habits)}")
    if profile.is_youth():
        if profile.talents:
            ctx_parts.append(f"Talents: {', '.join(profile.talents)}")
        if profile.side_hustles:
            ctx_parts.append(f"Side hustles: {', '.join(profile.side_hustles)}")

    user_ctx = "; ".join(ctx_parts)

    if profile.is_youth():
        persona = (
            "You are Agent Richy, an enthusiastic, encouraging financial coach for "
            "teenagers and young people. You make money topics fun and relatable. "
            "Use simple language, real-world examples teens can relate to, and emojis. "
            "Encourage saving, earning, and smart spending. "
        )
    else:
        persona = (
            "You are Agent Richy, a knowledgeable, empathetic financial advisor for "
            "adults. Many of your users are struggling paycheck-to-paycheck. "
            "Give clear, actionable advice with concrete numbers and steps. "
            "Be encouraging but honest. Never judge — always help. "
        )

    return (
        f"{persona}\n\n"
        f"User context: {user_ctx}\n\n"
        "Keep responses concise (under 250 words) unless the user asks for detail. "
        "Use bullet points and formatting for clarity. "
        "If you reference calculations, show the math briefly."
    )


# ── Page header ──────────────────────────────────────────────────────────
st.markdown("## 🤖 Chat with Agent Richy")

client = st.session_state.llm_client
has_ai = client is not None

if has_ai:
    st.caption("💡 AI-powered — ask me anything about money, debt, investing, budgeting, or your finances!")
else:
    st.caption("📚 Running in offline mode — I'll give you pre-built advice. Set `OPENAI_API_KEY` for full AI chat.")

# ── Suggested questions ──────────────────────────────────────────────────
if not st.session_state.chat_history:
    with st.chat_message("assistant", avatar="💰"):
        st.markdown(
            f"Hey **{profile.name}**! I'm Richy, your financial coach. 💰\n\n"
            "Ask me anything, or try one of these:"
        )

    if profile.is_youth():
        suggestions = [
            "How can I start earning money as a teenager?",
            "What's compound interest and why should I care?",
            "How do I budget my allowance and job income?",
            "What are the best ways to save for a car?",
            "How can I turn my hobbies into a side hustle?",
        ]
    else:
        suggestions = [
            "How do I escape the paycheck-to-paycheck cycle?",
            "What should I do with my first $1,000 in savings?",
            "How do I start investing with a small amount?",
            "Should I pay off debt or save first?",
            "How much do I need for an emergency fund?",
            "Help me create a 90-day financial action plan",
        ]

    cols = st.columns(min(len(suggestions), 3))
    for i, q in enumerate(suggestions):
        col = cols[i % len(cols)]
        with col:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.rerun()

# ── Display chat history ─────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    avatar = "💰" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Chat input ───────────────────────────────────────────────────────────
user_input = st.chat_input("Ask Richy anything about your finances...")

if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant", avatar="💰"):
        if has_ai:
            try:
                system_prompt = _build_system_prompt()
                messages = [{"role": "system", "content": system_prompt}]
                # Include recent history for context (last 10 messages)
                for msg in st.session_state.chat_history[-10:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                with st.spinner("Richy is thinking..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=800,
                        stream=True,
                    )
                    # Stream response
                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)

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
            fallback = _offline_response(user_input)
            st.markdown(fallback)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": fallback}
            )


def _offline_response(question: str) -> str:
    """Generate a helpful offline response based on keywords."""
    q = question.lower()
    if any(w in q for w in ["budget", "50/30/20", "spending"]):
        return (
            "**The 50/30/20 Rule is a great starting point:**\n\n"
            "- **50%** → Needs (rent, food, utilities, insurance)\n"
            "- **30%** → Wants (entertainment, dining out, hobbies)\n"
            "- **20%** → Savings & Debt payoff\n\n"
            "Use the **Financial Tools** page for a detailed budget simulator! 📊"
        )
    elif any(w in q for w in ["debt", "credit card", "loan", "payoff"]):
        return (
            "**Two proven debt-payoff strategies:**\n\n"
            "1. **Avalanche** — pay highest interest rate first (saves the most money)\n"
            "2. **Snowball** — pay smallest balance first (quickest wins for motivation)\n\n"
            "Either way, always pay more than minimums. "
            "Try the **Debt Destroyer** in Financial Tools! 💳"
        )
    elif any(w in q for w in ["invest", "stock", "etf", "401k", "roth"]):
        return (
            "**Investing basics:**\n\n"
            "1. First, get your employer's full 401(k) match (free money!)\n"
            "2. Build a 3-6 month emergency fund in a HYSA\n"
            "3. Max out a Roth IRA ($7,000/year)\n"
            "4. Invest in low-cost index funds (e.g., VTI, VOO)\n\n"
            "$500/mo invested at 8% for 30 years = **~$750K** 📈"
        )
    elif any(w in q for w in ["emergency", "savings", "save"]):
        return (
            "**Emergency fund priorities:**\n\n"
            "- Phase 1: Save $1,000 starter fund ASAP\n"
            "- Phase 2: Build to 3 months of expenses\n"
            "- Phase 3: Grow to 6 months for full protection\n\n"
            "Keep it in a High-Yield Savings Account (4-5% APY). "
            "Automate transfers on payday! 🏦"
        )
    elif any(w in q for w in ["paycheck", "struggling", "broke"]):
        return (
            "**Escaping paycheck-to-paycheck — a step-by-step plan:**\n\n"
            "1. Track every dollar for 2 weeks\n"
            "2. Find 3 expenses to cut ($50-$200/month is common)\n"
            "3. Build a $1,000 mini emergency fund\n"
            "4. Attack your highest-interest debt\n"
            "5. Automate savings — even $25/week adds up\n\n"
            "78% of Americans struggle with this. No shame — let's fix it! 💪"
        )
    elif any(w in q for w in ["earn", "hustle", "income", "money"]) and profile.is_youth():
        return (
            "**Ways teens can earn money:**\n\n"
            "- 🌿 Lawn care / yard work ($15-30/hr)\n"
            "- 🐾 Pet sitting / dog walking ($15-25/hr)\n"
            "- 💻 Freelance design / social media ($20-50/hr)\n"
            "- 📚 Tutoring younger students ($15-30/hr)\n"
            "- 🛒 Reselling on eBay / Mercari\n\n"
            "Check the **Learning Center** for a Side Hustle Builder! 🚀"
        )
    else:
        return (
            "Great question! Here's my general advice:\n\n"
            "**The 3 pillars of financial health:**\n"
            "1. **Earn** — maximize your income\n"
            "2. **Save** — pay yourself first (at least 20%)\n"
            "3. **Invest** — make your money work for you\n\n"
            "Try the **Financial Tools** or **Learning Center** for specific help! "
            "Set up an OpenAI API key for personalized AI-powered advice. 💡"
        )
