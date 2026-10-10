import streamlit as st
from services.parser import extract_text, clean_text
from core.graphs import build_analysis_graph

s=st.session_state.state
hero_title="Build a learning path around you."
st.markdown('<div class="hero"><div class="kicker">02 · LEARNER PROFILE</div><h1>Build a learning path around you.</h1><p>Your resume is evidence, not your identity. Add your target role, career goal and realistic weekly capacity so EduPath can make a useful decision about what comes next.</p></div>',unsafe_allow_html=True)

left,right=st.columns([1.1,1])
with left:
    st.markdown("### 1. Upload evidence")
    up=st.file_uploader("Resume / portfolio / certificate / project notes (PDF, DOCX, PPTX, TXT, MD)",type=["pdf","docx","pptx","txt","md"],key="resume_upload")
    if up:
        try:
            s["document_text"]=clean_text(extract_text(up)); s["document_name"]=up.name
            st.success(f"Parsed {up.name} · {len(s['document_text'])} characters")
        except Exception as e: st.error(f"Parser error: {e}")
    st.caption("Best result: upload the resume you would actually submit for the target role.")
with right:
    st.markdown("### 2. Define the destination")
    role=st.selectbox("Target role",["Generative AI Engineer","AI/ML Engineer","Data Analyst"],index=["Generative AI Engineer","AI/ML Engineer","Data Analyst"].index(s.get("target_role","Generative AI Engineer")))
    goal=st.text_area("Career goal",s.get("career_goal","Become job-ready for the target role with portfolio evidence."),height=90)
    hours=st.number_input("Realistic hours / week",1.0,40.0,float(s.get("weekly_hours",7)),0.5)
    current=st.text_area("Current skills / experience (optional)",s.get("current_skills",""),height=90)

jd=st.text_area("Optional real job description",s.get("job_description",""),height=150,placeholder="Paste a job description to make the gap map specific to a real role.")
if st.button("Analyze learner →",type="primary",use_container_width=True):
    if not s.get("document_text") and not current:
        st.warning("Upload evidence or enter your current skills first.")
    else:
        s.update({"target_role":role,"career_goal":goal,"weekly_hours":hours,"current_skills":current,"job_description":jd})
        if not s.get("document_text"): s["document_text"]=current
        with st.status("EduPath agents are analyzing your profile…",expanded=True) as status:
            graph=build_analysis_graph()
            result=graph.invoke(s)
            s.clear(); s.update(result)
            status.update(label="Analysis complete",state="complete",expanded=False)
        from services.store import save_state
        save_state(st.session_state.learner_id,s)
        st.switch_page("pages/command_center.py")
