
import streamlit as st

from ui import hero
from core.llm import groq_service
from core.coach_graph import COACH_SYSTEM, _classify_scope
from services.store import save_state


s = st.session_state.state
learner_id = st.session_state.learner_id

hero(
    "09 · CAREER COPILOT",
    "A coach, not a menu.",
    "Ask about your skills, projects, learning roadmap, resume, "
    "interviews, or career goals."
)

QUICK_PROMPTS = [
    "I have 2 hours today. What should I study?",
    "Why is my highest-priority skill gap important?",
    "Teach me the basics of Generative AI.",
    "How can I become a Gen AI Engineer?",
    "Give me 5 interview questions with answers.",
]


def build_context() -> dict:
    return {
        "target_role": s.get("target_role"),
        "career_goal": s.get("career_goal"),
        "current_skills": s.get("current_skills"),
        "experience": s.get("experience"),
        "profile": s.get("profile", {}),
        "readiness": s.get("readiness"),
        "critical_path": s.get("critical_path", []),
        "gaps": (s.get("gaps") or [])[:8],
        "objectives": (s.get("objectives") or [])[:8],
        "resources": (s.get("resources") or [])[:8],
        "progress": s.get("progress", {}),
        "evidence": str(s.get("document_text") or "")[:8000],
    }


def generate_answer(question: str) -> str:
    """Stream the answer, then persist the completed response."""
    history = s.setdefault("coach_history", [])

    history.append({"role": "user", "content": question})
    s["coach_question"] = question

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if _classify_scope(question) == "out_of_scope":
            answer = (
                "I'm EduPath Career Copilot. I focus on learning, "
                "skills, projects, interviews, and career planning. "
                "Ask me something related to those areas and I'll help."
            )
            st.markdown(answer)

        elif not groq_service.live:
            answer = (
                "Groq is not connected. Add GROQ_API_KEY to your .env "
                "file and restart EduPath to enable AI responses."
            )
            st.warning(answer)

        else:
            prompt = f"""
LEARNER PROFILE:
{build_context()}

RECENT CHAT HISTORY:
{history[-9:-1]}

CURRENT QUESTION:
{question}

Answer the current question directly.
Use the learner profile only when relevant.
Do not invent learner skills, experience, achievements, or progress.
For a roadmap, give ordered steps, projects, and practical milestones.
For technical questions, explain the concept and give examples.
If details are missing, say so clearly.
If the question is ambiguous but has a likely career/learning meaning,
answer that interpretation instead of rejecting it.
"""

            try:
                answer = st.write_stream(
                    groq_service.stream_text(
                        system=COACH_SYSTEM,
                        user=prompt,
                        model=groq_service.reasoning_model,
                        temperature=0.15,
                        max_tokens=2200,
                    )
                )

                if not answer or not str(answer).strip():
                    answer = groq_service.chat(
                        system=COACH_SYSTEM,
                        user=prompt,
                        model=groq_service.fast_model,
                        temperature=0.1,
                        max_tokens=1800,
                    )
                    st.markdown(answer)

            except Exception as exc:
                answer = (
                    "I couldn't generate an answer. Check your API key, "
                    "model configuration, and internet connection. "
                    f"Error: {type(exc).__name__}"
                )
                st.error(answer)

    history.append({"role": "assistant", "content": str(answer)})
    s["coach_answer"] = str(answer)

    st.session_state.state = s
    save_state(learner_id, s)


# Render previous conversation
for message in s.get("coach_history", []):
    with st.chat_message(
        "user" if message.get("role") == "user" else "assistant"
    ):
        st.markdown(message.get("content", ""))


# Quick prompts
st.markdown("#### Quick questions")

cols = st.columns(2)
for index, prompt in enumerate(QUICK_PROMPTS):
    if cols[index % 2].button(
        prompt,
        key=f"coach_quick_{index}",
        use_container_width=True,
    ):
        st.session_state.pending_coach_question = prompt


# Chat input
question = st.chat_input("Ask about your learning or career...")

if question:
    generate_answer(question)
    st.rerun()

if st.session_state.get("pending_coach_question"):
    pending = st.session_state.pop("pending_coach_question")
    generate_answer(pending)
    st.rerun()
