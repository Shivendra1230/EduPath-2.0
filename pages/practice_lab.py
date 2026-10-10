
import json
import streamlit as st

from core.llm import groq_service
from services.store import save_state
from ui import hero, metric


# ---------------------------------------------------------
# 1. Learner state and safe defaults
# ---------------------------------------------------------

s = st.session_state.state
s.setdefault("practice", [])
s.setdefault("practice_workspace", {})

hero(
    "06 · PRACTICE LAB",
    "Build something real. Prove what you know.",
    "Complete practical engineering missions with clear requirements, "
    "measurable acceptance criteria, saved progress, and contextual AI coaching."
)

if not s["practice"]:
    st.info("Analyze a learner profile first to generate practice missions.")
    st.stop()


def persist_state():
    """Persist learner state through the existing SQLite store."""
    st.session_state.state = s
    save_state(st.session_state.learner_id, s)


def normalize_list(value, fallback):
    """Ensure LLM-generated list fields have a safe structure."""
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        if items:
            return items
    return fallback


def fallback_mission(p):
    """Usable mission when the LLM is unavailable or returns invalid data."""
    skill = str(p.get("skill", "Target skill"))
    difficulty = str(p.get("difficulty", "Beginner"))
    minutes = p.get("minutes", 60)

    return {
        "title": str(p.get("title", f"{skill} practical mission")),
        "scenario": (
            f"You are working on a {difficulty.lower()}-level engineering task "
            f"that demonstrates practical knowledge of {skill}. "
            "Your goal is to create a small, testable artifact and explain "
            "the decisions behind it."
        ),
        "problem": (
            f"Implement a focused solution demonstrating {skill}. "
            "Define expected behavior, test a representative example, "
            "and document one limitation or trade-off."
        ),
        "environment": [
            "Use a reproducible development environment.",
            "Document any dependencies and setup steps.",
            "Do not report results for experiments you have not run.",
        ],
        "requirements": [
            f"Build a working artifact that demonstrates {skill}.",
            "Include a representative input and expected output.",
            "Test at least one edge case or failure scenario.",
            "Explain one implementation decision and its trade-off.",
        ],
        "steps": [
            "Write down the problem, assumptions, and expected behavior.",
            "Create the smallest working implementation.",
            "Run a representative test and record the actual result.",
            "Modify one requirement and verify the behavior again.",
            "Document findings, limitations, and possible improvements.",
        ],
        "deliverables": [
            str(p.get("deliverable", f"Working {skill} artifact")),
            "A README or short implementation report.",
            "Test results and one lesson learned.",
        ],
        "acceptance_criteria": [
            "The artifact is reproducible or can be reviewed.",
            "The main requirement is demonstrated with an example.",
            "At least one validation result is documented.",
            "The learner can explain the implementation independently.",
        ],
        "estimated_minutes": minutes if isinstance(minutes, int) else 60,
    }


def generate_mission(p):
    """Generate and validate a detailed mission using the existing Groq service."""
    fallback = fallback_mission(p)

    if not groq_service.live:
        return fallback

    system = """
You are EduPath's practical engineering mission designer.

Return one valid JSON object with these keys:
title, scenario, problem, environment, requirements, steps,
deliverables, acceptance_criteria, estimated_minutes.

Requirements:
- Design a realistic, specific task for the given skill and difficulty.
- Make the scenario and problem specific, not generic motivational text.
- Include 3-6 actionable requirements.
- Include 4-7 steps in execution order.
- Name concrete deliverables such as files, experiments, reports, tests,
  or small portfolio artifacts.
- Acceptance criteria must be independently checkable.
- Respect the learner's time budget and experience level.
- Never invent benchmark results or claim that code was executed.
- Do not include secrets, credentials, or unsafe instructions.
- Return JSON only, without Markdown fences.
"""

    user = {
        "target_role": s.get("target_role", "Not specified"),
        "skill": p.get("skill", "Not specified"),
        "difficulty": p.get("difficulty", "Beginner"),
        "time_budget_minutes": p.get("minutes", 60),
        "original_task": p.get("title", ""),
        "expected_deliverable": p.get("deliverable", ""),
        "validation_hints": p.get("checks", []),
        "learner_profile": s.get("profile", {}),
        "document_evidence": str(s.get("document_text", ""))[:5000],
    }

    try:
        result = groq_service.json(
            system,
            json.dumps(user, ensure_ascii=False, default=str),
            groq_service.fast_model,
            2200,
        )

        if not isinstance(result, dict):
            return fallback

        mission = {
            "title": str(result.get("title") or fallback["title"]),
            "scenario": str(result.get("scenario") or fallback["scenario"]),
            "problem": str(result.get("problem") or fallback["problem"]),
            "environment": normalize_list(
                result.get("environment"), fallback["environment"]
            ),
            "requirements": normalize_list(
                result.get("requirements"), fallback["requirements"]
            ),
            "steps": normalize_list(
                result.get("steps"), fallback["steps"]
            ),
            "deliverables": normalize_list(
                result.get("deliverables"), fallback["deliverables"]
            ),
            "acceptance_criteria": normalize_list(
                result.get("acceptance_criteria"),
                fallback["acceptance_criteria"],
            ),
            "estimated_minutes": fallback["estimated_minutes"],
        }

        # Preserve the existing mission's identity and skill.
        return mission

    except Exception:
        # Do not let an LLM/API failure break the Practice Lab.
        return fallback


