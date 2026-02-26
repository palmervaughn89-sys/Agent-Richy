"""Video player component — renders video lessons from video_data.py structure.

Uses the auto-detection pipeline from ``utils.video_loader`` to resolve the
best available source (local file → external URL → YouTube → placeholder).
"""

import re
import streamlit as st
from config import COLORS
from video_data import format_duration
from utils.video_loader import get_video_source


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


def render_video_player(lesson: dict) -> None:
    """Render the video embed for a lesson dict from video_data.py.

    Resolution order (handled by ``get_video_source``):
    1. Local MP4 in ``videos/shows/``
    2. External URL from ``videos/video_urls.json``
    3. YouTube or external ``video_url`` already in the lesson dict
    4. Placeholder "Coming Soon" card
    """
    source = get_video_source(lesson)
    title = lesson.get("title", "Lesson")
    duration = format_duration(lesson.get("duration_seconds", 0))

    if source["type"] == "local_file":
        # ── Play directly from local file ────────────────────────────
        st.video(source["source"])

    elif source["type"] == "youtube":
        # ── Embed YouTube video ──────────────────────────────────────
        video_url = source["source"]
        vid_id = _extract_youtube_id(video_url)
        if vid_id:
            embed_url = f"https://www.youtube.com/embed/{vid_id}"
        elif "embed/" in video_url:
            embed_url = video_url
        elif "watch?v=" in video_url:
            v_id = video_url.split("watch?v=")[1].split("&")[0]
            embed_url = f"https://www.youtube.com/embed/{v_id}"
        elif "youtu.be/" in video_url:
            v_id = video_url.split("youtu.be/")[1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{v_id}"
        else:
            embed_url = video_url

        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;
                    border-radius: 14px; margin: 0.5rem 0 1rem;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <iframe width="100%" height="450" src="{embed_url}"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                           border: none; border-radius: 14px;">
            </iframe>
        </div>
        """, unsafe_allow_html=True)

    elif source["type"] == "external_url":
        # ── Direct URL (non-YouTube hosted MP4 or CDN) ───────────────
        st.video(source["source"])

    else:
        # ── Placeholder — Coming Soon ────────────────────────────────
        cat_color = lesson.get("category_color", COLORS["gold"])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['navy_card']} 0%, {COLORS['surface']} 100%);
                    border: 2px dashed {cat_color}60;
                    border-radius: 16px; padding: 3rem 2rem; text-align: center;
                    margin: 1rem 0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎬</div>
            <h3 style="color: {COLORS['text_primary']}; margin: 0 0 0.5rem;">
                {title} — Coming Soon!
            </h3>
            <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 1rem;">
                We're creating an awesome video just for you! Check back soon! ✨
            </p>
            <div style="margin-top: 1rem; display: inline-block;
                background: {cat_color}20; color: {cat_color};
                padding: 6px 16px; border-radius: 20px; font-size: 0.9rem;">
                ⏱️ {duration}
            </div>
        </div>
        """, unsafe_allow_html=True)


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
