import importlib.metadata as m, sys
print("Python:",sys.version.split()[0])
print("Streamlit:",m.version("streamlit"))
print("LangGraph:",m.version("langgraph"))
print("Groq:",m.version("groq"))
from langgraph.graph import StateGraph, START, END
from core.graphs import build_analysis_graph
from core.coach_graph import build_coach_graph
print("LangGraph analysis graph: PASS")
print("LangGraph coach graph: PASS")
print("EduPath imports: PASS")
