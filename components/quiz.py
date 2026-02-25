"""Quiz component — fun, kid-friendly quizzes for video lessons."""

import streamlit as st
from config import COLORS


def render_quiz(questions: list[dict], lesson_id: str) -> bool:
    """Render an interactive quiz for a lesson. Returns True if quiz was completed.

    Questions use the video_data.py format:
        {"question": str, "options": list[str], "correct_index": int, "explanation": str}

    Args:
        questions: List of quiz question dicts.
        lesson_id: Unique lesson ID (used for session state keys).

    Returns:
        True if the quiz has been completed (passed), False otherwise.
    """
    if not questions:
        return False

    quiz_key = f"quiz_done_{lesson_id}"
    score_key = f"quiz_score_{lesson_id}"

    # Already completed — show summary
    if st.session_state.get(quiz_key):
        score = st.session_state.get(score_key, 0)
        total = len(questions)
        st.markdown(f"""
        <div style="background: {COLORS['green']}15; border: 1px solid {COLORS['green']}40;
                    border-radius: 14px; padding: 1.25rem; text-align: center; margin: 0.5rem 0;">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">🏆</div>
            <div style="font-weight: 700; color: {COLORS['green']}; font-size: 1.1rem;">
                Quiz Complete! You got {score} out of {total}!
            </div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.9rem; margin-top: 0.3rem;">
                {"Perfect score! You're a money genius! 🌟" if score == total else "Great effort! Keep learning! 💪"}
            </div>
        </div>
        """, unsafe_allow_html=True)
        return True

    # ── Quiz header ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background: {COLORS['gold']}15; border: 1px solid {COLORS['gold']}40;
                border-radius: 14px; padding: 1rem 1.25rem; margin: 0.5rem 0 1rem;">
        <div style="font-size: 1.3rem; font-weight: 700; color: {COLORS['gold']};">
            🧠 Quiz Time!
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.95rem;">
            Let's see what you learned! Answer all questions and hit Submit.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Question form ────────────────────────────────────────────────────
    with st.form(f"quiz_form_{lesson_id}"):
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f"""
            <div style="font-weight: 600; font-size: 1.05rem; color: {COLORS['text_primary']};
                        margin-top: {'1.5rem' if i > 0 else '0.5rem'}; margin-bottom: 0.4rem;">
                Question {i + 1}: {q['question']}
            </div>
            """, unsafe_allow_html=True)

            choice = st.radio(
                f"Q{i + 1}",
                q["options"],
                index=None,
                key=f"qz_{lesson_id}_q{i}",
                label_visibility="collapsed",
            )
            answers.append(choice)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "✅ Submit Answers",
            use_container_width=True,
        )

    # ── Grade ────────────────────────────────────────────────────────────
    if submitted:
        all_answered = all(a is not None for a in answers)
        if not all_answered:
            st.warning("⚠️ Please answer every question before submitting!")
            return False

        correct = 0
        total = len(questions)

        for i, q in enumerate(questions):
            user_ans = answers[i]
            correct_ans = q["options"][q["correct_index"]]
            explanation = q.get("explanation", "")

            if user_ans == correct_ans:
                correct += 1
                st.markdown(f"""
                <div style="background: {COLORS['green']}12; border-left: 4px solid {COLORS['green']};
                            border-radius: 0 10px 10px 0; padding: 0.75rem 1rem; margin: 0.5rem 0;">
                    <span style="font-weight: 700; color: {COLORS['green']};">
                        ✅ Q{i+1}: Correct!
                    </span>
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.9rem; margin-top: 0.3rem;">
                        {explanation}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: {COLORS['red']}12; border-left: 4px solid {COLORS['red']};
                            border-radius: 0 10px 10px 0; padding: 0.75rem 1rem; margin: 0.5rem 0;">
                    <span style="font-weight: 700; color: {COLORS['red']};">
                        ❌ Q{i+1}: Not quite! The answer is: {correct_ans}
                    </span>
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.9rem; margin-top: 0.3rem;">
                        {explanation}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Final score
        if correct == total:
            st.balloons()
            st.markdown(f"""
            <div style="background: {COLORS['gold']}18; border: 2px solid {COLORS['gold']};
                        border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏆</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: {COLORS['gold']};">
                    Perfect score! You're a money genius!
                </div>
                <div style="color: {COLORS['text_secondary']}; font-size: 1rem; margin-top: 0.25rem;">
                    You got {correct} out of {total}! 🌟
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: {COLORS['blue']}15; border: 1px solid {COLORS['blue']}40;
                        border-radius: 14px; padding: 1.25rem; text-align: center; margin: 1rem 0;">
                <div style="font-size: 1.8rem; margin-bottom: 0.4rem;">🌟</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: {COLORS['blue']};">
                    You got {correct} out of {total}!
                </div>
                <div style="color: {COLORS['text_secondary']}; font-size: 0.95rem; margin-top: 0.25rem;">
                    {"Great job! Almost perfect!" if correct >= total - 1 else "Keep learning — you'll get there! 💪"}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Save score in session
        st.session_state[quiz_key] = True
        st.session_state[score_key] = correct
        # Also persist in the central quiz_scores dict
        scores = st.session_state.get("quiz_scores", {})
        scores[lesson_id] = correct
        st.session_state["quiz_scores"] = scores

        return True

    return False
