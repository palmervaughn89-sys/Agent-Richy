"""Chat — Multi-agent AI financial coaching interface."""

import streamlit as st
from styles import inject_styles
from config import COLORS, AGENTS
from utils.session import (
    init_session_state, get_profile, get_chat_history, add_message,
    apply_extracted_data, is_message_limit_reached,
)
from agents import get_agent, route_to_agent
from agents.base_agent import BaseAgent
from components.agent_card import render_active_agent_header
from utils.intent_detection import build_enriched_context
from utils.response_cache import set_session_cache, fake_thinking_delay

st.set_page_config(page_title="Chat — Agent Richy", page_icon="💬", layout="wide")
inject_styles()
init_session_state()

# ── Session guard ────────────────────────────────────────────────────────
if not st.session_state.get("onboarded"):
    st.warning("Please complete onboarding first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile = get_profile()
client = st.session_state.llm_client
llm_provider = st.session_state.get("llm_provider", "openai")
has_ai = client is not None

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2rem;">💰</div>
        <div style="font-weight: 700; color: {COLORS['gold']};">Agent Richy</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Agent switcher
    st.markdown("**Switch Agent:**")
    active_key = st.session_state.get("active_agent", "coach_richy")

    agent_options = {k: f"{v['icon']} {v['name']}" for k, v in AGENTS.items()}
    agent_keys = list(agent_options.keys())
    agent_labels = list(agent_options.values())
    current_idx = agent_keys.index(active_key) if active_key in agent_keys else 0

    selected_label = st.selectbox(
        "Agent",
        agent_labels,
        index=current_idx,
        label_visibility="collapsed",
    )
    selected_key = agent_keys[agent_labels.index(selected_label)]
    if selected_key != active_key:
        st.session_state.active_agent = selected_key
        st.rerun()

    st.markdown("---")

    # Profile summary
    st.markdown(f"**{profile.name}** · {profile.age}yr")
    if profile.monthly_income > 0:
        surplus = profile.monthly_surplus()
        st.metric("Monthly Surplus", f"${surplus:,.0f}")
    if profile.debts:
        st.metric("Total Debt", f"${profile.total_debt():,.0f}")

    if st.session_state.get("plan_generated"):
        st.success("✅ Plan ready!")
        st.page_link("pages/4_My_Plan.py", label="📋 View Plan", use_container_width=True)

    st.markdown("---")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard", use_container_width=True)
    st.page_link("pages/3_Kids_Education.py", label="🎓 Kids", use_container_width=True)

    # Message counter (free tier)
    if not st.session_state.get("is_premium"):
        from config import FREE_MESSAGE_LIMIT
        count = st.session_state.get("message_count", 0)
        remaining = max(0, FREE_MESSAGE_LIMIT - count)
        st.markdown("---")
        st.caption(f"Free messages: {remaining}/{FREE_MESSAGE_LIMIT}")
        if remaining <= 3:
            st.page_link("pages/6_Upgrade.py", label="⭐ Upgrade", use_container_width=True)

# ── Active agent ─────────────────────────────────────────────────────────
active_key = st.session_state.get("active_agent", "coach_richy")
agent = get_agent(active_key)
agent_info = AGENTS.get(active_key, {})

# Header
render_active_agent_header(active_key)

if not has_ai:
    st.info(
        "🔑 Running in offline mode — set `OPENAI_API_KEY` (or `GOOGLE_API_KEY`) for full AI conversations. "
        "I can still help with basic advice!"
    )
elif llm_provider == "gemini":
    st.caption("Powered by Google Gemini · Set `OPENAI_API_KEY` for GPT-4o")

# ── Plan status badge ────────────────────────────────────────────────────
if st.session_state.get("plan_generated"):
    st.markdown(f"""
    <div style="background: {COLORS['gold']}20; border: 1px solid {COLORS['gold']}40;
                border-radius: 10px; padding: 6px 14px; display: inline-block;
                color: {COLORS['gold']}; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
        ✅ Plan Generated — Check My Plan page!
    </div>
    """, unsafe_allow_html=True)
elif profile.monthly_income > 0:
    st.markdown(f"""
    <div style="background: {COLORS['blue']}20; border: 1px solid {COLORS['blue']}40;
                border-radius: 10px; padding: 6px 14px; display: inline-block;
                color: {COLORS['blue']}; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
        📝 Gathering info — keep chatting!
    </div>
    """, unsafe_allow_html=True)


# ── Opening message (per agent) ──────────────────────────────────────────
history = get_chat_history(active_key)

if not history:
    # Generate opening message
    if hasattr(agent, 'get_opening_message'):
        opening = agent.get_opening_message(profile)
    else:
        opening = agent._offline_response("hello", profile)

    add_message("assistant", opening, active_key)
    history = get_chat_history(active_key)

    # Display opening
    with st.chat_message("assistant"):
        st.markdown(opening)

    # Suggestion buttons
    if active_key == "coach_richy":
        if profile.is_youth():
            suggestions = [
                "I get $30/week allowance and work part-time",
                "I want to save for a car",
                "How can I start making money?",
            ]
        else:
            suggestions = [
                "I make $4,500/month and I'm living paycheck to paycheck",
                "I have $15,000 in credit card debt",
                "Help me build a budget for my family",
                "I want to start investing but don't know where to begin",
            ]
    elif active_key == "budget_bot":
        suggestions = ["Here's my monthly breakdown...", "Help me cut expenses",
                       "Create a zero-based budget for me"]
    elif active_key == "invest_intel":
        suggestions = ["How should I invest $500/month?", "What's a Roth IRA?",
                       "Build me a portfolio for moderate risk"]
    elif active_key == "debt_destroyer":
        suggestions = ["I have 3 credit cards with debt", "Avalanche vs snowball?",
                       "I owe $50K in student loans"]
    elif active_key == "savings_sage":
        suggestions = ["Help me build an emergency fund", "I can't seem to save anything",
                       "Savings challenge ideas?"]
    elif active_key == "kid_coach":
        suggestions = ["How can I make money as a kid?", "What should I do with $100?",
                       "Teach me about investing"]
    else:
        suggestions = ["Help me with my finances"]

    cols = st.columns(min(len(suggestions), 3))
    for i, q in enumerate(suggestions):
        with cols[i % len(cols)]:
            if st.button(q, key=f"suggest_{active_key}_{i}", use_container_width=True):
                add_message("user", q, active_key)
                st.rerun()
else:
    # Display chat history
    for i, msg in enumerate(history):
        if i == 0 and msg["role"] == "assistant":
            # Show first message normally
            pass
        with st.chat_message(msg["role"]):
            display = (BaseAgent.strip_json_block(msg["content"])
                       if msg["role"] == "assistant" else msg["content"])
            st.markdown(display)


# ── Agent routing suggestion ─────────────────────────────────────────────
def _check_routing(user_msg: str, enriched: dict = None):
    """Check if we should suggest a different agent."""
    # Use enriched context if available, fallback to basic detection
    if enriched and enriched.get("suggested_agent"):
        suggested = enriched["suggested_agent"]
    else:
        suggested = route_to_agent(user_msg, active_key)
    if suggested != active_key:
        suggested_info = AGENTS.get(suggested, {})
        st.info(
            f"💡 **{suggested_info.get('name', 'Specialist')}** "
            f"({suggested_info.get('icon', '🤖')}) might be better for this topic. "
            f"Switch agents in the sidebar!"
        )


# ── Chat input ───────────────────────────────────────────────────────────
user_input = st.chat_input(f"Ask {agent_info.get('name', 'Richy')}...")

if user_input:
    # Check message limit
    if is_message_limit_reached():
        st.warning(
            f"You've reached the free tier limit of {st.session_state.get('message_count', 0)} messages. "
            "Upgrade to Premium for unlimited chats!"
        )
        st.page_link("pages/6_Upgrade.py", label="⭐ Upgrade to Premium",
                     use_container_width=True)
        st.stop()

    add_message("user", user_input, active_key)
    with st.chat_message("user"):
        st.markdown(user_input)

    # ── Smart pipeline: cache → intent → calculator → RAG → LLM ─────
    enriched = build_enriched_context(user_input)

    with st.chat_message("assistant"):
        # Fast path: cached response (pre-written or session)
        if enriched.get("cached_response"):
            fake_thinking_delay()
            cached = enriched["cached_response"]
            st.markdown(cached)
            add_message("assistant", cached, active_key)
            set_session_cache(user_input, cached)
        elif has_ai:
            try:
                # Build system prompt with enriched context
                base_system = agent.get_system_prompt(
                    user_profile=agent._profile_to_dict(profile),
                    financial_plan=st.session_state.get("financial_plan", {}),
                )

                # Inject calculator results + RAG context into system prompt
                system_prompt = base_system
                if enriched.get("enriched_prompt"):
                    system_prompt += (
                        "\n\n--- CONTEXT (use this data in your response) ---\n"
                        + enriched["enriched_prompt"]
                    )

                messages = [{"role": "system", "content": system_prompt}]
                for msg in history[-20:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                messages.append({"role": "user", "content": user_input})

                # Show custom spinner
                spinner_placeholder = st.empty()
                spinner_placeholder.markdown(f"""
                <div class="custom-spinner">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <span style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">
                        {agent_info.get('name', 'Agent')} is thinking...
                    </span>
                </div>
                """, unsafe_allow_html=True)

                if llm_provider == "gemini":
                    # Gemini path (streaming)
                    import google.generativeai as genai
                    model = genai.GenerativeModel(
                        "gemini-1.5-flash",
                        system_instruction=system_prompt,
                    )
                    history_parts = []
                    for msg in history[-20:]:
                        role = "user" if msg["role"] == "user" else "model"
                        history_parts.append({"role": role, "parts": [msg["content"]]})
                    chat = model.start_chat(history=history_parts)
                    spinner_placeholder.empty()

                    full_response = ""
                    placeholder = st.empty()
                    gemini_resp = chat.send_message(user_input, stream=True)
                    for chunk in gemini_resp:
                        if chunk.text:
                            full_response += chunk.text
                            display = BaseAgent.strip_json_block(full_response)
                            placeholder.markdown(display + "▌")

                    display = BaseAgent.strip_json_block(full_response)
                    placeholder.markdown(display)
                else:
                    # OpenAI path (streaming)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000,
                        stream=True,
                    )

                    spinner_placeholder.empty()

                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            display = BaseAgent.strip_json_block(full_response)
                            placeholder.markdown(display + "▌")

                    display = BaseAgent.strip_json_block(full_response)
                    placeholder.markdown(display)

                # Extract financial data
                extracted = BaseAgent.extract_financial_data(full_response)
                if extracted:
                    changes = apply_extracted_data(extracted)
                    if changes:
                        st.markdown(f"""
                        <div style="background: {COLORS['navy_card']}; border-left: 3px solid {COLORS['gold']};
                                    padding: 8px 12px; border-radius: 0 10px 10px 0;
                                    font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-top: 8px;">
                            📊 Updated: {", ".join(changes[:3])}{"..." if len(changes) > 3 else ""}
                        </div>
                        """, unsafe_allow_html=True)

                add_message("assistant", full_response, active_key)
                set_session_cache(user_input, full_response)

                # Check routing with enriched context
                _check_routing(user_input, enriched)

            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"LLM error: {e}")
                st.warning("Oops! Something went wrong connecting to AI. Using offline mode.")
                fallback = agent._offline_response(user_input, profile)
                st.markdown(fallback)
                add_message("assistant", fallback, active_key)
        else:
            # Offline mode
            fallback = agent._offline_response(user_input, profile)
            st.markdown(fallback)
            add_message("assistant", fallback, active_key)

    # ── Follow-up suggestion buttons ─────────────────────────────────
    intent_key = enriched.get("intent", {}).get("intent", "general") if enriched else "general"
    follow_ups = _get_follow_up_suggestions(intent_key)
    if follow_ups:
        st.markdown(f"""
        <div style="color: {COLORS['text_muted']}; font-size: 0.8rem; margin-top: 8px;">
            💡 Follow-up ideas:
        </div>
        """, unsafe_allow_html=True)
        cols = st.columns(min(len(follow_ups), 3))
        for i, q in enumerate(follow_ups):
            with cols[i % len(cols)]:
                if st.button(q, key=f"followup_{i}", use_container_width=True):
                    add_message("user", q, active_key)
                    st.rerun()

    st.rerun()


def _get_follow_up_suggestions(intent: str) -> list[str]:
    """Return context-aware follow-up suggestions based on intent."""
    suggestions_map = {
        "compound_interest": [
            "What if I increase my contribution?",
            "How does inflation affect this?",
            "Show me Roth IRA vs taxable growth",
        ],
        "debt_payoff": [
            "Compare snowball vs avalanche for me",
            "Should I consolidate my debt?",
            "Can I invest while paying off debt?",
        ],
        "debt_strategy": [
            "Help me list all my debts",
            "What about balance transfer cards?",
            "How much extra should I pay monthly?",
        ],
        "budget": [
            "How can I cut my expenses?",
            "Audit my subscriptions",
            "What's the envelope method?",
        ],
        "emergency_fund": [
            "Where should I keep my emergency fund?",
            "How do I build it faster?",
            "What counts as an emergency?",
        ],
        "investing": [
            "What's a good starter portfolio?",
            "How do index funds work?",
            "Roth IRA vs Traditional — which is better?",
        ],
        "savings_goal": [
            "How can I save faster?",
            "Best high-yield savings accounts?",
            "Automate my savings plan",
        ],
    }
    return suggestions_map.get(intent, [])
