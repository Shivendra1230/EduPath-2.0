import streamlit as st, pandas as pd, plotly.graph_objects as go
from ui import hero, metric

s=st.session_state.state
if not s.get("gaps"):
    hero("00 · WELCOME","A career path built around evidence.","Upload your resume or portfolio, choose a target role, and EduPath will turn your evidence into a prioritized study path. The system is designed to change when you change.")
    c1,c2,c3=st.columns(3)
    with c1: metric("Step 1","Evidence","Resume, portfolio, certificate or project")
    with c2: metric("Step 2","Gap map","Current capability vs role requirements")
    with c3: metric("Step 3","Adaptive loop","Learn → practice → feedback → replan")
    if st.button("Start learner setup →",type="primary",use_container_width=True):
        st.switch_page("pages/profile.py")
else:
    hero("01 · COMMAND CENTER",f"Your path to {s.get('target_role','your target role')} is evidence-driven.","EduPath continuously compares what you can prove with what the target role requires, then turns the highest-impact gap into the next practical action.")
    a,b,c,d=st.columns(4)
    with a: metric("Role readiness",f"{s.get('readiness',0)}/100","evidence-based estimate")
    with b: metric("Open gaps",str(sum(g["gap"]>0 for g in s["gaps"])),"remaining skill distance")
    with c: metric("Study objectives",str(len(s.get("objectives",[]))),"weekly path")
    with d: metric("Evidence source",s.get("document_name","Learner input")[:18],"uploaded source")
    top=next((g for g in s["gaps"] if g["gap"]>0),None)
    if top:
        st.markdown('<div class="section">Today’s decision</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="card"><span class="pill">{top["priority"]}</span><span class="pill">confidence {int(top["confidence"]*100)}%</span><h2>{top["skill"]}</h2><p>{top["rationale"]} Blockers: {", ".join(top["blockers"]) or "none"}.</p></div>',unsafe_allow_html=True)
    left,right=st.columns([1.05,1])
    with left:
        st.markdown('<div class="section">Capability map</div>',unsafe_allow_html=True)
        df=pd.DataFrame([{"Skill":g["skill"],"You":g["current"],"Role":g["target"],"Gap":g["gap"],"Priority":g["priority"]} for g in s["gaps"]])
        st.dataframe(df,use_container_width=True,hide_index=True)
    with right:
        st.markdown('<div class="section">Priority signal</div>',unsafe_allow_html=True)
        g=s["gaps"][:8]
        fig=go.Figure(go.Bar(x=[x["priority_score"] for x in g],y=[x["skill"] for x in g],orientation="h"))
        fig.update_layout(template="plotly_dark",height=400,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)
