from ui import hero, metric
import streamlit as st
s=st.session_state.state
hero("06 · PRACTICE LAB","Turn learning into proof.","Practice missions are designed to validate capability through artifacts, explanation and independent modification—not through passive completion.")
if not s.get("practice"): st.info("Analyze a learner profile first."); st.stop()
for i,p in enumerate(s["practice"],1):
    with st.container(border=True):
        st.markdown(f"### {i}. {p['title']}")
        st.caption(f"{p['skill']} · {p['difficulty']} · {p['minutes']} min")
        st.markdown(f"**Deliverable:** {p['deliverable']}")
        st.markdown("**Validation**")
        for x in p["checks"]: st.write("•",x)
        if st.button("Open mission",key=f"mission_{p['id']}"):
            st.session_state["active_mission"]=p
    if st.session_state.get("active_mission",{}).get("id")==p["id"]:
        st.info("Start with the smallest working artifact. When finished, report what was easy, hard, or surprising in Adaptive Loop.")