def get_workspace(mission_id):
    """Get or initialize persistent workspace data for one mission."""
    workspace = s["practice_workspace"]

    if mission_id not in workspace:
        workspace[mission_id] = {
            "mission": None,
            "checks": {},
            "artifact": "",
            "reflection": "",
            "coach_history": [],
            "submission_saved": False,
        }

    item = workspace[mission_id]
    item.setdefault("mission", None)
    item.setdefault("checks", {})
    item.setdefault("artifact", "")
    item.setdefault("reflection", "")
    item.setdefault("coach_history", [])
    item.setdefault("submission_saved", False)

    return item


def coach_response(mission, question, artifact):
    """Ask the existing Groq service for mission-specific guidance."""
    system = """
You are EduPath's practical engineering coach.

Help the learner complete the active mission using its actual requirements.
Give useful debugging steps, hints, explanations, and validation suggestions.
Ask clarifying questions when necessary. Prefer incremental guidance.
Review learner-provided code or reports when included.

Never claim to have executed code or verified results you have not seen.
Do not fabricate metrics or experiment outcomes.
Keep the response specific to the current mission.
"""

    context = {
        "mission": mission,
        "learner_artifact": artifact[:10000],
        "question": question,
    }

    return groq_service.chat(
        system,
        json.dumps(context, ensure_ascii=False, default=str),
        groq_service.fast_model,
        temperature=0.3,
        max_tokens=1400,
    )


# ---------------------------------------------------------
# 2. Mission list
# ---------------------------------------------------------

st.markdown("## Available missions")

for index, p in enumerate(s["practice"], 1):
    mission_id = str(p.get("id") or f"practice_{index}")
    workspace = get_workspace(mission_id)

    with st.container(border=True):
        st.markdown(
            f"### {index}. {p.get('title', p.get('skill', 'Practice mission'))}"
        )
        st.caption(
            f"{p.get('skill', 'Skill')} · "
            f"{p.get('difficulty', 'Beginner')} · "
            f"{p.get('minutes', 60)} min"
        )
        st.write(p.get("deliverable", "Build a practical artifact."))

        saved_mission = workspace.get("mission")
        status = (
            "Mission generated"
            if saved_mission
            else "Ready to generate"
        )
        st.caption(f"Workspace status: {status}")

        if st.button(
            "Open mission workspace →",
            key=f"open_mission_{mission_id}",
            type="primary",
        ):
            if not workspace.get("mission"):
                with st.spinner("Preparing your mission..."):
                    workspace["mission"] = generate_mission(p)

            st.session_state["active_mission_id"] = mission_id
            persist_state()
            st.rerun()


# ---------------------------------------------------------
# 3. Active mission workspace
# ---------------------------------------------------------

active_id = st.session_state.get("active_mission_id")

