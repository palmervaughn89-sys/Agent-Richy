"""Kids Education — Video-based financial literacy for young learners."""

import streamlit as st
from styles import inject_styles
from config import COLORS, KIDS_MODULES, FREE_VIDEO_MODULES, FREE_VIDEO_LESSONS
from utils.session import init_session_state, get_profile, complete_video, can_access_premium
from components.video_player import render_video_lesson, render_video_card, render_video_quiz
from components.progress_tracker import render_module_progress, render_achievement_badges

st.set_page_config(page_title="Kids Education — Agent Richy", page_icon="🎓", layout="wide")
inject_styles()
init_session_state()

if not st.session_state.get("onboarded"):
    st.warning("Please complete onboarding first.")
    st.page_link("app.py", label="← Go to Home", use_container_width=True)
    st.stop()

profile = get_profile()
is_premium = st.session_state.get("is_premium", False)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align: center; padding: 1rem 0 1.5rem;">
    <h1 style="margin: 0;">
        <span style="color: {COLORS['gold']};">🎓</span>
        Money Academy
    </h1>
    <p style="color: {COLORS['text_secondary']}; font-size: 1.1rem; margin: 0.5rem 0 0;">
        Learn smart money skills through fun video lessons!
    </p>
</div>
""", unsafe_allow_html=True)

# ── Progress overview ────────────────────────────────────────────────────
completed_videos = st.session_state.get("completed_videos", set())
total_videos = sum(len(m["lessons"]) for m in KIDS_MODULES)
total_completed = len(completed_videos)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border-radius: 12px; padding: 1rem;
                text-align: center; border: 1px solid {COLORS['border']};">
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['gold']};">
            {total_completed}/{total_videos}
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Lessons Completed</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    modules_done = sum(1 for m in KIDS_MODULES
                       if all(l["id"] in completed_videos for l in m["lessons"]))
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border-radius: 12px; padding: 1rem;
                text-align: center; border: 1px solid {COLORS['border']};">
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['blue']};">
            {modules_done}/{len(KIDS_MODULES)}
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Modules Complete</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    badges = st.session_state.get("badges", [])
    st.markdown(f"""
    <div style="background: {COLORS['navy_card']}; border-radius: 12px; padding: 1rem;
                text-align: center; border: 1px solid {COLORS['border']};">
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['green']};">
            {len(badges)}
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Badges Earned</div>
    </div>
    """, unsafe_allow_html=True)

# Badges row
if badges:
    render_achievement_badges(badges)

st.markdown("<br>", unsafe_allow_html=True)

# ── Module tabs ──────────────────────────────────────────────────────────
module_names = [f"{m['icon']} {m['title']}" for m in KIDS_MODULES]
tabs = st.tabs(module_names)

for mod_idx, (tab, module) in enumerate(zip(tabs, KIDS_MODULES)):
    with tab:
        # Check free-tier access
        module_locked = (not is_premium and mod_idx >= FREE_VIDEO_MODULES)

        if module_locked:
            st.markdown(f"""
            <div style="background: {COLORS['navy_card']}; border: 1px solid {COLORS['gold']}40;
                        border-radius: 16px; padding: 2rem; text-align: center; position: relative;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
                <h3 style="color: {COLORS['gold']}; margin: 0 0 0.5rem;">Premium Module</h3>
                <p style="color: {COLORS['text_secondary']}; margin: 0 0 1rem;">
                    Upgrade to unlock <strong>{module['title']}</strong> and all {len(module['lessons'])} lessons!
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/6_Upgrade.py", label="⭐ Unlock All Modules",
                         use_container_width=True)
            continue

        # Module description
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {module.get('color', COLORS['blue'])}20,
                     {COLORS['navy_card']}); border-radius: 16px; padding: 1.2rem;
                     border: 1px solid {module.get('color', COLORS['blue'])}40; margin-bottom: 1rem;">
            <h3 style="margin: 0 0 0.5rem; color: {module.get('color', COLORS['blue'])};">
                {module['icon']} {module['title']}
            </h3>
            <p style="color: {COLORS['text_secondary']}; margin: 0; font-size: 0.95rem;">
                {module.get('description', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Module progress bar
        module_lessons = module["lessons"]
        module_completed = sum(1 for l in module_lessons if l["id"] in completed_videos)
        render_module_progress(module_completed, len(module_lessons), module.get('color', COLORS['blue']))

        # Lesson cards
        for lesson_idx, lesson in enumerate(module_lessons):
            lesson_locked = (not is_premium and mod_idx == 0 and lesson_idx >= FREE_VIDEO_LESSONS
                             and mod_idx < FREE_VIDEO_MODULES)
            # Actually: free users get FREE_VIDEO_MODULES modules and FREE_VIDEO_LESSONS lessons per free module
            lesson_locked = (not is_premium and lesson_idx >= FREE_VIDEO_LESSONS and mod_idx < FREE_VIDEO_MODULES)

            is_completed = lesson["id"] in completed_videos

            with st.expander(
                f"{'✅' if is_completed else '🔒' if lesson_locked else '📺'} "
                f"Lesson {lesson_idx + 1}: {lesson['title']}",
                expanded=False
            ):
                if lesson_locked:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">
                        🔒 Premium lesson — upgrade to access!
                    </div>
                    """, unsafe_allow_html=True)
                    st.page_link("pages/6_Upgrade.py", label="⭐ Upgrade",
                                 use_container_width=True)
                    continue

                # Lesson info
                col_info, col_action = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    <p style="color: {COLORS['text_secondary']}; margin: 0 0 0.5rem;">
                        {lesson.get('description', '')}
                    </p>
                    <p style="font-size: 0.8rem; color: {COLORS['text_secondary']};">
                        ⏱️ {lesson.get('duration', '5 min')}
                        {' • ✅ Completed' if is_completed else ''}
                    </p>
                    """, unsafe_allow_html=True)
                with col_action:
                    if is_completed:
                        st.success("✅ Done!")

                # Objectives
                if lesson.get("objectives"):
                    st.markdown(f"**What you'll learn:**")
                    for obj in lesson["objectives"]:
                        st.markdown(f"- {obj}")

                # Video player
                st.markdown("---")
                render_video_lesson(lesson)

                # Mark completed button
                if not is_completed:
                    if st.button(
                        f"✅ I finished this lesson!",
                        key=f"complete_{lesson['id']}",
                        use_container_width=True
                    ):
                        complete_video(lesson["id"])
                        st.balloons()
                        st.rerun()

                # Quiz
                if lesson.get("quiz"):
                    st.markdown("---")
                    st.markdown(f"**🧠 Quick Quiz**")
                    render_video_quiz(lesson["quiz"], lesson["id"])

st.markdown("<br>", unsafe_allow_html=True)

# ── Bottom CTA ────────────────────────────────────────────────────────────
if not is_premium:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['gold']}20, {COLORS['navy_card']});
                border: 1px solid {COLORS['gold']}40; border-radius: 16px; padding: 1.5rem;
                text-align: center; margin-top: 1rem;">
        <h3 style="color: {COLORS['gold']}; margin: 0 0 0.5rem;">🌟 Unlock All Modules</h3>
        <p style="color: {COLORS['text_secondary']}; margin: 0 0 1rem;">
            Get access to all {len(KIDS_MODULES)} modules with {total_videos} video lessons,
            quizzes, and achievement badges!
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/6_Upgrade.py", label="⭐ Upgrade to Premium",
                 use_container_width=True)
else:
    st.markdown(f"""
    <div style="text-align: center; color: {COLORS['text_secondary']}; padding: 1rem;">
        Want to chat with a coach? Head to the
        <a href="/Chat" style="color: {COLORS['blue']};">💬 Chat</a> page!
    </div>
    """, unsafe_allow_html=True)
