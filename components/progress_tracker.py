"""Progress tracking component — visual progress bars and module completion."""

import streamlit as st
from config import COLORS


def render_progress_bar(completed: int, total: int, label: str = "") -> None:
    """Render a premium styled progress bar.

    Args:
        completed: Number of completed items.
        total: Total number of items.
        label: Optional label text.
    """
    pct = completed / total if total > 0 else 0
    pct_display = int(pct * 100)

    display_label = label or f"{completed}/{total} completed"

    st.markdown(f"""
    <div style="margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">{display_label}</span>
            <span style="color: {COLORS['text_primary']}; font-size: 0.8rem; font-weight: 600;">{pct_display}%</span>
        </div>
        <div style="background: {COLORS['navy_card']}; border-radius: 8px; height: 8px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, {COLORS['blue']}, {COLORS['gold']});
                        width: {pct_display}%; height: 100%; border-radius: 8px;
                        transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_module_progress(module_title: str, module_icon: str,
                           completed: int, total: int,
                           badges: list[str] = None) -> None:
    """Render module progress with badge display.

    Args:
        module_title: Module name.
        module_icon: Module emoji icon.
        completed: Lessons completed.
        total: Total lessons in module.
        badges: List of earned badge emojis.
    """
    is_complete = completed >= total

    st.markdown(f"""
    <div class="module-card" style="{'border-color: ' + COLORS['gold'] + ';' if is_complete else ''}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 2rem;">{module_icon}</span>
                <div>
                    <div style="font-weight: 700; color: {COLORS['text_primary']};">{module_title}</div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">
                        {completed}/{total} lessons
                    </div>
                </div>
            </div>
            <div>
                {"🏆" if is_complete else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_progress_bar(completed, total)

    if badges:
        badge_html = " ".join(
            f'<span class="achievement-badge">{b}</span>' for b in badges
        )
        st.markdown(badge_html, unsafe_allow_html=True)


def render_achievement_badges(earned: list[str], available: list[str]) -> None:
    """Render earned and locked achievement badges.

    Args:
        earned: List of earned badge emojis.
        available: List of all possible badge emojis.
    """
    html = ""
    for badge in available:
        if badge in earned:
            html += f'<span class="achievement-badge">{badge}</span>'
        else:
            html += f'<span class="achievement-badge locked">{badge}</span>'

    st.markdown(f'<div style="margin: 0.5rem 0;">{html}</div>', unsafe_allow_html=True)


def render_onboarding_progress(current_step: int, total_steps: int) -> None:
    """Render onboarding step progress.

    Args:
        current_step: Current step number (1-based).
        total_steps: Total number of steps.
    """
    steps_html = ""
    for i in range(1, total_steps + 1):
        if i < current_step:
            color = COLORS["green"]
            icon = "✅"
        elif i == current_step:
            color = COLORS["blue"]
            icon = f"<strong>{i}</strong>"
        else:
            color = COLORS["text_muted"]
            icon = str(i)

        steps_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
            <div style="width: 36px; height: 36px; border-radius: 50%;
                        background: {color}20; border: 2px solid {color};
                        display: flex; align-items: center; justify-content: center;
                        color: {color}; font-size: 0.85rem; font-weight: 600;">
                {icon}
            </div>
        </div>
        """
        if i < total_steps:
            line_color = COLORS["green"] if i < current_step else COLORS["border"]
            steps_html += f"""
            <div style="flex: 1; height: 2px; background: {line_color};
                        align-self: center; margin: 0 4px;"></div>
            """

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center;
                padding: 1rem 2rem; margin-bottom: 1.5rem;">
        {steps_html}
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"Step {current_step} of {total_steps}")
