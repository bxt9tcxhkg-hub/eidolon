from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def inbox_schema_sql() -> str:
    return 'CREATE TABLE IF NOT EXISTS inbox (id INTEGER PRIMARY KEY AUTOINCREMENT, peer_id TEXT NOT NULL, message TEXT NOT NULL, from_id TEXT NOT NULL, message_type TEXT NOT NULL, metadata_json TEXT NOT NULL, timestamp TEXT NOT NULL)'


def load_legacy_messages(path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def migrated_message_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'peer_id': item.get('peer_id') or item.get('to') or 'broadcast',
        'message': item.get('message', ''),
        'from_id': item.get('from_id') or item.get('from', 'legacy'),
        'message_type': item.get('message_type') or item.get('type', 'chat'),
        'metadata': item.get('metadata') or {},
        'timestamp': item.get('timestamp'),
    }


def utc_timestamp(timestamp: str | None = None) -> str:
    return timestamp or datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def inbox_row_payload(row: tuple[str, str, str, str, str, str]) -> dict[str, Any]:
    peer_id, message, from_id, message_type, metadata_json, timestamp = row
    return {
        'peer_id': peer_id,
        'message': message,
        'from_id': from_id,
        'from': from_id,
        'message_type': message_type,
        'metadata': json.loads(metadata_json or '{}'),
        'timestamp': timestamp,
    }
