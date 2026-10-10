import streamlit as st
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

if "learner_id" not in st.session_state:
    st.session_state.learner_id = ensure_learner()

if "state" not in st.session_state:
    st.session_state.state = load_state(st.session_state.learner_id)

if "chat" not in st.session_state:
    st.session_state.chat = []

if "interview_nonce" not in st.session_state:
    st.session_state.interview_nonce = 0

header(groq_service.live)

# Streamlit navigation expects a list/dict of Page objects. A list is robust
# across supported Streamlit versions and avoids treating a Page as iterable.
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

selected_page = st.navigation(pages, position="top", expanded=False)
selected_page.run()
