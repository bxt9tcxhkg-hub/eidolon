from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from eidolon.core.auth_models import ApiKey, SCOPES, User, has_scope


def create_api_key(manager, user_id, name, scopes=None, expires_days=365):
    user = manager._store.get_user(user_id)
    if not user:
        return {'ok': False, 'error': 'User nicht gefunden'}
    allowed_scopes = SCOPES.get(user.role, set())
    scopes = list(allowed_scopes) if scopes is None else [scope for scope in scopes if scope in allowed_scopes]
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = ApiKey(
        key_id=secrets.token_urlsafe(12),
        user_id=user_id,
        key_hash=key_hash,
        key_prefix=raw_key[:8],
        name=name,
        scopes=scopes,
        created_at=datetime.now(timezone.utc).isoformat(),
        expires_at=(datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat(),
    )
    manager._store.create_api_key(api_key)
    return {'ok': True, 'api_key': api_key.to_dict(), 'raw_key': raw_key}


def validate_api_key(manager, raw_key: str):
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = manager._store.get_api_key_by_hash(key_hash)
    if not api_key or not api_key.is_active:
        return None
    if api_key.expires_at:
        try:
            if datetime.fromisoformat(api_key.expires_at) < datetime.now(timezone.utc):
                return None
        except ValueError:
            pass
    return manager._store.get_user(api_key.user_id)


def user_has_scope(user: User, scope: str) -> bool:
    return has_scope(user.role, scope)
