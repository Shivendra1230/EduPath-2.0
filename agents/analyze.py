from core.competency import compute_gaps, readiness, critical_path, matched_resources
from core.llm import groq_service

PROFILE_SYSTEM = """You are EduPath's evidence analyst.
Analyze the supplied learner evidence conservatively. Extract only information supported by the text.
Do not equate a keyword with mastery. Return JSON with:
name, summary, experience, projects, skills_evidence (object mapping skill to evidence strings).
"""

def profile_node(state):
    text=state.get("document_text","")
    profile={"name":"Learner","summary":"","experience":"","projects":[],"skills_evidence":{}}
    if groq_service.live and text:
        try:
            profile=groq_service.json(PROFILE_SYSTEM, f"Role: {state.get('target_role')}\nEvidence:\n{text[:18000]}", groq_service.reasoning_model)
        except Exception:
            pass
    state["profile"]=profile
    state["trace"]=state.get("trace",[])+["Evidence Analyst completed"]
    return state

def gap_node(state):
    gaps=compute_gaps(state.get("document_text",""),state.get("target_role","AI/ML Engineer"),state.get("job_description",""))
    state["gaps"]=gaps
    state["readiness"]=readiness(gaps)
    state["critical_path"]=critical_path(gaps,state.get("target_role","AI/ML Engineer"))
    state["trace"]=state.get("trace",[])+["Competency Engine mapped evidence to target-role requirements"]
    return state

def plan_node(state):
    resources=matched_resources(state.get("gaps",[]))
    state["resources"]=resources
    hours=max(1,float(state.get("weekly_hours",7)))
    gaps=[g for g in state.get("gaps",[]) if g["gap"]>0][:6]
    per=max(45,int(hours*60/max(len(gaps),1)))
    objectives=[]
    for g in gaps:
        linked=[r for r in resources if g["skill"] in r["skills"]][:2]
        objectives.append({
            "id":g["skill"].lower().replace(" ","_").replace("/","_"),
            "skill":g["skill"],
            "title":f"Build evidence in {g['skill']}",
            "minutes":min(120,per),
            "outcome":f"Move from {g['current']}/5 toward {g['target']}/5 with a demonstrable artifact.",
            "success":["Explain the concept without notes","Complete a practical artifact","Pass a self-check and explain trade-offs"],
            "resources":linked
        })
    state["objectives"]=objectives
    state["practice"]=[{
        "id":g["skill"].lower().replace(" ","_"),
        "skill":g["skill"],
        "title":f"{g['skill']} proof task",
        "difficulty":"Beginner" if g["current"]<=1 else "Intermediate" if g["current"]<=3 else "Advanced",
        "minutes":60 if g["current"]<=2 else 90,
        "deliverable":f"Small portfolio artifact that demonstrates {g['skill']}.",
        "checks":["Explain your implementation","Modify one requirement independently","Write one failure/lesson learned"]
    } for g in gaps[:6]]
    state["trace"]=state.get("trace",[])+["Learning Planner created a time-boxed study path and practice missions"]
    return state

def interview_node(state):
    gaps=[g for g in state.get("gaps",[]) if g["gap"]>0][:5]
    fallback=[{
        "question":f"Explain {g['skill']} and describe one production trade-off you would consider.",
        "skill":g["skill"],"difficulty":"Intermediate",
        "answer":"Start with the definition, then the implementation workflow, one concrete example, and one trade-off.",
        "follow_up":f"How would you test your {g['skill']} implementation?"
    } for g in gaps]
    state["interview"]=fallback
    if groq_service.live and gaps:
        try:
            data=groq_service.json(
                """You are a senior technical interviewer. Return JSON {"questions":[...]} with 5 questions.
Each item must contain question, skill, difficulty, answer, follow_up. Questions must be tied to the candidate's gaps and role, not generic.""",
                f"Role: {state.get('target_role')}\nGaps:{gaps}", groq_service.reasoning_model, 2600)
            state["interview"]=data.get("questions",fallback)[:5]
        except Exception:
            pass
    state["trace"]=state.get("trace",[])+["Interview Coach generated evidence-linked questions"]
    return state

def analyze_graph(graph, state):
    return graph.invoke(state)
