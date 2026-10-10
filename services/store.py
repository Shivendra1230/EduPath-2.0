
import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

DB = Path(__file__).resolve().parents[1] / "data" / "edupath.sqlite3"


def _conn():
    DB.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB, timeout=30)
    connection.execute("PRAGMA busy_timeout = 30000")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS learners (
            id TEXT PRIMARY KEY,
            updated_at TEXT NOT NULL,
            state_json TEXT NOT NULL
        )
    """)

    connection.commit()
    return connection


def _now():
    return datetime.now(timezone.utc).isoformat()


def ensure_learner():
    """Create a new learner with an empty state."""
    learner_id = str(uuid.uuid4())
    connection = _conn()

    try:
        connection.execute(
            "INSERT INTO learners (id, updated_at, state_json) VALUES (?, ?, ?)",
            (learner_id, _now(), json.dumps({}))
        )
        connection.commit()
    finally:
        connection.close()

    return learner_id


def learner_exists(learner_id):
    """Check whether the learner exists in the database."""
    if not isinstance(learner_id, str) or not learner_id.strip():
        return False

    connection = _conn()

    try:
        row = connection.execute(
            "SELECT 1 FROM learners WHERE id = ?",
            (learner_id,)
        ).fetchone()

        return row is not None
    finally:
        connection.close()


def save_state(learner_id, state):
    """Persist the complete learner state without changing the schema."""
    if not learner_id:
        raise ValueError("A valid learner ID is required.")

    if not isinstance(state, dict):
        raise TypeError("Learner state must be a dictionary.")

    serialized_state = json.dumps(
        state,
        ensure_ascii=False,
        default=str
    )

    connection = _conn()

    try:
        connection.execute(
            """
            INSERT INTO learners (id, updated_at, state_json)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                updated_at = excluded.updated_at,
                state_json = excluded.state_json
            """,
            (learner_id, _now(), serialized_state)
        )

        connection.commit()
    finally:
        connection.close()


def load_state(learner_id):
    """Load saved learner state, returning an empty dictionary if absent."""
    if not learner_id:
        return {}

    connection = _conn()

    try:
        row = connection.execute(
            "SELECT state_json FROM learners WHERE id = ?",
            (learner_id,)
        ).fetchone()
    finally:
        connection.close()

    if not row or not row[0]:
        return {}

    try:
        state = json.loads(row[0])
        return state if isinstance(state, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def delete_learner(learner_id):
    """Optional helper for explicitly deleting a learner's saved state."""
    if not learner_id:
        return

    connection = _conn()

    try:
        connection.execute(
            "DELETE FROM learners WHERE id = ?",
            (learner_id,)
        )
        connection.commit()
    finally:
        connection.close()
