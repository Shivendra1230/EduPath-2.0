
import streamlit as st
import uuid
from dotenv import load_dotenv

from core.llm import groq_service
from services.store import ensure_learner, load_state
from ui import css, header, PAGES

load_dotenv()

st.set_page_config(
    page_title="EduPath | Adaptive Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

css()


# ---------------------------------------------------------
# Learner identity: preserve across browser refreshes
# ---------------------------------------------------------

def get_learner_id():
    """
    Restore learner identity from the URL.

    Important:
    This preserves identity across refreshes, but cannot restore
    data that has been deleted from the underlying database.
    """
    query_learner = st.query_params.get("learner")

    if query_learner:
        try:
            return str(uuid.UUID(str(query_learner)))
        except (ValueError, TypeError, AttributeError):
            # Invalid URL parameter: create a fresh learner.
            pass

    learner_id = ensure_learner()
    st.query_params["learner"] = learner_id
    return learner_id


learner_id = get_learner_id()
st.session_state.learner_id = learner_id


# ---------------------------------------------------------
# Load saved learner state once per Streamlit session
# ---------------------------------------------------------

if "state" not in st.session_state:
    st.session_state.state = load_state(learner_id)

if not isinstance(st.session_state.state, dict):
    st.session_state.state = {}


# ---------------------------------------------------------
# Initialize other application state
# ---------------------------------------------------------

if "chat" not in st.session_state:
    st.session_state.chat = []

if "interview_nonce" not in st.session_state:
    st.session_state.interview_nonce = 0


# ---------------------------------------------------------
# Application header
# ---------------------------------------------------------

header(groq_service.live)


# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------

pages = []

for item in PAGES:
    label = item.split(" ", 1)[1]
    slug = label.lower().replace(" ", "_")

    pages.append(
        st.Page(
            f"pages/{slug}.py",
            title=label,
            default=(label == "Command Center"),
        )
    )

selected_page = st.navigation(
    pages,
    position="top",
    expanded=False,
)

selected_page.run()
