from ui import hero, metric
import streamlit as st
s=st.session_state.state
hero("10 · PROGRESS REPORT","See what actually changed.","Progress combines completed learning objectives, current skill evidence, remaining gaps and the next evidence to collect.")
if not s.get("gaps"): st.info("Analyze a learner profile first."); st.stop()
progress=s.get("progress",{})
acquired=[o["skill"] for o in s.get("objectives",[]) if progress.get(o["id"])]
remaining=[g["skill"] for g in s["gaps"] if g["gap"]>0]
a,b,c=st.columns(3)
with a: metric("Objectives complete",str(len(acquired)),"new learning evidence")
with b: metric("Open skill gaps",str(len(remaining)),"remaining role distance")
with c: metric("Readiness",f"{s.get('readiness',0)}/100","current estimate")
st.markdown("### Skills acquired through the current plan")
st.write(", ".join(acquired) if acquired else "No objective marked complete yet.")
st.markdown("### Recommended next steps")
for g in s["gaps"][:6]:
    if g["gap"]>0: st.write(f"**{g['skill']}** — {g['rationale']}")
st.markdown("### Agent trace")
for t in s.get("trace",[]): st.write("✓",t)
