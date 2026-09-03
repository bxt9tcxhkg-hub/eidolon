from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from eidolon.core.config import MESH_INBOX, MESH_INBOX_DB
from eidolon.mesh.inbox_support import inbox_row_payload, inbox_schema_sql, load_legacy_messages, migrated_message_payload, utc_timestamp


class MeshInboxStore:
    def __init__(self, db_path: str | Path = MESH_INBOX_DB, legacy_json_path: str | Path = MESH_INBOX):
        self.db_path = Path(db_path)
        self.legacy_json_path = Path(legacy_json_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()
        self._migrate_legacy_json()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(inbox_schema_sql())
            conn.commit()

    def _migrate_legacy_json(self) -> None:
        self.migrate_legacy_json()

    def migrate_legacy_json(self) -> int:
        if not self.legacy_json_path.exists():
            return 0
        payload = load_legacy_messages(self.legacy_json_path)
        if not payload:
            return 0
        migrated = 0
        for item in payload:
            self.append(**migrated_message_payload(item))
            migrated += 1
        self.legacy_json_path.unlink(missing_ok=True)
        return migrated

    def append(self, *, peer_id: str | None = None, to: str | None = None, message: str, from_id: str = 'host', message_type: str = 'chat', metadata: dict[str, Any] | None = None, timestamp: str | None = None) -> dict[str, Any]:
        peer = peer_id or to or 'broadcast'
        metadata = metadata or {}
        ts = utc_timestamp(timestamp)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    'INSERT INTO inbox (peer_id, message, from_id, message_type, metadata_json, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                    (peer, message, from_id, message_type, json.dumps(metadata, ensure_ascii=False), ts),
                )
                conn.commit()
        return {'status': 'stored', 'peer_id': peer, 'message': message, 'timestamp': ts}

    def list(self, device_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = 'SELECT peer_id, message, from_id, message_type, metadata_json, timestamp FROM inbox'
        params: list[Any] = []
        if device_id:
            query += ' WHERE peer_id = ?'
            params.append(device_id)
        query += ' ORDER BY id DESC LIMIT ?'
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return list(reversed([inbox_row_payload(row) for row in rows]))

    def get_recent_messages(self, device_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        return self.list(device_id=device_id, limit=limit)


class MeshInbox(MeshInboxStore):
    pass


_default_store: MeshInboxStore | None = None


def get_mesh_inbox_store() -> MeshInboxStore:
    global _default_store
    if _default_store is None:
        _default_store = MeshInboxStore()
    return _default_store
