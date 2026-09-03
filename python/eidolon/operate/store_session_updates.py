from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_id(prefix: str) -> str:
    return f'{prefix}_{uuid.uuid4().hex[:10]}'


def update_session_record(store, session_id: str, **fields: Any):
    if not fields:
        current = store.get_session(session_id)
        if current is None:
            raise KeyError(session_id)
        return current
    fields['updated_at'] = now_iso()
    assignments = ', '.join(f'{key} = ?' for key in fields)
    values = list(fields.values()) + [session_id]
    with store._connect() as conn:
        cur = conn.execute(f'UPDATE work_sessions SET {assignments} WHERE id = ?', values)
        if cur.rowcount == 0:
            raise KeyError(session_id)
        conn.commit()
        row = conn.execute('SELECT * FROM work_sessions WHERE id = ?', (session_id,)).fetchone()
    return store._row_to_session(row)
