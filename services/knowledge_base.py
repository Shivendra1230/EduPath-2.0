"""Persistent, source-cited retrieval for EduPath learning materials.

Uses transparent BM25-style lexical ranking (no embedding API required), keeps
source/page/timestamp metadata, and stores conversation history in SQLite.
"""
import json
import math
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "edupath.sqlite3"
STOP = set("""
a an the is are was were be been being to of in on for with by from as at and
or it this that these those what how why when where which who do does did can
could should would will about into than then their your you we they i me my our
not if have has had please explain tell describe give show summarize summary
""".split())


def _connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=15)
    c.execute("""CREATE TABLE IF NOT EXISTS kb_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id TEXT NOT NULL,
        source TEXT NOT NULL,
        locator TEXT NOT NULL,
        chunk_text TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_kb_learner ON kb_chunks(learner_id)")
    c.execute("""CREATE TABLE IF NOT EXISTS learning_chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id TEXT NOT NULL,
        scope TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE INDEX IF NOT EXISTS idx_learning_chat
                 ON learning_chat(learner_id, scope, id)""")
    c.commit()
    return c


def _tokens(text):
    return [w for w in re.findall(r"[a-zA-Z0-9+#.-]{2,}", text.lower())
            if w not in STOP]


def chunk_sections(sections, size=1100, overlap=180):
    if size < 100:
        raise ValueError("Chunk size must be at least 100 characters.")
    if overlap < 0 or overlap >= size:
        raise ValueError("Overlap must be between zero and size - 1.")
    chunks = []
    for sec in sections:
        text = re.sub(r"\s+", " ", str(sec.get("text", ""))).strip()
        if not text:
            continue
        start, part = 0, 1
        while start < len(text):
            end = min(len(text), start + size)
            snippet = text[start:end].strip()
            if snippet:
                locator = sec.get("locator", "document")
                if len(text) > size:
                    locator = f"{locator}, chunk {part}"
                chunks.append({
                    "source": sec.get("source", "Uploaded material"),
                    "locator": locator,
                    "text": snippet,
                })
            if end >= len(text):
                break
            start = end - overlap
            part += 1
    return chunks


def add_sections(learner_id, sections):
    chunks = chunk_sections(sections)
    if not chunks:
        return 0
    c = _connect()
    try:
        with c:
            for source in sorted({x["source"] for x in chunks}):
                c.execute(
                    "DELETE FROM kb_chunks WHERE learner_id=? AND source=?",
                    (learner_id, source),
                )
            now = datetime.now(timezone.utc).isoformat()
            c.executemany(
                """INSERT INTO kb_chunks
                   (learner_id, source, locator, chunk_text, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                [(learner_id, x["source"], x["locator"], x["text"], now)
                 for x in chunks],
            )
    finally:
        c.close()
    return len(chunks)


def list_sources(learner_id):
    c = _connect()
    try:
        rows = c.execute(
            """SELECT source, COUNT(*), MAX(created_at) FROM kb_chunks
               WHERE learner_id=? GROUP BY source ORDER BY source""",
            (learner_id,),
        ).fetchall()
    finally:
        c.close()
    return [{"source": r[0], "chunks": r[1], "indexed_at": r[2]} for r in rows]


def retrieve(learner_id, query, k=5, min_score=0.025, source=None):
    """Rank relevant chunks with a small BM25-style score and phrase bonus."""
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    c = _connect()
    try:
        if source:
            rows = c.execute(
                """SELECT source, locator, chunk_text FROM kb_chunks
                   WHERE learner_id=? AND source=?""",
                (learner_id, source),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT source, locator, chunk_text FROM kb_chunks WHERE learner_id=?",
                (learner_id,),
            ).fetchall()
    finally:
        c.close()

    if not rows:
        return []

    docs = []
    document_frequency = Counter()
    for source, locator, text in rows:
        tokens = _tokens(text)
        counts = Counter(tokens)
        docs.append((source, locator, text, tokens, counts))
        document_frequency.update(set(tokens))

    avg_len = sum(len(d[3]) for d in docs) / max(len(docs), 1)
    q_counts = Counter(query_tokens)
    ranked = []
    n_docs = len(docs)

    for source, locator, text, tokens, counts in docs:
        score = 0.0
        doc_len = max(len(tokens), 1)
        for term, q_freq in q_counts.items():
            tf = counts.get(term, 0)
            if not tf:
                continue
            df = document_frequency.get(term, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            denom = tf + 1.2 * (1 - 0.75 + 0.75 * doc_len / max(avg_len, 1))
            score += idf * (tf * 2.2 / denom) * min(q_freq, 2)

        query_phrase = " ".join(query_tokens)
        doc_token_text = " ".join(tokens)
        if query_phrase and query_phrase in doc_token_text:
            score *= 1.25

        # Normalize by query size to make threshold less length-sensitive.
        score = score / max(len(set(query_tokens)), 1)
        if score >= min_score:
            ranked.append({
                "source": source,
                "locator": locator,
                "text": text,
                "score": round(score, 4),
            })

    ranked.sort(key=lambda x: (-x["score"], x["source"], x["locator"]))
    return ranked[:max(1, min(int(k), 10))]



def get_source_chunks(learner_id, source, limit=1000):
    """Return indexed source chunks in stable order for summary/quiz generation."""
    c = _connect()
    try:
        rows = c.execute(
            """SELECT locator, chunk_text FROM kb_chunks
               WHERE learner_id=? AND source=? ORDER BY id LIMIT ?""",
            (learner_id, source, max(1, min(int(limit), 2000))),
        ).fetchall()
    finally:
        c.close()
    return [{"locator": r[0], "text": r[1]} for r in rows]


def load_chat_history(learner_id, scope, limit=40):
    c = _connect()
    try:
        rows = c.execute(
            """SELECT role, content FROM learning_chat
               WHERE learner_id=? AND scope=? ORDER BY id DESC LIMIT ?""",
            (learner_id, scope, max(1, min(int(limit), 200))),
        ).fetchall()
    finally:
        c.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def append_chat_message(learner_id, scope, role, content):
    if role not in {"user", "assistant"}:
        raise ValueError("Chat role must be 'user' or 'assistant'.")
    c = _connect()
    try:
        with c:
            c.execute(
                """INSERT INTO learning_chat
                   (learner_id, scope, role, content, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (learner_id, scope, role, str(content),
                 datetime.now(timezone.utc).isoformat()),
            )
    finally:
        c.close()


def clear_chat_history(learner_id, scope):
    c = _connect()
    try:
        with c:
            c.execute(
                "DELETE FROM learning_chat WHERE learner_id=? AND scope=?",
                (learner_id, scope),
            )
    finally:
        c.close()
