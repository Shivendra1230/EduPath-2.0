from core.coach_graph import _classify_scope, OUT_OF_SCOPE_REPLY, answer_node


def test_scope_guard_fallback_rejects_unrelated(monkeypatch):
    import core.coach_graph as coach
    monkeypatch.setattr(coach.groq_service, "live", False)
    assert coach._classify_scope("Tell me a joke about cats") is False


def test_scope_guard_fallback_accepts_career_question(monkeypatch):
    import core.coach_graph as coach
    monkeypatch.setattr(coach.groq_service, "live", False)
    assert coach._classify_scope("How should I prepare for an interview?") is True


def test_out_of_scope_answer_does_not_call_llm(monkeypatch):
    import core.coach_graph as coach
    monkeypatch.setattr(coach, "_classify_scope", lambda question: False)
    state = {"coach_question": "Tell me a joke"}
    result = coach.answer_node(state)
    assert result["coach_answer"] == OUT_OF_SCOPE_REPLY
