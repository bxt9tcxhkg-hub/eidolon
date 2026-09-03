from __future__ import annotations

from datetime import datetime, timezone
import secrets

from eidolon.core.auth_models import Session


def create_session(manager, user_id: str, ip_address: str = '', user_agent: str = '') -> Session:
    now = datetime.now(timezone.utc)
    session = Session(
        session_id=secrets.token_urlsafe(32),
        user_id=user_id,
        created_at=now.isoformat(),
        expires_at=(now + manager._session_ttl).isoformat(),
        last_activity=now.isoformat(),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    manager._store.create_session(session)
    return session


def validate_session(manager, session_id: str):
    session = manager._store.get_session(session_id)
    if not session or session.is_expired():
        if session:
            manager._store.delete_session(session_id)
        return None
    session.last_activity = datetime.now(timezone.utc).isoformat()
    manager._store.update_session(session)
    return manager._store.get_user(session.user_id)
