from ui import hero, metric
import streamlit as st
from core.adaptive import replan
from services.store import save_state
s=st.session_state.state
hero("07 · ADAPTIVE LOOP","Tell EduPath what happened. It replans.","This is the core loop: evidence → recommendation → practice → feedback → new recommendation. Difficulty and struggle become new learner evidence.")
feedback=st.text_area("What happened while learning?",height=170,placeholder="Example: I finished the FastAPI task quickly, but Docker networking was confusing. I can run containers but cannot explain bridge networking.")
if st.button("Replan from this evidence →",type="primary",use_container_width=True):
    if not feedback.strip(): st.warning("Tell the coach what happened first.")
    else:
        s["feedback"]=feedback
        with st.status("Adaptive Planner is recalculating your path…"):
            s=replan(s)
            st.session_state.state=s
            save_state(st.session_state.learner_id,s)
        st.success("Path updated. The next recommendation now reflects your feedback.")
        st.rerun()
if s.get("feedback"):
    st.markdown("### Latest learner evidence")
    st.markdown(f'<div class="success-box">{s["feedback"]}</div>',unsafe_allow_html=True)
    st.markdown("### New critical path")
    st.write(" → ".join(s.get("critical_path",[])))
