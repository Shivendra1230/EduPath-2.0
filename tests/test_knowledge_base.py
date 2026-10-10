from services.knowledge_base import chunk_sections, retrieve, add_sections

def test_chunk_sections_preserves_source_locator():
    chunks=chunk_sections([{"source":"lecture.pdf","locator":"page 3","text":"Retrieval augmented generation uses retrieved evidence to ground language model answers."}], size=40, overlap=5)
    assert chunks
    assert chunks[0]["source"] == "lecture.pdf"
    assert "page 3" in chunks[0]["locator"]

def test_retrieval_returns_relevant_evidence(tmp_path, monkeypatch):
    import services.knowledge_base as kb
    monkeypatch.setattr(kb, "DB", tmp_path / "test.sqlite3")
    add_sections("learner-test", [{"source":"ml.pdf","locator":"page 2","text":"Supervised learning trains a model using labeled examples and known target values."}, {"source":"history.pdf","locator":"page 1","text":"The Roman empire expanded across parts of Europe and North Africa."}])
    hits=retrieve("learner-test", "How does supervised learning use labeled examples?")
    assert hits
    assert hits[0]["source"] == "ml.pdf"
    assert hits[0]["locator"] == "page 2"
