
import streamlit as st

from services.parser import extract_text, clean_text
from services.store import save_state
from core.graphs import build_analysis_graph


s = st.session_state.state

st.markdown(
    """
    <div class="hero">
        <div class="kicker">02 · LEARNER PROFILE</div>
        <h1>Build a learning path around you.</h1>
        <p>
            Your resume is evidence, not your identity. Add your target role,
            career goal and realistic weekly capacity so EduPath can make a
            useful decision about what comes next.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 1. Evidence upload
# ---------------------------------------------------------
left, right = st.columns([1.1, 1])

with left:
    st.markdown("### 1. Upload evidence")

    up = st.file_uploader(
        "Resume / portfolio / certificate / project notes "
        "(PDF, DOCX, PPTX, TXT, MD)",
        type=["pdf", "docx", "pptx", "txt", "md"],
        key="resume_upload",
    )

    if up is not None:
        try:
            extracted = clean_text(extract_text(up))

            if not extracted.strip():
                st.warning(
                    "No readable text was extracted. Try another document "
                    "or enter your skills manually."
                )
            else:
                # Only replace saved evidence after successful extraction.
                s["document_text"] = extracted
                s["document_name"] = up.name
                st.session_state.state = s

                st.success(
                    f"Parsed {up.name} · {len(extracted)} characters"
                )

        except Exception as exc:
            st.error(f"Parser error: {exc}")

    elif s.get("document_text"):
        st.success(
            f"Using saved evidence: "
            f"{s.get('document_name', 'Previously saved learner evidence')} "
            f"· {len(s['document_text'])} characters"
        )

        st.caption(
            "Your previously saved document text is available. "
            "Upload another file only if you want to replace it."
        )

    else:
        st.info(
            "No saved document found. Upload evidence or enter your current "
            "skills below."
        )

    st.caption(
        "Best result: upload the resume you would actually submit "
        "for the target role."
    )


# ---------------------------------------------------------
# 2. Target role and learner details
# ---------------------------------------------------------
roles = [
    "Generative AI Engineer",
    "AI/ML Engineer",
    "Data Analyst",
]

saved_role = s.get("target_role", "Generative AI Engineer")
role_index = roles.index(saved_role) if saved_role in roles else 0

with right:
    st.markdown("### 2. Define the destination")

    role = st.selectbox(
        "Target role",
        roles,
        index=role_index,
    )

    goal = st.text_area(
        "Career goal",
        value=s.get(
            "career_goal",
            "Become job-ready for the target role with portfolio evidence."
        ),
        height=90,
    )

    saved_hours = s.get("weekly_hours", 7)

    try:
        saved_hours = float(saved_hours)
    except (ValueError, TypeError):
        saved_hours = 7.0

    saved_hours = min(40.0, max(1.0, saved_hours))

    hours = st.number_input(
        "Realistic hours / week",
        min_value=1.0,
        max_value=40.0,
        value=saved_hours,
        step=0.5,
    )

    current = st.text_area(
        "Current skills / experience (optional)",
        value=s.get("current_skills", ""),
        height=90,
    )


jd = st.text_area(
    "Optional real job description",
    value=s.get("job_description", ""),
    height=150,
    placeholder="Paste a job description to make the gap map specific to a real role.",
)


# ---------------------------------------------------------
# 3. Analyze and persist
# ---------------------------------------------------------
if st.button(
    "Analyze learner →",
    type="primary",
    use_container_width=True,
):
    # Work on a copy so existing state is not cleared prematurely.
    analysis_input = dict(s)

    analysis_input.update({
        "target_role": role,
        "career_goal": goal,
        "weekly_hours": hours,
        "current_skills": current,
        "job_description": jd,
    })

    uploaded_text = str(analysis_input.get("document_text", "")).strip()
    current_text = current.strip()

    if not uploaded_text and not current_text:
        st.warning(
            "Upload evidence or enter your current skills first."
        )

    else:
        if not uploaded_text:
            analysis_input["document_text"] = current_text
            analysis_input["document_name"] = "Learner-entered skills"

        try:
            with st.status(
                "EduPath agents are analyzing your profile…",
                expanded=True,
            ) as status:
                graph = build_analysis_graph()
                result = graph.invoke(analysis_input)

                if not isinstance(result, dict):
                    raise ValueError(
                        "The analysis workflow returned an invalid state."
                    )

                # Preserve the result only after the graph succeeds.
                s.clear()
                s.update(result)

                # Persist the complete resulting state.
                save_state(st.session_state.learner_id, s)

                st.session_state.state = s

                status.update(
                    label="Analysis complete",
                    state="complete",
                    expanded=False,
                )

            st.switch_page("pages/command_center.py")

        except Exception as exc:
            st.error(
                f"Analysis failed: {exc}. "
                "Your previously saved database state has not been "
                "intentionally deleted. Check the error and try again."
            )
