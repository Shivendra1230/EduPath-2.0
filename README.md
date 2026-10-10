# 🎓 EduPath 2.0

### AI-Powered Adaptive Learning & Career Intelligence

Turn skill gaps into personalized learning paths with AI-powered
career coaching, source-grounded learning, interview preparation,
and adaptive progress tracking.


🚀 Live Application

Try the deployed application here:

Live Demo: https://edupath-20-gmr9a7w2fherjmjgk6ggej.streamlit.app/

Built using **Python, Streamlit, LangGraph, Groq, and SQLite**, EduPath combines deterministic skill-gap analysis with AI-assisted coaching and source-grounded learning.

---

## ✨ Why EduPath?

Traditional learning platforms recommend courses. EduPath focuses on a more practical question:

> What skills do I have today, what does my target role require, what should I learn next, and how can I prove that I have learned it?

EduPath connects learner evidence, skill-gap analysis, learning objectives, resources, practice activities, interview preparation, and progress tracking into one workflow.

## 🚀 Key Features

### 1. Personalized Career Profile
- Define current skills, experience, career goals, and target role.
- Maintain learner information for personalized recommendations.
- Use available profile information to contextualize career guidance.

### 2. Evidence-Based Skill Gap Analysis
- Analyze available resume, portfolio, certificate, and project evidence.
- Compare demonstrated competencies with target-role expectations.
- Identify skill gaps and prioritize learning objectives.
- Use structured analysis instead of relying entirely on free-form LLM output.

### 3. Adaptive Learning Path
- Break skill gaps into manageable learning objectives.
- Recommend relevant learning resources.
- Organize learning activities into a structured plan.
- Track progress and support adaptive replanning.

### 4. Practice Lab
- Generate practical exercises and project missions.
- Practice concepts through application-oriented activities.
- Use practice feedback to identify areas that need more work.

### 5. AI Interview Coach
- Generate role-relevant interview questions.
- Practice technical and career-related questions.
- Generate additional questions for continued preparation.

### 6. Career Copilot
- Ask questions about skills, projects, learning roadmaps, resumes, and interviews.
- Get guidance informed by available learner context.
- Receive practical next steps rather than generic course recommendations.

### 7. Learning Library — Source-Grounded Learning
- Upload PDF, DOCX, PPTX, TXT, and Markdown learning material.
- Extract text and index it into searchable chunks.
- Retrieve relevant passages using lexical retrieval.
- Ask questions about indexed learning material.
- Generate study summaries and quizzes from retrieved evidence.
- Preserve source metadata such as document names, page/slide locations, and transcript timestamps where available.
- Store indexed chunks and learner-specific learning data in SQLite.

### 8. YouTube Learning Copilot
- Import available captions from supported public YouTube videos.
- Watch the video within the application.
- Ask questions about the video's transcript.
- Generate transcript-based summaries and quizzes.
- Use retrieved transcript passages as evidence for answers.

**Important:** Transcript access depends on captions being available and accessible. EduPath does not download video/audio or automatically transcribe videos in this implementation.

### 9. Progress Tracking
- Track completed learning activities.
- Review available progress information.
- Identify areas requiring additional practice.
- Support updates to the learning plan as learner information changes.

### 10. Persistent Learner State
- Use SQLite to persist learner state and indexed learning content.
- Maintain separate learner-scoped knowledge-base records.
- Retain supported learning and coaching history between interactions when saved by the application.

### 11. Streaming AI Responses
- Stream supported LLM responses progressively instead of waiting for the entire answer.
- Improve perceived responsiveness during longer answers.
- Preserve completed answers in supported chat-history workflows.

Streaming must be connected to each individual response-generation flow; not every structured task necessarily streams.

---

## 🏗️ Architecture

EduPath combines deterministic analysis, graph-based orchestration, AI-assisted generation, and persistent storage.

```text
                   ┌─────────────────────────┐
                   │      Streamlit UI       │
                   │ Profile · Skills · Chat │
                   │ Practice · Learning     │
                   └────────────┬────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
    ┌─────────▼──────────┐             ┌──────────▼─────────┐
    │  Analysis Workflow │             │  Career Copilot    │
    │                    │             │                    │
    │ Evidence Analysis  │             │ Question Routing   │
    │ Skill Gap Analysis │             │ Learner Context     │
    │ Learning Planning  │             │ LLM Response        │
    └─────────┬──────────┘             └──────────┬─────────┘
              │                                   │
              └─────────────────┬─────────────────┘
                                │
                   ┌────────────▼────────────┐
                   │   Learning & Practice   │
                   │ Resources · Interviews  │
                   │ Quizzes · Progress      │
                   └────────────┬────────────┘
                                │
                   ┌────────────▼────────────┐
                   │      SQLite Storage     │
                   │ Learner State · Sources │
                   │ Knowledge-Base Chunks   │
                   └─────────────────────────┘
```

### Learning Library Retrieval Flow

```text
PDF / DOCX / PPTX / TXT / Markdown
                 │
                 ▼
           Text Extraction
                 │
                 ▼
        Chunking + Metadata
                 │
                 ▼
          SQLite Storage
                 │
                 ▼
           User Question
                 │
                 ▼
         Lexical Retrieval
                 │
                 ▼
      Relevant Evidence Passages
                 │
                 ▼
          Groq LLM Answer
                 │
                 ▼
       Answer + Source References
```

