from __future__ import annotations

from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def start_status_for_domain(domain: str) -> str:
    if domain == 'knowledge':
        return 'draft'
    if domain == 'personal':
        return 'todo'
    return 'backlog'
