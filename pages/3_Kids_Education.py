"""Kids Education — Agent Richy's Money School 🎓

Video-based financial literacy for young learners with quizzes, progress
tracking, and achievement badges.
"""

import os
import streamlit as st
from styles import inject_styles
from config import COLORS
from config import FREE_VIDEO_MODULES, FREE_VIDEO_LESSONS
from utils.session import init_session_state, get_profile
from video_data import (
    VIDEO_MODULES, MODULE_BADGES, MEGA_BADGE,
    format_duration, get_total_lessons,
)
from components.video_player import render_video_player, render_lesson_card
from components.quiz import render_quiz

st.set_page_config(page_title="Money School — Agent Richy", page_icon="🎓", layout="wide")
inject_styles()
init_session_state()

# ── Onboarding guard ─────────────────────────────────────────────────────
if not st.session_state.get("onboarded"):
    st.warning("Please complete onboarding first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile = get_profile()
is_premium = st.session_state.get("is_premium", False)

# ── Session helpers ──────────────────────────────────────────────────────
completed = st.session_state.get("completed_lessons", set())
if not isinstance(completed, set):
    completed = set(completed)
    st.session_state["completed_lessons"] = completed

total_lessons = get_total_lessons()
total_completed = len(completed)


def _complete_lesson(lid: str) -> None:
    """Mark a lesson completed and award badges."""
    completed.add(lid)
    st.session_state["completed_lessons"] = completed
    _check_badges()


def _check_badges() -> None:
    """Award module badges and the mega badge when eligible."""
    badges = st.session_state.get("earned_badges", [])
    for mod in VIDEO_MODULES:
        mid = mod["module_id"]
        lesson_ids = {l["lesson_id"] for l in mod["lessons"]}
        if lesson_ids.issubset(completed):
            badge_info = MODULE_BADGES.get(mid)
            if badge_info:
                badge_str = f"{badge_info['icon']} {badge_info['name']}"
                if badge_str not in badges:
                    badges.append(badge_str)
                    st.toast(f"Badge unlocked: {badge_str}!", icon="🏆")
    # Mega badge
    all_ids = {l["lesson_id"] for m in VIDEO_MODULES for l in m["lessons"]}
    if all_ids.issubset(completed):
        mega = f"{MEGA_BADGE['icon']} {MEGA_BADGE['name']}"
        if mega not in badges:
            badges.append(mega)
            st.toast(f"🎉 MEGA BADGE: {mega}!", icon="🏆")
    st.session_state["earned_badges"] = badges


# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0 1rem;">
    <h1 style="margin: 0; font-size: 2.2rem;">
        <span style="color: {COLORS['gold']};">🎓</span>
        Agent Richy's Money School
    </h1>
    <p style="color: {COLORS['text_secondary']}; font-size: 1.1rem; margin: 0.5rem 0 0;">
        Fun video lessons that teach you to be smart with money!
    </p>
</div>
""", unsafe_allow_html=True)

# ── Global progress bar ──────────────────────────────────────────────────
pct = int(total_completed / total_lessons * 100) if total_lessons else 0
st.markdown(f"""
<div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['border']};
            border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 0.5rem;">
        <span style="font-weight: 700; color: {COLORS['text_primary']}; font-size: 1.05rem;">
            Your Progress
        </span>
        <span style="color: {COLORS['gold']}; font-weight: 700; font-size: 1.05rem;">
            {total_completed} / {total_lessons} lessons
        </span>
    </div>
    <div style="background: {COLORS['border']}; border-radius: 10px; height: 14px;
                overflow: hidden;">
        <div style="background: linear-gradient(90deg, {COLORS['gold']}, {COLORS['gold_light']});
                    height: 100%; width: {pct}%; border-radius: 10px;
                    transition: width 0.4s ease;"></div>
    </div>
    <div style="text-align: right; color: {COLORS['text_muted']}; font-size: 0.8rem;
                margin-top: 0.35rem;">
        {"🚀 Keep it up!" if 0 < pct < 100 else "🌟 All done — you're a superstar!" if pct == 100 else "Let's get started!"}
    </div>