if active_id:
    workspace = s["practice_workspace"].get(active_id)

    if not workspace:
        st.warning("This mission workspace could not be found. Open it again.")
        st.stop()

    mission = workspace.get("mission")

    if not mission:
        st.warning("Mission details are missing. Reopen the mission to generate them.")
        st.stop()

    st.divider()
    st.markdown("## 🧪 Mission workspace")
    st.markdown(f"### {mission['title']}")

    
    active_skill = next(
        (
            p.get("skill", "")
            for p in s["practice"]
            if str(p.get("id")) == active_id
        ),
        "Practice",
    )

    st.caption(
        f"{active_skill} | "
        f"{mission.get('estimated_minutes', 60)} minutes"
    )


    st.info(mission["scenario"])

    st.markdown("### Problem statement")
    st.write(mission["problem"])

    with st.expander("Environment and constraints", expanded=True):
        for item in mission["environment"]:
            st.markdown(f"- {item}")

    st.markdown("### Requirements")
    for item in mission["requirements"]:
        st.markdown(f"- {item}")

    st.markdown("### Execution plan")
    for number, item in enumerate(mission["steps"], 1):
        st.markdown(f"**Step {number}.** {item}")

    st.markdown("### Deliverables")
    for item in mission["deliverables"]:
        st.markdown(f"- {item}")

    st.markdown("### Acceptance criteria")
    st.caption("Mark a criterion only after you have verified it.")

    for number, criterion in enumerate(mission["acceptance_criteria"]):
        check_key = f"lab_check_{active_id}_{number}"

        if check_key not in st.session_state:
            st.session_state[check_key] = bool(
                workspace["checks"].get(str(number), False)
            )

        st.checkbox(criterion, key=check_key)

        current_value = bool(st.session_state[check_key])
        if workspace["checks"].get(str(number)) != current_value:
            workspace["checks"][str(number)] = current_value
            persist_state()

    checked_count = sum(
        bool(workspace["checks"].get(str(i), False))
        for i in range(len(mission["acceptance_criteria"]))
    )
    total_checks = len(mission["acceptance_criteria"])
    percent = round(checked_count / total_checks * 100) if total_checks else 0

    c1, c2 = st.columns(2)
    with c1:
        metric("Criteria verified", f"{checked_count}/{total_checks}", "self-reported")
    with c2:
        metric("Checklist progress", f"{percent}%", "not an automatic grade")

    st.progress(percent / 100)

    # -----------------------------------------------------
    # Submission editor
    # -----------------------------------------------------

    st.markdown("### Submit your work")

    artifact_key = f"lab_artifact_{active_id}"
    if artifact_key not in st.session_state:
        st.session_state[artifact_key] = workspace.get("artifact", "")

    st.text_area(
        "Implementation, code, report, or experiment results",
        key=artifact_key,
        height=200,
        placeholder=(
            "Paste your implementation or summarize what you built. "
            "Include actual test results where applicable."
        ),
    )

    if st.button("Save submission", key=f"save_artifact_{active_id}"):
        workspace["artifact"] = st.session_state[artifact_key]
        workspace["submission_saved"] = True
        persist_state()
        st.success("Submission saved to your learner state.")

    if workspace.get("submission_saved"):
        st.caption("A submission has been saved for this mission.")

    # -----------------------------------------------------
    # Context-aware AI coach
    # -----------------------------------------------------

    st.markdown("### 🤖 AI Mission Coach")
    st.caption(
        "Ask for a hint, debugging help, an explanation, or feedback on your artifact."
    )

    question_key = f"lab_question_{active_id}"
    question = st.text_input(
        "What are you stuck on?",
        key=question_key,
        placeholder="e.g. How do I calculate exact-match accuracy?",
    )

    if st.button("Ask Coach", key=f"ask_coach_{active_id}"):
        if not question.strip():
            st.warning("Enter a question first.")
        elif not groq_service.live:
            st.warning(
                "Groq is not connected. Configure GROQ_API_KEY in your environment "
                "or Streamlit Cloud Secrets."
            )
        else:
            with st.spinner("Coach is thinking..."):
                try:
                    answer = coach_response(
                        mission,
                        question.strip(),
                        workspace.get("artifact", ""),
                    )

                    workspace["coach_history"].append({
                        "question": question.strip(),
                        "answer": str(answer),
                    })
                    persist_state()
                    st.rerun()

                except Exception:
                    st.error(
                        "The Coach request failed. Check your Groq configuration "
                        "and try again."
                    )

    for exchange in workspace["coach_history"]:
        with st.chat_message("user"):
            st.write(exchange.get("question", ""))
        with st.chat_message("assistant"):
            st.write(exchange.get("answer", ""))

    # -----------------------------------------------------
    # Reflection
    # -----------------------------------------------------

    st.markdown("### Reflection")

    reflection_key = f"lab_reflection_{active_id}"
    if reflection_key not in st.session_state:
        st.session_state[reflection_key] = workspace.get("reflection", "")

    st.text_area(
        "What was easy, difficult, or surprising? What would you improve?",
        key=reflection_key,
        height=120,
    )

    if st.button("Save reflection", key=f"save_reflection_{active_id}"):
        workspace["reflection"] = st.session_state[reflection_key]
        persist_state()
        st.success("Reflection saved.")

    if st.button("Close workspace", key=f"close_mission_{active_id}"):
        st.session_state.pop("active_mission_id", None)
        st.rerun()
