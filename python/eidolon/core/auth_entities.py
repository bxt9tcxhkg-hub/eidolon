from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from eidolon.core.auth_roles import Role


@dataclass
class User:
    user_id: str
    username: str
    password_hash: str
    role: Role = Role.USER
    display_name: str = ''
    email: str = ''
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_login_at: str = ''
    is_active: bool = True
    failed_login_attempts: int = 0
    locked_until: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role.value,
            'display_name': self.display_name,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login_at': self.last_login_at,
            'is_active': self.is_active,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until,
        }

    def can_login(self) -> bool:
        if not self.is_active:
            return False
        if self.locked_until:
            try:
                lock_time = datetime.fromisoformat(self.locked_until)
                if lock_time > datetime.now(timezone.utc):
                    return False
            except ValueError:
                pass
        return True


@dataclass
class Session:
    session_id: str
    user_id: str
    created_at: str
    expires_at: str
    last_activity: str
    ip_address: str = ''
    user_agent: str = ''

    def is_expired(self) -> bool:
        try:
            return datetime.fromisoformat(self.expires_at) < datetime.now(timezone.utc)
        except ValueError:
            return True


@dataclass
class ApiKey:
    key_id: str
    user_id: str
    key_hash: str
    key_prefix: str
    name: str
    scopes: list[str]
    created_at: str
    expires_at: str
    last_used_at: str = ''
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            'key_id': self.key_id,
            'user_id': self.user_id,
            'key_prefix': self.key_prefix,
            'name': self.name,
            'scopes': self.scopes,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'last_used_at': self.last_used_at,
            'is_active': self.is_active,
        }
