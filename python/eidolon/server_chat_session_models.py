from __future__ import annotations

import json
from datetime import datetime, timezone
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_title(title: str | None) -> str:
    text = (title or '').strip()
    return text[:80] if text else 'Neue Unterhaltung'


def infer_title_from_message(message: str) -> str:
    text = ' '.join((message or '').strip().split())
    return text[:80] if text else 'Neue Unterhaltung'


def new_session(title: str | None = None, source: str = 'chat') -> dict:
    now = now_iso()
    return {'session_id': uuid.uuid4().hex[:12], 'title': normalize_title(title), 'source': source, 'created_at': now, 'updated_at': now, 'message_count': 0, 'messages': []}
