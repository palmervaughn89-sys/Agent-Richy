"""Video player component — renders video lessons from video_data.py structure."""

import re
import streamlit as st
from config import COLORS
from video_data import format_duration


def _extract_youtube_id(url: str) -> str | None:
    """Extract a YouTube video ID from various URL formats."""
    patterns = [
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def _is_placeholder(url: str) -> bool:
    """Return True if the URL is still a placeholder."""
    return not url or url.startswith("PLACEHOLDER")


def render_video_player(lesson: dict) -> None:
    """Render the video embed for a lesson dict from video_data.py.

    Handles YouTube iframes, MP4 via st.video, and placeholder fallback.
    """
    url = lesson.get("video_url", "")
    video_type = lesson.get("video_type", "youtube")
    title = lesson.get("title", "Lesson")
    duration = format_duration(lesson.get("duration_seconds", 0))

    if _is_placeholder(url):
        # Graceful placeholder card
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border: 2px dashed {COLORS['gold']}60;
                    border-radius: 16px; padding: 3rem 2rem; text-align: center;
                    margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">🎬</div>
            <div style="font-size: 1.2rem; font-weight: 600; color: {COLORS['text_primary']};
                        margin-bottom: 0.5rem;">
                Video Coming Soon!
            </div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.95rem;">
                We're creating an awesome video for <strong>{title}</strong>.<br>
                Check back soon — it'll be worth the wait! ⏱️ {duration}
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if video_type == "youtube":
        vid_id = _extract_youtube_id(url)
        embed_url = f"https://www.youtube.com/embed/{vid_id}" if vid_id else url
        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;
                    border-radius: 14px; margin: 0.5rem 0 1rem;">
            <iframe width="100%" height="400" src="{embed_url}"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                           border: none; border-radius: 14px;">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    else:
        # MP4 / direct file
        st.video(url)


def render_lesson_card(lesson: dict, index: int, completed: bool = False,
                       active: bool = False) -> None:
    """Render a single lesson row in the module lesson list (display only, no button).

    Args:
        lesson: Lesson dict from video_data.py.
        index: 1-based lesson number.
        completed: Whether the user finished this lesson.
        active: Whether this lesson is currently selected.
    """
    emoji = lesson.get("thumbnail_emoji", "📺")
    title = lesson.get("title", "Lesson")
    duration = format_duration(lesson.get("duration_seconds", 0))
    status = "✅" if completed else "⭕"
    border_color = COLORS["gold"] if active else COLORS["border"]
    bg = f"{COLORS['gold']}10" if active else COLORS["navy_card"]

    st.markdown(f"""
    <div style="background: {bg}; border: 1px solid {border_color};
                border-radius: 12px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
                display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.4rem;">{emoji}</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: {COLORS['text_primary']}; font-size: 1rem;">
                {index}. {title}
            </div>
            <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">
                ⏱️ {duration}
            </div>
        </div>
        <span style="font-size: 1.2rem;">{status}</span>
    </div>
    """, unsafe_allow_html=True)
