"""Agent card component — agent selection and display."""

import streamlit as st
from config import AGENTS, COLORS


def render_agent_card(agent_key: str, show_sample: bool = True) -> bool:
    """Render an agent selection card. Returns True if clicked.

    Args:
        agent_key: Key from AGENTS config dict.
        show_sample: Whether to show sample question.

    Returns:
        True if the card button was clicked.
    """
    agent = AGENTS.get(agent_key, {})
    name = agent.get("name", agent_key)
    icon = agent.get("icon", "🤖")
    specialty = agent.get("specialty", "")
    tagline = agent.get("tagline", "")
    sample_q = agent.get("sample_q", "")
    color = agent.get("color", COLORS["blue"])

    st.markdown(f"""
    <div class="agent-card" style="border-left: 3px solid {color};">
        <span class="agent-icon">{icon}</span>
        <h4 style="color: {color} !important;">{name}</h4>
        <p>{tagline}</p>
    </div>
    """, unsafe_allow_html=True)

    if show_sample:
        st.caption(f"Try: \"{sample_q}\"")

    return st.button(
        f"Chat with {name}",
        key=f"agent_btn_{agent_key}",
        use_container_width=True,
    )


def render_agent_selector(current_agent: str = "coach_richy",
                          exclude: list[str] = None) -> str | None:
    """Render a compact agent switching dropdown.

    Args:
        current_agent: Currently active agent key.
        exclude: Agent keys to exclude from the dropdown.

    Returns:
        Selected agent key if changed, else None.
    """
    exclude = exclude or []
    agent_options = {
        k: f"{v['icon']} {v['name']}"
        for k, v in AGENTS.items()
        if k not in exclude
    }

    keys = list(agent_options.keys())
    labels = list(agent_options.values())

    current_idx = keys.index(current_agent) if current_agent in keys else 0

    selected_label = st.selectbox(
        "Switch Agent",
        labels,
        index=current_idx,
        key="agent_selector",
    )

    selected_key = keys[labels.index(selected_label)]
    if selected_key != current_agent:
        return selected_key
    return None


def render_active_agent_header(agent_key: str) -> None:
    """Render the active agent indicator in the chat.

    Args:
        agent_key: Currently active agent key.
    """
    agent = AGENTS.get(agent_key, {})
    name = agent.get("name", "Coach Richy")
    icon = agent.get("icon", "💰")
    color = agent.get("color", COLORS["gold"])
    specialty = agent.get("specialty", "")

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 10px 16px;
                background: linear-gradient(135deg, {COLORS['navy_card']}, {COLORS['navy_light']});
                border: 1px solid {color}30; border-radius: 14px; margin-bottom: 12px;">
        <span style="font-size: 2rem;">{icon}</span>
        <div>
            <div style="font-weight: 700; color: {color}; font-size: 1.1rem;">{name}</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">{specialty}</div>
        </div>
        <div style="margin-left: auto; padding: 4px 12px; background: {color}20;
                    border-radius: 20px; font-size: 0.75rem; color: {color};">Active</div>
    </div>
    """, unsafe_allow_html=True)