</div>
""", unsafe_allow_html=True)

# ── My Badges ────────────────────────────────────────────────────────────
badges = st.session_state.get("earned_badges", [])
if badges:
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['gold']}30;
                border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <div style="font-weight: 700; color: {COLORS['gold']}; margin-bottom: 0.5rem;
                    font-size: 1.05rem;">🏅 My Badges</div>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            {"".join(f'<span style="background: {COLORS["gold"]}18; border: 1px solid {COLORS["gold"]}40; border-radius: 20px; padding: 6px 14px; font-size: 0.9rem; font-weight: 600; color: {COLORS["gold"]};">{b}</span>' for b in badges)}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Stats row ────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border-radius: 12px; padding: 1rem;
                text-align: center; border: 1px solid {COLORS['border']};">
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['gold']};">
            {total_completed}
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">Lessons Done</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    modules_done = sum(
        1 for m in VIDEO_MODULES
        if all(l["lesson_id"] in completed for l in m["lessons"])
    )
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border-radius: 12px; padding: 1rem;
                text-align: center; border: 1px solid {COLORS['border']};">
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['blue']};">
            {modules_done} / {len(VIDEO_MODULES)}
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">Modules Complete</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border-radius: 12px; padding: 1rem;
                text-align: center; border: 1px solid {COLORS['border']};">
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['green']};">
            {len(badges)}
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">Badges Earned</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Module grid ──────────────────────────────────────────────────────────
# Two-column responsive module cards
for row_start in range(0, len(VIDEO_MODULES), 2):
    cols = st.columns(2)
    for col_idx, col in enumerate(cols):
        mod_idx = row_start + col_idx
        if mod_idx >= len(VIDEO_MODULES):
            break
        module = VIDEO_MODULES[mod_idx]
        mid = module["module_id"]
        lessons = module["lessons"]
        mod_completed = sum(1 for l in lessons if l["lesson_id"] in completed)
        mod_total = len(lessons)
        mod_pct = int(mod_completed / mod_total * 100) if mod_total else 0
        is_module_done = mod_completed == mod_total
        badge_info = MODULE_BADGES.get(mid, {})

        with col:
            # Check free-tier access
            module_locked = (not is_premium and mod_idx >= FREE_VIDEO_MODULES)

            if module_locked:
                # Locked module card
                st.markdown(f"""
                <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['gold']}40;
                            border-radius: 16px; padding: 1.25rem; margin-bottom: 0.25rem;
                            min-height: 200px; opacity: 0.6; position: relative;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.75rem;">
                        <span style="font-size: 2rem;">{module['icon']}</span>
                        <div>
                            <div style="font-weight: 700; font-size: 1.15rem; color: {COLORS['text_primary']};">
                                🔒 {module['title']}
                            </div>
                            <div style="font-size: 0.8rem; color: {COLORS['text_muted']};">
                                Ages {module['age_range']} · {mod_total} lessons
                            </div>
                        </div>
                    </div>
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.92rem;
                                margin-bottom: 0.75rem;">{module['description']}</div>
                    <div style="text-align: center; padding: 0.5rem; color: {COLORS['gold']};
                                font-weight: 600; font-size: 0.9rem;">
                        ⭐ Upgrade to Premium to unlock!
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.page_link("pages/6_Upgrade.py", label="⭐ Unlock All Modules",
                             use_container_width=True)
                continue

            # Module card
            st.markdown(f"""
            <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['border']};
                        border-radius: 16px; padding: 1.25rem; margin-bottom: 0.25rem;
                        min-height: 200px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.75rem;">
                    <span style="font-size: 2rem;">{module['icon']}</span>
                    <div>
                        <div style="font-weight: 700; font-size: 1.15rem; color: {COLORS['text_primary']};">
                            {module['title']}
                        </div>
                        <div style="font-size: 0.8rem; color: {COLORS['text_muted']};">
                            Ages {module['age_range']} · {mod_total} lessons
                        </div>
                    </div>
                    {"<span style='margin-left: auto; font-size: 1.4rem;'>✅</span>" if is_module_done else ""}
                </div>
                <div style="color: {COLORS['text_secondary']}; font-size: 0.92rem;
                            margin-bottom: 0.75rem;">{module['description']}</div>
                <div style="background: {COLORS['border']}; border-radius: 8px; height: 10px;
                            overflow: hidden; margin-bottom: 0.35rem;">
                    <div style="background: linear-gradient(90deg, {COLORS['gold']}, {COLORS['gold_light']});
                                height: 100%; width: {mod_pct}%; border-radius: 8px;"></div>
                </div>
                <div style="text-align: right; font-size: 0.78rem; color: {COLORS['text_muted']};">
                    {mod_completed}/{mod_total} complete
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_label = "✅ Complete!" if is_module_done else (
                "▶️ Continue" if mod_completed > 0 else "🚀 Start Learning")
            if st.button(btn_label, key=f"mod_btn_{mid}", use_container_width=True,
                         disabled=is_module_done):
                st.session_state["active_module"] = mid
                st.session_state.pop("active_lesson", None)
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Active module / lesson view ──────────────────────────────────────────
active_mid = st.session_state.get("active_module")
if active_mid:
    module = None
    for m in VIDEO_MODULES:
        if m["module_id"] == active_mid:
            module = m
            break

    if module:
        lessons = module["lessons"]
        active_lid = st.session_state.get("active_lesson")

        st.markdown("---")
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
            <span style="font-size: 2rem;">{module['icon']}</span>
            <div>
                <div style="font-weight: 800; font-size: 1.4rem; color: {COLORS['text_primary']};">
                    {module['title']}
                </div>
                <div style="color: {COLORS['text_secondary']}; font-size: 0.95rem;">
                    {module['description']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← Back to all modules", key="back_to_modules"):
            st.session_state.pop("active_module", None)
            st.session_state.pop("active_lesson", None)
            st.rerun()

        # Lesson list
        st.markdown(f"**Lessons** ({sum(1 for l in lessons if l['lesson_id'] in completed)}/{len(lessons)} complete)")

        # Determine free-tier module index
        _mod_indices = {m['module_id']: i for i, m in enumerate(VIDEO_MODULES)}
        _current_mod_idx = _mod_indices.get(active_mid, 0)

        for idx, lesson in enumerate(lessons):
            lid = lesson["lesson_id"]
            is_done = lid in completed
            is_active = lid == active_lid

            # Free-tier lesson limit within free modules
            lesson_locked = (not is_premium
                             and _current_mod_idx < FREE_VIDEO_MODULES
                             and idx >= FREE_VIDEO_LESSONS)

            render_lesson_card(lesson, idx + 1, completed=is_done, active=is_active)

            if lesson_locked:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.3rem; color: {COLORS['gold']};
                            font-size: 0.85rem; font-weight: 600;">
                    🔒 Premium lesson — <a href="/Upgrade" style="color: {COLORS['gold']};">upgrade to unlock</a>
                </div>
                """, unsafe_allow_html=True)
                continue

            btn_text = "✅ Completed" if is_done else ("📖 Watching..." if is_active else "▶️ Watch")
            if st.button(btn_text, key=f"les_btn_{lid}",
                         use_container_width=True, disabled=(is_done and not is_active)):
                st.session_state["active_lesson"] = lid
                st.rerun()

        # ── Lesson detail ────────────────────────────────────────────────
        if active_lid:
            lesson = None
            for l in lessons:
                if l["lesson_id"] == active_lid:
                    lesson = l
                    break

            if lesson:
                st.markdown("---")
                lid = lesson["lesson_id"]
                dur = format_duration(lesson.get("duration_seconds", 0))

                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: {COLORS['text_primary']};">
                        {lesson['thumbnail_emoji']} {lesson['title']}
                    </div>
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.95rem; margin-top: 0.3rem;">
                        {lesson['description']} · ⏱️ {dur}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Video player
                render_video_player(lesson)

                # Quiz
                if lesson.get("quiz"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    quiz_passed = render_quiz(lesson["quiz"], lid)

                    # Auto-complete on quiz pass
                    if quiz_passed and lid not in completed:
                        _complete_lesson(lid)
                        st.rerun()

                # Manual mark-complete (if no quiz or quiz not done yet)
                if lid not in completed:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ I finished this lesson!", key=f"mark_done_{lid}",
                                 use_container_width=True):
                        _complete_lesson(lid)
                        st.balloons()
                        st.rerun()

                # Back button
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("← Back to lesson list", key="back_to_lessons"):
                    st.session_state.pop("active_lesson", None)
                    st.rerun()

