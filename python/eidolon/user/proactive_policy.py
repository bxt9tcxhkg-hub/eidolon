from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib


def under_cooldown(prior: dict, cooldown_minutes: int | None = None) -> bool:
    updated = prior.get('updated_at')
    if not updated:
        return False
    try:
        last = datetime.fromisoformat(updated)
    except Exception:
        return False
    minutes = cooldown_minutes if cooldown_minutes is not None else int(prior.get('cooldown_minutes', 0) or 0)
    return minutes > 0 and datetime.now(timezone.utc) - last < timedelta(minutes=minutes)


def cooldown_for_status(status: str) -> int:
    return {'dismissed': 180, 'ignored': 90, 'accepted': 15, 'helpful': 10, 'unhelpful': 240, 'new': 0}.get(status, 30)


def policy_limits(user_model: dict) -> tuple[int, bool]:
    prefs = user_model.get('workspace_preferences', {}) if isinstance(user_model, dict) else {}
    max_visible = int(prefs.get('proactive_max_visible', 2) or 2)
    allow = bool(prefs.get('allow_proactive_suggestions', True))
    return max(1, min(4, max_visible)), allow


def suggestion_id(topic_id: str) -> str:
    return 'assist_' + hashlib.sha1(topic_id.encode('utf-8')).hexdigest()[:10]
