from __future__ import annotations

from datetime import datetime, timezone

from eidolon.core.auth_store_rows import row_to_session, row_to_user


def create_user(store, user) -> None:
    with store._connect() as conn:
        conn.execute("""INSERT INTO users (user_id, username, password_hash, role, display_name, email, created_at, updated_at, last_login_at, is_active, failed_login_attempts, locked_until) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (user.user_id, user.username, user.password_hash, user.role.value, user.display_name, user.email, user.created_at, user.updated_at, user.last_login_at, int(user.is_active), user.failed_login_attempts, user.locked_until))


def get_user(store, user_id: str):
    with store._connect() as conn:
        row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return row_to_user(row) if row else None


def get_user_by_username(store, username: str):
    with store._connect() as conn:
        row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return row_to_user(row) if row else None


def update_user(store, user) -> None:
    with store._connect() as conn:
        conn.execute("""UPDATE users SET username=?, password_hash=?, role=?, display_name=?, email=?, updated_at=?, last_login_at=?, is_active=?, failed_login_attempts=?, locked_until=? WHERE user_id=?""", (user.username, user.password_hash, user.role.value, user.display_name, user.email, user.updated_at, user.last_login_at, int(user.is_active), user.failed_login_attempts, user.locked_until, user.user_id))


def delete_user(store, user_id: str) -> None:
    with store._connect() as conn:
        conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))


def list_users(store):
    with store._connect() as conn:
        rows = conn.execute('SELECT * FROM users ORDER BY created_at').fetchall()
    return [row_to_user(row) for row in rows]


def create_session(store, session) -> None:
    with store._connect() as conn:
        conn.execute('INSERT INTO sessions (session_id, user_id, created_at, expires_at, last_activity, ip_address, user_agent) VALUES (?, ?, ?, ?, ?, ?, ?)', (session.session_id, session.user_id, session.created_at, session.expires_at, session.last_activity, session.ip_address, session.user_agent))


def get_session(store, session_id: str):
    with store._connect() as conn:
        row = conn.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    return row_to_session(row) if row else None


def update_session(store, session) -> None:
    with store._connect() as conn:
        conn.execute('UPDATE sessions SET last_activity=?, expires_at=? WHERE session_id=?', (session.last_activity, session.expires_at, session.session_id))


def delete_session(store, session_id: str) -> None:
    with store._connect() as conn:
        conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))


def cleanup_expired_sessions(store) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with store._connect() as conn:
        cursor = conn.execute('DELETE FROM sessions WHERE expires_at < ?', (now,))
        return cursor.rowcount
