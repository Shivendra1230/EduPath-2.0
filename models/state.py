
from typing import Any, Dict, List, TypedDict


class EduPathState(TypedDict, total=False):
    # Uploaded learning material
    document_text: str
    document_name: str

    # Learner profile and goals
    target_role: str
    career_goal: str
    current_skills: str
    experience: str
    job_description: str
    weekly_hours: float
    profile: Dict[str, Any]

    # Skill-gap analysis and learning plan
    gaps: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    objectives: List[Dict[str, Any]]
    practice: List[Dict[str, Any]]
    interview: List[Dict[str, Any]]
    readiness: int
    critical_path: List[str]

    # Progress and feedback
    feedback: str
    progress: Dict[str, Any]
    trace: List[str]
    learning_sources: List[Dict[str, Any]]

    # Career Copilot state — these fields are important
    coach_question: str
    coach_answer: str
    coach_route: str
    coach_scope: str
    coach_history: List[Dict[str, str]]
