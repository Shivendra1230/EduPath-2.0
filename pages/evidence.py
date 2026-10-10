
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui import hero, metric

s = st.session_state.state

hero(
    "03 · EVIDENCE LEDGER",
    "What can you actually prove?",
    "EduPath separates evidence from assumptions. This makes recommendations auditable: a skill is stronger when the document contains concrete evidence, not just a keyword."
)

if not s.get("gaps"):
    st.info("Analyze a learner profile first.")
    st.stop()

gaps = s["gaps"]

rows = []
for g in gaps:
    evidence = g.get("evidence", [])
    rows.append({
        "Skill": g["skill"],
        "Current": g["current"],
        "Target": g["target"],
        "Confidence": f'{int(g["confidence"] * 100)}%',
        "Confidence score": g["confidence"],
        "Evidence count": len(evidence),
        "Evidence": ", ".join(evidence) or "No direct evidence",
        "Blockers": ", ".join(g.get("blockers", [])) or "—",
    })

df = pd.DataFrame(rows)

covered = sum(row["Evidence count"] > 0 for row in rows)
total = len(rows)
coverage_pct = round(covered / total * 100) if total else 0

c1, c2, c3 = st.columns(3)
with c1:
    metric("Skills assessed", str(total), "target-role skills")
with c2:
    metric("With evidence", str(covered), "at least one matched term")
with c3:
    metric("Evidence coverage", f"{coverage_pct}%", "skills with matched evidence")

st.markdown("### Confidence by skill")

confidence_df = df.sort_values("Confidence score", ascending=True).tail(12)

fig_confidence = go.Figure(go.Bar(
    x=confidence_df["Confidence score"] * 100,
    y=confidence_df["Skill"],
    orientation="h",
    text=confidence_df["Confidence"],
    textposition="outside",
    hovertemplate="%{y}<br>Confidence estimate: %{x:.0f}%<extra></extra>",
))
fig_confidence.update_layout(
    template="plotly_dark",
    xaxis_title="Confidence estimate (%)",
    xaxis=dict(range=[0, 110]),
    yaxis_title=None,
    height=max(320, len(confidence_df) * 38),
    margin=dict(l=10, r=45, t=20, b=35),
)
st.plotly_chart(fig_confidence, use_container_width=True)

st.caption(
    "Confidence is calculated from matched evidence terms. "
    "It is not a probability that the learner has mastered the skill."
)

st.markdown("### Evidence coverage by skill")

fig_coverage = go.Figure(go.Bar(
    x=df["Skill"],
    y=df["Evidence count"],
    text=df["Evidence count"],
    textposition="auto",
))
fig_coverage.update_layout(
    template="plotly_dark",
    xaxis_title=None,
    yaxis_title="Matched evidence terms",
    height=380,
    margin=dict(l=20, r=20, t=20, b=100),
    xaxis_tickangle=-35,
)
st.plotly_chart(fig_coverage, use_container_width=True)

st.markdown("### Evidence details")
st.dataframe(
    df[["Skill", "Current", "Target", "Confidence", "Evidence", "Blockers"]],
    use_container_width=True,
    hide_index=True,
)

st.markdown("### Source")
st.write(s.get("document_name", "Learner-entered skills"))

with st.expander("Inspect extracted document text"):
    st.text(s.get("document_text", "")[:20000])
