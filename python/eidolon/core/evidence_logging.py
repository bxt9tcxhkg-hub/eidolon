from __future__ import annotations


def log_action(store, command: str, exit_code: int | None = None, stdout: str | None = None, stderr: str | None = None) -> int:
    with store._connect() as conn:
        cur = conn.execute('INSERT INTO actions (command, exit_code, stdout, stderr) VALUES (?, ?, ?, ?)', (command, exit_code, stdout, stderr))
        conn.commit()
        return cur.lastrowid


def log_observation(store, action_id: int | None, kind: str, description: str, detail: str | None = None) -> int:
    with store._connect() as conn:
        cur = conn.execute('INSERT INTO observations (action_id, kind, description, detail) VALUES (?, ?, ?, ?)', (action_id, kind, description, detail))
        conn.commit()
        return cur.lastrowid


def log_artifact(store, action_id: int | None, path: str, sha256: str | None = None, size_bytes: int | None = None) -> int:
    with store._connect() as conn:
        cur = conn.execute('INSERT INTO artifacts (action_id, path, sha256, size_bytes) VALUES (?, ?, ?, ?)', (action_id, path, sha256, size_bytes))
        conn.commit()
        return cur.lastrowid


def log_verification(store, action_id: int | None, claim: str, status: str, evidence: str | None = None) -> int:
    assert status in ('verified', 'inferred', 'unverified', 'blocked'), f'Invalid status: {status}'
    with store._connect() as conn:
        cur = conn.execute('INSERT INTO verifications (action_id, claim, status, evidence) VALUES (?, ?, ?, ?)', (action_id, claim, status, evidence))
        conn.commit()
        return cur.lastrowid


def log_blocked(store, claim: str, reason: str, capability: str | None = None) -> int:
    with store._connect() as conn:
        cur = conn.execute('INSERT INTO blocked_reasons (claim, reason, capability) VALUES (?, ?, ?)', (claim, reason, capability))
        conn.commit()
        return cur.lastrowid
