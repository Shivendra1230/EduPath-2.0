
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui import hero, metric
from services.store import save_state

s = st.session_state.state

hero(
    "05 · STUDY PATH",
    "A plan you can actually follow.",
    "Every objective connects a role gap to a measurable outcome, a realistic time box, and a resource. Marking an objective complete changes the progress report and gives the coach new evidence."
)

if not s.get("objectives"):
    st.info("Analyze a learner profile first.")
    st.stop()

objectives = s["objectives"]
progress = s.setdefault("progress", {})

completed_count = sum(
    bool(progress.get(o["id"], False)) for o in objectives
)
total_count = len(objectives)
completion_pct = round(completed_count / total_count * 100) if total_count else 0

c1, c2, c3 = st.columns(3)
with c1:
    metric("Objectives", str(total_count), "planned learning outcomes")
with c2:
    metric("Completed", str(completed_count), "marked complete")
with c3:
    metric("Completion", f"{completion_pct}%", "current plan progress")

st.markdown("### Learning progress")

fig_progress = go.Figure(go.Bar(
    x=["Completed", "Remaining"],
    y=[completed_count, total_count - completed_count],
    text=[completed_count, total_count - completed_count],
    textposition="auto",
))
fig_progress.update_layout(
    template="plotly_dark",
    yaxis_title="Objectives",
    height=300,
    margin=dict(l=20, r=20, t=20, b=20),
    showlegend=False,
)
st.plotly_chart(fig_progress, use_container_width=True)

st.markdown("### Study roadmap")

roadmap_df = pd.DataFrame([
    {
        "Objective": o["title"],
        "Skill": o["skill"],
        "Planned minutes": o["minutes"],
        "Status": (
            "Completed" if progress.get(o["id"], False)
            else "In progress"
        ),
    }
    for o in objectives
])

fig_roadmap = go.Figure(go.Bar(
    x=roadmap_df["Planned minutes"],
    y=roadmap_df["Skill"],
    orientation="h",
    text=roadmap_df["Planned minutes"].astype(str) + " min",
    textposition="auto",
    customdata=roadmap_df[["Status", "Objective"]].values,
    hovertemplate=(
        "%{customdata[1]}<br>"
        "Planned time: %{x} minutes<br>"
        "Status: %{customdata[0]}<extra></extra>"
    ),
))
fig_roadmap.update_layout(
    template="plotly_dark",
    xaxis_title="Planned time (minutes)",
    yaxis_title=None,
    height=max(300, len(objectives) * 55),
    margin=dict(l=10, r=20, t=20, b=40),
)
st.plotly_chart(fig_roadmap, use_container_width=True)

for i, o in enumerate(objectives, 1):
    done = bool(s.setdefault("progress", {}).get(o["id"], False))

    with st.container(border=True):
        c1, c2 = st.columns([4, 1])

        with c1:
            st.markdown(f"### {i}. {o['title']}")
            st.caption(f"{o['skill']} · {o['minutes']} minutes")
            st.write(o["outcome"])

        with c2:
            new = st.checkbox(
                "Complete",
                value=done,
                key=f"complete_{o['id']}",
            )
            if new != done:
                s.setdefault("progress", {})[o["id"]] = new
                save_state(st.session_state.learner_id, s)
                st.rerun()

        st.markdown("**Success criteria**")
        for x in o["success"]:
            st.write("✓", x)

        st.markdown("**Recommended resources**")
        for r in o["resources"]:
            st.markdown(
                f"- [{r['title']}]({r['url']}) · "
                f"{r['provider']} · {r['estimated_hours']}h · {r['level']}"
            )
