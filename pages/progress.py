
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui import hero, metric

s = st.session_state.state

hero(
    "10 · PROGRESS REPORT",
    "See what actually changed.",
    "Progress combines completed learning objectives, current skill evidence, remaining gaps and the next evidence to collect."
)

if not s.get("gaps"):
    st.info("Analyze a learner profile first.")
    st.stop()

progress = s.get("progress", {})
objectives = s.get("objectives", [])

acquired = [
    o["skill"] for o in objectives
    if progress.get(o["id"], False)
]
remaining = [g["skill"] for g in s["gaps"] if g["gap"] > 0]

completed_count = sum(
    bool(progress.get(o["id"], False)) for o in objectives
)
total_objectives = len(objectives)
remaining_objectives = total_objectives - completed_count
completion_pct = (
    round(completed_count / total_objectives * 100)
    if total_objectives else 0
)

a, b, c = st.columns(3)
with a:
    metric("Objectives complete", str(completed_count), "new learning evidence")
with b:
    metric("Open skill gaps", str(len(remaining)), "remaining role distance")
with c:
    metric("Readiness", f'{s.get("readiness", 0)}/100', "current estimate")

st.markdown("### Learning completion")

fig_completion = go.Figure(go.Pie(
    labels=["Completed", "Remaining"],
    values=[completed_count, remaining_objectives],
    hole=0.65,
    textinfo="label+value",
))
fig_completion.update_layout(
    template="plotly_dark",
    height=350,
    margin=dict(l=20, r=20, t=20, b=20),
    annotations=[dict(
        text=f"{completion_pct}%",
        x=0.5, y=0.5,
        font_size=25,
        showarrow=False,
    )],
)
st.plotly_chart(fig_completion, use_container_width=True)

st.markdown("### Remaining skill gaps")

gap_df = pd.DataFrame([
    {
        "Skill": g["skill"],
        "Gap": g["gap"],
        "Priority": g["priority_score"],
        "Current": g["current"],
        "Target": g["target"],
    }
    for g in s["gaps"]
    if g["gap"] > 0
])

if not gap_df.empty:
    gap_df = gap_df.sort_values("Gap", ascending=True).tail(10)

    fig_gaps = go.Figure(go.Bar(
        x=gap_df["Gap"],
        y=gap_df["Skill"],
        orientation="h",
        text=gap_df["Gap"],
        textposition="auto",
        customdata=gap_df[["Current", "Target", "Priority"]].values,
        hovertemplate=(
            "%{y}<br>Gap: %{x}"
            "<br>Current: %{customdata[0]}"
            "<br>Target: %{customdata[1]}"
            "<br>Priority score: %{customdata[2]}<extra></extra>"
        ),
    ))
    fig_gaps.update_layout(
        template="plotly_dark",
        xaxis_title="Remaining skill distance",
        yaxis_title=None,
        height=max(300, len(gap_df) * 40),
        margin=dict(l=10, r=20, t=20, b=35),
    )
    st.plotly_chart(fig_gaps, use_container_width=True)
else:
    st.success("No open skill gaps detected.")

st.markdown("### Skills acquired through the current plan")
st.write(", ".join(acquired) if acquired else "No objective marked complete yet.")

st.markdown("### Recommended next steps")
for g in s["gaps"][:6]:
    if g["gap"] > 0:
        st.write(f'**{g["skill"]}** — {g["rationale"]}')

st.markdown("### Agent trace")
for t in s.get("trace", []):
    st.write("✓", t)
