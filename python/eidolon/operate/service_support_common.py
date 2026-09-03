from __future__ import annotations

from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_title(user_request: str, explicit_title: str | None = None) -> str:
    base = (explicit_title or '').strip() or user_request.strip()
    return base[:160] or 'Unbenanntes Ziel'


def normalize_goal(user_request: str, normalized_goal: str | None = None) -> str:
    return (normalized_goal or '').strip() or user_request.strip() or 'Kein Ziel angegeben'


def scope_summary(scope_summary: str | None = None) -> str:
    return (scope_summary or '').strip() or 'understand, plan, execute, verify'
