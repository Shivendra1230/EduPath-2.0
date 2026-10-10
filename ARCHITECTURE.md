# Architecture

```text
                         ┌──────────────────────────┐
                         │       EduPath UI         │
                         │ Profile / Skills / Study │
                         │ Practice / Coach / Report│
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
             ANALYSIS GRAPH                       COACH GRAPH
                    │                                   │
          ┌─────────▼─────────┐               ┌────────▼────────┐
          │ Evidence Analyst  │               │ Intent Router   │
          └─────────┬─────────┘               └────────┬────────┘
                    ▼                                   ▼
          ┌───────────────────┐                ┌────────────────┐
          │ Competency Engine │                │ Groq Reasoning │
          └─────────┬─────────┘                │ Coach / Web*   │
                    ▼                          └────────────────┘
          ┌───────────────────┐
          │ Learning Planner  │
          └─────────┬─────────┘
                    ▼
          ┌───────────────────┐
          │ Interview Coach   │
          └─────────┬─────────┘
                    ▼
              Learner State
                    ▲
                    │
             Adaptive Replan
```

Deterministic competency logic controls the core learning decision. LLMs enrich evidence, generate explanations and interview content, and power open-ended coaching.


## Source-cited learning library (Track D)

The Learning Library stores source-aware chunks in SQLite (`kb_chunks`) with the learner ID, source filename/video ID, locator (PDF page, PPT slide, or transcript timestamp), and extracted text. Retrieval uses transparent lexical overlap scoring and returns the top passages. When Groq is configured, the tutor is prompted to answer only from retrieved evidence and cite passage IDs; otherwise the app still exposes retrieved evidence locally. Supported files include PDF, PPTX, DOCX, TXT and Markdown. Public YouTube transcript import depends on captions being available. This implementation does not claim OCR for scanned PDFs or video/audio transcription.
