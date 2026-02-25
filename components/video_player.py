"""Video player component — professional video lesson cards."""

import streamlit as st
from config import COLORS


def render_video_lesson(lesson_or_title, video_url: str = "",
                        description: str = "", duration: str = "",
                        objectives: list[str] = None,
                        lesson_id: str = "") -> None:
    """Render a complete video lesson with player and learning objectives.

    Args:
        lesson_or_title: Either a lesson dict (with keys: title, video_url,
                         description, duration, objectives) or a title string.
        video_url: YouTube embed URL or video file URL (if lesson_or_title is a string).
        description: Short lesson description (if lesson_or_title is a string).
        duration: Duration string e.g. "4:32" (if lesson_or_title is a string).
        objectives: List of learning objectives.
        lesson_id: Unique lesson identifier.
    """
    # Support being called with a lesson dict or individual args
    if isinstance(lesson_or_title, dict):
        lesson = lesson_or_title
        title = lesson.get("title", "")
        video_url = lesson.get("video_url", "")
        description = lesson.get("description", "")
        duration = lesson.get("duration", "")
        objectives = lesson.get("objectives", objectives)
        lesson_id = lesson.get("id", lesson_id)
    else:
        title = lesson_or_title

    st.markdown(f"### {title}")
    st.caption(f"⏱️ {duration} • {description}")

    # Responsive iframe embed
    if "youtube.com" in video_url or "youtu.be" in video_url:
        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;
                    border-radius: 12px; margin: 1rem 0;">
            <iframe src="{video_url}" style="position: absolute; top: 0; left: 0;
                    width: 100%; height: 100%; border: none; border-radius: 12px;"
                    allowfullscreen></iframe>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.video(video_url)

    if objectives:
        st.markdown("**What you'll learn:**")
        for obj in objectives:
            st.markdown(f"- ✅ {obj}")


def render_video_card(title: str, duration: str, description: str,
                      completed: bool = False, locked: bool = False,
                      premium: bool = False) -> bool:
    """Render a video lesson card (for lesson lists). Returns True if Watch clicked.

    Args:
        title: Lesson title.
        duration: Duration string.
        description: Short description.
        completed: Whether the lesson is completed.
        locked: Whether the lesson is locked (premium).
        premium: Whether to show premium badge.

    Returns:
        True if the watch button was clicked.
    """
    status_icon = "✅" if completed else "🔒" if locked else "▶️"
    premium_badge = (
        f'<span class="premium-badge">⭐ Premium</span>' if premium and locked else ""
    )

    st.markdown(f"""
    <div class="video-lesson-card" style="{'opacity: 0.5;' if locked else ''}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">{status_icon}</span>
                <div>
                    <div style="font-weight: 600; color: {COLORS['text_primary']};">
                        {title} {premium_badge}
                    </div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']};">
                        {description}
                    </div>
                </div>
            </div>
            <span class="duration-badge">{duration}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not locked:
        return st.button(
            "✅ Completed" if completed else "▶️ Watch Now",
            key=f"watch_{title.replace(' ', '_')}",
            disabled=completed,
            use_container_width=True,
        )
    return False


def render_video_quiz(questions_or_quiz, lesson_id: str = "") -> int | None:
    """Render a post-video quiz. Returns score if submitted, else None.

    Args:
        questions_or_quiz: List of quiz question dicts with keys: q, choices, answer.
        lesson_id: Unique lesson ID for form keys.

    Returns:
        Number of correct answers if submitted, else None.
    """
    questions = questions_or_quiz if isinstance(questions_or_quiz, list) else []
    if not questions:
        return None
    with st.form(f"quiz_{lesson_id}"):
        st.markdown("### 🧪 Quick Quiz")
        st.caption("Test what you learned!")

        answers = []
        for i, q in enumerate(questions):
            choice = st.radio(
                q["q"],
                q["choices"],
                index=None,
                key=f"quiz_{lesson_id}_q{i}",
            )
            answers.append(choice)

        submitted = st.form_submit_button("Check Answers ✅", use_container_width=True)

    if submitted:
        correct = 0
        for i, q in enumerate(questions):
            user_ans = answers[i]
            correct_ans = q["choices"][q["answer"]]
            if user_ans == correct_ans:
                correct += 1
                st.success(f"Q{i + 1}: ✅ Correct!")
            elif user_ans is None:
                st.warning(f"Q{i + 1}: ⚠️ No answer selected.")
            else:
                st.error(f"Q{i + 1}: ❌ {user_ans} → Correct: **{correct_ans}**")

        total = len(questions)
        pct = correct / total if total > 0 else 0
        if pct == 1.0:
            st.balloons()
            st.success(f"🏆 Perfect: {correct}/{total}!")
        elif pct >= 0.6:
            st.info(f"Score: {correct}/{total} — Good job!")
        else:
            st.warning(f"Score: {correct}/{total} — Review and try again!")

        return correct
    return None
