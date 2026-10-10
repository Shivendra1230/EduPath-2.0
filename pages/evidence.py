from ui import hero, metric
import streamlit as st, pandas as pd
s=st.session_state.state
hero("03 · EVIDENCE LEDGER","What can you actually prove?","EduPath separates evidence from assumptions. This makes the recommendations auditable: a skill is stronger when the document contains concrete evidence, not just a keyword.")
if not s.get("gaps"):
    st.info("Analyze a learner profile first."); st.stop()
rows=[]
for g in s["gaps"]:
    rows.append({"Skill":g["skill"],"Current":g["current"],"Target":g["target"],"Confidence":f'{int(g["confidence"]*100)}%',"Evidence":", ".join(g["evidence"]) or "No direct evidence","Blockers":", ".join(g["blockers"]) or "—"})
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
st.markdown("### Source")
st.write(s.get("document_name","Learner-entered skills"))
with st.expander("Inspect extracted document text"):
    st.text(s.get("document_text","")[:20000])
