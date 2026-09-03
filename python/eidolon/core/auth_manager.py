from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from eidolon.core.auth_logic import RateLimiter, authenticate, change_password, create_api_key, create_session, create_user, user_has_scope, validate_api_key, validate_session
from eidolon.core.auth_models import PasswordHasher, Role
from eidolon.core.auth_store import AuthStore


class AuthManager:
    def __init__(self, project_root: Path, session_ttl_hours: int = 24):
        self._store = AuthStore(project_root)
        self._hasher = PasswordHasher()
        self._rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
        self._session_ttl = timedelta(hours=session_ttl_hours)
        self._max_login_attempts = 5
        self._lockout_duration = timedelta(minutes=30)

    def create_user(self, username, password, role=Role.USER, display_name='', email=''):
        return create_user(self, username, password, role=role, display_name=display_name, email=email)

    def authenticate(self, username, password, ip_address=''):
        return authenticate(self, username, password, ip_address=ip_address)

    def get_user(self, user_id: str):
        return self._store.get_user(user_id)

    def list_users(self) -> list[dict[str, Any]]:
        return [user.to_dict() for user in self._store.list_users()]

    def update_user(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        from datetime import datetime, timezone
        user = self._store.get_user(user_id)
        if not user:
            return {'ok': False, 'error': 'User nicht gefunden'}
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.updated_at = datetime.now(timezone.utc).isoformat()
        self._store.update_user(user)
        return {'ok': True, 'user': user.to_dict()}

    def delete_user(self, user_id: str) -> dict[str, Any]:
        self._store.delete_user(user_id)
        return {'ok': True}

    def change_password(self, user_id, old_password, new_password):
        return change_password(self, user_id, old_password, new_password)

    def get_user_by_username(self, username: str):
        return self._store.get_user_by_username(username)

    def create_session(self, user_id: str, ip_address: str = '', user_agent: str = ''):
        return create_session(self, user_id, ip_address=ip_address, user_agent=user_agent)

    def validate_session(self, session_id: str):
        return validate_session(self, session_id)

    def destroy_session(self, session_id: str) -> None:
        self._store.delete_session(session_id)

    def cleanup_sessions(self) -> int:
        return self._store.cleanup_expired_sessions()

    def create_api_key(self, user_id, name, scopes=None, expires_days=365):
        return create_api_key(self, user_id, name, scopes=scopes, expires_days=expires_days)

    def validate_api_key(self, raw_key: str):
        return validate_api_key(self, raw_key)

    def list_api_keys(self, user_id: str) -> list[dict[str, Any]]:
        return [key.to_dict() for key in self._store.get_api_keys_for_user(user_id)]

    def delete_api_key(self, key_id: str) -> dict[str, Any]:
        self._store.delete_api_key(key_id)
        return {'ok': True}

    def check_rate_limit(self, identifier: str) -> tuple[bool, int]:
        return self._rate_limiter.is_allowed(identifier), self._rate_limiter.get_remaining(identifier)

    def user_has_scope(self, user, scope: str) -> bool:
        return user_has_scope(user, scope)
