from __future__ import annotations

from eidolon.core.auth_store_rows import row_to_api_key


def create_api_key(store, api_key) -> None:
    import json
    with store._connect() as conn:
        conn.execute("""INSERT INTO api_keys (key_id, user_id, key_hash, key_prefix, name, scopes, created_at, expires_at, last_used_at, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (api_key.key_id, api_key.user_id, api_key.key_hash, api_key.key_prefix, api_key.name, json.dumps(api_key.scopes), api_key.created_at, api_key.expires_at, api_key.last_used_at, int(api_key.is_active)))


def get_api_key_by_hash(store, key_hash: str):
    with store._connect() as conn:
        row = conn.execute('SELECT * FROM api_keys WHERE key_hash = ?', (key_hash,)).fetchone()
    return row_to_api_key(row) if row else None


def get_api_keys_for_user(store, user_id: str):
    with store._connect() as conn:
        rows = conn.execute('SELECT key_hash FROM api_keys WHERE user_id = ?', (user_id,)).fetchall()
    return [store.get_api_key_by_hash(row['key_hash']) for row in rows if row]


def delete_api_key(store, key_id: str) -> None:
    with store._connect() as conn:
        conn.execute('DELETE FROM api_keys WHERE key_id = ?', (key_id,))
