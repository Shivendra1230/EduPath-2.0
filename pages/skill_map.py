from ui import hero, metric
import streamlit as st, pandas as pd
s=st.session_state.state
hero("04 · SKILL INTELLIGENCE","Know exactly what to learn next.","Priority combines role importance, skill distance, prerequisite blockers and evidence confidence. It is not a generic list of courses.")
if not s.get("gaps"): st.info("Analyze a learner profile first."); st.stop()
st.markdown("### Critical path")
st.markdown(" → ".join(s.get("critical_path",[])) or "No critical blockers.")
df=pd.DataFrame([{"Skill":g["skill"],"Current":g["current"],"Target":g["target"],"Gap":g["gap"],"Weight":g["weight"],"Priority":g["priority_score"],"Confidence":g["confidence"]} for g in s["gaps"]])
st.dataframe(df,use_container_width=True,hide_index=True)