# ── Bottom CTA ────────────────────────────────────────────────────────────
if not is_premium:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['gold']}15, {COLORS['navy_card']});
                border: 1px solid {COLORS['gold']}40; border-radius: 16px; padding: 1.5rem;
                text-align: center; margin-top: 2rem;">
        <h3 style="color: {COLORS['gold']}; margin: 0 0 0.5rem;">🌟 Want more?</h3>
        <p style="color: {COLORS['text_secondary']}; margin: 0 0 1rem;">
            Upgrade to Premium for unlimited access to all {total_lessons} video lessons,
            quizzes, and achievement badges!
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/6_Upgrade.py", label="⭐ Upgrade to Premium",
                 use_container_width=True)
else:
    st.markdown(f"""
    <div style="text-align: center; color: {COLORS['text_secondary']}; padding: 1rem; margin-top: 2rem;">
        Want to chat with a coach? Head to the
        <a href="/Chat" style="color: {COLORS['blue']};">💬 Chat</a> page!
    </div>
    """, unsafe_allow_html=True)

# ── Admin: Video Pipeline Status Dashboard ───────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("🔧 Video Pipeline Status (Admin)", expanded=False):
    admin_pass = st.text_input("Enter admin password:", type="password", key="admin_pw")
    if admin_pass == os.environ.get("ADMIN_PASSWORD", "richy_admin"):
        from utils.video_loader import get_pipeline_summary, get_all_available_videos

        summary = get_pipeline_summary()
        available = get_all_available_videos()

        # Status overview
        st.markdown(f"""
        <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['border']};
                    border-radius: 14px; padding: 1.25rem; margin: 1rem 0;">
            <h4 style="color: {COLORS['gold']}; margin: 0 0 0.75rem;">📊 Pipeline Overview</h4>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 1.6rem; font-weight: 700; color: {COLORS['green']};">
                        {summary['local_count']}</div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">✅ Local Files</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.6rem; font-weight: 700; color: {COLORS['blue']};">
                        {summary['youtube_count']}</div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">🔗 YouTube</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.6rem; font-weight: 700; color: {COLORS['blue_light']};">
                        {summary['external_count']}</div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">🌐 External URL</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.6rem; font-weight: 700; color: {COLORS['gold']};">
                        {summary['placeholder_count']}</div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">⏳ Coming Soon</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Per-lesson table
        st.markdown(f"**Lesson Status** ({summary['total_lessons']} total)")
        for ls in summary["lessons"]:
            size_str = ""
            if ls["file_size"]:
                mb = ls["file_size"] / (1024 * 1024)
                size_str = f" — {mb:.1f} MB"
            mod_str = ""
            if ls["last_modified"]:
                mod_str = f" — modified {ls['last_modified']}"
            st.markdown(
                f"{ls['icon']} **{ls['title']}** ({ls['module']})  \n"
                f"&nbsp;&nbsp;&nbsp;&nbsp;`{ls['filename']}`{size_str}{mod_str}  \n"
                f"&nbsp;&nbsp;&nbsp;&nbsp;_{ls['detail']}_"
            )

        # Show loose files in videos/shows/ not mapped to any lesson
        if available:
            st.markdown("---")
            st.markdown("**📁 Files found in `videos/shows/`:**")
            for fname, fpath in sorted(available.items()):
                try:
                    mb = os.path.getsize(fpath) / (1024 * 1024)
                    st.markdown(f"- `{fname}` — {mb:.1f} MB")
                except OSError:
                    st.markdown(f"- `{fname}`")
        else:
            st.info("No .mp4 files found in `videos/shows/` yet. "
                    "Drop videos there and push to deploy automatically!")
    elif admin_pass:
        st.error("Incorrect password.")
