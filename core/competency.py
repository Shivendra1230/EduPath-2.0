import json, re
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROLES=json.loads((BASE/"data/roles.json").read_text())
RESOURCES=json.loads((BASE/"data/resources.json").read_text())

ALIASES={
 "Machine Learning":["machine learning","scikit-learn","sklearn"],
 "Deep Learning":["deep learning","cnn","ann","neural network","pytorch","tensorflow"],
 "LLM/RAG":["rag","retrieval augmented","llm","large language model","langchain","langgraph"],
 "LLM Evaluation":["llm evaluation","evals","ragas","evaluation dataset"],
 "FastAPI":["fastapi"],
 "Docker":["docker","container","docker compose"],
 "Cloud Deployment":["deployment","deployed","render","vercel","aws","azure","gcp"],
 "SQL":["sql","mysql","postgresql","database"],
 "Git":["github","git","gitlab"],
 "Python":["python"],
 "Statistics":["statistics","probability","hypothesis testing"],
 "Prompt Engineering":["prompt engineering","prompting"],
 "Embeddings":["embedding","sentence-transformers"],
 "Vector Databases":["faiss","chroma","pinecone","vector database"],
 "Agents":["agent","multi-agent","langgraph"],
 "MLOps":["mlops","monitoring","model registry"],
 "System Design":["system design","architecture"],
 "Excel":["excel","spreadsheet"],
 "Power BI":["power bi","powerbi"],
 "Data Visualization":["visualization","tableau","dashboard","plotly","matplotlib"]
}

def role(role): return ROLES.get(role, ROLES["AI/ML Engineer"])

def evidence_levels(text, role_name):
    t=text.lower()
    rd=role(role_name)
    levels={}; evidence={}
    for skill,target in rd["skills"].items():
        hits=[a for a in ALIASES.get(skill,[skill.lower()]) if a.lower() in t]
        score=0
        if hits:
            score=1
            if any(k in t for k in ["built","developed","implemented","deployed","project","internship","experience"]):
                score=2
            if any(k in t for k in ["production","architecture","optimization","monitoring","lead","designed"]):
                score=min(5,score+2)
            if len(hits)>=3: score=min(5,score+1)
        levels[skill]=min(score,target)
        evidence[skill]=hits[:6]
    return levels,evidence

def compute_gaps(text, role_name, job_description=""):
    rd=role(role_name)
    combined=text+"\n"+job_description
    levels, evidence=evidence_levels(combined, role_name)
    gaps=[]
    for skill,target in rd["skills"].items():
        cur=levels.get(skill,0)
        gap=max(0,target-cur)
        weight=rd["weights"].get(skill,.5)
        prereqs=rd["prerequisites"].get(skill,[])
        blockers=[p for p in prereqs if levels.get(p,0)<rd["skills"].get(p,1)]
        confidence=min(.96,.25+.14*len(evidence.get(skill,[]))) if evidence.get(skill) else .2
        score=min(100, gap*17*weight + len(blockers)*9)
        priority="Met" if gap==0 else ("Critical" if score>=60 else "High" if score>=35 else "Medium" if score>=18 else "Low")
        gaps.append({
            "skill":skill,"current":cur,"target":target,"gap":gap,"weight":weight,
            "priority_score":round(score,1),"priority":priority,
            "confidence":round(confidence,2),"evidence":evidence.get(skill,[]),
            "blockers":blockers,
            "rationale": f"{cur}/5 demonstrated vs {target}/5 target; role weight {weight:.2f}."
        })
    return sorted(gaps,key=lambda x:(-x["priority_score"],x["skill"]))

def readiness(gaps):
    denom=sum(g["target"]*g["weight"] for g in gaps) or 1
    num=sum(g["current"]*g["weight"] for g in gaps)
    return round(num/denom*100)

def critical_path(gaps, role_name):
    rd=role(role_name); result=[]
    for g in gaps:
        if g["gap"]<=0: continue
        for p in rd["prerequisites"].get(g["skill"],[]):
            if any(x["skill"]==p and x["gap"]>0 for x in gaps) and p not in result:
                result.append(p)
        if g["skill"] not in result: result.append(g["skill"])
        if len(result)>=7: break
    return result

def matched_resources(gaps):
    out=[]; seen=set()
    for g in gaps:
        if g["gap"]<=0: continue
        for r in RESOURCES:
            if g["skill"] in r["skills"] and r["title"] not in seen:
                rr=dict(r); rr["why"]=f"Directly targets your {g['skill']} gap ({g['current']}/5 → {g['target']}/5)."
                out.append(rr); seen.add(r["title"])
        if len(out)>=12: break
    return out
