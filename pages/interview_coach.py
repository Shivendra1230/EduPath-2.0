from ui import hero, metric
import streamlit as st
from core.llm import groq_service
from agents.analyze import interview_node
s=st.session_state.state
hero("08 · INTERVIEW COACH","Practice the questions your gaps create.","Questions are generated from the learner's target role, evidence and current gaps. Regenerate to get a different set.")
if st.button("↻ Generate fresh interview set",use_container_width=False):
    s=interview_node(s); st.session_state.state=s; st.rerun()
if not s.get("interview"): st.info("Analyze a learner profile first."); st.stop()
for i,q in enumerate(s["interview"],1):
    with st.expander(f"{i}. {q.get('question','Question')} · {q.get('difficulty','Intermediate')}"):
        st.caption(f"Skill: {q.get('skill','—')}")
        st.markdown("**Model answer**")
        st.write(q.get("answer",q.get("model_answer","")))
        st.markdown("**Follow-up**")
        st.write(q.get("follow_up",""))
