from __future__ import annotations


def get_verifications(store, status: str | None = None):
    query = 'SELECT * FROM verifications'
    params = []
    if status:
        query += ' WHERE status = ?'
        params.append(status)
    query += ' ORDER BY created_at DESC'
    with store._connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_actions(store, limit: int = 20):
    with store._connect() as conn:
        rows = conn.execute('SELECT * FROM actions ORDER BY created_at DESC LIMIT ?', (int(limit),)).fetchall()
    return [dict(row) for row in rows]


def get_artifacts(store, limit: int = 20):
    with store._connect() as conn:
        rows = conn.execute('SELECT * FROM artifacts ORDER BY created_at DESC LIMIT ?', (int(limit),)).fetchall()
    return [dict(row) for row in rows]


def get_blocked(store):
    with store._connect() as conn:
        rows = conn.execute('SELECT * FROM blocked_reasons ORDER BY created_at DESC').fetchall()
    return [dict(row) for row in rows]


def get_claim_verification(store, claim: str):
    with store._connect() as conn:
        row = conn.execute('SELECT * FROM verifications WHERE claim = ? ORDER BY created_at DESC LIMIT 1', (claim,)).fetchone()
    return dict(row) if row else None
