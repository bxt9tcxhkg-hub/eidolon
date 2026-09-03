from __future__ import annotations

from enum import Enum


class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'
    READONLY = 'readonly'


SCOPES = {
    Role.ADMIN: {
        'users:read', 'users:write', 'users:delete',
        'settings:read', 'settings:write',
        'skills:read', 'skills:write', 'skills:execute',
        'workspaces:read', 'workspaces:write', 'workspaces:delete',
        'mesh:read', 'mesh:write',
        'export', 'import',
        'system:read', 'system:write',
    },
    Role.USER: {
        'settings:read', 'settings:write',
        'skills:read', 'skills:execute',
        'workspaces:read', 'workspaces:write',
        'mesh:read', 'mesh:write',
        'export',
    },
    Role.READONLY: {
        'settings:read',
        'skills:read',
        'workspaces:read',
        'mesh:read',
    },
}


def has_scope(role: Role, scope: str) -> bool:
    return scope in SCOPES.get(role, set())
