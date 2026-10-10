import json, sqlite3, uuid
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parents[1] / "data" / "edupath.sqlite3"

def _conn():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS learners (
        id TEXT PRIMARY KEY, updated_at TEXT NOT NULL, state_json TEXT NOT NULL
    )""")
    c.commit()
    return c

def ensure_learner():
    sid = str(uuid.uuid4())
    c = _conn()
    c.execute("INSERT INTO learners VALUES (?, ?, ?)", (sid, datetime.utcnow().isoformat(), json.dumps({})))
    c.commit(); c.close()
    return sid

def save_state(learner_id, state):
    c = _conn()
    c.execute("INSERT OR REPLACE INTO learners VALUES (?, ?, ?)",
              (learner_id, datetime.utcnow().isoformat(), json.dumps(state, default=str)))
    c.commit(); c.close()

def load_state(learner_id):
    c = _conn()
    row = c.execute("SELECT state_json FROM learners WHERE id=?", (learner_id,)).fetchone()
    c.close()
    return json.loads(row[0]) if row else {}