**Retrieval note:** The current knowledge base uses lexical scoring rather than embedding-based semantic vector search. Results can therefore miss relevant passages when the question uses different terminology from the source.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| LangGraph | Workflow and agent orchestration |
| Groq API | LLM-powered coaching and generation |
| GPT-OSS models | Configurable reasoning and fast-generation models |
| SQLite | Learner state and knowledge-base persistence |
| PyMuPDF | PDF text extraction |
| python-docx | Word document processing |
| python-pptx | PowerPoint text extraction |
| Pandas | Data handling |
| Plotly | Interactive charts and visualizations |
| Pydantic | Data validation |
| python-dotenv | Environment configuration |
| youtube-transcript-api | Accessible YouTube transcript retrieval |

---

## 📋 Prerequisites

Before installing EduPath, ensure you have:

- Python 3.11 recommended for the supplied environment.
- pip or Conda.
- A Groq API key for LLM-powered features.
- Internet access for API calls and YouTube transcript retrieval.

Get your API key from [Groq Console](https://console.groq.com/).

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Shivendra1230/EduPath.git
cd EduPath
```

### 2. Create a virtual environment

Using Conda:

```bash
conda create -n edupath python=3.11 -y
conda activate edupath
```

Alternatively, using Python's virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_FAST=openai/gpt-oss-20b
GROQ_MODEL_REASONING=openai/gpt-oss-120b
```

Use model identifiers supported by your Groq account. Availability and API compatibility can change.

**Security:** Never commit your real `.env` file or expose your API key in source code, screenshots, or public repositories.

### 5. Run EduPath

From the project root:

```bash
streamlit run app.py
```

Streamlit will display the local application URL in the terminal, usually:

`http://localhost:8501`

---

## 🧪 Testing and Validation

Run the existing tests:

```bash
python -m pytest tests/ -v
```

Check Python syntax for key files:

```bash
python -m py_compile app.py core/llm.py core/coach_graph.py
```

You can also verify that the main application imports correctly:

```bash
python -c "from core.coach_graph import build_coach_graph; print('Import OK')"
```

### Suggested manual test checklist

- [ ] Create or load a learner profile.
- [ ] Enter a target role and career goal.
- [ ] Run skill-gap analysis.
- [ ] Generate a learning plan.
- [ ] Generate and review interview questions.
- [ ] Upload a text-based PDF and ask a question whose answer is present in it.
- [ ] Verify that the answer uses relevant retrieved passages.
- [ ] Import a YouTube video with accessible captions.
- [ ] Generate a summary and quiz from the transcript.
- [ ] Test relevant and unrelated Career Copilot questions.
- [ ] Restart the application and verify that saved learner data remains available.
- [ ] Confirm streaming behavior on every page that supports streamed responses.

A passing syntax check does not guarantee successful API calls, accurate answers, or a complete end-to-end workflow.

---

## 🔐 Privacy and Data Handling

- Learner state and indexed knowledge-base content are stored locally in SQLite by default.
- Uploaded content may be sent to the configured Groq model when used for AI generation.
- Do not upload confidential documents unless you understand the applicable API and data-handling policies.
- Keep API credentials in environment variables.
- Protect the local database and backups if they contain personal learner information.

---

## ⚠️ Current Limitations

- Scanned PDFs without selectable text require OCR, which is not included in the described extraction workflow.
- Lexical retrieval is not equivalent to semantic vector search and may miss relevant passages.
- Source-grounded prompting reduces unsupported answers but cannot guarantee zero hallucinations.
- YouTube transcript import depends on caption availability and access restrictions.
- LLM model availability, response quality, latency, and rate limits depend on the configured provider.
- Streaming is available only in response flows wired to the streaming API.
- Persistent chat history depends on the page's save/load implementation.
- Full production readiness requires end-to-end testing, retrieval-quality evaluation, error-path testing, and security review.

---

## 🔮 Future Improvements

- Semantic retrieval using embeddings and a vector index.
- Reranking and retrieval-quality evaluation.
- OCR for scanned documents.
- Stronger source citations and answer-grounding checks.
- Automated evaluation of model accuracy, relevance, and hallucination rate.
- More robust intent classification for Career Copilot.
- Persistent, session-aware chat memory across application restarts.
- Adaptive learning recommendations informed by quiz results and learner feedback.
- Expanded test coverage and production deployment monitoring.

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Submit a pull request describing the changes and validation performed.

Please avoid committing API keys, personal learner data, database files, or other sensitive information.

🎯 Project Goals

EduPath 2.0 aims to make AI-assisted learning more personalized, structured, and career-focused by connecting learning activities with practical skill development.

👨‍💻 Developer

Shivendra Pratap Singh

GitHub:  https://github.com/Shivendra1230

LinkedIn: www.linkedin.com/in/shivendra-pratap-singh-8bab22237

## 📄 License

Add a `LICENSE` file to the repository before distributing EduPath under a specific open-source license.

---

**EduPath — Learn with purpose. Practice with evidence. Grow with direction.**
