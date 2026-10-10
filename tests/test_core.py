from core.competency import compute_gaps, readiness, critical_path

def test_gap_engine():
    gaps=compute_gaps("Python FastAPI Git project", "Generative AI Engineer")
    assert gaps
    assert readiness(gaps) >= 0
    assert readiness(gaps) <= 100
    assert isinstance(critical_path(gaps,"Generative AI Engineer"),list)

def test_no_zero_target_error():
    gaps=compute_gaps("", "AI/ML Engineer")
    assert all(g["target"]>0 for g in gaps)
