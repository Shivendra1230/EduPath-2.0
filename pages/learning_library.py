
import re
import streamlit as st

from services.parser import extract_document
from services.knowledge_base import add_sections, list_sources, retrieve
from core.llm import groq_service
from ui import hero


# =========================================================
# INITIALIZATION
# =========================================================

learner_id = st.session_state.learner_id

DEFAULTS = {
    "yt_active_video": None,
    "yt_transcript_ready": False,
    "yt_summary": "",
    "yt_quiz": [],
    "yt_quiz_result": None,
    "doc_summary": "",
    "doc_quiz": [],
    "doc_quiz_result": None,
    "ll_history": {},
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

hero(
    "11 · LEARNING LIBRARY",
    "Your personal AI learning workspace.",
    "Watch lectures, study documents, generate summaries and quizzes, "
    "and ask questions grounded in your selected source.",
)


# =========================================================
# HELPERS
# =========================================================

def get_video_id(url):
    patterns = [
        r"(?:youtube\.com/watch\?.*?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Please provide a valid YouTube video URL.")


def fetch_transcript(video_id):
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    available = list(transcript_list)

    if not available:
        raise ValueError("No accessible captions were found.")

    try:
        selected = transcript_list.find_transcript(["en", "hi"])
    except Exception:
        selected = available[0]

    fetched = selected.fetch()
    sections = []

    for item in fetched:
        start = float(item.start)
        timestamp = (
            f"{int(start // 3600):02d}:"
            f"{int((start % 3600) // 60):02d}:"
            f"{int(start % 60):02d}"
        )

        text = item.text.strip()

        if text:
            sections.append({
                "source": f"YouTube {video_id}",
                "locator": f"timestamp {timestamp}",
                "text": text,
            })

    if not sections:
        raise ValueError("The available transcript is empty.")

    return sections, selected.language


def get_evidence(source, question, count=8):
    """Retrieve evidence only from the selected source."""
    hits = retrieve(
        learner_id,
        question,
        k=count,
        min_score=0.0,
        source=source,
    )

    return [
        hit for hit in hits
        if str(hit.get("text", "")).strip()
    ]


def format_evidence(hits):
    return "\n\n".join(
        f"[S{i}] Source: {hit['source']} | {hit['locator']}\n"
        f"{hit['text']}"
        for i, hit in enumerate(hits, 1)
    )


def get_summary_context(source):
    """Collect passages from several queries for broader topic coverage."""
    queries = [
        "main topic concepts definitions explanation",
        "important ideas examples methods steps",
        "conclusion key takeaways summary",
    ]

    gathered = []
    seen = set()

    for query in queries:
        for hit in get_evidence(source, query, count=8):
            marker = (hit["locator"], hit["text"])

            if marker not in seen:
                seen.add(marker)
                gathered.append(hit)

    return gathered[:20]


def generate_summary(source, source_type):
    if not groq_service.live:
        raise RuntimeError("Configure GROQ_API_KEY first.")

    hits = get_summary_context(source)

    if not hits:
        raise ValueError(
            "No readable evidence was found for this source. "
            "Re-import the transcript or re-index the document."
        )

    return groq_service.chat(
        system=(
            "You are EduPath, a careful study tutor. Create a structured "
            "study summary using only the supplied source excerpts. "
            "Do not invent facts. Cite source-derived claims with [S#]. "
            "Mention if the excerpts do not cover the entire source."
        ),
        user=(
            f"Summarize this {source_type} for a student.\n\n"
            "Include:\n"
            "1. Main topic\n"
            "2. Important concepts and definitions\n"
            "3. Key explanations and examples present in the source\n"
            "4. Important steps or methods, if applicable\n"
            "5. Five key takeaways\n\n"
            f"SOURCE EXCERPTS:\n{format_evidence(hits)}"
        ),
        model=groq_service.fast_model,
        temperature=0.2,
        max_tokens=2200,
    )


def generate_quiz(source, source_type, count=5):
    if not groq_service.live:
        raise RuntimeError("Configure GROQ_API_KEY first.")

    hits = get_evidence(
        source,
        "important concepts definitions examples methods",
        count=10,
    )

    if not hits:
        raise ValueError("No relevant passages were found for this quiz.")

    result = groq_service.json(
        system=(
            "Generate multiple-choice questions using ONLY the supplied "
            "source excerpts. Return JSON with a 'questions' array. "
            "Each question must contain 'question' (string), 'options' "
            "(exactly four distinct strings), 'answer' (integer 0-3), "
            "and 'explanation' (string). Do not invent facts. "
            "Return no markdown."
        ),
        user=(
            f"Generate {count} different quiz questions about this "
            f"{source_type}. Cover different concepts.\n\n"
            f"SOURCE EXCERPTS:\n{format_evidence(hits)}"
        ),
        model=groq_service.fast_model,
        max_tokens=2400,
    )

    questions = result.get("questions", [])
    valid = []

    for question in questions:
        options = question.get("options", [])
        answer = question.get("answer")

        if (
            isinstance(question.get("question"), str)
            and isinstance(options, list)
            and len(options) == 4
            and all(isinstance(option, str) for option in options)
            and len(set(options)) == 4
            and isinstance(answer, int)
            and not isinstance(answer, bool)
            and 0 <= answer < 4
        ):
            valid.append({
                "question": question["question"],
                "options": options,
                "answer": answer,
                "explanation": str(question.get("explanation", "")),
            })

    if not valid:
        raise ValueError(
            "The model returned no valid questions. Try generating again."
        )

    return valid


def ask_source(source, question):
    """Return a stream and evidence; intentionally omit history=."""
    hits = get_evidence(source, question, count=6)

    if not hits:
        return (
            "I couldn't find relevant evidence in this source. "
            "Try a more specific question or re-index the source."
        ), []

    if not groq_service.live:
        return (
            "Configure GROQ_API_KEY to generate an AI answer. "
            "Relevant source passages are shown below."
        ), hits

    context = format_evidence(hits)

    prompt = (
        "Answer the learner using only the source excerpts below. "
        "If evidence is insufficient, say so. Cite source-derived claims "
        "using [S1], [S2], etc. Do not claim to know content that is not "
        "present in the excerpts.\n\n"
        f"QUESTION:\n{question}\n\n"
        f"SOURCE EXCERPTS:\n{context}"
    )

    # FIX: Do not pass history= because the local stream_text version
    # may not support that keyword argument.
    stream = groq_service.stream_text(
        system=(
            "You are EduPath, a source-grounded learning tutor. "
            "Be clear, helpful and concise. Use the learner's language "
            "where practical. Answer only from supplied evidence and "
            "cite material-derived claims with [S#]."
        ),
        user=prompt,
        model=groq_service.fast_model,
        temperature=0.2,
        max_tokens=1800,
    )

    return stream, hits


def render_quiz(quiz, prefix):
    if not quiz:
        return

    with st.form(f"{prefix}_quiz_form"):
        answers = []

        for i, question in enumerate(quiz):
            st.markdown(f"**Q{i + 1}. {question['question']}**")

            answer = st.radio(
                "Select your answer",
                question["options"],
                index=None,
                key=f"{prefix}_answer_{i}",
                label_visibility="collapsed",
            )

            answers.append(answer)
            st.divider()

        submitted = st.form_submit_button(
            "Check answers",
            type="primary",
        )

    if submitted:
        if any(answer is None for answer in answers):
            st.warning("Please answer every question first.")
        else:
            correct = sum(
                question["options"].index(answer) == question["answer"]
                for question, answer in zip(quiz, answers)
            )

            st.session_state[f"{prefix}_quiz_result"] = {
                "correct": correct,
                "total": len(quiz),
            }

    result = st.session_state.get(f"{prefix}_quiz_result")

    if result:
        st.success(
            f"Score: {result['correct']}/{result['total']} "
            f"({result['correct'] / result['total'] * 100:.0f}%)"
        )

        with st.expander("Review answers and explanations"):
            for i, question in enumerate(quiz):
                st.markdown(f"**Q{i + 1}. {question['question']}**")
                st.write(
                    "Correct answer: "
                    f"{question['options'][question['answer']]}"
                )
                st.write(
                    question.get("explanation")
                    or "No explanation was provided."
                )


def render_evidence(hits, title):
    with st.expander(title):
        for i, hit in enumerate(hits, 1):
            st.markdown(
                f"**[S{i}] {hit['source']} · {hit['locator']}**"
            )
            st.write(hit["text"])


# =========================================================
# SEPARATE WORKSPACES
# =========================================================

youtube_tab, document_tab = st.tabs([
    "🎥 YouTube Learning",
    "📚 Document Learning",
])


# =========================================================
# YOUTUBE LEARNING
# =========================================================

with youtube_tab:
    st.subheader("Learn from a YouTube lecture")

    video_url = st.text_input(
        "YouTube lecture URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="yt_url_input",
    )

    load_col, import_col = st.columns(2)

    with load_col:
        if st.button(
            "Load video",
            type="primary",
            key="yt_load_video",
            use_container_width=True,
        ):
            try:
                video_id = get_video_id(video_url.strip())

                st.session_state.yt_active_video = {
                    "id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "source": f"YouTube {video_id}",
                }

                st.session_state.yt_transcript_ready = False
                st.session_state.yt_summary = ""
                st.session_state.yt_quiz = []
                st.session_state.yt_quiz_result = None

                st.success("Video loaded.")

            except Exception as exc:
                st.error(str(exc))

    with import_col:
        if st.button(
            "Import transcript",
            key="yt_import_transcript",
            use_container_width=True,
        ):
            try:
                video_id = get_video_id(video_url.strip())

                with st.spinner("Fetching available captions..."):
                    sections, language = fetch_transcript(video_id)

                with st.spinner("Indexing transcript..."):
                    chunks = add_sections(learner_id, sections)

                if chunks:
                    st.session_state.yt_active_video = {
                        "id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "source": f"YouTube {video_id}",
                    }

                    st.session_state.yt_transcript_ready = True
                    st.session_state.yt_summary = ""
                    st.session_state.yt_quiz = []
                    st.session_state.yt_quiz_result = None

                    st.success(
                        f"Transcript imported · Language: {language} · "
                        f"Indexed chunks: {chunks}"
                    )
                else:
                    st.warning("No transcript chunks were indexed.")

            except Exception as exc:
                st.error(
                    f"Transcript import failed ({type(exc).__name__}): {exc}"
                )

    video = st.session_state.yt_active_video

    if video:
        st.markdown("### Video player")
        st.video(video["url"])

        st.link_button("Open on YouTube", video["url"])

        if not st.session_state.yt_transcript_ready:
            st.info(
                "Import the transcript to enable source-grounded "
                "summaries, quizzes and video questions."
            )

        if st.session_state.yt_transcript_ready:
            source = video["source"]

            st.divider()
            st.markdown("### Lecture study tools")

            summary_col, quiz_col = st.columns(2)

            with summary_col:
                if st.button(
                    "✨ Generate video summary",
                    key="yt_make_summary",
                    use_container_width=True,
                ):
                    try:
                        with st.spinner("Summarizing transcript evidence..."):
                            st.session_state.yt_summary = generate_summary(
                                source, "YouTube lecture"
                            )
                    except Exception as exc:
                        st.error(f"Summary failed: {exc}")

            with quiz_col:
                if st.button(
                    "📝 Generate video quiz",
                    key="yt_make_quiz",
                    use_container_width=True,
                ):
                    try:
                        with st.spinner("Creating transcript-based questions..."):
                            st.session_state.yt_quiz = generate_quiz(
                                source, "YouTube lecture"
                            )
                            st.session_state.yt_quiz_result = None
                    except Exception as exc:
                        st.error(f"Quiz generation failed: {exc}")

            if st.session_state.yt_summary:
                st.markdown("### Lecture summary")
                st.markdown(st.session_state.yt_summary)

            if st.session_state.yt_quiz:
                st.markdown("### Video quiz")
                render_quiz(st.session_state.yt_quiz, "yt")

            st.divider()
            st.markdown("### Ask this video")

            yt_question = st.text_input(
                "Question about this lecture",
                placeholder="What is this video about?",
                key="yt_question",
            )

            if st.button(
                "Ask video tutor",
                type="primary",
                key="yt_ask",
            ):
                if not yt_question.strip():
                    st.warning("Enter a question first.")
                else:
                    try:
                        with st.spinner("Retrieving lecture evidence..."):
                            answer_stream, hits = ask_source(
                                source,
                                yt_question.strip(),
                            )

                        st.markdown("#### Answer")

                        if isinstance(answer_stream, str):
                            answer = answer_stream
                            st.markdown(answer)
                        else:
                            answer = st.write_stream(answer_stream)

                        history_key = f"youtube:{video['id']}"
                        history = st.session_state.ll_history.setdefault(
                            history_key, []
                        )

                        history.extend([
                            {
                                "role": "user",
                                "content": yt_question.strip(),
                            },
                            {
                                "role": "assistant",
                                "content": str(answer),
                            },
                        ])

                        st.session_state.ll_history[history_key] = history[-12:]

                        if hits:
                            render_evidence(hits, "Transcript evidence")

                    except Exception as exc:
                        st.error(
                            f"Video tutor failed ({type(exc).__name__}): {exc}"
                        )


# =========================================================
# DOCUMENT LEARNING
# =========================================================

with document_tab:
    st.subheader("Learn from your own documents")

    uploads = st.file_uploader(
        "Upload PDF, PowerPoint, Word, TXT or Markdown",
        type=["pdf", "pptx", "docx", "txt", "md"],
        accept_multiple_files=True,
        key="document_uploads",
    )

    if st.button(
        "Index documents",
        type="primary",
        disabled=not uploads,
        key="doc_index",
    ):
        total = 0
        errors = []

        with st.status("Extracting and indexing documents...", expanded=True):
            for uploaded_file in uploads:
                try:
                    sections = extract_document(uploaded_file)

                    if not sections:
                        errors.append(
                            f"{uploaded_file.name}: No readable text found."
                        )
                        continue

                    sections = [
                        {
                            **section,
                            "source": uploaded_file.name,
                        }
                        for section in sections
                    ]

                    total += add_sections(learner_id, sections)

                except Exception as exc:
                    errors.append(
                        f"{uploaded_file.name}: "
                        f"{type(exc).__name__}: {exc}"
                    )

        if total:
            st.success(f"Indexed {total} document chunks.")

        for error in errors:
            st.warning(error)

        st.rerun()

    all_sources = list_sources(learner_id)

    document_sources = [
        row for row in all_sources
        if not str(row["source"]).startswith("YouTube ")
    ]

    if not document_sources:
        st.info("Upload and index a document to begin.")

    else:
        source_names = [row["source"] for row in document_sources]

        selected_source = st.selectbox(
            "Choose a document",
            source_names,
            key="doc_selected_source",
        )

        selected_row = next(
            row for row in document_sources
            if row["source"] == selected_source
        )

        st.caption(
            f"Indexed chunks: {selected_row['chunks']} · "
            f"Last indexed: {selected_row['indexed_at']}"
        )

        st.divider()
        st.markdown("### Document study tools")

        summary_col, quiz_col = st.columns(2)

        with summary_col:
            if st.button(
                "✨ Summarize document",
                key="doc_make_summary",
                use_container_width=True,
            ):
                try:
                    with st.spinner("Summarizing document evidence..."):
                        st.session_state.doc_summary = generate_summary(
                            selected_source, "document"
                        )
                except Exception as exc:
                    st.error(f"Summary failed: {exc}")

        with quiz_col:
            if st.button(
                "📝 Generate document quiz",
                key="doc_make_quiz",
                use_container_width=True,
            ):
                try:
                    with st.spinner("Creating document-based questions..."):
                        st.session_state.doc_quiz = generate_quiz(
                            selected_source, "document"
                        )
                        st.session_state.doc_quiz_result = None
                except Exception as exc:
                    st.error(f"Quiz generation failed: {exc}")

        if st.session_state.doc_summary:
            st.markdown("### Document summary")
            st.markdown(st.session_state.doc_summary)

        if st.session_state.doc_quiz:
            st.markdown("### Document quiz")
            render_quiz(st.session_state.doc_quiz, "doc")

        st.divider()
        st.markdown("### Ask this document")

        doc_question = st.text_input(
            "Question about the selected document",
            placeholder="Explain a concept from this document...",
            key="doc_question",
        )

        if st.button(
            "Ask document tutor",
            type="primary",
            key="doc_ask",
        ):
            if not doc_question.strip():
                st.warning("Enter a question first.")
            else:
                try:
                    with st.spinner("Retrieving document evidence..."):
                        answer_stream, hits = ask_source(
                            selected_source,
                            doc_question.strip(),
                        )

                    st.markdown("#### Answer")

                    if isinstance(answer_stream, str):
                        answer = answer_stream
                        st.markdown(answer)
                    else:
                        answer = st.write_stream(answer_stream)

                    history_key = f"document:{selected_source}"
                    history = st.session_state.ll_history.setdefault(
                        history_key, []
                    )

                    history.extend([
                        {
                            "role": "user",
                            "content": doc_question.strip(),
                        },
                        {
                            "role": "assistant",
                            "content": str(answer),
                        },
                    ])

                    st.session_state.ll_history[history_key] = history[-12:]

                    if hits:
                        render_evidence(hits, "Document evidence")

                except Exception as exc:
                    st.error(
                        f"Document tutor failed ({type(exc).__name__}): {exc}"
                    )
