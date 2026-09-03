"""Multi-User-Auth-System fuer Eidolon."""
from __future__ import annotations

from pathlib import Path

from eidolon.core.auth_manager import AuthManager, RateLimiter
from eidolon.core.auth_models import ApiKey, PasswordHasher, Role, SCOPES, Session, User, has_scope
from eidolon.core.auth_store import AuthStore

__all__ = [
    'ApiKey',
    'AuthManager',
    'AuthStore',
    'PasswordHasher',
    'RateLimiter',
    'Role',
    'SCOPES',
    'Session',
    'User',
    'get_auth_manager',
    'has_scope',
]

_auth_manager: AuthManager | None = None


def get_auth_manager(project_root: Path, session_ttl_hours: int = 24) -> AuthManager:
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager(project_root, session_ttl_hours)
    return _auth_manager
