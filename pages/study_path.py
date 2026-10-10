from ui import hero, metric
import streamlit as st
from services.store import save_state
s=st.session_state.state
hero("05 · STUDY PATH","A plan you can actually follow.","Every objective connects a role gap to a measurable outcome, a realistic time box, and a resource. Marking an objective complete changes the progress report and gives the coach new evidence.")
if not s.get("objectives"): st.info("Analyze a learner profile first."); st.stop()
for i,o in enumerate(s["objectives"],1):
    done=s.setdefault("progress",{}).get(o["id"],False)
    with st.container(border=True):
        c1,c2=st.columns([4,1])
        with c1:
            st.markdown(f"### {i}. {o['title']}")
            st.caption(f"{o['skill']} · {o['minutes']} minutes")
            st.write(o["outcome"])
        with c2:
            new=st.checkbox("Complete",value=done,key=f"complete_{o['id']}")
            if new!=done:
                s.setdefault("progress",{})[o["id"]]=new
                save_state(st.session_state.learner_id,s)
                st.rerun()
        st.markdown("**Success criteria**")
        for x in o["success"]: st.write("✓",x)
        st.markdown("**Recommended resources**")
        for r in o["resources"]:
            st.markdown(f"- [{r['title']}]({r['url']}) · {r['provider']} · {r['estimated_hours']}h · {r['level']}")
