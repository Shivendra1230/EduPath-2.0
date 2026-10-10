from core.competency import compute_gaps, readiness, critical_path, matched_resources

def replan(state):
    feedback=state.get("feedback","").strip()
    if not feedback: return state
    text=state.get("document_text","")+"\nLearner feedback:\n"+feedback
    gaps=compute_gaps(text,state.get("target_role","AI/ML Engineer"),state.get("job_description",""))
    low=feedback.lower()
    for g in gaps:
        if g["skill"].lower() in low and any(w in low for w in ["hard","stuck","confus","struggl","difficult"]):
            g["priority_score"]=min(100,g["priority_score"]+25)
            g["priority"]="Critical" if g["priority_score"]>=60 else "High"
            g["rationale"]+=" Learner feedback indicates active struggle, so practice is promoted."
    state["gaps"]=sorted(gaps,key=lambda x:(-x["priority_score"],x["skill"]))
    state["readiness"]=readiness(state["gaps"])
    state["critical_path"]=critical_path(state["gaps"],state.get("target_role","AI/ML Engineer"))
    state["resources"]=matched_resources(state["gaps"])
    state["trace"]=state.get("trace",[])+["Adaptive Planner used new learner feedback to re-prioritize the path"]
    return state
