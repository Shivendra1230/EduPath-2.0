from langgraph.graph import StateGraph, START, END
from models.state import EduPathState
from agents.analyze import profile_node, gap_node, plan_node, interview_node

def build_analysis_graph():
    g=StateGraph(EduPathState)
    g.add_node("evidence",profile_node)
    g.add_node("gaps",gap_node)
    g.add_node("plan",plan_node)
    g.add_node("interview",interview_node)
    g.add_edge(START,"evidence"); g.add_edge("evidence","gaps"); g.add_edge("gaps","plan"); g.add_edge("plan","interview"); g.add_edge("interview",END)
    return g.compile()
