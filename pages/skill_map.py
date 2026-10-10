
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui import hero, metric

s = st.session_state.state

hero(
    "04 · SKILL INTELLIGENCE",
    "Know exactly what to learn next.",
    "Priority combines role importance, skill distance, prerequisite blockers and evidence confidence. It is not a generic list of courses."
)

if not s.get("gaps"):
    st.info("Analyze a learner profile first.")
    st.stop()

gaps = s["gaps"]

st.markdown("### Critical path")
st.markdown(" → ".join(s.get("critical_path", [])) or "No critical blockers.")

df = pd.DataFrame([
    {
        "Skill": g["skill"],
        "Current": g["current"],
        "Target": g["target"],
        "Gap": g["gap"],
        "Weight": g["weight"],
        "Priority": g["priority_score"],
        "Confidence": g["confidence"],
    }
    for g in gaps
])

# Skill radar: display a manageable number of skills.
st.markdown("### Capability radar")
radar_gaps = gaps[:10]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=[g["current"] for g in radar_gaps],
    theta=[g["skill"] for g in radar_gaps],
    fill="toself",
    name="Current level",
))
fig_radar.add_trace(go.Scatterpolar(
    r=[g["target"] for g in radar_gaps],
    theta=[g["skill"] for g in radar_gaps],
    fill="toself",
    name="Target level",
))
fig_radar.update_layout(
    template="plotly_dark",
    polar=dict(radialaxis=dict(visible=True, range=[0, 5], dtick=1)),
    height=480,
    margin=dict(l=40, r=40, t=35, b=35),
    legend=dict(orientation="h", y=-0.12),
)
st.plotly_chart(fig_radar, use_container_width=True)

st.caption(
    "Skill levels are evidence-based keyword estimates on a 0–5 scale, "
    "not independently verified proficiency scores."
)

st.markdown("### Highest-priority gaps")
priority_df = df[df["Gap"] > 0].sort_values(
    "Priority", ascending=True
).tail(10)

if not priority_df.empty:
    fig_priority = go.Figure(go.Bar(
        x=priority_df["Priority"],
        y=priority_df["Skill"],
        orientation="h",
        text=priority_df["Priority"],
        textposition="outside",
        hovertemplate="%{y}<br>Priority score: %{x}<extra></extra>",
    ))
    fig_priority.update_layout(
        template="plotly_dark",
        xaxis_title="Priority score",
        yaxis_title=None,
        height=max(320, len(priority_df) * 42),
        margin=dict(l=10, r=35, t=20, b=35),
    )
    st.plotly_chart(fig_priority, use_container_width=True)
else:
    st.success("No open skill gaps detected.")

st.markdown("### Complete skill assessment")
st.dataframe(df, use_container_width=True, hide_index=True)
